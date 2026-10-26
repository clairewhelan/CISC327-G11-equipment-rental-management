from datetime import date, timedelta

# TESTS FOR RENTAL LISTING/LOOKUP

def test_list_rentals_returns_empty_list_initially(client):
    response = client.get("/rentals")
    assert response.status_code == 200
    assert response.get_json() == []

def test_list_rentals_returns_all_rentals_wo_filtering(client):
    
    # create renter and equipment for rental 1
    
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
    response_1 = client.post("/rentals", json=payload_1)
    assert response_1.status_code == 201


    # create 2d renter and 2d equipment for rental 2
        
    renter_payload_2 = {
        "name": "renter2",
        "email": "renter2@renter.com",
    }
    renter_resp_2 = client.post("/renters", json=renter_payload_2)
    assert renter_resp_2.status_code == 201
    renter_id_2 = renter_resp_2.get_json()["id"]

    equipment_payload_2 = {
            "name": "item2",
            "category": "test",
            "total_units": 1,
            "is_available": True
        }
    equipment_resp_2 = client.post("/equipment", json=equipment_payload_2)
    assert equipment_resp_2.status_code == 201
    equipment_id_2 = equipment_resp_2.get_json()["id"]

    # create rental 2
    payload_2 = {
        "renter_id": renter_id_2,
        "equipment_id": equipment_id_2,
    }
    response_2 = client.post("/rentals", json=payload_2)
    assert response_2.status_code == 201

    # assert that rentals returns 2 rentals
    response = client.get("/rentals")
    assert response.status_code == 200
    assert len(response.get_json()) == 2

def test_list_returns_empty_list_if_filtered_equipment_dne(client):
    
    # create renter & equipment
    renter_payload = {
        "name": "renter",
        "email": "renter@renter.com",
    }
    renter_resp = client.post("/renters", json=renter_payload)
    assert renter_resp.status_code == 201
    renter_id = renter_resp.get_json()["id"]

    equipment_payload = {
            "name": "item1",
            "category": "test",
            "total_units": 1,
            "is_available": True
        }
    equipment_resp = client.post("/equipment", json=equipment_payload)
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    # create rental 1
    payload = {
        "renter_id": renter_id,
        "equipment_id": equipment_id,
    }
    response = client.post("/rentals", json=payload)
    assert response.status_code == 201

    # check that filtering on nonexistant equipment returns nothing
    response = client.get(f"/rentals?equipment_id={equipment_id+1}")
    assert response.status_code == 200
    assert response.get_json() == []

def test_list_returns_empty_list_if_filtered_renter_dne(client):
    
    # create renter & equipment

    renter_payload = {
        "name": "renter",
        "email": "renter@renter.com",
    }
    renter_resp = client.post("/renters", json=renter_payload)
    assert renter_resp.status_code == 201
    renter_id = renter_resp.get_json()["id"]

    equipment_payload = {
            "name": "item1",
            "category": "test",
            "total_units": 1,
            "is_available": True
        }
    equipment_resp = client.post("/equipment", json=equipment_payload)
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    # create rental 1
    payload = {
        "renter_id": renter_id,
        "equipment_id": equipment_id,
    }
    response = client.post("/rentals", json=payload)
    assert response.status_code == 201

    # check that filtering on nonexistant equipment returns nothing
    response = client.get(f"/rentals?renter_id={renter_id+1}")
    assert response.status_code == 200
    assert response.get_json() == []

def test_rentals_filters_by_equipment(client):
    
    # create renter
    renter_payload = {
        "name": "renter",
        "email": "renter@renter.com",
    }
    renter_resp = client.post("/renters", json=renter_payload)
    assert renter_resp.status_code == 201
    renter_id = renter_resp.get_json()["id"]

    # create 2 different equipments

    equipment_payload_1 = {
                "name": "item1",
                "category": "test",
                "total_units": 1,
                "is_available": True
            }
    equipment_resp_1 = client.post("/equipment", json=equipment_payload_1)
    assert equipment_resp_1.status_code == 201
    equipment_id_1 = equipment_resp_1.get_json()["id"]

    equipment_payload_2 = {
            "name": "item2",
            "category": "test",
            "total_units": 1,
            "is_available": True
        }
    equipment_resp_2 = client.post("/equipment", json=equipment_payload_2)
    assert equipment_resp_2.status_code == 201
    equipment_id_2 = equipment_resp_2.get_json()["id"]

    # create 2 rentals checking out different equipment

    # create rental 1
    payload_1 = {
        "renter_id": renter_id,
        "equipment_id": equipment_id_1,
    }
    response_1 = client.post("/rentals", json=payload_1)
    assert response_1.status_code == 201

    # create rental 2
    payload_2 = {
        "renter_id": renter_id,
        "equipment_id": equipment_id_2,
    }
    response_2 = client.post("/rentals", json=payload_2)
    assert response_2.status_code == 201

    # check that rentals filtered on equipment_id_1 only returns 1 rental
    response = client.get(f"/rentals?equipment_id={equipment_id_1}")
    assert response.status_code == 200
    assert len(response.get_json()) == 1
    
def test_rentals_filters_by_renter(client):
    # create equipment
    equipment_payload = {
            "name": "item",
            "category": "test",
            "total_units": 1,
            "is_available": True
        }
    equipment_resp = client.post("/equipment", json=equipment_payload)
    assert equipment_resp.status_code == 201
    equipment_id = equipment_resp.get_json()["id"]

    # create renters 1 & 2
    
    renter_payload_1 = {
        "name": "renter",
        "email": "renter@renter.com",
    }
    renter_resp_1 = client.post("/renters", json=renter_payload_1)
    assert renter_resp_1.status_code == 201
    renter_id_1 = renter_resp_1.get_json()["id"]

    renter_payload_2 = {
        "name": "renter",
        "email": "renter@renter.com",
    }
    renter_resp_2 = client.post("/renters", json=renter_payload_2)
    assert renter_resp_2.status_code == 201
    renter_id_2 = renter_resp_2.get_json()["id"]

    # create rentals 1 & 2
    payload_1 = {
        "renter_id": renter_id_1,
        "equipment_id": equipment_id,
    }
    response_1 = client.post("/rentals", json=payload_1)
    assert response_1.status_code == 201

    payload_2 = {
        "renter_id": renter_id_2,
        "equipment_id": equipment_id,
    }
    response_2 = client.post("/rentals", json=payload_2)
    assert response_2.status_code == 201

    # check that rentals filtered on renter_id_1 only returns 1 rental
    response = client.get(f"/rentals?renter_id={renter_id_1}")
    assert response.status_code == 200
    assert len(response.get_json()) == 1


# TESTS FOR CHECKOUT

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

def test_checkout_fails_if_due_date_lt_curr_date(client):
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
        "due_date": date.today() - timedelta(days=1)
    }
    response = client.post("/rentals", json=payload)
    assert response.status_code == 400

def test_checkout_returns_expected_fields(client):
    
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
        "deposit_amount": 100.0,
        "due_date": date.today() + timedelta(days=1)
    }
    response = client.post("/rentals", json=payload)
    assert response.status_code == 201

    # get rental
    rental_response = client.get(f"/rentals?renter_id={renter_id}&equipment_id={equipment_id}")
    assert rental_response.status_code == 200

    # check expected fields
    data = rental_response.get_json()[0]
    assert data["renter_id"] == renter_id
    assert data["equipment_id"] == equipment_id
    assert data["rental_date"] == date.today().strftime('%Y-%m-%d')
    assert data["due_date"] == (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    assert data["return_date"] == None
    assert data["deposit_amount"] == 100.0
    assert data["deposit_released"] == False

def test_checkout_updates_availability(client):

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
        "deposit_amount": 100.0,
        "due_date": date.today() + timedelta(days=1)
    }
    response = client.post("/rentals", json=payload)
    assert response.status_code == 201

    # check updated availaility
    check_equipment = client.get(f"/equipment/{equipment_id}/availability")
    assert check_equipment.status_code == 200
    equip_data = check_equipment.get_json()
    assert equip_data["available_units"] == 0


# TESTS FOR RETURNING EQUIPMENT

def test_return_fails_without_rental_id(client):
    response = client.put("/rentals/return")
    assert response.status_code == 404

def test_return_fails_if_rental_does_not_exist(client):
    response = client.put("/rentals/1/return")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Rental not found"}

def test_return_fails_if_rental_has_already_been_returned(client):
    
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

    # attempt to return rental twice

    first_return = client.put(f"/rentals/{rental_id}/return")
    assert first_return.status_code == 200

    second_return = client.put(f"/rentals/{rental_id}/return")
    assert second_return.status_code == 400
    assert second_return.get_json() == {"error": "Rental already returned"}

def test_return_updates_return_date(client):
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

    # return rental & check return date
    response = client.put(f"/rentals/{rental_id}/return")
    assert response.status_code == 200
    assert response.get_json()["return_date"] == date.today().isoformat()

def test_return_increments_available_units_by_one(client):
    
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

    # return rental & check return date
    response = client.put(f"/rentals/{rental_id}/return")
    assert response.status_code == 200

    # check return has updated availability
    new_availability_resp = client.get(f"/equipment/{equipment_id}/availability")
    new_availability = new_availability_resp.get_json()["available_units"]
    assert new_availability == 1


# TESTS FOR EXTENDING A RENTAL

def test_extending_rental_fails_without_rental_id(client):
    response = client.put("/rentals/extend")
    assert response.status_code == 404

def test_extending_rental_fails_if_rental_dne(client):
    response = client.put("/rentals/1/extend")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Rental not found"}

def test_extending_rental_fails_if_equipment_already_returned(client):
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

    # return rental

    rental_return = client.put(f"/rentals/{rental_id}/return")
    assert rental_return.status_code == 200

    # attempt to extend rental

    response = client.put(f"/rentals/{rental_id}/extend")
    assert response.status_code == 400
    assert response.get_json() == {"error": "Rental already returned"}

def test_extending_rental_updates_due_date(client):
    
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
    og_rental_due_date = rental_response.get_json()["due_date"]

    # extend rental

    rental_extend = client.put(f"/rentals/{rental_id}/extend", json={"days": 2})
    assert rental_extend.status_code == 200

    # check rental due date
    response = client.get(f"/rentals?renter_id={renter_id}&equipment_id={equipment_id}")
    assert response.status_code == 200
    due_date = response.get_json()[0]["due_date"]
    expected_due_date = date.fromisoformat(og_rental_due_date) + timedelta(days=2)
    assert date.fromisoformat(due_date) == expected_due_date


# TESTS FOR RELEASING A RENTAL DEPOSIT

def test_release_fails_without_rental_id(client):
    response = client.put("/rentals/deposit/release")
    assert response.status_code == 404

# TODO: test release fails if provided rental dne
def test_release_fails_if_rental_dne(client):
    response = client.put("/rentals/1/deposit/release")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Rental not found"}

# TODO: test release fails if rental has not been returned yet
def test_release_fails_if_rental_not_returned(client):
    
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
            "deposit_amount": 100.0
        },
    )
    assert rental_response.status_code == 201
    rental_id = rental_response.get_json()["id"]

    # try to release deposit despite not having returned rental

    response = client.put(f"/rentals/{rental_id}/deposit/release")
    assert response.status_code == 400
    assert response.get_json() == {"error": "Equipment has not been returned yet"}

# TODO: test release updates
def test_release_updates_flag_in_rental_obj(client):
    
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
            "deposit_amount": 100.0
        },
    )
    assert rental_response.status_code == 201
    rental_id = rental_response.get_json()["id"]

    # return rental
    rental_return = client.put(f"/rentals/{rental_id}/return")
    assert rental_return.status_code == 200

    # check that deposit_released on rental object is now True
    response = client.get(f"/rentals?renter_id={renter_id}&equipment_id={equipment_id}")
    assert response.status_code == 200
    deposit_released = response.get_json()[0]["deposit_released"]
    assert deposit_released == True


