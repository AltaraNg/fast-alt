import os.path
import typing

import pytest
from unittest.mock import Mock, MagicMock
import unittest
import pdfplumber

from bank_statement_reader.GtBankStatement import GtBankStatement

MIN_SALARY = 100
MAX_SALARY = 100000
HERE = os.path.abspath(os.path.dirname(__file__))


class GtBankStatementTest(unittest.TestCase):
    @classmethod
    def setUp(cls) -> None:
        path = os.path.join(HERE, '../bank_statement_reader/pdfs/gt/gt_version_one-2.pdf')
        cls.path = path
        cls.pdf = pdfplumber.open(path)
        cls.bank_statement = GtBankStatement(pdf_directory=path, min_salary=MIN_SALARY, max_salary=MAX_SALARY)
        cls.reader = pdfplumber.open(path, password="")
        cls.text = """
                     Statement Period :01-Oct-2022 to 31-Dec-2022 Print. Date 05-Jan-2023 Branch Name TAIWO ROAD,ILORIN 
                     Account No 0132156951 Internal Reference 443/459431/1/59/0 Address 17, ABDULRASAQ STREET,G.R.A 
                     Account Type SAVINGS ACCOUNT Currency Naira Total Debit 768,647.98 Total Credit 746,832.19 Opening Balance 21,866.60 
                     Closing Balance 50.81 CUSTOMER STATEMENT SALIHU, ABDULWAHEED OLATUNJI Trans. Date Value. Date Reference Debits 
                    """
        cls.formatted_summary_table = {
            'print_date': '05-Jan-2023',
            'branch_name': 'TAIWO ROAD,ILORIN',
            'account_no': '0132156951',
            'internal_reference': '443/459431/1/59/0',
            'address': '17, ABDULRASAQ STREET,G.R.A',
            'account_type': 'SAVINGS ACCOUNT',
            'currency': 'Naira',
            'total_debit': '768,647.98',
            'total_credit': '746,832.19',
            'opening_balance': '21,866.60',
            'closing_balance': '50.81'
        }

    @classmethod
    def tearDown(cls) -> None:
        cls.pdf.close()

    def test_account_number(self):
        account_name = self.bank_statement.get_account_number(self.formatted_summary_table)
        expected_account_number = "0132156951"
        assert account_name == expected_account_number

    def test_account_name(self):
        account_name = self.bank_statement.get_account_name(self.text)
        expected_account_name = "SALIHU ABDULWAHEED OLATUNJI"
        assert account_name == expected_account_name

    def test_account_name_v2(self):
        text_v2 = """
        Opening Balance -41,645.75 Closing Balance 236,086.65 Usable Balance 586,022.68 
        CUSTOMER STATEMENT ADEDAYO OLUDOLAMU OLUYEMISI 
        Trans. Date Value"
        """
        account_name = self.bank_statement.get_account_name(text_v2)
        expected_account_name = "ADEDAYO OLUDOLAMU OLUYEMISI"
        assert account_name == expected_account_name

    def test_get_account_number_len(self):
        account_number = self.bank_statement.get_account_number(self.formatted_summary_table)
        assert len(account_number) == 10 or len(account_number) == 12

    def test_bank_statement_period(self):
        period = self.bank_statement.get_statement_period(self.text)
        start_date = period.get("from_date")
        end_date = period.get("to_date")
        expected_start_date = "2022-10-01"
        expected_end_date = "2022-12-31"
        assert start_date == expected_start_date
        assert end_date == expected_end_date
