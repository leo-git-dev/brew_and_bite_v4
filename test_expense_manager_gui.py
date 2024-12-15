import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from gui.expense_manager_gui_v3 import ExpenseManagerGUI
from datetime import date, datetime


class TestExpenseManagerGUI(unittest.TestCase):
    def setUp(self):
        """Set up the GUI and mock the ExpenseManager."""
        self.root = tk.Tk()
        self.gui = ExpenseManagerGUI(self.root)
        self.gui.manager = MagicMock()  # Mock the ExpenseManager

    def tearDown(self):
        """Destroy the GUI."""
        self.root.destroy()

    @patch("tkinter.messagebox.showinfo")
    def test_add_expense_success(self, mock_showinfo):
        """Test adding an expense successfully."""
        self.gui.expense_date_entry.set_date(date(2024, 1, 1))  # Use a date object
        self.gui.category_var.set("Food")
        self.gui.supplier_var.set("1: Supplier A")
        self.gui.expense_name_entry.insert(0, "Test Expense")
        self.gui.total_items_entry.insert(0, "10")
        self.gui.unit_cost_entry.insert(0, "5.00")

        self.gui.add_expense()

        self.gui.manager.add_expense.assert_called_once_with(
            expense_date=date(2024, 1, 1),  # Use a date object to match the actual call
            category="Food",
            supplier_id=1,
            expense_name="Test Expense",
            total_items=10,
            unit_cost=5.0,
        )
        mock_showinfo.assert_called_once_with("Success", "Expense added successfully!")

    @patch("tkinter.messagebox.showerror")
    def test_add_expense_invalid_supplier(self, mock_showerror):
        """Test adding an expense with an invalid supplier."""
        self.gui.expense_date_entry.set_date(date(2024, 1, 1))
        self.gui.category_var.set("Food")
        self.gui.supplier_var.set("")  # Invalid supplier
        self.gui.expense_name_entry.insert(0, "Test Expense")
        self.gui.total_items_entry.insert(0, "10")
        self.gui.unit_cost_entry.insert(0, "5.00")

        self.gui.add_expense()

        self.gui.manager.add_expense.assert_not_called()
        mock_showerror.assert_called_once_with("Input Error", "Please select a valid supplier.")

    @patch("tkinter.messagebox.showerror")
    def test_add_expense_invalid_total_items(self, mock_showerror):
        """Test adding an expense with invalid total items."""
        self.gui.expense_date_entry.set_date(date(2024, 1, 1))
        self.gui.category_var.set("Food")
        self.gui.supplier_var.set("1: Supplier A")
        self.gui.expense_name_entry.insert(0, "Test Expense")
        self.gui.total_items_entry.insert(0, "-10")  # Invalid total items
        self.gui.unit_cost_entry.insert(0, "5.00")

        self.gui.add_expense()

        self.gui.manager.add_expense.assert_not_called()
        mock_showerror.assert_called_once_with("Input Error", "Total items must be a positive integer.")

    @patch("tkinter.messagebox.showerror")
    def test_refresh_suppliers_failure(self, mock_showerror):
        """Test refreshing suppliers with a failure."""
        self.gui.manager.get_suppliers.side_effect = Exception("Database error")

        self.gui.refresh_suppliers()

        mock_showerror.assert_called_once_with("Error", "Failed to load suppliers: Database error")

    def test_clear_add_expense_fields(self):
        """Test clearing fields after adding an expense."""
        self.gui.expense_date_entry.set_date(date(2024, 1, 1))
        self.gui.category_var.set("Beverages")
        self.gui.supplier_var.set("1: Supplier A")
        self.gui.expense_name_entry.insert(0, "Test Expense")
        self.gui.total_items_entry.insert(0, "10")
        self.gui.unit_cost_entry.insert(0, "5.00")
        self.gui.total_cost_var.set("50.00")

        self.gui.clear_add_expense_fields()

        self.assertEqual(self.gui.expense_date_entry.get_date(), datetime.now().date())
        self.assertEqual(self.gui.category_var.get(), "Food")
        self.assertEqual(self.gui.supplier_var.get(), "")
        self.assertEqual(self.gui.expense_name_entry.get(), "")
        self.assertEqual(self.gui.total_items_entry.get(), "")
        self.assertEqual(self.gui.unit_cost_entry.get(), "")
        self.assertEqual(self.gui.total_cost_var.get(), "0.00")

    @patch("tkinter.messagebox.showerror")
    def test_load_expenses_failure(self, mock_showerror):
        """Test loading expenses with a failure."""
        self.gui.manager.get_all_expenses.side_effect = Exception("Database error")

        self.gui.load_expenses()

        mock_showerror.assert_called_once_with("Error", "Failed to load expenses: Database error")

    def test_load_expenses_success(self):
        """Test loading expenses successfully."""
        self.gui.manager.get_all_expenses.return_value = [
            MagicMock(
                expense_id=1,
                expense_date=date(2024, 1, 1),
                category="Food",
                supplier=MagicMock(username="Supplier A"),
                expense_name="Expense A",
                total_items=10,
                unit_cost=5.00,
                total_cost=50.00,
            ),
            MagicMock(
                expense_id=2,
                expense_date=date(2024, 1, 2),
                category="Beverages",
                supplier=None,
                expense_name="Expense B",
                total_items=20,
                unit_cost=3.00,
                total_cost=60.00,
            ),
        ]

        self.gui.load_expenses()

        self.assertEqual(len(self.gui.expenses_tree.get_children()), 2)


if __name__ == "__main__":
    unittest.main()
