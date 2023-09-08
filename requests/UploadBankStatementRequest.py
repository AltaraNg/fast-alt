from pydantic import BaseModel
from typing import Annotated
from fastapi import File, Form, UploadFile


class UploadBankStatementRequest(BaseModel):
    customer_id: int
    bank_statement_pdf: UploadFile
    bank_statement_choice: int
    min_salary: float
    max_salary: float
