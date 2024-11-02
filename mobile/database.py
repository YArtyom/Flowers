import requests

API_BASE_URL = "http://127.0.0.1:8000"


def get_current_user(token):
    """Функция для получения текущего пользователя."""
    response = requests.get(f"{API_BASE_URL}/user/current-user", headers={
        "Authorization": f"Bearer {token}"
    })
    # print(response.json())
    if response.status_code == 200:
        return response.json()
    else:
        return {}