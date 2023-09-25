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
        # Filter the DataFrame to get rows with values within the specified range
        filtered_df = dataframe[(dataframe['Deposits'] >= self.min_salary) & (dataframe['Deposits'] <= self.max_salary)]
        potential_salary = []
        # Loop through each unique value and find occurrences
        for index, row in filtered_df.iterrows():
            unique = self.is_unique_amount_in_month_year(row, filtered_df)
            if not unique:
                continue
            potential_salary.append([])
        salary_df = self.format_dataframe_columns(table_headers, potential_salary)
        return salary_df
