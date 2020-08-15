import json
import os
from dotenv import load_dotenv
import requests


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

url = "	https://api.superjob.ru/2.0/vacancies/"
load_dotenv()
secret_key = os.getenv("SUPER_JOB_TOKEN")
AUTH_TOKEN = {'X-Api-App-Id': secret_key,}
payload = {'keyword': 'Программист', 'town': 4, 'payment_from': 9000}
response = requests.get(url, headers=AUTH_TOKEN, params=payload)
for vacancy in response.json()['objects']:
    salary = predict_rub_salary(vacancy)
    if salary:
        print(vacancy['profession'], 'Москва', salary)
    
with open('example.json', "w", encoding='utf-8') as my_file:
        json.dump(response.json(), my_file, indent=4, ensure_ascii=False)