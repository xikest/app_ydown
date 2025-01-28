from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
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
    bucket_name = request.storage_name
    
    if not request.url.strip():
        raise HTTPException(status_code=400, detail="Please enter a valid URL.")
    
    if request.file_type not in ["mp3", "mp4"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only 'mp3' or 'mp4' allowed.")
    filename = ydt.get_video_filename(url=request.url, file_type=request.file_type)
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
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
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
    

