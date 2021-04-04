from app import db

class db_user(db.Model):
    __tablename__ = 'db_user'

    email = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(20), unique=True)
    firstname = db.Column(db.String(20), nullable = False)
    lastname = db.Column(db.String(20), nullable = False)
    hashh = db.Column(db.String(100), nullable = False)

    def __init__(self, email, username, firstname, hashh):
            self.email = email
            self.username = username
            self.firstname = firstname
            self.lastname = lastname
            self.hashh = hashh

    def __repr__(self):
        return '<username {}>'.format(self.username)
    
    def serialize(self):
        return {
            'email': self.email, 
            'username': self.username,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'hashh': self.hashh
        }


