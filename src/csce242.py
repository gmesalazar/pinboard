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
    date = db.DateProperty()
    owner = db.StringProperty()

'''
@summary: Class containing handlers
'''
class Handler(webapp2.RequestHandler):
    
    def render(self, tempName):
        template = jinja_environment.get_template(tempName)
        self.response.out.write(template.render(self.template_values))  
    
    def get(self):
        
        user = users.get_current_user()
        
        if user:
            self.template_values = {
                'username': user.nickname() + ' ',
                'headurl': users.create_logout_url("/login"),
                'text': 'Logout'
            }
            
            self.render('base.html')
            
        else:
            self.redirect('/login')
            
    def post(self):
        
        user = users.get_current_user()
        
        self.template_values = {
            'url': self.request.get('url'),
            'caption': self.request.get('caption'),
            'username': user.nickname() + ' ',
            'headurl': users.create_logout_url('/login'),
            'text': 'Logout'
        }
        
        self.render('display.html')
        
   
'''
@summary: Class containing authentication handlers
'''     
class Auth(webapp2.RequestHandler):

    def render(self, tempName):
        template = jinja_environment.get_template(tempName)
        self.response.out.write(template.render(self.template_values))  
    
    def get(self):
        
        self.template_values = {
            'username': '',
            'headurl': users.create_login_url('/'),
            'text': 'Login'
        }
        
        self.render('login.html')



app = webapp2.WSGIApplication([('/', Handler), ('/display', Handler), ('/login', Auth)],
                              debug=True)
