from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Tuckerstriker12@localhost/fitnesscenter'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    name = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ('name', 'phone','id')

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

class Member(db.Model):
    __tablename__ = 'Members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15))

class WorkoutSession(db.Model):
    __tablename__ = 'Workoutsessions'
    session_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('Members.id'))
    member = db.relationship('Member', backref='workout_sessions')

class WorkoutSessionsSchema(ma.Schema):
    member_id = fields.Integer(required = True)
    date = fields.Date(required=True)
    time = fields.Time(required=True)
    description = fields.String(required=True)

    class Meta:
        fields = ('session_id', 'member_id', 'date', 'time', 'description')

workout_session_schema = WorkoutSessionsSchema()
workout_sessions_schema = WorkoutSessionsSchema(many=True)

#Task 2: Implementing CRUD Operations for Members Using ORM 

@app.route("/members", methods=['GET'])
def get_members():
    members = Member.query.all()
    return members_schema.jsonify(members)

@app.route("/members", methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_member = Member(name=member_data['name'], phone=member_data['phone'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'message':'New member has been added!'}), 201

@app.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    member = Member.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    member.name = member_data['name']
    member.phone = member_data['phone']
    db.session.commit()
    return jsonify({"message": 'The members details have been updated'})

@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message":"The specified member has been deleted"}), 200

#Task 3: Managing Workout Sessions with ORM

@app.route("/workoutsessions", methods=['POST'])
def add_workout():
    try:
        session_data = workout_session_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_session = WorkoutSession(
        member_id=session_data['member_id'], 
        date=session_data['date'],
        time = session_data['time'],
        description = session_data['description']
        )
    db.session.add(new_session)
    db.session.commit()
    return jsonify({'message':'New workout session has been added!'}), 201

@app.route("/workoutsessions/<int:session_id>", methods=['PUT'])
def update_workout(session_id):
    session = WorkoutSession.query.get_or_404(session_id)
    try:
        session_data = workout_session_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    session.member_id = session_data['member_id']
    session.date = session_data['date']
    session.time = session_data['time']
    session.description = session_data['description']
    db.session.commit()
    return jsonify({'message':'The workout session has been updated'})

@app.route("/workoutsessions/<int:session_id>", methods=['GET'])
def get_workout_session(session_id):
    session = WorkoutSession.query.get_or_404(session_id)
    return workout_session_schema.jsonify(session)

@app.route("/members/<int:member_id>/workout_sessions", methods=['GET'])
def get_member_workout_sessions(member_id):
    sessions = WorkoutSession.query.filter_by(member_id=member_id).all()
    return workout_sessions_schema.jsonify(sessions)



with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)