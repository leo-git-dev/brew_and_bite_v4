# business_logic/report_manager_v3.py

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from database.models_v3 import Base, Sales, Expense, Inventory, User


class FinancialReportManager:
    def __init__(self, db_url="sqlite:///brew_and_bite_v3.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)  # Ensure all tables are created
        self.Session = sessionmaker(bind=self.engine)

    def calculate_total_sales_per_day(self):
        """Calculate total sales per day."""
        session = self.Session()
        try:
            results = session.query(
                func.date(Sales.sales_date).label("date"),
                func.sum(Sales.total_cost).label("total_sales")
            ).group_by(func.date(Sales.sales_date)).order_by(func.date(Sales.sales_date)).all()
            return results
        finally:
            session.close()

    def calculate_sales_by_category(self):
        """Calculate total sales by product category."""
        session = self.Session()
        try:
            results = session.query(
                Inventory.category,
                func.sum(Sales.total_cost).label("total_sales")
            ).join(Sales, Sales.item_id == Inventory.item_id).group_by(Inventory.category).all()
            return results
        finally:
            session.close()

    def calculate_total_expenses_per_day(self):
        """Calculate total expenses per day."""
        session = self.Session()
        try:
            results = session.query(
                func.date(Expense.expense_date).label("date"),
                func.sum(Expense.total_cost).label("total_expenses")
            ).group_by(func.date(Expense.expense_date)).order_by(func.date(Expense.expense_date)).all()
            return results
        finally:
            session.close()

    def calculate_expense_vs_sales(self):
        """Calculate total expenses vs total sales."""
        session = self.Session()
        try:
            total_sales = session.query(func.sum(Sales.total_cost)).scalar() or 0
            total_expenses = session.query(func.sum(Expense.total_cost)).scalar() or 0
            difference = total_sales - total_expenses
            return {
                "total_sales": total_sales,
                "total_expenses": total_expenses,
                "difference": difference
            }
        finally:
            session.close()

    def calculate_expense_by_supplier_and_category(self):
        """Calculate expenses by supplier and category."""
        session = self.Session()
        try:
            results = session.query(
                User.company_name.label("supplier"),
                Expense.category.label("category"),
                func.sum(Expense.total_cost).label("total_expenses")
            ).join(User, Expense.supplier_id == User.user_id).group_by(User.company_name, Expense.category).all()
            return results
        finally:
            session.close()

    def generate_comprehensive_report(self):
        """Generate a comprehensive financial report."""
        report = {}
        report["sales_per_day"] = self.calculate_total_sales_per_day()
        report["sales_by_category"] = self.calculate_sales_by_category()
        report["expenses_per_day"] = self.calculate_total_expenses_per_day()
        report["expense_vs_sales"] = self.calculate_expense_vs_sales()
        report["expense_by_supplier_and_category"] = self.calculate_expense_by_supplier_and_category()
        return report
