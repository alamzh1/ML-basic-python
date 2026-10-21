"""Отчёт о должниках по рассрочкам: python solution.py [--google "Имя таблицы"]."""
import argparse
from datetime import date, datetime

REPORT_DATE = date(2023, 3, 1)  # долги считаем на эту дату
PERIOD_DAYS = 183               # платежи вносятся раз в 6 месяцев
DATE_FORMATS = ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%m/%d/%Y')
SHEETS = ('Лист1', 'Лист2', 'Лист3')
SCOPE = ['https://www.googleapis.com/auth/spreadsheets.readonly',
         'https://www.googleapis.com/auth/drive']


def to_date(value):
    """Приводит значение ячейки (datetime, date или строка) к date."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip().split(' ')[0]
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f'Не удалось распознать дату: {value!r}')


def overdue_payments(expected_date):
    """Сколько платежей просрочено на REPORT_DATE, если первый ожидался в expected_date."""
    days = (REPORT_DATE - expected_date).days
    if days < 0:
        return 0
    return days // PERIOD_DAYS + 1


def generate_report(sheet1, sheet2, sheet3):
    # Лист2 и Лист3 превращаем в словари "id студента -> строка" для быстрого поиска
    schedule = {row['student_id']: row for row in sheet2}
    amounts = {row['student_id']: row for row in sheet3}

    lines = []
    for student in sheet1:
        student_id = student['student_id']
        # интересуют только студенты с рассрочкой, у которых есть данные на обоих листах
        if student['installment'] != 'Y' or student_id not in schedule or student_id not in amounts:
            continue

        count = overdue_payments(to_date(schedule[student_id]['expected_payment_date']))
        money = amounts[student_id]
        # долг не может быть больше, чем осталось выплатить по рассрочке
        debt = min(count * int(money['one-time_payment']), int(money['left_to_pay']))

        if debt > 0:
            lines.append(f"Студент {student['student_name']} - долг {debt} рублей")

    with open('student_debt_report.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def load_from_google(table_name, creds_file='creds.json'):
    """Три листа из Google Sheets в виде списков словарей."""
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, SCOPE)
    client = gspread.authorize(creds)
    table = client.open(table_name)
    return [table.worksheet(name).get_all_records() for name in SHEETS]


def load_from_excel(path='Installments.xlsx'):
    """Те же три листа из локальной выгрузки таблицы в Excel."""
    import pandas as pd

    book = pd.read_excel(path, sheet_name=list(SHEETS))
    return [book[name].to_dict('records') for name in SHEETS]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Отчёт о долгах студентов по рассрочкам')
    parser.add_argument('--google', metavar='TABLE', help='имя таблицы в Google Sheets (нужен creds.json)')
    parser.add_argument('--creds', default='creds.json', help='файл ключа сервисного аккаунта')
    parser.add_argument('--excel', default='Installments.xlsx', help='локальный файл, если --google не указан')
    args = parser.parse_args()

    if args.google:
        sheets = load_from_google(args.google, args.creds)
    else:
        sheets = load_from_excel(args.excel)

    generate_report(*sheets)
    with open('student_debt_report.txt', encoding='utf-8') as f:
        count = sum(1 for _ in f)
    print(f'Отчёт сохранён в student_debt_report.txt, должников: {count}')
