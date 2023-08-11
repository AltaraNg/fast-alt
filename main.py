from fastapi import FastAPI, File, Form, UploadFile, Depends
from typing import Annotated
from bank_statement_reader.BankStatementExecutor import BankStatementExecutor

import models.bank_statement_model
from schemas.bank_statement_schema import BankStatementCreate, BankStatement
from config.database import SessionLocal, engine
from sqlalchemy.orm import Session
import os

from services.FileService import FileService
from services.BankStatementServiceCRUD import create_bank_statement

models.bank_statement_model.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/bank-statement-choices")
def get_bank_statement_choices():
    choices = BankStatementExecutor.BANK_STATEMENTS_CHOICES
    bank_statement_choices = []
    for choice in BankStatementExecutor.BANK_STATEMENTS_CHOICES:
        bank_statement_choices.append({"key": choice, "name": choices[choice] + " Bank"})
    return bank_statement_choices


@app.post("/upload")
def upload_bank_statement(
        bank_statement_pdf: Annotated[UploadFile, File()],
        bank_statement_choice: Annotated[str, Form()],
        min_salary: float = 10000,
        max_salary: float = 5000000,
        db: Session = Depends(get_db)
):
    executor = BankStatementExecutor()
    print(executor.BANK_STATEMENTS_CHOICES)
    result = executor.execute(int(bank_statement_choice), bank_statement_pdf.file)
    bank_statement_excel_file_path = result.excel_file_path
    bank_statement_excel_file_name = os.path.basename(bank_statement_excel_file_path)

    bank_statement_excel_file_path_salary = result.salary_excel_file_path
    bank_statement_excel_file_name_salary = os.path.basename(bank_statement_excel_file_path_salary)

    bank_statement_excel_response = FileService.upload_file(bank_statement_excel_file_path,
                                                            bank_statement_excel_file_name)
    bank_statement_excel_salary_response = FileService.upload_file(bank_statement_excel_file_path_salary,
                                                                   bank_statement_excel_file_name_salary)

    bank_statement = create_bank_statement(
        db,
        bank_statement_data=BankStatementCreate(
            account_name=result.account_name,
            account_number=result.account_number,
            opening_balance=result.opening_balance,
            closing_balance=result.closing_balance,
            total_deposit=result.total_deposits,
            total_withdrawal=result.total_withdrawals,
            salary_predictions_file_url=bank_statement_excel_salary_response.get('file_url'),
            exported_bank_statement_file_url=bank_statement_excel_response.get('file_url'),
            start_date=result.period.get('from_date'),
            end_date=result.period.get('to_date')
        )
    )
    return bank_statement
