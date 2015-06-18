import json,re
from bs4 import BeautifulSoup as bs
from collections import Counter
from nltk.corpus import stopwords
stop = stopwords.words('english')
#globals
__config={}
__key_store={}
__soup=None
def load_config():
	"""Loads the global config from the config.json file"""
	try:
		global __config
		f=open("config.json","r").read()
		__config=json.loads(f)
	except Exception as e:
		print "[ERROR] Config Missing ./config.json"
		raise Exception
def load_file(url,css,js):
	"""Loads a html file into dom with css and js files paths"""
	try:
		global __key_store,__soup,__frequency
		load_config()
		html_data=open(url,"r").read()
		__soup=bs(html_data)
		filter_dom()
		createKeyStore()
		__frequency=getFrequency()
	except IOError as e:
		print "[ERROR] File not found :"+url
	except Exception as e:
		#Errors propagate here
		print e
def getFrequency():
	"""Returns dic of keywords to the score"""
	list1=list(removeVerbs(filter_data(__soup.text.lower()).split(" ")))
	counts = Counter(list1)
	#print counts
def createKeyStore():
	allowedTags=__config["ALLOWED"]
	#Finding all meta tags
	metas=__soup.findAll("meta")
	if not metas is None:
		__key_store["meta"]=[]
		for meta in metas:
			__key_store["meta"]=__key_store["meta"]+filter_data(meta.get("content").lower()).split(" ")
		__key_store["meta"]=list(set(__key_store["meta"]))#Removing duplicates
	for allow in allowedTags:
		addTagKeyStore(allow)
	if len(__key_store.keys())==0:
		print "[ERROR] No tags found"
		raise Exception
def addTagKeyStore(tag):
	ts=__soup.findAll(tag)
	if not ts is None:
		__key_store[tag]=[]
		for t in ts:
			__key_store[tag]=__key_store[tag]+filter_data(t.text.lower()).split(" ")
		__key_store[tag]=list(set(__key_store[tag]))#Removing duplicates
def filter_data(data):
	#Removing stop words
	data=removeStopWords(data)
	#Removing new lines and extra spaces
	data=data.replace("\n"," ")
	data=data.replace("\r"," ")
	data=data.replace("\t"," ")
	data=re.sub(r"(\\)(.*?)(\s*)"," ",data)
	#Removing punctuations
	data=re.sub("&(.*?);"," ",data)#&nbsp; etc
	data=remove_punctuations(data)
	data=re.sub("\s+"," ",data)
	return data
def filter_dom():
	global __soup,__config
	for tag in __config["REMOVE"]:
		temp=__soup.findAll(tag)
		if not temp is None:
			for t in temp:
				t.decompose()
def removeVerbs(data):
	"""Removes verbs from data Only remove verbs from html content not special tags like title"""
	return data
def removeStopWords(data):
	"""Removes stop words"""
	#return " ".join([i for i in data.split() if i not in stop])
	return data
def remove_punctuations(s):
        #This one does not remove the hash tags
        try:
                output = re.sub(r'[\'\.\,-\/!<>?$#%\^&\*;:\+{}=\-_`~()\[\]]'," ",s)
                output = re.sub(r'\s+'," ", output).strip()
                return output
        except:
                return ""