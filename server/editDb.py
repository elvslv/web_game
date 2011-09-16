import MySQLdb
from misc import MAX_USERNAME_LEN
from misc import MAX_PASSWORD_LEN
from misc import MAX_GAMENAME_LEN
from misc import MAX_MAPNAME_LEN

DATABASE_HOST = "localhost"
DATABASE_USER = "admin"
DATABASE_NAME = "testdb"
DATABASE_PASSWD = "12345"
DATABASE_PORT = 3306

tables = ['Users', 'Sessions', 'Games', 'Players', 'Maps']

def createTables():
	cursor.execute("CREATE TABLE IF NOT EXISTS \
			Users(Id INT PRIMARY KEY AUTO_INCREMENT, UserName VARCHAR(%d) UNIQUE, Password VARCHAR(%d))" % (MAX_USERNAME_LEN, MAX_PASSWORD_LEN))
	cursor.execute("CREATE TABLE IF NOT EXISTS \
			Sessions(Sid INT PRIMARY KEY AUTO_INCREMENT, UserId INT UNIQUE, Start DATETIME)")
	cursor.execute("CREATE TABLE IF NOT EXISTS \
			Games(GameId INT UNSIGNED PRIMARY KEY, GameName VARCHAR(%d), MapId INT UNSIGNED, PlayersNum INT UNSIGNED, State TINYINT)" % MAX_GAMENAME_LEN)
	cursor.execute("CREATE TABLE IF NOT EXISTS \
			Players(Sid INT UNSIGNED PRIMARY KEY, GameId INT UNSIGNED, Readiness TINYINT(1), CurrentRace TINYINT UNSIGNED, \
			DeclineRace TINYINT UNSIGNED, Coins TINYINT UNSIGNED)")
	cursor.execute("CREATE TABLE IF NOT EXISTS \
			Maps(MapId INT UNSIGNED PRIMARY KEY, MapName VARCHAR(%d))" % MAX_MAPNAME_LEN)
                
def clearDb():
	for t in tables:
		cursor.execute("TRUNCATE TABLE %s" % t)
		

db = MySQLdb.connect(host = DATABASE_HOST, user = DATABASE_USER, passwd = DATABASE_PASSWD,
					port = int(DATABASE_PORT))
cursor = db.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS %s" % DATABASE_NAME)
cursor.execute("USE %s" % DATABASE_NAME)
createTables()
