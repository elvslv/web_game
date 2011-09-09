import MySQLdb
import editDb

cursor = editDb.cursor
db = editDb.db

def doAction(data):
	try:
		res = functions[data['action']](data)
		db.commit()
		return res
	except MySQLdb.Error, e:
		db.rollback()
		return e

def register(data):
	if not(('userName' in data) and ('password' in data)):
		return 'badJson'
		
	userName = data['userName']
	passwd = data['password']
	#when badUserName and badPassword?
	
	num = int(cursor.execute("SELECT 1 FROM %s WHERE UserName=%s" % (editDb.userTable(), userName)))
	if num:
		return 'userNameTaken'
	
	cursor.execute("INSERT INTO %s(UserName, Password) VALUES (%s, %s)" % (editDb.userTable(), userName, passwd))
	return 'ok'

def login(data):
	if not(('userName' in data) and ('password' in data)):
		return 'badJson'
	
	userName = data['userName']
	passwd = data['password']
	
	num = int(cursor.execute("SELECT id FROM %s WHERE UserName=%s AND Password=%s" % 
		(editDb.userTable(), userName, passwd)))
	if num == 0:
		return 'badUserNameOrPassword'
	id = cursor.fetchone()[0]
	num = int(cursor.execute("SELECT Sid FROM %s WHERE UserId=%d" % (editDb.sidTable(), id)))
	if num > 0:
		return 'userLogined'
		
	cursor.execute("INSERT INTO %s(UserId) VALUES(%d)" % (editDb.sidTable(), id))
	sid = db.insert_id()
	return['ok', sid]
	
def logout(data):
	if not('sid' in data):
		return 'badJson'
	
	sid = data['sid']
	num = int(cursor.execute("DELETE FROM %s WHERE Sid=%d" % (editDb.sidTable(), sid)))
	if num == 0:
		return 'badSid'
	return 'ok'

def doSmth(data):
	if not('sid' in data):
		return 'badJson'
		
	sid = data['sid']
	return int(cursor.execute("SELECT UserId FROM %s WHERE Sid=%d" % (editDb.sidTable(), sid)))
	
functions = { 'register': register, 'login': login, 'logout': logout, 'doSmth': doSmth }
