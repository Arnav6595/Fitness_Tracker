from flask import Blueprint, request, jsonify, current_app, g
from app.models import db, User, DietLog
from app.services.diet_planner import DietPlannerService
from app.services.reporting_service import ReportingService
import google.generativeai as genai
from datetime import datetime
from pydantic import ValidationError
from app.schemas.diet_schemas import DietLogSchema, GenerateDietPlanSchema
from app.utils.decorators import require_api_key # 1. IMPORT THE DECORATOR

# Create a Blueprint for diet routes
diet_bp = Blueprint('diet_bp', __name__)

@diet_bp.route('/generate-plan', methods=['POST'])
@require_api_key # 2. PROTECT THE ROUTE
def generate_diet_plan():
    raw_data = request.get_json()
    try:
        data = GenerateDietPlanSchema(**raw_data)
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400
    
    # 3. VERIFY USER BELONGS TO THE AUTHENTICATED CLIENT
    user = User.query.filter_by(id=data.user_id, client_id=g.client.id).first_or_404(
        description="User not found or does not belong to this client."
    )
    
    try:
        gemini_api_key = current_app.config.get('GEMINI_API_KEY')
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not configured in .env file.")
        genai.configure(api_key=gemini_api_key)
    except Exception as e:
        return jsonify({"error": "API Key configuration error", "details": str(e)}), 500

    planner = DietPlannerService(user=user, form_data=data.dict())
    result = planner.generate_plan()

    if result.get("success"):
        return jsonify(result['plan']), 200
    else:
        return jsonify({"error": result.get("error")}), 500


@diet_bp.route('/log', methods=['POST'])
@require_api_key # 2. PROTECT THE ROUTE
def log_meal():
    raw_data = request.get_json()
    try:
        data = DietLogSchema(**raw_data)
    except ValidationError as e:
        return jsonify({"error": "Invalid input", "details": e.errors()}), 400
    
    # 3. VERIFY USER BELONGS TO THE AUTHENTICATED CLIENT
    user = User.query.filter_by(id=data.user_id, client_id=g.client.id).first_or_404(
        description="User not found or does not belong to this client."
    )
    
    try:
        macros = data.macros.model_dump() if data.macros else {}
        new_log = DietLog(
            client_id=g.client.id,
            user_id=user.id,  #<-- Use user_id directly
            meal_name=data.meal_name,
            food_items=data.food_items,
            calories=data.calories,
            protein_g=macros.get('protein_g'),
            carbs_g=macros.get('carbs_g'),
            fat_g=macros.get('fat_g')
        )
        db.session.add(new_log)
        db.session.commit()
        return jsonify({"message": "Meal logged successfully!", "log": new_log.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to log meal.", "details": str(e)}), 500


@diet_bp.route('/<int:user_id>/logs', methods=['GET'])
@require_api_key # 2. PROTECT THE ROUTE
def get_diet_logs(user_id):
    # 3. VERIFY USER BELONGS TO THE AUTHENTICATED CLIENT
    user = User.query.filter_by(id=user_id, client_id=g.client.id).first_or_404(
        description="User not found or does not belong to this client."
    )
    logs = DietLog.query.filter_by(user_id=user.id, client_id=g.client.id).order_by(DietLog.date.desc()).all()
    return jsonify([log.to_dict() for log in logs]), 200

@diet_bp.route('/<int:user_id>/weekly-summary', methods=['GET'])
@require_api_key # 2. PROTECT THE ROUTE
def get_diet_summary(user_id):
    # 3. VERIFY USER BELONGS TO THE AUTHENTICATED CLIENT
    User.query.filter_by(id=user_id, client_id=g.client.id).first_or_404(
        description="User not found or does not belong to this client."
    )
    try:
        # Note: The ReportingService might also need to be made client-aware in the future
        reporter = ReportingService(user_id)
        summary = reporter.get_weekly_diet_summary()
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({"error": "Failed to generate diet summary", "details": str(e)}), 500