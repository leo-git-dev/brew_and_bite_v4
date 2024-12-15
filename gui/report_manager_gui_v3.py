# gui/report_manager_gui_v3.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from business_logic.report_manager_v3 import FinancialReportManager
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class FinancialReportGUI(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.report_manager = FinancialReportManager()
        self.initialize_gui()

    def initialize_gui(self):
        """Set up the Financial Report tab."""
        notebook = ttk.Notebook(self)
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Financial Reports")
        notebook.pack(expand=True, fill="both")

        # Buttons for different reports
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Total Sales Per Day", command=self.display_sales_per_day).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="Sales By Category", command=self.display_sales_by_category).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="Total Expenses Per Day", command=self.display_expenses_per_day).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(button_frame, text="Expense vs Sales", command=self.display_expense_vs_sales).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(button_frame, text="Expenses by Supplier and Category", command=self.display_expenses_by_supplier_and_category).grid(row=0, column=4, padx=5, pady=5)

        # Canvas for displaying the charts
        self.figure = plt.Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(expand=True, fill="both", padx=10, pady=10)

        # Export Button
        ttk.Button(frame, text="Export Current Report as JPEG/PNG", command=self.export_report).pack(pady=10)

    def clear_chart(self):
        """Clear the current chart."""
        self.figure.clf()

    def display_sales_per_day(self):
        """Display total sales per day as a bar chart."""
        self.clear_chart()
        data = self.report_manager.calculate_total_sales_per_day()
        if not data:
            messagebox.showinfo("Info", "No sales data available.")
            return

        dates = [record.date for record in data]
        totals = [record.total_sales for record in data]

        ax = self.figure.add_subplot(111)
        ax.bar(dates, totals, color='blue')
        ax.set_title("Total Sales Per Day")
        ax.set_xlabel("Date")
        ax.set_ylabel("Total Sales")
        ax.tick_params(axis='x', rotation=45)
        self.figure.tight_layout()
        self.canvas.draw()

    def display_sales_by_category(self):
        """Display sales by category as a pie chart."""
        self.clear_chart()
        data = self.report_manager.calculate_sales_by_category()
        if not data:
            messagebox.showinfo("Info", "No sales data available.")
            return

        categories = [record.category for record in data]
        totals = [record.total_sales for record in data]

        ax = self.figure.add_subplot(111)
        ax.pie(totals, labels=categories, autopct="%1.1f%%", startangle=140)
        ax.set_title("Sales By Category")
        self.canvas.draw()

    def display_expenses_per_day(self):
        """Display total expenses per day as a line chart."""
        self.clear_chart()
        data = self.report_manager.calculate_total_expenses_per_day()
        if not data:
            messagebox.showinfo("Info", "No expense data available.")
            return

        dates = [record.date for record in data]
        totals = [record.total_expenses for record in data]

        ax = self.figure.add_subplot(111)
        ax.plot(dates, totals, marker='o', color='red')
        ax.set_title("Total Expenses Per Day")
        ax.set_xlabel("Date")
        ax.set_ylabel("Total Expenses")
        ax.tick_params(axis='x', rotation=45)
        self.figure.tight_layout()
        self.canvas.draw()

    def display_expense_vs_sales(self):
        """Display total expense vs total sales as a bar chart."""
        self.clear_chart()
        data = self.report_manager.calculate_expense_vs_sales()
        if data is None:
            messagebox.showinfo("Info", "No sales or expense data available.")
            return

        categories = ["Total Sales", "Total Expenses"]
        totals = [data["total_sales"], data["total_expenses"]]

        ax = self.figure.add_subplot(111)
        ax.bar(categories, totals, color=['green', 'orange'])
        ax.set_title("Expense vs Sales")
        ax.set_ylabel("Amount")
        self.figure.tight_layout()
        self.canvas.draw()

    def display_expenses_by_supplier_and_category(self):
        """Display expenses by supplier and category as a grouped bar chart."""
        self.clear_chart()
        data = self.report_manager.calculate_expense_by_supplier_and_category()
        if not data:
            messagebox.showinfo("Info", "No expense data available.")
            return

        # Extract unique suppliers and categories
        suppliers = sorted(list(set([record.supplier for record in data])))
        categories = sorted(list(set([record.category for record in data])))

        # Prepare data
        supplier_category_expenses = {supplier: {category: 0 for category in categories} for supplier in suppliers}
        for record in data:
            supplier_category_expenses[record.supplier][record.category] += record.total_expenses

        # Plot grouped bar chart
        ax = self.figure.add_subplot(111)
        bar_width = 0.8 / len(suppliers)  # Adjust bar width based on number of suppliers
        indices = range(len(categories))
        for i, supplier in enumerate(suppliers):
            expenses = [supplier_category_expenses[supplier][category] for category in categories]
            ax.bar([x + i * bar_width for x in indices], expenses, bar_width, label=supplier)

        ax.set_xticks([x + bar_width * (len(suppliers) - 1) / 2 for x in indices])
        ax.set_xticklabels(categories, rotation=45)
        ax.set_xlabel("Category")
        ax.set_ylabel("Total Expenses")
        ax.set_title("Expenses by Supplier and Category")
        ax.legend()
        self.figure.tight_layout()
        self.canvas.draw()

    def export_report(self):
        """Export the current chart as a JPEG or PNG file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if not file_path:
            return
        try:
            self.figure.savefig(file_path)
            messagebox.showinfo("Success", f"Report saved as {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report: {e}")
