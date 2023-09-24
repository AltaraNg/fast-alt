import os.path
import typing

import pytest
from unittest.mock import Mock, MagicMock
import unittest
import pdfplumber

from bank_statement_reader.UBABankStatement import UBABankStatement

CHOICE = 3
pdf_directory = "pdfs/uba2.pdf"
MIN_SALARY = 100
MAX_SALARY = 100000
HERE = os.path.abspath(os.path.dirname(__file__))


class UbaBankStatementTest(unittest.TestCase):
    @classmethod
    def setUp(cls) -> None:
        path = os.path.join(HERE, '../bank_statement_reader/pdfs/uba/uba_version_two-1.pdf')
        cls.path = path
        cls.pdf = pdfplumber.open(path)
        cls.bank_statement = UBABankStatement(pdf_directory=path, min_salary=MIN_SALARY, max_salary=MAX_SALARY)
        cls.reader = pdfplumber.open(path, password="")
        cls.text = """
                      Account Number: 2102836998
                      Account Name: OLATUNDE OMONIKE BLESIING Transaction Date From: December 2nd 2022 Transaction Date To: March 2nd 2023
                      Debits: 455,791.89
                      Credits: 500,011.26
                    """

    @classmethod
    def tearDown(cls) -> None:
        cls.pdf.close()

    def test_account_number(self):
        account_name = self.bank_statement.get_account_number(self.text)
        expected_account_number = "2102836998"
        assert account_name == expected_account_number

    def test_account_name(self):
        account_name = self.bank_statement.get_account_name(self.text)
        expected_account_name = "OLATUNDE OMONIKE BLESIING"
        assert account_name == expected_account_name

    def test_get_account_number_len(self):
        account_number = self.bank_statement.get_account_number(self.text)
        assert len(account_number) == 10 or len(account_number) == 12

    def test_bank_statement_period(self):
        period = self.bank_statement.get_statement_period(self.text)
        start_date = period.get("from_date")
        end_date = period.get("to_date")
        expected_start_date = "2022-12-02"
        expected_end_date = "2023-03-02"
        assert start_date == expected_start_date
        assert end_date == expected_end_date
