import streamlit as st
from .yt_downloader import YTDownloader

st.title("Downloader")

url = st.text_input("Enter the YouTube URL:", "")
file_type = st.radio("Select file type:", ["mp3", "mp4"])
ydt = YTDownloader()

if st.button("Download"):
    if url.strip() == "":
        st.error("Please enter a valid URL.")
    else:
        file_name = ydt.download_video(url, file_type)
        st.success(f"File downloaded: {file_name}")

        if file_name.endswith(".mp4"):
            mime_type = "video/mp4"
        elif file_name.endswith(".mp3"):
            mime_type = "audio/mpeg"
        else:
            mime_type = "application/octet-stream"  # 기본 MIME 타입

        with open(file_name, "rb") as file:
            st.download_button(
                label="Click to download the file",
                data=file,
                file_name=file_name,
                mime=mime_type
            )
