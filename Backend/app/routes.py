from flask import current_app, Blueprint, request, jsonify
from app import db
from app.models import User, Meal, Menu, Order
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from utils.cloudinary import upload_image

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
customer_bp = Blueprint("customer", __name__, url_prefix="/customer")
### AUTHENTICATION ENDPOINTS ###

@auth_bp.route("/", methods=["GET"])
def home():
    return "Welcome to the Meal Booking System!"


@auth_bp.route("/register", methods=["POST"])
def register():
    db = current_app.extensions['sqlalchemy']
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "Customer")

    if not all([username, email, password]):
        return jsonify({"error": "All fields are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    hashed_password = generate_password_hash(password)
    user = User(username=username, email=email, password_hash=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({"message": f"Welcome back, {user.username}!", "role": user.role}), 200


### ADMIN ENDPOINTS ###
@admin_bp.route("/add_meal", methods=["POST"])
def add_meal():
    db = current_app.extensions["sqlalchemy"]
    data = request.form  # Use request.form to access form data (multipart/form-data)
    name = data.get("name")
    description = data.get("description", "")
    price = data.get("price")
    image_file = request.files.get("image_file")  # Get the image file from the request

    if not all([name, price]):
        return jsonify({"error": "Name and price are required"}), 400
    
    if not image_file:
        return jsonify({"error": "Image file is required"}), 400
    print("Image file:", image_file)
    image_url = upload_image(image_file)
    if not image_url:
        return jsonify({"error": "Failed to upload image"}), 500

    # Create a new meal entry
    meal = Meal(name=name, description=description, price=price, image_url=image_url)
    db.session.add(meal)
    db.session.commit()

    return jsonify({"message": "Meal added successfully", "meal": meal.name}), 201
@admin_bp.route("/set_menu", methods=["POST"])
def set_menu():
    db = current_app.extensions["sqlalchemy"]
    data = request.get_json()
    meal_ids = data.get("meal_ids")
    today = date.today()

    if Menu.query.filter_by(date=today).first():
        return jsonify({"error": "Menu for today already exists"}), 400

    if not meal_ids:
        return jsonify({"error": "At least one meal ID is required"}), 400

    for meal_id in meal_ids:
        menu = Menu(date=today, meal_id=meal_id)
        db.session.add(menu)

    db.session.commit()

    return jsonify({"message": "Menu set successfully for today"}), 201
@admin_bp.route("/view_orders", methods=["GET"])
def view_orders():
    orders = Order.query.all()
    result = [
        {
            "id": order.id,
            "user_id": order.user_id,
            "meal_id": order.meal_id,
            "status": order.status,
            "created_at": order.created_at,
        }
        for order in orders
    ]
    return jsonify(result), 200
@admin_bp.route("/update_order_status/<int:order_id>", methods=["PATCH"])
def update_order_status(order_id):
    db = current_app.extensions["sqlalchemy"]
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    status = data.get("status")

    if not status:
        return jsonify({"error": "Status is required"}), 400

    if status not in ["Pending", "Completed", "Cancelled"]:
        return jsonify({"error": "Invalid status"}), 400

    order.status = status
    db.session.commit()

    return jsonify({"message": f"Order status updated to {status}"}), 200
@admin_bp.route("/view_order/<int:order_id>", methods=["GET"])
def view_order(order_id):
    order = Order.query.get_or_404(order_id)
    result = {
        "id": order.id,
        "user_id": order.user_id,
        "meal_id": order.meal_id,
        "status": order.status,
        "created_at": order.created_at,
    }
    return jsonify(result), 200
@admin_bp.route("/delete_meal/<int:meal_id>", methods=["DELETE"])
def delete_meal(meal_id):
    db = current_app.extensions["sqlalchemy"]
    meal = Meal.query.get_or_404(meal_id)
    db.session.delete(meal)
    db.session.commit()

    return jsonify({"message": "Meal deleted successfully"}), 200
@admin_bp.route("/update_meal/<int:meal_id>", methods=["PATCH"])
def update_meal(meal_id):
    db = current_app.extensions["sqlalchemy"]
    meal = Meal.query.get_or_404(meal_id)
    data = request.get_json()

    meal.name = data.get("name", meal.name)
    meal.description = data.get("description", meal.description)
    meal.price = data.get("price", meal.price)
    meal.image_url = data.get("image_url", meal.image_url)

    db.session.commit()

    return jsonify({"message": "Meal updated successfully"}), 200



### CUSTOMER ENDPOINTS ###
@customer_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    
    if not all([username, email, password]):
        return jsonify({"error": "Username, email, and password are required"}), 400

    # Check if the email or username already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email is already registered"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username is already taken"}), 400

    # Use the default hashing method (pbkdf2:sha256)
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password_hash=hashed_password, role="customer")
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Customer created successfully"}), 201

@customer_bp.route("/profile/<int:user_id>", methods=["GET"])
def view_customer_profile(user_id):
    user = User.query.get(user_id)

    if user is None:
        return jsonify({"error": "User not found"}), 404

    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_verified": user.is_verified,
        "created_at": user.created_at
    }

    return jsonify(user_data), 200

@customer_bp.route("/menu", methods=["GET"])
def view_menu():
    today = date.today()
    menu_items = Menu.query.filter_by(date=today).all()
    result = [
        {"id": item.id, "meal_id": item.meal_id, "meal_name": Meal.query.get(item.meal_id).name}
        for item in menu_items
    ]
    return jsonify(result), 200


@customer_bp.route("/place_order", methods=["POST"])
def place_order():
    db = current_app.extensions["sqlalchemy"]
    data = request.get_json()
    user_id = data.get("user_id")
    meal_id = data.get("meal_id")

    if not all([user_id, meal_id]):
        return jsonify({"error": "User ID and Meal ID are required"}), 400

    order = Order(user_id=user_id, meal_id=meal_id)
    db.session.add(order)
    db.session.commit()

    return jsonify({"message": "Order placed successfully"}), 201


@customer_bp.route("/my_orders/<int:user_id>", methods=["GET"])
def my_orders(user_id):
    orders = Order.query.filter_by(user_id=user_id).all()
    result = [
        {
            "id": order.id,
            "meal_name": Meal.query.get(order.meal_id).name,
            "status": order.status,
            "created_at": order.created_at,
        }
        for order in orders
    ]
    return jsonify(result), 200
