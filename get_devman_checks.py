import argparse
import os

from dotenv import load_dotenv

import requests

import telegram


def get_devman_checks(auth_token, timestamp_to_request=None):
    headers = {
        'Authorization': f'Token {auth_token}'
    }
    params = {
        'timestamp': timestamp_to_request
    }
    devman_url = 'https://dvmn.org/api/long_polling/'
    response = requests.get(devman_url, headers=headers, params=params)
    response.raise_for_status()
    devman_checks = response.json()
    return devman_checks


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
    positive_message_template = 'У вас проверили работу.\n'
    'Результат: "Успешно"'
    while True:
        try:
            devman_checks = get_devman_checks(auth_token)
            if devman_checks['status'] == 'timeout':
                devman_checks_with_timestamp = get_devman_checks(
                    auth_token,
                    devman_checks['timestamp_to_request']
                )
                if devman_checks_with_timestamp['status'] == 'timeout':
                    continue
                elif devman_checks_with_timestamp['status'] == 'found':
                    new_attempts = devman_checks["new_attempts"]
                    for attempt in new_attempts:
                        if attempt["is_negative"]:
                            lesson_title = attempt["lesson_title"]
                            lesson_url = attempt["lesson_url"]
                            user_message = negative_message_template.format(
                                lesson_title,
                                lesson_url
                            )
                        else:
                            user_message = positive_message_template
                        bot_checking_tasks.send_message(
                            text=user_message, chat_id=args.chat_id)
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
                    else:
                        user_message = positive_message_template
                    bot_checking_tasks.send_message(
                        text=user_message,
                        chat_id=args.chat_id
                    )
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            continue


if __name__ == '__main__':
    main()
