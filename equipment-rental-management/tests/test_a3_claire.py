from app import store
from unittest.mock import patch
import pytest

# ----------------------------- Notification View Tests ----------------------------------

# COVERAGE TESTS
# ----------------------------- Renter Tests ----------------------------------
def test_get_nonexistant_renter_fails(client):
    # check that there are currently no renters
    resp1 = client.get("renters")
    assert resp1.status_code == 200
    assert resp1.get_json() == []

    # check that attempt to get nonexistant renter fails
    resp2 = client.get(f"/renters/{1}")
    assert resp2.status_code == 404

# ----------------------------- Rental Tests ----------------------------------
def test_set_deposit_threshold_success_path(client):
    # check current price
    price_resp = client.get("/rentals/deposit_threshold")
    assert price_resp.status_code == 200
    
    curr_price = price_resp.get_json()["deposit_threshold"]
    new_price = abs(curr_price + 10.0)

    payload = {
        "price": new_price
    }
    resp = client.put("/rentals/deposit_threshold", json=payload)
    assert resp.status_code == 200
    assert resp.get_json()["deposit_threshold"] == new_price

# ----------------------------- Rentals Views Tests ----------------------------------
def test_post_and_get_rentals_view_success(client):
    # create renter and equipment
        
    renter_payload_1 = {
        "name": "renter1",
        "email": "renter1@renter.com",
    }
    renter_resp_1 = client.post("/renters", json=renter_payload_1)
    assert renter_resp_1.status_code == 201
    renter_id_1 = renter_resp_1.get_json()["id"]

    equipment_payload_1 = {
            "name": "item1",
            "category": "test",
            "total_units": 1,
            "is_available": True
        }
    equipment_resp_1 = client.post("/equipment", json=equipment_payload_1)
    assert equipment_resp_1.status_code == 201
    equipment_id_1 = equipment_resp_1.get_json()["id"]

    # create rental 1
    payload_1 = {
        "renter_id": renter_id_1,
        "equipment_id": equipment_id_1,
    }
    response_1 = client.post("/ui/rentals", data=payload_1)
    assert response_1.status_code == 302
    
    get_response = client.get("/ui/rentals")
    assert get_response.status_code == 200
    assert b"1" in get_response.data
    assert len(store.rentals) == 1

def test_checkout_view_fails_if_equipment_dne(client):
    # create renter    
    renter_payload = {
        "name": "renter1",
        "email": "renter1@renter.com",
    }
    renter_resp = client.post("/renters", json=renter_payload)
    assert renter_resp.status_code == 201
    renter_id = renter_resp.get_json()["id"]

    
    # try to create rental with nonexistant equipment
    payload_1 = {
        "renter_id": renter_id,
        "equipment_id": 1,
    }
    response_1 = client.post("/ui/rentals", data=payload_1)
    assert response_1.status_code == 302
    assert len(store.rentals) == 0

def test_checkout_view_fails_if_renter_dne(client):
    # create renter    
    equipment_payload = {
        "name": "item1",
        "category": "test",
        "total_units": 1,
        "is_available": True
    }
    equipment_resp = client.post("/equipment", json=equipment_payload)
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    
    # try to create rental with nonexistant equipment
    payload_1 = {
        "renter_id": 1,
        "equipment_id": equipment_id,
    }
    response_1 = client.post("/ui/rentals", data=payload_1)
    assert response_1.status_code == 302
    assert len(store.rentals) == 0

# ----------------------------- Return Views Tests ----------------------------------

def test_return_view_success_undamaged(client):
    # create renter and equipment
    
    renter_payload = {
        "name": "renter",
        "email": "renter@renter.com",
    }
    renter_resp = client.post("/renters", json=renter_payload)
    assert renter_resp.status_code == 201
    renter_id = renter_resp.get_json()["id"]

    equipment_payload = {
            "name": "item",
            "category": "test",
            "total_units": 1,
            "is_available": True
        }
    equipment_resp = client.post("/equipment", json=equipment_payload)
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    # create rental

    rental_response = client.post(
        "/rentals",
        json={
            "renter_id": renter_id,
            "equipment_id": equipment_id,
        },
    )
    assert rental_response.status_code == 201
    rental_id = rental_response.get_json()["id"]

    # check rental has updated availability 
    og_availability_resp = client.get(f"/equipment/{equipment_id}/availability")
    og_availability = og_availability_resp.get_json()["available_units"]
    assert og_availability == 0

    return_data = {
        "damaged": "false"
    }
    return_resp = client.post(f"/ui/rentals/{rental_id}/return", data=return_data)
    assert return_resp.status_code == 302

    rental = store.rentals.get(rental_id)
    equipment = store.equipment.get(equipment_id)
    assert rental.unit_damaged == False
    assert equipment.available_units == 1
    assert equipment.damaged_units == 0

def test_return_view_success_damaged(client):
    # create renter and equipment
    
    renter_payload = {
        "name": "renter",
        "email": "renter@renter.com",
    }
    renter_resp = client.post("/renters", json=renter_payload)
    assert renter_resp.status_code == 201
    renter_id = renter_resp.get_json()["id"]

    equipment_payload = {
            "name": "item",
            "category": "test",
            "total_units": 1,
            "is_available": True
        }
    equipment_resp = client.post("/equipment", json=equipment_payload)
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    # create rental

    rental_response = client.post(
        "/rentals",
        json={
            "renter_id": renter_id,
            "equipment_id": equipment_id,
        },
    )
    assert rental_response.status_code == 201
    rental_id = rental_response.get_json()["id"]

    # check rental has updated availability 
    og_availability_resp = client.get(f"/equipment/{equipment_id}/availability")
    og_availability = og_availability_resp.get_json()["available_units"]
    assert og_availability == 0

    return_data = {
        "damaged": "true"
    }
    return_resp = client.post(f"/ui/rentals/{rental_id}/return", data=return_data)
    assert return_resp.status_code == 302
    
    rental = store.rentals.get(rental_id)
    equipment = store.equipment.get(equipment_id)
    assert rental.unit_damaged == True
    assert equipment.available_units == 0
    assert equipment.damaged_units == 1

def test_return_view_does_nothing_when_rental_dne(client):
    assert store.rentals.get(1) == None

    return_data = {
        "damaged": "false"
    }
    return_resp = client.post(f"/ui/rentals/{1}/return", data=return_data)
    assert return_resp.status_code == 302
    assert store.rentals.get(1) == None

def test_return_view_does_nothing_when_rental_already_returned(client):
    # create renter and equipment
    
    renter_payload = {
        "name": "renter",
        "email": "renter@renter.com",
    }
    renter_resp = client.post("/renters", json=renter_payload)
    assert renter_resp.status_code == 201
    renter_id = renter_resp.get_json()["id"]

    equipment_payload = {
            "name": "item",
            "category": "test",
            "total_units": 1,
            "is_available": True
        }
    equipment_resp = client.post("/equipment", json=equipment_payload)
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    # create rental

    rental_response = client.post(
        "/rentals",
        json={
            "renter_id": renter_id,
            "equipment_id": equipment_id,
        },
    )
    assert rental_response.status_code == 201
    rental_id = rental_response.get_json()["id"]

    # check rental has updated availability 
    og_availability_resp = client.get(f"/equipment/{equipment_id}/availability")
    og_availability = og_availability_resp.get_json()["available_units"]
    assert og_availability == 0

    # return once
    return_data_1 = {
        "damaged": "false"
    }
    return_resp_1 = client.post(f"/ui/rentals/{rental_id}/return", data=return_data_1)
    assert return_resp_1.status_code == 302
    rental_1 = store.rentals.get(rental_id)
    equipment_1 = store.equipment.get(equipment_id)
    assert rental_1.unit_damaged == False
    assert equipment_1.available_units == 1
    assert equipment_1.damaged_units == 0

    # attempt second return
    return_data = {
        "damaged": "false"
    }
    return_resp = client.post(f"/ui/rentals/{rental_id}/return", data=return_data)
    assert return_resp.status_code == 302
    rental_2 = store.rentals.get(rental_id)
    equipment_2 = store.equipment.get(equipment_id)
    assert rental_2.unit_damaged == False
    assert equipment_2.available_units == 1
    assert equipment_2.damaged_units == 0

def test_delete_renter(client):
    renter_payload = {
        "name": "renter",
        "email": "renter@renter.com",
    }
    renter_resp = client.post("/renters", json=renter_payload)
    assert renter_resp.status_code == 201
    renter_id = renter_resp.get_json()["id"]

    delete_resp = client.post(f"/ui/renters/{renter_id}/delete")
    assert delete_resp.status_code == 302
    assert store.renters.get(renter_id) == None

# ----------------------------- Equipment Views Tests ----------------------------------

def test_equipment_page_create(client):
    payload = {
        "name": "Canoe",
        "category": "Boat",
        "total_units": 10,
        "price": 50.0
    }
    equipment_resp = client.post("ui/equipment", data=payload)
    assert equipment_resp.status_code == 302

    # Verify if renter has been created
    equipment_id = max(store.equipment.keys())
    item = store.equipment[equipment_id]
    assert item.name == "Canoe"
    assert item.category == "Boat"
    assert item.total_units == 10
    assert item.price == '50.0'

def test_equipment_view_get(client):
    payload = {
        "name": "Canoe",
        "category": "Boat",
        "total_units": 10,
        "price": 50.0
    }
    equipment_resp = client.post("ui/equipment", data=payload)
    assert equipment_resp.status_code == 302


    # Verify if correct renter was collected
    get_equipment_resp = client.get("/ui/equipment")
    assert get_equipment_resp.status_code == 200
    assert b"Canoe" in get_equipment_resp.data
    assert b"Boat" in get_equipment_resp.data
    assert b"10" in get_equipment_resp.data
    assert b"50.0" in get_equipment_resp.data
