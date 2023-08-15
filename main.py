from fastapi import FastAPI, File, Form, UploadFile, Depends
from typing import Annotated
from bank_statement_reader.BankStatementExecutor import BankStatementExecutor
import logging
import models.bank_statement_model
from schemas.bank_statement_schema import BankStatementCreate, BankStatement
from config.database import SessionLocal, engine
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from services.FileService import FileService
from services.BankStatementServiceCRUD import create_bank_statement
from services.MailService import MailService

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
    return JSONResponse(
        status_code=200,
        content=bank_statement_choices
    )


@app.post("/upload")
def upload_bank_statement(
        bank_statement_pdf: Annotated[UploadFile, File()],
        bank_statement_choice: Annotated[str, Form()],
        min_salary: Annotated[float, Form()] = 10,
        max_salary: Annotated[float, Form()] = 100,
        db: Session = Depends(get_db)
) -> JSONResponse:
    try:
        executor = BankStatementExecutor()
        print(min_salary, max_salary)
        result = executor.execute(choice=int(bank_statement_choice), pdf_file=bank_statement_pdf.file,
                                  min_salary=min_salary, max_salary=max_salary)
        bank_statement_excel_response = FileService.upload_file(
            FileService.get_export_file_path(result.excel_file_path))
        bank_statement_excel_salary_response = FileService.upload_file(
            FileService.get_export_file_path(result.salary_excel_file_path))

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
        return JSONResponse(
            status_code=200,
            content={
                "data": bank_statement,
                "message": "Bank statement successfully processed",
                "status": "success"
            },

        )
    except Exception as e:
        logging.exception(e)
        return JSONResponse(
            status_code=400,
            content={
                "status": "failed",
                "message": str(e),
            }
        )


@app.get('/send-email/asynchronous')
def send_mail():
    MailService.send_email_async("Testing", "tadewuyi@altaracredit.com", {'title': 'Hello World', 'name': 'John Doe'})
    return 'Success'
