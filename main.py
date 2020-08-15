import json
import os
import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv

def predict_rub_salary_hh(job_info):
    salary_info = job_info['salary']
    if salary_info["currency"] != 'RUR':
        return
    elif salary_info['from'] == None:
        return salary_info['to']*0.8
    elif salary_info['to'] == None:
        return salary_info['from']*1.2
    else:
        return (salary_info['from'] + salary_info['to']) // 2


def predict_rub_salary(vacancy):
    if ((not vacancy["payment_from"] and not vacancy["payment_to"])
     or vacancy["currency"] != 'rub'):
        return
    elif vacancy['payment_from'] == None:
        return vacancy['payment_to']*0.8
    elif vacancy['payment_to'] == None:
        return vacancy['payment_from']*1.2
    else:
        return (vacancy['payment_from'] + vacancy['payment_to']) // 2


def hh_get_salarys(hh_payload):
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


def create_table(result, languages):
    table_data = [
    ['Язык программирования', 'Вакансий найдено',
     'Вакансий обработано', 'Средняя зарплата']]
    for language in languages:
        vacancies_found = result[language]['vacancies_found']
        vacancies_processed = result[language]['vacancies_processed']
        average_salary = result[language]['average_salary']
        language_info = [language, vacancies_found, vacancies_processed, average_salary]
        table_data.append(language_info)
    table = AsciiTable(table_data)
    return table


def sj_get_salarys(sj_payload):
    page = 0
    salarys = []
    while True:
        sj_payload['page'] = page
        sj_response = requests.get(sj_url, headers=AUTH_TOKEN, params=sj_payload)
        for vacancy in sj_response.json()['objects']:
            salary = predict_rub_salary(vacancy)
            if salary:
                salarys.append(int(salary))
            page += 1
        if not sj_response.json()['more']:
            break
    return salarys


if __name__ == "__main__":
    sj_url = "https://api.superjob.ru/2.0/vacancies/"
    url_hh = "https://api.hh.ru/vacancies"
    load_dotenv()
    sj_token = os.getenv("SJ_TOKEN")
    AUTH_TOKEN = {'X-Api-App-Id': sj_token,}
    sj_payload = {'town': 4, 'count':100}
    hh_payload = {
        "period": 30, 
        "area": "1",
        'per_page': 100,
        "only_with_salary": True}
    result = {}
    languages = ['Python','Java','Javascript','Ruby','PHP','C++','C#','C','Go']
    for language in languages:
        sj_payload['keyword'] = f"{language} Разработчик"
        sj_response = requests.get(sj_url, headers=AUTH_TOKEN, params=sj_payload)
        salarys = []
        result[language] = {}
        hh_payload['text'] = f"{language} Разработчик"
        hh_response = requests.get(url_hh, params=hh_payload)
        result[language]['vacancies_found'] = hh_response.json()['found'] + sj_response.json()['total']
        sj_salarys = sj_get_salarys(sj_payload)
        hh_salarys = hh_get_salarys(hh_payload)
        salarys = sj_salarys + hh_salarys
        if len(salarys) != 0:
            result[language]['average_salary'] = int(sum(salarys)/len(salarys))
        result[language]['vacancies_processed'] = len(salarys)
    table = create_table(result, languages)
    print(table.table)


