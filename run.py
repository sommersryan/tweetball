from game_meta import tweet
from game_engine import play, roster

teams = roster.getTeams()

g = play.Game(teams[0], teams[1])

g.play()

g.tearDown()

t = tweet.GameTweeter(g)

t.execute()
