import json
import pandas as pd
from sqlalchemy import engine as sql
from IPython import display
import os
import aiohttp, asyncio
import time
import environ

PATH_JSON_FILES = os.path.join(os.path.dirname(__file__), '..\\..\\..\\docs\\')
HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.12785 YaBrowser/13.12.1599.12785 Safari/537.36'}
NUM_VACANCIES = 0
START_TIME = time.time()

ENV = environ.Env()
environ.Env.read_env(os.path.dirname(__file__) + '\\..\\..\\..\\parser_hh\\.env')

async def get_page(current_page: int, session: aiohttp.ClientSession):
    params = {
        'text': 'NAME:Python',
        # 'area': 54,
        'schedule': 'remote',
        'page': current_page,
        'per_page': 100
    }
    resp = await session.get('https://api.hh.ru/vacancies', data=params, headers=HEADER)
    if resp.status == 200:
        #print(f'[INFO] GET PAGE: {current_page+1}')
        num_files = len(os.listdir(os.path.join(PATH_JSON_FILES, 'pagination\\')))
        nextFileName = os.path.join(PATH_JSON_FILES, 'pagination\\', '{}.json'.format(num_files))
        json_page = await resp.json()
        f = open(nextFileName, mode='w', encoding='utf8')
        f.write(json.dumps(json_page, ensure_ascii=False, indent=4))
        f.close()
        return json_page, current_page+1
    else:
        return {}, current_page+1

async def get_vacancies(page: int, session: aiohttp.ClientSession):
    page_json, current_page = await get_page(page, session)
    global NUM_VACANCIES
    for item in page_json['items']:
        resp = await session.get(item['url'], headers=HEADER)
        json_vac = await resp.json()
        nextFileName = os.path.join(PATH_JSON_FILES, 'vacancies\\', '{}.json'.format(item['id']))
        f = open(nextFileName, mode='w', encoding='utf8')
        f.write(json.dumps(json_vac, ensure_ascii=False, indent=4))
        f.close()
        #print(f'[INFO] GET VAC from {current_page} page: {item["id"]}')
        NUM_VACANCIES += 1
        time.sleep(0.25)
    if (page_json['pages'] - page) <= 1:
        return

def remove_files(path):
    for file in os.listdir(path):
        os.remove(os.path.join(path, file))


async def update_parse():
    dirs = ['pagination', r'vacancies']

    #Очистка старых данных
    for d in dirs:
        dir = os.path.join(PATH_JSON_FILES, d)
        remove_files(dir)

    async with aiohttp.ClientSession() as session:
        tasks = (get_vacancies(page, session) for page in range(0, 1))
        await asyncio.gather(*tasks)
        await session.close()

    print('[INFO] URL вакансий собраны')



def clear_db(db_connect):
    sqls = ["DELETE from main_skills", "DELETE from main_vacancies"]
    [db_connect.execute(sql) for sql in sqls]


def update_db():
    print('[INFO] URL вакансий собраны')
    IDs = []  # Список идентификаторов вакансий
    names = []  # Список наименований вакансий
    urls = []

    # Создаем списки для столбцов таблицы skills
    skills_vac = []  # Список идентификаторов вакансий
    skills_name = []  # Список названий навыков

    # Счетчик обработанных файлов установим в ноль
    cnt_docs = len(os.listdir(PATH_JSON_FILES + '\\vacancies'))
    i = 0

    for file in os.listdir(PATH_JSON_FILES + '\\vacancies'):

        # Открываем, читаем и закрываем файл
        f = open(PATH_JSON_FILES + '\\vacancies\\{}'.format(file), encoding='utf8')
        jsonText = f.read()
        f.close()

        json_vac = json.loads(jsonText)

        # Заполняем списки для таблиц
        IDs.append(int(json_vac['id']))
        names.append(json_vac['name'])
        urls.append(json_vac['alternate_url'])

        # Т.к. навыки хранятся в виде массива, то проходимся по нему циклом
        for skl in json_vac['key_skills']:
            skills_vac.append(int(json_vac['id']))
            skills_name.append(skl['name'])

        # Увеличиваем счетчик обработанных файлов на 1, очищаем вывод ячейки и выводим прогресс
        i += 1
        display.clear_output(wait=True)
        display.display('Готово {} из {}'.format(i, cnt_docs))
    ENV("DJANGO_ALLOWED_HOSTS")
    eng = sql.create_engine(ENV("DB_INFO"))
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
    asyncio.run(update_parse())
    print("[INFO] Время работы update_parse() {:.2f} sec".format(time.time() - START_TIME))
    print("[INFO] Количество вакансий:", NUM_VACANCIES)
    update_db()
    print('[INFO] PARSING DONE')

