from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://your_user:your_password@localhost:5432/your_db_name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

@app.route('/')
def index():
    return jsonify({"message": "Hello from Flask Backend!"})

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.name for user in users])

@app.route('/users', methods=['POST'])
def add_user():
    name = request.json.get('name')
    new_user = User(name=name)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": f"User {name} added successfully!"}), 201

if __name__ == '__main__':
    app.run(debug=True)
