from app import store
from unittest.mock import patch
import pytest

# ----------------------------- Notification View Tests ----------------------------------

def test_checkout_notification_view_success_stub(client, monkeypatch):
    """A stub test to see if the email from views.py was successfully sent"""
    monkeypatch.setattr(
        "app.routes.views.send_notification",
        lambda recipient, subject, message: True
    )

    # Create renter
    renter_payload = {
        "name": "John",
        "email": "John@gmail.com"
    }
    renter_resp = client.post("/ui/renters", data=renter_payload)
    assert renter_resp.status_code == 302

    # Create equipment
    equipment_payload = {
        "name": "Canoe",
        "category": "Boat",
        "total_units": 10,
        "price": 0
    }
    equipment_resp = client.post("/ui/equipment", data=equipment_payload)
    assert equipment_resp.status_code == 302

    renter_id = max(store.renters.keys())
    equipment_id = max(store.equipment.keys())

    # Checkout equipment
    rental_payload = {
        "equipment_id": equipment_id,
        "renter_id": renter_id
    }

    rental_resp = client.post("/ui/rentals", data=rental_payload)

    assert rental_resp.status_code == 302
    assert store.equipment[equipment_id].available_units == 9
    assert len(store.rentals) == 1


def test_checkout_notification_view_success_mock(client):
    """A mock test to see if the contents of the email from views.py are correctly sent"""
    # Create renter
    renter_payload = {
        "name": "John",
        "email": "John@gmail.com"
    }
    renter_resp = client.post("/ui/renters", data=renter_payload)
    assert renter_resp.status_code == 302

    # Create equipment
    equipment_payload = {
        "name": "Canoe",
        "category": "Boat",
        "total_units": 10,
        "price": 100
    }
    equipment_resp = client.post("/ui/equipment", data=equipment_payload)
    assert equipment_resp.status_code == 302

    # Get renter and equipment
    renter = list(store.renters.values())[0]
    equipment = list(store.equipment.values())[0]

    with patch("app.routes.views.send_notification", return_value=True) as mock_send:

        # Checkout equipment
        rental_payload = {
            "equipment_id": equipment.id,
            "renter_id": renter.id
        }

        rental_resp = client.post("/ui/rentals", data=rental_payload)

        assert rental_resp.status_code == 302

        # Email message
        message = (
            f"Thank you for checking out {equipment.name}. "
            f"Your scheduled return date is {list(store.rentals.values())[0].due_date}. "
            "We hope you enjoy the product."
        )

        mock_send.assert_called_once_with(
            renter.email,
            "Checkout Confirmation",
            message
        )
    

# ----------------------------- Notification Tests ----------------------------------

def test_checkout_notification_success_stub(client, monkeypatch):
    """A stub test to see if the email from the endpoint checkout_equipment in rentals.py was successfully sent"""
    monkeypatch.setattr(
        "app.routes.rentals.send_notification",
        lambda recipient, subject, message: True
    )

    # Create renter
    renter_payload = {
        "name": "John",
        "email": "John@gmail.com"
    }
    renter_resp = client.post("/renters", json=renter_payload)
    assert renter_resp.status_code == 201

    # Create equipment
    equipment_payload = {
        "name": "Canoe",
        "category": "Boat",
        "total_units": 10
    }
    equipment_resp = client.post("/equipment", json=equipment_payload)
    assert equipment_resp.status_code == 201

    renter_id = renter_resp.get_json()["id"]
    equipment_id = equipment_resp.get_json()["id"]

    # Checkout equipment
    rental_payload = {
        "equipment_id": equipment_id,
        "renter_id": renter_id
    }

    rental_resp = client.post("/rentals", json=rental_payload)

    assert rental_resp.status_code == 201

    # Check if rental was created 
    rental_check = client.get(f"/rentals")
    assert rental_check.status_code == 200
    assert len(rental_check.get_json()) == 1 
    
def test_checkout_notification_success_mock(client):
    """A mock test to see if the contents of the email from checkout_equipment in rentals.py are correctly sent"""
    # Create renter
    renter_payload = {
        "name": "John",
        "email": "John@gmail.com"
    }
    renter_resp = client.post("/renters", json=renter_payload)
    assert renter_resp.status_code == 201

    # Create equipment
    equipment_payload = {
        "name": "Canoe",
        "category": "Boat",
        "total_units": 10
    }
    equipment_resp = client.post("/equipment", json=equipment_payload)
    assert equipment_resp.status_code == 201

    renter_id = renter_resp.get_json()["id"]
    renter_email = renter_resp.get_json()["email"]
    equipment_id = equipment_resp.get_json()["id"]
    equipment_name = equipment_resp.get_json()["name"]

    with patch("app.routes.rentals.send_notification", return_value=True) as mock_send:
        # Checkout equipment
        rental_payload = {
            "equipment_id": equipment_id,
            "renter_id": renter_id
        }
        rental_resp = client.post("/rentals", json=rental_payload)
        assert rental_resp.status_code == 201

        # Verify the rental was recorded correctly 
        rental_check = client.get(f"/rentals")
        assert rental_check.status_code == 200
        assert len(rental_check.get_json()) == 1 

        # Prepare email 
        rental_return_date = rental_resp.get_json()["due_date"]
        message = f"Thank you for checking out {equipment_name}. Your scheduled return date is {rental_return_date}. We hope you enjoy the product."

        # Send mock email
        mock_send.assert_called_once_with(renter_email, "Checkout Confirmation", message)

# COVERAGE TESTS 
# ----------------------------- EQUIPMENT ----------------------------------

def test_get_equipment_availability_that_dne(client):    
    availability_resp = client.get("/equipment/9999/availability")
    assert availability_resp.status_code == 404
    assert availability_resp.get_json() == {"error": "Equipment not found"}

def test_get_equipment_that_dne(client):
    availability_resp = client.get("/equipment/9999")
    assert availability_resp.status_code == 404
    assert availability_resp.get_json() == {"error": "Equipment not found"}

def test_create_then_update_equipment_with_negative_valuess(client):
    payload = {
        "name": "Canoe",
        "category": "Boat",
        "total_units": 10
    }
    equipment_resp = client.post(f"/equipment", json=payload)
    equipment_id = equipment_resp.get_json()["id"]
    assert equipment_resp.status_code == 201

    # Create updated payload
    update_payload = {
        "damaged_units": -11,
    }
    update_resp = client.put(f"/equipment/{equipment_id}", json=update_payload)
    data = equipment_resp.get_json()
    assert update_resp.status_code == 400

    # Check if data has changed at all. 
    data = equipment_resp.get_json()
    assert data["name"] == "Canoe"
    assert data["category"] == "Boat"
    assert data["damaged_units"] == 0

# ----------------------------- Equipment Views ----------------------------------

def test_edit_equipment_page(client):
    payload = {
        "name": "Canoe",
        "category": "Boat",
        "total_units": 10
    }
    equipment_resp = client.post(f"/equipment", json=payload)
    equipment_id = equipment_resp.get_json()["id"]
    assert equipment_resp.status_code == 201

    updated_payload = {
        "name": "Kayak",
        "category": "Sport Boat",
        "total_units": 15
    }

    update_resp = client.post(f"/ui/equipment/{equipment_id}/edit", data=updated_payload)
    assert update_resp.status_code == 302

    item = store.equipment[equipment_id]
    assert item.name == "Kayak"
    assert item.category == "Sport Boat"
    assert item.total_units == 15

def test_edit_equipment_that_dne(client):
    updated_payload = {
        "name": "Kayak",
        "category": "Sport Boat",
        "total_units": 15
    }    
    update_resp = client.post(f"/ui/equipment/9999/edit", data=updated_payload)
    assert update_resp.status_code == 302
    assert update_resp.location.endswith("/ui/equipment")    

def test_equipment_page_create_then_update_equipment_with_negative_valuess(client):
    payload = {
        "name": "Canoe",
        "category": "Boat",
        "total_units": 10
    }
    equipment_resp = client.post(f"/equipment", json=payload)
    equipment_id = equipment_resp.get_json()["id"]
    assert equipment_resp.status_code == 201

    # Create updated payload
    updated_payload = {
        "name": "Kayak",
        "category": "Sport Boat",
        "total_units": -10
    }
    update_resp = client.post(f"/ui/equipment/{equipment_id}/edit", data=updated_payload)
    assert update_resp.status_code == 302
    assert update_resp.location.endswith("/ui/equipment")    

    # Check if values havae not chanaged 
    item = store.equipment[equipment_id]
    assert item.name == "Canoe"
    assert item.category == "Boat"
    assert item.total_units == 10

def test_equipment_page_when_there_are_more_damaged_plus_available_units_than_total(client):
    payload = {
        "name": "Canoe",
        "category": "Boat",
        "total_units": 10
    }
    equipment_resp = client.post(f"/equipment", json=payload)
    equipment_id = equipment_resp.get_json()["id"]
    assert equipment_resp.status_code == 201

    # create updated payload
    updated_payload = {
        "damaged_units": 5,
        "available_units": 6 
    }
    update_resp = client.post(f"/ui/equipment/{equipment_id}/edit", data=updated_payload)
    assert update_resp.status_code == 302
    assert update_resp.location.endswith("/ui/equipment")    

    # Check if values havae not chanaged 
    item = store.equipment[equipment_id]
    assert item.name == "Canoe"
    assert item.category == "Boat"
    assert item.total_units == 10

def test_delete_equipment_page(client):
    payload = {
        "name": "Canoe",
        "category": "Boat",
        "total_units": 10
    }
    equipment_resp = client.post(f"/equipment", json=payload)
    equipment_id = equipment_resp.get_json()["id"]
    assert equipment_resp.status_code == 201

    # Delete equipment
    update_resp = client.post(f"/ui/equipment/{equipment_id}/delete")
    assert update_resp.status_code == 302
    assert update_resp.location.endswith("/ui/equipment")    

    # verify list is deleted
    list_resp = client.get("/equipment")
    assert len(list_resp.get_json()) == 0

def test_delete_equipment_page_that_dne(client):
    update_resp = client.post(f"/ui/equipment/9999/delete")
    assert update_resp.status_code == 302
    assert update_resp.location.endswith("/ui/equipment")    

# ----------------------------- Renter Views ----------------------------------

def test_renters_page_create_client(client):
    payload = {
        "name": "John",
        "email": "John@gmail.com"
    }
    renter_resp = client.post("ui/renters", data=payload)
    assert renter_resp.location.endswith("/ui/renters")

    # Verify if renter has been created
    renter_id = max(store.renters.keys())
    item = store.renters[renter_id]
    assert item.name == "John"
    assert item.email == "John@gmail.com"

@pytest.mark.xfail(reason="Currently no email verification: would require a new library import")
def test_renters_page_client_with_invalid_email(client):
    payload = {
        "name": "John",
        "email": "test_case"
    }
    renter_resp = client.post("/ui/renters", data=payload)

    assert renter_resp.status_code == 302
    assert len(store.renters) == 0 

def test_renters_page_get_client(client):
    payload = {
        "name": "John",
        "email": "John@gmail.com"
    }
    renter_resp = client.post("ui/renters", data=payload)
    assert renter_resp.location.endswith("/ui/renters")
    assert renter_resp.status_code == 302

    # Verify if correct renter was collected
    get_renter_resp = client.get("/ui/renters")
    assert get_renter_resp.status_code == 200
    assert b"John" in get_renter_resp.data
    assert b"John@gmail.com" in get_renter_resp.data

def test_renters_page_get_renter_that_dne(client):
    # See if No invalid clients are taken
    get_renter_resp = client.get("/ui/renters")
    assert get_renter_resp.status_code == 200
    assert b"None" not in get_renter_resp.data


# ----------------------------- Deposit ----------------------------------
def test_update_deposit_threshold(client):
    payload = {
        "price": 250.00,
    }
    resp = client.put("/rentals/deposit_threshold", json=payload)
    assert resp.status_code == 200

    get_resp = client.get("/rentals/deposit_threshold")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["deposit_threshold"] == 250.00

# ----------------------------- Deposit Views ----------------------------------

def test_create_and_update_deposite_threshold_views(client):
    payload = {
        "price": 250.00
    }
    resp = client.post("/ui/rentals/deposit_threshold", data=payload)
    assert resp.status_code == 302
    assert store.deposit_threshold == 250.00

    updated_payload = {
        "price": 350.00
    }

    update_resp = client.post("/ui/rentals/deposit_threshold", data=updated_payload)
    assert update_resp.status_code == 302
    assert store.deposit_threshold == 350.00

def test_create_and_get_deposit_threshold_views(client):
    payload = {
        "price": 250.00
    }
    resp = client.post("/ui/rentals/deposit_threshold", data=payload)
    assert resp.status_code == 302
    assert store.deposit_threshold == 250.00

    get_resp = client.get("/ui/rentals/deposit_threshold")
    assert get_resp.status_code == 200
    assert b"250.0" in get_resp.data


    
