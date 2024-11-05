import unittest
from decimal import Decimal
from typing import Dict, List, Optional
import sys
from unittest.mock import Mock

# Define the Product class with attributes and methods for a product in an e-commerce system
class Product:
    def __init__(self, id: int, name: str, price: Decimal, description: str):
        # Initialize product with ID, name, price, description, tax rate, and discount rate
        self.id = id
        self._name = name
        self._price = price
        self._description = description
        self._tax_rate = Decimal('0.10')  # 10% tax
        self._discount_rate = Decimal('0.00')  # Default no discount

    # Define getter and setter for product name with validation
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value:
            raise ValueError("Name cannot be empty")
        self._name = value

    # Define getter and setter for product price with validation
    @property
    def price(self) -> Decimal:
        return self._price

    @price.setter
    def price(self, value: Decimal) -> None:
        if value < 0:
            raise ValueError("Price cannot be negative")
        self._price = value

    # Define getter and setter for product description with validation
    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        if not value:
            raise ValueError("Description cannot be empty")
        self._description = value

    # Method to set discount rate with validation
    def set_discount(self, discount_rate: Decimal) -> None:
        if not (0 <= discount_rate <= 1):
            raise ValueError("Discount rate must be between 0 and 1")
        self._discount_rate = discount_rate

    # Calculate the price with tax applied
    def get_price_with_tax(self) -> Decimal:
        return self.price * (1 + self._tax_rate)

    # Calculate the final price after applying tax and discount
    def get_final_price(self) -> Decimal:
        price_with_tax = self.get_price_with_tax()
        return price_with_tax * (1 - self._discount_rate)

# Define the ShoppingCart class to manage products and quantities
class ShoppingCart:
    def __init__(self):
        # Initialize an empty dictionary to store products and quantities
        self._items: Dict[Product, int] = {}

    # Add a product to the cart with a specified quantity
    def add_product(self, product: Product, quantity: int = 1) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if product in self._items:
            self._items[product] += quantity
        else:
            self._items[product] = quantity

    # Remove a product from the cart with a specified quantity
    def remove_product(self, product: Product, quantity: Optional[int] = None) -> None:
        if product not in self._items:
            raise ValueError("Product not in cart")
        
        if quantity is None or self._items[product] <= quantity:
            del self._items[product]
        else:
            self._items[product] -= quantity

    # Calculate the total cost of all items in the cart
    def get_total(self) -> Decimal:
        total = Decimal('0')
        for product, quantity in self._items.items():
            total += product.get_final_price() * quantity
        return total

    # Return a copy of the items in the cart
    def get_items(self) -> Dict[Product, int]:
        return self._items.copy()

# Unit tests for the Product class
class TestProduct(unittest.TestCase):
    def setUp(self):
        # Setup a sample product for testing
        self.product = Product(1, "Test Product", Decimal('10.00'), "Test Description")

    # Test initial values of the product attributes
    def test_initial_values(self):
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.price, Decimal('10.00'))
        self.assertEqual(self.product.description, "Test Description")

    # Test the price calculation with tax
    def test_price_with_tax(self):
        expected = Decimal('11.00')  # 10.00 + 10% tax
        self.assertEqual(self.product.get_price_with_tax(), expected)

    # Test for invalid price (negative)
    def test_invalid_price(self):
        with self.assertRaises(ValueError):
            self.product.price = Decimal('-1.00')

    # Test the application of discount and final price calculation
    def test_discount(self):
        self.product.set_discount(Decimal('0.20'))  # 20% discount
        expected = Decimal('8.80')  # (10.00 + 10% tax) - 20% discount
        self.assertEqual(self.product.get_final_price(), expected)

# Unit tests for the ShoppingCart class
class TestShoppingCart(unittest.TestCase):
    def setUp(self):
        # Setup a sample cart and products for testing
        self.cart = ShoppingCart()
        self.product1 = Product(1, "Product 1", Decimal('10.00'), "Description 1")
        self.product2 = Product(2, "Product 2", Decimal('20.00'), "Description 2")

    # Test adding a product to the cart
    def test_add_product(self):
        self.cart.add_product(self.product1, 2)
        items = self.cart.get_items()
        self.assertEqual(items[self.product1], 2)

    # Test removing a product from the cart
    def test_remove_product(self):
        self.cart.add_product(self.product1, 2)
        self.cart.remove_product(self.product1, 1)
        items = self.cart.get_items()
        self.assertEqual(items[self.product1], 1)

    # Test calculating the total cost of products in the cart
    def test_cart_total(self):
        self.cart.add_product(self.product1, 2)  # 2 * (10.00 + 10% tax) = 22.00
        self.cart.add_product(self.product2, 1)  # 1 * (20.00 + 10% tax) = 22.00
        expected = Decimal('44.00')
        self.assertEqual(self.cart.get_total(), expected)

# Integration tests to test interaction between Product and ShoppingCart classes
class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.cart = ShoppingCart()
        self.product = Product(1, "Test Product", Decimal('10.00'), "Test Description")

    # Test adding a product to the cart and calculating the total
    def test_add_and_calculate(self):
        self.product.set_discount(Decimal('0.20'))  # 20% discount
        self.cart.add_product(self.product, 2)
        expected = Decimal('17.60')  # 2 * ((10.00 + 10% tax) - 20% discount)
        self.assertEqual(self.cart.get_total(), expected)

    # Test removing a product from the cart in integration context
    def test_remove_product_integration(self):
        self.cart.add_product(self.product, 2)
        self.cart.remove_product(self.product, 1)
        self.assertEqual(self.cart.get_items()[self.product], 1)
        self.cart.remove_product(self.product)  # Remove remaining quantity
        self.assertNotIn(self.product, self.cart.get_items())

# Run tests and print a summary report
def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestProduct)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestShoppingCart))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIntegration))
    
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    
    # Summary report
    print("\nSummary Report:")
    print(f"Total tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    if result.failures or result.errors:
        print("\nDetails:")
        for failure in result.failures + result.errors:
            print(failure[1])  # Print error message

if __name__ == "__main__":
    main()
