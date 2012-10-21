'''
Created on Oct 18, 2012

@author: Guilherme Salazar 
@email gmesalazar@gmail.com
'''

import webapp2
import os
import jinja2

from datamodels import *
from google.appengine.api import users

jinja_environment = jinja2.Environment(
                        loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'))

'''
@summary: Class containing misc methods
'''
class Util(webapp2.RedirectHandler):

    def render(self, tempName):
        template = jinja_environment.get_template(tempName)
        self.response.out.write(template.render(self.template_values))
        
    def exceptionRender(self, message, tempName):
        
        user = users.get_current_user()
        
        if user:
            
            self.template_values = {
                    'username': user.nickname() + ' ',
                    'headurl': users.create_logout_url("/"),
                    'text': 'Logout',
                    'exception': True,
                    'message_header': 'Exceptional condition detected!',
                    'message_body':  message
                }           
            
            self.render(tempName)
        
        else:
            self.redirect('/login')
            
    def getObjectFromDatastore(self, path, objId):
        key = db.Key.from_path(path, objId)
        return db.get(key)

class MainPage(Util):
    
    def get(self):
        
        user = users.get_current_user()
        
        if user:
            anonymous = False
            username = user.nickname()
            headUrl = users.create_logout_url('/')
            text = 'Logout'            
        else:
            anonymous = True
            username = ''
            headUrl = users.create_login_url('/')
            text = 'Login'    
           
        self.template_values = {
            'anonymous': anonymous,
            'username': username,
            'headurl': headUrl,
            'text': text
        }         
        
        self.render('home.html')
            
class PinHandler(Util):
    
    def get(self, pinid):

        pinid = long(pinid)

        user = users.get_current_user()        
        
        if not user:
            self.redirect('/login')
            return

        pin = self.getObjectFromDatastore('Pin', pinid)
        
        if not pin:
            self.exceptionRender('Pin not found; you were redirected to the main page.',
                                 'home.html')
            return

        if not pin.private or pin.owner == user:
        
            pins = set()
            pins.add(pin)
            
            boards = set()
            
            for boardid in pin.boards:
                board = self.getObjectFromDatastore('Board', boardid)
                boards.add(board)
            
            self.template_values = {
                'items': pins,
                'boards': boards,
                'username': user.nickname(),
                'headurl': users.create_logout_url('/'),
                'text': 'Logout',
                'objectname': pin.caption,
                'pagecat': 'Pin',
                'anonymous': not user,
                'editable': user == pin.owner
            }
            
            self.render('pin.html')
        
    def post(self, pinid):
        
        pinid = long(pinid)
        
        user = users.get_current_user()
        
        key = db.Key.from_path('Pin', pinid)
        pin = db.get(key)
        
        if user == pin.owner:
        
            self.action = self.request.get('action')
        
            if self.action == 'update':
                newCaption = self.request.get('caption')
                
                pin.caption = newCaption
                
                checkbox = self.request.get('privacy')
                
                if checkbox == 'true':
                    pin.private = True
                else:
                    pin.private = False
                
                pin.save()
                
            elif self.action == 'delete':
                key = db.Key.from_path('Pin', pinid)
                pin = db.get(key)
                
                for boardid in pin.boards:
                    board = self.getObjectFromDatastore('Board', boardid)
                    board.pins.remove(pinid)
                    board.save()
                
                pin.delete()
                self.redirect('/pin')
            
class PinsHandler(Util):
    
    def get(self):
        
        user = users.get_current_user()
        
        if not user:
            self.redirect('login')
            return
        
        # Quick and dirty solution for the absence of an OR operator... :p
        self.q1 = Pin.all().filter("private =", False).fetch(1000)
        self.q2 = Pin.all().filter("owner", user).filter("private =", True).fetch(1000)
        self.pins = [] + self.q1 + self.q2
        
        self.template_values = {
            'items': self.pins,
            'username': user.nickname() + ' ',
            'headurl': users.create_logout_url('/'),
            'text': 'Logout',
            'pagecat': 'Pins',
            'editable': True
        }
    
        self.render('pthumbs.html')
        
    def post(self):
        
        pin = Pin(imgUrl=self.request.get('url'), caption=self.request.get('caption'), boards=[])
        
        checkbox = self.request.get('privacy')
        
        if checkbox == 'private':
            pin.private = True
        else:
            pin.private = False
        
        pin.save()
        pin.id = pin.key().id()
        pin.save()
        
        self.redirect('/pin/%s' % pin.key().id())

class BoardHandler(Util):
    
    def get(self, pinid):
        
        boardid = long(pinid)
        user = users.get_current_user()
        
        if user:
            username = user.nickname()
            headUrl = users.create_logout_url('/')
            headText = 'Logout'
        
        else:
            username = 'anonymous'
            headUrl = users.create_login_url('/')
            headText = 'Login'
        
        board = self.getObjectFromDatastore('Board', boardid)
        
        if not board:
            self.exceptionRender('Board not found; you were redirected to the main page.',
                                 'home.html')
            return
            
        if not board.private or board.owner == user:
            
            allpins = Pin.all().filter("owner =", user)
            
            boardpins = set()
            for pinid in board.pins:
                pin = self.getObjectFromDatastore('Pin', pinid)
                boardpins.add(pin)
            
            self.template_values = {
                'board': board,
                'allpins': allpins,
                'items': boardpins,
                'username': username,
                'headurl': headUrl,
                'text': headText,
                'objectname': board.title,
                'pagecat': 'Board',
                'anonymous': not user,
                'editable': user == board.owner
            }
        
            self.render('board.html')                  

    def post(self, boardid):
        
        boardid = long(boardid)
        board = self.getObjectFromDatastore('Board', boardid)
        
        user = users.get_current_user()
        
        if user == board.owner:
        
            action = self.request.get('action')
            
            if action == 'update':
                newTitle = self.request.get('title')
                newUrl = self.request.get('coverurl')
                
                board.title = newTitle
                board.imgUrl = newUrl
                
                checkbox = self.request.get('privacy')
                
                if checkbox == 'private':
                    board.private = True
                else:
                    board.private = False      
    
                if self.request.get("addpinlist") != '--':
                    pinid = long(self.request.get("addpinlist"))
                    board.pins.append(pinid)
                    pin = self.getObjectFromDatastore('Pin', pinid)
                    pin.boards.append(board.key().id())
                    pin.save()
                
                if self.request.get("delpinlist") != '--':
                    pinid = long(self.request.get("delpinlist"))
                    board.pins.remove(pinid)
                    pin = self.getObjectFromDatastore('Pin', pinid)
                    pin.boards.remove(board.key().id())
                    pin.save()
                
                board.save()
                self.redirect('/board/%s' % boardid)
                
            elif action == 'delete':
                
                for pinid in board.pins:
                    pin = self.getObjectFromDatastore('Pin', pinid)
                    pin.boards.remove(board.key().id())
                    pin.save()
                
                board.delete()
                self.redirect('/board')

class BoardsHandler(Util):
    
    def get(self):
        user = users.get_current_user()
        
        if user:
            anonymous = False
            username = user.nickname()
            headUrl = users.create_logout_url('/')
            headText = 'Logout'
        else:
            anonymous = True
            username = ''
            headUrl = users.create_login_url('/')
            headText = 'Login'
        
        # Quick and dirty solution for the absence of an OR operator... :p
        q1 = Board.all().filter("private =", False).fetch(1000)
        q2 = Board.all().filter("owner =", user).filter("private =", True).fetch(1000)
        boards = [] + q1 + q2
        
        pins = Pin.all().filter("owner =", user)
            
        self.template_values = {
            'allpins': pins,
            'items': boards,
            'username': username,
            'headurl': headUrl,
            'text': headText,
            'anonymous': anonymous,
            'pagecat': 'Boards' 
        }
    
        self.render('bthumbs.html')
            

    def post(self):

        board = Board(title=self.request.get('title'), imgUrl=self.request.get('coverurl'), pins=[])
        
        checkbox = self.request.get('privacy')
        
        if checkbox == 'private':
            board.private = True
        else:
            board.private = False
        
        if self.request.get("addpinlist") != '--':
            pinid = long(self.request.get("addpinlist"))
            board.pins.append(pinid)
            pin = self.getObjectFromDatastore('Pin', pinid)
            board.save()
            pin.boards.append(long(board.key().id()))
            pin.save()
        
        board.save()
        board.id = board.key().id()
        board.save()
        
        self.redirect('/board/%s' % board.key().id())
   
'''
@summary: Class containing authentication handlers
'''
class LoginHandler(Util):
    
    def get(self):
        
        self.template_values = {
            'username': '',
            'headurl': users.create_login_url('/'),
            'text': 'Login'
        }
        
        self.render('login.html')


'''
@summary: 404 error handler
'''
class NotFoundPageHandler(Util):
    
    def get(self):
        self.exceptionRender('Page not found; you were redirected to the main page.', 'home.html')
