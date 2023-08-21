from sqlalchemy import Column, Integer, String, DateTime, Float, Date, ForeignKey, Text
from config.database import Base
from datetime import datetime
import json
from sqlalchemy.types import TypeDecorator, TEXT


class JSONEncodedList(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class BankStatement(Base):
    __tablename__ = "bank_statements"
    id = Column(Integer, primary_key=True, index=True)
    account_name = Column(String, nullable=True)
    account_number = Column(String, nullable=True)
    opening_balance = Column(Float(precision=12), nullable=True)
    closing_balance = Column(Float(precision=12), nullable=True)
    total_deposit = Column(Float(precision=12), nullable=True)
    total_withdrawal = Column(Float(precision=12), nullable=True)
    salary_predictions_file_url = Column(String, nullable=True)
    exported_bank_statement_file_url = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=True, default=datetime.now())
    updated_at = Column(DateTime, nullable=True, default=datetime.now())
    customer_id = Column(Integer, nullable=True)
    repayment_capability = Column(JSONEncodedList, nullable=True)
    predicted_average_salary = Column(Float(precision=12), nullable=True)
    average_monthly_balance = Column(Float(precision=12), nullable=True)
