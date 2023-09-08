class UnprocessableBankStatementSupplied(Exception):
    def __str__(self):
        return "Unprocessable bank statement provided or bank statement format is not supported"
