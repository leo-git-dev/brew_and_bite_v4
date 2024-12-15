# gui/user_management_gui_v3.py

import tkinter as tk
from tkinter import ttk, messagebox
from business_logic.user_management_v3 import UserManager  # Updated import
import logging
from logging.handlers import RotatingFileHandler



class UserManagementGUI(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.user_manager = UserManager()
        self.initialize_gui()

    def initialize_gui(self):
        """Set up the main GUI layout."""
        notebook = ttk.Notebook(self)
        self.create_registration_tab(notebook)
        self.create_view_users_tab(notebook)
        self.create_update_users_tab(notebook)
        notebook.pack(expand=True, fill="both")

    # -------------------------------- Registration Tab --------------------------------
    def create_registration_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Register User")

        # Registration Type
        tk.Label(frame, text="Registration Type").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.registration_type_var = tk.StringVar()
        registration_type_menu = ttk.Combobox(frame, textvariable=self.registration_type_var, state="readonly")
        registration_type_menu['values'] = ("customer", "admin", "supplier")
        registration_type_menu.current(0)
        registration_type_menu.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.registration_type_var.trace("w", self.toggle_fields)

        # Common Fields
        self.add_common_fields(frame)

        # Role Type
        self.role_type_label = tk.Label(frame, text="Role Type")
        self.role_type_entry = ttk.Combobox(frame, values=("Barista", "Cleaning Staff", "Office Staff"), state="readonly")

        # Supplier Fields
        self.add_supplier_fields(frame)

        # Register Button
        tk.Button(frame, text="Register", command=self.handle_register).grid(row=10, column=0, columnspan=2, pady=10)

    def add_common_fields(self, frame):
        """Add common fields to the registration form."""
        tk.Label(frame, text="Username").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.username_entry = tk.Entry(frame)
        self.username_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frame, text="Password").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.password_entry = tk.Entry(frame, show="*")
        self.password_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frame, text="Contact").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.contact_entry = tk.Entry(frame)
        self.contact_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frame, text="Email").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.email_entry = tk.Entry(frame)
        self.email_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")

    def add_supplier_fields(self, frame):
        """Add supplier-specific fields to the registration form."""
        self.company_name_label = tk.Label(frame, text="Company Name")
        self.company_name_entry = tk.Entry(frame)

        self.company_city_label = tk.Label(frame, text="Company City")
        self.company_city_entry = tk.Entry(frame)

        self.company_phone_label = tk.Label(frame, text="Company Phone")
        self.company_phone_entry = tk.Entry(frame)

        self.company_category_label = tk.Label(frame, text="Company Category")
        self.company_category_var = tk.StringVar()
        self.company_category_menu = ttk.Combobox(frame, textvariable=self.company_category_var, state="readonly")
        self.company_category_menu['values'] = ("Food", "Beverages", "Cleaning", "Maintenance Services", "Other")

    # -------------------------------- View Users Tab --------------------------------
    def create_view_users_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="View All Users")

        # Users Treeview
        self.users_tree = ttk.Treeview(frame, columns=("ID", "Username", "Contact", "Email", "Type"), show="headings")
        self.users_tree.heading("ID", text="ID")
        self.users_tree.heading("Username", text="Username")
        self.users_tree.heading("Contact", text="Contact")
        self.users_tree.heading("Email", text="Email")
        self.users_tree.heading("Type", text="Type")
        self.users_tree.column("ID", width=50, anchor="center")
        self.users_tree.column("Username", width=150, anchor="center")
        self.users_tree.column("Contact", width=100, anchor="center")
        self.users_tree.column("Email", width=200, anchor="center")
        self.users_tree.column("Type", width=100, anchor="center")
        self.users_tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Refresh Button
        tk.Button(frame, text="Refresh", command=self.load_users).pack(pady=5)

    # -------------------------------- Update Users Tab --------------------------------
    def create_update_users_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Update/Delete Users")

        # Users Treeview
        self.update_tree = ttk.Treeview(frame, columns=("ID", "Username", "Contact", "Email", "Type"), show="headings")
        self.update_tree.heading("ID", text="ID")
        self.update_tree.heading("Username", text="Username")
        self.update_tree.heading("Contact", text="Contact")
        self.update_tree.heading("Email", text="Email")
        self.update_tree.heading("Type", text="Type")
        self.update_tree.column("ID", width=50, anchor="center")
        self.update_tree.column("Username", width=150, anchor="center")
        self.update_tree.column("Contact", width=100, anchor="center")
        self.update_tree.column("Email", width=200, anchor="center")
        self.update_tree.column("Type", width=100, anchor="center")
        self.update_tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Update Form
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Field to Update:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.field_var = tk.StringVar()
        field_menu = ttk.Combobox(form_frame, textvariable=self.field_var, state="readonly")
        field_menu['values'] = ("username", "password", "contact", "email", "registration_type", "role_type", "company_name", "company_city", "company_phone", "company_category")
        field_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(form_frame, text="New Value:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.new_value_entry = tk.Entry(form_frame)
        self.new_value_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Update User", command=self.update_user).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Delete User", command=self.delete_user).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Refresh", command=self.load_users_for_update).grid(row=0, column=2, padx=5)

    # -------------------------------- Common Methods --------------------------------
    def toggle_fields(self, *args):
        """Toggle fields based on registration type."""
        registration_type = self.registration_type_var.get()

        # Hide all optional fields first
        self.role_type_label.grid_remove()
        self.role_type_entry.grid_remove()
        self.company_name_label.grid_remove()
        self.company_name_entry.grid_remove()
        self.company_city_label.grid_remove()
        self.company_city_entry.grid_remove()
        self.company_phone_label.grid_remove()
        self.company_phone_entry.grid_remove()
        self.company_category_label.grid_remove()
        self.company_category_menu.grid_remove()

        # Show fields based on registration type
        if registration_type == "admin":
            self.role_type_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
            self.role_type_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")
        elif registration_type == "supplier":
            self.company_name_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
            self.company_name_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")
            self.company_city_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
            self.company_city_entry.grid(row=6, column=1, padx=10, pady=5, sticky="w")
            self.company_phone_label.grid(row=7, column=0, padx=10, pady=5, sticky="w")
            self.company_phone_entry.grid(row=7, column=1, padx=10, pady=5, sticky="w")
            self.company_category_label.grid(row=8, column=0, padx=10, pady=5, sticky="w")
            self.company_category_menu.grid(row=8, column=1, padx=10, pady=5, sticky="w")

    def load_users(self):
        """Load all users into the Treeview."""
        for row in self.users_tree.get_children():
            self.users_tree.delete(row)
        users = self.user_manager.get_all_users()
        for user in users:
            self.users_tree.insert("", "end", values=(
                user.user_id,
                user.username,
                user.contact,
                user.email,
                user.registration_type
            ))

    def load_users_for_update(self):
        """Load users into the update Treeview."""
        for row in self.update_tree.get_children():
            self.update_tree.delete(row)
        users = self.user_manager.get_all_users()
        for user in users:
            self.update_tree.insert("", "end", values=(
                user.user_id,
                user.username,
                user.contact,
                user.email,
                user.registration_type
            ))

    # -------------------------------- Action Methods --------------------------------
    def handle_register(self):
        """Handle user registration."""
        try:
            username = self.username_entry.get().strip()
            password = self.password_entry.get().strip()
            contact = self.contact_entry.get().strip()
            email = self.email_entry.get().strip()
            registration_type = self.registration_type_var.get()
            logging.debug(f"Attempting to register user with Registration Type: '{registration_type}'")

            role_type = company_name = company_city = company_phone = company_category = None

            if registration_type == "admin":
                role_type = self.role_type_entry.get().strip()
                logging.debug(f"Admin Role Type: '{role_type}'")
                if not role_type:
                    messagebox.showerror("Error", "Please select a role type for admin.")
                    logging.error("Admin registration attempted without selecting a role type.")
                    return

            if registration_type == "supplier":
                company_name = self.company_name_entry.get().strip()
                company_city = self.company_city_entry.get().strip()
                company_phone = self.company_phone_entry.get().strip()
                company_category = self.company_category_menu.get().strip()
                logging.debug(
                    f"Supplier Details: Company Name='{company_name}', City='{company_city}', Phone='{company_phone}', Category='{company_category}'")

                if not all([company_name, company_city, company_phone, company_category]):
                    messagebox.showerror("Error", "All supplier fields are required.")
                    logging.error("Supplier registration attempted without filling all required fields.")
                    return

            # Validate common fields
            if not all([username, password, contact, email]):
                messagebox.showerror("Error", "All common fields are required.")
                logging.error("Registration attempted with missing common fields.")
                return

            # Initialize UserManager
            self.user_manager.register_user(
                username=username,
                password=password,
                contact=int(contact),
                email=email,
                registration_type=registration_type,
                role_type=role_type,
                company_name=company_name,
                company_city=company_city,
                company_phone=company_phone,
                company_category=company_category
            )
            messagebox.showinfo("Success",
                                f"User '{username}' registered successfully as {registration_type.capitalize()}!")
            logging.info(f"User '{username}' registered successfully as '{registration_type}'.")
            self.load_users()
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
            logging.error(f"Input Error during registration: {ve}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to register user: {e}")
            logging.error(f"Error during registration: {e}")

    def update_user(self):
        """Update a selected user."""
        try:
            selected_items = self.update_tree.selection()
            if not selected_items:
                raise ValueError("Please select a user to update.")
            selected_item = self.update_tree.item(selected_items[0], "values")
            user_id = int(selected_item[0])
            field = self.field_var.get()
            new_value = self.new_value_entry.get().strip()
            logging.debug(f"Attempting to update User ID {user_id}: Field='{field}', New Value='{new_value}'")

            if not field or not new_value:
                raise ValueError("Both field and new value must be provided.")

            # For contact and other numeric fields, convert the new_value
            if field == "contact":
                new_value = int(new_value)
            elif field in ["user_id", "supplier_id"]:
                new_value = int(new_value)

            self.user_manager.update_user(user_id, field, new_value)
            messagebox.showinfo("Success", "User updated successfully!")
            logging.info(f"User ID {user_id} updated: Field='{field}', New Value='{new_value}'")
            self.load_users_for_update()
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
            logging.error(f"Input Error during user update: {ve}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update user: {e}")
            logging.error(f"Error during user update: {e}")

    def delete_user(self):
        """Delete a selected user."""
        try:
            selected_items = self.update_tree.selection()
            if not selected_items:
                raise ValueError("Please select a user to delete.")
            selected_item = self.update_tree.item(selected_items[0], "values")
            user_id = int(selected_item[0])
            logging.debug(f"Attempting to delete User ID {user_id}")

            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user ID {user_id}?")
            if not confirm:
                logging.info(f"Deletion cancelled for User ID {user_id}")
                return

            self.user_manager.delete_user(user_id)
            messagebox.showinfo("Success", "User deleted successfully!")
            logging.info(f"User ID {user_id} deleted successfully.")
            self.load_users_for_update()
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
            logging.error(f"Input Error during user deletion: {ve}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete user: {e}")
            logging.error(f"Error during user deletion: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = UserManagementGUI(root)
    app.pack(expand=True, fill="both")
    root.mainloop()
