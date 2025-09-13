from pydantic import BaseModel, Field, validator, field_validator
from typing import List, Optional
from datetime import date, datetime

class EmployeeBase(BaseModel):
    employee_id: str = Field(..., example="E123")
    name: str = Field(..., min_length=1)
    department: str = Field(..., min_length=1)
    salary: float = Field(..., ge=0)
    joining_date: date = Field(..., example="2023-01-15")
    skills: List[str] = Field(default_factory=list)

    @validator("skills", pre=True)
    def coerce_skills(cls, v):
        # allow string -> single element list, or comma-separated string
        if isinstance(v, str):
            # handle "a,b,c" or "a"
            if "," in v:
                return [s.strip() for s in v.split(",") if s.strip()]
            return [v]
        return v


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    # all fields optional for partial update
    name: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[float] = None
    joining_date: Optional[date] = None
    skills: Optional[List[str]] = None

    @field_validator("skills", mode="before")
    def coerce_skills(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            if "," in v:
                return [s.strip() for s in v.split(",") if s.strip()]
            return [v]
        return v
    
    model_config = {
        "extra": "forbid"
    }


class EmployeeOut(EmployeeBase):
    id: Optional[str] = None

    class Config:
        orm_mode = True
