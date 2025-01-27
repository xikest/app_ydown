from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import logging
from tools.gcp import StorageManager
from functions import YTDownloader

app = FastAPI()
ydt = YTDownloader()
bucket_name = "web-ydown-storage"
storage_manager = StorageManager("web-driver.json")
logging.basicConfig(level=logging.ERROR)


class DownloadRequest(BaseModel):
    url: str
    file_type: str

@app.post("/download/")
async def download_file(request: DownloadRequest):
    if not request.url.strip():
        raise HTTPException(status_code=400, detail="Please enter a valid URL.")
    
    if request.file_type not in ["mp3", "mp4"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only 'mp3' or 'mp4' allowed.")
    filename = ydt.get_video_filename(url=request.url, file_type=request.file_type)
    public_url = storage_manager.get_public_url_if_file_exists(bucket_name = bucket_name, file_name=filename)
    
    if public_url is None:
        file_path = ydt.download_video(video_url=request.url, file_type=request.file_type, filename_replaced=filename)
        logging.info(f"Downloaded file: {file_path}") 
        
        blob_name = file_path
        storage_manager.upload_file(bucket_name, file_path, blob_name)
        blob = storage_manager.client.bucket(bucket_name).blob(blob_name)
        blob.make_public()
        public_url = blob.public_url
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Error downloading the file.")
        message= "new"
        logging.info(f"new URL: {public_url}")
    else:
        message= "old"
        logging.info(f"exist URL: {public_url}")
    
    return JSONResponse(
        status_code=200,
        content={
            "message": message,
            "file_name": public_url
        }
    )
    

