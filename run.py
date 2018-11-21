from game_meta import tweet
from game_engine import play, roster
from game_engine.utils import getCity, nicknames
from data_access.factories import load_player_pool
from data_access.writers import PlateAppearanceWriter, PlayerWriter, save_game
import random

def getTeams():

	pool = load_player_pool()

	homeLoc = getCity()
	awayLoc = getCity()
	homeNick = random.choice(nicknames)
	awayNick = random.choice(nicknames)
	
	homeLineup = roster.Lineup(pool['homeHitters'], pool['homePitchers'])
	awayLineup = roster.Lineup(pool['awayHitters'], pool['awayPitchers'])
	
	homeTeam = roster.Team(homeNick, homeLoc, homeLineup)
	awayTeam = roster.Team(awayNick, awayLoc, awayLineup)
	
	return(homeTeam, awayTeam)

def main():
	
	paWriter = PlateAppearanceWriter()
	
	teams = getTeams()
	
	g = play.Game(teams[0], teams[1], paWriter)
	
	g.play()
	
	#g.tearDown()
	
	save_game(g)
	
	#t = tweet.GameTweeter(g)
	
	#t.execute()
	
if __name__ == "__main__":
	main()
	

