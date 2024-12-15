# gui/expense_manager_gui_v3.py

import tkinter as tk
from tkinter import ttk, messagebox
from business_logic.expense_management_v3 import ExpenseManager
from tkcalendar import DateEntry  # Ensure tkcalendar is installed
from datetime import datetime


class ExpenseManagerGUI(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.manager = ExpenseManager()
        self.initialize_gui()

    def initialize_gui(self):
        """Set up the main GUI layout."""
        notebook = ttk.Notebook(self)
        self.create_add_expense_tab(notebook)
        self.create_view_expenses_tab(notebook)
        self.create_update_expense_tab(notebook)
        self.create_delete_expense_tab(notebook)
        notebook.pack(expand=True, fill="both")

    # -------------------------------- Add Expense Tab --------------------------------
    def create_add_expense_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Add Expense")

        # Form Fields
        tk.Label(frame, text="Expense Date:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.expense_date_entry = DateEntry(frame, date_pattern='yyyy-mm-dd', font=("Arial", 12))
        self.expense_date_entry.set_date(datetime.now().date())
        self.expense_date_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frame, text="Category:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.category_var = tk.StringVar()
        category_menu = ttk.Combobox(frame, textvariable=self.category_var, state="readonly", font=("Arial", 12))
        category_menu['values'] = ("Food", "Beverages", "Cleaning", "Maintenance", "Other")
        category_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        category_menu.current(0)

        tk.Label(frame, text="Supplier:", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.supplier_var = tk.StringVar()
        self.supplier_menu = ttk.Combobox(frame, textvariable=self.supplier_var, state="readonly", font=("Arial", 12))
        self.supplier_menu.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self.refresh_suppliers()

        tk.Label(frame, text="Expense Name:", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.expense_name_entry = tk.Entry(frame, font=("Arial", 12))
        self.expense_name_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frame, text="Total Items:", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.total_items_entry = tk.Entry(frame, font=("Arial", 12))
        self.total_items_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frame, text="Unit Cost:", font=("Arial", 12)).grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.unit_cost_entry = tk.Entry(frame, font=("Arial", 12))
        self.unit_cost_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frame, text="Total Cost:", font=("Arial", 12)).grid(row=6, column=0, padx=10, pady=5, sticky="e")
        self.total_cost_var = tk.StringVar(value="0.00")
        tk.Label(frame, textvariable=self.total_cost_var, font=("Arial", 12)).grid(row=6, column=1, padx=10, pady=5, sticky="w")

        # Buttons
        ttk.Button(frame, text="Add Expense", command=self.add_expense).grid(row=7, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Refresh Suppliers", command=self.refresh_suppliers).grid(row=8, column=0, columnspan=2, pady=5)

    def add_expense(self):
        """Add a new expense."""
        try:
            expense_date = self.expense_date_entry.get_date()
            category = self.category_var.get()
            supplier_data = self.supplier_var.get()
            expense_name = self.expense_name_entry.get().strip()
            total_items = int(self.total_items_entry.get().strip())
            unit_cost = float(self.unit_cost_entry.get().strip())

            if ":" not in supplier_data:
                raise ValueError("Please select a valid supplier.")

            supplier_id = int(supplier_data.split(":")[0])

            # Validate total_items
            total_items = int(self.total_items_entry.get().strip())
            if total_items <= 0:
                raise ValueError("Total items must be a positive integer.")

            # Validate unit_cost
            unit_cost = float(self.unit_cost_entry.get().strip())
            if unit_cost <= 0:
                raise ValueError("Unit cost must be a positive number.")

            # Calculate total cost
            total_cost = total_items * unit_cost
            self.total_cost_var.set(f"{total_cost:.2f}")

            # Add expense via ExpenseManager
            self.manager.add_expense(
                expense_date=expense_date,
                category=category,
                supplier_id=supplier_id,
                expense_name=expense_name,
                total_items=total_items,
                unit_cost=unit_cost
            )

            # Locate InventoryManagementGUI and refresh inventory
            for tab in self.master.winfo_children():
                if isinstance(tab, ttk.Notebook):
                    for child in tab.winfo_children():
                        if isinstance(child, InventoryManagementGUI):
                            child.load_inventory()
                            break

            messagebox.showinfo("Success", "Expense added successfully!")
            self.clear_add_expense_fields()
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add expense: {e}")

    def clear_add_expense_fields(self):
        """Clear the fields after adding an expense."""
        self.expense_date_entry.set_date(datetime.now().date())
        self.category_var.set("Food")
        self.supplier_var.set("")
        self.expense_name_entry.delete(0, tk.END)
        self.total_items_entry.delete(0, tk.END)
        self.unit_cost_entry.delete(0, tk.END)
        self.total_cost_var.set("0.00")

    def refresh_suppliers(self):
        """Load suppliers into the dropdown."""
        try:
            suppliers = self.manager.get_suppliers()
            supplier_names = [f"{supplier.user_id}: {supplier.username}" for supplier in suppliers]
            self.supplier_menu['values'] = supplier_names
            self.supplier_var.set("")  # Clear current selection
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load suppliers: {e}")

    # -------------------------------- View Expenses Tab --------------------------------
    def create_view_expenses_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="View Expenses")

        columns = ("ID", "Date", "Category", "Supplier", "Expense Name", "Total Items", "Unit Cost", "Total Cost")
        self.expenses_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.expenses_tree.heading(col, text=col)
            self.expenses_tree.column(col, anchor="center", width=100)
        self.expenses_tree.pack(expand=True, fill="both", padx=10, pady=10)

        ttk.Button(frame, text="Refresh", command=self.load_expenses).pack(pady=5)

    def load_expenses(self):
        """Load all expenses into the Treeview."""
        try:
            for row in self.expenses_tree.get_children():
                self.expenses_tree.delete(row)
            expenses = self.manager.get_all_expenses()
            for expense in expenses:
                supplier_name = expense.supplier.username if expense.supplier else "N/A"
                self.expenses_tree.insert("", "end", values=(
                    expense.expense_id,
                    expense.expense_date.strftime("%Y-%m-%d"),
                    expense.category,
                    supplier_name,
                    expense.expense_name,
                    expense.total_items,
                    f"${expense.unit_cost:.2f}",
                    f"${expense.total_cost:.2f}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load expenses: {e}")

    # -------------------------------- Update Expense Tab --------------------------------
    def create_update_expense_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Update Expense")

        columns = ("ID", "Date", "Category", "Supplier", "Expense Name", "Total Items", "Unit Cost", "Total Cost")
        self.update_expenses_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.update_expenses_tree.heading(col, text=col)
            self.update_expenses_tree.column(col, anchor="center", width=100)
        self.update_expenses_tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Update Form
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Field to Update:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.update_field_var = tk.StringVar()
        field_menu = ttk.Combobox(form_frame, textvariable=self.update_field_var, state="readonly", font=("Arial", 12))
        field_menu['values'] = ("category", "supplier_id", "expense_name", "total_items", "unit_cost")
        field_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form_frame, text="New Value:", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.update_value_entry = ttk.Entry(form_frame, font=("Arial", 12))
        self.update_value_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Update Button
        ttk.Button(frame, text="Update Expense", command=self.update_expense).pack(pady=5)
        ttk.Button(frame, text="Refresh", command=self.load_expenses_for_update).pack(pady=5)

    def load_expenses_for_update(self):
        """Load expenses into the Treeview for updating."""
        try:
            for row in self.update_expenses_tree.get_children():
                self.update_expenses_tree.delete(row)
            expenses = self.manager.get_all_expenses()
            for expense in expenses:
                supplier_name = expense.supplier.username if expense.supplier else "N/A"
                self.update_expenses_tree.insert("", "end", values=(
                    expense.expense_id,
                    expense.expense_date.strftime("%Y-%m-%d"),
                    expense.category,
                    supplier_name,
                    expense.expense_name,
                    expense.total_items,
                    f"${expense.unit_cost:.2f}",
                    f"${expense.total_cost:.2f}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load expenses for update: {e}")

    def update_expense(self):
        """Update a selected expense."""
        try:
            selected_items = self.update_expenses_tree.selection()
            if not selected_items:
                raise ValueError("Please select an expense to update.")
            selected_item = self.update_expenses_tree.item(selected_items[0], "values")
            expense_id = int(selected_item[0])
            field = self.update_field_var.get()
            new_value = self.update_value_entry.get().strip()

            if not field or not new_value:
                raise ValueError("Both field and new value must be provided.")

            # Convert new_value based on field type
            if field == "supplier_id":
                new_value = int(new_value)
            elif field == "total_items":
                new_value = int(new_value)
            elif field == "unit_cost":
                new_value = float(new_value)

            self.manager.update_expense(expense_id, field, new_value)
            messagebox.showinfo("Success", "Expense updated successfully!")
            self.load_expenses_for_update()
            self.load_expenses()
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update expense: {e}")

    # -------------------------------- Delete Expense Tab --------------------------------
    def create_delete_expense_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Delete Expense")

        columns = ("ID", "Date", "Category", "Supplier", "Expense Name", "Total Items", "Unit Cost", "Total Cost")
        self.delete_expenses_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.delete_expenses_tree.heading(col, text=col)
            self.delete_expenses_tree.column(col, anchor="center", width=100)
        self.delete_expenses_tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Buttons
        ttk.Button(frame, text="Delete Expense", command=self.delete_expense).pack(pady=5)
        ttk.Button(frame, text="Refresh", command=self.load_expenses_for_delete).pack(pady=5)

    def load_expenses_for_delete(self):
        """Load expenses into the Treeview for deletion."""
        try:
            for row in self.delete_expenses_tree.get_children():
                self.delete_expenses_tree.delete(row)
            expenses = self.manager.get_all_expenses()
            for expense in expenses:
                supplier_name = expense.supplier.username if expense.supplier else "N/A"
                self.delete_expenses_tree.insert("", "end", values=(
                    expense.expense_id,
                    expense.expense_date.strftime("%Y-%m-%d"),
                    expense.category,
                    supplier_name,
                    expense.expense_name,
                    expense.total_items,
                    f"${expense.unit_cost:.2f}",
                    f"${expense.total_cost:.2f}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load expenses for deletion: {e}")

    def delete_expense(self):
        """Delete a selected expense."""
        try:
            selected_items = self.delete_expenses_tree.selection()
            if not selected_items:
                raise ValueError("Please select an expense to delete.")
            selected_item = self.delete_expenses_tree.item(selected_items[0], "values")
            expense_id = int(selected_item[0])

            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete expense ID {expense_id}?")
            if not confirm:
                return

            self.manager.delete_expense(expense_id)
            messagebox.showinfo("Success", "Expense deleted successfully!")
            self.load_expenses_for_delete()
            self.load_expenses()
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete expense: {e}")
