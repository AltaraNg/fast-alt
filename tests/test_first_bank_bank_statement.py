import os.path

import unittest
from unittest.mock import MagicMock
import pdfplumber

from bank_statement_reader.FirstBankStatement import FirstBankStatement

MIN_SALARY = 100
MAX_SALARY = 100000
HERE = os.path.abspath(os.path.dirname(__file__))


class FirstBankStatementTest(unittest.TestCase):
    path_v2 = None
    reader = None
    bank_statement: FirstBankStatement = None

    @classmethod
    def setUp(cls) -> None:
        path = os.path.join(HERE, '../bank_statement_reader/pdfs/firstbank/first_mobile_version.pdf')
        cls.path = path
        cls.path_v2 = os.path.join(HERE, '../bank_statement_reader/pdfs/firstbank/first_bank_version.pdf')
        cls.bank_statement = FirstBankStatement(pdf_directory=path, min_salary=MIN_SALARY,
                                                max_salary=MAX_SALARY, password="81054")
        # cls.reader = pdfplumber.open(path_or_fp=path, password="81054")
        # cls.bank_version_reader = pdfplumber.open(path_or_fp=cls.path_v2, password="81054")
        cls.mobile_text = """
                     CAUTION: Please ensure you do not reveal your online banking password(s), token number(s) and 
                     ATM PIN(s) to a third party. Do not open links, respond to suspicious calls, mails or letters 
                     requesting your banking details. These messages are fraudulent and are not from FirstBank. 
                     Account No: 3064581054 Currency: NGN Account Type: XPLOREFIRST TIER 2 A/C (16-29) 
                     Opening Balance: 303.68 For the Period of: 01-March-2023 to 31-March-2023 Closing Balance: 306.25 
                     Account Name: ADEWUYI TAOFEEK OLAMILEKAN Total Credit 2.57 Address ., Total Debit 0.00 TransDate 
                     Reference Transaction Details 
                    """
        cls.bank_version_text = """
        Dear Ibrahim Mariam Asabi SOKOTO ROAD, OPP EAT WELL RESTAURANT,,SABO- OKE,MAILINGADD1 ILORIN, KWARA NIGERIA 
        Please find below your bank statement for the period: 01-Feb-2023 To 01-May-2023 Account No: 3100704151 
        Pending Debit: (8,500.00) Account Name: IBRAHIM MARIAM ASABI Available Balance: 98,747.13 
        Account Type: SAVINGS A/C-PERSONAL Total Credit: 2,223,309.00 Currency: NGN Total Debit: 2,146,456.96 Trans Date Ref.
        """

    # @classmethod
    # def tearDown(cls) -> None:
    #     cls.reader.close()

    def test_mobile_account_number(self):
        account_name = self.bank_statement.get_account_number(self.mobile_text)
        expected_account_number = "3064581054"
        assert account_name == expected_account_number

    def test_bank_version_account_number(self):
        account_name = self.bank_statement.get_account_number(self.bank_version_text)
        expected_account_number = "3100704151"
        assert account_name == expected_account_number

    def test_mobile_account_name(self):
        account_name = self.bank_statement.get_account_name(self.mobile_text)
        expected_account_name = "ADEWUYI TAOFEEK OLAMILEKAN"
        assert account_name == expected_account_name

    def test_bank_version_account_name(self):
        account_name = self.bank_statement.get_account_name(self.bank_version_text)
        expected_account_name = "IBRAHIM MARIAM ASABI"
        assert account_name == expected_account_name

    def test_mobile_get_account_number_len(self):
        account_number = self.bank_statement.get_account_number(self.mobile_text)
        assert len(account_number) == 10 or len(account_number) == 12

    def test_bank_version_get_account_number_len(self):
        account_number = self.bank_statement.get_account_number(self.bank_version_text)
        assert len(account_number) == 10 or len(account_number) == 12

    def test_mobile_bank_statement_period(self):
        period = self.bank_statement.get_statement_period(self.mobile_text)
        start_date = period.get("from_date")
        end_date = period.get("to_date")
        expected_start_date = "2023-03-01"
        expected_end_date = "2023-03-31"
        assert start_date == expected_start_date
        assert end_date == expected_end_date

    def test_bank_version_bank_statement_period(self):
        period = self.bank_statement.get_statement_period(self.bank_version_text)
        start_date = period.get("from_date")
        end_date = period.get("to_date")
        expected_start_date = "2023-02-01"
        expected_end_date = "2023-05-01"
        assert start_date == expected_start_date
        assert end_date == expected_end_date

    def test_mobile_get_opening_balance(self):
        opening_balance = self.bank_statement.get_opening_balance(self.mobile_text)
        expected_balance = 303.68
        assert opening_balance == expected_balance

    def test_bank_version_get_opening_balance(self):
        first_row = ['', '', 'Opening Balance', '', '9,502.91']
        opening_balance = self.bank_statement.get_opening_balance(first_row)
        expected_balance = 9502.91
        assert opening_balance == expected_balance

    def test_mobile_get_closing_balance(self):
        closing_balance = self.bank_statement.get_closing_balance(self.mobile_text)
        expected_balance = 306.25
        assert closing_balance == expected_balance

    def test_bank_version_get_closing_balance(self):
        first_row = ['', '', 'Closing Balance', '', '98,937.97']
        closing_balance = self.bank_statement.get_closing_balance(first_row)
        expected_balance = 98937.97
        assert closing_balance == expected_balance
