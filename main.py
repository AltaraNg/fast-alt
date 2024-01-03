import logging
from typing import Dict
from fastapi import FastAPI, File, Form, UploadFile, Depends, Path, Request, Query, BackgroundTasks, HTTPException
from typing import Annotated
from bank_statement_reader.BankStatementExecutor import BankStatementExecutor
import models.BankStatementModel
import models.BankStatementDayEndTransactionsModel
import models.BankStatementTransactionsModel
from schemas.bank_statement_schema import BankStatement
from schemas.bank_statement_day_end_trans_schema import BankStatementTransactionOut
from config.database import SessionLocal, engine
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from exceptions.NotFoundException import NotFoundException
from services.FileService import FileService
from services.BankStatementServiceCRUD import create_bank_statement, get_bank_statement, all_bank_statements, \
    sync_with_end_of_day_transactions, bank_statement_exists, retrieve_bank_statement_repayment_capability, \
    sync_with_all_transactions, all_bank_statement_transactions
from services.MailService import MailService
from fastapi_pagination import add_pagination, Page
from fastapi.middleware.cors import CORSMiddleware
from config.ConfigService import config
from shutil import copyfileobj
import os
from fastapi.exceptions import RequestValidationError, ValidationException
from filters.BankStatementQueryParams import BankStatementQueryParams
from filters.BankStatementTransactionsQueryParams import BankStatementTransactionQueryParams
import requests
import tempfile
import shutil

Page = Page.with_custom_options(
    size=Query(15, ge=1, le=100),
)
models.BankStatementModel.Base.metadata.create_all(bind=engine, checkfirst=True)
models.BankStatementDayEndTransactionsModel.Base.metadata.create_all(bind=engine, checkfirst=True)
models.BankStatementTransactionsModel.Base.metadata.create_all(bind=engine, checkfirst=True)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
add_pagination(app)


@app.exception_handler(NotFoundException)
async def unicorn_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=404,
        content={
            "status": "failed",
            "message": exc.message,
        },
    )


@app.exception_handler(RequestValidationError)
@app.exception_handler(ValidationException)
async def validation_exception_handler(request, exc):
    validation_errors = format_validation_errors(exc.errors())
    return JSONResponse(
        status_code=422,
        content=validation_errors,
    )


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"Hello": "World1"}


@app.get("/bank-statement-choices", summary="Get all supported bank statement choices")
def get_bank_statement_choices() -> JSONResponse:
    choices = BankStatementExecutor.BANK_STATEMENTS_CHOICES
    bank_statement_choices = []
    for choice in BankStatementExecutor.BANK_STATEMENTS_CHOICES:
        bank_statement_choices.append({"key": choice, "name": choices[choice] + " Bank"})
    return JSONResponse(
        status_code=200,
        content=bank_statement_choices
    )


@app.post("/bank-statements", summary="Upload bank statement for processing")
async def store(
         bank_statement_choice: Annotated[int, Form()],
        customer_id: Annotated[int, Form()],
        bank_statement_pdf: Annotated[UploadFile, File(...)] = None,
        bank_statement_pdf_url: Annotated[str, Form()] = None, 
        min_salary: Annotated[float, Form()] = 100000,
        max_salary: Annotated[float, Form()] = 150000,
        password: Annotated[str, Form()] = '',
        # bank_statement_pdf: UploadFile =  File(None),
        background_tasks: BackgroundTasks = BackgroundTasks,
        db: Session = Depends(get_db),
) -> JSONResponse:
    if bank_statement_pdf and bank_statement_pdf_url:
        raise HTTPException(status_code=400, detail="Only provide either bank statement pdf or bank statement pdf url")
    
    if bank_statement_pdf_url:
        try:
            uploaded_file =  download_file(bank_statement_pdf_url)
            bank_statement_pdf = uploaded_file
        except Exception as e:
            print(e)
            raise e

    try:
        executor = BankStatementExecutor()

        result = executor.execute(choice=int(bank_statement_choice), pdf_file=bank_statement_pdf.file,
                                  min_salary=min_salary, max_salary=max_salary, password=password)
        uploaded_statement_exists = bank_statement_exists(db=db, account_number=result.account_number,
                                                          start_date=result.period.get('from_date'),
                                                          end_date=result.period.get('to_date')
                                                          )

        if uploaded_statement_exists is None:
            excel_file_full_path = FileService.get_export_file_path(result.excel_file_path)
            salary_excel_full_path = FileService.get_export_file_path(result.salary_excel_file_path)

            bank_statement_excel_response = FileService.upload_file(excel_file_full_path)
            bank_statement_excel_salary_response = FileService.upload_file(salary_excel_full_path)
            background_tasks.add_task(clean_exports, [excel_file_full_path, salary_excel_full_path])
            bank_statement_data = BankStatement.from_request_api(
                customer_id=customer_id, result=result,
                bank_statement_excel_salary_response=bank_statement_excel_salary_response,
                bank_statement_excel_response=bank_statement_excel_response
            )
            saved_bank_statement = create_bank_statement(db=db, bank_statement_data=bank_statement_data)
        else:
            saved_bank_statement = uploaded_statement_exists
        bank_statement_resource = BankStatement.from_model_to_resource(saved_bank_statement)
        sync_with_end_of_day_transactions(db, result.last_transaction_per_day, saved_bank_statement)
        sync_with_all_transactions(db, result.transactions, saved_bank_statement)
        return JSONResponse(
            status_code=200,
            content={
                "data": bank_statement_resource,
                "message": "Bank statement successfully processed",
                "status": "success"
            },
        )
    except Exception as e:
        logging.error(e)
        if config.app_env != 'local':
            bank_statement_name = executor.BANK_STATEMENTS_CHOICES.get(int(bank_statement_choice))
            pdf_file_path = create_upload_file(bank_statement_pdf)
            bank_statement_pdf_response = FileService.upload_file(pdf_file_path)
            print(bank_statement_pdf_response)
            background_tasks.add_task(clean_exports, [pdf_file_path])
            await MailService.send_email_async(
                subject="Bank Statement Processing Failed",
                email_to="tadewuyi@altaracredit.com",
                body={
                    "actual_error": str(e),
                    "bank_statement_name": bank_statement_name,
                    "min_salary": min_salary,
                    "max_salary": max_salary,
                    "file_name": bank_statement_pdf.filename,
                    "file_url": bank_statement_pdf_response.get('file_url', None),
                },
                template="bank_statement_processing_failed",
                attachment=pdf_file_path
            )
        return JSONResponse(
            status_code=400,
            content={
                "status": "failed",
                "message": str(e),
            }
        )



@app.get("/bank-statements", summary="Get paginated processed bank statements")
def index(
        bank_statement_query_params: BankStatementQueryParams = Depends(BankStatementQueryParams),
        db: Session = Depends(get_db)
) -> Page[BankStatement]:
    # query_params = bank_statement_query_params.__dict__
    bank_statements = all_bank_statements(db=db, filter_query=bank_statement_query_params)
    return bank_statements


@app.get("/bank-statements/{bank_statement_id}/transactions",
         summary="Get paginated processed bank statements transactions")
def get_bank_statement_transactions(
        bank_statement_id: int = Path(title="The ID of the bank statement to filter by"),
        bank_statement_query_params: BankStatementTransactionQueryParams = Depends(BankStatementTransactionQueryParams),
        db: Session = Depends(get_db)
) -> Page[BankStatementTransactionOut]:
    bank_statements = all_bank_statement_transactions(db=db, filter_query=bank_statement_query_params,
                                                      bank_statement_id=bank_statement_id)
    return bank_statements


@app.get("/bank-statements/{bank_statement_id}",
         summary="Retrieve a single bank statement by passing bank statement id")
def show(bank_statement_id: int = Path(title="The ID of the bank statement to get"),
         db: Session = Depends(get_db)):
    bank_statement = get_bank_statement(db, bank_statement_id)

    return JSONResponse(
        status_code=200,
        content={
            "data": jsonable_encoder(bank_statement),
            "message": "Bank statement successfully processed",
            "status": "success"
        },
    )


@app.get("/bank-statements/{bank_statement_id}/repayment/capability/{amount}",
         summary="Retrieve repayment capability from bank statement by passing bank statement id")
def get_bank_statement_repayment_capability(bank_statement_id: int = Path(title="The ID of the bank statement to filter by"),
         amount: float = Path(title="The amount of repayment"),
         db: Session = Depends(get_db)):
    bank_statement = retrieve_bank_statement_repayment_capability(db, bank_statement_id, amount)
    return JSONResponse(
        status_code=200,
        content={
            "data": bank_statement,
            "message": "Bank statement repayment capability retrieved",
            "status": "success"
        },
    )


def format_validation_errors(errors: Dict[str, str]) -> Dict[str, str]:
    formatted_errors = {}
    print(errors)
    for error in errors:
        field = error['loc'][1]
        error_message = error['msg']
        formatted_errors[field] = error_message
    return formatted_errors


def clean_exports(paths_to_files: list[str]):
    for path_to_file in paths_to_files:
        FileService.remove_file_from_dir(path_to_file)


def create_upload_file(uploaded_file: UploadFile = File(...)):
    folder_location = "exports/pdfs"
    if not os.path.exists(folder_location):
        os.makedirs(folder_location)
        # Get the file's content and save it locally
    with open(os.path.join(folder_location, uploaded_file.filename), "wb") as f:
        copyfileobj(uploaded_file.file, f)
    path = folder_location + "/" + uploaded_file.filename
    print(f"file {uploaded_file.filename} saved at {path}")
    return FileService.get_export_file_path(path)


def download_file(file_url: str):
    upload_file = None
    try:
        response = requests.get(file_url)
        file_content = response.content
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"Failed to fetch file from provided url: {file_url}")
    temp_file= tempfile.SpooledTemporaryFile()
   
    temp_file.write(file_content)
    try:
        temp_file.seek(0)
        upload_file = UploadFile(temp_file, filename=file_url.split("/")[-1])
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"Error occurred creating Upload File: {str(e)}")
    return upload_file