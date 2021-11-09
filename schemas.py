from marshmallow import Schema, fields


class RatingSetSchema(Schema):
    class Meta:
        fields = ("contact", "power", "discipline", "control", "stuff", "composure", "batting", "pitching")
        ordered = True


class PlayerSchema(Schema):
    ratings = fields.Nested(RatingSetSchema)

    class Meta:
        fields = ("id", "name", "fullName", "handle", "position", "sub")
        ordered = True


class EventSchema(Schema):
    class Meta:
        fields = ("type", "narrative", "batterOut", "isAB", "isHit")
        ordered = True


class BaseOutSchema(Schema):
    first = fields.Pluck('PlayerSchema', 'id')
    second = fields.Pluck('PlayerSchema', 'id')
    third = fields.Pluck('PlayerSchema', 'id')

    class Meta:
        additional = ("outs",)
        ordered = True


class PlateAppearanceSchema(Schema):
    batter = fields.Pluck('PlayerSchema', 'id')
    pitcher = fields.Pluck('PlayerSchema', 'id')
    event = fields.Nested(EventSchema)
    baseState = fields.Nested(BaseOutSchema)
    endState = fields.Nested(BaseOutSchema)
    timestamp = fields.DateTime()

    class Meta:
        additional = ("narratives",)
        ordered = True


class LineupSchema(Schema):
    battingOrder = fields.Pluck('PlayerSchema', 'id', many=True)
    pitchers = fields.Pluck('PlayerSchema', 'id', many=True)
    usedPitchers = fields.Pluck('PlayerSchema', 'id', many=True)


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
        ordered = True