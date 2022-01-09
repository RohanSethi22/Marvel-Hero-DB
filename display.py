import hidden
import urllib.request, urllib.parse, urllib.error
import hashlib
import sqlite3
import datetime
import json

print('\nWelcome to our superhero database.')
print('\nType "quit" to quit.')
while(True):
	sup_string=input('\nEnter the name of your favourite superhero: ')
	if sup_string=='quit':
		break
	elif len(sup_string)<1:
		sup_string='Shaktimaan'

	print('Searching query in local database...')

	dbcon=sqlite3.connect('marvel_herodb.sqlite')
	cur=dbcon.cursor()
	cur.execute('SELECT * FROM Characters WHERE Name=?',(sup_string,))
	row=cur.fetchone()

	if row is None:
		print('Character not found in local database.')
		print('Initiating character search in remote database...')
		ts= datetime.datetime.utcnow().timestamp()
		hashin=str(ts)+hidden.private_key+hidden.public_key
		code=hashlib.md5(hashin.encode())
		base='https://gateway.marvel.com/v1/public/characters'

		url=base+'?ts='+str(ts)+'&apikey='+str(hidden.public_key)+'&hash='+str(code.hexdigest())+'&nameStartsWith='+sup_string
		try:
			connection=urllib.request.urlopen(url)
		except:
			print("Couldn't fetch data from remote server.\nEnding search.")
			continue

		headers=dict(connection.getheaders())
		data=connection.read().decode()
		info=json.loads(data)
		if info['status']=='Ok':
			#print('Resonse : \n',json.dumps(info,indent=3))
			heroes=[]
			count=0
			for hero in info['data']['results']:
				img_url=hero['thumbnail']['path']+'.'+hero['thumbnail']['extension']
				row=(hero['id'],hero['name'],hero['description'],img_url,hero['urls'][0]['url'])
				print('Character found. Here are the details:')
				print('-'*36)
				print('ID: ',row[0])
				print('Name: ',row[1])
				if row[2]!='':
					print('description: ',row[2])
				print('Image URL: ',row[3])
				print('Character URL: ',row[4])
				cur.execute('INSERT OR IGNORE INTO Characters VALUES(?,?,?,?,?)',(hero['id'],hero['name'],hero['description'],img_url,hero['urls'][0]['url']))
				count+=1
			print('-'*36)
			print(count,'heroes matched the search string.\nThey\'ve been added to database.')
			dbcon.commit()
			cur.close()
		else:
			print('Error',info['status'])
			print("Character not found in remote server.\nEnding search.")
			continue
	else:
		print('Character found. Here are the details:')
		print('-'*36)
		print('ID: ',row[0])
		print('Name: ',row[1])
		if row[2]!='':
			print('description: ',row[2])
		print('Image URL: ',row[3])
		print('Character URL: ',row[4])

print('\nHope you enjoyed it.')
quit()