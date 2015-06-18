import json,re
from bs4 import BeautifulSoup as bs
from collections import Counter
import nltk
from urllib2 import urlparse as u
stop = nltk.corpus.stopwords.words('english')
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
def load_file(html_file,url):
	"""Loads a html file into dom Main function of the program"""
	try:
		global __key_store,__soup,__frequency
		load_config()
		html_data=open(html_file,"r").read()
		__soup=bs(html_data)
		filter_dom()
		createKeyStore()
		__key_store["url"]=addWordsFromUrl(url)
		__frequency=getFrequency()
		print __frequency
	except IOError as e:
		print "[ERROR] File not found :"+url
	except Exception as e:
		#Errors propagate here
		print e
def getFrequency():
	"""Returns dic of keywords to the score"""
	list1=list(removeVerbs(filter_data(__soup.find("body").text.lower())).split(" "))
	counts1 = Counter(list1)
	vals=[]
	for k in __key_store.values():
		vals+=k
	count_dict=list(filter_data(" ".join(vals)).lower().split(" "))
	counts2 = Counter(count_dict)
	for c in counts2:
		counts2[c]=1000
	counts=counts1+counts2
	temp={}
	for c in counts:
		if counts[c]>=__config["BASE_COUNT"]:
			temp[c]=counts[c]
	return temp
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
	tokens = nltk.word_tokenize(data)
	tagged = nltk.pos_tag(tokens)
	temp=[]
	for t in tagged:
		if t[1][0]!="N":
			temp.append(t[0])
	return " ".join(temp).lower()
def removeStopWords(data):
	"""Removes stop words"""
	return " ".join([i for i in data.split() if i not in stop])
def remove_punctuations(s):
        #This one does not remove the hash tags
        try:
                output = re.sub(r'[\'\.\,-\/!<>?$#%\^&\*;:\+{}=\-_`~()\[\]]'," ",s)
                output = re.sub(r'\s+'," ", output).strip()
                return output
        except:
                return ""
def addWordsFromUrl(url):
	parts=u.urlparse(url)
	netloc=parts[1].replace("."," ")
	path=parts[2].replace("/"," ")
	query=parts[4].split("&")
	t=[]
	for q in query:
		try:
			t+=q.split("=")[1].split(" ")
		except IndexError as e:
			t+=q.split("=")[0].split(" ")
	t+=(path+netloc).split(" ")
	#Things to be done removing .com .net etc
	#Filtering enocoding types present in url
	return filter_data(" ".join(t)).split(" ")
	

