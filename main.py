import logging
from typing import Dict
from fastapi import FastAPI, File, Form, UploadFile, Depends, Path, Request, Query, BackgroundTasks, HTTPException
from typing import Annotated
from bank_statement_reader.BankStatementExecutor import BankStatementExecutor
import models.bank_statement_model
from schemas.bank_statement_schema import BankStatementCreate, BankStatement
from config.database import SessionLocal, engine
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from exceptions.NotFoundException import NotFoundException
from services.FileService import FileService
from services.BankStatementServiceCRUD import create_bank_statement, get_bank_statement, all_bank_statements
from services.MailService import MailService
from fastapi_pagination import add_pagination, Page
from fastapi.middleware.cors import CORSMiddleware
from config.ConfigService import config
from shutil import copyfileobj
import os
from fastapi.exceptions import RequestValidationError, ValidationException
from filters.BankStatementQueryParams import BankStatementQueryParams

Page = Page.with_custom_options(
    size=Query(15, ge=1, le=100),
)
models.bank_statement_model.Base.metadata.create_all(bind=engine, checkfirst=True)

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
    print("here")
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
        customer_id: Annotated[int, Form()],
        bank_statement_pdf: Annotated[UploadFile, File(...)],
        bank_statement_choice: Annotated[int, Form()],
        min_salary: Annotated[float, Form()] = 100000,
        max_salary: Annotated[float, Form()] = 150000,
        password: Annotated[str, Form()] = '',
        background_tasks: BackgroundTasks = BackgroundTasks,
        db: Session = Depends(get_db),
) -> JSONResponse:
    try:
        executor = BankStatementExecutor()

        result = executor.execute(choice=int(bank_statement_choice), pdf_file=bank_statement_pdf.file,
                                  min_salary=min_salary, max_salary=max_salary, password=password)

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
        bank_statement = create_bank_statement(db=db, bank_statement_data=bank_statement_data)
        bank_statement_resource = BankStatement.from_model_to_resource(bank_statement)
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
            background_tasks.add_task(clean_exports, [pdf_file_path])
            await MailService.send_email_async(
                subject="Bank Statement Processing Failed",
                email_to="tadewuyi@altaracredit.com",
                body={
                    "actual_error": str(e),
                    "bank_statement_name": bank_statement_name,
                    "min_salary": min_salary,
                    "max_salary": max_salary,
                    "file_name": bank_statement_pdf.filename
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
