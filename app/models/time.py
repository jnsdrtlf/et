from app.models import db, ma


class Time(db.Model):
    """Time

    THis table contains all possible times a lesson can take place. The
    duration of lessons are specified in the `school` table
    (see `lesson_duration`)
    """
    __tablename__ = 'time'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'),
                          nullable=False)

    identifier = db.Column(db.String(48), nullable=False, unique=True)

    # Important: u'HH:MM' 24h format
    start_time = db.Column(db.String(5), nullable=False, unique=True)

    def __repr__(self):
        return f'<Time {self.identifier}>'


class TimeSchema(ma.Schema):
    class Meta:
        fields = ('id', 'identifier', 'start_time')
