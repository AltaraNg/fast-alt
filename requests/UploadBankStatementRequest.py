from pydantic import BaseModel
from typing import Annotated
from fastapi import File, Form, UploadFile


class UploadBankStatementRequest(BaseModel):
    # bank_statement_pdf: UploadFile
    bank_statement_choice: str
    min_salary: float = 10000
    max_salary: float = 5000000
