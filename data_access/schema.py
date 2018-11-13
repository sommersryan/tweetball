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
	
class BaseStateSchema(Schema):

	first = fields.Nested(PlayerSchema, only=["_id"])
	second = fields.Nested(PlayerSchema, only=["_id"])
	third = fields.Nested(PlayerSchema, only=["_id"])
	outs = fields.Integer()

class EventSchema(Schema):

	type = fields.String()
	narrative = fields.String()
	isHit = fields.Boolean()
	isAB = fields.Boolean()
	batterOut = fields.Boolean()
	
class PlateAppearanceSchema(Schema):

	_id = fields.String()
	game_id = fields.String()
	game_ordinal = fields.Integer()
	top = fields.Boolean()
	inning = fields.Integer()
	awayScore = fields.Integer()
	homeScore = fields.Integer()
	batterId = fields.String()
	pitcherId = fields.String()
	narratives = fields.List(fields.String())
	isSubstitution = fields.Boolean()
	wpa = fields.Decimal()
	baseState = fields.Nested(BaseStateSchema)
	endState = fields.Nested(BaseStateSchema)
	event = fields.Nested(EventSchema)
	runs = fields.Integer()
	timestamp = fields.DateTime()

class TeamSchema(Schema):

	_id = fields.String()
	nickname = fields.String()
	location = fields.String()
	
class GameSchema(Schema):

	_id = fields.String()
	startTime = fields.DateTime()
	homeTeam = fields.Nested(TeamSchema, only=["_id"])
	awayTeam = fields.Nested(TeamSchema, only=["_id"])
	homeScore = fields.Integer()
	awayScore = fields.Integer()
	complete = fields.Boolean()
	
	
# class ObjectID(fields.Field)

	# def _serialize(self, value, attr, obj, **kwargs):
		# if value is None:
			# return ''
			
		# return oid(value)
		
	# def _deserialize(self, value, attr, obj, **kwargs):
		
		# return str(value)