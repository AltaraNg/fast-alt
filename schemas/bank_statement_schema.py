import datetime
from pydantic import BaseModel, field_serializer


class BankStatementBase(BaseModel):
    account_name: str
    account_number: str
    opening_balance: float
    closing_balance: float
    total_deposit: float
    total_withdrawal: float
    salary_predictions_file_url: str | None
    exported_bank_statement_file_url: str | None
    start_date: str | datetime.date
    end_date: str | datetime.date


class BankStatementCreate(BankStatementBase):
    pass


class BankStatement(BankStatementBase):
    id: int

    @field_serializer('start_date')
    def serialize_start_date(self, start_date: datetime.date, _info):
        return start_date.isoformat()

    @field_serializer('end_date')
    def serialize_end_date(self, end_date: datetime.date, _info):
        return end_date.isoformat()

    class Config:
        from_attributes = True
