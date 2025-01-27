import requests

# 요청할 URL과 데이터 설정
# api_url = "https://127.0.0.0:8080/download/"
data = {
    "url": "",  # 
    "file_type": "mp4"  # 또는 "mp4"
}

# POST 요청 보내기
response = requests.post(api_url, json=data)

# 응답 결과 출력
if response.status_code == 200:
    print("파일 다운로드 성공!")
    
    print("공개 URL:", response.json())
else:
    print(f"파일 다운로드 실패: {response.status_code}, {response.json()['detail']}")
