import MySQLdb
import editDb
import re

from misc import MAX_USERNAME_LEN
from misc import MAX_PASSWORD_LEN
from misc import MIN_USERNAME_LEN
from misc import MIN_PASSWORD_LEN

cursor = editDb.cursor
db = editDb.db

usrnameRegexp = r'^[a-z]+[\w_-]{%d,%d}$' % (MIN_USERNAME_LEN - 1, MAX_USERNAME_LEN - 1)
pwdRegexp = r'^\w{%d,%d}$' % (MIN_PASSWORD_LEN, MAX_PASSWORD_LEN)

def act_register(data):
	if not(('username' in data) and ('password' in data)):
			return {"result": "badJson"}

	username = data['username']
	passwd = data['password']
	try:
		if  not re.match(usrnameRegexp, username, re.I):
			return {"result": "badUsername"}
	except(TypeError, ValueError):
		return {"result": "badUsername"}
	try:
		if  not re.match(pwdRegexp, passwd, re.I):
			return {"result": "badPassword"}
	except(TypeError, ValueError):
		return {"result": "badPassword"}

	num = int(cursor.execute("SELECT 1 FROM Users WHERE Username=%s", username))
	
	if num:
		return {"result": "usernameTaken"}

	cursor.execute("INSERT INTO Users(username, password) VALUES (%s, %s)",(username, passwd))
	return {"result": "ok"}

def act_login(data):
	if not(('username' in data) and ('password' in data)):
		return {"result": "badJson"}

	username = data['username']
	passwd = data['password']

	num = int(cursor.execute("SELECT id FROM Users WHERE Username=%s AND Password=%s",
		(username, passwd)))

	if num == 0:
		return {"result": "badUsernameOrPassword"}
	id = int(cursor.fetchone()[0])
	try:
		num = int(cursor.execute("SELECT Sid FROM Sessions WHERE UserId=%s", id))
	except (TypeError, ValueError), e:
		return e
	if num > 0:
		return {"result": "userLoggedIn"}

	cursor.execute("INSERT INTO Sessions(UserId) VALUES(%s)", id)
	sid = db.insert_id()
	return {"result": "ok", "sid": sid}

def act_logout(data):
	if not('sid' in data):
		return {"result": "badJson"}

	sid = data['sid']
	try:
		num = int(cursor.execute("DELETE FROM Sessions WHERE Sid=%s", sid))
	except(TypeError, ValueError):
		return {"result": "badSid"}
	if num == 0:
		return {"result": "badSid"}
	return {"result": "ok"}

def act_doSmth(data):
	if not('sid' in data):
		return {"result": "badJson"}

	sid = data['sid']
	try:
		num = int(cursor.execute("SELECT UserId FROM Sessions WHERE Sid=%s", sid))
	except(TypeError, ValueError):
		return {"result": "badSid"}
	if num == 0:
		return {"result": "badSid"}
	else:
		return {"result": "ok"}

def doAction(data):
	try:
		func = 'act_%s' % data['action']
		if not(func in globals()):
			return {'result': 'badAction'}
		res = globals()[func](data)
		db.commit()
		return res
	except MySQLdb.Error, e:
		db.rollback()
		return e

