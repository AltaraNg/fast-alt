import os.path

from unittest.mock import MagicMock
import unittest
import pdfplumber
import pandas as pd
from bank_statement_reader.FcmbBankStatement import FcmbBankStatement

CHOICE = 3
pdf_directory = "pdfs/fcmb.pdf"
MIN_SALARY = 100
MAX_SALARY = 100000
HERE = os.path.abspath(os.path.dirname(__file__))


class FcmbBankStatementTest(unittest.TestCase):
    @classmethod
    def setUp(cls) -> None:
        path = os.path.join(HERE, '../bank_statement_reader/pdfs/fcmb/fcmb_version_one-1.pdf')
        cls.path = path
        cls.pdf = pdfplumber.open(path)
        cls.bank_statement = FcmbBankStatement(pdf_directory=path, min_salary=MIN_SALARY, max_salary=MAX_SALARY)
        cls.reader = pdfplumber.open(path, password="")
        cls.formatted_summary_table = {
            # "opening_balance": "33,020.33",
            "opening_balance": "8,678,437.86",
            "closing_balance": "3,405.26",
            "start_date": "23-Apr-2023",
            "end_date": "22-Jul-2023",
            "account_number": "8113591014",
            "customer_name": "ADEWUYI TAOFEEQ OLAMILEKAN"
        }

    @classmethod
    def tearDown(cls) -> None:
        cls.pdf.close()

    def test_bank_statement_class_instantiation(self):
        assert self.bank_statement.pdf_directory == self.path
        assert self.bank_statement.min_salary == MIN_SALARY
        assert self.bank_statement.max_salary == MAX_SALARY

    def test_valid_file_path(self):
        reader, status, message = self.bank_statement.get_pdf_reader()
        assert status == 1

    def test_reader_is_instance_of_PDF(self):
        reader, status, message = self.bank_statement.get_pdf_reader()
        assert isinstance(reader, pdfplumber.PDF)

    def test_page_count(self):
        reader, status, message = self.bank_statement.get_pdf_reader()
        page_count = len(reader.pages)
        assert page_count >= 0

    def test_account_number(self):
        account_name = self.bank_statement.get_account_number(self.formatted_summary_table)
        expected_account_number = "8113591014"
        assert account_name == expected_account_number

    def test_account_name(self):
        account_name = self.bank_statement.get_account_name(self.formatted_summary_table)
        expected_account_name = "ADEWUYI TAOFEEQ OLAMILEKAN"
        assert account_name == expected_account_name

    def test_get_opening_balance(self):
        opening_balance = self.bank_statement.get_opening_balance(self.formatted_summary_table)
        expected_balance = 8678437.86
        assert opening_balance == expected_balance

    def test_get_closing_balance(self):
        closing_balance = self.bank_statement.get_closing_balance(self.formatted_summary_table)
        expected_balance = 3405.26
        assert closing_balance == expected_balance

    def test_get_account_number(self):
        account_number = self.bank_statement.get_account_number(self.formatted_summary_table)
        assert len(account_number) == 10 or len(account_number) == 12

    def test_bank_statement_period(self):
        period = self.bank_statement.get_statement_period(self.formatted_summary_table)
        start_date = period.get("from_date")
        end_date = period.get("to_date")
        expected_start_date = "2023-04-23"
        expected_end_date = "2023-07-22"
        assert start_date == expected_start_date
        assert end_date == expected_end_date

    def test_result_method(self):
        account_name_extracted = "John Doe"
        account_number_extracted = "123456789"
        total_deposit_extracted = 5000.00
        total_withdrawals_extracted = 3000.00
        opening_balance_extracted = 1000.00
        closing_balance_extracted = 3000.00
        average_monthly_balance = 2000.00
        statement_period_extracted = {'from_date': '10-Oct-2022', 'to_date': '14-Jan-2023'}
        formatted_df = pd.DataFrame()

        # self.bank_statement.extract_formatted_df = lambda text: formatted_df
        self.bank_statement.extract_account_name = lambda text: account_name_extracted
        self.bank_statement.extract_account_number = lambda text: account_number_extracted
        self.bank_statement.extract_total_deposit = lambda text: total_deposit_extracted
        self.bank_statement.extract_total_withdrawals = lambda text: total_withdrawals_extracted
        self.bank_statement.extract_opening_balance = lambda text: opening_balance_extracted
        self.bank_statement.extract_closing_balance = lambda text: closing_balance_extracted
        self.bank_statement.calculate_average_monthly_balance = lambda: average_monthly_balance
        # Mock the get_pdf_reader method to return a reader and status
        mock_reader = pdfplumber.open(self.path, password="")
        self.bank_statement.get_pdf_reader = MagicMock(return_value=(mock_reader, 1, "File loaded successfully"))

        # Mock the get_pdf_page_text method to return mock text
        self.bank_statement.get_pdf_page_text = MagicMock(return_value="Mock PDF text")
        self.bank_statement.format_dataframe_columns = MagicMock(return_value=formatted_df)
        # Mock the format_account_summary_table method to return mock text
        self.bank_statement.format_account_summary_table = MagicMock(return_value=self.formatted_summary_table)
        self.bank_statement.get_average_monthly_balance = MagicMock(return_value=3000)
        self.bank_statement.get_statement_period = MagicMock(
            return_value={'from_date': '10-Oct-2022', 'to_date': '14-Jan-2023'})
        result = self.bank_statement.result()
        # Define the expected response structure
        expected_response = {
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
        assert result.keys() == expected_response.keys()
