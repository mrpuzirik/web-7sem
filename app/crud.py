from sqlalchemy.orm import Session
from app import models, schemas


def get_employee(db: Session, employee_id: int) -> models.Employee | None:
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()


def get_employees(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    department: str | None = None,
) -> list[models.Employee]:
    query = db.query(models.Employee)
    if department:
        query = query.filter(models.Employee.department == department)
    return query.offset(skip).limit(limit).all()


def create_employee(db: Session, employee: schemas.EmployeeCreate) -> models.Employee:
    db_employee = models.Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def update_employee(
    db: Session, employee_id: int, employee: schemas.EmployeeUpdate
) -> models.Employee | None:
    db_employee = get_employee(db, employee_id)
    if db_employee is None:
        return None
    update_data = employee.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_employee, key, value)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def delete_employee(db: Session, employee_id: int) -> bool:
    db_employee = get_employee(db, employee_id)
    if db_employee is None:
        return False
    db.delete(db_employee)
    db.commit()
    return True
