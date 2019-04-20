from app.models import db, ma


class Period(db.Model):
    """Period

    A period describes a due date for all reports to be done. A report 
    must therefore contain all events from the periods `begin_date` to
    its `due_date`
    """

    __tablename__ = 'period'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'),
                          nullable=False)

    begin_date = db.Column(db.Date, unique=True, nullable=False)
    due_date = db.Column(db.Date, unique=True, nullable=False)

    reports = db.relationship(
        'Report', back_populates='period',
        primaryjoin='Period.id == Report.period_id')


class PeriodSchema(ma.Schema):
    class Meta:
        fields = ('id', 'begin_date', 'due_date')
