import os.path
import unittest
import pdfplumber

from bank_statement_reader.AccessBankStatement import AccessBankStatement

MIN_SALARY = 100
MAX_SALARY = 100000
HERE = os.path.abspath(os.path.dirname(__file__))


class AccessBankStatementTest(unittest.TestCase):
    @classmethod
    def setUp(cls) -> None:
        path = os.path.join(HERE, '../bank_statement_reader/pdfs/access/access_version_one.pdf')
        cls.path = path
        cls.pdf = pdfplumber.open(path)
        cls.bank_statement = AccessBankStatement(pdf_directory=path, min_salary=MIN_SALARY, max_salary=MAX_SALARY)
        cls.reader = pdfplumber.open(path, password="")
        cls.text = """
                     ABEOKUTA BRANCH 14 LALUBU STREET OKE ILEWO, ABEOKUTA OGUN STATE, NIGERIA 
                     Account Statement Summary Details ACCOUNT NO. 0015042839 OPENING BALANCE: 2,469.37 
                     Summary Statement for 01-Feb-2023 To 30-Apr-2023 TOTAL WITHDRAWALS: 996,207.34 
                     Currency: NGN TOTAL LODGEMENTS: 993,755.50 Account Name: ABEL AKINPELU ADARANIJO 
                     CLOSING BALANCE: 17.53 CLEARED BALANCE: 30,148.98 UNCEARED BALANCE: 0.00 
                     PRIVATE & CONFIDENTIAL PREPAID CARD-PREMIUM Value Date Transaction Details 
                    """
        cls.formatted_summary_table = {
            "opening_balance": "15,940,439.25",
            "closing_balance": "15,861,937.09",
            "summary_statement_for": "Monday, July 10, 2023 to Monday, August 21, 2023",
            "account_number": "1797631381",
            "account_name": "OLAOSEBIKAN BABAJIDE SHODEYI"
        }

    @classmethod
    def tearDown(cls) -> None:
        cls.pdf.close()

    def test_account_number_version_one(self):
        self.bank_statement.version_one = True
        account_name = self.bank_statement.get_account_number(self.text)
        expected_account_number = "0015042839"
        assert account_name == expected_account_number

    def test_account_name_version_one(self):
        self.bank_statement.version_one = True
        account_name = self.bank_statement.get_account_name(self.text)
        expected_account_name = "ABEL AKINPELU ADARANIJO"
        assert account_name == expected_account_name

    def test_get_account_number_len_version_one(self):
        self.bank_statement.version_one = True
        account_number = self.bank_statement.get_account_number(self.text)
        assert len(account_number) == 10 or len(account_number) == 12

    def test_get_opening_balance_version_one(self):
        self.bank_statement.version_one = True
        opening_balance = self.bank_statement.get_opening_balance(self.text)
        expected_balance = 2469.37
        assert opening_balance == expected_balance

    def test_get_closing_balance_version_one(self):
        self.bank_statement.version_one = True
        closing_balance = self.bank_statement.get_closing_balance(self.text)
        expected_balance = 17.53
        assert closing_balance == expected_balance

    def test_bank_statement_period_version_one(self):
        self.bank_statement.version_one = True
        period = self.bank_statement.get_statement_period(self.text)
        start_date = period.get("from_date")
        end_date = period.get("to_date")
        expected_start_date = "2023-02-01"
        expected_end_date = "2023-04-30"
        assert start_date == expected_start_date
        assert end_date == expected_end_date

    def test_account_number_version_two(self):
        self.bank_statement.version_two = True
        account_name = self.bank_statement.get_account_number(self.formatted_summary_table)
        expected_account_number = "1797631381"
        assert account_name == expected_account_number

    def test_account_name_version_two(self):
        self.bank_statement.version_two = True
        account_name = self.bank_statement.get_account_name(self.formatted_summary_table)
        expected_account_name = "OLAOSEBIKAN BABAJIDE SHODEYI"
        assert account_name == expected_account_name

    def test_get_account_number_len_version_two(self):
        self.bank_statement.version_two = True
        account_number = self.bank_statement.get_account_number(self.formatted_summary_table)
        assert len(account_number) == 10 or len(account_number) == 12

    def test_get_opening_balance_version_two(self):
        self.bank_statement.version_two = True
        opening_balance = self.bank_statement.get_opening_balance(self.formatted_summary_table)
        expected_balance = 15940439.25
        assert opening_balance == expected_balance

    def test_get_closing_balance_version_two(self):
        self.bank_statement.version_two = True
        closing_balance = self.bank_statement.get_closing_balance(self.formatted_summary_table)
        expected_balance = 15861937.09
        assert closing_balance == expected_balance

    def test_bank_statement_period_version_two(self):
        self.bank_statement.version_two = True
        period = self.bank_statement.get_statement_period(self.formatted_summary_table)
        start_date = period.get("from_date")
        end_date = period.get("to_date")
        expected_start_date = "2023-07-10"
        expected_end_date = "2023-08-21"
        assert start_date == expected_start_date
        assert end_date == expected_end_date
