import sqlite3

class DatabaseRepository:
    def __init__(self, db_name="brew_and_bite_v3.db"):
        self.db_name = db_name

    def initialize_tables(self):
        """Initialize all required database tables."""
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        # Create Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            contact INTEGER NOT NULL,
            email TEXT NOT NULL,
            registration_type TEXT NOT NULL CHECK (registration_type IN ('customer', 'admin', 'supplier')),
            role_type TEXT,
            company_name TEXT,
            company_city TEXT,
            company_phone TEXT,
            company_category TEXT CHECK (company_category IN ('Food', 'Beverages', 'Cleaning', 'Maintenance Services', 'Other'))
        );
        """)

        # Create Inventory Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Inventory (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            category TEXT CHECK (category IN ('Food', 'Tea', 'Coffee', 'Soft Drinks', 'Cleaning Products', 'Maintenance', 'Dairy Items', 'Alcoholic Drinks', 'Stationary')),
            quantity INTEGER NOT NULL CHECK (quantity >= 0),
            unit_cost REAL NOT NULL CHECK (unit_cost >= 0),
            total_cost REAL GENERATED ALWAYS AS (quantity * unit_cost) STORED,
            supplier_id INTEGER,
            FOREIGN KEY (supplier_id) REFERENCES Users(user_id) ON DELETE SET NULL
        );
        """)

        # Create Sales Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Sales (
            sales_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            quantity_sold INTEGER NOT NULL CHECK (quantity_sold > 0),
            unit_price REAL NOT NULL CHECK (unit_price > 0),
            total_cost REAL NOT NULL,
            sales_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES Inventory(item_id) ON DELETE CASCADE
        );
        """)

        # Create Expenses Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Expenses (
            expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_date TEXT NOT NULL,
            category TEXT NOT NULL,
            supplier_id INTEGER,
            expense_name TEXT NOT NULL,
            total_items INTEGER NOT NULL CHECK (total_items > 0),
            unit_cost REAL NOT NULL CHECK (unit_cost > 0),
            total_cost REAL GENERATED ALWAYS AS (total_items * unit_cost) STORED,
            FOREIGN KEY (supplier_id) REFERENCES Users(user_id) ON DELETE SET NULL
        );
        """)

        connection.commit()
        connection.close()

    # Users CRUD Operations
    def insert_user(self, data):
        """Insert a new user into the Users table."""
        self._execute_query("""
            INSERT INTO Users (username, password, contact, email, registration_type, role_type, company_name, company_city, company_phone, company_category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)

    def fetch_all_users(self):
        """Fetch all users from the Users table."""
        return self._fetch_all("SELECT * FROM Users")

    def update_user(self, user_id, field, new_value):
        """Update a user record in the Users table."""
        self._execute_query(f"UPDATE Users SET {field} = ? WHERE user_id = ?", (new_value, user_id))

    def delete_user(self, user_id):
        """Delete a user record from the Users table."""
        self._execute_query("DELETE FROM Users WHERE user_id = ?", (user_id,))

    # Inventory CRUD Operations
    def insert_inventory_item(self, data):
        """Insert a new inventory item."""
        self._execute_query("""
            INSERT INTO Inventory (item_name, category, quantity, unit_cost, supplier_id)
            VALUES (?, ?, ?, ?, ?)
        """, data)

    def fetch_inventory_items(self, category=None):
        """Fetch all inventory items, optionally filtered by category."""
        if category:
            return self._fetch_all("SELECT * FROM Inventory WHERE category = ?", (category,))
        return self._fetch_all("SELECT * FROM Inventory")

    def update_inventory_item(self, item_id, field, new_value):
        """Update an inventory item."""
        self._execute_query(f"UPDATE Inventory SET {field} = ? WHERE item_id = ?", (new_value, item_id))

    def delete_inventory_item(self, item_id):
        """Delete an inventory item."""
        self._execute_query("DELETE FROM Inventory WHERE item_id = ?", (item_id,))

    # Sales CRUD Operations
    def insert_sales_record(self, data):
        """Insert a new sales record."""
        self._execute_query("""
            INSERT INTO Sales (item_id, quantity_sold, unit_price, total_cost)
            VALUES (?, ?, ?, ?)
        """, data)

    def delete_sales_record(self, sales_id):
        """Delete a sales record."""
        self._execute_query("DELETE FROM Sales WHERE sales_id = ?", (sales_id,))

    # Expenses CRUD Operations
    def insert_expense(self, data):
        """Insert a new expense."""
        self._execute_query("""
            INSERT INTO Expenses (expense_date, category, supplier_id, expense_name, total_items, unit_cost)
            VALUES (?, ?, ?, ?, ?, ?)
        """, data)

    def fetch_all_expenses(self):
        """Fetch all expenses."""
        return self._fetch_all("""
            SELECT e.expense_id, e.expense_date, e.category, u.username AS supplier_name, e.expense_name, e.total_items,
                   e.unit_cost, e.total_cost
            FROM Expenses e
            LEFT JOIN Users u ON e.supplier_id = u.user_id
        """)

    def update_expense(self, expense_id, field, new_value):
        """Update an expense."""
        self._execute_query(f"UPDATE Expenses SET {field} = ? WHERE expense_id = ?", (new_value, expense_id))

    def delete_expense(self, expense_id):
        """Delete an expense."""
        self._execute_query("DELETE FROM Expenses WHERE expense_id = ?", (expense_id,))

    # Helper Methods
    def _execute_query(self, query, params=()):
        """Execute a query with optional parameters."""
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            connection.commit()
        except sqlite3.Error as e:
            raise Exception(f"Database Error: {e}")
        finally:
            connection.close()

    def _fetch_all(self, query, params=()):
        """Fetch all rows for a query."""
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            raise Exception(f"Database Error: {e}")
        finally:
            connection.close()
