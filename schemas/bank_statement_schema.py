import datetime
from pydantic import BaseModel, field_serializer


class BankStatementBase(BaseModel):
    customer_id: int | None = None
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
    repayment_capability: str | dict | list[dict] | None = []


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

    class Config:
        from_attributes = True
