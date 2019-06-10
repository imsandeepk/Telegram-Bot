import os

class CookieSessionManager:
    def __init__(self, sessionFolder, filename):
        self.sessionFolder = sessionFolder
        self.filename = filename


    def get_saved_cookies(self):
        try:
            f = open(self.sessionFolder + self.filename, 'r') 
            return f.read()
        except FileNotFoundError:
            return None

    def set_saved_cookies(self, cookiesString):
        if not os.path.exists(self.sessionFolder):
            os.makedirs(self.sessionFolder)

        f = open(self.sessionFolder + self.filename,"w+")
        f.write(cookiesString)
        f.close

    def empty_saved_cookies(self):
        try:
            os.remove(self.sessionFolder + self.filename)
        except FileNotFoundError:
            pass