from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


# initialize db instance
db = SQLAlchemy(session_options={"autoflush": False})
ma = Marshmallow()
