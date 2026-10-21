"""Метрики активности пользователей: python solution.py [registrations.csv] [entries.csv]."""
import csv
import sys
from collections import defaultdict
from datetime import datetime, timedelta

DATE_FORMATS = ('%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d.%m.%Y', '%d/%m/%Y', '%m/%d/%Y')


def to_date(text):
    """Строка из CSV -> date (время, если есть, отбрасывается)."""
    text = text.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    # формат вида 2021-01-05T10:00:00 или с долями секунд
    return datetime.fromisoformat(text).date()


def read_dates(path, column):
    """Список пар (user_id, date) из CSV с колонками user_id и column."""
    with open(path, encoding='utf-8') as f:
        return [(row['user_id'], to_date(row[column])) for row in csv.DictReader(f, delimiter=';')]


def load(registrations_path='registrations.csv', entries_path='entries.csv'):
    """registrations: {user_id: дата регистрации}; entries: {user_id: множество дней, когда был вход}."""
    registrations = dict(read_dates(registrations_path, 'registration_date'))
    entries = defaultdict(set)
    for user_id, day in read_dates(entries_path, 'entry_date'):
        entries[user_id].add(day)
    return registrations, entries


def entry_days(registrations, entries, users):
    """Для каждого пользователя: на какие дни после регистрации (0, 1, 2, ...) приходятся его входы."""
    return {u: {(d - registrations[u]).days for d in entries.get(u, ())} for u in users}


def retention(registrations, entries, users, n):
    """Доля (в %) пользователей, зашедших ровно на n-й день после регистрации."""
    days = entry_days(registrations, entries, users)
    returned = sum(1 for u in users if n in days[u])
    return returned / len(users) * 100


def rolling_retention(registrations, entries, users, n):
    """Доля (в %) пользователей, зашедших на n-й день или позже."""
    days = entry_days(registrations, entries, users)
    returned = sum(1 for u in users if any(d >= n for d in days[u]))
    return returned / len(users) * 100


def lifetime(registrations, entries, users):
    """Сумма n-day retention (в долях) по всем дням: сколько дней в среднем пользователь активен."""
    days = entry_days(registrations, entries, users)
    counts = defaultdict(int)
    for u in users:
        for d in days[u]:
            if d >= 0:
                counts[d] += 1
    return sum(counts.values()) / len(users)


def active_users(entries, start, end):
    """Число уникальных пользователей, заходивших с start по end включительно."""
    return sum(1 for days in entries.values() if any(start <= d <= end for d in days))


def average_active(entries, period_key):
    """Среднее число уникальных пользователей по периодам (месяц/неделя/день)."""
    periods = defaultdict(set)
    for user_id, days in entries.items():
        for d in days:
            periods[period_key(d)].add(user_id)
    return sum(len(users) for users in periods.values()) / len(periods)


def month_key(d):
    return d.year, d.month


def week_key(d):
    return d.isocalendar()[:2]  # (год, номер недели по ISO)


def day_key(d):
    return d


def calculate(registrations, entries):
    all_users = list(registrations)
    january = [u for u, d in registrations.items() if d.month == 1]

    last_day = max(d for days in entries.values() for d in days)  # 31.12.2021
    month_start = last_day.replace(day=1)

    return {
        'retention_15_day': round(retention(registrations, entries, january, 15), 5),
        'rolling_retention': round(rolling_retention(registrations, entries, january, 30), 5),
        'lifetime': round(lifetime(registrations, entries, all_users), 5),
        'churn_29': round(1 - rolling_retention(registrations, entries, all_users, 29) / 100, 5),
        'dec_mau': active_users(entries, month_start, last_day),
        'dec_wau': active_users(entries, last_day - timedelta(days=6), last_day),
        'dec_dau': active_users(entries, last_day, last_day),
        'avg_mau': round(average_active(entries, month_key), 5),
        'avg_wau': round(average_active(entries, week_key), 5),
        'avg_dau': round(average_active(entries, day_key), 5),
    }


if __name__ == '__main__':
    paths = sys.argv[1:3] or ['registrations.csv', 'entries.csv']
    for name, value in calculate(*load(*paths)).items():
        print(f'{name:18} {value}')
