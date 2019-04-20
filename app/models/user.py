import secrets
import hashlib
from datetime import datetime, timedelta
import bcrypt

from app.models import db, ma

from app.models.enums import Role, Status, Locale, Weekday


class User(db.Model):
    """
    User object to store user information
    """
    default_picture_path = '/static/images/profile/%s.png'

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'),
                          nullable=False)

    # personal information
    name = db.Column(db.String(48), nullable=False)
    email = db.Column(db.String(48), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)

    teacher_name = db.Column(db.String(48), nullable=True)

    picture = db.Column(db.String(128), nullable=True, unique=False)
    has_placeholder = db.Column(db.Boolean, nullable=False, unique=False,
                                default=True)

    locale = db.Column(db.Enum(Locale), nullable=False, default=Locale.en)

    # email confirmation
    email_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmation_token = db.Column(db.String(32), unique=True, nullable=True)

    # password reset
    password_token = db.Column(db.String(32), unique=True, nullable=True)
    last_reset = db.Column(db.DateTime, nullable=True, unique=False)
    reset_active = db.Column(db.Boolean, nullable=False, default=False)

    # school relationship
    role = db.Column(db.Enum(Role), nullable=False, default=Role.none)
    status = db.Column(db.Enum(Status), nullable=True, default=Status.pending)

    grade_id = db.Column(db.Integer, db.ForeignKey('grade.id'), nullable=True)

    # subjects
    subjects = db.relationship('Subject', secondary='user_subject',
                               back_populates='users')
    grade = db.relationship('Grade', foreign_keys=[grade_id],
                            back_populates='users')
    tutor_grades = db.relationship('Grade', secondary='user_grade')
    reports = db.relationship('Report', back_populates='user')

    tutor_lessons = db.relationship(
        'Lesson', back_populates='tutor',
        primaryjoin='Lesson.tutor_id == User.id')
    student_lessons = db.relationship(
        'Lesson', secondary='user_lesson',
        back_populates='students',
        primaryjoin='(Lesson.id == UserLesson.lesson_id) & '
                    '(User.id == UserLesson.user_id)')

    sessions = db.relationship('Session', back_populates='user')

    def __init__(self, role: Role):
        self.email_confirmed = False
        self.confirmation_token = secrets.token_hex(32)

        self.role = role
        self.status = Status.pending

    def __repr__(self):
        return f'<User {self.name}>'

    def reset_password(self):
        self.last_reset = datetime.now()
        self.reset_active = True
        self.password_token = secrets.token_hex(32)

    def is_reset_expired(self):
        return (self.last_reset + timedelta(minutes=30)) < datetime.now()

    def update_email(self, email):
        self.email = email
        self.email_confirmed = False
        self.confirmation_token = secrets.token_hex(32)

    def set_password(self, password):
        self.reset_active = False
        self.password_token = None
        self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password)

    def set_picture(self, name: str):
        self.picture = self.default_picture_path % name

    def get_initials(self):
        initials = self.name[0]
        if ' ' in self.name:
            # add first letter of last name
            initials += self.name.split(' ')[-1][0]

        return initials


class UserSchema(ma.Schema):
    subjects = ma.Nested('SubjectSchema', many=True, exclude=('users',))
    grade = ma.Nested('GradeSchema', exclude=('users',))
    tutor_grades = ma.Nested('GradeSchema', many=True, exclude=('users',))
    tutor_lessons = ma.Nested('LessonSchema', many=True, exclude=('tutor',))
    student_lessons = ma.Nested('LessonSchema', many=True, exclude=('students',))
    role = ma.Method('get_role')
    status = ma.Method('get_status')

    def get_role(self, obj: User):
        return obj.role.value

    def get_status(self, obj: User):
        return obj.status.value

    class Meta:
        fields = (
            'id', 'name', 'picture',
            'role', 'subjects', 'status',
            'grade', 'tutor_grades', 'teacher_name',
            'tutor_lessons', 'student_lessons')


class UserSchemaWeekdays(UserSchema):
    class Meta:
        fields = (
            'id', 'name', 'picture',
            'role', 'subjects', 'status',
            'grade', 'tutor_grades', 'teacher_name',
            'tutor_lessons', 'student_lessons', 'weekdays')
