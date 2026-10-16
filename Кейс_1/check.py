"""Локальная проверка решения: скачивает данные и эталон, запускает process_files и сравнивает."""
import io
import urllib.request
import zipfile

import pandas as pd

from solution import process_files

ZIP_URL = 'https://github.com/vs8th/reports/archive/main.zip'
ANSWER_URL = 'https://gist.github.com/Vs8th/9347dd7b8f59de2997feb19770dc32c1/raw/data.csv'

# Файлы с кириллицей в именах (Year 2010-2011-Т...) нужны только как "мусор":
# на их имена распаковка может ругаться, поэтому пропускаем то, что не удалось записать.
with urllib.request.urlopen(ZIP_URL) as r:
    archive = zipfile.ZipFile(io.BytesIO(r.read()))
for member in archive.namelist():
    try:
        archive.extract(member, 'reports_data')
    except OSError:
        print('пропущен файл:', repr(member))

process_files('reports_data/reports-main', 'comb_reports')

user_answer = pd.read_csv('comb_reports/combined_data.csv')
correct_answer = pd.read_csv(ANSWER_URL)

assert user_answer.shape == correct_answer.shape, f'Размеры: {user_answer.shape} != {correct_answer.shape}'
assert user_answer.columns.equals(correct_answer.columns), 'Названия столбцов не совпадают'
assert (user_answer == correct_answer).all().all(), 'Ответы не совпадают'
print('Поздравляем, проверки пройдены!', user_answer.shape)
