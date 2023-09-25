import argparse
import os
import sys

# Define a template for the class file
CLASS_TEMPLATE = """\
from bank_statement_reader.BaseBankStatementReport import BankStatementReport
from abc import abstractmethod

class {class_name}(BankStatementReport):

     def __init__(self, pdf_directory, min_salary, max_salary):
        if pdf_directory is None or pdf_directory == '':
            pdf_directory = "bank_statement_reader/pdfs/{pdf_folder}/{pdf_name}.pdf"
        super().__init__(password='', pdf_directory=pdf_directory, min_salary=min_salary, max_salary=max_salary,
                         bank_name='{bank_name}')
     
     @abstractmethod
     def get_transactions_table_rows(self, reader, page):
        pass

     @abstractmethod
     def get_transactions_table_header_mapping(self):
        pass
        
        
     @abstractmethod
     def result(self):
        pass
        
     @abstractmethod
     def predict_salary_income(self, dataframe, table_headers):
        pass
"""


def generate_class_file(bank_name):
    """
        Generate a Python class file for a bank statement.

        Args:
            bank_name (str): The name of the bank for which the class file is to be generated.

        Raises:
            SystemExit: If a class file for the specified bank already exists.

        Returns:
            None
    """

    file_name = bank_name.capitalize() + "BankStatement.py"
    class_name = bank_name + "BankStatement"
    # Check if the file already exists in the "bank_statement" directory
    file_path = os.path.join("bank_statement_reader", file_name)

    if os.path.exists(file_path):
        sys.exit(f"Error: Implementation for {bank_name} already exists")

    # Replace placeholders in the template with provided inputs
    class_code = CLASS_TEMPLATE.format(bank_name=bank_name.lower(), class_name=class_name, pdf_name=bank_name.lower(),
                                       pdf_folder=bank_name.lower())

    # Write the class code to the specified file
    with open(file_path, "w") as file:
        file.write(class_code)


def main():
    """
       Main function to generate a bank statement class file based on user input.

       Args:
           None

       Returns:
           None
    """
    # Create a command-line argument parser
    parser = argparse.ArgumentParser(description="Generate a banks statement class file for supplied bank name.")

    # Add arguments for filename, class name, and superclass
    parser.add_argument("bank_name", help="Name of the bank statement to generate")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Add validation logic here
    if not args.bank_name:
        sys.exit("Error: Bank name is required")

    # Generate the class file with the provided inputs
    generate_class_file(args.bank_name)
    sys.stdout.write(f"Success: {args.bank_name} bank statement class generated successfully\n")


if __name__ == "__main__":
    main()
