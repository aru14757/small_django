import logging
import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger


from bot.routers.utils import read_user_data, get_language_from_server

logging.basicConfig(level=logging.INFO)

scheduler = AsyncIOScheduler()

load_dotenv()
MESSAGES_API = os.getenv('MESSAGES_API')

def read_messages(url=MESSAGES_API):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Request to {url} failed: {e}")
        return []

async def send_scheduled_message(bot, chat_id: int, message_text: str):
    logging.info(f"Sending message to chat_id {chat_id}: {message_text}")
    try:
        await bot.send_message(chat_id, message_text, parse_mode="HTML")
        logging.info(f"Message sent to chat_id {chat_id}.")
    except Exception as e:
        logging.error(f"Failed to send message to chat_id {chat_id}: {e}")

async def send_message_with_updated_language(bot, chat_id: int, manager_name: str, employee_name: str, employee_id: int, user_name: str, message_kz: str, message_ru: str):
    language = get_language_from_server(chat_id)
    message_template = message_kz if language == 'kk' else message_ru
    message_text = await format_message(bot, message_template, manager_name, employee_name, employee_id, user_name)
    await send_scheduled_message(bot, chat_id, message_text)

async def format_message(bot, template: str, manager_name: str, employee_name: str, employee_id: int, user_name: str) -> str:
    chat = await bot.get_chat(employee_id)
    username = chat.username if chat.username else "No username"
    return template.format(
        manager_name=manager_name,
        employee_name=f'<a href="tg://user?id={employee_id}">{employee_name}</a> (@{username})',
        user_name=user_name
    )

def get_employees_for_manager(manager, all_employees):
    supervised_ids = {emp['telegram_id'] for emp in manager.get('supervised_employees', [])}
    mentored_ids = {emp['telegram_id'] for emp in manager.get('mentored_employees', [])}
    return [emp for emp in all_employees if emp['telegram_id'] in supervised_ids or mentored_ids]

def get_message_args_employee(bot, item, emp, message):
    return [bot, item['telegram_id'], "", emp['name'], item['telegram_id'], emp['name'], message['message_kz'], message['message_ru']]

def get_message_args_manager(bot, item, emp, message):
    return [bot, item['telegram_id'], item['name'], emp['name'], emp['telegram_id'], emp['name'], message['message_kz'], message['message_ru']]

def schedule_messages_for_role(bot, role, get_role_items, get_message_args):
    users_data = read_user_data()
    messages = read_messages()
    role_items = get_role_items(users_data)
    logging.info(f"{role.title()}s found: {role_items}")

    for item in role_items:
        chat_id = item['telegram_id']
        name = item['name']
        employees = users_data.get('employees', [])

        logging.info(f"Scheduling for {role}: {name}")

        for emp in get_employees_for_manager(item, employees) if role == 'manager' else users_data.get('employees', []):
            first_day_str = emp.get('first_day')
            if not first_day_str:
                logging.warning(f"No first_day value for {role} {name}")
                continue

            try:
                first_day = datetime.strptime(first_day_str, "%Y-%m-%d").date()
            except ValueError as e:
                logging.error(f"Error parsing first_day for {role} {name}: {e}")
                continue

            for message in messages:
                if message['role'] == item['role']:
                    message_day = first_day + timedelta(days=int(message['day']) - 1)
                    scheduled_time = datetime.combine(message_day, datetime.strptime(message['time'], "%H:%M:%S").time())

                    if scheduled_time > datetime.now():
                        job_id = f"{role}_{chat_id}_{scheduled_time.isoformat()}"
                        if not scheduler.get_job(job_id):
                            scheduler.add_job(
                                send_message_with_updated_language,
                                DateTrigger(run_date=scheduled_time),
                                args=get_message_args(bot, item, emp, message),
                                id=job_id
                            )
                            logging.info(f"{role.title()} job scheduled for chat_id {chat_id} at {scheduled_time}")
                        else:
                            logging.info(f"Job for chat_id {chat_id} at {scheduled_time} already exists.")
                    else:
                        logging.info(f"Scheduled time {scheduled_time} is in the past for {name}.")

def schedule_messages_for_employees(bot):
    schedule_messages_for_role(
        bot,
        'employee',
        lambda data: data.get('employees', []),
        get_message_args_employee
    )

def schedule_messages_for_managers(bot):
    schedule_messages_for_role(
        bot,
        'manager',
        lambda data: data.get('managers', []),
        get_message_args_manager
    )

def new_scheduler():
    scheduler.start()
    logging.info("Scheduler started.")
