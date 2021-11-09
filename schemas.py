from marshmallow import Schema, fields


class PlayerSchema(Schema):
    class Meta:
        fields = ("id", "name", "fullName", "handle", "position", "sub")


class EventSchema(Schema):
    class Meta:
        fields = ("batterOut", "isAB", "isHit", "narrative", "type")


class BaseOutSchema(Schema):
    first = fields.Pluck('PlayerSchema', 'id')
    second = fields.Pluck('PlayerSchema', 'id')
    third = fields.Pluck('PlayerSchema', 'id')

    class Meta:
        additional = ("outs",)


class PlateAppearanceSchema(Schema):
    batter = fields.Pluck('PlayerSchema', 'id')
    pitcher = fields.Pluck('PlayerSchema', 'id')
    event = fields.Nested(EventSchema)
    baseState = fields.Nested(BaseOutSchema)
    endState = fields.Nested(BaseOutSchema)
    timestamp = fields.DateTime()


class LineupSchema(Schema):
    battingOrder = fields.Pluck('PlayerSchema', 'id', many=True)
    pitchers = fields.Pluck('PlayerSchema', 'id', many=True)


class TeamSchema(Schema):
    lineup = fields.Nested(LineupSchema)

    class Meta:
        additional = ('location', 'nickname')


class GameSchema(Schema):
    homeTeam = fields.Nested(TeamSchema)
    awayTeam = fields.Nested(TeamSchema)
    PAs = fields.List(fields.Nested(PlateAppearanceSchema), data_key='plateAppearances')

    class Meta:
        additional = ('startTime', 'homeScore', 'awayScore', 'complete')
