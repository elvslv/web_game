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


def doAction(data):
        try:
                res = functions[data['action']](data)
                db.commit()
                return res
        except MySQLdb.Error, e:
                db.rollback()
                return e

def register(data):
        if not(('username' in data) and ('password' in data)):
                return 'badJson'

        username = data['username']
        passwd = data['password']
        try:
                if  not re.match(usrnameRegexp, username, re.I):
                                        return 'badUsername'
        except(TypeError, ValueError):
                return 'badUserName'
        try:
                if  not re.match(pwdRegexp, passwd, re.I):
                        return 'badPassword'
        except(TypeError, ValueError):
                return 'badPassword'
        
        num = int(cursor.execute("SELECT 1 FROM %s WHERE username='%s'" % (editDb.userTable(), username)))

        if num:
                return 'usernameTaken'

        cursor.execute("INSERT INTO %s(username, password) VALUES ('%s', '%s')" % (editDb.userTable(), username, passwd))
        return 'ok'

def login(data):
	if not(('username' in data) and ('password' in data)):
		return 'badJson'

	username = data['username']
	passwd = data['password']

	num = int(cursor.execute("SELECT id FROM %s WHERE username='%s' AND Password='%s'" % 
		(editDb.userTable(), username, passwd)))
	if num == 0:
		return 'badUsernameOrPassword'
	id = cursor.fetchone()[0]
	num = int(cursor.execute("SELECT Sid FROM %s WHERE UserId=%d" % (editDb.sidTable(), id)))
	if num > 0:
		return 'userLoggedIn'

	cursor.execute("INSERT INTO %s(UserId) VALUES(%d)" % (editDb.sidTable(), id))
	sid = db.insert_id()
	return['ok', sid]

def logout(data):
	if not('sid' in data):
		return 'badJson'

	sid = data['sid']
	try:
                num = int(cursor.execute("DELETE FROM %s WHERE Sid=%d" % (editDb.sidTable(), sid)))
        except(TypeError, ValueError):
                return 'badSid'
	if num == 0:
		return 'badSid'
	return 'ok'

def doSmth(data):
	if not('sid' in data):
		return 'badJson'

	sid = data['sid']
	try:
                num = int(cursor.execute("SELECT UserId FROM %s WHERE Sid=%d" % (editDb.sidTable(), sid)))
        except(TypeError, ValueError):
                return 'badSid'
        if num == 0:
                return 'badSid'
        else:
                return 'ok'

functions = { 'register': register, 'login': login, 'logout': logout, 'doSmth': doSmth }
