from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from Models import User, db
from datetime import timedelta

def register_user(email, password, full_name):
    if User.query.filter_by(Email=email).first():
        return None  # Пользователь уже существует

    hashed_password = generate_password_hash(password)
    new_user = User(
        Email=email,
        Password=hashed_password,
        Full_Name=full_name
    )

    db.session.add(new_user)
    db.session.commit()
    return new_user

def authenticate_user(email, password):
    user = User.query.filter_by(Email=email).first()
    if user and check_password_hash(user.Password, password):
        access_token = create_access_token(
            identity=user.IdUser,
            expires_delta=timedelta(hours=1)
        )
        return access_token
    return None
