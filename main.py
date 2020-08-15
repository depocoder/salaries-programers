import json
import os
import requests


def predict_rub_salary(job_info):
        salary_info = job_info['salary']
        if salary_info["currency"] != 'RUR':
            return
        elif salary_info['from'] == None:
            return salary_info['to']*0.8
        elif salary_info['to'] == None:
            return salary_info['from']*1.2
        else:
            return (salary_info['from'] + salary_info['to']) // 2

if __name__ == "__main__":
    
    url_hh = "https://api.hh.ru/vacancies"

    payload = {
        "period": 30, 
        "area": "1",
        'per_page': 100,
        "only_with_salary": True}
    result = {}

    languages = ['Python','Java','Javascript','Ruby','PHP','C++','C#','C','Go']
    for language in languages:
        salarys = []
        result[language] = {}
        payload['text'] = f"{language} Разработчик"
        page_response = requests.get(url_hh, params=payload)
        result[language]['vacancies_found'] = page_response.json()['found']
        last_page = page_response.json()['pages']
        for page in range(last_page + 1):
            payload['page'] = page
            response = requests.get(url_hh, params=payload)
            for job_info in response.json()['items']:
                salary = predict_rub_salary(job_info)
                if salary:
                    print(salary)
                    salarys.append(salary)
        result[language]['average_salary'] = int(sum(salarys)/len(salarys))
        result[language]['vacancies_processed'] = len(salarys)
    print(result)
json_path = 'example.json'

with open(json_path, "w", encoding='utf-8') as my_file:
        json.dump(result, my_file, indent=4, ensure_ascii=False)

