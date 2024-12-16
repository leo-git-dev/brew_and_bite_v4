import unittest
from unittest.mock import patch, MagicMock
from business_logic.sales_management_v3 import SalesManager
from database.models_v3 import Sales, Inventory


class TestSalesManager(unittest.TestCase):

    @patch('business_logic.sales_management_v3.sessionmaker')
    def setUp(self, mock_sessionmaker):
        """Set up the SalesManager and mock session."""
        self.mock_session = MagicMock()
        mock_sessionmaker.return_value = self.mock_session
        self.sales_manager = SalesManager(db_url="sqlite:///:memory:")

    @patch('business_logic.sales_management_v3.Inventory')
    @patch('business_logic.sales_management_v3.Sales')
    def test_register_sales_success(self, mock_sales, mock_inventory):
        """Test successful registration of sales."""
        mock_inventory_item = MagicMock(quantity=20)
        self.mock_session.return_value.query.return_value.filter_by.return_value.first.return_value = mock_inventory_item

        sales_data = [{"item_id": 1, "quantity": 5, "unit_price": 10.0}]

        self.sales_manager.register_sales(sales_data)

        self.assertEqual(mock_inventory_item.quantity, 15)
        self.mock_session.return_value.add.assert_any_call(mock_sales())
        self.mock_session.return_value.commit.assert_called_once()

    @patch('business_logic.sales_management_v3.Inventory')
    def test_register_sales_insufficient_stock(self, mock_inventory):
        """Test registration of sales with insufficient stock."""
        mock_inventory_item = MagicMock(quantity=2)
        self.mock_session.return_value.query.return_value.filter_by.return_value.first.return_value = mock_inventory_item

        sales_data = [{"item_id": 1, "quantity": 5, "unit_price": 10.0}]

        with self.assertRaises(ValueError) as context:
            self.sales_manager.register_sales(sales_data)
        self.assertEqual(str(context.exception), "Insufficient stock for item ID 1.")

    def test_register_sales_negative_values(self):
        """Test registration of sales with negative quantity or price."""
        sales_data = [{"item_id": 1, "quantity": -5, "unit_price": -10.0}]
        with self.assertRaises(ValueError) as context:
            self.sales_manager.register_sales(sales_data)
        self.assertEqual(str(context.exception), "Quantity and unit price must be positive numbers.")

    @patch('business_logic.sales_management_v3.DatabaseRepository')
    def test_fetch_inventory_items(self, mock_repo):
        """Test fetching inventory items."""
        # Mock the repository instance
        mock_repo_instance = mock_repo.return_value
        mock_repo_instance.fetch_inventory_items.return_value = [
            (1, "Item1"),
            (2, "Item2")
        ]

        # Override the repository in SalesManager with the mock
        self.sales_manager.repo = mock_repo_instance

        # Call the method
        result = self.sales_manager.fetch_inventory_items()

        # Expected result
        expected_result = [
            {"item_id": 1, "item_name": "Item1"},
            {"item_id": 2, "item_name": "Item2"}
        ]

        # Assert the results match
        self.assertEqual(result, expected_result)

        # Verify the mock was called
        mock_repo_instance.fetch_inventory_items.assert_called_once()

    @patch('business_logic.sales_management_v3.Sales')
    def test_delete_sales_record_success(self, mock_sales):
        """Test successful deletion of a sales record."""
        mock_sales_record = MagicMock()
        self.mock_session.return_value.query.return_value.filter_by.return_value.first.return_value = mock_sales_record

        self.sales_manager.delete_sales_record(sales_id=1)
        self.mock_session.return_value.delete.assert_called_once_with(mock_sales_record)
        self.mock_session.return_value.commit.assert_called_once()

    def test_delete_sales_record_not_found(self):
        """Test deletion of a non-existent sales record."""
        self.mock_session.return_value.query.return_value.filter_by.return_value.first.return_value = None

        with self.assertRaises(ValueError) as context:
            self.sales_manager.delete_sales_record(sales_id=1)
        self.assertEqual(str(context.exception), "No sales record found with Sales ID 1.")

    @patch('business_logic.sales_management_v3.Sales')
    def test_update_sales_record_success(self, mock_sales):
        """Test successful update of a sales record."""
        mock_sales_record = MagicMock(quantity_sold=5, unit_price=10.0, total_cost=50.0)
        self.mock_session.return_value.query.return_value.filter_by.return_value.first.return_value = mock_sales_record

        self.sales_manager.update_sales_record(sales_id=1, field="quantity_sold", new_value=10)

        self.assertEqual(mock_sales_record.quantity_sold, 10)
        self.assertEqual(mock_sales_record.total_cost, 100.0)
        self.mock_session.return_value.commit.assert_called_once()

    def test_update_sales_record_not_found(self):
        """Test updating a non-existent sales record."""
        self.mock_session.return_value.query.return_value.filter_by.return_value.first.return_value = None

        with self.assertRaises(ValueError) as context:
            self.sales_manager.update_sales_record(sales_id=1, field="quantity_sold", new_value=10)
        self.assertEqual(str(context.exception), "No sales record found with Sales ID 1.")


if __name__ == "__main__":
    unittest.main()
