import play
import roster

teams = roster.getTeams()

g = play.Game(teams[0], teams[1])

g.play()

# g.tearDown()

# t = tweet.GameTweeter(g)

# t.execute()
