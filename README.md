# Compassway Credit
API сервіс, який дозволить побудувати та змінити графік платежів за кредитом.

# Коментарій

## Технології
- Django
- Django Rest Framework
- Docker

## Інстрікція

Запуск тестів
```sh
$ docker compose -f docker-compose-test.yaml up --build
```
Запуск проекту
```sh
$ docker compose up --build -d
```
## Використання

Проект буде доступний за адресою 
```
http://127.0.0.1:8000/
```

### API
Створення графіка платежів. Данна адреса підтримуе CRUD
```
[POST] http://127.0.0.1:8000/api/schedule
```

Body
```json
{
	"amount": 1000,
	"loan_start_date": "10-01-2024",
	"number_of_payments": 4,
	"periodicity": "1m",
	"interest_rate": 0.1
}
```
Response
```json
{
    "id": 1,
    "amount": "1000.00",
    "loan_start_date": "2024-01-10",
    "number_of_payments": 4,
    "periodicity": "1m",
    "interest_rate": "0.10",
    "created_at": "2024-09-04T15:10:12.294474Z",
    "payments": [
        {
            "id": 1,
            "date": "2024-02-10",
            "principal": "246.90",
            "interest": "8.33",
            "is_fixed": false,
            "loan": 2
        },
        {
            "id": 2,
            "date": "2024-03-10",
            "principal": "248.95",
            "interest": "6.28",
            "is_fixed": false,
            "loan": 2
        },
        {
            "id": 3,
            "date": "2024-04-10",
            "principal": "251.03",
            "interest": "4.20",
            "is_fixed": false,
            "loan": 2
        },
        {
            "id": 4,
            "date": "2024-05-10",
            "principal": "253.12",
            "interest": "2.11",
            "is_fixed": false,
            "loan": 2
        }
    ]
}
```
Оновлення пдатежу
```
[POST] http://127.0.0.1:8000/api/schedule/<int:payment_id>/payments
```
BODY
```json
{
    "principal": 100
}
```
Response
```json
{
    "id": 2,
    "date": "2024-03-10",
    "principal": "100.00",
    "interest": "50.00",
    "is_fixed": true,
    "loan": 1
}
```

Переглянути всі платежі за позикою можна за посиланням:
```
[GET] http://127.0.0.1:8000/api/schedule/<int:loan_id>
```