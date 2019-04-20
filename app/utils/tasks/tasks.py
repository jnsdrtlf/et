from datetime import datetime, timedelta

from huey import crontab
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import exists

from app import create_app
from app.models.session import Session
from app.models.period import Period
from app.models.event import Event
from app.models.lesson import Lesson
from app.utils.tasks import huey


@huey.task()
def remove_session(session_id):
    """Remove session
    """
    app, db = create_app(None, minimal=True)
    with app.app_context():
        try:
            session: Session = db.session.query(session_id) \
                .filter(Session.id == session_id) \
                .one()
            if session.is_expired():
                db.session.delete(session)
            else:
                expiration_date = session.last_use + timedelta(days=60)
                remove_session.schedule(args=(session_id,), eta=expiration_date)
        except NoResultFound:
            print(f'Session {session_id} not found.')


@huey.periodic_task(crontab(day_of_week='1'))
def create_events():
    app, db = create_app(None, minimal=True)
    with app.app_context():
        lessons = db.session.query(Lesson).all()
        for lesson in lessons:
            create_event_for_lesson(db, lesson)


@huey.task()
def create_events_now(lesson_id):
    app, db = create_app(None, minimal=True)
    with app.app_context():
        lesson: Lesson = db.session.query(Lesson) \
            .filter(Lesson.id == lesson_id).one()
        create_event_for_lesson(db, lesson)


def next_weekday(date, weekday: int):
    days_ahead = weekday - date.weekday()
    if days_ahead <= 0:
        days_ahead += 7

    return (date + timedelta(days=days_ahead))


def create_event_for_lesson(db, lesson):
    events = db.session.query(Event) \
        .filter((Event.lesson_id == lesson.id) &
                (Event.date > datetime.now().date())) \
        .order_by(Event.date) \
        .all()
    last_date = datetime.now().date() if len(events) == 0 else events[-1].date
    for i in range(len(events), 4):
        next_date = next_weekday(last_date, lesson.weekday.value)
        """current_period = db.session.query(Period) \
            .filter((Period.school_id == lesson.school_id) &
                    (Period.begin_date < next_date) &
                    (Period.due_date > next_date)) \
            .one()"""
        _event = Event()
        _event.date = next_date
        _event.school_id = lesson.school_id
        _event.lesson_id = lesson.id
        _event.period_id = 1
        db.session.add(_event)
        last_date = next_date

    db.session.commit()
