import re
from bank_statement_reader.BaseBankStatementReport import BankStatementReport
from bank_statement_reader.exceptions.InprocessibleBankStatementSupplied import UnprocessableBankStatementSupplied
from datetime import datetime


class AccessBankStatement(BankStatementReport):
    version_one: bool = False
    version_two: bool = False

    def __init__(self, pdf_directory, min_salary, max_salary):
        if pdf_directory is None or pdf_directory == '':
            pdf_directory = "pdfs/access/access_version_one.pdf"  # version one
            # pdf_directory = "pdfs/access/access_version_two.pdf"  # version two
        self.pdf_directory = pdf_directory
        super().__init__(password='', pdf_directory=pdf_directory, min_salary=min_salary, max_salary=max_salary,
                         bank_name='access')

    def get_statement_period(self, data: str | dict = None):
        if isinstance(data, str) and self.version_one:
            return super().get_statement_period(data)
        if isinstance(data, dict) and self.version_two:
            date_string = data['summary_statement_for']
            # Split the date string into start and end date parts
            start_date_str, end_date_str = date_string.split(" to ")
            # Define the input and output date formats
            input_date_format = "%A, %B %d, %Y"
            output_date_format = "%Y-%m-%d"
            # Convert start and end date strings to datetime objects
            start_date = datetime.strptime(start_date_str, input_date_format)
            end_date = datetime.strptime(end_date_str, input_date_format)
            # Format the datetime objects as strings in the desired output format
            formatted_start_date = start_date.strftime(output_date_format)
            formatted_end_date = end_date.strftime(output_date_format)
            return {'from_date': formatted_start_date, 'to_date': formatted_end_date}
        return {'from_date': None, 'to_date': None}

    def get_account_number(self, data):
        if self.version_one:
            return super().get_account_number(data)
        if self.version_two and isinstance(data, dict):
            return data['account_number']
        return None

    def get_account_name(self, data: str | dict = None):
        if self.version_one:
            return super().get_account_name(data)
        if self.version_two and isinstance(data, dict):
            return data['account_name']
        return None

    def get_opening_balance(self, data):
        if self.version_one:
            return super().get_opening_balance(data)
        if self.version_two and isinstance(data, dict):
            return self.convert_to_money(data['opening_balance'])
        return None

    def get_closing_balance(self, data):
        if self.version_one:
            return super().get_closing_balance(data)
        if self.version_two and isinstance(data, dict):
            return self.convert_to_money(data['closing_balance'])
        return None

    def get_total_deposit(self, data):
        if self.version_one:
            return super().get_total_deposit(data)
        if self.version_two and isinstance(data, dict):
            return self.convert_to_money(data['total_lodgement'])
        return None

    def get_total_withdrawal(self, data):
        if self.version_one:
            return super().get_total_withdrawal(data)
        if self.version_two and isinstance(data, dict):
            return self.convert_to_money(data['total_withdrawals'])
        return None

    def get_transactions_table_header_mapping(self):
        if self.version_one:
            return {
                'date': 'Date',
                'transaction_details': 'Transaction Details',
                'reference': 'Reference',
                'value_date': 'Value Date',
                'withdrawals': 'Withdrawals',
                'lodgements': 'Lodgements',
                'balance': 'Balance'
            }
        if self.version_two:
            return {
                'posted_date': 'Posted Date',
                'value_date': 'Value Date',
                'description': 'Description',
                'debit': 'Debit',
                'credit': 'Credit',
                'balance': 'Balance'
            }

    def get_transactions_table_headers(self, reader):
        return super().get_transactions_table_headers(reader)

    def pad_header_with_unknown(self, rows, headers):
        if len(rows[0]) > len(headers):
            # Index of "Value Date" in the list
            value_date_index = headers.index('Value Date')
            headers.pop(value_date_index - 1)
            # # Insert the new item before "Value Date"
            # headers.insert(value_date_index, unknown)
            return headers

        else:
            return headers

    def get_transactions_table_rows(self, reader, page=0):
        if self.version_one:
            return self.get_transactions_table_rows_version_one(reader, page)
        if self.version_two:
            return self.get_transactions_table_rows_version_two(reader, page)
        raise UnprocessableBankStatementSupplied()

    def get_transactions_table_rows_version_one(self, reader, page=0):
        if page == 0:
            table = reader.pages[page].extract_tables()[1]
            rows_without_header = table[2:]
        else:
            table = reader.pages[page].extract_tables()[0]
            rows_without_header = table[1:]
        modified_rows = [[item.replace('\n', '').strip() if item else '' for item in row] for row in
                         rows_without_header]
        new_trans_rows = []
        pattern = r"\d{1,2}-[A-Z]{3}-\d{4}"
        second_pattern = r"\d{1,2}-[A-Z]{3}-\d{2}"
        for row in modified_rows:
            if page == 0:
                trans_date = row[0]
                value_date = row[4]
                row.pop(3)
            else:
                trans_date = row[0]
                value_date = row[3]
            if re.match(pattern, trans_date) is None:
                continue
            if re.match(second_pattern, value_date) is None:
                continue
            new_trans_rows.append(row)

        return new_trans_rows

    def read_version_one(self, reader, cleaned_text):
        account_name_extracted = self.get_account_name(cleaned_text)
        statement_period_extracted = self.get_statement_period(cleaned_text)
        account_number_extracted = self.get_account_number(cleaned_text)
        total_withdrawals_extracted = self.get_total_withdrawal(cleaned_text)
        total_deposit_extracted = self.get_total_deposit(cleaned_text)
        opening_balance_extracted = self.get_opening_balance(cleaned_text)
        closing_balance_extracted = self.get_closing_balance(cleaned_text)

        table_headers = self.get_transactions_table_headers(reader)

        num_pages = len(reader.pages)
        trans_rows = []
        for page_num in range(num_pages):
            try:
                self.set_page_state(page_num, num_pages)
                new_rows = self.get_transactions_table_rows(reader, page_num)
                if self.current_page_number == 0:
                    self.pad_header_with_unknown(new_rows, table_headers)
                trans_rows.extend(new_rows)
            except Exception as e:
                print(page_num)
                print("from result", e)
                raise e

        formatted_df = self.format_dataframe_columns(table_headers, table_rows=trans_rows)
        average_monthly_balance = self.get_average_monthly_balance(formatted_df)

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

    def get_transactions_table_rows_version_two(self, reader, page=0):
        tables = reader.pages[page].extract_tables()
        modified_rows = []
        if self.at_first_page:
            table = tables[2]
            rows_without_header = table[1:]
        else:
            table = tables[0]
            rows_without_header = table[1:]
        for row in rows_without_header:
            if len(row) == 6:
                trans_date = row[0]
                value_date = row[1]
                transaction_details = self.clean_text(row[2])
                withdrawal = row[3]
                deposit = row[4]
                balance = row[5]
                modified_rows.append(
                    [trans_date, value_date, transaction_details, withdrawal, deposit, balance])
        return modified_rows

    def read_version_two(self, reader, cleaned_text):
        formatted_summary_table_first = self.format_account_summary_table(reader)
        formatted_summary_table_second = self.format_account_summary_table(reader, 1)
        account_name_extracted = self.get_account_name(formatted_summary_table_second)
        statement_period_extracted = self.get_statement_period(formatted_summary_table_second)
        account_number_extracted = self.get_account_number(formatted_summary_table_first)
        total_withdrawals_extracted = self.get_total_withdrawal(formatted_summary_table_first)
        total_deposit_extracted = self.get_total_deposit(formatted_summary_table_first)
        opening_balance_extracted = self.get_opening_balance(formatted_summary_table_first)
        closing_balance_extracted = self.get_closing_balance(formatted_summary_table_first)

        table_headers = self.get_transactions_table_headers(reader)
        num_pages = len(reader.pages)
        trans_rows = []

        for page_num in range(num_pages):
            try:
                self.set_page_state(page_num, num_pages)
                new_rows = self.get_transactions_table_rows(reader, page_num)
                trans_rows.extend(new_rows)
            except Exception as e:
                print(page_num)
                print("from result", e)
                raise e
        formatted_df = self.format_dataframe_columns(table_headers, table_rows=trans_rows)
        average_monthly_balance = self.get_average_monthly_balance(formatted_df)

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

    def result(self):
        reader, status, message = self.get_pdf_reader()
        print(message)
        if status == 0 and message is not None:
            raise Exception(message)

        text = self.get_pdf_page_text(reader)
        cleaned_text = self.clean_text(text)
        first_page_tables = reader.pages[0].extract_tables()
        first_page_table_length = len(first_page_tables[0])
        if first_page_table_length == 1:
            self.version_one = True
            return self.read_version_one(reader, cleaned_text)
        if first_page_table_length == 7:
            self.version_two = True
            return self.read_version_two(reader, cleaned_text)

        raise UnprocessableBankStatementSupplied()

    def predict_salary_income(self, dataframe, table_headers):
        # Filter the DataFrame to get rows with values within the specified range
        filtered_df = dataframe[(dataframe['Deposits'] >= self.min_salary) & (dataframe['Deposits'] <= self.max_salary)]
        potential_salary = []
        for index, row in filtered_df.iterrows():
            unique = self.is_unique_amount_in_month_year(row, filtered_df)
            if not unique:
                continue
            if self.version_one:
                potential_salary.append([
                    row['Transaction Date'],
                    row['Description'],
                    row['Reference'],
                    row['Value Date'],
                    row['Withdrawals'],
                    row['Deposits'],
                    row['Balance'],
                ])
            if self.version_two:
                potential_salary.append([
                    row['Transaction Date'],
                    row['Value Date'],
                    row['Description'],
                    row['Withdrawals'],
                    row['Deposits'],
                    row['Balance'],
                ])
        formatted_salary_df = self.format_dataframe_columns(table_headers, potential_salary)
        return formatted_salary_df
