from datetime import datetime, timedelta

from werkzeug.exceptions import NotFound, Forbidden
from sqlalchemy import exists, or_, and_
from sqlalchemy.orm.exc import NoResultFound

from flask import Blueprint, request, jsonify, g, redirect, render_template, flash, url_for
from flask_babel import gettext, get_locale

from app.models.session import Session
from app.models.user import User
from app.models.subject import Subject
from app.models.lesson import Lesson
from app.models.event import Event
from app.models.enums import Locale, Weekday
from app.models import db
from app.utils import requires_auth, requires_auth_status

bp = Blueprint('index', __name__)


@bp.route('/', methods=['GET'])
@requires_auth_status()
def index():
    """GET /
    :return: render_template
    """
    upcoming = []

    lessons = db.session.query(Lesson) \
        .filter(Lesson.tutor_id == g.session.user_id) \
        .all()
    lessons += db.session.query(Lesson).join(User, Lesson.students) \
        .filter(User.id == g.session.user_id) \
        .all()
    print(lessons)

    for _lesson in lessons:
        events = db.session.query(Event) \
            .filter((Event.lesson_id == _lesson.id) &
                    (Event.date >= datetime.now().date())) \
            .order_by(Event.date) \
            .all()

        print(events)

        for event in events:
            upcoming.append({
                'date': event.date,
                'lesson': _lesson,
                'weekday': get_locale().days['format']['wide'][_lesson.weekday.value]
            })

    return render_template('sites/index.html', title=gettext('Dashboard'),
                           upcoming=upcoming)


@bp.route('/discover', methods=['GET'])
@requires_auth_status()
def discover():
    subjects = db.session.query(Subject).all()
    return render_template('sites/discover.html', subjects=subjects,
                           title=gettext('Find Tutor'))


@bp.route('/calendar', methods=['GET'])
@requires_auth_status()
def calendar():
    return render_template('sites/calendar.html', title=gettext('Calendar'))


@bp.route('/report', methods=['GET'])
@requires_auth_status()
def report():
    return render_template('sites/report.html', title=gettext('Report'))


@bp.route('/search', methods=['GET'])
@requires_auth_status()
def search():
    query = request.values.get('query', '')
    query_like = '%' + '%'.join(query[i:i + 1] for i in range(0, len(query), 1)) + '%'

    subjects = db.session.query(Subject).filter(Subject.name.ilike(query_like)).all()
    users = db.session.query(User).filter(User.name.ilike(query_like)).all()
    users_subject = db.session.query(User).join(Subject, User.subjects).filter(Subject.name.ilike(query_like)).all()
    users = list(set(users + users_subject))

    _locale = get_locale()

    for user in users:
        user.weekdays = []

        for weekday in Weekday.to_list():
            _lessons = db.session.query(Lesson) \
                .filter((Lesson.tutor_id == user.id) &
                        (Lesson.weekday == Weekday(weekday)) &
                        Lesson.available) \
                .all()
            _object = {
                'name': _locale.days['format']['short'][weekday],
                'available': bool(len(_lessons) > 0)
            }
            user.weekdays.append(_object)

    return render_template('sites/search.html',
                           title=gettext('Search for %s' % query),
                           users=users, subjects=subjects)


@bp.route('/subject/<int:subject_id>', methods=['GET'])
@requires_auth_status()
def subject(subject_id):
    try:
        _subject = db.session.query(Subject).filter(Subject.id.is_(subject_id)).one()

        _locale = get_locale()

        for user in _subject.users:
            user.weekdays = []
            for weekday in Weekday.to_list():
                _lessons = db.session.query(Lesson) \
                    .filter((Lesson.tutor_id == user.id) &
                            (Lesson.weekday == Weekday(weekday)) &
                            Lesson.available) \
                    .all()
                _object = {
                    'name': _locale.days['format']['short'][weekday],
                    'available': bool(len(_lessons) > 0)
                }
                user.weekdays.append(_object)

        return render_template('sites/subject.html', title=_subject.name, subject=_subject)
    except Exception as e:
        if isinstance(e, NoResultFound):
            return NotFound()
        else:
            raise e


@bp.route('/lesson/<int:lesson_id>', methods=['GET'])
@requires_auth_status()
def lesson(lesson_id):
    try:
        remove = request.args.get('remove', False)
        signout = request.args.get('signout', False)
        signup = request.args.get('signup', False)

        _lesson = db.session.query(Lesson).filter(Lesson.id == lesson_id).one()

        if remove:
            if _lesson.tutor_id == g.session.user_id:
                db.session.delete(_lesson)
                db.session.commit()
                return redirect(url_for('index.index'))
            else:
                return Forbidden()
        if signout:
            if g.session.user in _lesson.students:
                _lesson.students.remove(g.session.user)
                _lesson.available = bool(len(_lesson.students) == 0)
                db.session.commit()
            else:
                return Forbidden()
        if signup:
            if _lesson.available and not _lesson.tutor_id == g.session.user_id \
                    and g.session.user not in _lesson.students:
                _lesson.students.append(g.session.user)
                _lesson.available = bool(len(_lesson.students) > 1)
                db.session.commit()
            else:
                return Forbidden()

        return render_template('sites/lesson.html', title=_lesson.tutor.name, lesson=_lesson)
    except NoResultFound:
        return NotFound()
    except Exception as e:
        raise e
