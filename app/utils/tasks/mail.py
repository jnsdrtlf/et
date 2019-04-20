from flask_mail import Mail, Message

from app import create_app

from app.utils.tasks import huey


@huey.task()
def send_mail(**kwargs):
    """Send Mail

    Send an E-Mail using the default configuration.
    :param: `**kwargs` see below

    Possible arguments (from `flask_mail.Message.__init__`):
    :param subject: email subject header
    :param recipients: list of email addresses
    :param body: plain text message
    :param html: HTML message
    :param sender: email sender address, or **DEFAULT_MAIL_SENDER** by default
    :param cc: CC list
    :param bcc: BCC list
    :param attachments: list of Attachment instances
    """
    app, db = create_app(None, minimal=True)
    mail = Mail(app)
    with app.app_context():
        try:
            message = Message(**kwargs)
            mail.send(message)
        except Exception as e:
            raise e
