#!/usr/bin/env python3

#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
With this Python3 script you can selectively copy your subscriptions from one
StatusNet [1] instance to another. The script runs in the terminal and does not
need any command line parameters. All you need to do is change the credentials
for the two StatusNet instances (see below) and answer some yes/no questions.

If you encounter any problems feel free to contact me [2] or patch them by
yourself.

Have fun!
  bavatar / Tobias Diekershoff

[1]  http://status.net
[2]  tobias.diekershoff~att~gmx.net
     http://diekershoff.homeunix.net/statusnet/bavatar/
     http://identi.ca/bavatar
"""

###  identica credentials
identica = {
        'user':'USER_HERE',
        'api':'https://PREVIOUS_INSTANCE/api/'
        }
### main SN installation
sn = {
        'user':'NEW_USER',  # your username
        'password':'SUPER_SECRET_PASSWORD',       # your password
        'api':'https://NEW_INSTANCE/api/'         # base api
     }

#
#   That should be all
#

import json, urllib.request
from urllib.parse import urlencode
import subprocess
from sys import exit

def ask_to_connect(friend):
    """
    ask for confirmation to follow that 'friend' after displaying some
    informations about that particular one.
    """
    print('===== %s (%s) =====\n  [%s]' % (friend['screen_name'],
        friend['name'], friend['description']))
    yn = input('Shall I subscribe? [y/N] > ')
    return yn.upper() == 'Y'

#
#  fetch the friend lists from the source and the target StatusNet installation
#  for comparison during the subscription process later
#
friends_from = urllib.request.urlopen(identica['api']+'/statuses/friends/%s.json' %
        identica['user']).read().decode('UTF-8')
friends_there = urllib.request.urlopen(sn['api']+'statuses/friends/%s.json' %
        sn['user']).read().decode('UTF-8')
jfriends_from = json.loads( friends_from )
jfriends_there = json.loads( friends_there )

#
#  set up the connection at the target installation so that we can post notices
#  there to subscribe to some accounts at any given StatusNet installation
#
pwd_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
pwd_mgr.add_password(None, sn['api'], sn['user'], sn['password'])
handler = urllib.request.HTTPBasicAuthHandler(pwd_mgr)
opener = urllib.request.build_opener(handler)
urllib.request.install_opener(opener)

#  get a list with profile urls of the friends do not we already have to avoid
#  duplicate subscription error messages that we need to handle otherwise...
urls = []
for f in jfriends_there:
    urls.append(f['statusnet_profile_url'])
for f in jfriends_from:
    aurl = f['statusnet_profile_url']
    if not aurl in urls:
        #  ok if the profile url is not already subscribed then ask the user if
        #  s/he wants to and then do so.
        if ask_to_connect(f):
            themsg = urlencode( {'status':"follow %s" % aurl} )
            urllib.request.urlopen(sn['api']+'/statuses/update.json?%s' % themsg, '')
