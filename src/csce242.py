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

'''
@summary: Class containing handlers
'''
    
class Util(webapp2.RedirectHandler):
    
    def render(self, tempName):
        template = jinja_environment.get_template(tempName)
        self.response.out.write(template.render(self.template_values))
        
    def exceptionRender(self, message, tempname):
        
        self.user = users.get_current_user()
        
        self.template_values = {
                'username': self.user.nickname() + ' ',
                'headurl': users.create_logout_url("/login"),
                'text': 'Logout',
                'exception': True,
                'message_header': 'Exceptional condition detected!',
                'message_body':  message + 
                                '; you were redirected to the main page.'
            }           
            
        self.render(tempname)

class MainPage(Util):
    
    def get(self):
        
        user = users.get_current_user()
        
        if user:
            self.template_values = {
                'username': user.nickname() + ' ',
                'headurl': users.create_logout_url("/login"),
                'text': 'Logout'
            }
            
            self.render('home.html')
            
        else:
            self.redirect('/login')
      
class Handler(Util):
    
    def get(self):
        
        user = users.get_current_user()
        
        self.pins = Pin.all()
        self.pins.filter("owner =", user)
        
        self.template_values = {
            'pins': self.pins,
            'username': user.nickname() + ' ',
            'headurl': users.create_logout_url('/login'),
            'text': 'Logout'
        }
        
        self.render('thumbnails.html')
        
    def post(self):
        
        self.pin = Pin(imgUrl=self.request.get('url'), caption=self.request.get('caption'))
        
        self.pin.save()
        
        self.pin.id = self.pin.key().id()
        
        self.pin.save()
        
        self.redirect('/pin/%s' % self.pin.key().id())
            
class PinHandler(Util):
    
    def get(self, id):

        user = users.get_current_user()        
        
        self.key = db.Key.from_path('Pin', long(id))
        self.pin = db.get(self.key)
        
        if self.pin:
        
            self.pins = set()
            self.pins.add(self.pin)
                
            self.template_values = {
                'pins': self.pins,
                'username': user.nickname() + ' ',
                'headurl': users.create_logout_url('/login'),
                'text': 'Logout'
            }
        
            self.render('pin.html')
            
        else:
            
            self.exceptionRender('Pin not found', 'home.html')
        
    def post(self, id):
        
        self.action = self.request.get('action')
        
        if self.action == 'update':
            newUrl = self.request.get('url')
            newCaption = self.request.get('caption')
            
            self.key = db.Key.from_path('Pin', long(id))
            self.pin = db.get(self.key)
            
            self.pin.imgUrl = newUrl
            self.pin.caption = newCaption
            
            self.pin.save()
            self.redirect('/pin/%s' % id)
            
        else:
            self.key = db.Key.from_path('Pin', long(id))
            self.pin = db.get(self.key)
            
            self.pin.delete()
            self.redirect('/pin')
        
   
'''
@summary: Class containing authentication handlers
'''
class Auth(Util):
    
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
        self.exceptionRender('Page not found', 'home.html')
    
    
app = webapp2.WSGIApplication([('/', MainPage), ('/pin/(.[0-9]*)/?', PinHandler),
                               ('/pin|/pin/', Handler), ('/login', Auth), 
                               ('/.*', NotFoundPageHandler)],
                               debug=True)
