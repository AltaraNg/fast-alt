import unittest
import os
from unittest.mock import MagicMock

import pdfplumber
from bank_statement_reader.BaseBankStatementReport import BankStatementReport

MIN_SALARY = 100
MAX_SALARY = 100000
HERE = os.path.abspath(os.path.dirname(__file__))


class BaseBankStatementReportTest(unittest.TestCase):

    @classmethod
    def setUp(cls) -> None:
        path = os.path.join(HERE, '../bank_statement_reader/pdfs/fcmb/fcmb_version_one-1.pdf')
        cls.path = path
        cls.pdf = pdfplumber.open(path)
        cls.bank_statement = BankStatementReport(pdf_directory=path, min_salary=MIN_SALARY, max_salary=MAX_SALARY)
        cls.reader = pdfplumber.open(path, password="")

        cls.formatted_summary_table = {
            "opening_balance": "33,020.33",
            "closing_balance": "3,405.26",
            "start_date": "23-Apr-2023",
            "end_date": "22-Jul-2023",
            "account_number": "8113591014",
            "customer_name": "ADEWUYI TAOFEEQ OLAMILEKAN"
        }

    def test_account_name_sample_one(self):
        text = "Account Name: Taofeeq Adewuyi Ola"
        account_name_sample_one = self.bank_statement.get_account_name(text)
        expected_account_name_sample_one = "Taofeeq Adewuyi Ola"
        self.assertEqual(account_name_sample_one, expected_account_name_sample_one)

    def test_account_name_sample_four(self):
        text = "Account Name: Taofeeq Adewuyi"
        account_name_sample_one = self.bank_statement.get_account_name(text)
        expected_account_name_sample_one = "Taofeeq Adewuyi"
        self.assertEqual(account_name_sample_one, expected_account_name_sample_one)

    def test_account_name_sample_two(self):
        text = " Account Name . Taofeeq Adewuyi Ola "
        account_name_sample_one = self.bank_statement.get_account_name(text)
        expected_account_name_sample_one = "Taofeeq Adewuyi Ola"
        self.assertEqual(account_name_sample_one, expected_account_name_sample_one)

    def test_account_name_sample_three(self):
        text = " Account Name Taofeeq Adewuyi Ola "
        account_name_sample_one = self.bank_statement.get_account_name(text)
        expected_account_name_sample_one = "Taofeeq Adewuyi Ola"
        self.assertEqual(account_name_sample_one, expected_account_name_sample_one)

    def test_account_number_sample_one(self):
        text = "Account Number: 8900398485"
        account_number_sample_one = self.bank_statement.get_account_number(text)
        expected_account_number_sample_one = "8900398485"
        self.assertEqual(expected_account_number_sample_one, account_number_sample_one)

    def test_account_number_sample_two(self):
        text = "Account Number: 890039848512"
        account_number_sample_one = self.bank_statement.get_account_number(text)
        expected_account_number_sample_one = "890039848512"
        self.assertEqual(expected_account_number_sample_one, account_number_sample_one)

    def test_account_number_sample_three(self):
        text = "Account Number. 8900398485"
        account_number_sample_one = self.bank_statement.get_account_number(text)
        expected_account_number_sample_one = "8900398485"
        self.assertEqual(expected_account_number_sample_one, account_number_sample_one)

    def test_account_number_sample_four(self):
        text = "kjwenwe Account No: 8900398485  ksjwjknsjd"
        account_number_sample_one = self.bank_statement.get_account_number(text)
        expected_account_number_sample_one = "8900398485"
        self.assertEqual(expected_account_number_sample_one, account_number_sample_one)

    def test_opening_balance_sample_one(self):
        text = "Opening Balance: 234,345,999.09"
        account_name_sample_one = self.bank_statement.get_opening_balance(text)
        expected_account_name_sample_one = 234345999.09
        self.assertEqual(account_name_sample_one, expected_account_name_sample_one)

    def test_get_total_deposit_total_lodgements_format(self):
        text = "Currency: NGN TOTAL LODGEMENTS: 993,755.50"
        result = self.bank_statement.get_total_deposit(text)
        expected_result = 993755.50
        self.assertEqual(result, expected_result)

    def test_get_total_deposit_total_deposits_format(self):
        text = "Currency: NGN TOTAL deposits: 993,755.50"
        result = self.bank_statement.get_total_deposit(text)
        expected_result = 993755.50
        self.assertEqual(result, expected_result)

    def test_get_total_deposit_total_credit_format(self):
        text = "Currency: NGN total credit: 993,755.50"
        result = self.bank_statement.get_total_deposit(text)
        expected_result = 993755.50
        self.assertEqual(result, expected_result)

    def test_get_total_deposit_total_withdrawals_format(self):
        text = "Currency: NGN TOTAL WITHDRAWALS: 993,755.50"
        result = self.bank_statement.get_total_withdrawal(text)
        expected_result = 993755.50
        self.assertEqual(result, expected_result)


    def test_get_total_deposit_total_debit_format(self):
        text = "Currency: NGN TOTAL Debit: 993,755.50"
        result = self.bank_statement.get_total_withdrawal(text)
        expected_result = 993755.50
        self.assertEqual(result, expected_result)

    def test_get_total_deposit_total_debits_format(self):
        text = "Currency: NGN TOTAL Debits: 993,755.50"
        result = self.bank_statement.get_total_withdrawal(text)
        expected_result = 993755.50
        self.assertEqual(result, expected_result)

    def test_get_total_deposit_using_wih_unsupported_format(self):
        text = "Currency: NGN TOTAL Debit sDebit Withdrawals Debits: 993,755.50"
        result = self.bank_statement.get_total_withdrawal(text)
        expected_result = None
        self.assertEqual(result, expected_result)

    def test_opening_balance_sample_two(self):
        text = "Opening Balance: 234,345,999.09"
        account_name_sample_one = self.bank_statement.get_opening_balance(text)
        expected_account_name_sample_one = 234345999.09
        self.assertEqual(account_name_sample_one, expected_account_name_sample_one)

    def test_opening_balance_sample_three(self):
        text = "Opening Balance 234,345,999.09"
        result = self.bank_statement.get_opening_balance(text)
        expected_result = 234345999.09
        self.assertEqual(result, expected_result)

    def test_get_transactions_table_header(self):
        mapping_dic = {
            'date_posted': 'Date Posted',
            'value_date': 'Value Date',
            'description': 'Description',
            'debit': 'Debit',
            'credit': 'Credit',
            'balance': 'Balance'
        }
        self.bank_statement.get_transactions_table_header_mapping = MagicMock(return_value=mapping_dic)
        result = self.bank_statement.get_transactions_table_headers(self.reader)
        self.assertEqual(len(result), len(mapping_dic))
        self.assertListEqual(result, list(mapping_dic.values()))

    def test_get_statement_period_first_pattern(self):
        text = "Period: 01/10/2022 TO 18/01/2023"
        result = self.bank_statement.get_statement_period(text)
        expected_result = {'from_date': "2022-10-01", 'to_date': "2023-01-18"}
        self.assertEqual(result.get('from_date'), expected_result.get('from_date'))
        self.assertEqual(result.get('to_date'), expected_result.get('to_date'))

    def test_get_statement_period_second_pattern(self):
        text = "01-Apr-2023 to 30-Jun-2023"
        result = self.bank_statement.get_statement_period(text)
        expected_result = {'from_date': "2023-04-01", 'to_date': "2023-06-30"}
        self.assertEqual(result.get('from_date'), expected_result.get('from_date'))
        self.assertEqual(result.get('to_date'), expected_result.get('to_date'))

    def test_get_statement_period_third_pattern(self):
        text = "For the Period of: 01-March-2023 to 31-March-2023 Closing Balance: 306.25"
        result = self.bank_statement.get_statement_period(text)
        expected_result = {'from_date': "2023-03-01", 'to_date': "2023-03-31"}
        self.assertEqual(result.get('from_date'), expected_result.get('from_date'))
        self.assertEqual(result.get('to_date'), expected_result.get('to_date'))


if __name__ == '__main__':
    unittest.main()
