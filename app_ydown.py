from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import re
import emoji
import logging
from tools.gcp import StorageManager
from functions import YTDownloader

app = FastAPI()
ydt = YTDownloader()
storage_manager = StorageManager("ydown-manager.json")
logging.basicConfig(level=logging.ERROR)


class DownloadRequest(BaseModel):
    url: str
    file_type: str
    storage_name: str 

@app.post("/download/")
async def download_file(request: DownloadRequest):
    def remove_emojis_special_characters(text):
        format = text.split(".")[-1]
        text = text.replace(f".{format}", "")
        text = emoji.replace_emoji(text, replace='')  # 이모티콘을 빈 문자열로 대체
        text = re.sub(r'[^a-zA-Z0-9가-힣\s]', '', text)
        cleaned_text = f"{text}.{format}"
        return cleaned_text
                
    bucket_name = request.storage_name
    url = request.url
    file_type=request.file_type
        
    try:
        if not request.url.strip():
            raise HTTPException(status_code=400, detail={"error": "Please enter a valid URL."})
        
        if request.file_type not in ["mp3"]:
            raise HTTPException(status_code=400, detail={"error": "Invalid file type. Only 'mp3' allowed."})
        file_name = ydt.get_video_filename(url=url, file_type=file_type)
        file_name = remove_emojis_special_characters(file_name)
        signed_url = storage_manager.get_url_if_file_exists(bucket_name = bucket_name, file_name=file_name, use_public=False)
        if signed_url is None:
            try:
                # file_name : xx.mp
                file_name = ydt.download_video(video_url=url, file_type=file_type, filename_replaced=file_name)
                if not file_name:
                    logging.error("Download failed: file_name is None")
                    raise HTTPException(status_code=500, detail="Failed to download video")
                else:
                    logging.info(f"Downloaded file: {file_name}") 
                storage_manager.upload_file(bucket_name, file_path=file_name, destination_blob_name=file_name, make_public=False)
                
                if os.path.exists(file_name):
                    os.unlink(file_name)
                else:
                    logging.warning(f"File {file_name} not found for deletion.")
                
                
                signed_url = storage_manager.get_url_if_file_exists(bucket_name = bucket_name, file_name=file_name, use_public=False)
                
                message= "new"
                logging.info(f"new URL: {signed_url}")
                
            except Exception as e:
                logging.error(f"Error processing file: {str(e)}")
                raise HTTPException(status_code=500, detail={"error": f"Error processing file: {str(e)}"})
        else:
            message= "old"
            logging.info(f"exist URL: {signed_url}")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": message,
                "label":file_name,
                "url": signed_url
            })
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error: {str(e)}"
            )

    
@app.post("/mp3list/")
async def get_mp3list(request: Request) -> dict:
    bucket_name = request.query_params.get("storage_name")
    
    if not bucket_name:
        raise HTTPException(status_code=400, detail="Please provide a valid storage name.")
    
    try:
        # 버킷 내 파일 목록 가져오기
        filenamelist = storage_manager.list_files_in_bucket(bucket_name)
        
        if not filenamelist:
            raise HTTPException(status_code=404, detail="No files found in the bucket.")
        
        # 각 파일에 대해 signed URL 생성
        link_dict = {
            filename: storage_manager.get_url_if_file_exists(bucket_name=bucket_name, file_name=filename, use_public=False)
            for filename in filenamelist
        }
        return JSONResponse(
            status_code=200,
            content={
                "message": "Success",  # 메시지 추가
                "mp3list": link_dict  # 반환할 키 이름을 file_names로 수정
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching files from bucket: {str(e)}")