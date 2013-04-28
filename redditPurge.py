#!/usr/bin/python

import time, sys, json
import requests

things_list = list()
karma = 0;


#
# Get username & password from arguments
#

if len(sys.argv) == 3:
    username = sys.argv[1]
    password = sys.argv[2]
else:
    print 'usage: '+sys.argv[0]+' username password'
    sys.exit()


#
# Do login
#

head = {'User-Agent': 'reddit purge 0.1'}                                                                             
client = requests.session()
data = {'user': username, 'passwd': password, 'api_type': 'json'}
r = client.post('https://ssl.reddit.com/api/login', data=data, headers=head)

# Check if login was successful & store modhash, otherwise exit
try:
    modhash = r.json()['json']['data']['modhash']
except:
    if 'json' in r.json().keys():
        if 'errors' in r.json()['json'].keys():
            print ('[ ERROR ] ' + str(r.status_code) + ': ' +
               r.json()['json']['errors'][0][0] + ' ' + 
               r.json()['json']['errors'][0][1])
        else:
           print '[ ERROR ] getting modhash' 
    else:
        print '[ ERROR ] getting modhash'
    sys.exit()


#
# Get first 100 things
#

print 'please wait while your things are fetched...'
rUrl = 'http://www.reddit.com/user/'+username+'/overview.json?limit=100'
r = client.get(rUrl, headers=head)

# Make sure things were found
if len(r.json()['data']['children']) > 0:
    # Fetch each thing's ID
    for thing in xrange(0, len(r.json()['data']['children'])):
        # and save it to the list
        things_list.append(r.json()['data']['children'][thing]['data']['name'])
        karma += r.json()['data']['children'][thing]['data']['ups']
        karma -= r.json()['data']['children'][thing]['data']['downs']


# If not, display the best error we can
else:
    if 'json' in r.json().keys():
        if 'errors' in r.json()['json'].keys():
            print ('[ ERROR ] ' + str(r.status_code) + ': ' +
               r.json()['json']['errors'][0][0] + ' ' + 
               r.json()['json']['errors'][0][1])
        else:
           print '[ ERROR ] fetching things' 
    else:
        print '[ ERROR ] fetching things'
    sys.exit()


#
# If there are more things, fetch them until we run out
#

if r.json()['data']['after'] != None:
    while True:
        r = client.get(rUrl+'&after='+r.json()['data']['after'], headers=head)

        # Make sure things were found
        if len(r.json()['data']['children']) > 0:
            # Fetch each thing's ID
            for thing in xrange(0, len(r.json()['data']['children'])):
                # Store every thing ID in the list
                things_list.append(
                    r.json()['data']['children'][thing]['data']['name'])
                karma += r.json()['data']['children'][thing]['data']['ups']
                karma -= r.json()['data']['children'][thing]['data']['downs']

        # If not, display the best error we can
        else:
            if 'json' in r.json().keys():
                if 'errors' in r.json()['json'].keys():
                    print ('[ ERROR ] ' + str(r.status_code) + ': ' +
                       r.json()['json']['errors'][0][0] + ' ' + 
                       r.json()['json']['errors'][0][1])
                else:
                   print '[ ERROR ] fetching things' 
            else:
                print '[ ERROR ] fetching things'
            sys.exit()

        # We're out of things, so stop fetching more
        if r.json()['data']['after'] == None:
            break

        # Otherwise there are more things, continue fetching them
        else:
            # Reddit's API rate limit is 2s
            time.sleep(2)


#
# Now delete all the things!
#

print 'done fetching! you\'re sacrificing ' + str(karma) + ' karma today!'
print 'now, delete all the things:'

for thing_id in things_list:
    # Try deleting the thing
    data = {'id': thing_id, 'uh': modhash}
    r = client.post('http://www.reddit.com/api/del', data=data, headers=head)
    print '[ '+str(r.status_code)+' ] ' + thing_id

    # Reddit's API rate limit is 2s
    time.sleep(2)
