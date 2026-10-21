"""Локальная проверка решения: считает метрики и сравнивает с эталоном metrics.txt (как в курсе)."""
from solution import calculate, load

# порядок строк в metrics.txt
NAMES = ['retention_15_day', 'rolling_retention', 'lifetime', 'churn_29',
         'dec_mau', 'dec_wau', 'dec_dau', 'avg_mau', 'avg_wau', 'avg_dau']

with open('metrics.txt') as f:
    answers = f.read().split('\n')

result = calculate(*load('registrations.csv', 'entries.csv'))

failed = 0
for name, answer in zip(NAMES, answers):
    ok = result[name] == float(answer)
    failed += not ok
    print(f"{'OK ' if ok else 'ERR'} {name:18} {result[name]!s:>10}  (эталон {answer})")

assert not failed, f'Не совпало метрик: {failed}'
print('Поздравляем, все проверки пройдены!')
