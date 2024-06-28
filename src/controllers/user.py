from connectors.mysql_connector import connection
from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from flask_login import login_user, logout_user, login_required
from models.user import User
from sqlalchemy.orm import sessionmaker

user_routes = Blueprint("user_routes", __name__)


@user_routes.route('/register', methods=['POST'])
def register_user():
    Session = sessionmaker(connection)
    s = Session()

    s.begin()
    try:
        NewUser = User(
            name=request.form['name'],
            email=request.form['email']
        )

        NewUser.set_password(request.form['password'])

        s.add(NewUser)
        s.commit()
    except Exception as e:
        s.rollback()
        return {"message": "Fail to Register"}, 500

    return {"message": "Register Success"}, 200


@user_routes.route('/login', methods=['POST'])
def check_login():
    Session = sessionmaker(connection)
    s = Session()

    s.begin()
    try:
        email = request.form['email']
        user = s.query(User).filter(User.email == email).first()

        if user == None:
            return {"message": "User not found"}, 403

        if not user.check_password(request.form['password']):
            return {"message": "Invalid password"}, 403

        # Bisa diproses untuk login
        login_user(user)

        # Get Session ID
        session_id = request.cookies.get('session')

        return {
            "session_id": session_id,
            "message": "Login Success"
        }, 200

    except Exception as e:
        s.rollback()
        return {"message": "Gagal login"}, 500


@user_routes.route('/loginjwt', methods=['POST'])
def check_login_jwt():
    Session = sessionmaker(connection)
    s = Session()

    s.begin()
    try:
        email = request.form['email']
        user = s.query(User).filter(User.email == email).first()

        if user == None:
            return {"message": "User not found"}, 403

        if not user.check_password(request.form['password']):
            return {"message": "Invalid password"}, 403

        access_token = create_access_token(identity=user.id, additional_claims={"name": user.name, "id": user.id})

        return {
            "access_token": access_token,
            "message": "Login Success"
        }, 200

    except Exception as e:
        s.rollback()
        return {"message": "Gagal login"}, 500


@user_routes.route('/logout', methods=['GET'])
@login_required
def user_logout():
    logout_user()
    return {"message": "Success logout"}
