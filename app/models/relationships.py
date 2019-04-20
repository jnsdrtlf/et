from app.models import db


class UserGrade(db.Model):
    """UserGrade

    Association between the user and the grades he is permitted to
    teach.
    """
    __tablename__ = 'user_grade'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey('grade.id'), nullable=False)


class UserLesson(db.Model):
    """TODO add
    """
    __tablename__ = 'user_lesson'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))


class ReportEvent(db.Model):
    """TODO add
    """
    __tablename__ = 'report_event'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)

    report_id = db.Column(db.Integer, db.ForeignKey('report.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))


class UserSubject(db.Model):
    """UserSubject

    Relationship between users and subjects. Each user has a list of 
    subjects that are associtated with the user. The user is permitted 
    to teach those subjects.
    See `Subject`
    """
    __tablename__ = 'user_subject'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
