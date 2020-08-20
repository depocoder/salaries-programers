import os
import argparse
import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv
from itertools import count


def predict_rub_salary(salary_from, salary_to):
    if salary_from is None:
        return salary_to*0.8
    elif salary_to is None:
        return salary_from*1.2
    else:
        return (salary_from + salary_to) // 2


def get_salaries_hh(language):
    url = "https://api.hh.ru/vacancies"
    salaries = []
    params = {
        "period": 30,
        "area": "1",
        'per_page': 100,
        "only_with_salary": True,
        'text': f'{language} Разработчик'}
    for page_hh in count(0):
        params['page'] = page_hh
        response = requests.get(url, params=params)
        decoded_response = response.json()
        for job_info in decoded_response['items']:
            salary_info = job_info['salary']
            if salary_info['currency'] == 'RUR':
                hh_salary_from = salary_info['from']
                hh_salary_to = salary_info['to']
                salary = predict_rub_salary(hh_salary_from, hh_salary_to)
                salaries.append(int(salary))
        if page_hh >= decoded_response['pages']:
            break
    hh_total_vacancies = decoded_response['found']
    return hh_total_vacancies, salaries


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


def get_salaries_sj(language):
    headers = {'X-Api-App-Id': sj_token}
    params = {'town': 4, 'count': 100}
    params['keyword'] = f"{language} Разработчик"
    salaries = []
    url = "https://api.superjob.ru/2.0/vacancies/"
    for page in count(0):
        params['page'] = page
        params['keyword'] = f"{language} Разработчик"
        min_salary = 8000
        sj_response = requests.get(url, headers=headers, params=params)
        sj_json_vacancies = sj_response.json()
        for vacancy in sj_json_vacancies['objects']:
            sj_salary_from = vacancy['payment_from']
            sj_salary_to = vacancy['payment_to']
            if vacancy['currency'] == 'rub':
                salary = predict_rub_salary(sj_salary_from, sj_salary_to)
                if salary > min_salary:
                    salaries.append(int(salary))
                page += 1
        if not sj_json_vacancies['more']:
            break
    sj_total_vacancies = sj_json_vacancies['total']
    return sj_total_vacancies, salaries


def create_statistics_salaries(language, total_vacancies,
                               salaries, statistics_salaries):
    statistics_salaries[language] = {}
    statistics_salaries[language]['vacancies_found'] = total_vacancies
    if len(salaries) != 0:
        statistics_salaries[language]['average_salary'] = (
            int(sum(salaries)/len(salaries)))
    else:
        statistics_salaries[language]['average_salary'] = 0
    statistics_salaries[language]['vacancies_processed'] = len(salaries)
    return statistics_salaries


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
    load_dotenv()
    sj_token = os.getenv("SJ_TOKEN")
    sj_payload = {'town': 4, 'count': 100}
    sj_statistic = {}
    hh_statistics = {}
    for language in languages:
        if not args.skip_hh:
            hh_total_vacancies, hh_salaries = get_salaries_hh(language)
            hh_info_salaries = create_statistics_salaries(
                language, hh_total_vacancies, hh_salaries, hh_statistics)
        if not args.skip_sj:
            sj_total_vacancies, sj_salaries = get_salaries_sj(language)
            sj_info_salaries = create_statistics_salaries(
                language, sj_total_vacancies, sj_salaries, sj_statistic)
    if not args.skip_hh:
        hh_table = create_table(
            hh_info_salaries, languages, 'HeadHunter Moscow')
        print(hh_table.table)
    if not args.skip_sj:
        sj_table = create_table(sj_info_salaries, languages, 'SuperJob Moscow')
        print(sj_table.table)
