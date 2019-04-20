from app.models import db, ma


class Event(db.Model):
    """Event

    An Event is always linked to a lesson. While a lesson only describes
    the repeating pattern, an event has an actual date.
    """
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'),
                          nullable=False)

    period_id = db.Column(db.Integer, db.ForeignKey('period.id'),
                          nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'),
                          nullable=False)

    date = db.Column(db.Date, nullable=False, unique=False)
    inactive = db.Column(db.Boolean, default=False,
                         nullable=False, unique=False)

    lesson = db.relationship('Lesson', back_populates='events')
    period = db.relationship('Period')
    report = db.relationship('Report', secondary='report_event', back_populates='events')


class EventSchema(ma.Schema):
    lesson = ma.Nested('LessonSchema', exclude=('events',))

    class Meta:
        fields = ('id', 'lesson', 'date')
