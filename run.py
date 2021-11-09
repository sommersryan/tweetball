import play
import roster
import json
from schemas import GameSchema


def execute_from_json(game_json_string):
    game_dict = json.loads(game_json_string)

    home_team_dict = game_dict['homeTeam']
    away_team_dict = game_dict['awayTeam']

    home_team = roster.Team.from_dict(**home_team_dict)
    away_team = roster.Team.from_dict(**away_team_dict)

    game = play.Game(away_team, home_team)

    game.play()

    result = GameSchema().dump(game)

    return json.dumps(result)
