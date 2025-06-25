from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import RequestEntityTooLarge
import re
from datetime import timedelta
import os
from dotenv import load_dotenv
import base64
from sqlalchemy.pool import NullPool

# Загрузка переменных окружения
load_dotenv()

# Инициализация приложения
app = Flask(__name__)

# Конфигурация
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pet_osow_user:2rvhAkqrVRTBDrXgVxtFnFCMRNU3TOdG@dpg-d1dktkre5dus73dm1edg-a.frankfurt-postgres.render.com/pet_osow'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'poolclass': NullPool,  # Отключаем пул соединений для SQLite
    'connect_args': {'timeout': 30}  # Увеличиваем таймаут
}
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB лимит

# Инициализация расширений
db = SQLAlchemy(app)
jwt = JWTManager(app)


class User(db.Model):
    __tablename__ = 'User'
    IdUser = db.Column(db.Integer, primary_key=True)
    Full_Name = db.Column(db.String(150), nullable=False)
    Email = db.Column(db.String(50), nullable=False, unique=True)
    Password = db.Column(db.String(255), nullable=False)
    Phone = db.Column(db.String(20))
    BirthDay = db.Column(db.String(10))  # Формат YYYY-MM-DD


class Pet(db.Model):
    __tablename__ = 'Pet'
    IdPet = db.Column(db.Integer, primary_key=True)
    NamePet = db.Column(db.String(100), nullable=False)
    Type = db.Column(db.String(50))
    Breed = db.Column(db.String(50))
    Gender = db.Column(db.String(10))
    BirthDay = db.Column(db.String(10))
    DateInfFamily = db.Column(db.String(10))
    Weight = db.Column(db.Float)
    Photo = db.Column(db.LargeBinary)
    Microchip = db.Column(db.String(3))
    Cataraton = db.Column(db.String(7))
    IdOwner = db.Column(db.Integer, db.ForeignKey('User.IdUser', ondelete='CASCADE'))

    def to_dict(self):
        return {
            'IdPet': self.IdPet,
            'NamePet': self.NamePet,
            'Type': self.Type,
            'Breed': self.Breed,
            'Gender': self.Gender,
            'BirthDay': self.BirthDay,
            'DateInfFamily': self.DateInfFamily,
            'Weight': self.Weight,
            'Microchip': self.Microchip,
            'Cataraton': self.Cataraton,
            'IdOwner': self.IdOwner
        }


# Создание таблиц
with app.app_context():
    db.create_all()


@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400

        app.logger.info(f"Incoming registration data: {data}")

        required_fields = ['Full_Name', 'Email', 'Password', 'Phone']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing required field: {field}'}), 400

        if not isinstance(data['Email'], str) or not re.match(r"[^@]+@[^@]+\.[^@]+", data['Email']):
            return jsonify({'message': 'Invalid email format'}), 400

        if not isinstance(data['Phone'], str) or not re.match(r"^\+?[0-9]{10,15}$", data['Phone']):
            return jsonify({'message': 'Invalid phone format'}), 400

        if User.query.filter_by(Email=data['Email']).first():
            return jsonify({'message': 'User already exists'}), 400

        hashed_password = generate_password_hash(data['Password'])
        new_user = User(
            Full_Name=data['Full_Name'],
            Email=data['Email'],
            Password=hashed_password,
            Phone=data['Phone'],
            BirthDay=data.get('BirthDay')
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully'}), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'message': 'Registration failed. Please try again.'}), 500


@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400

        if 'Email' not in data or 'Password' not in data:
            return jsonify({'message': 'Email and password are required'}), 400

        user = db.session.query(User).filter_by(Email=data['Email']).first()
        if not user or not check_password_hash(user.Password, data['Password']):
            return jsonify({'message': 'Invalid credentials'}), 401

        access_token = create_access_token(identity=user.IdUser)
        refresh_token = create_refresh_token(identity=user.IdUser)

        return jsonify({
            'accessToken': access_token,
            'refreshToken': refresh_token,
            'userId': user.IdUser
        }), 200

    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({'message': 'Login failed. Please try again.'}), 500


@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user)
        return jsonify({'accessToken': new_token}), 200
    except Exception as e:
        app.logger.error(f"Refresh token error: {str(e)}")
        return jsonify({'message': 'Failed to refresh token'}), 500


@app.route('/pets', methods=['GET'])
@jwt_required()
def get_pets():
    try:
        current_user_id = get_jwt_identity()
        pets = db.session.query(Pet).filter_by(IdOwner=current_user_id).all()

        pets_list = []
        for pet in pets:
            pet_data = pet.to_dict()
            if pet.Photo:
                pet_data['Photo'] = base64.b64encode(pet.Photo).decode('utf-8')
            pets_list.append(pet_data)

        return jsonify({'pets': pets_list}), 200
    except Exception as e:
        app.logger.error(f"Get pets error: {str(e)}")
        return jsonify({'message': 'Failed to get pets'}), 500


@app.route('/pets/<int:petId>', methods=['GET'])
@jwt_required()
def get_pet(petId):
    try:
        current_user_id = get_jwt_identity()
        pet = db.session.query(Pet).filter_by(IdPet=petId, IdOwner=current_user_id).first()

        if not pet:
            return jsonify({'message': 'Pet not found or not owned by user'}), 404

        pet_data = pet.to_dict()
        if pet.Photo:
            pet_data['Photo'] = base64.b64encode(pet.Photo).decode('utf-8')

        return jsonify(pet_data), 200
    except Exception as e:
        app.logger.error(f"Get pet error: {str(e)}")
        return jsonify({'message': 'Failed to get pet'}), 500


@app.route('/pets', methods=['POST'])
@jwt_required()
def add_pet():
    try:
        current_user_id = get_jwt_identity()

        # Проверяем Content-Type
        if not request.content_type.startswith('multipart/form-data'):
            return jsonify({'message': 'Content-Type must be multipart/form-data'}), 400

        # Получаем данные из формы
        name = request.form.get('NamePet')  # Исправлено на NamePet
        type_ = request.form.get('Type')
        breed = request.form.get('Breed')
        gender = request.form.get('Gender')
        birth_day = request.form.get('BirthDay')
        date_inf_family = request.form.get('DateInfFamily')
        weight = request.form.get('Weight')
        microchip = request.form.get('Microchip')
        castration = request.form.get('Cataraton')

        # Обработка фото
        photo_data = None
        if 'photo' in request.files:
            photo_file = request.files['photo']
            if photo_file.filename != '':
                photo_data = photo_file.read()
                if len(photo_data) > 2 * 1024 * 1024:  # 2MB
                    return jsonify({'message': 'Image too large, max 2MB allowed'}), 400
        else:
            # Обработка application/json
            data = request.get_json()
            if not data:
                return jsonify({'message': 'No data provided'}), 400

            name = data.get('NamePet')
            type_ = data.get('Type')
            breed = data.get('Breed')
            gender = data.get('Gender')
            birth_day = data.get('BirthDay')
            date_inf_family = data.get('DateInfFamily')
            weight = data.get('Weight')
            microchip = data.get('Microchip')
            castration = data.get('Cataraton')

            photo_data = None
            if 'Photo' in data and data['Photo']:
                try:
                    photo_data = base64.b64decode(data['Photo'])
                    if len(photo_data) > 2 * 1024 * 1024:
                        return jsonify({'message': 'Image too large, max 2MB allowed'}), 400
                except Exception:
                    return jsonify({'message': 'Invalid photo format'}), 400

        # Валидация обязательных полей
        required_fields = {
            'NamePet': name,
            'Type': type_,
            'Gender': gender,
            'BirthDay': birth_day,
            'DateInfFamily': date_inf_family
        }

        for field, value in required_fields.items():
            if not value:
                return jsonify({'message': f'Missing required field: {field}'}), 400

        # Валидация формата дат
        date_fields = {'BirthDay': birth_day, 'DateInfFamily': date_inf_family}
        for field, value in date_fields.items():
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                return jsonify({'message': f'Invalid date format for {field}. Use YYYY-MM-DD'}), 400

        new_pet = Pet(
            NamePet=name,
            Type=type_,
            Breed=breed or '',
            Gender=gender,
            BirthDay=birth_day,
            DateInfFamily=date_inf_family,
            Weight=float(weight) if weight else None,
            Photo=photo_data,
            Microchip=microchip or 'Нет',
            Cataraton=castration or 'Нет',
            IdOwner=current_user_id
        )

        db.session.add(new_pet)
        db.session.commit()

        return jsonify({
            'message': 'Pet added successfully',
            'pet': new_pet.to_dict()
        }), 201

    except RequestEntityTooLarge:
        return jsonify({'message': 'Request data too large (max 16MB)'}), 413
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Add pet error: {str(e)}")
        return jsonify({'message': 'Failed to add pet'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
