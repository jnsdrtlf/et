from app.models import db, ma


class School(db.Model):
    """School

    This table stores the configuration for each individual school.
    Schools are addressed through their short name.
    """

    __tablename__ = 'school'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)

    school_name = db.Column(db.String(48), nullable=False)
    # `short_name` can be used as a subdomain (e.g. abc.tuutor.de)
    short_name = db.Column(db.String(8), nullable=False, unique=True)

    # Duration of a typical lesson (see `time` or `lesson`) in minutes
    lesson_duration = db.Column(db.Integer, nullable=False, default=45)

    def __repr__(self):
        return f'<School {self.short_name}>'
