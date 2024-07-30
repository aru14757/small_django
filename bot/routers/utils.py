import requests
import logging
from dotenv import load_dotenv
import os


load_dotenv()
LANGUAGE_API = os.getenv('LANGUAGE_API')
SEND_FEEDBACK = os.getenv('SEND_FEEDBACK')
USER_DATA = os.getenv('USER_DATA')

def update_user_language(telegram_id: int, language: str) -> bool:
    try:
        response = requests.post(LANGUAGE_API, json={"telegram_id": telegram_id, "language": language})
        response.raise_for_status()
        return response.json().get("success", False)
    except requests.RequestException as e:
        logging.error(f"Failed to update language for user_id {telegram_id}: {e}")
        return False


def read_user_data() -> dict:
    try:
        response_employees = requests.get(f"{USER_DATA}/get_employees/")
        response_employees.raise_for_status()
        employees_data = response_employees.json().get("get_employees", [])

        response_managers = requests.get(f"{USER_DATA}/get_managers/")
        response_managers.raise_for_status()
        managers_data = response_managers.json().get("get_managers", [])

        return {
            "employees": employees_data,
            "managers": managers_data,
        }
    except requests.RequestException as e:
        logging.error(f"Failed to get user data: {e}")
        return {"employees": [], "managers": []}


def read_employee_data() -> list:
    try:
        response = requests.get(f"{USER_DATA}/get_employees/")
        response.raise_for_status()
        data = response.json()
        return data.get("get_employees", [])
    except requests.RequestException as e:
        logging.error(f"Failed to get user data: {e}")
        return []


def send_feedback_to_server(username, user_id, message_type, response, time):
    data = {
        'name': username,
        'telegram_id': user_id,
        'message_type': message_type,
        'response': response,
        'time': time
    }
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(SEND_FEEDBACK, json=data, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send feedback: {e}")


async def get_language_from_server(telegram_id: int) -> str:
    try:
        users_data = read_user_data()
        all_users = users_data['employees'] + users_data['managers']
        user = next((user for user in all_users if user['telegram_id'] == telegram_id), None)

        if user:
            language = user.get('language', 'ru')
            if language not in ['ru', 'kk']:
                logging.warning(f"Unsupported language '{language}' for user '{telegram_id}'. Defaulting to 'ru'.")
                return 'ru'
            logging.info(f"Fetched language '{language}' for user '{telegram_id}'")
            return language
        else:
            logging.warning(f"User '{telegram_id}' not found.")
            return 'ru'
    except Exception as e:
        logging.error(f"Error while fetching user language: {e}")
        return 'ru'
