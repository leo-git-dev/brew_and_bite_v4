# database/models_v3.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'  # Lowercase table name for consistency

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=False)  # Increased length for hashed passwords
    contact = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    registration_type = Column(String(20), nullable=False)  # 'customer', 'supplier', 'admin'
    role_type = Column(String(50), nullable=True)  # Only for admins
    company_name = Column(String(100), nullable=True)  # Only for suppliers
    company_city = Column(String(50), nullable=True)  # Only for suppliers
    company_phone = Column(String(20), nullable=True)  # Only for suppliers
    company_category = Column(String(50), nullable=True)  # Only for suppliers

    def __repr__(self):
        return f"<User(username='{self.username}', registration_type='{self.registration_type}')>"

    # Relationships
    expenses = relationship("Expense", back_populates="supplier", cascade="all, delete-orphan")
    inventory_items = relationship("Inventory", back_populates="supplier", cascade="all, delete-orphan")

    # Check constraints for better validation
    __table_args__ = (
        CheckConstraint("registration_type IN ('customer', 'supplier', 'admin')", name="check_registration_type"),
        CheckConstraint("company_category IN ('Food', 'Beverages', 'Cleaning', 'Maintenance Services', 'Other')",
                        name="check_company_category"),
    )


class Inventory(Base):
    __tablename__ = 'inventory'  # Lowercase table name for consistency

    item_id = Column(Integer, primary_key=True, autoincrement=True)
    item_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Float, nullable=False)
    supplier_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)

    # Relationships
    sales = relationship("Sales", back_populates="item")
    supplier = relationship("User", back_populates="inventory_items")


class Sales(Base):
    __tablename__ = 'sales'  # Lowercase table name for consistency

    sales_id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey('inventory.item_id'), nullable=False)
    quantity_sold = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)  # Calculated as quantity_sold * unit_price
    sales_date = Column(DateTime, default=func.now(), nullable=False)  # Now properly using func
    total_cost = Column(Float, nullable=False)  # Ensure this exists

    # Relationship with Inventory
    item = relationship("Inventory", back_populates="sales")


class Expense(Base):
    __tablename__ = 'expenses'  # Lowercase table name for consistency

    expense_id = Column(Integer, primary_key=True, autoincrement=True)
    expense_date = Column(DateTime, nullable=False)
    category = Column(String, nullable=False)
    supplier_id = Column(Integer, ForeignKey('users.user_id'), nullable=True)
    expense_name = Column(String, nullable=False)
    total_items = Column(Integer, nullable=False)
    unit_cost = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)  # Calculated as total_items * unit_cost

    # Relationships
    supplier = relationship("User", back_populates="expenses")
