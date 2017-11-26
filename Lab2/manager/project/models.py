from project import db

class Chunk(db.Model):
    	__tablename__ = 'chunks'
    	id = db.Column(db.Integer, primary_key=True)
    	message = db.Column(db.String(), nullable=False)

    	def __init__(self, message):
	        self.message = message