from sqlalchemy.orm import Session
from schemas.bank_statement_schema import BankStatementCreate, BankStatement as BankStatementSchema
from models.bank_statement_model import BankStatement
from pydantic import ValidationError
from datetime import datetime
from exceptions.NotFoundException import NotFoundException
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select,asc,desc
from fastapi_pagination import Page
from pydantic import Field

Page = Page.with_custom_options(
    size=Field(15, ge=1, le=100)
)


def create_bank_statement(db: Session, bank_statement_data: BankStatementCreate):
    try:
        db_bank_statement = BankStatement(
            customer_id=bank_statement_data.customer_id,
            repayment_capability=bank_statement_data.repayment_capability,
            account_name=bank_statement_data.account_name,
            account_number=bank_statement_data.account_number,
            opening_balance=bank_statement_data.opening_balance,
            closing_balance=bank_statement_data.closing_balance,
            total_deposit=bank_statement_data.total_deposit,
            total_withdrawal=bank_statement_data.total_withdrawal,
            average_monthly_balance=bank_statement_data.average_monthly_balance,
            predicted_average_salary=bank_statement_data.predicted_average_salary,
            salary_predictions_file_url=bank_statement_data.salary_predictions_file_url,
            exported_bank_statement_file_url=bank_statement_data.exported_bank_statement_file_url,
            start_date=datetime.strptime(bank_statement_data.start_date, "%Y-%m-%d"),
            end_date=datetime.strptime(bank_statement_data.end_date, "%Y-%m-%d")
        )
        db.add(db_bank_statement)
        db.commit()
        db.refresh(db_bank_statement)
        return db_bank_statement
    except ValidationError as validation_error:
        raise validation_error
    except Exception as e:
        raise e


def get_bank_statement(db: Session, bank_statement_id):
    item = db.query(BankStatement).filter(BankStatement.id == bank_statement_id).first()
    if item is None:
        raise NotFoundException(f"The provided bank statement id: {bank_statement_id} could not be found")
    # print(item.dict())
    return item


def all_bank_statements(db: Session) -> Page[BankStatementSchema]:
    bank_statements = paginate(db, select(BankStatement).order_by(desc('created_at')))
    return bank_statements
