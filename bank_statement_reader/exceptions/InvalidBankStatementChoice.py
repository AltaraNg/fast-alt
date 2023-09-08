class InvalidBankStatementChoice(Exception):
    def __str__(self):
        return "Invalid bank statement choice supplied, please provide a valid one"
