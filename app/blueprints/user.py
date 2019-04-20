from werkzeug.exceptions import NotFound, Forbidden
from sqlalchemy.sql import and_, or_
from sqlalchemy.orm.exc import NoResultFound

from flask import Blueprint, request, jsonify, g, redirect, render_template, flash, url_for
from flask_babel import gettext, get_locale

from app.models.session import Session
from app.models.lesson import Lesson
from app.models.user import User
from app.models.grade import Grade
from app.models.enums import Locale, Weekday, Role, Status
from app.models import db
from app.utils import requires_auth, requires_auth_status

bp = Blueprint('user', __name__)


@bp.route('/<user_id>', methods=['GET'])
@requires_auth()
def profile(user_id):
    """GET /user/<user_id>

    User profile
    :return: render_template or redirect
    """
    try:
        _user = db.session.query(User).filter(User.id.is_(user_id)).one()
        _weekdays = []
        _locale = get_locale()
        for weekday in Weekday.to_list():
            _lessons = db.session.query(Lesson) \
                .filter((Lesson.tutor_id == _user.id) &
                        (Lesson.weekday == Weekday(weekday)) &
                        Lesson.available) \
                .all()
            _object = {
                'name': _locale.days['format']['short'][weekday],
                'available': bool(len(_lessons) > 0),
                'lessons': _lessons
            }
            _weekdays.append(_object)

        print(_weekdays)
        return render_template('sites/user/profile.html',
                               title=gettext('Profile'),
                               user=_user, weekdays=_weekdays)
    except Exception as e:
        if isinstance(e, NoResultFound):
            return NotFound()
        else:
            raise e


@bp.route('/settings', methods=['GET'])
@requires_auth()
def settings():
    _sessions = db.session.query(Session).filter(Session.user_id.is_(g.session.user_id)).all()
    _sessions.reverse()

    return render_template('sites/user/settings/index.html',
                           title=gettext('Settings'), sessions=_sessions,
                           languages=Locale.to_list())


@bp.route('/settings/lessons', methods=['GET'])
@requires_auth_status()
def lessons():
    _weekdays = []
    _locale = get_locale()
    for weekday in Weekday.to_list():
        _lessons = db.session.query(Lesson) \
            .filter((Lesson.tutor_id == g.session.user_id) &
                    (Lesson.weekday == Weekday(weekday))) \
            .all()
        _object = {
            'name': _locale.days['format']['wide'][weekday],
            'available': bool(len(_lessons) > 0),
            'lessons': _lessons
        }
        _weekdays.append(_object)

    return render_template('sites/user/settings/lessons.html',
                           title=gettext('Lesson Settings'),
                           weekdays=_weekdays)


@bp.route('/settings/lessons/add', methods=['GET'])
@requires_auth_status()
def add_lesson():
    weekdays = get_locale().days['format']['wide']
    grades = db.session.query(Grade).all()
    return render_template('sites/user/settings/add_lesson.html',
                           title=gettext('Add Lesson'),
                           weekdays=weekdays, grades=grades)
