import requests

# 요청할 URL과 데이터 설정
url = "https://app-ydown-646543566973.asia-northeast3.run.app/download/"
# url = "https://127.0.0.0:8080/download/"
data = {
    "url": "https://youtu.be/SlPhMPnQ58k?si=55RxR7mWvOWtMwGC",  # 실제 유튜브 URL로 대체
    "file_type": "mp3"  # 또는 "mp4"
}

# POST 요청 보내기
response = requests.post(url, json=data)

# 응답 결과 출력
if response.status_code == 200:
    print("파일 다운로드 성공!")
    
    print("공개 URL:", response.json())
else:
    print(f"파일 다운로드 실패: {response.status_code}, {response.json()['detail']}")
