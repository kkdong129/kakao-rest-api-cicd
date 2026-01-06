import requests
import os
import json
import datetime

# 1. GitHub Secrets에서 정보 가져오기
raw_data = {
    "CLIENT_ID": os.environ.get('KAKAO_CLIENT_ID', ''),
    "CLIENT_SECRET": os.environ.get('KAKAO_CLIENT_SECRET', ''),
    "REFRESH_TOKEN": os.environ.get('KAKAO_REFRESH_TOKEN', '')
}

# 2. 디버그용 리스트 생성 (보안을 위해 마스킹 처리)
debug_list = []
for key, value in raw_data.items():
    if value:
        # 앞, 뒤 5자만 남기고 나머지는 마스킹 처리
        masked_value = f"{value[:5]}...{value[-5:]}"
        debug_list.append(f"{key}: {masked_value}")
    else:
        debug_list.append(f"{key}: 값을 찾을 수 없습니다!")

# 3. 디버그 정보 출력
print("----- [DEBUG INFO: Environment Variables] -----")
for i in debug_list:
    print(i)
print("-----------------------------------------------")

# GitHub Secrets에서 정보 가져오기
client_id = raw_data["CLIENT_ID"]
client_secret = raw_data["CLIENT_SECRET"]
refresh_token = raw_data["REFRESH_TOKEN"]

def send_kakao_feed_message(access_token, is_success=True, expires_msg="", error_msg=""):
    """나에게 카카오톡 메시지 보내기 (피드 템플릿 사용)"""
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    title = f"Github actions 작업 결과"
    description = "카카오 토큰 갱신이 정상적으로 완료되었습니다.\n리프레시 토큰 남은 유효기간(일): {expires_msg}" if is_success else f"에러 발생: {error_msg}"

    # 피드(Feed) 템플릿 구조
    template_object = {
        "object_type": "feed",
        "content": {
            "title": title,
            "description": description,
            "image_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",  # 깃허브 로고 이미지
            "link": {
                "web_url": "https://github.com/kkdong129/kakao-rest-api-cicd/actions",
                "mobile_web_url": "https://github.com/kkdong129/kakao-rest-api-cicd/actions"
            }
        },
        "buttons": [
            {
                "title": "실행 결과 확인하기",
                "link": {
                    "web_url": "https://github.com/kkdong129/kakao-rest-api-cicd/actions",
                    "mobile_web_url": "https://github.com/kkdong129/kakao-rest-api-cicd/actions"
                }
            }
        ]
    }

    payload = {
        "template_object": json.dumps(template_object)
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        print(f"카톡 알림 전송 성공 ({'성공' if is_success else '실패'} 알림)")
    else:
        print(f"카톡 알림 전송 실패! 상태코드: {response.status_code}, 상세내용: {response.json()}")

def send_kakao_text_message(access_token, is_success=True, expires_msg= "", error_msg=""):
    """나에게 카카오톡 메시지 보내기 (성공/실패 공용)"""
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # 상태에 따른 메시지 내용 분기
    if is_success:
        main_text = f"Github actions 작업 결과: 카카오 토큰 갱신이 정상적으로 완료되었습니다.\n리프레시 토큰 남은 유효기간(일): {expires_msg}"
    else:
        main_text = f"Github actions 작업 결과: 에러 발생\n사유: {error_msg}"

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
        print(f"카톡 알림 전송 성공 ({'성공' if is_success else '실패'} 알림)")
    else:
        print(f"카톡 알림 전송 실패! 상태코드: {response.status_code}, 상세내용: {response.json()}")

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
        remained_seconds = result.get('refresh_token_expires_in')

        # 리프레시 토큰 만료일 확인 로직
        if remained_seconds:
            # 초 단위를 '일' 단위로 환산
            remained_days = remained_seconds / (60 * 60 * 24)
            print(f"알림: 리프레시 토큰의 유효기간이 약 {remained_days:.1f}일 남았습니다.")

            if remained_days < 7:
                print("경고: 리프레시 토큰 만료가 7일 미만입니다! 곧 업데이트가 필요합니다.")

        expires_msg = remained_days
        print("새로운 액세스 토큰 발급 성공!")
        print(f"new_access_token: {new_access_token[:5]}...{new_access_token[-5:]}")
        # 성공 메시지 전송
        # send_kakao_feed_message(new_access_token, is_success=True, expires_msg) # 피드 템플릿
        send_kakao_text_message(new_access_token, is_success=True, expires_msg) # 텍스트 템플릿
    else:
        error_info = result.get('error_description', 'Unknown Error')
        print(f"토큰 갱신 실패: {error_info}")

if __name__ == "__main__":
    refresh_access_token()
