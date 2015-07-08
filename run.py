import os,json
from bs4 import BeautifulSoup as bs
import MySQLdb
import pymongo
import threading
files=os.listdir("./crawlNEW")
def move(f,success):
	if success:
		os.system("mv ./crawlNEW/"+f+" ./done/"+f)
	else:
		os.system("mv ./crawlNEW/"+f+" ./fail/"+f)
def parse_pages(f):
	try:
		print "###New Record###"
		import parseBS4 as p
		file_data=open("./crawlNEW/"+f,"r").read()
		print "[INFO] File read"
		temp=file_data.split("###split###")
		url=temp[0]
		data=p.removeUnEncoded(temp[1])
		soup=bs(p.removeComments(data))
		p.load_dom(soup,url)
		print "[INFO] Loaded Dom"
		dic=p.getKeywords()
		if not dic is None:
			print "[INFO] Got keywords"
			if p.__pageDesc=="":
				b=p.__soup.find("body")
				if not b is None:
					p.__pageDesc=b.text[0:400]
			fi=open("./cache/"+url.replace("/","##"),"w")
			text=url+"###SPLIT###"+p.filter_content(p.removeUnEncoded(p.__title))+"###SPLIT###"+p.filter_content(p.removeUnEncoded(p.__pageDesc))+"###SPLIT###"+json.dumps(dic)
			fi.write(str(text))
			fi.close()
	except Exception as e:
		print "[ERROR] From parser"
		move(f,False)
def parse_process(files):
	for f in files:
		try:
			if threading.activeCount()<100:
				threading.Thread(target=parse_pages,args=(f,)).start()
			else:
				while True:
					if threading.activeCount()<100:
						threading.Thread(target=parse_pages,args=(f,)).start()
						break
		except Exception as e:
			print e
			
parse_process(files)
