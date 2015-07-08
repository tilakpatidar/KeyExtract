import json,re
import nltk,sys
from nltk.stem.lancaster import LancasterStemmer as LS
from urllib2 import urlparse as u
stop = nltk.corpus.stopwords.words('english')
#globals
__config={}
__key_store={}
__soup=None
__url=None
__addWordTag=None
__pageDesc=""
__title=""
lancaster_stemmer = LS()
__stem_cache={}
__once={}
def load_config():
	"""Loads the global config from the config.json file"""
	try:
		global __config
		f=open("config.json","r").read()
		__config=json.loads(f)
	except Exception as e:
		print e
		print "[ERROR] Config Missing ./config.json"
		raise Exception
def getKeywords():
	"""Loads a html file into dom Main function of the program"""
	try:
		global __key_store,__soup,__once
		load_config()
		createKeyStore()
		filter_dom()
		#addWordsFromUrl(__url)#extracts keys from url
		addNormalWords()
		for a in __once.keys():
			try:
				del __key_store[a]
			except KeyError:
				pass
		return __key_store
	except Exception as e:
		raise Exception
def load_dom(dom,url):
	global __soup,__url
	__soup=dom
	__url=url
def addNormalWords():
	"""Adds rest of normal words to the key store"""
	try:
		list1=removeVerbs(filter_data(__soup.find("body").text.lower()))
		addWords(list1,"normal")
	except Exception as e:
		print e
		print "[ERROR] in addNormalWords()"
		raise Exception
def createKeyStore():
	try:
		global __addWordTag,__pageDesc
		allowedTags=__config["ALLOWED"]
		#Finding all meta tags
		try:
			metas=__soup.find_all("meta")
		except:
			return
		if not metas is None:
			temp=[]
			for meta in metas:
				try:
					if meta.get("name")=="description":
						__pageDesc=meta.get("content")
					temp+=filter_data(meta.get("content").lower()).split(" ")
				except:
					#if get is none
					pass
			addWords(temp,"meta")
			removeTag("meta")
		for allow in allowedTags:
			addTagKeyStore(allow)
	except Exception as e:
		print e
		typee, value, traceback = sys.exc_info()
		print traceback.tb_lineno
		print "[ERROR] in createKeyStore()"
		raise Exception
def addTagKeyStore(tag):
	"""Special tags are allowed.Be specific while selecting tag in config.json as taking tags which are usually
	used as parent tags will result is taking entire content Ex: allowing divs will have entire content"""
	global __title
	try:
		if tag=="title":
			t=__soup.find("title")
			if not t is None:
				__title=t.text
		try:
			ts=__soup.find_all(tag)
		except:
			return
		if not ts is None:
			temp=[]
			for t in ts:
				temp=temp+filter_data(t.text.lower()).split(" ")
			addWords(temp,tag)
			removeTag(tag)
	except Exception as e:
		print e
		typee, value, traceback = sys.exc_info()
		print traceback.tb_lineno
		print "[ERROR] in addTagKeyStore()"
		raise Exception
def addWords(li,tag):
	try:
		global __addWordTag
		#if not tag in __config["NO_STEM"]:#No stemming for special tags
		li=map(getStem,li)
		__addWordTag=tag
		map(addWord,li)
		__addWordTag=None
	except Exception as e:
		print e
		print "[ERROR] in addWords()"
def addWord(word):
	global __addWordTag,__once,__key_store
	try:
		temp=__key_store[word]
		if temp >=__config["BASE_COUNT"]:
			try:
				del __once[word]
			except KeyError:
				pass
		__key_store[word]=temp+1
	except KeyError:
		#hence word not present just give its score next time only frequency will be increased
		__key_store[word]=__config["WEIGHT"][__addWordTag]
		__once[word]=0
	except Exception as e:
		print e
		print "[Error in addWord]"
def filter_content(data):
	try:
		data=remove_punctuations(data)
		data=re.sub("\s+"," ",data).strip()
		return data
	except Exception as e:
		print e
		print "[ERROR] in filter_content()"
		raise Exception
def filter_data(data):
	try:
		#Removing stop words
		data=removeStopWords(data)
		return filter_content(data)
	except Exception as e:
		print e
		print "[ERROR] in filter_data()"
		raise Exception
def filter_dom():
	try:
		global __soup,__config
		for tag in __config["REMOVE"]:
			t=__soup.find_all(tag)
			if not t is None:
				for tt in t:
					tt.decompose()
		
	except Exception as e:
		print e
		print "[ERROR] in filter_dom()"
		raise Exception
def removeVerbs(data):
	"""Removes verbs from data. Only remove verbs from body content not special tags like title.
	Most of the words like playing etc are not useful.And if they are,for example a page on HOW TO PLAY FOOTBALL even if we remove verbs from body but we are not removing verbs from special tags as a result we will only
	get usefull verbs in context with the subject as these verbs are present in special tags"""
	try:
		tokens = nltk.word_tokenize(data)
		tagged = nltk.pos_tag(tokens)
		temp=[]
		for t in tagged:
			if t[1][0]!="V":
				temp.append(t[0])
		return temp
	except Exception as e:
		print e
		print "[ERROR] in removeVerbs()"
		raise Exception
def removeStopWords(data):
	"""Removes stop words"""
	try:
		return " ".join([i for i in data.split() if i not in stop])
	except Exception as e:
		print e
		print "[ERROR] in removeStopWords()"
		raise Exception
def remove_punctuations(s):
        #This one does not remove the hash tags
        try:
                output = re.sub(r'[\'\.\,-\/!<>?|$#"%\^&\*;:\+{}=\-_`~()\[\]]'," ",s)
                output = re.sub(r'\s+'," ", output).strip()
                return output
        except Exception as e:
		print "[ERROR] in remove_punctuations()"
		raise Exception
def addWordsFromUrl(url):
	try:
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
		li=filter_data(" ".join(t)).split(" ")
		addWords(li,"url")
	except Exception as e:
		print e
		print "[ERROR] in addWordsFromUrl()"
		raise Exception
def getOccuredWords(data):
	global __soup
	try:
		"""Returns words from data which are present in body"""
		return list(set(__soup.find_element_by_tag_name("body").text.lower().split(" ")).intersection(set(data.split(" "))))
	except Exception as e:
		print e
		print "[ERROR] in getOccuredWords()"
		raise Exception
def removeNonAscii(data):
	return str(filter(lambda x:ord(x)>31 and ord(x)<128,data))
def getStem(word):
	global lmtzr,__stem_cache
	try:
		return __stem_cache[word]
	except KeyError:
		temp=lancaster_stemmer.stem(word)
		__stem_cache[word]=temp
		return temp
	except Exception as e:
		print e
		print "[ERROR] in getStem()"
def removeTag(tag):
	try:
		global __soup
		tags=__soup.find_all(tag)
		if not tags is None:
			for tt in tags:
				tt.decompose()
	except Exception as e:
		print e
		print "[Error in removeTag()]"
def getWordsFromAnchorTags():
	pass
def removeComments(data):
	return re.sub("<!--(.*?)-->","",data)
def removeUnEncoded(data):
	data=data.replace("\\n"," ")
	data=data.replace("\\r"," ")
	data=data.replace("\\t"," ")
	data=re.sub(r"(\\)(.*?)\s"," ",data)
	#Removing punctuations
	data=re.sub("&(.*?);"," ",data)#&nbsp; etc
	return re.sub("\s+"," ",data).strip()
