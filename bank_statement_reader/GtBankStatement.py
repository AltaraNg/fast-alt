from bank_statement_reader.BaseBankStatementReport import BankStatementReport
import pandas as pd
import re


class GtBankStatement(BankStatementReport):

    def __init__(self, pdf_directory, min_salary, max_salary):
        if pdf_directory is None or pdf_directory == '':
            pdf_directory = "pdfs/gt/gt_version_one-2.pdf"
        super().__init__(password='', pdf_directory=pdf_directory, min_salary=min_salary, max_salary=max_salary,
                         bank_name='gt')

    def get_account_number(self, _formatted_summary_table):
        return _formatted_summary_table['account_no']

    def get_total_withdrawal(self, _formatted_summary_table) -> float:
        return self.convert_to_money(_formatted_summary_table['total_debit'])

    def get_total_deposit(self, _formatted_summary_table) -> float:
        return self.convert_to_money(_formatted_summary_table['total_credit'])

    def get_opening_balance(self, _formatted_summary_table):
        return self.convert_to_money(_formatted_summary_table['opening_balance'])

    def get_closing_balance(self, _formatted_summary_table) -> float:
        return self.convert_to_money(_formatted_summary_table['closing_balance'])

    def get_account_name(self,  text: str | dict = None) -> str | None:
        if text is None:
            return None
        text = text.replace(',', '')
        pattern = r"(?i)CUSTOMER\s+STATEMENT\s*[:.]?\s*([a-zA-Z\s]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            account_name = match.group(1)
            if account_name is not None:
                # Split the string by spaces
                words = account_name.split()
                # Take the first 3 words and join them back into a single string
                account_name = ' '.join(words[:3])
            return account_name
        else:
            return None

    def get_transactions_table_headers(self, reader):

        table = reader.pages[0].extract_tables()[1]
        headers = table[0]
        header_mapping = self.get_transactions_table_header_mapping()
        header_columns = [header_mapping[col.replace('\n', ' ').lower().replace(' ', '_').replace('.', '').strip()]
                          for col in headers if col is not None]
        return header_columns

    def get_transactions_table_rows(self, reader, page):
        date_pattern = r'\d{1,2}-([A-Z]|[a-z]){3}-\d{4}'
        if page == 0:
            table = reader.pages[page].extract_tables()[1]
            rows_without_header = table[1:]
        else:
            table = reader.pages[page].extract_tables()[0]
            rows_without_header = table[0:]
        trans_rows = []
        for row in rows_without_header:
            trans_date = row[0]
            # value_date = row[1]
            if re.match(date_pattern, trans_date) is None:
                continue
            trans_rows.append(row)
        return trans_rows

    def get_transactions_table_header_mapping(self):
        return {
            'trans_date': 'Trans Date',
            'remarks': 'Remarks',
            'reference': 'Reference',
            'value_date': 'Value Date',
            'debits': 'Debits',
            'credits': 'Credits',
            'balance': 'Balance',
            'originating_branch': 'Originating Branch',
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
                row['Value Date'],
                row['Reference'],
                row['Withdrawals'],
                row['Deposits'],
                row['Balance'],
                row['Originating Branch'],
                row['Description'],
            ])
        formatted_salary_df = self.format_dataframe_columns(table_headers, potential_salary)
        return formatted_salary_df

    def result(self):
        reader, status, message = self.get_pdf_reader()
        print(message)
        if status == 0:
            raise Exception("Reading of file failed")

        text = self.get_pdf_page_text(reader)
        cleaned_text = self.clean_text(text)
        formatted_summary_table = self.format_account_summary_table(reader)

        statement_period_extracted = self.get_statement_period(cleaned_text)
        account_name_extracted = self.get_account_name(cleaned_text)
        account_number_extracted = self.get_account_number(formatted_summary_table)
        total_withdrawals_extracted = self.get_total_withdrawal(formatted_summary_table)
        total_deposit_extracted = self.get_total_deposit(formatted_summary_table)
        opening_balance_extracted = self.get_opening_balance(formatted_summary_table)
        closing_balance_extracted = self.get_closing_balance(formatted_summary_table)

        table_headers = self.get_transactions_table_headers(reader)

        num_pages = len(reader.pages)
        trans_rows = []
        for page_num in range(num_pages):
            try:
                new_rows = self.get_transactions_table_rows(reader, page_num)
                trans_rows.extend(new_rows)
            except Exception as e:
                print(page_num)
                print("from result", e)
        if opening_balance_extracted is None:
            opening_balance_extracted = trans_rows[0][5]

        if closing_balance_extracted is None:
            closing_balance_extracted = trans_rows[len(trans_rows) - 1][5]
        formatted_df = self.format_dataframe_columns(table_headers, table_rows=trans_rows)
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
