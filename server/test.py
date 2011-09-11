import unittest
import actions
import editDb

class Test(unittest.TestCase):
	def setUp(self):
		editDb.clearDb()
		
	def testRegister(self):
		res = actions.doAction({"action": "register", "userName": "aa1", "password": "1aaaaa"})
		assert res == 'ok'
		
	def testRegister1(self):
		assert actions.doAction({"action": "register", "userName": "abc", "password": "abcdefg"}) == 'ok'
		assert actions.doAction({"action": "register", "userName": "abd", "password": "abcdefg"}) == 'ok'
		
	def testLogin(self):
		assert actions.doAction({"action": "register", "userName": "aa3", "password": "abcdef"}) == 'ok'
		res = actions.doAction({"action": "login", "userName": "aa3", "password": "abcdef"})
		assert res[0] == 'ok' and res[1] > 0
	
	def testLoginNotUser(self):
		assert actions.doAction({"action": "login", "userName": "1", "password": "1"}) == 'badUserNameOrPassword'
	
	def testInvalidPass(self):
		assert actions.doAction({"action": "register", "userName": "abc1", "password": "abcdef1"}) == 'ok'
		assert actions.doAction({"action": "login", "userName": "abc1", "password": "abcdef2"}) == 'badUserNameOrPassword'
		
	def testLoginTwice(self):
		assert actions.doAction({"action": "register", "userName": "abc2", "password": "abc123"}) == 'ok'
		actions.doAction({"action": "login", "userName": "abc2", "password": "abc123"})
		assert actions.doAction({"action": "login", "userName": "abc2", "password": "abc123"}) == 'userLogined'
	
	def testLogin2(self):
		assert actions.doAction({"action": "register", "userName": "abc3", "password": "111111"}) == 'ok'
		assert actions.doAction({"action": "register", "userName": "abc4", "password": "222222"}) == 'ok'
		sid1 = actions.doAction({"action": "login", "userName": "abc3", "password": "111111"})[1]
		sid2 = actions.doAction({"action": "login", "userName": "abc4", "password": "222222"})[1]
		assert sid1 > 0 and sid2 > 0 and sid1 != sid2
	
	def testLogout(self):
		actions.doAction({"action": "register", "userName": "guest", "password": "guest1"})
		sid = actions.doAction({"action": "login", "userName": "guest", "password": "guest1"})[1]
		res = actions.doAction({"action": "logout", "sid": sid})
		assert res == 'ok'
		
	def testDoSmthAfterLogin(self):
		actions.doAction({"action": "register", "userName": "cool_name", "password": "younevergu"})
		sid = actions.doAction({"action": "login", "userName": "cool_name", "password": "younevergu"})[1]
		res = actions.doAction({"action": "doSmth", "sid": sid})
		assert actions.doAction({"action": "doSmth", "sid": sid}) == 1
		
	def testDoSmthAfterLogout(self):
		actions.doAction({"action": "register", "userName": "JohnDoe", "password": "xse7en"})
		sid = actions.doAction({"action": "login", "userName": "JohnDoe", "password": "xse7en"})[1]
		actions.doAction({"action": "logout", "sid": sid})
		res = actions.doAction({"action": "doSmth", "sid": sid})
		assert actions.doAction({"action": "doSmth", "sid": sid}) == 0
		
if __name__ == '__main__':
    unittest.main()
