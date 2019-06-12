import unittest
from unittest.mock import patch
from test_data import username, password, user_agent
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
from igramscraper.instagram import Instagram

class TestIgramscraper(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        cwd = os.getcwd()
        session_folder = cwd + os.path.sep + 'sessions' + os.path.sep
        if username == None or password == None:
            self.instagram = Instagram()
        else:
            self.instagram = Instagram.with_credentials(username, password, session_folder)
            self.instagram.login()
        
        if user_agent != None:
            #set user agent
            pass

    @classmethod
    def tearDownClass(self):
        pass

    def test_get_account_by_username(self):
        account = self.instagram.get_account('kevin')
        self.assertEqual('kevin', account.username)
        self.assertEqual('3', account.identifier)
    
    def test_get_account_by_id(self):
        account = self.instagram.get_account_by_id(3)
        self.assertEqual('kevin', account.username)
        self.assertEqual('3', account.identifier)



if __name__ == '__main__':
    unittest.main()

