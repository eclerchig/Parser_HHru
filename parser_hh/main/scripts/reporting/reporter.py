import sqlalchemy
import pandas as pd
import math


class GenReport:
    def __init__(self):
        self._tokens_df = None
        self._skills = None
        self._pivot = None
        self._vacancies = None

    def get_tokens_sliced(self, range1=0, range2=0):
        if self._tokens_df is not None:
            return self._tokens_df.sort_values(by='idf', ascending=False)[range1: range2]
        else:
            return None

    def get_pivot(self):
        return self._pivot

    def get_skills(self):
        return self._skills

    def get_vacs_by_token(self, token):
        conn = sqlalchemy.create_engine(
            'postgresql://postgres:femupe95_eclerchig@localhost:5432/DB_vacancies_HH').connect()

        # Загружаем наименования вакансий
        sql = 'select name_vac, url_hh from public.main_vacancies'
        vacancies = pd.read_sql(sql, conn)

        # Закрываем соединение с БД
        conn.close()

        return vacancies[vacancies['name_vac'].astype("string").str.lower().str.contains(token)]

    def generate_cloud_code(self, range1, range2):
        ds = self.get_tokens_sliced(range1, range2)

        # Получаем максимальное и минимальное значения idf. Будем использовать их для установки
        # размера шрифта токена в облаке
        mx = self._tokens_df['idf'].max()
        mn = self._tokens_df['idf'].min()

        tags = ''

        for idx, tuple in enumerate(ds.sort_index().itertuples()):

            # Масштабируем значения idf от 0 до 1 и переворачиваем их,
            # чтобы максимальное значение стало минимальным.
            if mx > mn:
                # Задаем размер шрифта и высоту токена в облаке
                fs = int((((tuple.idf - mn) / (mx - mn)) * -1 + 1) * 30 + 15)
                hd = math.ceil(fs / 10) * 10 + 8
            else:
                fs = 40

            # Добавляем токен в облако в формате html. Токену назначаем функцию tag_click для
            # события клика. Сама функция описана ниже за пределами данного метода
            tag_tmpl = """<div class="tag-wrapper" style="height:{height}px">
                        <span id="cloud_{id}"onclick="tag_click(this.innerText)" class="tagword" style="font-size:{size}px">{name}</span>
                        </div>"""
            tags += tag_tmpl.format(id=idx, name=tuple.Index, size=fs, height=hd)
        tags += '<div class="clearfix"></div>'
        return tags

    def get_count_tokens(self):
        return self._tokens_df['idf'].count()

    def generate_tokens(self):
        conn = sqlalchemy.create_engine(
            'postgresql://postgres:femupe95_eclerchig@localhost:5432/DB_vacancies_HH').connect()

        # Загружаем наименования вакансий
        sql = 'select name_vac from public.main_vacancies'
        vacancies_name = pd.read_sql(sql, conn).name_vac

        # Загружаем навыки по вакансиям
        sql = """
            select
                v.name_vac,
                name_skill
            from
                public.main_skills s
                join public.main_vacancies v
                    on v.id = s.vacancy_id
        """

        self._skills = pd.read_sql(sql, conn)

        # Закрываем соединение с БД
        conn.close()

        # sklearn - библиотека, содержащая набор инструментов для машинного обучения.
        # feature_extraction.text извлекает признаки из текста, которые затем можно будет
        # использовать в моделировании. В нашем случае моделирование не требуется. Нам нужно
        # получить биграммы и их оценку
        from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer

        # Получим матрицу встрчаемости биграмм (токенов) для каждой вакансии
        # В качестве стоп-слов установим грейды сотрудников, т.е. нам
        # не важно Старший аналитик данных или Младший, нам важно, что он аналитик данных
        # Также исключаем биграммы, которые встречаются реже, чем в 1-ой тысячной всех вакансий
        cv = CountVectorizer(
            ngram_range=(1, 2),
            stop_words=['главный', 'эксперт', 'старший', 'для', 'по'],
            min_df=0.001
        )
        word_vector = cv.fit_transform(vacancies_name)

        # Рассчитаем меру idf (обратная частота документа)
        # Чем выше мера для конкретного токена, тем реже он встречается
        idf = TfidfTransformer().fit(word_vector)

        # Строим датафрейм с оценкой idf для каждого токена. Далее он понадобится для построения облака
        self._tokens_df = pd.DataFrame(idf.idf_, index=cv.get_feature_names_out(), columns=["idf"])
        # Строим датафрейм из матрицы частоты токенов, где в качестве строк вакансии,
        # токены в качестве столбцов. Далее используем его для получения списка вакансий, для
        # которых встречается конкретный токен
        self._pivot = pd.DataFrame(
            word_vector.toarray(),
            columns=cv.get_feature_names_out(),
            index=vacancies_name.values
        )


def create_tokens():
    report = GenReport()
    return report
