from app.models import db, ma

from app.models.enums import Weekday


class Lesson(db.Model):
    """Lesson

    A lesson takes place every week. This is only a repetition pattern.
    Each week a new event (see `Event`) is created.
    """

    __tablename__ = 'lesson'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'),
                          nullable=False)

    tutor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    available = db.Column(db.Boolean, nullable=False, default=True)
    # Time and repetition pattern (weekly)
    weekday = db.Column(db.Enum(Weekday), nullable=False,
                        default=Weekday.monday)
    time_id = db.Column(db.Integer, db.ForeignKey('time.id'), nullable=False)

    tutor = db.relationship(
        'User', foreign_keys=[tutor_id],
        back_populates='tutor_lessons')
    students = db.relationship(
        'User', secondary='user_lesson',
        back_populates='student_lessons')
    time = db.relationship('Time', foreign_keys=[time_id])
    events = db.relationship('Event', back_populates='lesson')

    def __repr__(self):
        return f'<Lesson {self.tutor.name}@{self.weekday}>'


class LessonSchema(ma.Schema):
    tutor = ma.Nested('UserSchema', exclude=('tutor_lessons',))
    students = ma.Nested('UserSchema', many=True, exclude=('student_lessons',))
    time = ma.Nested('TimeSchema')
    weekday = ma.Method('get_weekday')

    def get_weekday(self, obj: Lesson):
        return obj.weekday.value

    class Meta:
        fields = ('id', 'available', 'weekday', 'time', 'tutor', 'students')
