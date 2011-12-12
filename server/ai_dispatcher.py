import httplib
import json

from ai import AI
from httplib import HTTPException
from time import sleep

aiCnt = 0
url = 'localhost:80'


def sendCmd(conn, data):
	conn.request("POST", "/small_worlds", json.dumps(data))
	return json.loads(conn.getresponse().read()) 
	

def dispatch(conn, gameId):
	freeNameFound = False
	name = None
	while not freeNameFound:
		name = 'AI%d' % aiCnt
		r = sendCmd(conn, {'action' : 'register', 'username' : name, 'password' : '12345'})
		aiCnt += 1
		if r['result'] == 'ok': freeNameFound = True
	userInfo = sendCmd(conn, {'action' : 'login', 'username' : name, 'password' : '12345'})
	sendCmd(conn, {'action' : 'joinGame', 'sid' : userInfo['sid'], 'gameId' : gameId})
	ai = AI(url, gameId, userInfo['sid'], userInfo['id'])
	sendCmd(conn, {'action' : 'setReadinessStatus', 'sid' : userInfo['sid'], 'isReady' : True})
		
def main():	
	try:
		conn = httplib.HTTPConnection(url)
		while 1:
			gameList = sendCmd(conn, {'action' : 'getGameList'})['games']
			print gameList
			for game in gameList:
				aiNum = game['ai'] or 0
				for i in range(0, aiNum):
					dispatch(conn, game['id'])
			sleep(5)
	except HTTPException, e:
		print e
		conn.close()

if __name__ == "__main__":
	main()
			
					
			
			

