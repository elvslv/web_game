import MySQLdb
from misc import MAX_USERNAME_LEN
from misc import MAX_PASSWORD_LEN
from misc import MAX_GAMENAME_LEN
from misc import MAX_GAMEDESCR_LEN
from misc import MAX_MAPNAME_LEN

DATABASE_HOST = "localhost"
DATABASE_USER = "admin"
DATABASE_NAME = "testdb"
DATABASE_PASSWD = "12345"
DATABASE_PORT = 3306

tables = ['Users', 'Games', 'Chat']

def createTables():
	cursor.execute("CREATE TABLE IF NOT EXISTS \
			Users(Id INT PRIMARY KEY AUTO_INCREMENT, UserName VARCHAR(%s) UNIQUE, Password VARCHAR(%s), Sid BIGINT UNIQUE,\
			GameId INT UNSIGNED, Readiness TINYINT(1), CurrentRace TINYINT UNSIGNED, DeclineRace TINYINT UNSIGNED,\
			Coins TINYINT UNSIGNED)", (MAX_USERNAME_LEN, MAX_PASSWORD_LEN))
	cursor.execute("CREATE TABLE IF NOT EXISTS \
			Games(GameId INT UNSIGNED PRIMARY KEY AUTO_INCREMENT, GameName VARCHAR(%s), GameDescr VARCHAR(%s), PlayersNum INT UNSIGNED, State INT UNSIGNED, MapId INT UNSIGNED)", 
			(MAX_GAMENAME_LEN, MAX_GAMEDESCR_LEN))
	cursor.execute("CREATE TABLE IF NOT EXISTS \
			Maps(MapId INT UNSIGNED PRIMARY KEY AUTO_INCREMENT, MapName VARCHAR(%s), PlayersNum INT UNSIGNED)" % MAX_MAPNAME_LEN)
	cursor.execute("CREATE TABLE IF NOT EXISTS \
			Chat(Id INT PRIMARY KEY AUTO_INCREMENT, UserId INT, Message TEXT, Time REAL)")
                
def clearDb():
	for t in tables:
		cursor.execute("TRUNCATE TABLE %s" % t)
		

db = MySQLdb.connect(host = DATABASE_HOST, user = DATABASE_USER, passwd = DATABASE_PASSWD,
					port = int(DATABASE_PORT))
cursor = db.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS %s" % DATABASE_NAME)
cursor.execute("USE %s" % DATABASE_NAME)
createTables()
