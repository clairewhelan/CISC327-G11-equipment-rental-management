from unittest.mock import patch

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

