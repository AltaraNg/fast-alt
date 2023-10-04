import unittest

import os.path
import typing

import pytest
from unittest.mock import Mock, MagicMock
import unittest
import pdfplumber

from bank_statement_reader.OpayBankStatement import OpayBankStatement

CHOICE = 8
MIN_SALARY = 100
MAX_SALARY = 100000
HERE = os.path.abspath(os.path.dirname(__file__))


class OpayBankStatementParser(unittest.TestCase):

    @classmethod
    def setUp(cls) -> None:
        path = os.path.join(HERE, '../bank_statement_reader/pdfs/opay/opay.pdf')
        cls.path = path
        cls.pdf = pdfplumber.open(path)
        cls.bank_statement = OpayBankStatement(pdf_directory=path, min_salary=MIN_SALARY, max_salary=MAX_SALARY)
        cls.reader = pdfplumber.open(path, password="")
        cls.text = """2023-08-31T20:33:06 AATransfer -1000.00 0.00 230831013144247550
                        FATOKUNBO|+2348162582183
                        2023-08-31T20:25:44 Bouns +8.00 0.00 230831193132663647
                        2023-08-31T20:24:52 Airtime -400.00 0.00 9031762551|MTN 230831103131324150
                        Access Bank|KOLADE SAMUEL
                        """

    @classmethod
    def tearDown(cls) -> None:
        cls.pdf.close()

    def test_parse_transaction_page_text(self):
        text = """2023-08-31T20:33:06 AATransfer -1000.00 0.00 230831013144247550
                        FATOKUNBO|+2348162582183
                        2023-08-31T20:25:44 Bouns +8.00 0.00 230831193132663647
                        2023-08-31T20:24:52 Airtime -400.00 0.00 9031762551|MTN 230831103131324150
                        Access Bank|KOLADE SAMUEL
                        """
        actual_outcome = self.bank_statement.parse_transaction_page_text(text)
        expected_outcome = [
            ['2023-08-31T20:33:06 AATransfer -1000.00 0.00 230831013144247550\nFATOKUNBO|+2348162582183'],
            ['2023-08-31T20:25:44 Bouns +8.00 0.00 230831193132663647'],
            ['2023-08-31T20:24:52 Airtime -400.00 0.00 9031762551|MTN 230831103131324150\nAccess Bank|KOLADE SAMUEL']
        ]

        self.assertEqual(actual_outcome, expected_outcome)


if __name__ == '__main__':
    unittest.main()
