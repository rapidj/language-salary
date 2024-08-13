import os
import requests
from dotenv import load_dotenv
import time
from terminaltables import AsciiTable


def fetch_sj_token(login, password, client_id, client_secret):
    params = {
        'login': login,
        'password': password,
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.get('https://api.superjob.ru/2.0/oauth2/password/', params=params)
    response.raise_for_status()
    sj_api = response.json()
    return sj_api['access_token']


def predict_salary(payment_from, payment_to):
    if payment_from and payment_to:
        return (payment_from + payment_to) / 2
    elif payment_from:
        return payment_from * 1.2
    elif payment_to:
        return payment_to * 0.8
    else:
        return 0


def predict_rub_salary_hh(vacancy):
    salary = vacancy.get('salary')
    if not salary or salary['currency'] != 'RUR':
        return None
    return predict_salary(salary.get('from'), salary.get('to'))


def fetch_vacancies_hh(text, page_limit):
    vacancies_url = 'https://api.hh.ru/vacancies'
    area_id = '1'
    vacancies_per_page = '100'
    params = {
        'text': text,
        'area': area_id,
        'per_page': vacancies_per_page,
    }
    all_vacancies = []

    page = 0
    pages_number = 1
    while page < pages_number and page < page_limit:
        params['page'] = page
        response = requests.get(vacancies_url, params=params)
        response.raise_for_status()
        vacancy_descriptions = response.json()
        all_vacancies.extend(vacancy_descriptions['items'])
        pages_number = vacancy_descriptions['pages']
        page += 1
        time.sleep(0.5)
    return all_vacancies, vacancy_descriptions['found']


def fetch_statistics_hh(languages, page_limit=1000):
    vacancies_hh = {}
    delay_time = 0.5

    for language in languages:
        vacancies, vacancies_found = fetch_vacancies_hh(language, page_limit)
        vacancies_processed = 0
        total_salary = 0
        for vacancy in vacancies:
            predicted_salary = predict_rub_salary_hh(vacancy)
            if predicted_salary:
                vacancies_processed += 1
                total_salary += predicted_salary

        average_salary = int(total_salary / vacancies_processed) \
            if vacancies_processed else 0
        salaries = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary,
        }

        vacancies_hh[language] = salaries
        time.sleep(delay_time)

    return vacancies_hh


def fetch_sj_vacancies(language, client_secret, token, page_limit=1000):
    vacancies_url = "https://api.superjob.ru/2.0/vacancies/"
    start_page_number = 0
    vacancies_per_page = 100
    city_name = 'Москва'
    headers = {
        'Host': 'api.superjob.ru',
        'X-Api-App-Id': client_secret,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Bearer {token}'
    }

    params = {
        'page': start_page_number,
        'count': vacancies_per_page,
        'town': city_name,
        'keyword': language
    }

    all_vacancies = []

    page = 0
    while True:
        params['page'] = page
        response = requests.get(vacancies_url, headers=headers, params=params)
        response.raise_for_status()

        vacancy_descriptions = response.json()
        all_vacancies.extend(vacancy_descriptions['objects'])
        if len(all_vacancies) >= vacancy_descriptions['total']:
            break
        if page >= page_limit:
            break
        page += 1
        time.sleep(0.5)
    return all_vacancies, vacancy_descriptions['total']


def fetch_sj_statistics(client_secret, token, languages, page_limit=1000):
    vacancies_sj = {}
    delay_time = 0.5

    for language in languages:
        vacancies, vacancies_found = fetch_sj_vacancies(
            language, client_secret, token, page_limit
        )
        vacancies_processed = 0
        total_salary = 0
        for vacancy in vacancies:
            predicted_salary = predict_salary(vacancy.get('payment_from'), vacancy.get('payment_to'))
            if predicted_salary:
                vacancies_processed += 1
                total_salary += predicted_salary

        average_salary = int(total_salary / vacancies_processed)\
            if vacancies_processed else 0
        vacancies_sj[language] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary,
        }
        time.sleep(delay_time)

    return vacancies_sj


def print_table(vacancy_descriptions, title):
    table_columns = [[
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата',
    ]]
    for language, stats in vacancy_descriptions.items():
        table_columns.append([
            language,
            stats['vacancies_found'],
            stats['vacancies_processed'],
            stats['average_salary']
        ])
    table = AsciiTable(table_columns, title)
    print(table.table)
    print()


def main():
    load_dotenv()
    sj_login = os.environ['SJ_LOGIN']
    sj_password = os.environ['SJ_PASSWORD']
    sj_client_id = os.environ['SJ_CLIENT_ID']
    sj_client_secret = os.environ['SJ_CLIENT_SECRET']
    sj_token = fetch_sj_token(sj_login, sj_password, sj_client_id, sj_client_secret)

    languages = [
        'Java',
        'C++',
        'JavaScript',
        'C#',
        'Python',
        'Go',
        'Kotlin',
        'Swift',
        'Ruby',
        'PHP'
    ]

    hh_lang_salaries = fetch_statistics_hh(languages)
    print_table(hh_lang_salaries, "HeadHunter Moscow")

    sj_lang_salaries = fetch_sj_statistics(sj_client_secret, sj_token, languages)
    print_table(sj_lang_salaries, "SuperJob Moscow")


if __name__ == '__main__':
    main()
