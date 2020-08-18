import os
import argparse
import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv


def predict_rub_salary(salary_info, payment_from, payment_to, rub):
    if salary_info['currency'] != rub:
        return
    elif salary_info[payment_from] is None:
        return salary_info[payment_to]*0.8
    elif salary_info[payment_to] is None:
        return salary_info[payment_from]*1.2
    else:
        return (salary_info[payment_from] + salary_info[payment_to]) // 2


def predict_rub_salary_hh(job_info):
    salary_info = job_info['salary']
    return predict_rub_salary(salary_info, 'from', 'to', 'RUR')


def predict_rub_salary_sj(vacancy):
    if not vacancy["payment_from"] and not vacancy["payment_to"]:
        return
    return predict_rub_salary(
        vacancy, 'payment_from', 'payment_to', 'rub')


def get_salaries_hh(hh_payload, hh_response):
    last_page = hh_response.json()['pages']
    salaries = []
    for page_hh in range(last_page + 1):
        hh_payload['page'] = page_hh
        response = requests.get(url_hh, params=hh_payload)
        for job_info in response.json()['items']:
            salary = predict_rub_salary_hh(job_info)
            if salary:
                salaries.append(int(salary))
    return salaries


def create_table(salaries_stastics, languages, table_title):
    table_heading = [['Язык программирования', 'Вакансий найдено',
                      'Вакансий обработано', 'Средняя зарплата']]
    for language in languages:
        vacancies_found = salaries_stastics[language]['vacancies_found']
        vacancies_processed = (
            salaries_stastics[language]['vacancies_processed'])
        average_salary = salaries_stastics[language]['average_salary']
        language_info = [
            language, vacancies_found, vacancies_processed, average_salary]
        table_heading.append(language_info)
    table = AsciiTable(table_heading, table_title)
    return table


def get_salaries_sj(sj_payload):
    page = 0
    salaries = []
    while True:
        sj_payload['page'] = page
        min_salary = 8000
        sj_response = requests.get(
            sj_url, headers=headers, params=sj_payload)
        for vacancy in sj_response.json()['objects']:
            salary = predict_rub_salary_sj(vacancy)
            if salary:
                if salary > min_salary:
                    salaries.append(int(salary))
            page += 1
        if not sj_response.json()['more']:
            break
    return salaries


def create_dict_salaries(language, total_vacancies, salaries, dict_name):
    dict_name[language] = {}
    dict_name[language]['vacancies_found'] = total_vacancies
    if len(salaries) != 0:
        dict_name[language]['average_salary'] = (
            int(sum(salaries)/len(salaries)))
    else:
        dict_name[language]['average_salary'] = 0
    dict_name[language]['vacancies_processed'] = len(salaries)
    return dict_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='''Этот проект позволяет узнать среднюю зарплату
        программистов в Москве через API: HeadHunter и SuperJob.''')
    parser.add_argument('prog_language', metavar='N', type=str, nargs='*',
                        default=['PHP'],
                        help='''Введите языки программирования
                        по которым хотите узнать среднюю зарплату''')
    parser.add_argument(
        '--skip_hh', action="store_true",
        help='Не делать таблицу hh.')
    parser.add_argument(
        '--skip_sj', action="store_true",
        help='Не делать таблицу sj.')

    args = parser.parse_args()
    languages = ['Python', 'Java', 'Javascript',
                 'Ruby', 'C++', 'C#', 'C', 'Go']
    languages += args.prog_language
    sj_url = "https://api.superjob.ru/2.0/vacancies/"
    url_hh = "https://api.hh.ru/vacancies"
    load_dotenv()
    sj_token = os.getenv("SJ_TOKEN")
    headers = {'X-Api-App-Id': sj_token}
    sj_payload = {'town': 4, 'count': 100}
    hh_payload = {
        "period": 30,
        "area": "1",
        'per_page': 100,
        "only_with_salary": True}
    sj_statistic = {}
    hh_statistics = {}
    for language in languages:
        if not args.skip_hh:
            hh_payload['text'] = f"{language} Разработчик"
            hh_response = requests.get(url_hh, params=hh_payload)
            hh_salaries = get_salaries_hh(hh_payload, hh_response)
            hh_total_vacancies = hh_response.json()['found']
            hh_info_salaries = create_dict_salaries(
                language, hh_total_vacancies, hh_salaries, hh_statistics)
        if not args.skip_sj:
            sj_payload['keyword'] = f"{language} Разработчик"
            sj_response = requests.get(
                sj_url, headers=headers, params=sj_payload)
            sj_salaries = get_salaries_sj(sj_payload)
            sj_total_vacancies = sj_response.json()['total']
            sj_info_salaries = create_dict_salaries(
                language, sj_total_vacancies, sj_salaries, sj_statistic)
    if not args.skip_hh:
        hh_table = create_table(
            hh_info_salaries, languages, 'headhunter Moscow')
        print(hh_table.table)
    if not args.skip_sj:
        sj_table = create_table(sj_info_salaries, languages, 'superjob Moscow')
        print(sj_table.table)
