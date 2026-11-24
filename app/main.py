from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, crud
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Employee Computers API",
    description="CRUD API для обліку співробітників, що мають комп'ютер",
    version="1.0.0",
)


@app.get("/", tags=["root"])
def root():
    return {"message": "Employee Computers API. Документація: /docs"}


@app.post("/employees/", response_model=schemas.EmployeeOut, status_code=status.HTTP_201_CREATED, tags=["employees"])
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    return crud.create_employee(db, employee)


@app.get("/employees/", response_model=list[schemas.EmployeeOut], tags=["employees"])
def read_employees(
    skip: int = 0,
    limit: int = 100,
    department: str | None = None,
    db: Session = Depends(get_db),
):
    return crud.get_employees(db, skip=skip, limit=limit, department=department)


@app.get("/employees/{employee_id}", response_model=schemas.EmployeeOut, tags=["employees"])
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = crud.get_employee(db, employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Співробітника не знайдено")
    return db_employee


@app.put("/employees/{employee_id}", response_model=schemas.EmployeeOut, tags=["employees"])
def update_employee(employee_id: int, employee: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    db_employee = crud.update_employee(db, employee_id, employee)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Співробітника не знайдено")
    return db_employee


@app.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["employees"])
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    success = crud.delete_employee(db, employee_id)
    if not success:
        raise HTTPException(status_code=404, detail="Співробітника не знайдено")
    return None
