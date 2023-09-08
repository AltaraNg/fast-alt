class BankStatementProcessingFailed(Exception):
    def __str__(self):
        return "Bank statement processing failed, unable to process the selected bank statement."
