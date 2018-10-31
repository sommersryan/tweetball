from marshmallow import Schema, fields, pprint, post_load
from game_engine.roster import Player
from bson import ObjectId as oid

class PlayerSchema(Schema):

	_id = fields.String()
	id = fields.Integer()
	name = fields.String()
	fullName = fields.String()
	handle = fields.String()
	handedness = fields.String()
	uniNumber = fields.Integer()
	ratings = fields.Dict(values = fields.Integer(), keys = fields.String())
	battingProbabilities = fields.Dict(values = fields.Float(), keys = fields.String())
	pitchingProbabilities = fields.Dict(values = fields.Float(), keys = fields.String())
	
	@post_load
	def make_player(self, data):
		return Player(**data)
	
class PlateAppearanceSchema(Schema):

	_id = fields.String()
	
class GameSchema(Schema):

	_id = fields.String()
	
class TeamSchema(Schema):

	_id = fields.String()
	
# class ObjectID(fields.Field)

	# def _serialize(self, value, attr, obj, **kwargs):
		# if value is None:
			# return ''
			
		# return oid(value)
		
	# def _deserialize(self, value, attr, obj, **kwargs):
		
		# return str(value)