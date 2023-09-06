from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, Date
from config.database import Base
from datetime import datetime


class BankStatement(Base):
    __tablename__ = "bank_statements"
    id = Column(Integer, primary_key=True, index=True)
    account_name = Column(String, nullable=True)
    account_number = Column(String, nullable=True)
    opening_balance = Column(Float, nullable=True)
    closing_balance = Column(Float, nullable=True)
    total_deposit = Column(Float, nullable=True)
    total_withdrawal = Column(Float, nullable=True)
    salary_predictions_file_url = Column(String, nullable=True)
    exported_bank_statement_file_url = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=True, default=datetime.now())
    updated_at = Column(DateTime, nullable=True, default=datetime.now())
