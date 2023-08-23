import datetime
from pydantic import BaseModel, field_serializer
from models.bank_statement_model import BankStatement as BankStatementBankModel
from bank_statement_reader.BankStatementFinalResultResponse import BankStatementFinalResultResponse
from typing import Any
class BankStatementBase(BaseModel):
    customer_id: int | None = None
    account_name: str | None
    account_number: str | None
    opening_balance: float | None
    closing_balance: float | None
    total_deposit: float | None
    total_withdrawal: float | None
    salary_predictions_file_url: str | None
    exported_bank_statement_file_url: str | None
    start_date: str | datetime.date | None
    end_date: str | datetime.date | None
    repayment_capability: str | dict | list[dict] | None = []
    average_monthly_balance: float | None = None
    predicted_average_salary: float | None = None


class BankStatementCreate(BankStatementBase):
    pass


class BankStatement(BankStatementBase):
    id: int
    created_at: str | datetime.datetime
    updated_at: str | datetime.datetime

    @field_serializer('start_date')
    def serialize_start_date(self, start_date: datetime.date, _info):
        return start_date.isoformat()

    @field_serializer('end_date')
    def serialize_end_date(self, end_date: datetime.date, _info):
        return end_date.isoformat()

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime.date, _info):
        return created_at.__format__('%Y-%m-%d %H:%M:%S')

    @field_serializer('updated_at')
    def serialize_updated_at(self, updated_at: datetime.date, _info):
        return updated_at.__format__('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def from_model_to_resource(bank_statement: BankStatementBankModel) -> dict[str, Any]:
        return BankStatement(
            id=bank_statement.id,
            customer_id=bank_statement.customer_id,
            account_name=bank_statement.account_name,
            account_number=bank_statement.account_number,
            opening_balance=bank_statement.opening_balance,
            closing_balance=bank_statement.closing_balance,
            total_deposit=bank_statement.total_deposit,
            total_withdrawal=bank_statement.total_withdrawal,
            predicted_average_salary=bank_statement.predicted_average_salary,
            average_monthly_balance=bank_statement.average_monthly_balance,
            salary_predictions_file_url=bank_statement.salary_predictions_file_url,
            exported_bank_statement_file_url=bank_statement.exported_bank_statement_file_url,
            start_date=bank_statement.start_date,
            end_date=bank_statement.end_date,
            created_at=bank_statement.created_at,
            updated_at=bank_statement.updated_at
        ).model_dump()

    @staticmethod
    def from_request_api(customer_id: int, result: BankStatementFinalResultResponse,
                         bank_statement_excel_salary_response: dict | None,
                         bank_statement_excel_response: dict | None) -> BankStatementCreate:
        return BankStatementCreate(
            customer_id=customer_id,
            account_name=result.account_name,
            account_number=result.account_number,
            opening_balance=result.opening_balance,
            closing_balance=result.closing_balance,
            total_deposit=result.total_deposits,
            total_withdrawal=result.total_withdrawals,
            predicted_average_salary=result.predicted_average_salary,
            average_monthly_balance=result.average_monthly_balance,
            salary_predictions_file_url=bank_statement_excel_salary_response.get('file_url'),
            exported_bank_statement_file_url=bank_statement_excel_response.get('file_url'),
            start_date=result.period.get('from_date'),
            end_date=result.period.get('to_date')
        )

    class Config:
        from_attributes = True
