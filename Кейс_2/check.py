"""Локальная проверка решения: строит отчёт по Installments.xlsx и сравнивает с эталоном."""
import pandas as pd

from solution import generate_report, load_from_excel

ANSWER_URL = 'https://gist.github.com/Vs8th/63832f093f4db8d8b251ba5d39571f3d/raw/student_debt.txt'

generate_report(*load_from_excel('Installments.xlsx'))

user_answer = pd.read_csv('student_debt_report.txt')
correct_answer = pd.read_csv(ANSWER_URL)

assert user_answer.shape == correct_answer.shape, f'Размеры: {user_answer.shape} != {correct_answer.shape}'
assert user_answer.columns.equals(correct_answer.columns), 'Названия столбцов не совпадают'
assert (user_answer == correct_answer).all().all(), 'Ответы не совпадают'
print('Поздравляем, проверки пройдены!', user_answer.shape)
