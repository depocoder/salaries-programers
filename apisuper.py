import json
import requests


def predict_rub_salary(vacancy):
    if vacancy["currency"] != 'RUR':
        return
    elif salary_info['from'] == None:
        return salary_info['to']*0.8
    elif salary_info['to'] == None:
        return salary_info['from']*1.2
    else:
        return (salary_info['from'] + salary_info['to']) // 2

url = "	https://api.superjob.ru/2.0/vacancies/"
secret_key = "v3.r.132760579.d32e4e43e08879a84f59239c248bd044ae5cd92c.9aee469a67de819b18d36a46489e329c118d0d20"
AUTH_TOKEN = {'X-Api-App-Id': secret_key,}
payload = {'keyword': 'Программист', 'town': 4}
response = requests.get(url, headers=AUTH_TOKEN, params=payload)
for vacancy in response.json()['objects']:
    print(vacancy['profession'], 'Москва', predict_rub_salary(vacancy))
    
with open('example.json', "w", encoding='utf-8') as my_file:
        json.dump(response.json(), my_file, indent=4, ensure_ascii=False)