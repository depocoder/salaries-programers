import os
import argparse
import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv


def predict_rub_salary_hh(job_info):
    salary_info = job_info['salary']
    if salary_info["currency"] != 'RUR':
        return
    elif salary_info['from'] is None:
        return salary_info['to']*0.8
    elif salary_info['to'] is None:
        return salary_info['from']*1.2
    else:
        return (salary_info['from'] + salary_info['to']) // 2


def predict_rub_salary_sj(vacancy):
    if ((not vacancy["payment_from"] and not vacancy["payment_to"])
       or vacancy["currency"] != 'rub'):
        return
    elif vacancy['payment_from'] is None:
        return vacancy['payment_to']*0.8
    elif vacancy['payment_to'] is None:
        return vacancy['payment_from']*1.2
    else:
        return (vacancy['payment_from'] + vacancy['payment_to']) // 2


def get_salarys_hh(hh_payload):
    last_page = hh_response.json()['pages']
    salarys = []
    for page_hh in range(last_page + 1):
        hh_payload['page'] = page_hh
        response = requests.get(url_hh, params=hh_payload)
        for job_info in response.json()['items']:
            salary = predict_rub_salary_hh(job_info)
            if salary:
                salarys.append(int(salary))
    return salarys


def create_table(result, languages, title):
    table_data = [['Язык программирования', 'Вакансий найдено',
                   'Вакансий обработано', 'Средняя зарплата']]
    for language in languages:
        vacancies_found = result[language]['vacancies_found']
        vacancies_processed = result[language]['vacancies_processed']
        average_salary = result[language]['average_salary']
        language_info = [
            language, vacancies_found, vacancies_processed, average_salary]
        table_data.append(language_info)
    table = AsciiTable(table_data, title)
    return table


def get_salarys_sj(sj_payload):
    page = 0
    salarys = []
    while True:
        sj_payload['page'] = page
        sj_response = requests.get(
            sj_url, headers=AUTH_TOKEN, params=sj_payload)
        for vacancy in sj_response.json()['objects']:
            salary = predict_rub_salary_sj(vacancy)
            if salary:
                if salary > 8000:
                    salarys.append(int(salary))
            page += 1
        if not sj_response.json()['more']:
            break
    return salarys


def create_result(language, total_vacancies, salarys, dict):
    dict[language] = {}
    dict[language]['vacancies_found'] = total_vacancies
    if len(salarys) != 0:
        dict[language]['average_salary'] = int(sum(salarys)/len(salarys))
    else:
        dict[language]['average_salary'] = 0
    dict[language]['vacancies_processed'] = len(salarys)
    return dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='''Этот проект позволяет узнать среднюю зарплату
        программистов в Москве через API: HeadHunter и SuperJob.''')
    parser.add_argument('prog_language', metavar='N', type=str, nargs='*',
                        default=['PHP'],
                        help='''Введите языки программирования
                        по которым хотите узнать среднюю зарплату''')
    parser.add_argument(
        '--skip_hh', action="store_false",
        help='Не делать таблицу hh.')
    parser.add_argument(
        '--skip_sj', action="store_false",
        help='Не делать таблицу sj.')

    args = parser.parse_args()
    languages = ['Python', 'Java', 'Javascript',
                 'Ruby', 'C++', 'C#', 'C', 'Go']
    languages += args.prog_language
    sj_url = "https://api.superjob.ru/2.0/vacancies/"
    url_hh = "https://api.hh.ru/vacancies"
    load_dotenv()
    sj_token = os.getenv("SJ_TOKEN")
    AUTH_TOKEN = {'X-Api-App-Id': sj_token}
    sj_payload = {'town': 4, 'count': 100}
    hh_payload = {
        "period": 30,
        "area": "1",
        'per_page': 100,
        "only_with_salary": True}
    sj_dict = {}
    hh_dict = {}
    for language in languages:
        if args.skip_hh:
            hh_payload['text'] = f"{language} Разработчик"
            hh_response = requests.get(url_hh, params=hh_payload)
            hh_salarys = get_salarys_hh(hh_payload)
            hh_total_vacancies = hh_response.json()['found']
            hh_info_salarys = create_result(
                language, hh_total_vacancies, hh_salarys, hh_dict)
        if args.skip_sj:
            sj_payload['keyword'] = f"{language} Разработчик"
            sj_response = requests.get(
            sj_url, headers=AUTH_TOKEN, params=sj_payload)
            sj_salarys = get_salarys_sj(sj_payload)
            sj_total_vacancies = sj_response.json()['total']
            sj_info_salarys = create_result(
            language, sj_total_vacancies, sj_salarys, sj_dict)
    if args.skip_hh:
        hh_table = create_table(hh_info_salarys, languages, 'headhunter Moscow')
        print(hh_table.table)
    if args.skip_sj:
        sj_table = create_table(sj_info_salarys, languages, 'superjob Moscow')
        print(sj_table.table)
