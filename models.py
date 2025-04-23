from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Links(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(200), index=True)
    title = db.Column(db.String(150), index=True)
    component = db.Column(db.String(100), index=True)
    is_parsed = db.Column(db.Boolean, default=False)
    date_parse = db.Column(db.DateTime, nullable=True)
    image_url = db.Column(db.String(200), index=True)
    price = db.Column(db.Integer, index=True)
    articul_yandex = db.Column(db.String(50), index=True)
    is_actual = db.Column(db.Boolean, default=True)
    characteristics = db.relationship(
        'Characteristics',
        back_populates='link',
        cascade='all, delete-orphan'
        )

    def __repr__(self):
        return f'<Links {self.component}>'


class Characteristics(db.Model):
    __tablename__ = 'characteristics'
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey("links.id"))
    link = db.relationship("Links", back_populates="characteristics")
    group = db.Column(db.String(100), index=True)
    name = db.Column(db.String(100), index=True)
    value = db.Column(db.String(100), index=True)

    def __repr__(self):
        return f'<Characteristics link={self.link_id}, group={self.group}, name={self.name}, value={self.value}>'