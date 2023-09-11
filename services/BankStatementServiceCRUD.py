from sqlalchemy.orm import Session, joinedload
from schemas.bank_statement_schema import BankStatementCreate, BankStatement as BankStatementSchema
from models.BankStatementModel import BankStatement
from pydantic import ValidationError
from datetime import datetime
from exceptions.NotFoundException import NotFoundException
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, asc, desc, or_, and_, delete, func
from fastapi_pagination import Page
from pydantic import Field
from filters.BankStatementQueryParams import BankStatementQueryParams
from filters.BankStatementTransactionsQueryParams import BankStatementTransactionQueryParams
from exceptions.BankStatementExists import BankStatementExists
from schemas.bank_statement_day_end_trans_schema import BankStatementTransactionOut
from models.BankStatementDayEndTransactionsModel import BankStatementDayEndTransactions
from models.BankStatementTransactionsModel import BankStatementTransactionsModel
from config.ConfigService import config

Page = Page.with_custom_options(
    size=Field(15, ge=1, le=100)
)


def bank_statement_exists(db: Session, account_number, start_date, end_date) -> BankStatement | None:
    return db.query(BankStatement).filter(
        BankStatement.account_number == account_number,
        BankStatement.start_date == start_date,
        BankStatement.end_date == end_date
    ).order_by(desc('created_at')).first()


def create_bank_statement(db: Session, bank_statement_data: BankStatementCreate):
    try:

        db_bank_statement = BankStatement(
            customer_id=bank_statement_data.customer_id,
            repayment_capability=bank_statement_data.repayment_capability,
            account_name=bank_statement_data.account_name,
            account_number=bank_statement_data.account_number,
            opening_balance=bank_statement_data.opening_balance,
            closing_balance=bank_statement_data.closing_balance,
            total_deposit=bank_statement_data.total_deposit,
            total_withdrawal=bank_statement_data.total_withdrawal,
            average_monthly_balance=bank_statement_data.average_monthly_balance,
            predicted_average_salary=bank_statement_data.predicted_average_salary,
            salary_predictions_file_url=bank_statement_data.salary_predictions_file_url,
            exported_bank_statement_file_url=bank_statement_data.exported_bank_statement_file_url,
            start_date=datetime.strptime(bank_statement_data.start_date, "%Y-%m-%d"),
            end_date=datetime.strptime(bank_statement_data.end_date, "%Y-%m-%d")
        )

        db.add(db_bank_statement)
        db.commit()
        db.refresh(db_bank_statement)
        return db_bank_statement
    except ValidationError as validation_error:
        raise validation_error
    except Exception as e:
        raise e


def get_bank_statement(db: Session, bank_statement_id) -> BankStatement:
    item = (db.query(BankStatement).options(joinedload(BankStatement.bankStatementDayEndTransactions))
            .filter(BankStatement.id == bank_statement_id).first())
    if item is None:
        raise NotFoundException(f"The provided bank statement id: {bank_statement_id} could not be found")
    return item


def retrieve_bank_statement_repayment_capability(db: Session, bank_statement_id, amount):
    bank_statement = get_bank_statement(db, bank_statement_id)
    date_ranges = generate_date_range(bank_statement.start_date, bank_statement.end_date);
    if config.db_connection == 'sqlite':
        items = (db.query(
            func.STRFTIME("%m-%Y", BankStatementDayEndTransactions.transaction_date).label("month"),
            func.count().label("count_no")
        ).filter(BankStatementDayEndTransactions.balance >= amount,
                 BankStatementDayEndTransactions.bank_statement_id == bank_statement_id)
                 .group_by(
            func.STRFTIME("%m-%Y", BankStatementDayEndTransactions.transaction_date)).all())
    else:
        items = (db.query(
            func.DATE_FORMAT(BankStatementDayEndTransactions.transaction_date, "%m-%Y").label("month"),
            func.count().label("count_no")
        ).filter(BankStatementDayEndTransactions.balance >= amount,
                 BankStatementDayEndTransactions.bank_statement_id == bank_statement_id)
                 .group_by(
            func.DATE_FORMAT(BankStatementDayEndTransactions.transaction_date, "%m-%Y"))
                 .order_by(desc('month'))
                 .all())
    result = []
    for index, item in enumerate(items):
        result.append({
            "month_name": datetime.strptime(item.month, "%m-%Y").strftime('%B'),
            "month_year": item.month,
            "count": item.count_no,
        })
        date_ranges = [date_range_item for date_range_item in date_ranges if
                       date_range_item["month_year"].lower() != item.month]
    final_result = result + date_ranges
    final_result = sorted(final_result, key=lambda x: x['month_year'])
    return final_result


def merge_dates(generated_date_ranges, actual_actual_date):
    print(generated_date_ranges, actual_actual_date)


def generate_date_range(start_date, end_date):
    current_date = start_date
    date_format = "%m-%Y"
    date_ranges = []
    while current_date <= end_date:
        formatted_date = current_date.strftime(date_format)
        # Increment to the next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
        date_ranges.append(
            {
                "month_name": datetime.strptime(formatted_date, "%m-%Y").strftime('%B'),
                "month_year": formatted_date,
                "count": 0,
            }
        )
    return date_ranges


def all_bank_statements(filter_query: BankStatementQueryParams, db: Session) -> Page[BankStatementSchema]:
    query = db.query(BankStatement)
    query = filter_query.apply(query)
    query = query.order_by(desc('created_at'))
    return paginate(query)


def all_bank_statement_transactions(filter_query: BankStatementTransactionQueryParams, db: Session,
                                    bank_statement_id) -> Page[
    BankStatementTransactionOut]:
    get_bank_statement(db, bank_statement_id)
    query = db.query(BankStatementTransactionsModel)
    query = query.filter(BankStatementTransactionsModel.bank_statement_id == bank_statement_id)
    query = filter_query.apply(query)
    query = query.order_by(asc('transaction_date'))
    return paginate(query)


def sync_with_end_of_day_transactions(db: Session, end_of_day_transactions: list[dict], bank_statement: BankStatement):
    data = []
    # build model instances
    for transaction in end_of_day_transactions:
        create_data = BankStatementTransactionOut.from_request_api(
            bank_statement_id=bank_statement.id,
            balance=transaction.get('balance'),
            deposit=transaction.get('deposits'),
            withdrawal=transaction.get('withdrawals'),
            transaction_date=transaction.get('transaction_date'),
            description=transaction.get('description')
        )
        data.append(BankStatementTransactionOut.from_create_to_model_day_end_transactions(create_data))
    # remove existing data
    (db.query(BankStatementDayEndTransactions).
     filter(BankStatementDayEndTransactions.bank_statement_id == bank_statement.id).
     delete())
    db.add_all(data)
    db.commit()
    return


def sync_with_all_transactions(db: Session, transactions: list[dict], bank_statement: BankStatement):
    data = []
    # build model instances
    for transaction in transactions:
        create_data = BankStatementTransactionOut.from_request_api(
            bank_statement_id=bank_statement.id,
            balance=transaction.get('balance'),
            deposit=transaction.get('deposits'),
            withdrawal=transaction.get('withdrawals'),
            transaction_date=transaction.get('transaction_date'),
            description=transaction.get('description')
        )
        data.append(BankStatementTransactionOut.from_create_to_model_transactions(create_data))
    # remove existing data
    (db.query(BankStatementTransactionsModel).
     filter(BankStatementTransactionsModel.bank_statement_id == bank_statement.id).
     delete())
    db.add_all(data)
    db.commit()
    return
