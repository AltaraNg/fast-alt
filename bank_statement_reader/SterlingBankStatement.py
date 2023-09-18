import re

import pandas as pd

from bank_statement_reader.BaseBankStatementReport import BankStatementReport


class SterlingBankStatement(BankStatementReport):

    def __init__(self, pdf_directory, min_salary, max_salary):
        if pdf_directory is None or pdf_directory == '':
            pdf_directory = "bank_statement_reader/pdfs/sterling/sterling.pdf"
        super().__init__(password='', pdf_directory=pdf_directory, min_salary=min_salary, max_salary=max_salary,
                         bank_name='sterling')

    def format_account_summary_table(self, reader, table_index=0, page=0):
        # get first table in first page
        summary_tables = reader.pages[page].extract_tables()[table_index]
        table_dictionary = {}
        for item in summary_tables:
            if len(item) >= 2:
                # Convert the key by replacing spaces with underscores and making it lowercase
                key1 = item[0].replace(' ', '_').replace('.', '').replace(':', '').replace('\n', '_').lower()
                # Set the value as the second item in the list
                value1 = item[1].replace('\n', '_')
                table_dictionary[key1] = value1
            if len(item) >= 4:
                # Convert the key by replacing spaces with underscores and making it lowercase
                key2 = item[2].replace(' ', '_').replace('.', '').replace(':', '').replace('\n', '_').lower()
                # Set the value as the second item in the list
                value2 = item[3].replace('\n', '_')
                table_dictionary[key2] = value2

        return table_dictionary

    def get_total_withdrawal(self, _formatted_summary_table) -> float:
        return _formatted_summary_table['total_debit']

    def get_total_deposit(self, _formatted_summary_table) -> float:
        return _formatted_summary_table['total_credit']

    def get_opening_balance(self, _formatted_summary_table):
        return _formatted_summary_table['opening_balance']

    def get_closing_balance(self, _formatted_summary_table):
        return _formatted_summary_table['closing_balance']

    def get_account_number(self, text):
        pattern = r"(\d{10,12})\s+Branch Name"
        match = re.search(pattern, text)
        if match:
            account_number = match.group(1)
            return account_number

        else:
            return None

    def get_account_name(self, text: str | dict = None) -> str | None:
        if text is None:
            return None
        text = text.replace(',', '')
        pattern = r"\s*[:.]?\s*([a-zA-Z\s]+)Account\s+Type"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            account_name = match.group(1)
            if account_name is not None:
                # Split the string by spaces
                words = account_name.split()
                # Take the first 3 words and join them back into a single string
                account_name = ' '.join(words[-3:])
            return account_name
        else:
            return None

    def get_transactions_table_header_mapping(self):
        return {
            'trans_date': 'Trans Date',
            'narration': 'Narration',
            'value_date': 'Value Date',
            'debit': 'Debit',
            'credit': 'Credit',
            'balance': 'Balance'
        }

    def get_transactions_table_headers(self, reader):
        return self.get_transactions_table_header_mapping().values()

    def get_transactions_table_rows(self, reader, page=0):
        date_pattern = r'\d{1,2}-([A-Z]|[a-z]){3}-\d{4}'
        money_pattern = r'\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b'
        if page == 0:
            table = reader.pages[page].extract_tables()[1]
            rows_without_header = table[1:]
        else:
            table = reader.pages[page].extract_tables()[1]
            rows_without_header = table[0:]

        modified_rows = []
        # Remove None
        for index, row in enumerate(rows_without_header):
            if len(row) > 5:
                transaction_date = row[0]
                narration = row[1]
                value_date = row[2]
                debit = row[3]
                credit = row[4]
                balance = row[5]
                modified_rows.append([transaction_date, narration, value_date, debit, credit, balance])

        return modified_rows

    def result(self):
        reader, status, message = self.get_pdf_reader()
        print(message)
        if status == 0:
            raise Exception("Reading of file failed")

        num_pages = len(reader.pages)
        text = self.get_pdf_page_text(reader)
        last_page_text = self.get_pdf_page_text(reader, num_pages - 1)

        cleaned_text = self.clean_text(text)

        formatted_summary_table = self.format_account_summary_table(reader)

        total_withdrawals_extracted = self.get_total_withdrawal(formatted_summary_table)
        total_deposit_extracted = self.get_total_deposit(formatted_summary_table)
        account_name_extracted = self.get_account_name(cleaned_text)
        statement_period_extracted = self.get_statement_period(cleaned_text)
        account_number_extracted = self.get_account_number(cleaned_text)
        opening_balance_extracted = self.get_opening_balance(formatted_summary_table)
        closing_balance_extracted = self.get_closing_balance(formatted_summary_table)

        table_headers = self.get_transactions_table_headers(reader)
        trans_rows = []
        for page_num in range(num_pages):
            try:
                # print(page_num)
                new_rows = self.get_transactions_table_rows(reader, page_num)
                trans_rows.extend(new_rows)
            except Exception as e:
                print(page_num)
                print("from result", e)

        formatted_df = self.format_dataframe_columns(table_headers, table_rows=trans_rows)

        salary_df = self.predict_salary_income(formatted_df.copy(), table_headers)

        average_monthly_balance = self.get_average_monthly_balance(formatted_df.copy())

        return {
            'dataframe': formatted_df,
            'period': statement_period_extracted,
            "account_name": account_name_extracted,
            "account_number": account_number_extracted,
            "total_turn_over_credit": total_deposit_extracted,
            "total_turn_over_debits": total_withdrawals_extracted,
            "opening_balance": opening_balance_extracted,
            "closing_balance": closing_balance_extracted,
            "average_monthly_balance": average_monthly_balance
        }

    def predict_salary_income(self, dataframe, table_headers):
        # Filter the DataFrame to get rows with values within the specified range
        filtered_df = dataframe[(dataframe['Deposits'] >= self.min_salary) & (dataframe['Deposits'] <= self.max_salary)]
        potential_salary = []
        for index, row in filtered_df.iterrows():
            unique = self.is_unique_amount_in_month_year(row, filtered_df)
            if not unique:
                continue
            potential_salary.append([
                row['Transaction Date'],
                row['Description'],
                row['Value Date'],
                row['Withdrawals'],
                row['Deposits'],
                row['Balance'],
            ])
        # salary_df = pd.DataFrame(potential_salary, columns=table_headers)
        formatted_salary_df = self.format_dataframe_columns(table_headers, potential_salary)
        return formatted_salary_df
