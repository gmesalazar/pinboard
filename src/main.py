'''
Created on Aug 28, 2012

@author: Guilherme Salazar 
@email gmesalazar@gmail.com
'''

from handlers import *

urlmap = [('/', MainPage), 
          ('/pin/(.[0-9]*)/?', PinHandler),
          ('/board/(.[0-9]*)/?', BoardHandler),
          ('/board/?', BoardsHandler),
          ('/pin/?', PinsHandler), ('/login', LoginHandler),
          ('/.*', NotFoundPageHandler)]

app = webapp2.WSGIApplication(urlmap, debug=True)