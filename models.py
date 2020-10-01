from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Client(db.Model):
    __tablename__ = 'client'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    jobs =  db.relationship('Job', backref='client', lazy=True, passive_deletes=True)



    def __repr__(self):
        return f'<client {self.id} {self.name}>'



class Contractor(db.Model):
    __tablename__ = 'contractor'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    phone = db.Column(db.String(120))
    jobs = db.relationship('Job', backref='contractor', lazy=True, passive_deletes=True)




    def __repr__(self):
        return f'<contractor {self.id} {self.name}>'

class Job(db.Model): #New model for shows
    __tablename__= 'job'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=True)
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractor.id', ondelete='CASCADE'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id', ondelete='CASCADE'), nullable=False)


    def __repr__(self):
        return f'<job {self.id} {self.start_time} contractor_id={contractor_id} client_id={client_id}>'
