import MySQLdb
from misc import MAX_USERNAME_LEN
from misc import MAX_PASSWORD_LEN

DATABASE_HOST = "localhost"
DATABASE_USER = "admin"
DATABASE_NAME = "testdb"
DATABASE_PASSWD = "12345"
DATABASE_PORT = 3306

tables = {"Users": "Users", "Sessions": "Sessions"}

def userTable():
	return tables['Users']

def sidTable():
	return tables['Sessions']

def createTables():
	cursor.execute("CREATE TABLE IF NOT EXISTS \
			%s(Id INT PRIMARY KEY AUTO_INCREMENT, UserName VARCHAR(%d) UNIQUE, Password VARCHAR(%d))" % 
                (userTable(), MAX_USERNAME_LEN, MAX_PASSWORD_LEN))
	cursor.execute("CREATE TABLE IF NOT EXISTS \
			%s(Sid INT PRIMARY KEY AUTO_INCREMENT, UserId INT UNIQUE, Start DATETIME)" % sidTable())
                
def clearDb():
	for t in tables:
		cursor.execute("TRUNCATE TABLE %s" % t)
		

db = MySQLdb.connect(host = DATABASE_HOST, user = DATABASE_USER, passwd = DATABASE_PASSWD,
					port = int(DATABASE_PORT))
cursor = db.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS %s" % DATABASE_NAME)
cursor.execute("USE %s" % DATABASE_NAME)
createTables()
