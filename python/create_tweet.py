from requests_oauthlib import OAuth1Session
import os
import json
import subprocess
import psycopg2
import sys
import secrets

proc = subprocess.Popen("php /var/www/randomtrialpicker/get_random_trial_id.php", shell=True, stdout=subprocess.PIPE)
pmid = int(proc.stdout.read())

# Connect to MariaDB Platform
try:
    conn = psycopg2.connect(
        user=secrets.user,
        password=secrets.password,
        host=secrets.host,
        database=secrets.database
    )
except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL Platform: {e}")
    sys.exit(1)
# Get Cursor
cur = conn.cursor()
cur.execute(f"SELECT ArticleTitle from pubmed where PMID={pmid};")
for x in cur:
    text = x[0]
title = (text[:180] + ' [...]') if len(text) > 180 else text
cur.close()

# Be sure to add replace the text of the with the text you wish to Tweet. You can also add parameters to post polls, quote Tweets, Tweet with reply settings, and Tweet to Super Followers in addition to other features.
payload = {"text":  f"Today's random trial: '{title}' randomtrialpicker.org/trial?PMID={pmid}"}

# Make the request
oauth = OAuth1Session(
    secrets.consumer_key,
    client_secret=secrets.consumer_secret,
    resource_owner_key=secrets.resource_owner_key,
    resource_owner_secret=secrets.resource_owner_secret
)

# Making the request
response = oauth.post(
    "https://api.twitter.com/2/tweets",
    json=payload,
)

if response.status_code != 201:
    raise Exception(
        "Request returned an error: {} {}".format(response.status_code, response.text)
    )

print("Response code: {}".format(response.status_code))

# Saving the response as JSON
json_response = response.json()
print(json.dumps(json_response, indent=4, sort_keys=True))
