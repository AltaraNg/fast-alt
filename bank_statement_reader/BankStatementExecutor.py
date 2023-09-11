import logging

from bank_statement_reader.AccessBankStatement import AccessBankStatement
from bank_statement_reader.FcmbBankStatement import FcmbBankStatement
from bank_statement_reader.FidelityBankStatement import FidelityBankStatement
from bank_statement_reader.FirstBankStatement import FirstBankStatement
from bank_statement_reader.GtBankStatement import GtBankStatement
from bank_statement_reader.SterlingBankStatement import SterlingBankStatement
from bank_statement_reader.UBABankStatement import UBABankStatement
from bank_statement_reader.ZenithBankStatement import ZenithBankStatement
from bank_statement_reader.BankStatementFinalResultResponse import BankStatementFinalResultResponse
from bank_statement_reader.exceptions.InvalidBankStatementChoice import InvalidBankStatementChoice
from bank_statement_reader.exceptions.BankStatementProcessingFailed import BankStatementProcessingFailed
from bank_statement_reader.exceptions.InvalidSalaryRange import InvalidSalaryRange
from bank_statement_reader.exceptions.InvalidDataFrameType import InvalidDataframeType
from bank_statement_reader.BaseBankStatementReport import BankStatementReport
from bank_statement_reader.exceptions.InprocessibleBankStatementSupplied import UnprocessableBankStatementSupplied


class BankStatementExecutor:
    bank_statement_report_instance: BankStatementReport = BankStatementReport
    BANK_STATEMENTS_CHOICES = {
        1: "Zenith",
        2: "UBA",
        3: "Access",
        4: "First",
        5: "GT",
        6: "FCMB",
        7: "Fidelity",
        8: "Sterling"
        # Add more bank statements with corresponding numbers here
    }

    def __init__(self):
        # self.pdf_directory = pdf_directory
        self.bank_statement_report = self.bank_statement_report_instance
        self.bank_statements_choices = self.BANK_STATEMENTS_CHOICES

    def close(self):
        exit(0)

    def display_menu(self):
        print("Available Bank Statements:")
        for number, statement in self.bank_statements_choices.items():
            print(f"{number}. {statement}")

    def get_user_choice(self):
        while True:
            try:
                choice = int(input("Select a number to execute the corresponding bank statement: "))
                if choice in self.bank_statements_choices:
                    return choice
                else:
                    print("Invalid option. Please choose a valid number.")
            except ValueError:
                self.display_menu()
                print("Invalid input. Please enter a number.")

    def execute(self, choice, pdf_file='', password='', min_salary=10000,
                max_salary=500000) -> BankStatementFinalResultResponse:
        try:
            file_to_execute = self.bank_statements_choices.get(choice)
            if file_to_execute is None:
                raise InvalidBankStatementChoice
            print(file_to_execute + " Bank Statement Selected")
            bank_statement = None
            if choice == 1:
                bank_statement = ZenithBankStatement(pdf_directory=pdf_file, min_salary=min_salary,
                                                     max_salary=max_salary)
            elif choice == 2:
                bank_statement = UBABankStatement(pdf_directory=pdf_file, min_salary=min_salary,
                                                  max_salary=max_salary)
            elif choice == 3:
                bank_statement = AccessBankStatement(pdf_directory=pdf_file, min_salary=min_salary,
                                                     max_salary=max_salary)
            elif choice == 4:
                bank_statement = FirstBankStatement(pdf_directory=pdf_file, min_salary=min_salary,
                                                    max_salary=max_salary, password=password)
            elif choice == 5:
                bank_statement = GtBankStatement(pdf_directory=pdf_file, min_salary=min_salary,
                                                 max_salary=max_salary)
            elif choice == 6:
                bank_statement = FcmbBankStatement(pdf_directory=pdf_file, min_salary=min_salary,
                                                   max_salary=max_salary)
            elif choice == 7:
                bank_statement = FidelityBankStatement(pdf_directory=pdf_file, min_salary=min_salary,
                                                       max_salary=max_salary)
            elif choice == 8:
                bank_statement = SterlingBankStatement(pdf_directory=pdf_file, min_salary=min_salary,
                                                       max_salary=max_salary)
            self.bank_statement_report_instance = bank_statement
            result = bank_statement.result()

            reader, status, message = bank_statement.get_pdf_reader()
            table_headers = bank_statement.get_transactions_table_headers(reader)
            salary_df = bank_statement.predict_salary_income(result.get('dataframe'), table_headers)
            predicted_salary_average = bank_statement.get_predicted_salary_average(salary_df)
            last_transaction_per_day = bank_statement.last_transaction_per_day(result.get('dataframe'))

            # bank_statement.predict_repayment_capability(result.get('dataframe'), required_payment=15000.00)

            excel_file_path = bank_statement.export_to_excel(
                dataframe=result.get('dataframe'),
                name=result.get('account_name'),
                start_date=result.get('period').get('from_date'),
                end_date=result.get('period').get('to_date')
            )
            salary_excel_file_path = bank_statement.export_to_excel(
                dataframe=salary_df,
                name=result.get('account_name'),
                start_date=result.get('period').get('from_date'),
                end_date=result.get('period').get('to_date'),
                is_salary=True
            )

            if excel_file_path:
                result.update({'excel_file_path': excel_file_path})
            if salary_excel_file_path:
                result.update({'salary_excel_file_path': salary_excel_file_path})
            transactions = result.get('dataframe')
            transactions.columns = transactions.columns.str.lower()
            transactions.columns = transactions.columns.str.replace(' ', '_')
            last_transaction_per_day.columns = last_transaction_per_day.columns.str.lower()
            last_transaction_per_day.columns = last_transaction_per_day.columns.str.replace(' ', '_')
            response = BankStatementFinalResultResponse(
                selected_bank_name=bank_statement.bank_name,
                min_salary=bank_statement.min_salary,
                max_salary=bank_statement.max_salary,
                period=result.get('period'),
                account_name=result.get('account_name'),
                account_number=result.get('account_number'),
                total_deposits=result.get('total_turn_over_credit'),
                total_withdrawals=result.get('total_turn_over_debits'),
                opening_balance=result.get('opening_balance'),
                closing_balance=result.get('closing_balance'),
                average_monthly_balance=result.get('average_monthly_balance'),
                excel_file_path=result.get('excel_file_path'),
                salary_excel_file_path=result.get('salary_excel_file_path'),
                predicted_average_salary=predicted_salary_average,
                last_transaction_per_day=last_transaction_per_day.to_dict(orient='records'),
                transactions=transactions.to_dict(orient='records')
            )
            return response
        except InvalidBankStatementChoice as e:
            raise e
        except InvalidSalaryRange as e:
            raise e
        except BankStatementProcessingFailed as e:
            raise e
        except InvalidDataframeType as e:
            raise e
        except UnprocessableBankStatementSupplied as e:
            raise e
        except BaseException as e:
            logging.error(e)
            raise BankStatementProcessingFailed
