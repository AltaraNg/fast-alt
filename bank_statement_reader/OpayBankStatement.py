from bank_statement_reader.BaseBankStatementReport import BankStatementReport
from abc import abstractmethod


class OpayBankStatement(BankStatementReport):

    def __init__(self, pdf_directory, min_salary, max_salary):
        if pdf_directory is None or pdf_directory == '':
            pdf_directory = "bank_statement_reader/pdfs/opay/opay.pdf"
        super().__init__(password='', pdf_directory=pdf_directory, min_salary=min_salary, max_salary=max_salary,
                         bank_name='opay')

    @abstractmethod
    def get_transactions_table_rows(self, reader, page):
        pass

    @abstractmethod
    def get_transactions_table_header_mapping(self):
        pass

    @abstractmethod
    def result(self):
        pass

    @abstractmethod
    def predict_salary_income(self, dataframe, table_headers):
        pass
