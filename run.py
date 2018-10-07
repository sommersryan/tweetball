import tweet, play, roster

teams = roster.getTeams()

g = play.Game(teams[0], teams[1])

g.play()

t = tweet.GameTweeter(g)

t.execute()

g.tearDown()