from sqlalchemy.sql import exists
from werkzeug.exceptions import Forbidden
import urllib.parse

from flask import Blueprint, request, jsonify, url_for, g
from flask_babel import get_locale, gettext

from app.blueprints.api.v1.session import login
from app.models import db
from app.models.user import User, UserSchema, UserSchemaWeekdays
from app.models.subject import Subject
from app.models.lesson import Lesson
from app.models.grade import Grade
from app.models.enums import Role, Locale, Weekday, Status
from app.utils.tasks import mail, picture
from app.utils import requires_auth_status, requires_auth, get_best_locale

bp = Blueprint('user_api1', __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
users_schema_weekdays = UserSchemaWeekdays(many=True)


@bp.route('/', methods=['POST'])
def user_post():
    """POST /

    Create new user
    :return: JSON object with `success`, `reason` and `redirect` fields
    """
    name = request.values.get('name')
    email = request.values.get('email')
    password = request.values.get('password')
    role = request.values.get('role')
    do_login = request.values.get('login')

    if db.session.query(exists().where(User.email.is_(email))).scalar():
        return jsonify({'success': False, 'reason': 'email'}), 401
    if len(password) < 8:
        return jsonify({'success': False, 'reason': 'password length'}), 401

    _role = Role.student
    if role == 'tutor':
        _role = Role.tutor

    user = User(_role)
    user.name = name
    user.school_id = g.school.id
    user.email = email
    user.locale = get_best_locale()
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    picture.create_user_image(user.id)
    confirm_url = urllib.parse.urljoin(
        request.host_url,
        url_for('auth.confirm', token=user.confirmation_token))
    # TODO: Add HTML template using jinja
    kwargs = {
        'subject': gettext('Verify Email Address'),
        'body': confirm_url,
        'recipients': [user.email]
    }
    mail.send_mail(**kwargs)

    if do_login:
        next_url = url_for('index.index')
        # TODO redirect to configuration site
        return login(email, password, True, next_url)

    return jsonify({'success': True}), 200


@bp.route('/teacher', methods=['GET'])
@requires_auth()
def teacher_get():
    """ GET /teacher

    Get all teachers of specified subjects. See `UserSchema`.
    A list of subjects has to be passed using the `subjects[]`
    parameter. This list must contain integer id's of subjects.
    """
    subjects: list[int] = request.values.getlist('subjects[]')
    subjects = list(map(int, subjects))  # Cast list to integer

    teachers = db.session.query(User) \
        .join(Subject, User.subjects) \
        .filter((User.role == Role.tutor) | Subject.id.in_(subjects)) \
        .all()

    # Append weekdays to user
    # This uses the default locale the user selected.
    # A dict of all weekdays is added to the user object.
    # user.weekdays:
    #  - `name`: Abbreviated name of weekday (e.g. 'Mo')
    #  - `available`: States whether the user offers a session
    _locale = get_locale()
    for user in teachers:
        user.weekdays = []

        for weekday in Weekday.to_list():
            _lessons = db.session.query(Lesson) \
                .filter(
                (Lesson.tutor_id == user.id) &
                (Lesson.available == True) &
                (Lesson.weekday == Weekday(weekday))) \
                .all()
            _object = {
                'name': _locale.days['format']['abbreviated'][weekday],
                'available': bool(len(_lessons) > 0)
            }
            user.weekdays.append(_object)

    return users_schema_weekdays.jsonify(teachers)


@bp.route('/<int:user_id>', methods=['PUT'])
@requires_auth()
def user_put(user_id: int):
    """PUT /<user_id>

    Update a given user's resources
    Example: PUT http://exaple.com/api/v1/user/1
    Corresponding form data should be provided.
    :param user_id: Unique user id of the user
    that should be updated
    :return: JSON
    """
    if g.session.user_id != user_id and g.session.user.role != Role.admin:
        return Forbidden()

    try:
        user = db.session.query(User).filter(User.id == user_id).one()

        name = request.values.get('name')
        email = request.values.get('email')
        password = request.values.get('password')
        teacher_name = request.values.get('teacher_name')
        role = request.values.get('role')
        status = request.values.get('status')
        grade_id = request.values.get('grade_id')
        locale = request.values.get('locale')

        task_list = []

        if name:
            old_initials = user.get_initials()
            user.name = name
            if old_initials != user.get_initials():
                task_list.append((picture.create_user_image, user.id))
        if email:
            if db.session.query(exists().where(User.email == email)).scalar():
                return jsonify({'success': False, 'reason': 'email'}), 401
            user.update_email(email)
            confirm_url = urllib.parse.urljoin(request.host_url, url_for('auth.confirm', token=user.confirmation_token))
            task_list.append((mail.send_mail, 'E-Mail Adresse bestätigen', confirm_url, [user.email]))

        if password:
            if len(password) < 8:
                return jsonify({'success': False, 'reason': 'password'}), 401
            user.set_password(password)
        if role:
            if role in Role.__members__:
                user.role = Role(role)
                user.status = Status.pending
            else:
                return jsonify({'success': False, 'reason': 'role'}), 401
        if status:
            if status in Status.__members__ and g.session.user.role == Role.editor:
                user.status = Role(status)
                user.status = Status.pending
            else:
                return jsonify({'success': False, 'reason': 'status'}), 401
        if grade_id:
            if db.session.query(exists().where(Grade.id == grade_id)).scalar():
                user.grade_id = grade_id
            else:
                return jsonify({'success': False, 'reason': 'grade_id'}), 401
        if teacher_name:
            user.teacher_name = teacher_name
        if locale:
            if locale in Locale.to_list():
                user.locale = Locale(locale)
            else:
                return jsonify({'success': False, 'reason': 'locale'}), 401

        db.session.commit()
        for task in task_list:
            task[0](*task[1:])

        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'reason': 'user'}), 404
