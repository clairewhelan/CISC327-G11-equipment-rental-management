def test_list_equipment_returns_empty_list_initially(client):
    response = client.get("/equipment")
    assert response.status_code == 200
    assert response.get_json() == []

def test_create_equipment_and_check_created(client): 
    payload = {
        "name": "Canoe",
        "category": "Boat",
        "total_units": 1,
        "available_units": 1,
        "is_available": True,
    }

    create_resp = client.post("/equipment", json=payload)
    assert create_resp.status_code == 201
    equipment_id = create_resp.get_json()["id"]

    avail_resp = client.get(f"/equipment/{equipment_id}")
    assert avail_resp.status_code == 200
    data = avail_resp.get_json()

    assert data["category"] == "Boat"
    assert data["name"] == "Canoe"
    assert data["total_units"] == 1
    assert data["available_units"] == 1
    assert data["is_available"] == True


def test_equipment_input_if_equipment_name_exists(client):
    # Create the first canoe
    payload = {
        "name": "Canoe",
        "category": "Boat",
        "total_units": 1,
        "available_units": 1,
        "is_available": True,
    }

    canoe1_create_resp = client.post("/equipment", json=payload)
    assert canoe1_create_resp.status_code == 201

    # Attempt to create another canoe with the same name
    duplicate_payload = {
        "name": "Canoe",
        "category": "Boat",
        "total_units": 5,
        "available_units": 5,
        "is_available": True,
    }

    canoe2_create_resp = client.post("/equipment", json=duplicate_payload)

    # Duplicate equipment names should be rejected (even if lower or uppercase)
    assert canoe2_create_resp.status_code == 409

    # Verify the original canoe remains unchanged
    canoe1_id = canoe1_create_resp.get_json()["id"]
    canoe1_resp = client.get(f"/equipment/{canoe1_id}")

    assert canoe1_resp.status_code == 200

    canoe1_data = canoe1_resp.get_json()
    assert canoe1_data["name"] == "Canoe"
    assert canoe1_data["total_units"] == 1
    assert canoe1_data["available_units"] == 1
    assert canoe1_data["is_available"] is True


def test_equipment_input_if_name_differs_by_case(client):
    payload1 = {
        "name": "Canoe",
        "category": "Boat",
        "total_units": 1,
        "available_units": 1,
        "is_available": True,
    }

    resp1 = client.post("/equipment", json=payload1)
    assert resp1.status_code == 201

    # Second payload with different capitalization 
    payload2 = {
        "name": "canoe",
        "category": "Boat",
        "total_units": 1,
        "available_units": 1,
        "is_available": True,
    }

    resp2 = client.post("/equipment", json=payload2)
    assert resp2.status_code == 409