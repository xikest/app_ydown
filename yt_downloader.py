import json
import yt_dlp
import streamlit as st

json_path = "./json/yt_options.json"  # 옵션 파일 경로

class YTDownloader:
    @staticmethod
    def download_video(video_url: str, file_type: str) -> str:
        with open(json_path, 'r', encoding='utf-8') as file:
            options = json.load(file)
        
        try:
            # yt-dlp로 파일 다운로드
            with yt_dlp.YoutubeDL(options.get(file_type)) as ydl:
                result = ydl.extract_info(video_url, download=True)
                file_name = ydl.prepare_filename(result)
                
                # .webm 파일을 mp4 또는 mp3로 변환하지 않고 그대로 저장
                file_name = file_name.replace(".webm", f".{file_type}")
                return file_name

        except yt_dlp.utils.DownloadError as e:
            st.error(f"Download error: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
        return None