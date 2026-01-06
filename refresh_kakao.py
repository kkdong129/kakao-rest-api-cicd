import requests
import os

# GitHub Secrets에서 정보 가져오기
client_id = os.environ.get('KAKAO_CLIENT_ID')
client_secret = os.environ.get('KAKAO_CLIENT_SECRET')
refresh_token = os.environ.get('KAKAO_REFRESH_TOKEN')


def refresh_access_token():
    url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }

    response = requests.post(url, data=data)
    result = response.json()

    if response.status_code == 200:
        print("새로운 액세스 토큰 발급 성공!")
        print(f"Access Token: {result.get('access_token')}")
        # 실제 QA 업무라면 여기서 발급된 토큰을 DB에 저장하거나 알림을 보낼 수 있습니다.
    else:
        print(f"실패 원인: {result}")


if __name__ == "__main__":
    refresh_access_token()