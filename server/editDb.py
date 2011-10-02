import MySQLdb
from misc import MAX_USERNAME_LEN, MAX_PASSWORD_LEN, MAX_GAMENAME_LEN, MAX_GAMEDESCR_LEN, MAX_MAPNAME_LEN, MAX_RACENAME_LEN
from misc import MAX_SKILLNAME_LEN

DATABASE_HOST = "localhost"
DATABASE_USER = "admin"
DATABASE_NAME = "testdb"
DATABASE_PASSWD = "12345"
DATABASE_PORT = 3306

tables = ['Users', 'Games', 'Chat', 'Maps', 'Regions', 'CurrentRegionState', 
	'AdjacentRegions', 'TokenBadges', 'History', 'AttackingHistory']

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
	cursor.execute("""CREATE TABLE IF NOT EXISTS Users(
			Id INT PRIMARY KEY AUTO_INCREMENT, 
			UserName VARCHAR(%s) UNIQUE, 
			Password VARCHAR(%s), 
			Sid BIGINT UNIQUE,
			GameId INT UNSIGNED REFERENCES Games(GameId), 
			IsReady TINYINT(1), 
			CurrentTokenBadge INT UNSIGNED, 
			DeclinedTokenBadge INT UNSIGNED, 
			Coins TINYINT UNSIGNED, 
			TokensInHand INT UNSIGNED DEFAULT 0, 
			Priority INT UNSIGNED)""",
			(MAX_USERNAME_LEN, MAX_PASSWORD_LEN))
			
	cursor.execute("""CREATE TABLE IF NOT EXISTS Games(
			GameId INT UNSIGNED PRIMARY KEY AUTO_INCREMENT, 
			GameName VARCHAR(%s), 
			GameDescr VARCHAR(%s), 
			PlayersNum INT UNSIGNED, 
			State INT UNSIGNED, 
			Turn TINYINT UNSIGNED, 
			ActivePlayer INT UNSIGNED,
			MapId INT UNSIGNED REFERENCES Maps(MapId))""", 
			(MAX_GAMENAME_LEN, MAX_GAMEDESCR_LEN))
			
	cursor.execute("""CREATE TABLE IF NOT EXISTS Maps(
			MapId INT UNSIGNED PRIMARY KEY AUTO_INCREMENT, 
			MapName VARCHAR(%s), 
			PlayersNum INT UNSIGNED, 
			TurnsNum INT UNSIGNED)""", 
			MAX_MAPNAME_LEN)
			
	cursor.execute("""CREATE TABLE IF NOT EXISTS Regions(
			MapId INT UNSIGNED REFERENCES Maps(MapId), 
			RegionId INT UNSIGNED PRIMARY KEY AUTO_INCREMENT, 
			DefaultTokensNum INT UNSIGNED DEFAULT 0,
			Border BOOL DEFAULT FALSE, 
			Coast BOOL DEFAULT FALSE, 
			Mountain BOOL DEFAULT FALSE, 
			Sea BOOL DEFAULT FALSE, 
			Mine BOOL DEFAULT FALSE, 
			Farmland BOOL DEFAULT FALSE, 
			Magic BOOL DEFAULT FALSE, 
			Forest BOOL DEFAULT FALSE, 
			Hill BOOL DEFAULT FALSE, 
			Swamp BOOL DEFAULT FALSE, 
			Cavern BOOL DEFAULT FALSE)""")
			
	cursor.execute("""CREATE TABLE IF NOT EXISTS CurrentRegionState(
			CurrentRegionId INT UNSIGNED PRIMARY KEY AUTO_INCREMENT, 
			RegionId INT UNSIGNED REFERENCES Regions(RegionId),
			GameId INT UNSIGNED REFERENCES Games(GameId),
			TokenBadgeId INT UNSIGNED, 
			TokensNum INT UNSIGNED DEFAULT 0, 
			OwnerId INT UNSIGNED, 
			HoleInTheGround BOOL DEFAULT FALSE,
			Encampment INT UNSIGNED DEFAULT 0, 
			Dragon BOOL DEFAULT FALSE, 
			Fortress BOOL DEFAULT FALSE,
			Hero BOOL DEFAULT FALSE,
			Fortifield BOOL DEFAULT FALSE,
			InDecline BOOL)""")
			
	cursor.execute("""CREATE TABLE IF NOT EXISTS 
			AdjacentRegions (
			FirstRegionId INT UNSIGNED REFERENCES Regions(RegionId), 
			SecondRegionId INT UNSIGNED REFERENCES Regions(RegionId),
			UNIQUE(FirstRegionId, SecondRegionId))""")
			
	cursor.execute("""CREATE TABLE IF NOT EXISTS TokenBadges(
			TokenBadgeId INT UNSIGNED PRIMARY KEY AUTO_INCREMENT, 
			RaceId INT UNSIGNED, 
			SpecialPowerId INT UNSIGNED,
			GameId INT UNSIGNED REFERENCES Games(GameId), 
			Position TINYINT, 
			BonusMoney TINYINT, 
			OwnerId INT UNSIGNED, 
			InDecline BOOL DEFAULT FALSE, 
			TotalTokensNum INT UNSIGNED DEFAULT 0,
			RaceBonusNum INT UNSIGNED DEFAULT 0,
			SpecialPowerBonusNum INT UNSIGNED DEFAULT 0,
			TotalSpecialPowerBonusNum INT UNSIGNED DEFAULT 0)""")
			
	cursor.execute("""CREATE TABLE IF NOT EXISTS Chat(
			Id INT PRIMARY KEY AUTO_INCREMENT, 
			UserId INT REFERENCES Users(Id), 
			Message TEXT, 
			Time INT)""")

	cursor.execute("""CREATE TABLE IF NOT EXISTS History(
			HistoryId INT PRIMARY KEY AUTO_INCREMENT,
			UserId INT REFERENCES Users(Id),
			GameId INT REFERENCES Games(GameId),
			State INT UNSIGNED,
			TokenBadgeId INT UNSIGNED,
			Turn INT UNSIGNED,
			Dice INT UNSIGNED)""")

	cursor.execute("""CREATE TABLE IF NOT EXISTS AttackingHistory(
			AttackingHistoryId INT PRIMARY KEY AUTO_INCREMENT,
			HistoryId INT UNSIGNED REFERENCES History(HistoryId),
			AttackingTokenBadgeId INT UNSIGNED REFERENCES TokenBadges(TokenBadgeId),
			ConqueredRegion INT UNSIGNED, 
			AttackedTokenBadgeId INT UNSIGNED, 
			AttackedTokensNum INT UNSIGNED DEFAULT 0, 
			Dice INT UNSIGNED,
			AttackType INT UNSIGNED DEFAULT 0)""")
	        
def clearDb():		
	for t in tables:
		cursor.execute("TRUNCATE TABLE %s" % t)
		

db = MySQLdb.connect(host = DATABASE_HOST, user = DATABASE_USER, passwd = DATABASE_PASSWD,
					port = int(DATABASE_PORT))
cursor = db.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS %s" % DATABASE_NAME)
cursor.execute("USE %s" % DATABASE_NAME)
createTables()
