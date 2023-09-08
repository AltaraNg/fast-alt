from bank_statement_reader.BankStatementExecutor import BankStatementExecutor

executor = BankStatementExecutor()
print(executor.BANK_STATEMENTS_CHOICES)

# for index in range(1,8):
#     result = executor.execute(choice=index, min_salary=10000000, max_salary=100000)
#     print(result.period)
result = executor.execute(choice=6)
print(result.last_transaction_per_day)
print(result.account_name)
print(result.closing_balance)
print(result.opening_balance)
print(result.total_withdrawals)
print(result.total_deposits)
print(result.period)
