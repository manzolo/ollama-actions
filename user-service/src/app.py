from flask import Flask, request, jsonify
import uuid
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
USER_SERVICE_PORT = int(os.environ.get("USER_SERVICE_PORT", 5001))

# In-memory database (simple dict)
users_db = {}

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "ok",
        "message": "User Service is running",
        "endpoints": {
            "GET /users": "List all users",
            "GET /users/<id>": "Get user by ID",
            "POST /users": "Create new user (JSON body with name, city, etc.)",
            "DELETE /users/<id>": "Delete user by ID"
        }
    }), 200

@app.route("/users", methods=["GET"])
def get_users():
    """List all users"""
    return jsonify({
        "status": "success",
        "count": len(users_db),
        "users": list(users_db.values())
    }), 200

@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    """Get a specific user by ID"""
    user = users_db.get(user_id)
    if not user:
        return jsonify({
            "status": "error",
            "message": f"User with ID {user_id} not found"
        }), 404

    return jsonify({
        "status": "success",
        "user": user
    }), 200

@app.route("/users", methods=["POST"])
def create_user():
    """Create a new user"""
    data = request.json

    if not data:
        return jsonify({
            "status": "error",
            "message": "No JSON data provided"
        }), 400

    # Generate unique ID
    user_id = str(uuid.uuid4())

    # Create user object
    user = {
        "id": user_id,
        "name": data.get("name"),
        "city": data.get("city"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "address": data.get("address"),
        "created_at": datetime.now().isoformat()
    }

    # Store in database
    users_db[user_id] = user

    return jsonify({
        "status": "success",
        "message": "User created successfully",
        "user": user
    }), 201

@app.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Delete a user by ID"""
    if user_id not in users_db:
        return jsonify({
            "status": "error",
            "message": f"User with ID {user_id} not found"
        }), 404

    deleted_user = users_db.pop(user_id)

    return jsonify({
        "status": "success",
        "message": "User deleted successfully",
        "user": deleted_user
    }), 200

@app.route("/users/<user_id>", methods=["PUT", "PATCH"])
def update_user(user_id):
    """Update a user by ID"""
    if user_id not in users_db:
        return jsonify({
            "status": "error",
            "message": f"User with ID {user_id} not found"
        }), 404

    data = request.json
    if not data:
        return jsonify({
            "status": "error",
            "message": "No JSON data provided"
        }), 400

    # Update user fields
    user = users_db[user_id]
    for key in ["name", "city", "email", "phone", "address"]:
        if key in data:
            user[key] = data[key]

    user["updated_at"] = datetime.now().isoformat()

    return jsonify({
        "status": "success",
        "message": "User updated successfully",
        "user": user
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=USER_SERVICE_PORT)
