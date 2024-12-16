import tkinter as tk
from tkinter import ttk, messagebox
from business_logic.sales_management_v3 import SalesManager


class SalesManagerGUI(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.manager = SalesManager()
        self.sales_data = []  # Holds multiple sales items
        self.initialize_gui()

    def initialize_gui(self):
        """Set up the main GUI layout."""
        notebook = ttk.Notebook(self)
        self.create_entry_sales_tab(notebook)
        self.create_view_all_sales_tab(notebook)
        self.create_update_sales_tab(notebook)
        self.create_delete_sales_tab(notebook)
        notebook.pack(expand=True, fill="both")

    # -------------------------------- Entry Sales Tab --------------------------------
    def create_entry_sales_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Enter Sales")

        # Form Fields
        tk.Label(frame, text="Item Name", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.item_var = tk.StringVar()
        self.item_menu = ttk.Combobox(frame, textvariable=self.item_var, state="readonly", font=("Arial", 12), width=30)
        self.item_menu.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.refresh_items()

        tk.Label(frame, text="Quantity", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.quantity_entry = tk.Entry(frame, font=("Arial", 12))
        self.quantity_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frame, text="Unit Price", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.unit_price_entry = tk.Entry(frame, font=("Arial", 12))
        self.unit_price_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frame, text="Total Cost", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.total_cost_var = tk.StringVar(value="0.00")
        tk.Label(frame, textvariable=self.total_cost_var, font=("Arial", 12)).grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Buttons
        tk.Button(frame, text="Add to Sale", command=self.add_to_sale).grid(row=4, column=0, columnspan=2, pady=10)
        self.register_button = tk.Button(frame, text="Register Sale", command=self.register_sale, state="disabled")
        self.register_button.grid(row=5, column=0, columnspan=2, pady=5)

        # Refresh Button for Inventory
        tk.Button(frame, text="Refresh Items", command=self.refresh_items).grid(row=5, column=2, padx=10, pady=5)

        # Treeview for displaying registered items
        columns = ("Item Name", "Quantity", "Unit Price", "Total Cost")
        self.sales_tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, anchor="center", width=150)
        self.sales_tree.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

    def refresh_items(self):
        """Load inventory items into the dropdown."""
        try:
            items = self.manager.fetch_inventory_items()
            item_names = [f"{item['item_name']} (ID: {item['item_id']})" for item in items]
            self.item_var.set("")
            self.item_menu['values'] = item_names
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory items: {e}")

    def add_to_sale(self):
        """Add an item to the current sale."""
        try:
            item = self.item_var.get()
            if not item:
                raise ValueError("Select an item.")

            item_id = int(item.split("(ID: ")[1].strip(")"))
            quantity = int(self.quantity_entry.get())
            unit_price = float(self.unit_price_entry.get())
            total_cost = quantity * unit_price

            if quantity <= 0 or unit_price <= 0:
                raise ValueError("Quantity and unit price must be positive numbers.")

            self.sales_data.append({
                "item_id": item_id,
                "item_name": item.split(" (ID:")[0],
                "quantity": quantity,
                "unit_price": unit_price,
                "total_cost": total_cost
            })

            self.sales_tree.insert("", "end", values=(item.split(" (ID:")[0], quantity, f"${unit_price:.2f}", f"${total_cost:.2f}"))

            current_total = float(self.total_cost_var.get())
            updated_total = current_total + total_cost
            self.total_cost_var.set(f"{updated_total:.2f}")
            self.register_button.config(state="normal")

            self.item_menu.set("")
            self.quantity_entry.delete(0, tk.END)
            self.unit_price_entry.delete(0, tk.END)

        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add to sale: {e}")

    def register_sale(self):
        """Register all sales items."""
        try:
            if not self.sales_data:
                raise ValueError("No items in the sales list.")

            self.manager.register_sales(self.sales_data)
            messagebox.showinfo("Success", "Sales registered successfully!")

            self.sales_data.clear()
            for row in self.sales_tree.get_children():
                self.sales_tree.delete(row)

            self.total_cost_var.set("0.00")
            self.register_button.config(state="disabled")
            self.refresh_items()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to register sales: {e}")

    # -------------------------------- View All Sales Tab --------------------------------
    def create_view_all_sales_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="View All Sales")

        columns = ("Sales ID", "Item Name", "Quantity", "Unit Price", "Total Cost", "Sales Date")
        self.view_sales_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.view_sales_tree.heading(col, text=col)
            self.view_sales_tree.column(col, anchor='center')
        self.view_sales_tree.pack(expand=True, fill="both", padx=10, pady=10)

        tk.Button(frame, text="Refresh", command=self.load_sales).pack(pady=5)

    def load_sales(self):
        """Load all sales records into the Treeview."""
        try:
            for row in self.view_sales_tree.get_children():
                self.view_sales_tree.delete(row)
            records = self.manager.fetch_sales_records()
            for record in records:
                self.view_sales_tree.insert("", "end", values=(
                    record.sales_id,
                    record.item_name,
                    record.quantity_sold,
                    f"${record.unit_price:.2f}",
                    f"${record.total_cost:.2f}",
                    record.sales_date.strftime("%Y-%m-%d %H:%M:%S")
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sales records: {e}")

    # -------------------------------- Update Sales Tab --------------------------------
    def create_update_sales_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Update Sales")

        columns = ("Sales ID", "Item Name", "Quantity", "Unit Price", "Total Cost", "Sales Date")
        self.update_sales_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.update_sales_tree.heading(col, text=col)
            self.update_sales_tree.column(col, anchor='center')
        self.update_sales_tree.pack(expand=True, fill="both", padx=10, pady=10)

        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Field to Update:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.update_field_var = tk.StringVar()
        field_menu = ttk.Combobox(form_frame, textvariable=self.update_field_var, state="readonly")
        field_menu['values'] = ("quantity_sold", "unit_price")
        field_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(form_frame, text="New Value:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.update_value_entry = tk.Entry(form_frame)
        self.update_value_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Update Sale", command=self.update_sales_record).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Refresh", command=self.load_sales_for_update).grid(row=0, column=1, padx=5)

    def load_sales_for_update(self):
        """Load sales records into the update Treeview."""
        try:
            for row in self.update_sales_tree.get_children():
                self.update_sales_tree.delete(row)
            records = self.manager.fetch_sales_records()
            for record in records:
                self.update_sales_tree.insert("", "end", values=(
                    record.sales_id,
                    record.item_name,
                    record.quantity_sold,
                    f"${record.unit_price:.2f}",
                    f"${record.total_cost:.2f}",
                    record.sales_date.strftime("%Y-%m-%d %H:%M:%S")
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sales records for update: {e}")

    def update_sales_record(self):
        """Update a selected sales record."""
        try:
            selected_items = self.update_sales_tree.selection()
            if not selected_items:
                raise ValueError("Please select a sales record to update.")
            selected_item = self.update_sales_tree.item(selected_items[0], "values")
            sales_id = int(selected_item[0])
            field = self.update_field_var.get().strip()
            new_value = self.update_value_entry.get().strip()

            if not field or not new_value:
                raise ValueError("Both field and new value must be provided.")

            if field == "quantity_sold":
                new_value = int(new_value)
            elif field == "unit_price":
                new_value = float(new_value)

            self.manager.update_sales_record(sales_id, field, new_value)
            messagebox.showinfo("Success", "Sales record updated successfully!")
            self.load_sales_for_update()
            self.load_sales()

        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update sales record: {e}")

    # -------------------------------- Delete Sales Tab --------------------------------
    def create_delete_sales_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Delete Sales")

        columns = ("Sales ID", "Item Name", "Quantity", "Unit Price", "Total Cost", "Sales Date")
        self.delete_sales_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.delete_sales_tree.heading(col, text=col)
            self.delete_sales_tree.column(col, anchor='center')
        self.delete_sales_tree.pack(expand=True, fill="both", padx=10, pady=10)

        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Delete Sale", command=self.delete_sales_record).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Refresh", command=self.load_sales_for_delete).grid(row=0, column=1, padx=5)

    def load_sales_for_delete(self):
        """Load sales records into the delete Treeview."""
        try:
            for row in self.delete_sales_tree.get_children():
                self.delete_sales_tree.delete(row)
            records = self.manager.fetch_sales_records()
            for record in records:
                self.delete_sales_tree.insert("", "end", values=(
                    record.sales_id,
                    record.item_name,
                    record.quantity_sold,
                    f"${record.unit_price:.2f}",
                    f"${record.total_cost:.2f}",
                    record.sales_date.strftime("%Y-%m-%d %H:%M:%S")
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sales records for deletion: {e}")

    def delete_sales_record(self):
        """Delete a selected sales record."""
        try:
            selected_items = self.delete_sales_tree.selection()
            if not selected_items:
                raise ValueError("Please select a sales record to delete.")
            selected_item = self.delete_sales_tree.item(selected_items[0], "values")
            sales_id = int(selected_item[0])

            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete sales ID {sales_id}?")
            if not confirm:
                return

            self.manager.delete_sales_record(sales_id)
            messagebox.showinfo("Success", "Sales record deleted successfully!")
            self.load_sales_for_delete()
            self.load_sales()
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete sales record: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SalesManagerGUI(root)
    app.pack(expand=True, fill="both")
    root.mainloop()


'''import tkinter as tk
from tkinter import ttk, messagebox
from business_logic.sales_management_v3 import SalesManager


class SalesManagerGUI(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.manager = SalesManager()
        self.sales_data = []  # Holds multiple sales items
        self.initialize_gui()

    def initialize_gui(self):
        """Set up the main GUI layout."""
        notebook = ttk.Notebook(self)
        self.create_entry_sales_tab(notebook)
        self.create_view_all_sales_tab(notebook)
        self.create_update_sales_tab(notebook)
        self.create_delete_sales_tab(notebook)
        notebook.pack(expand=True, fill="both")

    # -------------------------------- Entry Sales Tab --------------------------------
    def create_entry_sales_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Enter Sales")

        # Form Fields
        tk.Label(frame, text="Item Name", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.item_var = tk.StringVar()
        self.item_menu = ttk.Combobox(frame, textvariable=self.item_var, state="readonly", font=("Arial", 12), width=30)
        self.item_menu.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.refresh_items()

        tk.Label(frame, text="Quantity", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.quantity_entry = tk.Entry(frame, font=("Arial", 12))
        self.quantity_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frame, text="Unit Price", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.unit_price_entry = tk.Entry(frame, font=("Arial", 12))
        self.unit_price_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frame, text="Total Cost", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.total_cost_var = tk.StringVar(value="0.00")
        tk.Label(frame, textvariable=self.total_cost_var, font=("Arial", 12)).grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Buttons
        tk.Button(frame, text="Add to Sale", command=self.add_to_sale).grid(row=4, column=0, columnspan=2, pady=10)
        self.register_button = tk.Button(frame, text="Register Sale", command=self.register_sale, state="disabled")
        self.register_button.grid(row=5, column=0, columnspan=2, pady=5)

        # Refresh Button for Inventory
        tk.Button(frame, text="Refresh Items", command=self.refresh_items).grid(row=5, column=2, padx=10, pady=5)

        # Treeview for displaying registered items ##### testing this
        columns = ("Item Name", "Quantity", "Unit Price", "Total Cost")
        self.sales_tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, anchor="center", width=150)
        self.sales_tree.grid(row=6, column=0, columnspan=3, padx=10, pady=10) #### testing this

    def refresh_items(self):
        """Load inventory items into the dropdown."""
        try:
            items = self.manager.fetch_inventory_items()
            # Correctly access dictionary keys
            item_names = [f"{item['item_name']} (ID: {item['item_id']})" for item in items]
            self.item_var.set("")
            self.item_menu['values'] = item_names
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory items: {e}")

    def add_to_sale(self):
        """Add an item to the current sale."""
        try:
            item = self.item_var.get()
            if not item:
                raise ValueError("Select an item.")

            item_id = int(item.split("(ID: ")[1].strip(")"))
            quantity = int(self.quantity_entry.get())
            unit_price = float(self.unit_price_entry.get())
            total_cost = quantity * unit_price

            if quantity <= 0 or unit_price <= 0:
                raise ValueError("Quantity and unit price must be positive numbers.")

            self.sales_data.append({
                "item_id": item_id,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_cost": total_cost
            })

            # Update the Treeview with the new item #### testing this
            self.sales_tree.insert("", "end", values=(item.split(" (ID:")[0], quantity, f"${unit_price:.2f}", f"${total_cost:.2f}"))

            # Update total cost
            updated_total = float(self.total_cost_var.get()) + total_cost ### testing this
            self.total_cost_var.set(f"{total_cost:.2f}")
            self.register_button.config(state="normal")

            # Clear entries
            self.item_menu.set("")
            self.quantity_entry.delete(0, tk.END)
            self.unit_price_entry.delete(0, tk.END)
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add to sale: {e}")

    def register_sale(self):
        """Register all sales items."""
        try:
            if not self.sales_data:
                raise ValueError("No items in the sales list.")

            self.manager.register_sales(self.sales_data)
            messagebox.showinfo("Success", "Sales registered successfully!")
            self.sales_data.clear()
            for row in self.sales_tree.get_children(): ### testing these 2 lines
                self.sales_tree.delete(row)
            # Reset total cost
            self.total_cost_var.set("0.00")
            self.register_button.config(state="disabled")
            self.refresh_items()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to register sales: {e}")

    # -------------------------------- View All Sales Tab --------------------------------
    def create_view_all_sales_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="View All Sales")

        columns = ("Sales ID", "Item Name", "Quantity", "Unit Price", "Total Cost", "Sales Date")
        self.sales_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, anchor='center')
        self.sales_tree.pack(expand=True, fill="both", padx=10, pady=10)

        tk.Button(frame, text="Refresh", command=self.load_sales).pack(pady=5)

    def load_sales(self):
        """Load all sales records into the Treeview."""
        try:
            for row in self.sales_tree.get_children():
                self.sales_tree.delete(row)
            records = self.manager.fetch_sales_records()
            for record in records:
                self.sales_tree.insert("", "end", values=(
                    record.sales_id,
                    record.item_name,
                    record.quantity_sold,
                    f"${record.unit_price:.2f}",
                    f"${record.total_cost:.2f}",
                    record.sales_date.strftime("%Y-%m-%d %H:%M:%S")
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sales records: {e}")

    # -------------------------------- Update Sales Tab --------------------------------
    def create_update_sales_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Update Sales")

        columns = ("Sales ID", "Item Name", "Quantity", "Unit Price", "Total Cost", "Sales Date")
        self.update_sales_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.update_sales_tree.heading(col, text=col)
            self.update_sales_tree.column(col, anchor='center')
        self.update_sales_tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Update Form
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Field to Update:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.update_field_var = tk.StringVar()
        field_menu = ttk.Combobox(form_frame, textvariable=self.update_field_var, state="readonly")
        field_menu['values'] = ("quantity_sold", "unit_price")
        field_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(form_frame, text="New Value:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.update_value_entry = tk.Entry(form_frame)
        self.update_value_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Update Sale", command=self.update_sales_record).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Refresh", command=self.load_sales_for_update).grid(row=0, column=1, padx=5)

    def load_sales_for_update(self):
        """Load sales records into the update Treeview."""
        try:
            for row in self.update_sales_tree.get_children():
                self.update_sales_tree.delete(row)
            records = self.manager.fetch_sales_records()
            for record in records:
                self.update_sales_tree.insert("", "end", values=(
                    record.sales_id,
                    record.item_name,
                    record.quantity_sold,
                    f"${record.unit_price:.2f}",
                    f"${record.total_cost:.2f}",
                    record.sales_date.strftime("%Y-%m-%d %H:%M:%S")
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sales records for update: {e}")

    def update_sales_record(self):
        """Update a selected sales record."""
        try:
            selected_items = self.update_sales_tree.selection()
            if not selected_items:
                raise ValueError("Please select a sales record to update.")
            selected_item = self.update_sales_tree.item(selected_items[0], "values")
            sales_id = int(selected_item[0])
            field = self.update_field_var.get().strip()
            new_value = self.update_value_entry.get().strip()

            if not field or not new_value:
                raise ValueError("Both field and new value must be provided.")

            # Convert new_value based on field type
            if field == "quantity_sold":
                new_value = int(new_value)
            elif field == "unit_price":
                new_value = float(new_value)

            self.manager.update_sales_record(sales_id, field, new_value)
            messagebox.showinfo("Success", "Sales record updated successfully!")
            self.load_sales_for_update()
            self.load_sales()
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update sales record: {e}")

    # -------------------------------- Delete Sales Tab --------------------------------
    def create_delete_sales_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Delete Sales")

        columns = ("Sales ID", "Item Name", "Quantity", "Unit Price", "Total Cost", "Sales Date")
        self.delete_sales_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.delete_sales_tree.heading(col, text=col)
            self.delete_sales_tree.column(col, anchor='center')
        self.delete_sales_tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Delete Sale", command=self.delete_sales_record).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Refresh", command=self.load_sales_for_delete).grid(row=0, column=1, padx=5)

    def load_sales_for_delete(self):
        """Load sales records into the delete Treeview."""
        try:
            for row in self.delete_sales_tree.get_children():
                self.delete_sales_tree.delete(row)
            records = self.manager.fetch_sales_records()
            for record in records:
                self.delete_sales_tree.insert("", "end", values=(
                    record.sales_id,
                    record.item_name,
                    record.quantity_sold,
                    f"${record.unit_price:.2f}",
                    f"${record.total_cost:.2f}",
                    record.sales_date.strftime("%Y-%m-%d %H:%M:%S")
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sales records for deletion: {e}")

    def delete_sales_record(self):
        """Delete a selected sales record."""
        try:
            selected_items = self.delete_sales_tree.selection()
            if not selected_items:
                raise ValueError("Please select a sales record to delete.")
            selected_item = self.delete_sales_tree.item(selected_items[0], "values")
            sales_id = int(selected_item[0])

            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete sales ID {sales_id}?")
            if not confirm:
                return

            self.manager.delete_sales_record(sales_id)
            messagebox.showinfo("Success", "Sales record deleted successfully!")
            self.load_sales_for_delete()
            self.load_sales()
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete sales record: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SalesManagerGUI(root)
    app.pack(expand=True, fill="both")
    root.mainloop()
'''