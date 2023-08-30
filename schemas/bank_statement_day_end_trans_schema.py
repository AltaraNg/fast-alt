import datetime
from pydantic import BaseModel, field_serializer
from models.BankStatementDayEndTransactionsModel import \
    BankStatementDayEndTransactions as BankStatementDayEndTransactionsModel

from typing import Any


class BankStatementDayEndTransactionBase(BaseModel):
    bank_statement_id: int
    balance: float | None
    deposit: float | None
    withdrawal: float | None
    transaction_date: str | datetime.date | datetime.datetime
    description: str | None


class BankStatementDayEndTransactionCreate(BankStatementDayEndTransactionBase):
    pass


class BankStatementDayEndTransactionOut(BankStatementDayEndTransactionBase):
    id: int
    created_at: str | datetime.datetime
    updated_at: str | datetime.datetime

    @field_serializer('transaction_date')
    def serialize_start_date(self, transaction_date: datetime.date, _info):
        return transaction_date.isoformat()

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime.date, _info):
        return created_at.__format__('%Y-%m-%d %H:%M:%S')

    @field_serializer('updated_at')
    def serialize_updated_at(self, updated_at: datetime.date, _info):
        return updated_at.__format__('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def from_model_to_resource(data: BankStatementDayEndTransactionsModel) -> dict[str, Any]:
        return BankStatementDayEndTransactionOut(
            id=data.id,
            bank_statement_id=data.bank_statement_id,
            balance=data.balance,
            deposit=data.deposit,
            withdrawal=data.withdrawal,
            transaction_date=data.transaction_date,
            description=data.description,
            created_at=data.created_at,
            updated_at=data.updated_at
        ).model_dump()

    @staticmethod
    def from_create_to_model(data: BankStatementDayEndTransactionCreate) -> BankStatementDayEndTransactionsModel:
        return BankStatementDayEndTransactionsModel(
            bank_statement_id=data.bank_statement_id,
            balance=data.balance,
            deposit=data.deposit,
            withdrawal=data.withdrawal,
            transaction_date=data.transaction_date,
            description=data.description,
        )

    @staticmethod
    def from_request_api(bank_statement_id: int, balance: float, deposit: float, withdrawal: float,
                         transaction_date: datetime.date | datetime.datetime,
                         description: str) -> BankStatementDayEndTransactionCreate:
        return BankStatementDayEndTransactionCreate(
            bank_statement_id=bank_statement_id,
            balance=balance,
            deposit=deposit,
            withdrawal=withdrawal,
            transaction_date=transaction_date,
            description=description,
        )

    class Config:
        from_attributes = True
