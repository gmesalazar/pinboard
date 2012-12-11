import sys
sys.path.append('lib')

import gdata.alt.appengine
import gdata.photos.service

from google.appengine.api import urlfetch

class WebPicasa(gdata.photos.service.PhotosService):

    def __init__(self, scope, email):
        gdata.photos.service.PhotosService.__init__(self)
        gdata.alt.appengine.run_on_appengine(self)
        self.scope = scope
        self.email = email

    def getAuthSubUrl(self, requestContext):
        
        redirect = requestContext.request.host_url + '/pin?export=picasa'
        scope = self.scope
        secure = False
        session = True
        gd_client = gdata.photos.service.PhotosService()
        
        return gd_client.GenerateAuthSubURL(redirect, scope, secure, session)
    
    def getSessionToken(self, requestContext):
        
        auth_token = gdata.auth.extract_auth_sub_token_from_url(requestContext.request.url)
        stored_token = self.token_store.find_token(self.scope)
        
        try:
            self.AuthSubTokenInfo()
        except gdata.service.RequestError:
            stored_token = None
        except gdata.service.NonAuthSubToken:
            stored_token = None

        
        if stored_token and stored_token.valid_for_scope(self.scope):
            
            self.current_token = stored_token
            return stored_token
        
        elif auth_token:

            session_token = self.upgrade_to_session_token(auth_token)
            self.token_store.add_token(session_token)
            self.current_token = session_token
            return session_token
        
        else:
            return None
    
    def connect(self, requestContext):
        
        token = self.getSessionToken(requestContext)
        if not token:
            self.redirect(self.getAuthSubUrl(self).to_string())
            
    
    #TODO: correct the 'Title" part, so that the Web Picasa image gets a title/caption 
    def insertImage(self, album, title, image, mime):
       
        contentLength = len(image)
        result = urlfetch.fetch(url=album,
            method=urlfetch.POST,
            follow_redirects=False,
            payload=image,
            headers={'Authorization': str(self.current_token),
                     'Content-Length': contentLength,
                     'Content-Type': mime,
                     'Title': title})
        return result