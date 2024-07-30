import os
import requests
from dotenv import load_dotenv

load_dotenv()
USERCHECK_API = os.getenv('USERCHECK_API')

def check_user_exists(telegram_id):
    params = {'telegram_id': telegram_id}

    try:
        response = requests.get(USERCHECK_API, params=params)
        if response.status_code == 200:
            data = response.json()
            user_exists = data.get('user_exists', False)
            return user_exists
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return False