from datetime import date, timedelta

# TESTS FOR CHECKOUT

# Input tests

def test_checkout_fails_without_equipment_id(client):
    create_payload = {
        "name": "renter",
        "email": "renter@renter.com",
    }
    create_resp = client.post("/renters", json=create_payload)
    assert create_resp.status_code == 201
    assert type(create_resp.get_json()["id"]) is int

    # provide valid renter_id but not equipment_id
    payload = {
        "renter_id": create_resp.get_json()["id"],
        "equipment_id": None
    }
    response = client.post("/rentals", json=payload)
    assert response.status_code == 404

def test_checkout_fails_without_renter_id(client):
    create_payload = {
            "name": "item",
            "category": "test",
            "total_units": 1,
            "is_available": True
        }
    create_resp = client.post("/equipment", json=create_payload)
    assert create_resp.status_code == 201
    assert type(create_resp.get_json()["id"]) is int

    # provide valid equipment_id but not renter_id
    payload = {
        "renter_id": None,
        "equipment_id": create_resp.get_json()["id"]
    }
    response = client.post("/rentals", json=payload)
    assert response.status_code == 404

def test_checkout_fails_if_equipment_dne(client):
    create_payload = {
        "name": "renter",
        "email": "renter@renter.com",
    }
    create_resp = client.post("/renters", json=create_payload)
    assert create_resp.status_code == 201
    assert type(create_resp.get_json()["id"]) is int

    # confirm equipment of id 1 does not exist
    equipment_response = client.get("/equipment/{1}")
    assert equipment_response.status_code == 404

    # provide valid renter_id with nonexistant equipment_id
    payload = {
        "renter_id": create_resp.get_json()["id"],
        "equipment_id": 1
    }
    response = client.post("/rentals", json=payload)
    assert response.status_code == 404

def test_checkout_fails_if_renter_dne(client):
    create_payload = {
            "name": "item",
            "category": "test",
            "total_units": 1,
            "is_available": True
        }
    create_resp = client.post("/equipment", json=create_payload)
    assert create_resp.status_code == 201
    assert type(create_resp.get_json()["id"]) is int

    # confirm renter of id 1 does not exist
    renter_response = client.get("/renter/{1}")
    assert renter_response.status_code == 404

    # provide valid equipment_id but not renter_id
    payload = {
        "renter_id": 1,
        "equipment_id": create_resp.get_json()["id"]
    }
    response = client.post("/rentals", json=payload)
    assert response.status_code == 404

def test_checkout_fails_with_invalid_deposit_amount(client):
    
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
    payload = {
        "renter_id": renter_id,
        "equipment_id": equipment_id,
        "deposit_amount": -1.0
    }
    response = client.post("/rentals", json=payload)
    assert response.status_code == 404

# Other tests

def test_checkout_requires_is_available_true(client):
    
    # create renter and equipment with is_available=False
    
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
            "is_available": False
        }
    equipment_resp = client.post("/equipment", json=equipment_payload)
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    # try to create rental
    payload = {
        "renter_id": renter_id,
        "equipment_id": equipment_id,
    }
    response = client.post("/rentals", json=payload)
    assert response.status_code == 404

def test_checkout_requires_positive_available_units(client):
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

    # create rental 1
    payload_1 = {
        "renter_id": renter_id,
        "equipment_id": equipment_id,
    }
    response_1 = client.post("/rentals", json=payload_1)
    assert response_1.status_code == 201

    # check new availaility is 0
    check_equipment = client.get(f"/equipment/{equipment_id}/availability")
    assert check_equipment.status_code == 200
    equip_data = check_equipment.get_json()
    assert equip_data["available_units"] == 0

    # try to create rental 2 with same equipment
    payload_2 = {
        "renter_id": renter_id,
        "equipment_id": equipment_id,
    }
    response_1 = client.post("/rentals", json=payload_2)
    assert response_1.status_code == 404
    
def test_checkout_returns_expected_fields_and_updates_availability(client):
    
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
    payload = {
        "renter_id": renter_id,
        "equipment_id": equipment_id,
        "deposit_amount": 100.0
    }
    response = client.post("/rentals", json=payload)
    assert response.status_code == 201

    # check expected fields
    data = response.get_json()
    assert data["renter_id"] == renter_id
    assert data["equipment_id"] == equipment_id
    assert data["rental_date"] == date.today().strftime('%Y-%m-%d')
    assert data["return_date"] == None
    assert data["deposit_amount"] == 100.0
    assert data["deposit_released"] == False

    # check updated availaility
    check_equipment = client.get(f"/equipment/{equipment_id}/availability")
    assert check_equipment.status_code == 200
    equip_data = check_equipment.get_json()
    assert equip_data["available_units"] == 0

