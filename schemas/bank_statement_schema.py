from pydantic import BaseModel


class BankStatementBase(BaseModel):
    account_name: str
    account_number: str
    opening_balance: float
    closing_balance: float
    total_deposit: float
    total_withdrawal: float
    salary_predictions_file_url: str
    exported_bank_statement_file_url: str
    start_date: str
    end_date: str


class BankStatementCreate(BankStatementBase):
    pass
    # def __int__(self, account_name, account_number, opening_balance, closing_balance, total_deposit, total_withdrawal,
    #             salary_predictions_file_url, exported_bank_statement_file_url, start_date, end_date):
    #     self.account_number = account_number
    #     self.account_name = account_number
    #     self.opening_balance = opening_balance
    #     self.closing_balance = closing_balance
    #     self.total_deposit = total_deposit
    #     self.total_withdrawal = total_withdrawal
    #     self.salary_predictions_file_url = salary_predictions_file_url
    #     self.exported_bank_statement_file_url = exported_bank_statement_file_url
    #     self.start_date = start_date
    #     self.end_date = end_date


class BankStatement(BankStatementBase):
    id: int

    class Config:
        from_attributes = True
