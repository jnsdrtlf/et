from app.models import db, ma


class Subject(db.Model):
    """
    Subjects are linked to users using the 
    user_subject table
    """
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'),
                          nullable=False)

    name = db.Column(db.String(48), nullable=False, unique=True)

    users = db.relationship('User', secondary='user_subject',
                            back_populates='subjects', lazy='dynamic')

    def __repr__(self):
        return f'<Subject {self.name}>'


class SubjectSchema(ma.Schema):
    users = ma.Nested('UserSchema', many=True, exclude=('subjects',))

    class Meta:
        fields = ('id', 'name', 'users')
