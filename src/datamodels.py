'''
Created on Oct 18, 2012

@author: Guilherme Salazar 
@email gmesalazar@gmail.com
'''

from google.appengine.ext import db

'''
@summary: data model for a pin
'''
class Pin(db.Model):
    
    imgUrl = db.StringProperty()
    image = db.BlobProperty()
    width = db.IntegerProperty()
    height = db.IntegerProperty()
    format = db.IntegerProperty()
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
    xCoords = db.StringProperty()
    yCoords = db.StringProperty()