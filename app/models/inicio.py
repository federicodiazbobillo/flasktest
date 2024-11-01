from app import db

class Inicio(db.Model):
    __tablename__ = 'inicio'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Inicio {self.title}>'
