# TESTS ADDING NEW EQUIPMENT 

# Input Tests 

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

# TESTS DELETING EQUIPMENT 

def test_delete_equipment(client):
    paylod = {
        "name": "Canoe",
        "category": "Boat",
        "total_units": 1,
        "available_units": 1,
        "is_available": True,
    }
    equipment_resp = client.post("/equipment", json=paylod)
    assert equipment_resp.status_code == 201

    resp_id = equipment_resp.get_json()["id"]

    # Delete equipment 
    resp_delete = client.delete(f"/equipment/{resp_id}")
    assert resp_delete.status_code == 204

    # Verify if equipment no longer exists in list 
    list_resp = client.get("/equipment")
    assert len(list_resp.get_json()) == 0

def test_delete_rented_equipment_returned(client):
    # Create equipment with 0 available units
        paylod_equipment = {
            "name": "Canoe",
            "category": "Boat",
            "available_units": 0,
            "is_available": False
        }
        equipment_resp = client.post("/equipment", json=paylod_equipment)
        assert equipment_resp.status_code == 201
        equipment_id = equipment_resp.get_json()["id"]
    
        # Create client 
        payload_renter = {
            "name": "renter1",
            "email": "renter1@renter.com",
        }
        renter_resp = client.post("/renters", json=payload_renter)
        assert renter_resp.status_code == 201
        renter_id = renter_resp.get_json()["id"]
    
        # Create rented
        payload_rented = {
            "renter_id": renter_id,
            "equipment_id": equipment_id,
        }
        rented_resp = client.post("/rentals", json=payload_rented)
        assert rented_resp.status_code == 201
        rented_id = rented_resp.get_json()["id"]

        # return equipment 
        rented_return_resp = client.put(f"/rentals/{rented_id}/return")
        assert rented_return_resp.status_code == 200

        # Delete equipment
        resp_equipment_delete = client.delete(f"/equipment/{equipment_id}")
        assert resp_equipment_delete.status_code == 204

        # Verify if equipment no longer exists in list 
        list_resp = client.get("/equipment")
        assert len(list_resp.get_json()) == 0

def test_delete_rented_equipment_not_returned(client):
    # Create equipment 
    paylod_equipment = {
        "name": "Canoe",
        "category": "Boat",
        "available_units": 0,
        "is_available": False
    }
    equipment_resp = client.post("/equipment", json=paylod_equipment)
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    # Create client 
    payload_client = {
        "name": "renter1",
        "email": "renter1@renter.com",
    }
    client_resp = client.post("/renters", json=payload_client)
    assert client_resp.status_code == 201
    client_id = client_resp.get_json()["id"]

    # Create rented 
    payload_rental = {
        "renter_id": client_id,
        "equipment_id": equipment_id,
    }
    rental_resp = client.post("/rentals", json=payload_rental)
    assert rental_resp.status_code == 201
    rental_id = rental_resp.get_json()["id"]

    # Attempt to delete equipment before rental is returned 
    deeted_resp = client.delete(f"/equipment/{equipment_id}")
    assert deeted_resp.status_code == 409

    # Verify if the equipment still exists 
    equipment_check = client.get(f"/equipment/{equipment_id}")
    assert equipment_check.status_code == 200
    assert equipment_check.get_json()["id"] == equipment_id

    # Verify if the rental record still exists 
    rental_check = client.get(f"/rentals/{rental_id}")
    assert rental_check.status_code == 200
    assert rental_check.get_json()["id"] == rental_id

# TESTS EQUIPMENT LISTING

def test_creating_and_listing_multiple_equipment(client):
    payload1 = {
        "name": "Canoe",
        "category": "Boat",
        "total_units": 1,
    }
    resp1 = client.post("/equipment", json=payload1)
    assert resp1.status_code == 201
    canoe_id = resp1.get_json()["id"]

    payload2 = {
        "name": "Tent",
        "category": "Camping",
        "total_units": 2,
    }
    resp2 = client.post("/equipment", json=payload2)
    assert resp2.status_code == 201
    tent_id = resp2.get_json()["id"]

    list_resp = client.get("/equipment")
    assert list_resp.status_code == 200

    equipment_list = list_resp.get_json()
    equipment_ids = [item["id"] for item in equipment_list]

    assert canoe_id in equipment_ids
    assert tent_id in equipment_ids
    assert len(equipment_list) == 2
    
def test_create_equipment_and_check_availability(client):
    payload = {
        "name": "Canoe",
        "category": "Boat",
        "total_units": 3,
    }
    create_resp = client.post("/equipment", json=payload)
    assert create_resp.status_code == 201
    equipment_id = create_resp.get_json()["id"]

    avail_resp = client.get(f"/equipment/{equipment_id}/availability")
    assert avail_resp.status_code == 200
    data = avail_resp.get_json()
    assert data["available_units"] == 3
    assert data["is_available"] is True

# TESTS EDITING/UPDATING EQUIPMENT 

def test_create_and_update_equipment(client): 
    payload = {
        "name": "Canoe",
        "category": "Boat",
    }
    create_resp = client.post("/equipment", json=payload)
    assert create_resp.status_code == 201
    equipment_id = create_resp.get_json()["id"]

    # veryify data exists 
    equipment_data = create_resp.get_json()
    assert equipment_data["id"] == equipment_id
    assert equipment_data["name"] == "Canoe"
    assert equipment_data["category"] == "Boat"

    # Update equipment 
    update_payload = {
        "name": "Tent",
        "category": "Outdoor Equipment",
        "total_units": 10
    }
    update_resp = client.put(f"/equipment/{equipment_id}", json=update_payload)
    assert update_resp.status_code == 200

    # Test if data has been updated 
    update_data = update_resp.get_json()
    assert update_data["id"] == equipment_id
    assert update_data["name"] == "Tent"
    assert update_data["category"] == "Outdoor Equipment"
    assert update_data["total_units"] == 10

def test_updating_equipment_that_dne(client):
    # Create payload
    update_payload = {
        "name": "Tent",
        "category": "Outdoor Equipment",
        "total_units": 10
    }
    # Attempt to update non-existent equipment 
    update_resp = client.put(f"/equipment/{999999}", json=update_payload)
    assert update_resp.status_code == 404

# TESTS UPDATING EQUIPMENT STATUS

def test_changing_equipment_status(client):
    payload = {
        "name": "Canoe",
        "category": "Boat",
    }
    create_resp = client.post("/equipment", json=payload)
    assert create_resp.status_code == 201
    equipment_id = create_resp.get_json()["id"]

    # Update stsatus of equipment from true to false 
    equipment_status_rest = client.patch(f"/equipment/{equipment_id}/status", json={"is_available": False})
    assert equipment_status_rest.status_code == 200

    # Check if updatad 
    status_data = equipment_status_rest.get_json()
    assert status_data["id"] == equipment_id
    assert status_data["name"] == "Canoe"
    assert status_data["category"] == "Boat"
    assert status_data["is_available"] == False

def test_changing_equipment_status_for_equipment_that_dne(client):
    # Attempt to change the status of non-existent equipment 
    update_resp = client.patch(f"/equipment/{999999}/status", json={"is_available": False})
    assert update_resp.status_code == 404