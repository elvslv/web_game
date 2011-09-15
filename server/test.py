import unittest
import actions
import editDb

class Test(unittest.TestCase):
	def setUp(self):
		editDb.clearDb()
		
	def testRegister(self):
		res = actions.doAction({"action": "register", "username": "aa1", "password": "1aaaaa"})
		assert res == 'ok'
		
	def testRegister1(self):
		assert actions.doAction({"action": "register", "username": "abc", "password": "abcdefg"}) == 'ok'
		assert actions.doAction({"action": "register", "username": "abd", "password": "abcdefg"}) == 'ok'
		
	def testLogin(self):
		assert actions.doAction({"action": "register", "username": "aa3", "password": "abcdef"}) == 'ok'
		res = actions.doAction({"action": "login", "username": "aa3", "password": "abcdef"})
		assert res[0] == 'ok' and res[1] > 0
	
	def testLoginNotUser(self):
		assert actions.doAction({"action": "login", "username": "1", "password": "1"}) == 'badUsernameOrPassword'
	
	def testInvalidPass(self):
		assert actions.doAction({"action": "register", "username": "abc1", "password": "abcdef1"}) == 'ok'
		assert actions.doAction({"action": "login", "username": "abc1", "password": "abcdef2"}) == 'badUsernameOrPassword'
		
	def testLoginTwice(self):
		assert actions.doAction({"action": "register", "username": "abc2", "password": "abc123"}) == 'ok'
		actions.doAction({"action": "login", "username": "abc2", "password": "abc123"})
		assert actions.doAction({"action": "login", "username": "abc2", "password": "abc123"}) == 'userLoggedIn'
	
	def testLogin2(self):
		assert actions.doAction({"action": "register", "username": "abc3", "password": "111111"}) == 'ok'
		assert actions.doAction({"action": "register", "username": "abc4", "password": "222222"}) == 'ok'
		sid1 = actions.doAction({"action": "login", "username": "abc3", "password": "111111"})[1]
		sid2 = actions.doAction({"action": "login", "username": "abc4", "password": "222222"})[1]
		assert sid1 > 0 and sid2 > 0 and sid1 != sid2
	
	def testLogout(self):
		actions.doAction({"action": "register", "username": "guest", "password": "guest1"})
		sid = actions.doAction({"action": "login", "username": "guest", "password": "guest1"})[1]
		res = actions.doAction({"action": "logout", "sid": sid})
		assert res == 'ok'
		
	def testDoSmthAfterLogin(self):
		actions.doAction({"action": "register", "username": "cool_name", "password": "younevergu"})
		sid = actions.doAction({"action": "login", "username": "cool_name", "password": "younevergu"})[1]
		res = actions.doAction({"action": "doSmth", "sid": sid})
		assert res == 'ok'
		
	def testDoSmthAfterLogout(self):
		actions.doAction({"action": "register", "username": "JohnDoe", "password": "xse7en"})
		sid = actions.doAction({"action": "login", "username": "JohnDoe", "password": "xse7en"})[1]
		actions.doAction({"action": "logout", "sid": sid})
		res = actions.doAction({"action": "doSmth", "sid": sid})
		assert res == 'badSid'
		
if __name__ == '__main__':
    unittest.main()
