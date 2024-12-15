# business_logic/sales_management_v3.py

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.models_v3 import Base, Sales, Inventory  # Updated import to models_v3
from database.setup_v3 import DatabaseRepository


class SalesManager:
    def __init__(self, db_url="sqlite:///brew_and_bite_v3.db"):
        # Initialize SQLAlchemy engine and session
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)  # Create tables if they don't exist
        self.Session = sessionmaker(bind=self.engine)
        self.repo = DatabaseRepository()


    def register_sales(self, sales_data):
        """Register multiple sales records and update inventory quantities."""
        session = self.Session()
        try:
            for sale in sales_data:
                item_id = sale['item_id']
                quantity_sold = sale['quantity']
                unit_price = sale['unit_price']
                total_cost = quantity_sold * unit_price

                if quantity_sold <= 0 or unit_price <= 0:
                    raise ValueError("Quantity and unit price must be positive numbers.")

                # Check inventory availability
                inventory_item = session.query(Inventory).filter_by(item_id=item_id).first()
                if not inventory_item or inventory_item.quantity < quantity_sold:
                    raise ValueError(f"Insufficient stock for item ID {item_id}.")

                # Deduct inventory quantity
                inventory_item.quantity -= quantity_sold

                # Add sales record
                new_sale = Sales(
                    item_id=item_id,
                    quantity_sold=quantity_sold,
                    unit_price=unit_price,
                    total_cost=total_cost
                )
                session.add(new_sale)

            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(f"Error registering sales: {e}")
        finally:
            session.close()

    def fetch_inventory_items(self):
        """Fetch all inventory items."""
        try:
            items = self.repo.fetch_inventory_items()  # Assuming this fetches ORM objects or raw rows
            # Convert raw database rows or objects into a list of dictionaries
            return [
                {"item_id": item[0], "item_name": item[1]}  # Adjust indices as per table schema
                for item in items
            ]
        except Exception as e:
            raise Exception(f"Error fetching inventory items: {e}")

    def fetch_sales_records(self):
        """Fetch all sales records with joined inventory details."""
        session = self.Session()
        try:
            records = session.query(
                Sales.sales_id,
                Inventory.item_name,
                Sales.quantity_sold,
                Sales.unit_price,
                Sales.total_cost,
                Sales.sales_date
            ).join(Inventory, Sales.item_id == Inventory.item_id).all()
            return records
        finally:
            session.close()

    def delete_sales_record(self, sales_id):
        """Delete a specific sales record."""
        session = self.Session()
        try:
            sales_record = session.query(Sales).filter_by(sales_id=sales_id).first()
            if not sales_record:
                raise ValueError(f"No sales record found with Sales ID {sales_id}.")
            session.delete(sales_record)
            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(f"Error deleting sales record: {e}")
        finally:
            session.close()

    def update_sales_record(self, sales_id, field, new_value):
        """Update a specific field in a sales record."""
        session = self.Session()
        valid_fields = ["quantity_sold", "unit_price"]
        if field not in valid_fields:
            raise ValueError(f"Invalid field: {field}")

        try:
            sales_record = session.query(Sales).filter_by(sales_id=sales_id).first()
            if not sales_record:
                raise ValueError(f"No sales record found with Sales ID {sales_id}.")

            setattr(sales_record, field, new_value)

            # Recalculate total cost if necessary
            if field in ["quantity_sold", "unit_price"]:
                sales_record.total_cost = sales_record.quantity_sold * sales_record.unit_price

            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(f"Error updating sales record: {e}")
        finally:
            session.close()
