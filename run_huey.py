from huey import RedisHuey

huey = RedisHuey()

from app.utils.tasks.picture import create_user_image
from app.utils.tasks.mail import send_mail
from app.utils.tasks.tasks import remove_session, create_events, create_events_now

if __name__ == '__main__':
    pass