# TESTS IF EQUIPMENT ENDPOINT EXISTS 

def test_list_equipment_returns_empty_list_initially(client):
    response = client.get("/equipment")
    assert response.status_code == 200
    assert response.get_json() == []

# TESTS ADDING NEW EQUIPMENT 

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

    # Duplicate equipment names should be rejected 
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

def test_deleting_equiping_that_dne(client):
    resp_delete = client.delete(f"/equipment/{999999}")
    assert resp_delete.status_code == 404

def test_delete_rented_equipment_returned(client):
    # Create equipment with 0 available units
        paylod_equipment = {
            "name": "Canoe",
            "category": "Boat",
        }
        equipment_resp = client.post("/equipment", json=paylod_equipment)
        assert equipment_resp.status_code == 201
        equipment_id = equipment_resp.get_json()["id"]
    
        # Create renter 
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
    }
    equipment_resp = client.post("/equipment", json=paylod_equipment)
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    # Create renter 
    payload_renter = {
        "name": "renter1",
        "email": "renter1@renter.com",
    }
    renter_resp = client.post("/renters", json=payload_renter)
    assert renter_resp.status_code == 201
    client_id = renter_resp.get_json()["id"]

    # Create rented 
    payload_rental = {
        "renter_id": client_id,
        "equipment_id": equipment_id,
    }
    rental_resp = client.post("/rentals", json=payload_rental)
    assert rental_resp.status_code == 201
    rental_id = rental_resp.get_json()["id"]

    # Attempt to delete equipment before rental is returned 
    deleted_resp = client.delete(f"/equipment/{equipment_id}")
    assert deleted_resp.status_code == 409

    # Verify if the equipment still exists 
    equipment_check = client.get(f"/equipment/{equipment_id}")
    assert equipment_check.status_code == 200
    assert equipment_check.get_json()["id"] == equipment_id

    # Verify if the rental record still exists 
    rental_check = client.get(f"/rentals")
    assert rental_check.status_code == 200
    assert len(rental_check.get_json()) == 1

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

# ------------------- RENTERS TEST -------------------------------

# TEST RENTERS ENDPOINT EXISTS 

def test_list_renturs_returns_empty_list_initially(client):
    response = client.get("/renters")
    assert response.status_code == 200
    assert response.get_json() == []

# TESTS ADDING RENTERS 

def test_add_and_list_new_renter(client): 
    payload = {
        "name": "test",
        "email": "test@gmail.com"
    }
    resp = client.post("/renters", json=payload)
    assert resp.status_code == 201
    renter_id = resp.get_json()["id"]

    resp_data = resp.get_json()
    
    assert resp_data["id"] == renter_id
    assert resp_data["name"] == "test"
    assert resp_data["email"] == "test@gmail.com"

def test_add_renter_w_existing_email(client):
    renter1_payload = {
        "name": "test",
        "email": "test@gmail.com"
    }
    renter1_resp = client.post("/renters", json=renter1_payload)
    assert renter1_resp.status_code == 201

    # Create second renter with the same email as renter1 
    renter2_payload = {
        "name": "John",
        "email": "test@gmail.com"
    }
    renter2_resp = client.post("/renters", json=renter2_payload)
    # Prevent renter from being made 
    assert renter2_resp.status_code == 409

def test_add_renter_w_non_email(client): 
    payload = {
        "name": "test",
        "email": "non-email"
    }
    renter1_resp = client.post("/renters", json=payload)
    assert renter1_resp.status_code == 400

# TESTS DELETING RENTERS

def test_delete_renter_and_check_list(client):
    add_payload = {
        "name": "test",
        "email": "test@gmail.com"
    }
    renter_resp = client.post("/renters", json=add_payload)
    assert renter_resp.status_code == 201
    renter_id = renter_resp.get_json()["id"]

    # delete renter 
    delete_resp = client.delete(f"/renters/{renter_id}")
    assert delete_resp.status_code == 204

    # Check if renter is deleted and no longer listed 
    renter_resp = client.get("/renters")
    renter_data = renter_resp.get_json()
    assert len(renter_data) == 0 

def test_delete_non_existent_renter(client):
    delete_resp = client.delete(f"/renters/{99999999}")
    assert delete_resp.status_code == 404

def test_delete_renter_that_has_returned_equipment(client):
    # Create equipment with 0 available units
    paylod_equipment = {
        "name": "Canoe",
        "category": "Boat",
    }
    equipment_resp = client.post("/equipment", json=paylod_equipment)
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    # Create renter
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

    # Delete renter
    resp_renter_delete = client.delete(f"/renters/{renter_id}")
    assert resp_renter_delete.status_code == 204

    # Verify if equipment no longer exists in list 
    list_resp = client.get("/renters")
    assert len(list_resp.get_json()) == 0

def test_delete_renter_that_has_not_returned_equipment(client):
    # Create equipment 
    paylod_equipment = {
        "name": "Canoe",
        "category": "Boat",
    }
    equipment_resp = client.post("/equipment", json=paylod_equipment)
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    # Create renter 
    payload_renter = {
        "name": "renter1",
        "email": "renter1@renter.com",
    }
    renter_resp = client.post("/renters", json=payload_renter)
    assert renter_resp.status_code == 201
    renter_id = renter_resp.get_json()["id"]

    # Create rented 
    payload_rental = {
        "renter_id": renter_id,
        "equipment_id": equipment_id,
    }
    rental_resp = client.post("/rentals", json=payload_rental)
    assert rental_resp.status_code == 201
    rental_id = rental_resp.get_json()["id"]

    # Attempt to delete renter before rental is returned 
    deleted_resp = client.delete(f"/renters/{renter_id}")
    assert deleted_resp.status_code == 409

    # Verify if the renter still exists 
    renter_check = client.get(f"/renters/{renter_id}")
    assert renter_check.status_code == 200
    assert renter_check.get_json()["id"] == renter_id

    # Verify if the rental record still exists 
    rental_check = client.get(f"/rentals")
    assert rental_check.status_code == 200
    assert len(rental_check.get_json()) == 1

# TESTS EDITING/UPDATING RENTERS 

def test_edit_existing_renter(client):
    payload = {
        "name": "test",
        "email": "test@gmail.com"
    }
    renter_resp = client.post("/renters", json=payload)
    assert renter_resp.status_code == 201
    renter_id = renter_resp.get_json()["id"]

    updated_payload = {
        "name": "John",
        "email": "john@gmail.com"
    }
    update_renter_resp = client.put(f"/renters/{renter_id}", json=updated_payload)
    assert update_renter_resp.status_code == 200

    renter_data = update_renter_resp.get_json()
    assert renter_data["id"] == renter_id
    assert renter_data["name"] == "John"
    assert renter_data["email"] == "john@gmail.com"

def test_edit_renter_that_dne(client):
    updated_payload = {
        "name": "John",
        "email": "john@gmail.com"
    }
    update_renter_resp = client.put(f"/renters/{9999999}", json=updated_payload)
    assert update_renter_resp.status_code == 404
   
def test_edit_renter_email_w_non_email(client):
    # Create renter with a valid email
    payload_renter = {
        "name": "test",
        "email": "test@gmail.com",
    }
    renter_resp = client.post("/renters", json=payload_renter)
    assert renter_resp.status_code == 201
    renter_id = renter_resp.get_json()["id"]

    # Attempt to update renter with an invalid email
    payload_update = {
        "email": "something",
    }
    update_resp = client.put(f"/renters/{renter_id}", json=payload_update)

    # Invalid email should be rejected
    assert update_resp.status_code == 400

    # Verify the original email remains unchanged
    renter_check = client.get(f"/renters/{renter_id}")
    assert renter_check.status_code == 200
    assert renter_check.get_json()["email"] == "renter1@example.com"

# TESTS LISTING RENTERS 

def list_renters(client):
    payload = {
        "name": "test",
        "email": "test@gmail.com"
    }
    resp = client.post("/renters", json=payload)
    assert resp.status_code == 201

    payload2 = {
        "name": "John",
        "email": "john@gmail.com"
    }
    resp2 = client.post("/renters", json=payload2)
    assert resp2.status_code == 201

    # Check if resp list is displaying new renters
    resp_list = client.post("/renter")
    assert resp_list.status_code == 201
    assert len(resp.get_json()) == 2
