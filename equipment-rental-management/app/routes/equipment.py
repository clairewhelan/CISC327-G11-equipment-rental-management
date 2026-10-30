from flask import Blueprint, jsonify, request

from app import store
from app.models.equipment import Equipment

equipment_bp = Blueprint("equipment", __name__, url_prefix="/equipment")


@equipment_bp.route("", methods=["GET"])
def list_equipment():
    return jsonify([e.to_dict() for e in store.equipment.values()])


@equipment_bp.route("", methods=["POST"])
def create_equipment():
    data = request.get_json()
    equipment_id = store.next_id("equipment")
    item = Equipment(
        id=equipment_id,
        name=data["name"],
        category=data["category"],
        total_units=data.get("total_units", 1),
        available_units=data.get("total_units", 1),
        is_available=data.get("is_available", True),
        damaged_units=data.get("damaged_units", 0),
    )
    store.equipment[equipment_id] = item
    return jsonify(item.to_dict()), 201


@equipment_bp.route("/<int:equipment_id>", methods=["GET"])
def get_equipment(equipment_id):
    item = store.equipment.get(equipment_id)
    if item is None:
        return jsonify({"error": "Equipment not found"}), 404
    return jsonify(item.to_dict())


@equipment_bp.route("/<int:equipment_id>", methods=["PUT"])
def update_equipment(equipment_id):
    item = store.equipment.get(equipment_id)
    if item is None:
        return jsonify({"error": "Equipment not found"}), 404
    data = request.get_json()
    
    total_units = data.get("total_units", item.total_units)
    available_units = data.get("available_units", item.available_units)
    damaged_units = data.get("damaged_units", item.damaged_units)
    
    # Case where if user tries to input more damaged units then there are available units 
    if total_units < 0 or available_units < 0 or damaged_units < 0:
        return "There are more available or damaged units then there are total units", 400

    # Case if use tries to add more damaged units and available units then there are total units
    if damaged_units + available_units > total_units:
        return "There are more damaged and available units than total units", 400
    
    item.name = data.get("name", item.name)
    item.category = data.get("category", item.category)
    item.total_units = data.get("total_units", item.total_units)
    item.available_units = data.get("available_units", item.available_units)
    item.is_available = data.get("is_available", item.is_available)
    item.damaged_units = data.get("damaged_units", item.damaged_units)
    return jsonify(item.to_dict())


@equipment_bp.route("/<int:equipment_id>", methods=["DELETE"])
def delete_equipment(equipment_id):
    item = store.equipment.pop(equipment_id, None)
    if item is None:
        return jsonify({"error": "Equipment not found"}), 404
    return "", 204


@equipment_bp.route("/<int:equipment_id>/status", methods=["PATCH"])
def set_equipment_status(equipment_id):
    """Mark equipment as available or out-of-service (e.g. under repair).

    Set is_available=false to take a piece of equipment out of service.

    NOTE (intentional bug): checkout_equipment() in rentals.py does NOT check
    this flag. Out-of-service equipment can still be checked out — a test that
    marks equipment unavailable and then attempts a checkout will reveal this.

    NOTE (Brandon): this function has a secondary bug where if there is only 1 unit that is damaged, 
    setting this flag on will cause all available units to be considered damaged, regardles if only
    one unit is actually damaged. Because of this, a new implementation has been added in to instead 
    count the number of damaged units.
    """
    item = store.equipment.get(equipment_id)
    if item is None:
        return jsonify({"error": "Equipment not found"}), 404
    data = request.get_json()
    item.is_available = data["is_available"]
    return jsonify(item.to_dict())


@equipment_bp.route("/<int:equipment_id>/availability", methods=["GET"])
def get_availability(equipment_id):
    """Return availability summary for a single piece of equipment."""
    item = store.equipment.get(equipment_id)
    if item is None:
        return jsonify({"error": "Equipment not found"}), 404
    return jsonify({
        "equipment_id": item.id,
        "is_available": item.is_available,
        "available_units": item.available_units,
        "total_units": item.total_units,
    })
