from datetime import date, timedelta

from flask import Blueprint, jsonify, request

from app import store
from app.models.rental import Rental
from notification_service import send_notification

rentals_bp = Blueprint("rentals", __name__, url_prefix="/rentals")


@rentals_bp.route("", methods=["GET"])
def list_rentals():
    results = list(store.rentals.values())
    renter_id = request.args.get("renter_id", type=int)
    equipment_id = request.args.get("equipment_id", type=int)
    if renter_id is not None:
        results = [r for r in results if r.renter_id == renter_id]
    if equipment_id is not None:
        results = [r for r in results if r.equipment_id == equipment_id]
    return jsonify([r.to_dict() for r in results])


@rentals_bp.route("", methods=["POST"])
def checkout_equipment():
    data = request.get_json()
    item = store.equipment.get(data["equipment_id"])
    if item is None:
        return jsonify({"error": "Equipment not found"}), 404

    # check for renter
    renter_item = store.renters.get(data["renter_id"])
    if renter_item is None:
        return jsonify({"error": "Renter not found"}), 404

    # check available units
    if item.available_units <=0:
        return jsonify({"error": "No available units"}), 400

    # check valid due date
    due_date = Rental.default_due_date()
    if "due_date" in data:
        if date.fromisoformat(data["due_date"]) < date.today():
            return jsonify({"error": "Invalid due date"}), 400
        else:
            due_date = date.fromisoformat(data["due_date"])

    
    item.available_units -= 1

    # calculate default deposit amount based on deposit threshold
    default_deposit = 0.0
    deposit_threshold = store.deposit_threshold
    if float(item.price) > deposit_threshold:
        default_deposit = float(item.price)*0.05

    rental_id = store.next_id("rental")
    rental = Rental(
        id=rental_id,
        equipment_id=data["equipment_id"],
        renter_id=data["renter_id"],
        due_date=due_date,
        deposit_amount=data.get("deposit_amount", default_deposit),
    )
    store.rentals[rental_id] = rental
    
    # Send notification after checkout 
    message = f"Thank you for checking out {item.name}. Your scheduled return date is {rental.due_date}. We hope you enjoy the product."    
    subject = "Checkout Confirmation"
    renter = store.renters.get(data["renter_id"])

    if renter is None:
        return jsonify({"error": "No renter with that id found"}), 404
    
    notification_state = send_notification(renter.email, subject, message)
    if notification_state == False: 
        return jsonify({
            "error": "Rental was created successfully, but the notification failed to send.",
            "rental": rental.to_dict()
        }), 500    
    
    return jsonify(rental.to_dict()), 201


@rentals_bp.route("/<int:rental_id>/return", methods=["PUT"])
def return_equipment(rental_id):
    rental = store.rentals.get(rental_id)
    if rental is None:
        return jsonify({"error": "Rental not found"}), 404
    if rental.return_date is not None:
        return jsonify({"error": "Rental already returned"}), 400
    
    if request.is_json:
        data = request.get_json()
    else:
        data = {}   
         
    rental.return_date = date.today()
    item = store.equipment.get(rental.equipment_id)

    if item is not None:
        if data.get("damaged") is True:
            rental.unit_damaged = True
            item.damaged_units += 1
        else:
            item.available_units += 1

    return jsonify(rental.to_dict())


@rentals_bp.route("/<int:rental_id>/extend", methods=["PUT"])
def extend_rental(rental_id):
    """Extend a rental's due date by the given number of days."""
    rental = store.rentals.get(rental_id)
    if rental is None:
        return jsonify({"error": "Rental not found"}), 404
    if rental.return_date is not None:
        return jsonify({"error": "Rental already returned"}), 400

    data = request.get_json()
    days = data.get("days", 1)
    rental.due_date = rental.due_date + timedelta(days=days)
    return jsonify(rental.to_dict())


@rentals_bp.route("/<int:rental_id>/deposit/release", methods=["PUT"])
def release_deposit(rental_id):
    """Release the damage deposit hold for a returned rental."""

    rental = store.rentals.get(rental_id)
    if rental is None:
        return jsonify({"error": "Rental not found"}), 404
    if rental.return_date is None:
        return jsonify({"error": "Equipment has not been returned yet"}), 400
    if rental.deposit_released == True:
        return jsonify({"error": "Deposit has already been released"}), 400

    rental.deposit_released = True
    return jsonify({"rental_id": rental_id, "deposit_released": True})

@rentals_bp.route("/deposit_threshold", methods=["GET"])
def get_deposit_threshold():
    price = store.deposit_threshold
    return jsonify({"deposit_threshold": price})

@rentals_bp.route("/deposit_threshold", methods=["PUT"])
def update_deposit_threshold():
    price = request.get_json()["price"]
    if price is None:
        return jsonify({"error": "Price not given"}), 404
    if type(price) != float:
        return jsonify({"error": "Price invalid"}), 404
    if price < 0.0:
        return jsonify({"error": "Price cannot be negative"}), 400

    store.deposit_threshold = price
    return jsonify({"deposit_threshold": price})
