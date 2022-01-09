import hidden
import urllib.request, urllib.parse, urllib.error
import hashlib
import sqlite3
import datetime
import json

ts= datetime.datetime.utcnow().timestamp()
hashin=str(ts)+hidden.private_key+hidden.public_key
code=hashlib.md5(hashin.encode())
base='https://gateway.marvel.com/v1/public/characters'

url=base+'?ts='+str(ts)+'&apikey='+str(hidden.public_key)+'&hash='+str(code.hexdigest())

try:
	connection=urllib.request.urlopen(url)
except:
	print("Couldn't fetch data\nExiting")
	quit()

headers=dict(connection.getheaders())				# python dictionary
data=connection.read().decode()						# large string of response
info=json.loads(data)								# python dictionary
if info['status']=='Ok':
	print('Headers : \n',headers)
	print()
	#print('Resonse : \n',json.dumps(info,indent=3))
	count=0

	dbcon=sqlite3.connect('marvel_herodb.sqlite')
	cur=dbcon.cursor()
	cur.execute('''
		CREATE TABLE IF NOT EXISTS "Characters" (
			"Id"	INTEGER,
			"Name"	TEXT,
			"Description"	TEXT,
			"ImageURL"	TEXT,
			"ResourceURL"	TEXT,
			PRIMARY KEY("Id")
		)
		''')

	for hero in info['data']['results']:
		print(hero['id'],': ',hero['name'])
		img_url=hero['thumbnail']['path']+'.'+hero['thumbnail']['extension']
		cur.execute('INSERT OR IGNORE INTO Characters VALUES(?,?,?,?,?)',(hero['id'],hero['name'],hero['description'],img_url,hero['urls'][0]['url']))
		count+=1
		if count%10==0:
			print('-'*32)
			print('Commiting changes. Please wait.')
			dbcon.commit()
			print('-'*32)
	dbcon.commit()
	cur.close()
	print(count,'heroes fetched and added to database.')
else:
	print('Error',info['status'])