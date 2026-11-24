# Employee Computers API

CRUD-застосунок на FastAPI для обліку співробітників, що мають комп'ютер.

Поля запису: `surname` (прізвище), `room_number` (номер кімнати),
`department` (назва відділу), `computer_info` (дані про комп'ютер).

## Структура проєкту

```
employee_computers_app/
├── app/
│   ├── __init__.py
│   ├── main.py        # FastAPI застосунок і ендпоінти
│   ├── database.py     # підключення до БД
│   ├── models.py        # SQLAlchemy-модель Employee
│   ├── schemas.py       # Pydantic-схеми
│   └── crud.py           # функції створення/читання/оновлення/видалення
├── seed_data.py     # наповнення БД тестовими даними
├── requirements.txt
├── .env.example
└── README.md
```

## Яку базу даних краще використати

**Для навчання/розробки — SQLite** (вже налаштовано за замовчуванням).
Причини:
- не потрібно нічого встановлювати чи запускати окремо — це файл `employees.db`, що створюється автоматично;
- вбудована підтримка в Python (через SQLAlchemy);
- достатньо продуктивна для невеликих обсягів даних (десятки-сотні співробітників).

**Для реального/командного проєкту — PostgreSQL**. Причини:
- витримує паралельні запити від багатьох користувачів;
- підтримує складніші типи даних, обмеження цілісності, повнотекстовий пошук;
- легко розгортається в Docker або хмарі (наприклад, на сервері підприємства).

Завдяки SQLAlchemy перехід з SQLite на PostgreSQL не вимагає змін у коді
моделей/CRUD — достатньо змінити рядок підключення `DATABASE_URL`.

## Встановлення та запуск

```bash
# 1. Встановити залежності
pip install -r requirements.txt

# 2. Наповнити базу тестовими даними
python seed_data.py

# 3. Запустити сервер
uvicorn app.main:app --reload
```

Після запуску:
- API: http://127.0.0.1:8000
- Інтерактивна документація (Swagger): http://127.0.0.1:8000/docs

## Ендпоінти

| Метод | URL                    | Опис                                  |
|-------|------------------------|----------------------------------------|
| GET   | `/employees/`          | список усіх співробітників (можна фільтрувати `?department=...`) |
| GET   | `/employees/{id}`      | отримати одного співробітника          |
| POST  | `/employees/`          | створити новий запис                   |
| PUT   | `/employees/{id}`      | оновити запис                          |
| DELETE| `/employees/{id}`      | видалити запис                         |

Приклад тіла запиту для POST/PUT:
```json
{
  "surname": "Коваленко",
  "room_number": "101",
  "department": "Бухгалтерія",
  "computer_info": "Dell OptiPlex 3080, inv. №00123"
}
```

## Як підключити PostgreSQL замість SQLite

1. Встановити PostgreSQL (локально або через Docker):
   ```bash
   docker run --name employees-postgres \
     -e POSTGRES_PASSWORD=mypassword \
     -e POSTGRES_DB=employees_db \
     -p 5432:5432 -d postgres:16
   ```
2. Встановити драйвер:
   ```bash
   pip install psycopg2-binary
   ```
3. Задати змінну середовища `DATABASE_URL` (скопіювавши `.env.example` в `.env`
   і розкоментувавши потрібний рядок, або прямо в терміналі):
   ```bash
   export DATABASE_URL="postgresql+psycopg2://postgres:mypassword@localhost:5432/employees_db"
   ```
4. Запустити застосунок як звичайно — таблиці створяться автоматично при старті:
   ```bash
   uvicorn app.main:app --reload
   ```

Код застосунку залишається незмінним — `app/database.py` сам читає
`DATABASE_URL` зі змінних середовища.

## Розгортання в Docker

У проєкті вже є `Dockerfile` (образ застосунку) та `docker-compose.yml`
(база даних PostgreSQL + застосунок разом). Створювати нічого додатково
не потрібно — обидва файли лежать у корені проєкту, поруч з `requirements.txt`.

Що описано в `docker-compose.yml`:
- **сервіс `db`** — офіційний образ `postgres:16`, дані зберігаються
  в іменованому томі `pgdata` (не зникають при перезапуску контейнера);
- **сервіс `api`** — збирається з локального `Dockerfile`, чекає, поки
  БД стане готовою (`healthcheck`), і підключається до неї за
  `DATABASE_URL=postgresql+psycopg2://postgres:mypassword@db:5432/employees_db`
  (тут `db` — це ім'я сервіса-контейнера БД, Docker сам резолвить його як хост).

Запуск:
```bash
docker compose up --build
```
Після старту:
- API: http://localhost:8000/docs
- PostgreSQL: доступний ззовні на `localhost:5432` (user: `postgres`, password: `mypassword`, db: `employees_db`)

Наповнити базу тестовими даними всередині контейнера:
```bash
docker compose exec api python seed_data.py
```

Зупинити і прибрати контейнери (дані в томі `pgdata` залишаться):
```bash
docker compose down
```

Повністю видалити разом з даними:
```bash
docker compose down -v
```

**Важливо:** реквізити (пароль БД) у `docker-compose.yml` — навчальні
за замовчуванням. Для реального використання обов'язково зміни
`POSTGRES_PASSWORD` і відповідний `DATABASE_URL` на щось надійніше,
а ще краще — виніс їх у `.env`-файл і не комітьте його в репозиторій.
