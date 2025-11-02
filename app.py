from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "age": self.age,
            "grade": self.grade
        }

@app.route('/api/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify({
        "status": "success",
        "count": len(students),
        "data": [s.to_dict() for s in students]
    }), 200

@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"status": "error", "message": "Talaba topilmadi"}), 404
    return jsonify({"status": "success", "data": student.to_dict()}), 200

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json()
    required = ["firstname", "lastname", "age", "grade"]
    for f in required:
        if f not in data:
            return jsonify({"status": "error", "message": f"'{f}' maydoni kerak"}), 400
    student = Student(
        firstname=data["firstname"],
        lastname=data["lastname"],
        age=data["age"],
        grade=data["grade"]
    )
    db.session.add(student)
    db.session.commit()
    return jsonify({"status": "success", "message": "Yangi talaba qo‘shildi", "data": student.to_dict()}), 201

@app.route('/api/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.get_json()
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"status": "error", "message": "Talaba topilmadi"}), 404
    student.firstname = data.get("firstname", student.firstname)
    student.lastname = data.get("lastname", student.lastname)
    student.age = data.get("age", student.age)
    student.grade = data.get("grade", student.grade)
    db.session.commit()
    return jsonify({"status": "success", "message": "Yangilandi", "data": student.to_dict()}), 200

@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"status": "error", "message": "Talaba topilmadi"}), 404
    db.session.delete(student)
    db.session.commit()
    return jsonify({"status": "success", "message": f"Talaba {student_id} o‘chirildi"}), 200

@app.errorhandler(404)
def not_found(e):
    return make_response(jsonify({"status": "error", "message": "Sahifa topilmadi"}), 404)

@app.errorhandler(500)
def server_error(e):
    return make_response(jsonify({"status": "error", "message": "Serverda xatolik yuz berdi"}), 500)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

