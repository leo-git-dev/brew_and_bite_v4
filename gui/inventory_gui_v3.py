# gui/inventory_gui_v3.py

import tkinter as tk
from tkinter import ttk, messagebox
from business_logic.inventory_management_v3 import InventoryManager

class InventoryManagementGUI(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.manager = InventoryManager()
        self.initialize_gui()

    def initialize_gui(self):
        """Set up the main GUI layout."""
        notebook = ttk.Notebook(self)
        self.create_add_inventory_tab(notebook)
        self.create_view_inventory_tab(notebook)
        self.create_update_inventory_tab(notebook)
        self.create_delete_inventory_tab(notebook)
        notebook.pack(expand=True, fill="both")

    def create_add_inventory_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Add Inventory")

        # Form Fields
        tk.Label(frame, text="Item Name:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.item_name_entry = tk.Entry(frame, font=("Arial", 12))
        self.item_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frame, text="Category:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.category_var = tk.StringVar()
        category_menu = ttk.Combobox(frame, textvariable=self.category_var, state="readonly", font=("Arial", 12))
        category_menu['values'] = ('Food', 'Tea', 'Coffee', 'Soft Drinks', 'Cleaning Products', 'Maintenance', 'Dairy Items', 'Alcoholic Drinks', 'Stationary')
        category_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        category_menu.current(0)

        tk.Label(frame, text="Quantity:", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.quantity_entry = tk.Entry(frame, font=("Arial", 12))
        self.quantity_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frame, text="Unit Cost:", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.unit_cost_entry = tk.Entry(frame, font=("Arial", 12))
        self.unit_cost_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frame, text="Supplier:", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.supplier_var = tk.StringVar()
        self.supplier_menu = ttk.Combobox(frame, textvariable=self.supplier_var, state="readonly", font=("Arial", 12))
        self.supplier_menu.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        self.refresh_suppliers()

        # Buttons
        ttk.Button(frame, text="Add Item", command=self.add_inventory_item).grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Refresh Suppliers", command=self.refresh_suppliers).grid(row=6, column=0, columnspan=2, pady=5)

    def create_view_inventory_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="View Inventory")

        columns = ("ID", "Name", "Category", "Quantity", "Unit Cost", "Total Cost", "Supplier")
        self.inventory_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, anchor="center", width=100)
        self.inventory_tree.pack(expand=True, fill="both", padx=10, pady=10)

        ttk.Button(frame, text="Refresh", command=self.load_inventory).pack(pady=5)

    def create_update_inventory_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Update Inventory")

        columns = ("ID", "Name", "Category", "Quantity", "Unit Cost", "Total Cost", "Supplier")
        self.update_inventory_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.update_inventory_tree.heading(col, text=col)
            self.update_inventory_tree.column(col, anchor="center", width=100)
        self.update_inventory_tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Update Form
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Field to Update:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.update_field_var = tk.StringVar()
        field_menu = ttk.Combobox(form_frame, textvariable=self.update_field_var, state="readonly", font=("Arial", 12))
        field_menu['values'] = ("item_name", "category", "quantity", "unit_cost")
        field_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form_frame, text="New Value:", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.update_value_entry = ttk.Entry(form_frame, font=("Arial", 12))
        self.update_value_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Update Button
        ttk.Button(frame, text="Update Item", command=self.update_inventory_item).pack(pady=5)
        ttk.Button(frame, text="Refresh", command=self.load_inventory_for_update).pack(pady=5)

    def create_delete_inventory_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Delete Inventory")

        columns = ("ID", "Name", "Category", "Quantity", "Unit Cost", "Total Cost", "Supplier")
        self.delete_inventory_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.delete_inventory_tree.heading(col, text=col)
            self.delete_inventory_tree.column(col, anchor="center", width=100)
        self.delete_inventory_tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Buttons
        ttk.Button(frame, text="Delete Item", command=self.delete_inventory_item).pack(pady=5)
        ttk.Button(frame, text="Refresh", command=self.load_inventory_for_delete).pack(pady=5)

    def refresh_suppliers(self):
        """Load suppliers into the dropdown."""
        try:
            suppliers = self.manager.fetch_all_suppliers()
            supplier_names = [f"{supplier.user_id}: {supplier.username}" for supplier in suppliers]
            self.supplier_menu['values'] = supplier_names
            self.supplier_var.set("")  # Clear current selection
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load suppliers: {e}")

    def add_inventory_item(self):
        """Add a new inventory item."""
        try:
            item_name = self.item_name_entry.get().strip()
            category = self.category_var.get().strip()
            quantity = int(self.quantity_entry.get().strip())
            unit_cost = float(self.unit_cost_entry.get().strip())
            supplier_data = self.supplier_var.get().strip()

            if not supplier_data:
                raise ValueError("Please select a supplier.")

            # Extract supplier_id from the selected string
            supplier_id = int(supplier_data.split(":")[0])

            # Add inventory via InventoryManager
            self.manager.add_inventory_item(
                item_name=item_name,
                category=category,
                quantity=quantity,
                unit_cost=unit_cost,
                supplier_id=supplier_id
            )
            messagebox.showinfo("Success", "Inventory item added successfully!")
            self.clear_add_inventory_fields()
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add inventory item: {e}")

    def clear_add_inventory_fields(self):
        """Clear the fields after adding an inventory item."""
        self.item_name_entry.delete(0, tk.END)
        self.category_var.set("Food")
        self.quantity_entry.delete(0, tk.END)
        self.unit_cost_entry.delete(0, tk.END)
        self.supplier_var.set("")

    def load_inventory(self):
        """Load all inventory items into the Treeview."""
        try:
            for row in self.inventory_tree.get_children():
                self.inventory_tree.delete(row)
            items = self.manager.fetch_inventory()
            for item in items:
                supplier_name = item.supplier.username if item.supplier else "Unknown"
                total_cost = item.quantity * item.unit_cost
                self.inventory_tree.insert("", "end", values=(
                    item.item_id,
                    item.item_name,
                    item.category,
                    item.quantity,
                    f"${item.unit_cost:.2f}",
                    f"${total_cost:.2f}",
                    supplier_name
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory: {e}")

    def load_inventory_for_update(self):
        """Load inventory items into the update Treeview."""
        try:
            for row in self.update_inventory_tree.get_children():
                self.update_inventory_tree.delete(row)
            items = self.manager.fetch_inventory()
            for item in items:
                supplier_name = item.supplier.username if item.supplier else "Unknown"
                total_cost = item.quantity * item.unit_cost
                self.update_inventory_tree.insert("", "end", values=(
                    item.item_id,
                    item.item_name,
                    item.category,
                    item.quantity,
                    f"${item.unit_cost:.2f}",
                    f"${total_cost:.2f}",
                    supplier_name
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory for update: {e}")

    def update_inventory_item(self):
        """Update a selected inventory item."""
        try:
            selected_items = self.update_inventory_tree.selection()
            if not selected_items:
                raise ValueError("Please select an inventory item to update.")
            selected_item = self.update_inventory_tree.item(selected_items[0], "values")
            item_id = int(selected_item[0])
            field = self.update_field_var.get()
            new_value = self.update_value_entry.get().strip()

            if not field or not new_value:
                raise ValueError("Both field and new value must be provided.")

            # Convert new_value based on field type
            if field == "quantity":
                new_value = int(new_value)
            elif field == "unit_cost":
                new_value = float(new_value)

            self.manager.update_inventory_item(item_id, field, new_value)
            messagebox.showinfo("Success", "Inventory item updated successfully!")
            self.load_inventory_for_update()
            self.load_inventory()
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update inventory item: {e}")

    def load_inventory_for_delete(self):
        """Load inventory items into the delete Treeview."""
        try:
            for row in self.delete_inventory_tree.get_children():
                self.delete_inventory_tree.delete(row)
            items = self.manager.fetch_inventory()
            for item in items:
                supplier_name = item.supplier.username if item.supplier else "Unknown"
                total_cost = item.quantity * item.unit_cost
                self.delete_inventory_tree.insert("", "end", values=(
                    item.item_id,
                    item.item_name,
                    item.category,
                    item.quantity,
                    f"${item.unit_cost:.2f}",
                    f"${total_cost:.2f}",
                    supplier_name
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory for deletion: {e}")

    def delete_inventory_item(self):
        """Delete a selected inventory item."""
        try:
            selected_items = self.delete_inventory_tree.selection()
            if not selected_items:
                raise ValueError("Please select an inventory item to delete.")
            selected_item = self.delete_inventory_tree.item(selected_items[0], "values")
            item_id = int(selected_item[0])

            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete item ID {item_id}?")
            if not confirm:
                return

            self.manager.delete_inventory_item(item_id)
            messagebox.showinfo("Success", "Inventory item deleted successfully!")
            self.load_inventory_for_delete()
            self.load_inventory()
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete inventory item: {e}")
