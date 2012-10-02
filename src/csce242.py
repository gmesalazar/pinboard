'''
Created on Aug 28, 2012

@author: Guilherme Salazar 
@email gmesalazar@gmail.com
'''

import webapp2
import jinja2
import os

from google.appengine.ext import db
from google.appengine.api import users

jinja_environment = jinja2.Environment(
                        loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'))

'''
@summary: data model for a pin
'''
class Pin(db.Model):
    imgUrl = db.StringProperty()
    caption = db.StringProperty()
    date = db.DateProperty(auto_now=True)
    owner = db.UserProperty(auto_current_user=True)
    id = db.IntegerProperty()
    private = db.BooleanProperty()
    boards = db.ListProperty(long)

'''
@summary: data model for a board
'''
class Board(db.Model):
    id = db.IntegerProperty()
    title = db.StringProperty()
    private = db.BooleanProperty()
    pins = db.ListProperty(long)
    imgUrl = db.StringProperty()
    owner = db.UserProperty(auto_current_user=True)

'''
@summary: Class containing handlers
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
    
    def get(self, id):

        user = users.get_current_user()        
        
        if user:
        
            key = db.Key.from_path('Pin', long(id))
            pin = db.get(key)
            
            if pin:
                
                if not pin.private or pin.owner == user:
                
                    pins = set()
                    pins.add(pin)
                        
                    if pin.private == True:
                        private = 'checked="checked"'
                    else:
                        private = ''
                    
                    boards = set()
                    for boardId in pin.boards:
                        key = db.Key.from_path('Board', long(boardId))
                        board = db.get(key)
                        boards.add(board)
                    
                    self.template_values = {
                        'items': pins,
                        'boards': boards,
                        'username': user.nickname() + ' ',
                        'headurl': users.create_logout_url('/'),
                        'text': 'Logout',
                        'private': private,
                        'pagename': '&ndash; Pin',
                        'editable': user == pin.owner
                    }
                    
                    self.render('pin.html')
                else:
                    self.exceptionRender('Pin not found; you were redirected to the main page.',
                                     'home.html')
                    
            else:
                self.exceptionRender('Pin not found; you were redirected to the main page.',
                                     'home.html')
                  
        else:
            self.redirect('/login')
        
    def post(self, id):
        
        user = users.get_current_user()
        
        key = db.Key.from_path('Pin', long(id))
        pin = db.get(key)
        
        if user == pin.owner:
        
            self.action = self.request.get('action')
        
            if self.action == 'update':
                newUrl = self.request.get('url')
                newCaption = self.request.get('caption')
                
                pin.imgUrl = newUrl
                pin.caption = newCaption
                
                checkbox = self.request.get('privacy')
                
                if checkbox == 'private':
                    pin.private = True
                else:
                    pin.private = False
                
                pin.save()
                self.redirect('/pin/%s' % id)
                
            else:
                key = db.Key.from_path('Pin', long(id))
                pin = db.get(key)
                
                for boardId in pin.boards:
                    key = db.Key.from_path('Board', boardId)
                    board = db.get(key)
                    board.pins.remove(long(id))
                    board.save()
                
                pin.delete()
                self.redirect('/pin')
            
class PinsHandler(Util):
    
    def get(self):
        
        user = users.get_current_user()
        
        if user:
        
            # Quick and dirty solution for the absence of an OR operator... :p
            self.q1 = Pin.all().filter("private =", False).fetch(1000)
            self.q2 = Pin.all().filter("owner", user).filter("private =", True).fetch(1000)
            self.pins = [] + self.q1 + self.q2
            
            self.template_values = {
                'items': self.pins,
                'username': user.nickname() + ' ',
                'headurl': users.create_logout_url('/'),
                'text': 'Logout',
                'pagename': '&ndash; Pins',
                'editable': True
            }
        
            self.render('pthumbs.html')
            
        else:
            self.redirect('login')
        
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
    
    def get(self, id):
        
        user = users.get_current_user()
        
        if user:
            anonymous = False,
            username = user.nickname()
            headUrl = users.create_logout_url('/')
            text = 'Logout'
        
        else:
            anonymous = True,
            username = ''
            headUrl = users.create_login_url('/')
            text = 'Login'
        
        key = db.Key.from_path('Board', long(id))
        board = db.get(key)
        
        if board:
            
            if not board.private or board.owner == user:

                if board.private == True:
                    privateAttr = 'checked="checked"'
                else:
                    privateAttr = ''
                
                allpins = Pin.all().filter("owner =", user)
                
                boardpins = set()
                for pinKey in board.pins:
                    key = db.Key.from_path('Pin', long(pinKey))
                    pin = db.get(key)
                    boardpins.add(pin)
                
                self.template_values = {
                    'anonymous': anonymous,
                    'allpins': allpins,
                    'items': boardpins,
                    'board': board,
                    'username': username,
                    'headurl': headUrl,
                    'text': text,
                    'private': privateAttr,
                    'pagename': '&ndash; Board',
                    'editable': user == board.owner
                }
            
                self.render('board.html')
            else:
                self.exceptionRender('Board not found; you were redirected to the main page.',
                                 'home.html')     
                
        else:
            self.exceptionRender('Board not found; you were redirected to the main page.',
                                 'home.html')
                  

    def post(self, id):
        
        user = users.get_current_user()
        
        key = db.Key.from_path('Board', long(id))
        board = db.get(key)
        
        if user == board.owner:
        
            self.action = self.request.get('action')
            
            if self.action == 'update':
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
                    board.pins.append(long(self.request.get("addpinlist")))
                    key = db.Key.from_path('Pin', long(self.request.get("addpinlist")))
                    pin = db.get(key)
                    pin.boards.append(board.key().id())
                    pin.save()
                
                if self.request.get("delpinlist") != '--':
                    board.pins.remove(long(self.request.get("delpinlist")))
                    key = db.Key.from_path('Pin', long(self.request.get("delpinlist")))
                    pin = db.get(key)
                    pin.boards.remove(board.key().id())
                    pin.save()
                
                board.save()
                self.redirect('/board/%s' % id)
                
            else:
                key = db.Key.from_path('Board', long(id))
                board = db.get(key)
                
                for pinId in board.pins:
                    key = db.Key.from_path('Pin', pinId)
                    pin = db.get(key)
                    pin.boards.remove(board.key().id())
                
                board.delete()
                self.redirect('/board')

class BoardsHandler(Util):
    
    def get(self):
        user = users.get_current_user()
        
        if user:
            editable = True
            username = user.nickname()
            headUrl = users.create_logout_url('/')
            text = 'Logout'
            pagename = '&ndash; Boards'
        else:
            editable = False
            username = ''
            headUrl = users.create_login_url('/')
            text = 'Login'
            pagename = '&ndash; Public Boards'
        
        # Quick and dirty solution for the absence of an OR operator... :p
        q1 = Board.all().filter("private =", False).fetch(1000)
        q2 = Board.all().filter("owner", user).filter("private =", True).fetch(1000)
        boards = [] + q1 + q2
        
        pins = Pin.all().filter("owner =", user)
            
        self.template_values = {
            'allpins': pins,
            'items': boards,
            'username': username,
            'headurl': headUrl,
            'text': text,
            'pagename': pagename,
            'editable': editable
        }
    
        self.render('bthumbs.html')
            

    def post(self):

        board = Board(title=self.request.get('title'), imgUrl=self.request.get('coverurl'), pins = [])
        
        checkbox = self.request.get('privacy')
        
        if checkbox == 'private':
            board.private = True
        else:
            board.private = False
        
        if self.request.get("addpinlist") != '--':
            board.pins.append(long(self.request.get("addpinlist")))
            
            key = db.Key.from_path('Pin', long(self.request.get("addpinlist")))
            pin = db.get(key)
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
    
    
app = webapp2.WSGIApplication([('/', MainPage), ('/pin/(.[0-9]*)/?', PinHandler),
                               ('/board/(.[0-9]*)/?', BoardHandler),
                               ('/board/?', BoardsHandler),
                               ('/pin/?', PinsHandler), ('/login', LoginHandler),
                               ('/.*', NotFoundPageHandler)],
                               debug=True)
