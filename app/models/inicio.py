from app import db

class Inicio(db.Model):
    __tablename__ = 'inicio'
    title = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"<Inicio(title='{self.title}')>"
