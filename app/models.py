from datetime import date, datetime, timezone
import uuid
from . import db

# --- B2B CLIENT (TENANT) MODEL ---
class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False, unique=True)
    api_key = db.Column(db.String(128), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, company_name):
        self.company_name = company_name
        self.api_key = str(uuid.uuid4())

    def __repr__(self):
        return f'<Client {self.company_name}>'


# --- USER MODEL WITH UPDATED CONSTRAINTS ---
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)

    username = db.Column(db.String(80), nullable=False)
    contact_info = db.Column(db.String(120), nullable=False)

    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    weight_kg = db.Column(db.Float)
    height_cm = db.Column(db.Float)
    fitness_goals = db.Column(db.Text)
    workouts_per_week = db.Column(db.String(10))
    workout_duration = db.Column(db.Integer)
    disliked_foods = db.Column(db.Text)
    allergies = db.Column(db.Text)
    health_conditions = db.Column(db.Text)
    sleep_hours = db.Column(db.String(10))
    stress_level = db.Column(db.String(20))
    activity_level = db.Column(db.String(50))

    client = db.relationship('Client', backref=db.backref('users', lazy=True))
    membership = db.relationship('Membership', back_populates='user', uselist=False, cascade="all, delete-orphan")
    diet_logs = db.relationship('DietLog', backref='author', lazy=True, cascade="all, delete-orphan")
    workout_logs = db.relationship('WorkoutLog', backref='author', lazy=True, cascade="all, delete-orphan")
    weight_history = db.relationship('WeightEntry', backref='author', lazy=True, cascade="all, delete-orphan")
    measurement_logs = db.relationship('MeasurementLog', backref='author', lazy=True, cascade="all, delete-orphan")
    workout_plans = db.relationship('WorkoutPlan', backref='author', lazy=True, cascade="all, delete-orphan")
    achievements = db.relationship('Achievement', backref='author', lazy=True, cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint('username', 'client_id', name='_username_client_uc'),
        db.UniqueConstraint('contact_info', 'client_id', name='_contact_info_client_uc'),
    )


class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    start_date = db.Column(db.Date, default=date.today)
    end_date = db.Column(db.Date)
    plan = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    client = db.relationship('Client', backref=db.backref('memberships', lazy=True))
    user = db.relationship('User', back_populates='membership')


class DietLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    meal_name = db.Column(db.String(100), nullable=False)
    food_items = db.Column(db.Text)
    calories = db.Column(db.Integer)
    protein_g = db.Column(db.Float)
    carbs_g = db.Column(db.Float)
    fat_g = db.Column(db.Float)
    date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    client = db.relationship('Client', backref=db.backref('diet_logs', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'meal_name': self.meal_name,
            'food_items': self.food_items,
            'calories': self.calories,
            'protein_g': self.protein_g,
            'carbs_g': self.carbs_g,
            'fat_g': self.fat_g,
            'date': self.date.isoformat()
        }


class WorkoutLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    client = db.relationship('Client', backref=db.backref('workout_logs', lazy=True))
    exercises = db.relationship('ExerciseEntry', backref='workout_log', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'date': self.date.isoformat(),
            'exercises': [exercise.to_dict() for exercise in self.exercises]
        }


class ExerciseEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    workout_log_id = db.Column(db.Integer, db.ForeignKey('workout_log.id'), nullable=False)

    client = db.relationship('Client', backref=db.backref('exercise_entries', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sets': self.sets,
            'reps': self.reps,
            'weight': self.weight
        }


class WeightEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    client = db.relationship('Client', backref=db.backref('weight_entries', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'weight_kg': self.weight_kg,
            'date': self.date.isoformat()
        }


class MeasurementLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    waist_cm = db.Column(db.Float)
    chest_cm = db.Column(db.Float)
    arms_cm = db.Column(db.Float)
    hips_cm = db.Column(db.Float)
    date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    client = db.relationship('Client', backref=db.backref('measurement_logs', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'waist_cm': self.waist_cm,
            'chest_cm': self.chest_cm,
            'arms_cm': self.arms_cm,
            'hips_cm': self.hips_cm,
            'date': self.date.isoformat()
        }


class WorkoutPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    generated_plan = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    client = db.relationship('Client', backref=db.backref('workout_plans', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'generated_plan': self.generated_plan
        }


class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    unlocked_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    client = db.relationship('Client', backref=db.backref('achievements', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'unlocked_at': self.unlocked_at.isoformat()
        }
