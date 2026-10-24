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

# #R6
# def test_checkout_returns_expected_fields():
#     #assert that ids are right and that rental_date is today, due date is null
#     print()

# #R3

# def test_checkout_updates_equipment_availability():
#     print()

# #R5

# def test_checkout_requires_availability():
#     #is_available flag & available units > 0
#     print()



