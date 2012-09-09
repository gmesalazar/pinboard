'''
Created on Aug 28, 2012

@author: Guilherme Salazar 
@email gmesalazar@{acm, gmail}.com
'''

import webapp2
import jinja2
import os

jinja_environment = jinja2.Environment(
                        loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'))

'''
@summary: Handler associated with the main page
'''
class MainPage(webapp2.RequestHandler):
    def get(self):

        template = jinja_environment.get_template('base.html')
        self.response.out.write(template.render())

'''
@summary: Handler associated with the "display" page
'''
class Display(webapp2.RequestHandler):
    def post(self):
        
        template_values = {
            'url': self.request.get('url'),
            'caption': self.request.get('caption')
        }
        
        template = jinja_environment.get_template('display.html')
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage), ('/display', Display)],
                              debug=True)
