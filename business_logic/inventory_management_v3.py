# business_logic/inventory_management_v3.py

from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine
from business_logic.expense_management_v3 import ExpenseManager
from database.models_v3 import Base, Inventory, User, Expense  # Updated import to models_v3

class InventoryManager:
    def __init__(self, db_url="sqlite:///brew_and_bite_v3.db"):
        # Initialize SQLAlchemy engine and session
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)  # Create tables if they don't exist
        self.Session = sessionmaker(bind=self.engine)
        self.expense_manager = ExpenseManager(db_url)

    def add_inventory_item(self, item_name, category, quantity, unit_cost, supplier_id):
        """Add an item to the inventory."""
        if not item_name:
            raise ValueError("Item name cannot be empty.")
        if category not in ['Food', 'Tea', 'Coffee', 'Soft Drinks', 'Cleaning Products', 'Maintenance', 'Dairy Items', 'Alcoholic Drinks', 'Stationary']:
            raise ValueError(f"Invalid category: {category}")
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        if unit_cost < 0:
            raise ValueError("Unit cost cannot be negative.")
        if supplier_id is None:
            raise ValueError("Supplier ID cannot be null.")

        session = self.Session()
        try:
            # Verify that the supplier exists and is of type 'supplier'
            supplier = session.query(User).filter_by(user_id=supplier_id, registration_type="supplier").first()
            if not supplier:
                raise ValueError(f"Supplier with ID {supplier_id} does not exist.")

            new_item = Inventory(
                item_name=item_name,
                category=category,
                quantity=quantity,
                unit_cost=unit_cost,
                supplier_id=supplier_id
            )
            session.add(new_item)
            session.commit()

            # Synchronize with expenses
            self.expense_manager.sync_expense_from_inventory(
                item_name=item_name,
                category=category,
                supplier_id=supplier_id,
                quantity=quantity,
                unit_cost=unit_cost
            )
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to add inventory item: {e}")
        finally:
            session.close()

    def fetch_inventory(self, category=None):
        """Fetch inventory items, optionally filtering by category."""
        session = self.Session()
        try:
            query = session.query(Inventory).options(joinedload(Inventory.supplier))
            if category:
                query = query.filter(Inventory.category == category)
            return query.all()
        except Exception as e:
            raise Exception(f"Failed to fetch inventory: {e}")
        finally:
            session.close()

    def update_inventory_item(self, item_id, field, new_value):
        """Update a specific field of an inventory item."""
        valid_fields = ["item_name", "category", "quantity", "unit_cost"]
        if field not in valid_fields:
            raise ValueError(f"Invalid field: {field}")

        session = self.Session()
        try:
            item = session.query(Inventory).filter_by(item_id=item_id).first()
            if not item:
                raise ValueError(f"Item with ID {item_id} not found.")

            # Handle specific field validations
            if field == "quantity":
                if new_value < 0:
                    raise ValueError("Quantity cannot be negative.")
            elif field == "unit_cost":
                if new_value < 0:
                    raise ValueError("Unit cost cannot be negative.")

            setattr(item, field, new_value)
            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to update inventory item: {e}")
        finally:
            session.close()

    def delete_inventory_item(self, item_id):
        """Delete an inventory item by ID."""
        session = self.Session()
        try:
            item = session.query(Inventory).filter_by(item_id=item_id).first()
            if not item:
                raise ValueError(f"Item with ID {item_id} not found.")

            session.delete(item)
            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to delete inventory item: {e}")
        finally:
            session.close()

    def fetch_all_suppliers(self):
        """Fetch all suppliers from the database."""
        session = self.Session()
        try:
            suppliers = session.query(User).filter_by(registration_type="supplier").all()
            return suppliers
        except Exception as e:
            raise Exception(f"Failed to fetch suppliers: {e}")
        finally:
            session.close()