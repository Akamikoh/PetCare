from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Gender(db.Model):
    __tablename__ = 'Gender'
    NameGender = db.Column(db.String(50), primary_key=True)

class Microchip(db.Model):
    __tablename__ = 'Microchip'
    NameAvailability = db.Column(db.String(50), primary_key=True)

class Castration(db.Model):
    __tablename__ = 'Castration'
    NameChoice = db.Column(db.String(50), primary_key=True)

class User(db.Model):
    __tablename__ = 'User'
    IdUser = db.Column(db.Integer, primary_key=True)
    Full_Name = db.Column(db.String(150), nullable=False)
    Email = db.Column(db.String(50), nullable=False, unique=True)
    Password = db.Column(db.String(255), nullable=False)
    Phone = db.Column(db.String(20))
    BirthDay = db.Column(db.String(10))  # TEXT в базе

class Pet(db.Model):
    __tablename__ = 'Pet'
    IdPet = db.Column(db.Integer, primary_key=True)
    NamePet = db.Column(db.String(100), nullable=False)
    Type = db.Column(db.String(50))
    Breed = db.Column(db.String(50))
    Gender = db.Column(db.String(50), db.ForeignKey('Gender.NameGender'))
    BirthDay = db.Column(db.String(10))  # TEXT в базе
    DateInfFamily = db.Column(db.String(10))  # TEXT в базе
    Weight = db.Column(db.Float)
    Photo = db.Column(db.LargeBinary)
    Microchip = db.Column(db.String(50), db.ForeignKey('Microchip.NameAvailability'))
    Cataraton = db.Column(db.String(50), db.ForeignKey('Castration.NameChoice'))
    IdOwner = db.Column(db.Integer, db.ForeignKey('User.IdUser', ondelete='CASCADE'))

class Clinics(db.Model):
    __tablename__ = 'Clinics'
    IdClinics = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(100), nullable=False)
    Address = db.Column(db.String(200))
    Phone = db.Column(db.String(20))
    WorkingHours = db.Column(db.String(50))

class PetStore(db.Model):
    __tablename__ = 'PetStore'
    IdPetStore = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(100), nullable=False)
    Address = db.Column(db.String(200))
    Phone = db.Column(db.String(20))
    WorkingHours = db.Column(db.String(50))

class Activities(db.Model):
    __tablename__ = 'Activities'
    IdActivities = db.Column(db.Integer, primary_key=True)
    IdPet = db.Column(db.Integer, db.ForeignKey('Pet.IdPet', ondelete='CASCADE'), nullable=False)
    RecordingDate = db.Column(db.String(10), nullable=False)  # TEXT в базе
    TypeOfActivity = db.Column(db.String(50), nullable=False)
    Duration = db.Column(db.String(20))
    Description = db.Column(db.Text)

class Reminders(db.Model):
    __tablename__ = 'Reminders'
    IdReminders = db.Column(db.Integer, primary_key=True)
    IdPet = db.Column(db.Integer, db.ForeignKey('Pet.IdPet', ondelete='CASCADE'), nullable=False)
    TypeOfReminder = db.Column(db.String(50), nullable=False)
    DataAndTime = db.Column(db.String(50), nullable=False)  # TEXT в базе
    Comment = db.Column(db.Text)

class Visiting(db.Model):
    __tablename__ = 'Visiting'
    IdVisiting = db.Column(db.Integer, primary_key=True)
    IdPet = db.Column(db.Integer, db.ForeignKey('Pet.IdPet', ondelete='CASCADE'), nullable=False)
    IdClinics = db.Column(db.Integer, db.ForeignKey('Clinics.IdClinics', ondelete='CASCADE'), nullable=False)
    DateOfVisit = db.Column(db.String(10), nullable=False)  # TEXT в базе

class Feed(db.Model):
    __tablename__ = 'Feed'
    IdFeed = db.Column(db.Integer, primary_key=True)
    IdPet = db.Column(db.Integer, db.ForeignKey('Pet.IdPet', ondelete='CASCADE'), nullable=False)
    RecordingDate = db.Column(db.String(10), nullable=False)  # TEXT в базе
    TypeOfFeed = db.Column(db.String(50), nullable=False)
    AdditionalAddRived = db.Column(db.String(200))

class Purchases(db.Model):
    __tablename__ = 'Purchases'
    IdPurchases = db.Column(db.Integer, primary_key=True)
    IdPet = db.Column(db.Integer, db.ForeignKey('Pet.IdPet', ondelete='CASCADE'), nullable=False)
    IdPetStore = db.Column(db.Integer, db.ForeignKey('PetStore.IdPetStore', ondelete='CASCADE'), nullable=False)
    DateOfPurchase = db.Column(db.String(10), nullable=False)  # TEXT в базе
