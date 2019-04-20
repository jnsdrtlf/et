from app.models import db, ma


class Report(db.Model):
    """Report

    Reports are a list of events that took place in a specific time
    period.

    Fields:
      - `id`: Primary key
      - `period_id`: Associated period
      - `user_id`: Creator of this report
      - `comment`: Additional information by the user
    """

    __tablename__ = 'report'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'),
                          nullable=False)

    period_id = db.Column(db.Integer, db.ForeignKey('period.id'),
                          nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    comment = db.Column(db.String(240))

    # Relationships
    period = db.relationship('Period', back_populates='reports')
    user = db.relationship('User', back_populates='reports')
    events = db.relationship('Event', secondary='report_event', back_populates='report')

    def __repr__(self):
        return f'<Report {self.user.name}@{self.period_id}>'
