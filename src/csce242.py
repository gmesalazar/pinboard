'''
Created on Aug 28, 2012

@author: Guilherme Salazar 
@email gmesalazar@{acm, gmail}.com
'''

import webapp2
import jinja2
import os

from google.appengine.api import users

jinja_environment = jinja2.Environment(
                        loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'))

'''
@summary: Handler associated with the main page
'''
class MainPage(webapp2.RequestHandler):
    def get(self):
        
        user = users.get_current_user()
        
        if user:
            template_values = {
                'username': user.nickname() + ' ',
                'headurl': users.create_logout_url("/login"),
                'text': 'Logout'
            }
            
            template = jinja_environment.get_template('base.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect('/login')

'''
@summary: Handler associated with the "display" page
'''
class Display(webapp2.RequestHandler):
    def post(self):
        
        user = users.get_current_user()
        
        template_values = {
            'url': self.request.get('url'),
            'caption': self.request.get('caption'),
            'username': user.nickname() + ' ',
            'headurl': users.create_logout_url('/login'),
            'text': 'Logout'
        }
        
        template = jinja_environment.get_template('display.html')
        self.response.out.write(template.render(template_values))
        
class Login(webapp2.RequestHandler):
    def get(self):
        
        template_values = {
            'username': '',
            'headurl': users.create_login_url('/'),
            'text': 'Login'
        }
        
        template = jinja_environment.get_template('login.html')
        self.response.out.write(template.render(template_values))
 


app = webapp2.WSGIApplication([('/', MainPage), ('/display', Display), ('/login', Login)],
                              debug=True)
