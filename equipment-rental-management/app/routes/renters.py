from flask import Blueprint, jsonify, request

from app import store
from app.models.renter import Renter

renters_bp = Blueprint("renters", __name__, url_prefix="/renters")


@renters_bp.route("", methods=["GET"])
def list_renters():
    return jsonify([r.to_dict() for r in store.renters.values()])


@renters_bp.route("", methods=["POST"])
def create_renter():
    data = request.get_json()
    
    # check that there's no renter that already has given email
    has_unreturned_rental = any(
        renter.email.lower() == data["email"].lower()
        for renter in store.renters.values()
    )
    if has_unreturned_rental:
            return jsonify({"error": "Renter with that email already exists"}), 409

    renter_id = store.next_id("renter")
    renter = Renter(id=renter_id, name=data["name"], email=data["email"])
    store.renters[renter_id] = renter
    return jsonify(renter.to_dict()), 201


@renters_bp.route("/<int:renter_id>", methods=["GET"])
def get_renter(renter_id):
    renter = store.renters.get(renter_id)
    if renter is None:
        return jsonify({"error": "Renter not found"}), 404
    return jsonify(renter.to_dict())


@renters_bp.route("/<int:renter_id>", methods=["PUT"])
def update_renter(renter_id):
    renter = store.renters.get(renter_id)
    if renter is None:
        return jsonify({"error": "Renter not found"}), 404
    data = request.get_json()
    renter.name = data.get("name", renter.name)
    renter.email = data.get("email", renter.email)
    return jsonify(renter.to_dict())


@renters_bp.route("/<int:renter_id>", methods=["DELETE"])
def delete_renter(renter_id):
    # check that equipment is not associated with an unreturned rental
    has_unreturned_rental = any(
        rental.renter_id == renter_id and rental.return_date is None
        for rental in store.rentals.values()
    )
    if has_unreturned_rental:
            return jsonify({"error": "Renter associated with unreturned rental"}), 409


    renter = store.renters.pop(renter_id, None)
    if renter is None:
        return jsonify({"error": "Renter not found"}), 404
    return "", 204
