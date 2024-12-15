# main.py

import tkinter as tk
from tkinter import ttk, messagebox
from gui.user_management_gui_v3 import UserManagementGUI
from gui.expense_manager_gui_v3 import ExpenseManagerGUI
from gui.inventory_gui_v3 import InventoryManagementGUI
from gui.report_manager_gui_v3 import FinancialReportGUI
from gui.sales_manager_gui_v3 import SalesManagerGUI
from business_logic.user_management_v3 import UserManager
from database.setup_v3 import DatabaseRepository
import logging

# Super Admin Credentials
SUPER_ADMIN_USERNAME = "admin"
SUPER_ADMIN_PASSWORD = "password"


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Brew and Bite Cafe")
        self.geometry("800x600")
        self.user_role = None
        self.registration_type = None
        self.user_manager = UserManager()  # Initialize UserManager
        self.repo = DatabaseRepository()  # Initialize Database Repository
        self.repo.initialize_tables()  # Ensure tables exist
        self.initialize_login_screen()

    def initialize_login_screen(self):
        """Display the login/registration screen."""
        for widget in self.winfo_children():
            widget.destroy()

        # Welcome Screen
        tk.Label(self, text="Welcome to Brew and Bite Cafe", font=("Arial", 16)).pack(pady=20)
        tk.Label(self, text="Please choose your registration type:", font=("Arial", 12)).pack(pady=10)

        self.registration_type_var = tk.StringVar()
        registration_menu = ttk.Combobox(self, textvariable=self.registration_type_var)
        registration_menu['values'] = ("customer", "supplier", "admin")
        registration_menu.pack(pady=5)

        tk.Button(self, text="Register", command=self.handle_registration).pack(pady=5)
        tk.Button(self, text="Login", command=self.initialize_login_form).pack(pady=5)

    def handle_registration(self):
        """Redirect to the user management registration tab."""
        registration_type = self.registration_type_var.get()
        if registration_type not in ["customer", "supplier", "admin"]:
            messagebox.showerror("Error", "Please select a valid registration type.")
            return

        self.registration_type = registration_type
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text=f"Registration for {registration_type.capitalize()}", font=("Arial", 14)).pack(pady=20)

        # Create registration form
        frame = ttk.Frame(self)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        self.create_registration_form(frame)

        # Back Button to Return to Login/Registration Screen
        tk.Button(self, text="Back", command=self.initialize_login_screen).pack(pady=20)

    def create_registration_form(self, parent):
        """Create registration form based on the selected registration type."""
        tk.Label(parent, text="Username").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.username_entry = tk.Entry(parent)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(parent, text="Password").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.password_entry = tk.Entry(parent, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(parent, text="Contact").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.contact_entry = tk.Entry(parent)
        self.contact_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(parent, text="Email").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.email_entry = tk.Entry(parent)
        self.email_entry.grid(row=3, column=1, padx=5, pady=5)

        # Admin-specific field
        self.role_type_label = tk.Label(parent, text="Role Type")
        self.role_type_entry = ttk.Combobox(parent, values=("Barista", "Cleaning Staff", "Office Staff"))

        if self.registration_type == "admin":
            self.role_type_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)
            self.role_type_entry.grid(row=4, column=1, padx=5, pady=5)

        # Supplier-specific fields
        self.company_name_label = tk.Label(parent, text="Company Name")
        self.company_name_entry = tk.Entry(parent)
        self.company_city_label = tk.Label(parent, text="Company City")
        self.company_city_entry = tk.Entry(parent)
        self.company_phone_label = tk.Label(parent, text="Company Phone")
        self.company_phone_entry = tk.Entry(parent)
        self.company_category_label = tk.Label(parent, text="Company Category")
        self.company_category_var = tk.StringVar()
        self.company_category_menu = ttk.Combobox(parent, textvariable=self.company_category_var)
        self.company_category_menu['values'] = ("Food", "Beverages", "Cleaning", "Maintenance Services", "Other")

        if self.registration_type == "supplier":
            self.company_name_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)
            self.company_name_entry.grid(row=4, column=1, padx=5, pady=5)
            self.company_city_label.grid(row=5, column=0, sticky="w", padx=5, pady=5)
            self.company_city_entry.grid(row=5, column=1, padx=5, pady=5)
            self.company_phone_label.grid(row=6, column=0, sticky="w", padx=5, pady=5)
            self.company_phone_entry.grid(row=6, column=1, padx=5, pady=5)
            self.company_category_label.grid(row=7, column=0, sticky="w", padx=5, pady=5)
            self.company_category_menu.grid(row=7, column=1, padx=5, pady=5)

        # Register Button
        tk.Button(parent, text="Register", command=self.handle_register).grid(row=8, column=0, columnspan=2, pady=10)

    def handle_register(self):
        """Handle the registration process."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        contact = self.contact_entry.get()
        email = self.email_entry.get()

        role_type, company_name, company_city, company_phone, company_category = None, None, None, None, None

        if self.registration_type == "admin":
            role_type = self.role_type_entry.get()
            if not role_type:
                messagebox.showerror("Error", "Please select a role type for admin!")
                return

        if self.registration_type == "supplier":
            company_name = self.company_name_entry.get()
            company_city = self.company_city_entry.get()
            company_phone = self.company_phone_entry.get()
            company_category = self.company_category_var.get()
            if not (company_name and company_city and company_phone and company_category):
                messagebox.showerror("Error", "All supplier fields are required!")
                return

        # Validate common fields
        if not username or not password or not contact or not email:
            messagebox.showerror("Error", "All common fields are required!")
            return

        try:
            success, message = self.user_manager.register_user(
                username=username,
                password=password,
                contact=int(contact),
                email=email,
                registration_type=self.registration_type,
                role_type=role_type,
                company_name=company_name,
                company_city=company_city,
                company_phone=company_phone,
                company_category=company_category
            )
            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {e}")
            return

        self.initialize_login_screen()

    def initialize_login_form(self):
        """Display the login form."""
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text="Login", font=("Arial", 16)).pack(pady=20)
        tk.Label(self, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self, text="Login", command=self.handle_login).pack(pady=10)

    def handle_login(self):
        """Handle the login logic."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Super Admin Login
        if username == SUPER_ADMIN_USERNAME and password == SUPER_ADMIN_PASSWORD:
            self.user_role = "super_admin"
            self.initialize_main_screen()
            return

        # Authenticate user from the database
        try:
            success, user_data = self.user_manager.authenticate_user(username, password)
            if success:
                self.user_role = user_data.get("role_type")  # Extract role type
                self.initialize_main_screen()
            else:
                messagebox.showerror("Error", user_data)  # user_data contains error message
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {e}")

    def initialize_main_screen(self):
        """Initialize the main application screen."""
        for widget in self.winfo_children():
            widget.destroy()

        if self.user_role in ["customer", "supplier"]:
            # Restrict customer and supplier access
            messagebox.showerror("Access Denied", "You do not have access to this system.")
            self.initialize_login_screen()
            return

        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        # Super Admin Access
        if self.user_role == "super_admin":
            notebook.add(UserManagementGUI(notebook), text="User Management")
            notebook.add(ExpenseManagerGUI(notebook), text="Expense Management")
            notebook.add(InventoryManagementGUI(notebook), text="Inventory Management")
            notebook.add(SalesManagerGUI(notebook), text="Sales Management")
            notebook.add(FinancialReportGUI(notebook), text="Financial Reports")

        # Office Staff Access
        elif self.user_role == "Office Staff":
            notebook.add(UserManagementGUI(notebook), text="User Management")
            notebook.add(ExpenseManagerGUI(notebook), text="Expense Management")
            notebook.add(InventoryManagementGUI(notebook), text="Inventory Management")
            notebook.add(SalesManagerGUI(notebook), text="Sales Management")
            notebook.add(FinancialReportGUI(notebook), text="Financial Reports")

        # Barista Access
        elif self.user_role == "Barista":
            notebook.add(InventoryManagementGUI(notebook), text="Inventory Management")
            notebook.add(SalesManagerGUI(notebook), text="Sales Management")
            notebook.add(UserManagementGUI(notebook),
                         text="Customer Management")  # Use "User Management" for customer tab

        # Logout Tab
        logout_frame = ttk.Frame(notebook)
        notebook.add(logout_frame, text="Logout")
        ttk.Button(
            logout_frame,
            text="Logout",
            command=self.logout,
        ).pack(pady=50)

    def logout(self):
        """Handle user logout."""
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?")
        if confirm:
            self.user_role = None
            self.initialize_login_screen()


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
