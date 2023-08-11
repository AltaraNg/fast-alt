from sqlalchemy.orm import Session
from schemas.bank_statement_schema import BankStatementCreate
from models.bank_statement_model import BankStatement
from pydantic import ValidationError
from datetime import datetime


def create_bank_statement(db: Session, bank_statement_data: BankStatementCreate):
    try:
        db_bank_statement = BankStatement(
            account_name=bank_statement_data.account_name,
            account_number=bank_statement_data.account_number,
            opening_balance=bank_statement_data.opening_balance,
            closing_balance=bank_statement_data.closing_balance,
            total_deposit=bank_statement_data.total_deposit,
            total_withdrawal=bank_statement_data.total_withdrawal,
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
