from bank_statement_reader.BaseBankStatementReport import BankStatementReport
import re

from bank_statement_reader.exceptions.InprocessibleBankStatementSupplied import UnprocessableBankStatementSupplied


class FirstBankStatement(BankStatementReport):
    mode = None

    def __init__(self, pdf_directory, password, min_salary, max_salary):
        if pdf_directory is None or pdf_directory == '':
            pdf_directory = "pdfs/firstbank/first_bank_version.pdf"
            # pdf_directory = "pdfs/firstbank/first_mobile_version.pdf"
            password = "34932"
        super().__init__(password=password, pdf_directory=pdf_directory, min_salary=min_salary, max_salary=max_salary,
                         bank_name='first')

    def get_opening_balance_from_table(self, reader):
        table = reader.pages[0].extract_tables()[1]
        opening_balance_row = table[1]
        last_item = opening_balance_row[-1]
        opening_balance = None
        for row in opening_balance_row:
            if 'Opening Balance' == row and self.is_money_pattern(last_item):
                opening_balance = self.convert_to_money(last_item)
                break
        return opening_balance

    def get_transactions_table_header_mapping(self):
        return {
            'transdate': 'TransDate',
            'reference': 'Reference',
            'transaction_details': 'Transaction Details',
            'valuedate': 'ValueDate',
            'deposit': 'Deposit',
            'withdrawal': 'Withdrawal',
            'balance': 'Balance'
        }

    def get_transactions_table_headers(self, reader):
        return self.get_transactions_table_header_mapping().values()

    def pad_header_with_unknown(self, rows, headers):
        if len(rows[0]) > len(headers):
            # New item to be inserted
            unknown = 'Unknown'

            # Index of "Value Date" in the list
            value_date_index = headers.index('Value Date')

            # Insert the new item before "Value Date"
            headers.insert(value_date_index, unknown)
            return headers
        else:
            return headers

    def get_transactions_table_rows_bank_version(self, reader, page=0):
        modified_rows = []
        if page == 0:
            table = reader.pages[page].extract_tables()[1]
            rows_without_header = table[1:]
            rows_without_header = rows_without_header[1:]
        else:
            table = reader.pages[page].extract_tables()[0]
            rows_without_header = table[1:]
        for row in rows_without_header:
            if len(row) == 7:
                trans_date = row[0]
                reference = row[1]
                transaction_details = row[2].replace('\n', '')
                value_date = row[3]
                withdrawal = row[4]
                deposit = row[5]
                balance = row[6]
                modified_rows.append(
                    [trans_date, reference, transaction_details, value_date, deposit, withdrawal, balance])
        if self.at_last_page is True:
            modified_rows.pop(-1)
        return modified_rows

    def get_transactions_table_rows(self, reader, page=0):
        # first_page_tables = reader.pages[0].extract_tables()
        # mobile version only has one table on first page
        if self.mode == 1:
            # print("Mobile")
            return self.get_transactions_table_rows_mobile_version(reader, page)
        # none mobile version has more than one table on first page
        if self.mode == 2:
            # print("Bank")
            return self.get_transactions_table_rows_bank_version(reader, page)

        raise UnprocessableBankStatementSupplied()

    def extract_date_by_position(self, input_string, position):
        date_formats = [
            r'\d{2}-[A-Za-z]{3}-\d{2}',
            r'\d{2}-[A-Za-z]{3}-\d{4}',
            r'\d{2}/\d{2}/\d{2}',
            r'\d{2}/\d{2}/\d{4}',
        ]
        matches = re.findall(rf'({"|".join(date_formats)})', input_string)

        if position <= len(matches):
            return matches[position - 1]
        else:
            return None

    def extract_money_by_position(self, input_string, position):
        money_formats = [
            r'\b\d{1,3}(?:,\d{3})*\.\d{2}\b',
            r'\b\d{1,3}(?:\.\d{3})*,\d{2}\b',
        ]

        matches = re.findall(rf'({"|".join(money_formats)})', input_string)
        if position <= len(matches):
            return matches[position - 1]
        else:
            return None

    def remove_substrings(self, original_string, substrings_to_remove):
        if not original_string:
            return ''
        new_string = original_string
        for substring in substrings_to_remove:
            if not substring:
                continue
            new_string = new_string.replace(substring, '')
        return new_string

    def get_transactions_table_rows_mobile_version(self, reader, page=0, on_first_page=False, on_last_page=False):
        try:
            modified_rows = []
            tables = reader.pages[page].extract_tables()
            if tables is None:
                return []
            opening_balance = None
            if page == 0:
                table = tables[0]
                rows_without_header = table[1:]
                opening_balance_row = rows_without_header[0]
                opening_balance = self.extract_money_by_position(opening_balance_row[0], 1)
                rows_without_header = rows_without_header[1:]
            else:
                rows_without_header = []
                if len(tables) > 0:
                    table = tables[0]
                    rows_without_header = table[1:]

            for row in rows_without_header:

                input_string = row[0]
                if input_string is None:
                    continue
                if input_string == '':
                    continue
                trans_date = self.extract_date_by_position(input_string, 1)
                value_date = self.extract_date_by_position(input_string, 2)
                deposit_or_withdrawal = self.extract_money_by_position(input_string, 1)
                balance = self.extract_money_by_position(input_string, 2)
                reference = ''
                transaction_details = self.remove_substrings(
                    input_string,
                    [
                        trans_date,
                        value_date,
                        deposit_or_withdrawal,
                        balance
                    ]
                )
                if transaction_details is not None:
                    transaction_details = self.clean_text(transaction_details)
                if trans_date is not None and deposit_or_withdrawal is not None and balance is not None:
                    modified_rows.append(
                        [trans_date, reference, transaction_details, value_date,
                         deposit_or_withdrawal, deposit_or_withdrawal, balance])
            for index, row in enumerate(modified_rows):
                current_row = modified_rows[index]
                current_row_balance = current_row[6]
                # row[4] is deposit column
                # row[5] is withdrawal column
                amount = row[4]
                if index == 0:
                    previous_row_balance = opening_balance
                else:
                    previous_row = modified_rows[index - 1]
                    previous_row_balance = previous_row[6]
                deposit, withdrawal = self.compute_deposit_withdrawal(current_row_balance, previous_row_balance, amount)
                if deposit is None or withdrawal is None:
                    continue
                row[4] = deposit
                row[5] = withdrawal
            return modified_rows
        except Exception as e:
            print(e)
            raise e

    def compute_deposit_withdrawal(self, current_row_balance, previous_row_balance, amount):
        if current_row_balance is None or previous_row_balance is None:
            return None, None

        if self.convert_to_money(current_row_balance) > self.convert_to_money(previous_row_balance):
            deposit = amount
            withdrawal = 0.00
        else:
            deposit = 0.00
            withdrawal = amount
        return deposit, withdrawal

    def result(self):
        reader, status, message = self.get_pdf_reader()
        print(message)
        if status == 0:
            raise Exception("Reading of file failed")
        text = self.get_pdf_page_text(reader)
        cleaned_text = self.clean_text(text)

        first_page_tables = reader.pages[0].extract_tables()

        self.mode = len(first_page_tables)
        # mobile version only has one table on first page
        if self.mode == 1:
            return self.read_mobile_app_version(reader, cleaned_text)

        # none mobile version has more than one table on first page
        if self.mode >= 2:
            return self.read_bank_version(reader, cleaned_text)

        raise UnprocessableBankStatementSupplied()

    def read_bank_version(self, reader, cleaned_text):
        num_pages = len(reader.pages)
        first_page_tables = reader.pages[0].extract_tables()
        first_page_trans_table = first_page_tables[1]
        last_page_trans_table = reader.pages[num_pages - 1].extract_tables()[0]
        opening_balance_row = first_page_trans_table[1]
        closing_balance_row = last_page_trans_table[-1]
        statement_period_extracted = self.get_statement_period(cleaned_text)
        account_name_extracted = self.get_account_name(cleaned_text)
        account_number_extracted = self.get_account_number(cleaned_text)
        total_withdrawals_extracted = self.get_total_withdrawal(cleaned_text)
        total_deposit_extracted = self.get_total_deposit(cleaned_text)
        opening_balance_extracted = self.get_opening_balance(opening_balance_row)
        closing_balance_extracted = self.get_closing_balance(closing_balance_row)
        table_headers = self.get_transactions_table_headers(reader)
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
            "average_monthly_balance": average_monthly_balance,
        }

    def read_mobile_app_version(self, reader, cleaned_text):
        try:
            statement_period_extracted = self.get_statement_period(cleaned_text)
            account_name_extracted = self.get_account_name(cleaned_text)
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
                    new_rows = self.get_transactions_table_rows(reader, page_num)
                    if page_num > 0 and len(new_rows) > 0:
                        last_row_of_trans_rows = trans_rows[-1]
                        last_row_of_new = new_rows[-1]
                        last_row_of_trans_rows_balance = last_row_of_trans_rows[-1]
                        last_row_of_new_balance = last_row_of_new[-1]
                        amount = last_row_of_new[4]
                        deposit, withdrawal = self.compute_deposit_withdrawal(last_row_of_new_balance,
                                                                              last_row_of_trans_rows_balance, amount)
                        last_row_of_new[4] = deposit
                        last_row_of_new[5] = withdrawal
                    if new_rows:
                        if len(new_rows) < 1:
                            continue
                        trans_rows.extend(new_rows)
                except Exception as e:
                    print("from result", e)
                    raise e
            formatted_df = self.format_dataframe_columns(table_headers, table_rows=trans_rows)
            # print(formatted_df)
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
                "average_monthly_balance": average_monthly_balance,
            }
        except Exception as e:
            raise e

    def predict_salary_income(self, dataframe, table_headers):
        # Filter the DataFrame to get rows with values within the specified range
        filtered_df = dataframe[(dataframe['Deposits'] >= self.min_salary) & (dataframe['Deposits'] <= self.max_salary)]
        if filtered_df.empty:
            return None

        potential_salary = []
        for index, row in filtered_df.iterrows():
            unique = self.is_unique_amount_in_month_year(row, filtered_df)
            if not unique:
                continue
            potential_salary.append([
                row['Transaction Date'],
                row['Reference'],
                row['Description'],
                row['Value Date'],
                row['Deposits'],
                row['Withdrawals'],
                row['Balance'],
            ])
        salary_df = self.format_dataframe_columns(table_headers, potential_salary)
        return salary_df
