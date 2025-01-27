
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

COPY . .


RUN python -m pip install --upgrade pip \
    && pip install --default-timeout=100 --no-cache-dir -r requirements.txt


# ENV STREAMLIT_SERVER_PORT 8080

# CMD ["streamlit", "run", "app_stream.py", "--server.port=8080", "--server.address=0.0.0.0"]
EXPOSE 8080
CMD ["uvicorn", "app_ydown:app", "--host", "0.0.0.0", "--port", "8080"]