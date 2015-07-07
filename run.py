import os
from bs4 import BeautifulSoup as bs
import MySQLdb
import pymongo
files=os.listdir("/home/srmse/Desktop/Git/data")
def insertInMongo(word,dic):
	client=pymongo.MongoClient()
	d=client.stemindex
	index=d.index
	for kk in dic:
		d.index.update({"keyword":word},{"$set":{kk:dic[kk]}},{"upsert":"true"})
def checkIfIndex(url):
	db = MySQLdb.connect("localhost","root","#srmseONserver1","test" )
	cursor = db.cursor()
	sql = "SELECT `id` from source_main1 where `url`='%s'" % (url)
	try:
	   	cursor.execute(sql)
	   	results = cursor.fetchone()
	   	if results is None:
	   		print "Not in Index"
	   		return False
	   	else:
	   		print "In Index"
	   		return True
	except:
   		raise Exception
def insert(url,title,desc):
	db = MySQLdb.connect("localhost","root","#srmseONserver1","test" )
	cursor = db.cursor()
	sql = """INSERT INTO source_main_new(`url`,`title`,`desc`)VALUES ('%s','%s','%s');SELECT LAST_INSERT_ID();"""%(url,title,desc)
	try:
	   cursor.execute(sql)
	   return cursor.fetchone()[0]
	   db.commit()
	except:
	   db.rollback()
	db.close()
for f in files:
	try:
		import parseBS4 as p
		file_data=open(f,"r").read()
		temp=file_data.split("###SPLIT###")
		url=temp[0]
		data=temp[1]
		soup=bs(p.removeComments(data))
		p.load_dom(soup,url)
		p.getKeywords()
		if not checkIfIndex(url):
			idd=insert(url,p.__title,p.__pageDesc)
	except:
		pass
