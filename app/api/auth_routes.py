# app/api/auth_routes.py

from flask import Blueprint, request, jsonify, g
from app.models import db, User, Membership
from datetime import datetime
from pydantic import ValidationError
from app.schemas.user_schemas import UserRegistrationSchema
from app.utils.decorators import require_api_key # 1. IMPORT THE DECORATOR

# Create a Blueprint for authentication routes
auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
@require_api_key  # 2. APPLY THE DECORATOR TO PROTECT THE ROUTE
def register_user():
    """
    Endpoint to create a new user profile for the authenticated client.
    """
    raw_data = request.get_json()
    if not raw_data:
        return jsonify({"error": "Request body must be JSON."}), 400

    # Validate the incoming data using the Pydantic schema
    try:
        data = UserRegistrationSchema(**raw_data)
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400

    username = data.name.lower().replace(' ', '_')
    
    # 3. Check if user already exists FOR THIS SPECIFIC CLIENT
    if User.query.filter_by(username=username, client_id=g.client.id).first():
        return jsonify({"error": f"User with name '{data.name}' already exists for this client."}), 409

    # Use the clean, validated data to create the database objects
    try:
        new_user = User(
            # 4. ASSOCIATE THE NEW USER WITH THE AUTHENTICATED CLIENT
            client_id=g.client.id,
            username=username,
            name=data.name,
            age=data.age,
            gender=data.gender,
            contact_info=data.contact_info,
            weight_kg=data.weight_kg,
            height_cm=data.height_cm,
            fitness_goals=data.fitness_goals,
            workouts_per_week=data.workouts_per_week,
            workout_duration=data.workout_duration,
            disliked_foods=data.disliked_foods,
            allergies=data.allergies,
            health_conditions=data.health_conditions,
            sleep_hours=data.sleep_hours,
            stress_level=data.stress_level
        )

        if data.membership:
            new_membership = Membership(
                # 5. ASSOCIATE THE MEMBERSHIP WITH THE CLIENT
                client_id=g.client.id,
                plan=data.membership.plan,
                user=new_user
            )
            # Note: The membership will be added via the user relationship cascade

        db.session.add(new_user)
        db.session.commit()

        # The to_dict() method might need to be updated to handle new relationships
        return jsonify({
            "message": f"User '{new_user.name}' created successfully for client {g.client.company_name}!",
            "user_id": new_user.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create user.", "details": str(e)}), 500