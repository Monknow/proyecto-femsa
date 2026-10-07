from sqlalchemy import Column, Integer, String, DateTime, Float, func
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

MAX_NAME_LENGTH = 125

class Base(DeclarativeBase):
    pass

datetime_col: Mapped[datetime] = Column(DateTime, nullable = False, server_default = func.now())
int_col =  Column(Integer, nullable = False)
float_col =  Column(Integer, nullable = False)
string_col = Column(String, nullable = False)

class File(Base):
    __tablename__ = "Files"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str]
    creation_date: Mapped[datetime]
    load_date: Mapped[datetime]
    file_size_megabytes: Mapped[int]
    vulnerabilities_introduced: Mapped[int]
    vulnerabilities_fixed: Mapped[int]

class Historic(Base):
    __tablename__ = "Historic"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    # TODO: add each row of the processed df
    file_id: Mapped[int] = mapped_column(ForeignKey("Files.id"), nullable=False)
    status: Mapped[bool]
    
    