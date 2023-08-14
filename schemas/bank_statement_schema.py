from pydantic import BaseModel


class BankStatementBase(BaseModel):
    account_name: str
    account_number: str
    opening_balance: float
    closing_balance: float
    total_deposit: float
    total_withdrawal: float
    salary_predictions_file_url: str | None
    exported_bank_statement_file_url: str | None
    start_date: str
    end_date: str


class BankStatementCreate(BankStatementBase):
    pass


class BankStatement(BankStatementBase):
    id: int

    class Config:
        from_attributes = True
