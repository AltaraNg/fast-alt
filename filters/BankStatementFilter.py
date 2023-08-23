from models.bank_statement_model import BankStatement
from datetime import datetime, timedelta

from sqlalchemy import between
from fastapi import FastAPI, Request


class BankStatementFilter:
    account_number: str = None
    customer_id: int = None
    status: str = None
    bank_name: str = None
    account_name: str = None
    from_date: str | datetime = None
    to_date: str | datetime = None

    def __init__(self, params: dict):
        self.account_number = params.get('account_number')
        self.account_name = params.get('account_name')
        self.status = params.get('status')
        self.customer_id = params.get('customer_id')
        self.bank_name = params.get('bank_name')
        self.from_date = params.get('from_date')
        self.to_date = params.get('to_date')

    def apply(self, query):
        if self.account_name:
            query = query.filter(BankStatement.account_name.ilike(f"%{self.account_name}%"))
        if self.account_number:
            query = query.filter(BankStatement.account_number == self.account_number)
        # if self.bank_name:
        #     query = query.filter(BankStatement.bank_name == self.bank_name)
        if self.customer_id:
            query = query.filter(BankStatement.customer_id == self.customer_id)
        if self.from_date:
            self.from_date = datetime.now() if not self.from_date else datetime.strptime(self.from_date, "%Y-%m-%d")
            self.to_date = self.from_date + timedelta(days=30) if self.to_date is None else self.to_date
            self.to_date = datetime.strptime(self.to_date, "%Y-%m-%d")
            self.from_date = datetime.strptime(self.from_date, "%Y-%m-%d")
            query = query.filter(between(BankStatement.created_at, self.from_date, self.to_date))
        return query
