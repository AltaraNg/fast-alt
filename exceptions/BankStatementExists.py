class BankStatementExists(Exception):
    def __init__(self, account_number, start_date, end_date):
        self.account_number = account_number
        self.start_date = start_date
        self.end_date = end_date

    def __str__(self):
        return f"Bank statement with supplied account no: {self.account_number}, period: {self.start_date} to {self.end_date} already exists"
