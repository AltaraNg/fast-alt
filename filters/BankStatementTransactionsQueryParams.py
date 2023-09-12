from models.BankStatementTransactionsModel import BankStatementTransactionsModel
from datetime import datetime, timedelta

from sqlalchemy import between
from fastapi import Query


class BankStatementTransactionQueryParams:
    max_deposit: float = None
    min_deposit: float = None

    max_withdrawal: float = None
    min_withdrawal: float = None

    # bank_statement_id: int = None
    description: str = None

    transaction_from_date: str | datetime = None
    transaction_to_date: str | datetime = None

    def __init__(self,
                 # bank_statement_id=Query(
                 #     None,
                 #     description="Filter bank statements by exact match bank statement id",
                 #     example=1
                 # ),
                 max_deposit=Query(
                     None,
                     description="Filter bank statements by max deposit, its dependent on min deposit",
                     example=3000
                 ),
                 min_deposit=Query(
                     None,
                     description="Filter bank statements by min deposit, its dependent on max deposit",
                     example=1000
                 ),
                 max_withdrawal=Query(
                     None,
                     description="Filter bank statements by max withdrawal, its dependent on min withdrawal",
                     example=3000
                 ),
                 min_withdrawal=Query(
                     None,
                     description="Filter bank statements by min withdrawal, its dependent on max withdrawal",
                     example=1000
                 ),
                 description=Query(
                     None,
                     description="Filter bank statements by exact bank statement_choice",
                     example="POS"
                 ),
                 transaction_from_date=Query(
                     None,
                     description="Filter bank statements transaction date on or after this date (Y-m-d)",
                     example="2023-08-21"
                 ),

                 transaction_to_date=Query(
                     None,
                     description="Filter bank statements transaction date on or before this date (Y-m-d)",
                     example="2023-12-21"
                 )
                 ):
        self.max_deposit = max_deposit
        self.min_deposit = min_deposit
        self.max_withdrawal = max_withdrawal
        self.min_withdrawal = min_withdrawal
        self.description = description
        self.transaction_to_date = transaction_to_date
        self.transaction_from_date = transaction_from_date

    def apply(self, query):
        if self.description:
            query = query.filter(BankStatementTransactionsModel.description.ilike(f"%{self.description}%"))
        if self.max_deposit and self.min_deposit:
            if self.max_deposit >= self.min_deposit:
                query = query.filter(
                    between(BankStatementTransactionsModel.deposit, self.min_deposit,
                            self.max_deposit))
        if self.max_withdrawal and self.min_withdrawal:
            if float(self.max_withdrawal) >= float(self.min_withdrawal):
                query = query.filter(
                    between(BankStatementTransactionsModel.withdrawal, float(self.min_withdrawal),
                            float(self.max_withdrawal)))
        if self.transaction_from_date:
            self.transaction_from_date = datetime.now() if not self.transaction_from_date else datetime.strptime(
                self.transaction_from_date, "%Y-%m-%d")
            self.transaction_to_date = self.transaction_from_date + timedelta(
                days=30) if self.transaction_to_date is None else datetime.strptime(
                self.transaction_to_date, "%Y-%m-%d")
            query = query.filter(between(BankStatementTransactionsModel.transaction_date, self.transaction_from_date,
                                         self.transaction_to_date))
        return query
