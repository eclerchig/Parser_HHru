import requests
import json
import time
import pandas as pd
from sqlalchemy import engine as sql
from IPython import display
import os


def getPage(page=0):
    params = {
        'text': 'NAME:Python',
        'area': 54,
        'page': page,
        'per_page': 100
    }

    req = requests.get('https://api.hh.ru/vacancies', params)
    data = req.content.decode()
    req.close()
    return data


def remove_files(path):
    for file in os.listdir(path):
        os.remove(os.path.join(path, file))


def update_parse():
    dirs = ['pagination', 'vacancies\\python']

    # очистка старых данных
    for d in dirs:
        dir = os.path.join(os.getcwd(), 'docs\\', d)
        remove_files(dir)

    for page in range(0, 20):
        jsObj = json.loads(getPage(page))

        nextFileName = os.path.join('.\\docs\\pagination\\', '{}.json'.format(len(os.listdir('.\\docs\\pagination\\'))))

        f = open(nextFileName, mode='w', encoding='utf8')
        f.write(json.dumps(jsObj, ensure_ascii=False, indent=4))
        f.close()

        for item in jsObj['items']:
            req = requests.get(item['url'])
            data = req.content.decode()
            req.close()

            # Создаем файл в формате json с идентификатором вакансии в качестве названия
            # Записываем в него ответ запроса и закрываем файл
            fileName = os.getcwd() + '\docs\\vacancies\\python\{}.json'.format(item['id'])
            f = open(fileName, mode='w', encoding='utf8')
            f.write(json.dumps(json.loads(data), indent=4))
            f.close()
            time.sleep(0.25)

        if (jsObj['pages'] - page) <= 1:
            break

        time.sleep(0.25)
        print(f"Получена страница {page}")

    print('Страницы поиска собраны')


def clear_db(db_connect):
    sqls = ["DELETE from main_skills", "DELETE from main_vacancies"]
    [db_connect.execute(sql) for sql in sqls]


def update_db():
    IDs = []  # Список идентификаторов вакансий
    names = []  # Список наименований вакансий
    urls = []


    # Создаем списки для столбцов таблицы skills
    skills_vac = []  # Список идентификаторов вакансий
    skills_name = []  # Список названий навыков

    # В выводе будем отображать прогресс
    # Для этого узнаем общее количество файлов, которые надо обработать
    # Счетчик обработанных файлов установим в ноль
    cnt_docs = len(os.listdir(os.getcwd() + '\\docs\\vacancies\\python'))
    i = 0

    for file in os.listdir(os.getcwd() + '\\docs\\vacancies\\python'):

        # Открываем, читаем и закрываем файл
        f = open(os.getcwd() + '\\docs\\vacancies\\python\\{}'.format(file), encoding='utf8')
        jsonText = f.read()
        f.close()

        # Текст файла переводим в справочник
        jsonObj = json.loads(jsonText)

        # Заполняем списки для таблиц
        IDs.append(int(jsonObj['id']))
        names.append(jsonObj['name'])
        urls.append(jsonObj['alternate_url'])

        # Т.к. навыки хранятся в виде массива, то проходимся по нему циклом
        for skl in jsonObj['key_skills']:
            skills_vac.append(int(jsonObj['id']))
            skills_name.append(skl['name'])

        # Увеличиваем счетчик обработанных файлов на 1, очищаем вывод ячейки и выводим прогресс
        i += 1
        display.clear_output(wait=True)
        display.display('Готово {} из {}'.format(i, cnt_docs))

    eng = sql.create_engine('postgresql://postgres:femupe95_eclerchig@localhost:5432/DB_vacancies_HH')
    CONN = eng.connect()

    clear_db(CONN)

    # Создаем пандосовский датафрейм, который затем сохраняем в БД в таблицу vacancies
    df = pd.DataFrame({'id': IDs, 'name_vac': names, 'url_hh': urls})
    df.to_sql('main_vacancies', CONN, schema='public', if_exists='append', index=False)

    df = pd.DataFrame({'vacancy_id': skills_vac, 'name_skill': skills_name})
    df.to_sql('main_skills', CONN, schema='public', if_exists='append', index=False)

    CONN.close()
    # Выводим сообщение об окончании программы
    display.clear_output(wait=True)
    display.display('Вакансии загружены в БД')


def start():
    update_parse()
    update_db()
    print('PARSING DONE')




