import unittest
import actions
import editDb

class Test(unittest.TestCase):
	def setUp(self):
		editDb.clearDb()
		
	def testRegister(self):
		res = actions.doAction({"action": "register", "userName": "1", "password": "1"})
		assert res == 'ok'
		
	def testRegister1(self):
		assert actions.doAction({"action": "register", "userName": "1", "password": "1"}) == 'ok'
		assert actions.doAction({"action": "register", "userName": "2", "password": "1"}) == 'ok'
		
	def testLogin(self):
		assert actions.doAction({"action": "register", "userName": "1", "password": "1"}) == 'ok'
		res = actions.doAction({"action": "login", "userName": "1", "password": "1"})
		assert res[0] == 'ok' and res[1] > 0
	
	def testLoginNotUser(self):
		assert actions.doAction({"action": "login", "userName": "1", "password": "1"}) == 'badUserNameOrPassword'
	
	def testInvalidPass(self):
		assert actions.doAction({"action": "register", "userName": "1", "password": "1"}) == 'ok'
		assert actions.doAction({"action": "login", "userName": "1", "password": "2"}) == 'badUserNameOrPassword'
		
	def testLoginTwice(self):
		assert actions.doAction({"action": "register", "userName": "1", "password": "1"}) == 'ok'
		actions.doAction({"action": "login", "userName": "1", "password": "1"})
		assert actions.doAction({"action": "login", "userName": "1", "password": "1"}) == 'userLogined'
	
	def testLogin2(self):
		assert actions.doAction({"action": "register", "userName": "1", "password": "1"}) == 'ok'
		assert actions.doAction({"action": "register", "userName": "2", "password": "2"}) == 'ok'
		sid1 = actions.doAction({"action": "login", "userName": "1", "password": "1"})[1]
		sid2 = actions.doAction({"action": "login", "userName": "2", "password": "2"})[1]
		assert sid1 > 0 and sid2 > 0 and sid1 != sid2
	
	def testLogout(self):
		actions.doAction({"action": "register", "userName": "1", "password": "1"})
		sid = actions.doAction({"action": "login", "userName": "1", "password": "1"})[1]
		res = actions.doAction({"action": "logout", "sid": sid})
		assert res == 'ok'
		
	def testDoSmthAfterLogin(self):
		actions.doAction({"action": "register", "userName": "1", "password": "1"})
		sid = actions.doAction({"action": "login", "userName": "1", "password": "1"})[1]
		res = actions.doAction({"action": "doSmth", "sid": sid})
		assert actions.doAction({"action": "doSmth", "sid": sid}) == 1
		
	def testDoSmthAfterLogout(self):
		actions.doAction({"action": "register", "userName": "1", "password": "1"})
		sid = actions.doAction({"action": "login", "userName": "1", "password": "1"})[1]
		actions.doAction({"action": "logout", "sid": sid})
		res = actions.doAction({"action": "doSmth", "sid": sid})
		assert actions.doAction({"action": "doSmth", "sid": sid}) == 0
		
if __name__ == '__main__':
    unittest.main()
