from models.bank_statement_model import BankStatement
from datetime import datetime, timedelta

from sqlalchemy import between
from fastapi import Query


class BankStatementQueryParams:
    account_number: str = None
    account_name: str = None
    customer_id: int = None
    status: str = None
    bank_statement_choice: int = None
    from_date: str | datetime = None
    to_date: str | datetime = None

    def __init__(self,
                 account_number=Query(
                     None,
                     description="Filter bank statements by exact match on account number",
                     example="7777191"
                 ),
                 account_name=Query(
                     None,
                     description="Filter bank statements by account name containing this string",
                     example="John Doe"
                 ),
                 status=Query(
                     None,
                     description="(COMING SOON....) Filter bank statements by status ",
                     example="pending"),
                 customer_id=Query(
                     None,
                     description="Filter bank statements by exact match on customer id",
                     example=23
                 ),
                 bank_statement_choice=Query(
                     None,
                     description="(COMING SOON....) Filter bank statements by exact bank statement_choice",
                     example=1
                 ),
                 from_date=Query(
                     None,
                     description="Filter bank statements created on or after this date (Y-m-d)",
                     example="2023-08-21"
                 ),

                 to_date=Query(
                     None,
                     description="Filter bank statements created on or before this date (Y-m-d)",
                     example="2023-12-21"
                 )
                 ):
        self.account_number = account_number
        self.account_name = account_name
        self.status = status
        self.customer_id = customer_id
        self.bank_statement_choice = bank_statement_choice
        self.from_date = from_date
        self.to_date = to_date

    def apply(self, query):
        if self.account_name:
            query = query.filter(BankStatement.account_name.ilike(f"%{self.account_name}%"))
        if self.account_number:
            query = query.filter(BankStatement.account_number == self.account_number)
        # if self.bank_statement_choice:
        #     query = query.filter(BankStatement.bank_statement_choice == self.bank_statement_choice)
        if self.customer_id:
            query = query.filter(BankStatement.customer_id == self.customer_id)
        if self.from_date:
            self.from_date = datetime.now() if not self.from_date else datetime.strptime(self.from_date, "%Y-%m-%d")
            self.to_date = self.from_date + timedelta(days=30) if self.to_date is None else datetime.strptime(self.to_date, "%Y-%m-%d")
            query = query.filter(between(BankStatement.created_at, self.from_date, self.to_date))
        return query
