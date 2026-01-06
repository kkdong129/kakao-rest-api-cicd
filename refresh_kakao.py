import requests
import os

# GitHub Secrets에서 정보 가져오기
client_id = os.environ.get('KAKAO_CLIENT_ID')
client_secret = os.environ.get('KAKAO_CLIENT_SECRET')
refresh_token = os.environ.get('KAKAO_REFRESH_TOKEN')

print(f"id: {client_id[:2]}****")
print(f"secret: {client_secret[:2]}****")
print(f"token: {client_token[:2]}****")

def send_kakao_message(access_token, is_success=True, error_msg=""):
    """나에게 카카오톡 메시지 보내기 (성공/실패 공용)"""
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # 상태에 따른 메시지 내용 분기
    if is_success:
        main_text = "카카오 토큰 갱신 성공!"
    else:
        main_text = f"카카오 토큰 갱신 실패!\n사유: {error_msg}"

    payload = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": f" {main_text}",
            "link": {
                "web_url": "https://github.com/kkdong129/kakao-rest-api-cicd/actions",
                "mobile_web_url": "https://github.com/kkdong129/kakao-rest-api-cicd/actions"
            },
            "button_title": "결과 확인"
        })
    }

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        print(f"카톡 알림 전송 완료 ({'성공' if is_success else '실패'} 알림)")
    else:
        print(f"카톡 알림 전송 실패: {response.json()}")

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print("카톡 메시지 전송 성공!")
    else:
        print(f"메시지 전송 실패: {response.json()}")

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
        new_access_token = result.get('access_token')
        print("새로운 액세스 토큰 발급 성공!")
        # 성공 메시지 전송
        send_kakao_message(new_access_token, is_success=True)
    else:
        error_info = result.get('error_description', 'Unknown Error')
        print(f"토큰 갱신 실패: {error_info}")

if __name__ == "__main__":
    refresh_access_token()