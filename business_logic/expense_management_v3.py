# business_logic/expense_management_v3.py

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.models_v3 import Base, Expense, User  # Ensure models_v3.py is correctly imported
from datetime import date
from sqlalchemy.orm import joinedload
from database.models_v3 import Inventory

class ExpenseManager:
    def __init__(self, db_url="sqlite:///brew_and_bite_v3.db"):
        # Initialize SQLAlchemy engine and session
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)  # Create tables if they don't exist
        self.Session = sessionmaker(bind=self.engine)

    def add_expense(self, expense_date, category, supplier_id, expense_name, total_items, unit_cost):
        """Add an expense to the database."""
        if not expense_name:
            raise ValueError("Expense name cannot be empty.")
        if category not in ['Food', 'Beverages', 'Cleaning', 'Maintenance', 'Other']:
            raise ValueError(f"Invalid category: {category}")
        if total_items < 0:
            raise ValueError("Total items cannot be negative.")
        if unit_cost < 0:
            raise ValueError("Unit cost cannot be negative.")
        if supplier_id is not None:
            # Verify that the supplier exists and is of type 'supplier'
            session = self.Session()
            try:
                supplier = session.query(User).filter_by(user_id=supplier_id, registration_type="supplier").first()
                if not supplier:
                    raise ValueError(f"Supplier with ID {supplier_id} does not exist.")
            finally:
                session.close()

        session = self.Session()
        try:
            new_expense = Expense(
                expense_date=expense_date,
                category=category,
                supplier_id=supplier_id,
                expense_name=expense_name,
                total_items=total_items,
                unit_cost=unit_cost,
                total_cost=total_items * unit_cost
            )
            session.add(new_expense)

            # Update inventory ######testing this
            inventory_item = session.query(Inventory).filter_by(item_name=expense_name).first()
            if inventory_item:
                # Update quantity and optionally unit cost
                inventory_item.quantity += total_items
                inventory_item.unit_cost = unit_cost  # Update unit cost if needed
            else:
                # Create new inventory record if the item doesn't exist
                new_inventory_item = Inventory(
                    item_name=expense_name,
                    category=category,
                    quantity=total_items,
                    unit_cost=unit_cost,
                    supplier_id=supplier_id
                )
                session.add(new_inventory_item)###### testing this


            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to add expense: {e}")
        finally:
            session.close()

    def sync_expense_from_inventory(self, item_name, category, supplier_id, quantity, unit_cost): ######## testing this
        """Synchronize a new inventory item with expenses."""
        session = self.Session()
        try:
            expense = session.query(Expense).filter_by(expense_name=item_name).first()
            if not expense:
                # Add a new expense for the inventory item
                new_expense = Expense(
                    expense_date=date.today(),
                    category=category,
                    supplier_id=supplier_id,
                    expense_name=item_name,
                    total_items=quantity,
                    unit_cost=unit_cost,
                    total_cost=quantity * unit_cost
                )
                session.add(new_expense)
                session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to synchronize expense from inventory: {e}")
        finally:
            session.close()   #######testing this

    def get_all_expenses(self):
        """Retrieve all expenses from the database."""
        session = self.Session()
        try:
            # Use joinedload to eagerly load the supplier relationship
            return session.query(Expense).options(joinedload(Expense.supplier)).all()
        except Exception as e:
            raise Exception(f"Failed to retrieve expenses: {e}")
        finally:
            session.close()

    def update_expense(self, expense_id, field, new_value):
        """Update a specific field of an expense."""
        valid_fields = ['expense_date', 'category', 'supplier_id', 'expense_name', 'total_items', 'unit_cost']
        if field not in valid_fields:
            raise ValueError(f"Invalid field: {field}")

        session = self.Session()
        try:
            expense = session.query(Expense).filter_by(expense_id=expense_id).first()
            if not expense:
                raise ValueError(f"No expense found with ID {expense_id}.")

            # Handle supplier_id update
            if field == 'supplier_id':
                if new_value is not None:
                    supplier = session.query(User).filter_by(user_id=new_value, registration_type="supplier").first()
                    if not supplier:
                        raise ValueError(f"Supplier with ID {new_value} does not exist.")

            # Handle category validation
            if field == 'category':
                if new_value not in ['Food', 'Beverages', 'Cleaning', 'Maintenance', 'Other']:
                    raise ValueError(f"Invalid category: {new_value}")

            # Adjust inventory if relevant fields are updated ####### testing this
            if field == 'total_items':
                quantity_diff = new_value - expense.total_items
                inventory_item = session.query(Inventory).filter_by(item_name=expense.expense_name).first()
                if inventory_item:
                    inventory_item.quantity += quantity_diff

            if field == 'expense_name':
                inventory_item = session.query(Inventory).filter_by(item_name=expense.expense_name).first()
                if inventory_item:
                    inventory_item.item_name = new_value ####### testing this

            # Update the field
            setattr(expense, field, new_value)

            # Recalculate total_cost if total_items or unit_cost is updated
            if field in ['total_items', 'unit_cost']:
                expense.total_cost = expense.total_items * expense.unit_cost

            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to update expense: {e}")
        finally:
            session.close()

    def delete_expense(self, expense_id):
        """Delete an expense from the database."""
        session = self.Session()
        try:
            expense = session.query(Expense).filter_by(expense_id=expense_id).first()
            if not expense:
                raise ValueError(f"No expense found with ID {expense_id}.")

            # Adjust inventory ###### testing this
            inventory_item = session.query(Inventory).filter_by(item_name=expense.expense_name).first()
            if inventory_item:
                inventory_item.quantity -= expense.total_items
                if inventory_item.quantity <= 0:
                    session.delete(inventory_item)  # Remove item if quantity becomes zero or less ###### testing this

            session.delete(expense)
            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to delete expense: {e}")
        finally:
            session.close()

    def get_suppliers(self):
        """Fetch all suppliers from the database."""
        session = self.Session()
        try:
            suppliers = session.query(User).filter_by(registration_type="supplier").all()
            return suppliers
        except Exception as e:
            raise Exception(f"Failed to fetch suppliers: {e}")
        finally:
            session.close()
