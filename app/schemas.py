from pydantic import BaseModel, ConfigDict


class EmployeeBase(BaseModel):
    surname: str
    room_number: str
    department: str
    computer_info: str


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    surname: str | None = None
    room_number: str | None = None
    department: str | None = None
    computer_info: str | None = None


class EmployeeOut(EmployeeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
