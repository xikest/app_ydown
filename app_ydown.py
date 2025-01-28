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
storage_manager = StorageManager("web-driver.json")
logging.basicConfig(level=logging.ERROR)


class DownloadRequest(BaseModel):
    url: str
    file_type: str
    storage_name: str 

@app.post("/download/")
async def download_file(request: DownloadRequest):
    def remove_emojis(text):
        clean_text = emoji.replace_emoji(text, replace='')  # 이모티콘을 빈 문자열로 대체
        return clean_text
            
    
    bucket_name = request.storage_name
    
    if not request.url.strip():
        raise HTTPException(status_code=400, detail={"error": "Please enter a valid URL."})
    
    if request.file_type not in ["mp3"]:
         raise HTTPException(status_code=400, detail={"error": "Invalid file type. Only 'mp3' allowed."})
    filename = ydt.get_video_filename(url=request.url, file_type=request.file_type)
    filename = remove_emojis(filename)
    filename = remove_special_characters(filename)
    signed_url = storage_manager.get_signed_url_if_file_exists(bucket_name = bucket_name, file_name=filename)
    if signed_url is None:
        try:
            # file_name : xx.mp
            file_name = ydt.download_video(video_url=request.url, file_type=request.file_type, filename_replaced=filename)
            
            logging.info(f"Downloaded file: {file_name}") 
            
            file_path = file_name
            storage_manager.upload_file(bucket_name, file_path, file_name)
            
            if os.path.exists(file_path):
                os.unlink(file_path)
            else:
                logging.warning(f"File {file_name} not found for deletion.")
            
            
            signed_url = storage_manager.get_signed_url_if_file_exists(bucket_name = bucket_name, file_name=file_name)

            
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
            "file_name": signed_url
        }
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
            filename: storage_manager.get_signed_url_if_file_exists(bucket_name=bucket_name, file_name=filename)
            for filename in filenamelist
        }
        return JSONResponse(
            status_code=200,
            content={
                "message": "Success",  # 메시지 추가
                "file_name": link_dict  # 반환할 키 이름을 file_names로 수정
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching files from bucket: {str(e)}")

def remove_special_characters(text):
    cleaned_text = re.sub(r'[^a-zA-Z0-9가-힣\s]', '', text)
    return cleaned_text
