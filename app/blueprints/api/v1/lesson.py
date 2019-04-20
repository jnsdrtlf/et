from flask import Blueprint, jsonify, request, g, redirect, url_for
from sqlalchemy import exists

from app.models import db
from app.models.enums import Status, Role, Weekday
from app.models.lesson import Lesson, LessonSchema
from app.models.time import Time
from app.models.user import User
from app.utils import requires_auth_status, requires_auth
from app.utils.tasks import tasks

bp = Blueprint('lesson_api1', __name__)
lesson_schema = LessonSchema()
lesson_schemas = LessonSchema(many=True)


@bp.route('/', methods=['POST'])
@requires_auth_status()
def lesson_post():
    """POST /

    Create new `Lesson
    :return: JSON object with `success`, `reason` and `redirect` fields
    """
    if g.session.user.status != Status.accepted or \
            g.session.user.role != Role.tutor:
        return jsonify({'success': False, 'reason': 'forbidden'}), 403

    try:
        weekday = int(request.values.get('weekday', -1))
        time = int(request.values.get('time', -1))
        print(time)
        if time == -1 or \
                not db.session.query(exists().where(Time.id == time)).scalar():
            return jsonify({'success': False, 'reason': 'time'}), 401
        if weekday == -1 or weekday not in Weekday.to_list():
            return jsonify({'success': False, 'reason': 'weekday'}), 401

        lesson = Lesson()
        lesson.school_id = g.session.user.school_id
        lesson.tutor_id = g.session.user_id
        lesson.weekday = Weekday(weekday)
        lesson.time_id = time
        db.session.add(lesson)
        db.session.commit()

        tasks.create_events_now(lesson.id)
        return redirect(url_for('index.index'))
        #return lesson_schema.jsonify(lesson)
    except Exception as e:
        raise e
        return jsonify({'success': False, 'reason': 'other'}), 401


@bp.route('/user/<int:user_id>', methods=['GET'])
@requires_auth()
def get_lesson_by_user(user_id):
    """ GET /user/<int:user_id>

    Get all lessons of a specific user where user_id is the unique id of
    the user in question.
    :return: `LessonSchema`
    """
    _lessons = db.session.query(Lesson).join(User, Lesson.students) \
        .filter(
        (User.id == user_id) |
        (Lesson.tutor_id == user_id)) \
        .all()

    return lesson_schemas.jsonify(_lessons)
