import os
import re

import pandas as pd

# Шаблон имени чека: 2023-02-15-10-26-0.csv  (ГГГГ-ММ-ДД-ЧЧ-ММ-N.csv)
FILE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d+\.csv$')
COLUMNS = ['date', 'product', 'store', 'cost']


def process_files(src_folder, dest_folder):
    frames = []
    for name in sorted(os.listdir(src_folder)):
        if not FILE_PATTERN.match(name):
            continue
        df = pd.read_csv(os.path.join(src_folder, name), sep=';')
        frames.append(df[COLUMNS])  # лишние столбцы (например, id) отбрасываем

    result = pd.concat(frames, ignore_index=True)
    # дата в ISO-формате (в данных есть "2023-02-30"), поэтому строковая сортировка корректна
    result = result.sort_values(['date', 'product'], kind='stable').reset_index(drop=True)

    os.makedirs(dest_folder, exist_ok=True)
    result.to_csv(os.path.join(dest_folder, 'combined_data.csv'), sep=',', index=False)
