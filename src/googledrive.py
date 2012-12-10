# Ripped and adapted from the DrEdit Google example application
# https://developers.google.com/drive/examples/python

# DrEdit is licensed under the Apache License, version 2.0
# http://www.apache.org/licenses/LICENSE-2.0.html

import sys
sys.path.append('lib')

import os
import httplib2
import sessions

from google.appengine.ext import db
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.appengine import CredentialsProperty
from oauth2client.appengine import StorageByKeyName

SCOPES = ('https://www.googleapis.com/auth/drive.file '
                            'https://www.googleapis.com/auth/userinfo.email '
                            'https://www.googleapis.com/auth/userinfo.profile')

# Load the secret that is used for client side sessions
# Create one of these for yourself with, for example:
# python -c "import os; print os.urandom(64)" > session-secret
SESSION_SECRET = open(os.path.dirname(__file__) + '/session.secret').read()

class Credentials(db.Model):

    credentials = CredentialsProperty()

def createOAuthFlow(request):

    flow = flow_from_clientsecrets('client_secrets.json', scope='')
    
    flow.redirect_uri = request.request.host_url + '/pin?export=drive'
    return flow

def getSessionCredentials(request):

    session = sessions.LilCookies(request, SESSION_SECRET)
    userid = session.get_secure_cookie(name='userid')
    if not userid:
        return None

    creds = StorageByKeyName(Credentials, userid, 'credentials').get()

    if creds and creds.invalid:
        return None

    return creds

def createService(service, version, creds):

    http = httplib2.Http()
    creds.authorize(http)
    return build(service, version, http=http)
        
def getCodeCredentials(request):

    code = request.request.get('code')
    if not code:
        return None

    oauth_flow = createOAuthFlow(request)

    try:
        creds = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        return None

    users_service = createService('oauth2', 'v2', creds)

    userid = users_service.userinfo().get().execute().get('id')

    session = sessions.LilCookies(request, SESSION_SECRET)
    session.set_secure_cookie(name='userid', value=userid)

    StorageByKeyName(Credentials, userid, 'credentials').put(creds)
    return creds

def redirectAuth(request):
    
    flow = createOAuthFlow(request)

    flow.scope = SCOPES

    uri = flow.step1_get_authorize_url(flow.redirect_uri)
    
    request.redirect(str(uri))