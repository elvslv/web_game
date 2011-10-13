import MySQLdb
from misc import MAX_USERNAME_LEN, MAX_PASSWORD_LEN, MAX_GAMENAME_LEN, MAX_GAMEDESCR_LEN, MAX_MAPNAME_LEN, MAX_RACENAME_LEN
from misc import MAX_SKILLNAME_LEN

DATABASE_HOST = "localhost"
DATABASE_USER = "admin"
DATABASE_NAME = "testdb"
DATABASE_PASSWD = "12345"
DATABASE_PORT = 3306

tables = ['Users', 'Games', 'Chat', 'Maps', 'Regions', 'CurrentRegionState', 
	'AdjacentRegions', 'TokenBadges', 'History', 'AttackingHistory', 'GameHistory']

def fetchone():
	return cursor.fetchone()

def fetchall():
	return cursor.fetchall()

def lastId():
	return db.insert_id()

def query(qstring, *args):
    return int(cursor.execute(qstring, args))	

def queryt(qstring, args):
    return int(cursor.execute(qstring, args))	

def commit():
	db.commit()

def rollback():
	db.rollback()

def createTables():
	cursor.execute('SET storage_engine=INNODB')
	cursor.execute('SET AUTOCOMMIT=0')
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
			GameId INT UNSIGNED AUTO_INCREMENT, 
			GameName VARCHAR(%s), 
			GameDescr VARCHAR(%s),
			PlayersNum INT UNSIGNED DEFAULT 0,
			State INT UNSIGNED, 
			Turn TINYINT UNSIGNED, 
			ActivePlayer INT UNSIGNED,
			MapId INT UNSIGNED REFERENCES Maps(MapId),
			PRIMARY KEY(GameId, GameName))""", 
			(MAX_GAMENAME_LEN, MAX_GAMEDESCR_LEN))
			
	cursor.execute("""CREATE TABLE IF NOT EXISTS Maps(
			MapId INT UNSIGNED PRIMARY KEY AUTO_INCREMENT, 
			MapName VARCHAR(%s), 
			PlayersNum INT UNSIGNED, 
			TurnsNum INT UNSIGNED)""", 
			MAX_MAPNAME_LEN)
			
	cursor.execute("""CREATE TABLE IF NOT EXISTS Regions(
			MapId INT UNSIGNED REFERENCES Maps(MapId), 
			RegionId INT UNSIGNED,
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
			Cavern BOOL DEFAULT FALSE,
			PRIMARY KEY(MapId, RegionId))""")
			
	cursor.execute("""CREATE TABLE IF NOT EXISTS CurrentRegionState(
			RegionId INT UNSIGNED REFERENCES Regions(RegionId),
			GameId INT UNSIGNED REFERENCES Games(GameId) ON DELETE CASCADE ON UPDATE CASCADE,
			TokenBadgeId INT UNSIGNED, 
			TokensNum INT UNSIGNED DEFAULT 0, 
			OwnerId INT UNSIGNED, 
			HoleInTheGround BOOL DEFAULT FALSE,
			Encampment INT UNSIGNED DEFAULT 0, 
			Dragon BOOL DEFAULT FALSE, 
			Fortress BOOL DEFAULT FALSE,
			Hero BOOL DEFAULT FALSE,
			Fortifield BOOL DEFAULT FALSE,
			InDecline BOOL,
			PRIMARY KEY(RegionId, GameId))""")
			
	cursor.execute("""CREATE TABLE IF NOT EXISTS AdjacentRegions (
			FirstRegionId INT UNSIGNED REFERENCES Regions(RegionId), 
			SecondRegionId INT UNSIGNED REFERENCES Regions(RegionId),
			MapId INT UNSIGNED REFERENCES Maps(MapId),
			UNIQUE(FirstRegionId, SecondRegionId, MapId))""")
			
	cursor.execute("""CREATE TABLE IF NOT EXISTS TokenBadges(
			TokenBadgeId INT UNSIGNED AUTO_INCREMENT, 
			RaceId INT UNSIGNED, 
			SpecialPowerId INT UNSIGNED,
			GameId INT UNSIGNED REFERENCES Games(GameId) ON DELETE CASCADE ON UPDATE CASCADE, 
			Position TINYINT, 
			BonusMoney TINYINT, 
			OwnerId INT UNSIGNED, 
			InDecline BOOL DEFAULT FALSE, 
			TotalTokensNum INT UNSIGNED DEFAULT 0,
			TotalSpecialPowerBonusNum INT UNSIGNED DEFAULT 0,
			PRIMARY KEY(TokenBadgeId, GameId))""")
			
	cursor.execute("""CREATE TABLE IF NOT EXISTS Chat(
			Id INT PRIMARY KEY AUTO_INCREMENT, 
			UserId INT REFERENCES Users(Id), 
			Message TEXT, 
			Time INT)""")

	cursor.execute("""CREATE TABLE IF NOT EXISTS History(
			HistoryId INT AUTO_INCREMENT,
			UserId INT REFERENCES Users(Id),
			GameId INT REFERENCES Games(GameId) ON DELETE CASCADE ON UPDATE CASCADE,
			State INT UNSIGNED,
			TokenBadgeId INT UNSIGNED,
			Turn INT UNSIGNED,
			Dice INT UNSIGNED, 
			Friend INT UNSIGNED,
			PRIMARY KEY(HistoryId, GameId))""")

	cursor.execute("""CREATE TABLE IF NOT EXISTS AttackingHistory(
			AttackingHistoryId INT AUTO_INCREMENT,
			HistoryId INT UNSIGNED REFERENCES History(HistoryId) ON DELETE CASCADE ON UPDATE CASCADE,
			AttackingTokenBadgeId INT UNSIGNED REFERENCES TokenBadges(TokenBadgeId),
			ConqueredRegion INT UNSIGNED, 
			AttackedTokenBadgeId INT UNSIGNED, 
			AttackedTokensNum INT UNSIGNED DEFAULT 0, 
			Dice INT UNSIGNED,
			AttackType INT UNSIGNED DEFAULT 0,
			PRIMARY KEY(AttackingHistoryId, HistoryId))""")

	cursor.execute("""CREATE TABLE IF NOT EXISTS GameHistory(
			GameHistoryId INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
			GameId INT UNSIGNED REFERENCES Games(GameId) ON DELETE CASCADE ON UPDATE CASCADE,
			Action TEXT 
		)""")
	        
def clearDb():		
	for t in tables:
		cursor.execute("TRUNCATE TABLE %s" % t)

def clearGame(gameId):	
	cursor.execute("DELETE FROM Games WHERE GameId=%s" % gameId)
	cursor.execute("DELETE FROM TokenBadges WHERE GameId=%s" % gameId)
	cursor.execute("DELETE FROM CurrentRegionState WHERE GameId=%s" % gameId)
	cursor.execute("DELETE FROM History WHERE GameId=%s" % gameId)
	cursor.execute("DELETE FROM GameHistory WHERE GameId=%s" % gameId)
	cursor.execute("ALTER TABLE Games AUTO_INCREMENT=1")
	cursor.execute("ALTER TABLE AttackingHistory AUTO_INCREMENT=1")
	cursor.execute("ALTER TABLE History AUTO_INCREMENT=1")
	cursor.execute("ALTER TABLE CurrentRegionState AUTO_INCREMENT=1" )
	cursor.execute("ALTER TABLE TokenBadges AUTO_INCREMENT=1")
	cursor.execute("ALTER TABLE GameHistory AUTO_INCREMENT=1")

db = MySQLdb.connect(host = DATABASE_HOST, user = DATABASE_USER, passwd = DATABASE_PASSWD,
					port = int(DATABASE_PORT))
cursor = db.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS %s" % DATABASE_NAME)
cursor.execute("USE %s" % DATABASE_NAME)
createTables()
