import os, urllib, urllib.request

api_ip = os.environ.get('API_IP')
user = os.environ.get('API_USER')
pwd = os.environ.get('API_PASSWORD')

# create a password manager
password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

# Add the username and password.
# If we knew the realm, we could use it instead of None.
apiUrl = "http://{0}/".format(api_ip)
password_mgr.add_password(None, apiUrl, user, pwd)

handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

# create "opener" (OpenerDirector instance)
opener = urllib.request.build_opener(handler)

# use the opener to fetch a URL
opener.open(apiUrl)

# Install the opener.
# Now all calls to urllib.request.urlopen use our opener.
urllib.request.install_opener(opener)

apiOpen = urllib.request.urlopen