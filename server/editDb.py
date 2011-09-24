import MySQLdb
from misc import MAX_USERNAME_LEN, MAX_PASSWORD_LEN, MAX_GAMENAME_LEN, MAX_GAMEDESCR_LEN, MAX_MAPNAME_LEN, MAX_RACENAME_LEN
from misc import MAX_SKILLNAME_LEN

DATABASE_HOST = "localhost"
DATABASE_USER = "admin"
DATABASE_NAME = "testdb"
DATABASE_PASSWD = "12345"
DATABASE_PORT = 3306

tables = ['Users', 'Games', 'Chat', 'Maps', 'Races', 'Regions', 'AdjacentRegions', 'TokenBadges']

def fetchone():
	return cursor.fetchone()

def fetchall():
	return cursor.fetchall()

def lastId():
	return db.insert_id()

def query(qstring, *args):
    return int(cursor.execute(qstring, args))	

def commit():
	db.commit()

def rollback():
	db.rollback()

def createTables():
	cursor.execute("CREATE TABLE IF NOT EXISTS \
			Users(Id INT PRIMARY KEY AUTO_INCREMENT, UserName VARCHAR(%s) UNIQUE, Password VARCHAR(%s), Sid BIGINT UNIQUE,\
			GameId INT UNSIGNED, IsReady TINYINT(1), CurrentRace TINYINT UNSIGNED, DeclineRace TINYINT UNSIGNED,\
			Coins TINYINT UNSIGNED, TokensInHand INT UNSIGNED, Bonus TINYINT UNSIGNED, Priority INT UNSIGNED)",
				(MAX_USERNAME_LEN, MAX_PASSWORD_LEN))
	cursor.execute("CREATE TABLE IF NOT EXISTS \
			Games(GameId INT UNSIGNED PRIMARY KEY AUTO_INCREMENT, GameName VARCHAR(%s), \
			GameDescr VARCHAR(%s), PlayersNum INT UNSIGNED, State INT UNSIGNED, Turn TINYINT UNSIGNED, \
			ActivePlayer INT UNSIGNED, MapId INT UNSIGNED)", (MAX_GAMENAME_LEN, MAX_GAMEDESCR_LEN))
	cursor.execute("CREATE TABLE IF NOT EXISTS \
			Maps(MapId INT UNSIGNED PRIMARY KEY AUTO_INCREMENT, MapName VARCHAR(%s), PlayersNum INT UNSIGNED)" % MAX_MAPNAME_LEN)
	cursor.execute("CREATE TABLE IF NOT EXISTS \
			Regions(MapId INT UNSIGNED, RegionId INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,  \
			RaceId INT UNSIGNED, TokensNum INT UNSIGNED, OwnerId INT UNSIGNED, \
			Borderline BOOL, Highland BOOL,	Coastal BOOL, Seaside BOOL, InDecline BOOL)")
	cursor.execute("""CREATE TABLE IF NOT EXISTS AdjacentRegions (FirstRegionId INT UNSIGNED, 
			SecondRegionId INT UNSIGNED)""")
	cursor.execute("""CREATE TABLE IF NOT EXISTS Races(RaceId TINYINT UNSIGNED PRIMARY KEY 
			AUTO_INCREMENT, RaceName VARCHAR(%s) UNIQUE, InitialNum INT UNSIGNED, 
			BonusID INT UNSIGNED, FarFromStack TINYINT, BonusMoney TINYINT, 
			RaceIndex INT UNSIGNED)""", MAX_RACENAME_LEN)
	cursor.execute("""CREATE TABLE IF NOT EXISTS Skills(SkillId TINYINT UNSIGNED 
			PRIMARY KEY AUTO_INCREMENT, SkillName VARCHAR(%s) UNIQUE, 
			SkillIndex INT UNSIGNED UNIQUE)""", MAX_SKILLNAME_LEN)		
	cursor.execute("CREATE TABLE IF NOT EXISTS \
			AdjacentRegions (FirstRegionId INT UNSIGNED, SecondRegionId INT UNSIGNED)")
	cursor.execute("CREATE TABLE IF NOT EXISTS \
			Races(RaceId TINYINT UNSIGNED PRIMARY KEY AUTO_INCREMENT, RaceName VARCHAR(%s) UNIQUE, \
			InitialNum INT UNSIGNED, BonusID INT UNSIGNED)", MAX_RACENAME_LEN)
	cursor.execute("CREATE TABLE IF NOT EXISTS TokenBadges(RaceId TINYINT UNSIGNED, FarFromStack TINYINT, BonusMoney TINYINT)")
			
	cursor.execute("CREATE TABLE IF NOT EXISTS 	Chat(Id INT PRIMARY KEY AUTO_INCREMENT, UserId INT, Message TEXT, Time INT)")
                
def clearDb():
	for t in tables:
		cursor.execute("TRUNCATE TABLE %s" % t)
		

db = MySQLdb.connect(host = DATABASE_HOST, user = DATABASE_USER, passwd = DATABASE_PASSWD,
					port = int(DATABASE_PORT))
cursor = db.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS %s" % DATABASE_NAME)
cursor.execute("USE %s" % DATABASE_NAME)
createTables()
