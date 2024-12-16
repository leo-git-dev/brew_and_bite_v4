import unittest
from unittest.mock import patch, MagicMock
from business_logic.inventory_management_v3 import InventoryManager
from database.models_v3 import Inventory, User


class TestInventoryManager(unittest.TestCase):

    @patch('business_logic.inventory_management_v3.sessionmaker')
    def setUp(self, mock_sessionmaker):
        """Set up the InventoryManager and mock session."""
        self.mock_session = MagicMock()
        mock_sessionmaker.return_value = self.mock_session
        self.inventory_manager = InventoryManager(db_url="sqlite:///:memory:")

    @patch('business_logic.inventory_management_v3.User')
    @patch('business_logic.inventory_management_v3.Inventory')
    def test_add_inventory_item_success(self, mock_inventory, mock_user):
        """Test successful addition of an inventory item."""
        mock_supplier = MagicMock()
        mock_user.query.filter_by.return_value.first.return_value = mock_supplier

        self.inventory_manager.add_inventory_item(
            item_name="Test Item",
            category="Food",
            quantity=10,
            unit_cost=5.0,
            supplier_id=1
        )

        self.mock_session.return_value.add.assert_called_once()
        self.mock_session.return_value.commit.assert_called_once()

    def test_add_inventory_item_invalid_category(self):
        """Test adding an inventory item with an invalid category."""
        with self.assertRaises(ValueError) as context:
            self.inventory_manager.add_inventory_item(
                item_name="Test Item",
                category="Invalid Category",
                quantity=10,
                unit_cost=5.0,
                supplier_id=1
            )
        self.assertEqual(str(context.exception), "Invalid category: Invalid Category")

    def test_add_inventory_item_negative_quantity(self):
        """Test adding an inventory item with negative quantity."""
        with self.assertRaises(ValueError) as context:
            self.inventory_manager.add_inventory_item(
                item_name="Test Item",
                category="Food",
                quantity=-10,
                unit_cost=5.0,
                supplier_id=1
            )
        self.assertEqual(str(context.exception), "Quantity cannot be negative.")

    def test_add_inventory_item_negative_cost(self):
        """Test adding an inventory item with negative unit cost."""
        with self.assertRaises(ValueError) as context:
            self.inventory_manager.add_inventory_item(
                item_name="Test Item",
                category="Food",
                quantity=10,
                unit_cost=-5.0,
                supplier_id=1
            )
        self.assertEqual(str(context.exception), "Unit cost cannot be negative.")

    @patch('business_logic.inventory_management_v3.Inventory')
    def test_fetch_inventory(self, mock_inventory):
        """Test fetching inventory items."""
        mock_query = self.mock_session.return_value.query.return_value
        mock_query.options.return_value.all.return_value = ["MockItem1", "MockItem2"]

        result = self.inventory_manager.fetch_inventory()
        self.assertEqual(result, ["MockItem1", "MockItem2"])
        mock_query.options.return_value.all.assert_called_once()

    @patch('business_logic.inventory_management_v3.Inventory')
    def test_update_inventory_item_success(self, mock_inventory):
        """Test successful update of an inventory item."""
        mock_item = MagicMock()
        self.mock_session.return_value.query.return_value.filter_by.return_value.first.return_value = mock_item

        self.inventory_manager.update_inventory_item(item_id=1, field="quantity", new_value=20)

        self.assertEqual(mock_item.quantity, 20)
        self.mock_session.return_value.commit.assert_called_once()

    def test_update_inventory_item_invalid_field(self):
        """Test updating an inventory item with an invalid field."""
        with self.assertRaises(ValueError) as context:
            self.inventory_manager.update_inventory_item(item_id=1, field="invalid_field", new_value="value")
        self.assertEqual(str(context.exception), "Invalid field: invalid_field")

    @patch('business_logic.inventory_management_v3.Inventory')
    def test_delete_inventory_item_success(self, mock_inventory):
        """Test successful deletion of an inventory item."""
        mock_item = MagicMock()
        self.mock_session.return_value.query.return_value.filter_by.return_value.first.return_value = mock_item

        self.inventory_manager.delete_inventory_item(item_id=1)
        self.mock_session.return_value.delete.assert_called_once_with(mock_item)
        self.mock_session.return_value.commit.assert_called_once()

    @patch('business_logic.inventory_management_v3.Inventory')
    def test_delete_inventory_item_not_found(self, mock_inventory):
        """Test deleting a non-existent inventory item."""
        # Ensure the query chain returns None
        self.mock_session.return_value.query.return_value.filter_by.return_value.first.return_value = None

        # Call the method and verify that ValueError is raised
        with self.assertRaises(ValueError) as context:
            self.inventory_manager.delete_inventory_item(item_id=1)

        # Check the error message
        self.assertEqual(str(context.exception), "Item with ID 1 not found.")

    @patch('business_logic.inventory_management_v3.User')
    def test_fetch_all_suppliers(self, mock_user):
        """Test fetching all suppliers."""
        mock_query = self.mock_session.return_value.query.return_value
        mock_query.filter_by.return_value.all.return_value = ["Supplier1", "Supplier2"]

        result = self.inventory_manager.fetch_all_suppliers()
        self.assertEqual(result, ["Supplier1", "Supplier2"])
        mock_query.filter_by.assert_called_once_with(registration_type="supplier")


if __name__ == "__main__":
    unittest.main()
