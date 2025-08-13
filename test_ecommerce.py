import pytest
import json
import tempfile
import os
from fastapi.testclient import TestClient
from decimal import Decimal
from datetime import datetime

from main import app, USERS_FILE, ORDERS_FILE, PRODUCTS_FILE, ADDRESSES_FILE, PAYOUTS_FILE
from main import UserRole, OrderStatus, PaymentStatus, PaymentMethod, PayoutStatus

client = TestClient(app)

# Test fixtures
@pytest.fixture
def clean_files():
    """Clean up data files before and after tests"""
    files = [USERS_FILE, ORDERS_FILE, PRODUCTS_FILE, ADDRESSES_FILE, PAYOUTS_FILE]
    
    # Clean before test
    for file in files:
        if os.path.exists(file):
            os.remove(file)
    
    yield
    
    # Clean after test
    for file in files:
        if os.path.exists(file):
            os.remove(file)

@pytest.fixture
def customer_user(clean_files):
    """Create a test customer user"""
    response = client.post("/register", json={
        "email": "customer@test.com",
        "password": "testpass123",
        "role": "customer"
    })
    assert response.status_code == 200
    
    # Login to get token
    login_response = client.post("/login", json={
        "email": "customer@test.com",
        "password": "testpass123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    return {
        "email": "customer@test.com",
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }

@pytest.fixture
def vendor_user(clean_files):
    """Create a test vendor user"""
    response = client.post("/register", json={
        "email": "vendor@test.com",
        "password": "testpass123",
        "role": "vendor"
    })
    assert response.status_code == 200
    
    # Login to get token
    login_response = client.post("/login", json={
        "email": "vendor@test.com",
        "password": "testpass123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    return {
        "email": "vendor@test.com",
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }

@pytest.fixture
def admin_user(clean_files):
    """Create a test admin user"""
    response = client.post("/register", json={
        "email": "admin@test.com",
        "password": "testpass123",
        "role": "admin"
    })
    assert response.status_code == 200
    
    # Login to get token
    login_response = client.post("/login", json={
        "email": "admin@test.com",
        "password": "testpass123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    return {
        "email": "admin@test.com",
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }

@pytest.fixture
def test_address(customer_user):
    """Create a test address"""
    response = client.post("/addresses", 
        headers=customer_user["headers"],
        json={
            "street": "123 Test Street",
            "city": "Test City",
            "state": "Test State",
            "postal_code": "12345",
            "country": "Test Country",
            "is_default": True
        }
    )
    assert response.status_code == 200
    return response.json()

@pytest.fixture
def test_product(vendor_user):
    """Create a test product"""
    response = client.post("/products",
        headers=vendor_user["headers"],
        json={
            "name": "Test Product",
            "description": "A test product for testing",
            "price": "29.99",
            "inventory_count": 100,
            "category": "Test Category",
            "image_urls": ["http://test.com/image1.jpg"]
        }
    )
    assert response.status_code == 200
    return response.json()

class TestUserRegistration:
    """Test user registration with roles"""
    
    def test_register_customer(self, clean_files):
        response = client.post("/register", json={
            "email": "customer@test.com",
            "password": "testpass123",
            "role": "customer"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "customer@test.com"
        assert data["role"] == "customer"
    
    def test_register_vendor(self, clean_files):
        response = client.post("/register", json={
            "email": "vendor@test.com",
            "password": "testpass123",
            "role": "vendor"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "vendor@test.com"
        assert data["role"] == "vendor"
    
    def test_register_admin(self, clean_files):
        response = client.post("/register", json={
            "email": "admin@test.com",
            "password": "testpass123",
            "role": "admin"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@test.com"
        assert data["role"] == "admin"

class TestAddressManagement:
    """Test address CRUD operations"""
    
    def test_create_address(self, customer_user):
        response = client.post("/addresses", 
            headers=customer_user["headers"],
            json={
                "street": "123 Test Street",
                "city": "Test City",
                "state": "Test State",
                "postal_code": "12345",
                "country": "Test Country",
                "is_default": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["street"] == "123 Test Street"
        assert data["is_default"] == True
    
    def test_list_addresses(self, customer_user, test_address):
        response = client.get("/addresses", headers=customer_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == test_address["id"]
    
    def test_get_address(self, customer_user, test_address):
        response = client.get(f"/addresses/{test_address['id']}", 
                            headers=customer_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_address["id"]
        assert data["street"] == "123 Test Street"
    
    def test_update_address(self, customer_user, test_address):
        response = client.put(f"/addresses/{test_address['id']}", 
            headers=customer_user["headers"],
            json={
                "street": "456 Updated Street",
                "city": "Updated City",
                "state": "Updated State",
                "postal_code": "54321",
                "country": "Updated Country",
                "is_default": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["street"] == "456 Updated Street"
        assert data["city"] == "Updated City"
    
    def test_delete_address(self, customer_user, test_address):
        response = client.delete(f"/addresses/{test_address['id']}", 
                               headers=customer_user["headers"])
        assert response.status_code == 200
        
        # Verify deletion
        response = client.get("/addresses", headers=customer_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

class TestProductManagement:
    """Test product CRUD operations"""
    
    def test_create_product_vendor(self, vendor_user):
        response = client.post("/products",
            headers=vendor_user["headers"],
            json={
                "name": "Test Product",
                "description": "A test product for testing",
                "price": "29.99",
                "inventory_count": 100,
                "category": "Test Category",
                "image_urls": ["http://test.com/image1.jpg"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Product"
        assert data["vendor_email"] == vendor_user["email"]
        assert float(data["price"]) == 29.99
    
    def test_create_product_customer_forbidden(self, customer_user):
        response = client.post("/products",
            headers=customer_user["headers"],
            json={
                "name": "Test Product",
                "description": "A test product for testing",
                "price": "29.99",
                "inventory_count": 100,
                "category": "Test Category"
            }
        )
        assert response.status_code == 403
    
    def test_list_products(self, vendor_user, test_product):
        response = client.get("/products")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(product["id"] == test_product["id"] for product in data)
    
    def test_get_product(self, vendor_user, test_product):
        response = client.get(f"/products/{test_product['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_product["id"]
        assert data["name"] == "Test Product"

class TestCheckoutProcess:
    """Test the checkout and order creation process"""
    
    def test_validate_cart(self, customer_user, vendor_user, test_product):
        response = client.post("/checkout/validate-cart",
            headers=customer_user["headers"],
            json=[{
                "product_id": test_product["id"],
                "quantity": 2,
                "price": "29.99"
            }]
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["validated_items"]) == 1
        assert float(data["subtotal"]) == 59.98
        assert float(data["total_amount"]) > float(data["subtotal"])  # Includes tax and shipping
    
    def test_validate_cart_insufficient_inventory(self, customer_user, vendor_user, test_product):
        response = client.post("/checkout/validate-cart",
            headers=customer_user["headers"],
            json=[{
                "product_id": test_product["id"],
                "quantity": 200,  # More than available inventory (100)
                "price": "29.99"
            }]
        )
        assert response.status_code == 400
        assert "Insufficient inventory" in response.json()["detail"]
    
    def test_validate_cart_price_mismatch(self, customer_user, vendor_user, test_product):
        response = client.post("/checkout/validate-cart",
            headers=customer_user["headers"],
            json=[{
                "product_id": test_product["id"],
                "quantity": 1,
                "price": "19.99"  # Wrong price
            }]
        )
        assert response.status_code == 400
        assert "Price mismatch" in response.json()["detail"]
    
    def test_process_checkout(self, customer_user, vendor_user, test_product, test_address):
        response = client.post("/checkout/process",
            headers=customer_user["headers"],
            json={
                "cart_items": [{
                    "product_id": test_product["id"],
                    "quantity": 1,
                    "price": "29.99"
                }],
                "shipping_address_id": test_address["id"],
                "payment_info": {
                    "payment_method": "credit_card",
                    "token": "test_payment_token_12345",
                    "billing_address_id": test_address["id"]
                },
                "guest_checkout": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["customer_email"] == customer_user["email"]
        assert data["status"] == "confirmed"
        assert data["payment_status"] == "completed"
        assert len(data["items"]) == 1

class TestOrderManagement:
    """Test order tracking and management"""
    
    def create_test_order(self, customer_user, vendor_user, test_product, test_address):
        """Helper method to create a test order"""
        response = client.post("/checkout/process",
            headers=customer_user["headers"],
            json={
                "cart_items": [{
                    "product_id": test_product["id"],
                    "quantity": 1,
                    "price": "29.99"
                }],
                "shipping_address_id": test_address["id"],
                "payment_info": {
                    "payment_method": "credit_card",
                    "token": "test_payment_token_12345",
                    "billing_address_id": test_address["id"]
                },
                "guest_checkout": False
            }
        )
        return response.json()
    
    def test_list_customer_orders(self, customer_user, vendor_user, test_product, test_address):
        order = self.create_test_order(customer_user, vendor_user, test_product, test_address)
        
        response = client.get("/orders", headers=customer_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == order["id"]
    
    def test_get_order_details(self, customer_user, vendor_user, test_product, test_address):
        order = self.create_test_order(customer_user, vendor_user, test_product, test_address)
        
        response = client.get(f"/orders/{order['id']}", headers=customer_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order["id"]
        assert data["customer_email"] == customer_user["email"]
    
    def test_cancel_order(self, customer_user, vendor_user, test_product, test_address):
        order = self.create_test_order(customer_user, vendor_user, test_product, test_address)
        
        response = client.post(f"/orders/{order['id']}/cancel", headers=customer_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

class TestVendorManagement:
    """Test vendor order management and statistics"""
    
    def create_test_order(self, customer_user, vendor_user, test_product, test_address):
        """Helper method to create a test order"""
        response = client.post("/checkout/process",
            headers=customer_user["headers"],
            json={
                "cart_items": [{
                    "product_id": test_product["id"],
                    "quantity": 1,
                    "price": "29.99"
                }],
                "shipping_address_id": test_address["id"],
                "payment_info": {
                    "payment_method": "credit_card",
                    "token": "test_payment_token_12345",
                    "billing_address_id": test_address["id"]
                },
                "guest_checkout": False
            }
        )
        return response.json()
    
    def test_list_vendor_orders(self, customer_user, vendor_user, test_product, test_address):
        order = self.create_test_order(customer_user, vendor_user, test_product, test_address)
        
        response = client.get("/vendor/orders", headers=vendor_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == order["id"]
    
    def test_update_order_status(self, customer_user, vendor_user, test_product, test_address):
        order = self.create_test_order(customer_user, vendor_user, test_product, test_address)
        
        response = client.post(f"/vendor/orders/{order['id']}/update-status",
            headers=vendor_user["headers"],
            json={
                "status": "shipped",
                "tracking_number": "TRACK123456"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "shipped"
        assert data["tracking_number"] == "TRACK123456"
    
    def test_vendor_stats(self, customer_user, vendor_user, test_product, test_address):
        order = self.create_test_order(customer_user, vendor_user, test_product, test_address)
        
        response = client.get("/vendor/stats", headers=vendor_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert data["total_orders"] >= 1
        assert float(data["total_revenue"]) >= 29.99

class TestPayoutSystem:
    """Test automated payout system"""
    
    def test_list_vendor_payouts(self, vendor_user):
        response = client.get("/vendor/payouts", headers=vendor_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_process_payouts_admin(self, admin_user):
        response = client.post("/admin/process-payouts", headers=admin_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

class TestAdminFunctionality:
    """Test administrator platform monitoring"""
    
    def test_admin_metrics(self, admin_user):
        response = client.get("/admin/metrics", headers=admin_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert "total_orders" in data
        assert "total_revenue" in data
        assert "active_vendors" in data
        assert "active_customers" in data
    
    def test_list_all_users(self, admin_user, customer_user, vendor_user):
        response = client.get("/admin/users", headers=admin_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert len(data["users"]) >= 3  # admin, customer, vendor
    
    def test_update_user_role(self, admin_user, customer_user):
        response = client.post(f"/admin/users/{customer_user['email']}/update-role",
            headers=admin_user["headers"],
            json="vendor"
        )
        assert response.status_code == 200
        data = response.json()
        assert "updated" in data["message"]
    
    def test_list_all_orders(self, admin_user):
        response = client.get("/admin/orders", headers=admin_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"

# Integration tests
class TestIntegrationFlow:
    """Test complete e-commerce flow"""
    
    def test_complete_purchase_flow(self, clean_files):
        # 1. Register users
        customer_response = client.post("/register", json={
            "email": "customer@integration.com",
            "password": "testpass123",
            "role": "customer"
        })
        assert customer_response.status_code == 200
        
        vendor_response = client.post("/register", json={
            "email": "vendor@integration.com",
            "password": "testpass123",
            "role": "vendor"
        })
        assert vendor_response.status_code == 200
        
        # 2. Login users
        customer_login = client.post("/login", json={
            "email": "customer@integration.com",
            "password": "testpass123"
        })
        customer_token = customer_login.json()["access_token"]
        customer_headers = {"Authorization": f"Bearer {customer_token}"}
        
        vendor_login = client.post("/login", json={
            "email": "vendor@integration.com",
            "password": "testpass123"
        })
        vendor_token = vendor_login.json()["access_token"]
        vendor_headers = {"Authorization": f"Bearer {vendor_token}"}
        
        # 3. Vendor creates product
        product_response = client.post("/products",
            headers=vendor_headers,
            json={
                "name": "Integration Test Product",
                "description": "Product for integration testing",
                "price": "49.99",
                "inventory_count": 50,
                "category": "Integration"
            }
        )
        assert product_response.status_code == 200
        product = product_response.json()
        
        # 4. Customer creates address
        address_response = client.post("/addresses",
            headers=customer_headers,
            json={
                "street": "123 Integration Street",
                "city": "Test City",
                "state": "Test State",
                "postal_code": "12345",
                "country": "Test Country",
                "is_default": True
            }
        )
        assert address_response.status_code == 200
        address = address_response.json()
        
        # 5. Customer places order
        order_response = client.post("/checkout/process",
            headers=customer_headers,
            json={
                "cart_items": [{
                    "product_id": product["id"],
                    "quantity": 2,
                    "price": "49.99"
                }],
                "shipping_address_id": address["id"],
                "payment_info": {
                    "payment_method": "credit_card",
                    "token": "integration_test_token_12345",
                    "billing_address_id": address["id"]
                },
                "guest_checkout": False
            }
        )
        assert order_response.status_code == 200
        order = order_response.json()
        
        # 6. Vendor updates order status
        status_response = client.post(f"/vendor/orders/{order['id']}/update-status",
            headers=vendor_headers,
            json={
                "status": "shipped",
                "tracking_number": "INTEGRATION123"
            }
        )
        assert status_response.status_code == 200
        
        # 7. Verify final state
        final_order = client.get(f"/orders/{order['id']}", headers=customer_headers)
        assert final_order.status_code == 200
        assert final_order.json()["status"] == "shipped"
        assert final_order.json()["tracking_number"] == "INTEGRATION123"

if __name__ == "__main__":
    pytest.main(["-v", __file__])