from game_engine import play, roster
from game_engine.utils import getCity, nicknames
from data_access.factories import load_player_pool
from data_access.writers import PlateAppearanceWriter, GameWriter
import random


def get_teams():
    pool = load_player_pool()

    home_loc = getCity()
    away_loc = getCity()
    home_nick = random.choice(nicknames)
    away_nick = random.choice(nicknames)

    home_lineup = roster.Lineup(pool['homeHitters'], pool['homePitchers'])
    away_lineup = roster.Lineup(pool['awayHitters'], pool['awayPitchers'])

    home_team = roster.Team(home_nick, home_loc, home_lineup)
    away_team = roster.Team(away_nick, away_loc, away_lineup)

    return home_team, away_team


def main():
    pa_writer = PlateAppearanceWriter()
    game_writer = GameWriter()

    teams = get_teams()

    g = play.Game(teams[0], teams[1], pa_writer)

    print("generated id: {0}".format(g._id))

    g.play()

    # g.tearDown()

    resp = game_writer.save_game(g)

    print(resp)


if __name__ == "__main__":
    main()
