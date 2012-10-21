'''
Created on Oct 18, 2012

@author: Guilherme Salazar 
@email gmesalazar@gmail.com
'''

import webapp2
import os
import jinja2
import json

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
            
    def getObjectFromDatastore(self, path, objid):
        key = db.Key.from_path(path, objid)
        obj = db.get(key)
        return obj
    
    def writeJSON(self, jsonStr):
        self.response.out.headers['Content-Type'] = 'text/json'
        self.response.out.write(jsonStr)

class MainPage(Util):
    
    def get(self):
        
        user = users.get_current_user()
        
        if not user:
            self.redirect('/login')
            return

        self.template_values = {
            'username': user.nickname(),
            'headurl': users.create_logout_url('/'),
            'text': 'Logout'
        }
        
        self.render('home.html')
        
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Pin):
            return {'imgUrl': obj.imgUrl, 'caption': obj.caption, 'date': obj.date,
                    'owner': obj.owner, 'id': obj.id, 'private': obj.private,
                    'boards': obj.boards}
        elif isinstance(obj, Board):
            return {'id': obj.id, 'title': obj.title, 'private': obj.private,
                    'pins': obj.pins, 'imgUrl': obj.imgUrl, 'owner': obj.owner
                    }
        elif isinstance(obj, users.User):
            return obj.nickname()
        elif hasattr(obj, 'isoformat'):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)

class PinJsonHandler(Util):

    def get(self, pinid):
        
        user = users.get_current_user()
        
        if not user:
            self.redirect('/login')
            return
            
        pinid = long(pinid.split('.')[0])
        pin = self.getObjectFromDatastore('Pin', pinid)
        
        if not pin:
            self.exceptionRender('Pin not found; you were redirected to the main page.',
                                 'home.html')
            return

        pinjson = json.dumps(pin, cls=MyEncoder, sort_keys=True, indent=4)
        
        self.writeJSON(pinjson)

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
        
        fmt = self.request.get('fmt')
        
        if fmt == 'json':
            
            pinjson = json.dumps(pin, cls=MyEncoder, sort_keys=True, indent=4)
            
            self.writeJSON(pinjson)
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
        pin = self.getObjectFromDatastore('Pin', pinid)
        
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
            
        fmt = self.request.get('fmt')
        
        if fmt == 'json':
            user = users.get_current_user()
    
            pins = Pin.all().filter("owner =", user).fetch(1000)   
            
            pinsjson = json.dumps(pins, cls=MyEncoder, sort_keys=True, indent=4)
        
            self.writeJSON(pinsjson)
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
    

class BoardJsonHandler(Util):

    def get(self, boardid):
        
        user = users.get_current_user()
        
        boardid = long(boardid.split('.')[0])
        board = self.getObjectFromDatastore('Board', boardid)
        
        if not user or (board.private and board.owner != user):
            self.redirect('/login')
            return
        
        if not board:
            self.exceptionRender('Board not found; you were redirected to the main page.',
                                 'home.html')
            return

        boardjson = json.dumps(board, cls=MyEncoder, sort_keys=True, indent=4)
    
        self.template_values = {
            'jsonrepr': boardjson
        }
    
        self.writeJSON(boardjson)

class BoardHandler(Util):
    
    def get(self, boardid):
        
        boardid = long(boardid)
        board = self.getObjectFromDatastore('Board', boardid)
        
        user = users.get_current_user()
        
        if not board:
            self.exceptionRender('Board not found; you were redirected to the main page.',
                                 'home.html')
            return
        
        if not user or (board.private and board.owner != user):
            self.redirect('/login')
            return
        
        fmt = self.request.get('fmt')
        
        if fmt == 'json':
            
            boardjson = json.dumps(board, cls=MyEncoder, sort_keys=True, indent=4)
        
            self.writeJSON(boardjson)
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
                'username': user.nickname(),
                'headurl': users.create_logout_url('/'),
                'text': 'Logout',
                'objectname': board.title,
                'pagecat': 'Board',
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
                if newTitle:
                    board.title = newTitle
                
                checkbox = self.request.get('privacy')
                
                if checkbox == 'true':
                    board.private = True
                elif checkbox == 'false':
                    board.private = False
    
                if self.request.get("addpin"):
                    pinid = long(self.request.get("addpin"))
                    board.pins.append(pinid)
                    pin = self.getObjectFromDatastore('Pin', pinid)
                    pin.boards.append(board.key().id())
                    pin.save()
                
                if self.request.get("delpin"):
                    pinid = long(self.request.get("delpin"))
                    board.pins.remove(pinid)
                    pin = self.getObjectFromDatastore('Pin', pinid)
                    pin.boards.remove(board.key().id())
                    pin.save()
                
                board.save()
                
            elif action == 'delete':
                board = self.getObjectFromDatastore('Board', boardid)
                
                for pinid in board.pins:
                    pin = self.getObjectFromDatastore('Pin', pinid)
                    pin.boards.remove(board.key().id())
                    pin.save()
                
                board.delete()
                self.redirect('/board')

class BoardsHandler(Util):
    
    def get(self):
        user = users.get_current_user()
        
        if not user:
            self.redirect('/login')
            return
        
        fmt = self.request.get('fmt')
        
        if fmt == 'json':
            boards = Board.all().filter("owner =", user).fetch(1000)   
            
            boardsjson = json.dumps(boards, cls=MyEncoder, sort_keys=True, indent=4)
            
            self.writeJSON(boardsjson)
            return
        
        # Quick and dirty solution for the absence of an OR operator... :p
        q1 = Board.all().filter("private =", False).fetch(1000)
        q2 = Board.all().filter("owner =", user).filter("private =", True).fetch(1000)
        boards = [] + q1 + q2
        
        pins = Pin.all().filter("owner =", user)
            
        self.template_values = {
            'allpins': pins,
            'items': boards,
            'username': user.nickname(),
            'headurl': users.create_logout_url('/'),
            'text': 'Logout',
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