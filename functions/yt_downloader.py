import yt_dlp
import logging
import os 

class YTDownloader:
    
    def __init__(self):
        pass 
    
    def get_video_filename(self, url: str, file_type: str) -> str:
        ydl_opts = {
            'quiet': True,  # 출력 최소화
            'format': 'bestaudio/best',  # 가장 좋은 품질 선택
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 동영상 메타데이터 가져오기
            info_dict = ydl.extract_info(url, download=False)  # 다운로드하지 않음
            title = info_dict.get('title', 'unknown_title')  # 동영상 제목
            title= title.strip()
            return f"{title}.{file_type}"  # 파일 이름 생성    
    
    
    def download_video(self, video_url: str, file_type: str, options:dict=None, filename_replaced:str=None) -> str:
        
        
        if options is None:
            options =  {
                        "format": "bestaudio/best",
                        "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "128"
                        }
                        ],
                        "ffmpeg_location": "/usr/bin/ffmpeg",
                        "outtmpl": "%(title)s.%(ext)s",
                        "headers": {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
                        }
                        }
               
           
                         
        try:
            # yt-dlp로 파일 다운로드
            with yt_dlp.YoutubeDL(options) as ydl:
                result = ydl.extract_info(video_url, download=True)
                file_name = ydl.prepare_filename(result)
                file_name = file_name.replace(".webm", f".{file_type}")
                if filename_replaced is not None:
                    os.rename(file_name, filename_replaced)
                    file_name = filename_replaced
                return file_name

        except yt_dlp.utils.DownloadError as e:
            logging.error(f"Download error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
        return None
    

 
