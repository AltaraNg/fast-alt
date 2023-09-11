from typing import Dict


class BankStatementFinalResultResponse:
    def __init__(self,
                 period: Dict[str, str | None],
                 account_name: str | None, account_number: str | None,
                 total_deposits: float | None, total_withdrawals: float | None,
                 opening_balance: float | None, closing_balance: float | None,
                 average_monthly_balance: float | None, excel_file_path: str | None,
                 salary_excel_file_path: str | None, selected_bank_name: str | None,
                 min_salary: float | None, max_salary: float | None,
                 predicted_average_salary: float | None = 0.00,
                 last_transaction_per_day: list[dict] = None,
                 transactions: list[dict] = None,
                 ):
        self.account_number = account_number
        self.excel_file_path = excel_file_path
        self.salary_excel_file_path = salary_excel_file_path
        self.predicted_average_salary = predicted_average_salary
        self.average_monthly_balance = average_monthly_balance
        self.closing_balance = closing_balance
        self.opening_balance = opening_balance
        self.total_withdrawals = total_withdrawals
        self.total_deposits = total_deposits
        self.account_name = account_name
        self.period = period
        self.selected_bank_name = selected_bank_name
        self.min_salary = min_salary
        self.max_salary = max_salary
        self.last_transaction_per_day = last_transaction_per_day
        self.transactions = transactions
