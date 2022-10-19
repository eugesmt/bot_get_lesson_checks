import argparse
import os
import time

from dotenv import load_dotenv

import requests

import telegram


def main():
    load_dotenv()
    auth_token = os.environ['AUTHORIZATION_TOKEN']
    telegram_token = os.environ['TELEGRAM_TOKEN']
    bot_checking_tasks = telegram.Bot(token=telegram_token)
    parser = argparse.ArgumentParser(
        description='Программа посылает а телеграм чат полльзователя'
        'проверки заданий от https://dvmn.org/'
    )
    parser.add_argument(
        '--chat_id',
        help='Идентификатор чата пользователя'
    )
    args = parser.parse_args()
    negative_message_template = (
        'У вас проверили работу.\n'
        'Результат: "Не удачно"\n'
        'Название урока: {}\n'
        'Ссылка на урок: {}'
    )
    positive_message_template = 'У вас проверили работу: {}.\n'
    'Результат: "Успешно"'
    headers = {
        'Authorization': f'Token {auth_token}'
    }
    devman_url = 'https://dvmn.org/api/long_polling/'
    timestamp_to_request = ''
    params = {
        'timestamp': f'{timestamp_to_request}'
    }
    while True:
        try:
            response = requests.get(devman_url, headers=headers, params=params)
            response.raise_for_status()
            devman_checks = response.json()
            if devman_checks['status'] == 'timeout':
                timestamp_to_request = devman_checks['timestamp_to_request']
            elif devman_checks['status'] == 'found':
                new_attempts = devman_checks["new_attempts"]
                for attempt in new_attempts:
                    if attempt["is_negative"]:
                        lesson_title = attempt["lesson_title"]
                        lesson_url = attempt["lesson_url"]
                        user_message = negative_message_template.format(
                            lesson_title,
                            lesson_url
                        )
                    elif not attempt["is_negative"]:
                        lesson_title = attempt["lesson_title"]
                        user_message = positive_message_template.format(
                            lesson_title
                        )
                    bot_checking_tasks.send_message(
                        text=user_message,
                        chat_id=args.chat_id
                    )
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(30)
            continue


if __name__ == '__main__':
    main()
