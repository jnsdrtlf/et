from app.models import db, ma


class Grade(db.Model):
    """Grade

    Grades hav a unique name (e.g. '5' or 'KS1') and are associated with
    a user. A user has a grade_id that links the users own grade.
    Additionally a user is associated with grades using the `user_grade`
    table.
    """
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'),
                          nullable=False)

    name = db.Column(db.String(8), nullable=False, unique=True)

    users = db.relationship('User', back_populates='grade',
                            primaryjoin='User.grade_id == Grade.id')

    def __repr__(self):
        return f'<Grade {self.name}>'


class GradeSchema(ma.Schema):
    users = ma.Nested('UserSchema', many=True, exclude=('grade',))

    class Meta:
        fields = ('id', 'name', 'users')
