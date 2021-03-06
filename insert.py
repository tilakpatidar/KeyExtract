import os,json,threading,MySQLdb
import pymongo
files=os.listdir("./cache")
def move(f,success):
	if success:
		os.system("mv ./crawlNEW/"+f+" ./done/"+f)
	else:
		os.system("mv ./crawlNEW/"+f+" ./fail/"+f)
def insertInMongo(dic,idd):
	idd=str(idd)
	client=pymongo.MongoClient()
	d=client.newIndex
	index=d.index
	for kk in dic:
		d.index.update({"keyword":kk},{"$set":{idd:dic[kk]}},upsert=True)
def checkIfIndex(url):
	db = MySQLdb.connect("localhost","root","#srmseONserver1","test" )
	cursor = db.cursor()
	sql = "SELECT `id` from source_main1 where `url`='%s'" % (url)
	try:
	   	cursor.execute(sql)
	   	results = cursor.fetchone()
	   	if results is None:
	   		print "[INFO] Not in Index"
	   		return False
	   	else:
	   		print "In Index"
	   		return True
	except:
   		raise Exception
def insert(url,title,desc):
	db = MySQLdb.connect("localhost","root","#srmseONserver1","test" )
	cursor = db.cursor()
	sql = """INSERT INTO source_main_new(`url`,`title`,`body`)VALUES ('%s','%s','%s');"""%(MySQLdb.escape_string(url),MySQLdb.escape_string(title),MySQLdb.escape_string(desc))
	try:
	   cursor.execute(sql)
	   cursor.execute('SELECT last_insert_id()')
	   v=cursor.fetchone()[0]
	   return v
	   db.commit()
	except Exception as e:
	   print e
	   return -1
	   db.rollback()
	db.close()
def parseFiles(ff):
	tup=open("./cache/"+ff,"r").read().split("###SPLIT###")
	idd=insert(tup[0],tup[1],tup[2])
	dic=json.loads(tup[3])
	if idd!=-1:
		print "[INFO] Inserted in docs"
		if not dic is None:
			insertInMongo(dic,idd)
			print "[INFO] Inserted in index"
			move(ff,True)
			print "[INFO] File moved"
		else:
			move(ff,False)
			print "[INFO] File moved"
	else:
		move(ff,False)
		print "[INFO] File moved"
for ff in files:
	if threading.activeCount()<100:
		threading.Thread(target=parseFiles,args=(ff,)).start()
	else:
		while True:
			if threading.activeCount()<100:
				threading.Thread(target=parseFiles,args=(ff,)).start()
				break
