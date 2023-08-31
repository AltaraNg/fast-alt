from sqlalchemy import Column, Integer, String, DateTime, Float, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime


class BankStatementDayEndTransactions(Base):
    __tablename__ = "bank_statement_day_end_transactions"
    id = Column(Integer, primary_key=True, index=True)
    bank_statement_id = Column(Integer, ForeignKey('bank_statements.id'))
    balance = Column(Float(precision=12), nullable=True)
    deposit = Column(Float(precision=12), nullable=True)
    withdrawal = Column(Float(precision=12), nullable=True)
    transaction_date = Column(Date, nullable=False)
    description = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=True, default=datetime.now())
    updated_at = Column(DateTime, nullable=True, default=datetime.now())
    bankStatement = relationship("BankStatement", back_populates="bankStatementDayEndTransactions")
