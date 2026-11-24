"""
Скрипт для наповнення бази даних тестовими записами.

Запуск:
    python seed_data.py
"""

from app.database import SessionLocal, engine
from app import models

models.Base.metadata.create_all(bind=engine)

sample_employees = [
    {
        "surname": "Коваленко",
        "room_number": "101",
        "department": "Бухгалтерія",
        "computer_info": "Dell OptiPlex 3080, inv. №00123",
    },
    {
        "surname": "Шевченко",
        "room_number": "203",
        "department": "IT-відділ",
        "computer_info": "HP EliteDesk 800 G6, inv. №00456",
    },
    {
        "surname": "Бондаренко",
        "room_number": "305",
        "department": "Відділ кадрів",
        "computer_info": "Lenovo ThinkCentre M720q, inv. №00789",
    },
    {
        "surname": "Мельник",
        "room_number": "101",
        "department": "Бухгалтерія",
        "computer_info": "Dell OptiPlex 3080, inv. №00124",
    },
    {
        "surname": "Ткаченко",
        "room_number": "204",
        "department": "IT-відділ",
        "computer_info": "HP EliteDesk 800 G6, inv. №00457",
    },
]


def seed():
    db = SessionLocal()
    try:
        existing = db.query(models.Employee).count()
        if existing > 0:
            print(f"У базі вже є {existing} записів. Наповнення пропущено.")
            return

        for data in sample_employees:
            db.add(models.Employee(**data))
        db.commit()
        print(f"Додано {len(sample_employees)} тестових записів.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
