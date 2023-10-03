from bank_statement_reader.BaseBankStatementReport import BankStatementReport
import re
import sys


class OpayBankStatement(BankStatementReport):

    def __init__(self, pdf_directory, min_salary, max_salary):
        if pdf_directory is None or pdf_directory == '':
            # pdf_directory = "bank_statement_reader/pdfs/opay/opay.pdf"
            pdf_directory = "bank_statement_reader/pdfs/opay/opay-version-2.pdf"
        super().__init__(password='', pdf_directory=pdf_directory, min_salary=min_salary, max_salary=max_salary,
                         bank_name='opay')

    def get_statement_period(self, text: str | dict = None):
        # matches 2022/01/10 TO 2022/03/10
        pattern = r"(\b\d{4}/\d{2}/\d{2}\b)\s+to\s+(\b\d{4}/\d{2}/\d{2}\b)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            from_date = match.group(1)
            to_date = match.group(2)
            output_format = "%Y-%m-%d"
            from_date = self.try_multiple_date_formats(from_date)
            from_date = from_date.strftime(output_format)
            to_date = self.try_multiple_date_formats(to_date)
            to_date = to_date.strftime(output_format)
            return {'from_date': from_date, 'to_date': to_date}

        return {'from_date': None, 'to_date': None}

    def get_account_name(self, text: str | dict = None) -> str | None:
        if text is None:
            return None
        pattern = r"(?i)Name\s*[:.]?\s*([a-zA-Z\s]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            account_name = match.group(1)
            if account_name is not None:
                # Split the string by spaces
                words = account_name.split()
                # We Take the first 3 words and join them back into a single string
                account_name = ' '.join(words[:3])
            return account_name
        return None

    def get_account_number(self, text: str | dict = None) -> str | None:
        if text is None:
            return None
        pattern = r"(?i)Wallet Number:\s+(\d{10,12})"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            account_number = match.group(1)
            if account_number is not None:
                account_number = match.group(1)
                return account_number
        return None

    def get_transactions_table_rows(self, reader, page=0):
        if page == 0:
            tables = reader.pages[page].extract_tables()[0]
            text = tables[len(tables) - 1][0]
        else:
            tables = reader.pages[page].extract_tables()[0]
            text = tables[0][1]

        if text == "" or text is None:
            return False
        rows_without_header = self.parse_transaction_page_text(text)
        return rows_without_header

    def get_transactions_table_header_mapping(self):
        return {
            "transaction_date": "Transaction Date",
            "value_date": "Value Date",
            "debit": "Debit",
            "credit": "Credit",
            "balance": "Balance",
            "description": "Description",
        }

    def parse_transaction_page_text(self, text):

        # pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2} [A-Za-z]+ [+-]?\d+\.\d+ \d+\.\d+ \w+|\d+)'
        pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2} [A-Za-z]+ [+-]?\d+\.\d+ \d+\.\d+ \w+|\d+|\n)'
        date_time_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
        credit_or_debit_pattern = r"([-|+]?\d+\.\d{2})"
        balance_pattern = r'\b(\d+\.\d{1,2})\b(?<![+-])'

        matches = re.findall(pattern, text)

        filtered_matches = []
        for match in matches:
            if re.match(date_time_pattern, match):
                filtered_matches.append(match)
        result = []
        for index, item in enumerate(filtered_matches):

            transaction_date = None
            credit = None
            debit = None
            balance = None


            transaction_date_match = re.search(date_time_pattern, item)
            credit_or_debit_match = re.search(credit_or_debit_pattern, item)
            balance_match = re.findall(balance_pattern, item)
            if transaction_date_match:
                transaction_date = transaction_date_match.group(0)
            if credit_or_debit_match:
                value = credit_or_debit_match.group(0)
                if value.startswith("+"):
                    credit = value.split("+")[1]
                if value.startswith("-"):
                    debit = value.split("-")[1]

            if len(balance_match) > 0:
                balance = balance_match[1]

            if transaction_date and (credit or debit) and balance:
                description = re.sub(date_time_pattern, '', item)
                description = re.sub(credit_or_debit_pattern, '', description)
                description = re.sub(balance_pattern, '', description)
                description = description.replace("[]", " ")
                description = " ".join(description.split())
                result.append([transaction_date, transaction_date, debit, credit, balance, description])
            else:
                continue
        return result

    def result(self):
        reader, status, message = self.get_pdf_reader()
        print(message)
        if status == 0:
            raise Exception("Reading of file failed")
        num_pages = len(reader.pages)
        text = self.get_pdf_page_text(reader)
        cleaned_text = self.clean_text(text)
        statement_period_extracted = self.get_statement_period(cleaned_text)
        account_name_extracted = self.get_account_name(cleaned_text)
        account_number_extracted = self.get_account_number(cleaned_text)
        total_withdrawals_extracted = self.get_total_withdrawal(cleaned_text)
        total_deposit_extracted = self.get_total_deposit(cleaned_text)

        table_headers = self.get_transactions_table_headers(reader)
        trans_rows = []
        for page_num in range(num_pages):
            try:
                # print(page_num)
                new_rows = self.get_transactions_table_rows(reader, page_num)
                if new_rows:
                    trans_rows.extend(new_rows)
            except Exception as e:
                print(page_num)
                print("from result", e)
        opening_balance_extracted = trans_rows[0][4]
        closing_balance_extracted = trans_rows[len(trans_rows) - 1][4]

        formatted_df = self.format_dataframe_columns(table_headers, table_rows=trans_rows)
        formatted_df_copy = formatted_df.copy()
        average_monthly_balance = self.get_average_monthly_balance(formatted_df_copy)

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
        # Loop through each unique value and find occurrences
        for index, row in filtered_df.iterrows():
            unique = self.is_unique_amount_in_month_year(row, filtered_df)
            if not unique:
                continue
            potential_salary.append([
                row['Transaction Date'],
                row['Value Date'],
                row['Withdrawals'],
                row['Deposits'],
                row['Balance'],
                row['Description'],
            ])
        salary_df = self.format_dataframe_columns(table_headers, potential_salary)
        return salary_df
