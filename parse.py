import json,re
import nltk
from nltk.stem.lancaster import LancasterStemmer as LS
from urllib2 import urlparse as u
stop = nltk.corpus.stopwords.words('english')
#globals
__config={}
__key_store={}
__soup=None
__url=None
__addWordTag=None
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
		print "[ERROR] Config Missing ./config.json"
		raise Exception
def getKeywords():
	"""Loads a html file into dom Main function of the program"""
	try:
		global __key_store,__soup,__frequency
		load_config()#Loads config from json file
		filter_dom()#removes unwanted tags desc in config.json
		createKeyStore()#extracts keys from special tags defined in config.json
		addWordsFromUrl(__url)#extracts keys from url
		addNormalWords()
		for a in __once.keys():
			del __key_store[a]
		print __key_store
	except IOError as e:
		print "[ERROR] File not found :"+url
	except Exception as e:
		#Errors propagate here
		print e
def load_dom(dom,url):
	global __soup,__url
	__soup=dom
	__url=url
def addNormalWords():
	"""Adds rest of normal words to the key store"""
	try:
		list1=removeVerbs(filter_data(__soup.find_element_by_tag_name("body").text.lower()))
		addWords(list1,"normal")
	except Exception as e:
		print "[ERROR] in addNormalWords()"
		raise Exception
def createKeyStore():
	try:
		global __addWordTag
		allowedTags=__config["ALLOWED"]
		#Finding all meta tags
		metas=__soup.find_elements_by_css_selector("meta")
		if not metas is None:
			temp=[]
			for meta in metas:
				temp+=filter_data(meta.get_attribute("content").lower()).split(" ")
			addWords(temp,"meta")
			removeTag("meta")
		for allow in allowedTags:
			addTagKeyStore(allow)
	except Exception as e:
		print "[ERROR] in createKeyStore()"
		raise Exception
def addTagKeyStore(tag):
	"""Special tags are allowed.Be specific while selecting tag in config.json as taking tags which are usually
	used as parent tags will result is taking entire content Ex: allowing divs will have entire content"""
	try:
		ts=__soup.find_elements_by_css_selector(tag)
		if not ts is None:
			temp=[]
			for t in ts:
				temp=temp+filter_data(t.text.lower()).split(" ")
			addWords(temp,tag)
			removeTag(tag)
	except Exception as e:
		print "[ERROR] in addTagKeyStore()"
		raise Exception
def addWords(li,tag):
	global __addWordTag
	if not tag in __config["NO_STEM"]:#No stemming for special tags
		li=map(getStem,li)
	__addWordTag=tag
	map(addWord,li)
	__addWordTag=None
def addWord(word):
	global __addWordTag,__once,__key_store
	try:
		temp=__key_store[word]
		if temp==(__config["BASE_COUNT"]-1):
			del __once[word]
		__key_store[word]=temp+1
	except KeyError:
		#hence word not present just give its score next time only frequency will be increased
		__key_store[word]=__config["WEIGHT"][__addWordTag]
		__once[word]=0
def filter_data(data):
	try:
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
	except Exception as e:
		print "[ERROR] in filter_data()"
		raise Exception
def filter_dom():
	try:
		global __soup,__config
		for tag in __config["REMOVE"]:
			__soup.execute_script("""var element = document.getElementsByTagName('"""+tag+"""');
for (index = element.length - 1; index >= 0; index--) {
    element[index].parentNode.removeChild(element[index]);
}
//js code to remove comments and unnecessary whitespaces and new lines
function clean(node)
{
  for(var n = 0; n < node.childNodes.length; n ++)
  {
    var child = node.childNodes[n];
    if
    (
      child.nodeType === 8 
      || 
      (child.nodeType === 3 && !/\S/.test(child.nodeValue))
    )
    {
      node.removeChild(child);
      n --;
    }
    else if(child.nodeType === 1)
    {
      clean(child);
    }
  }
}
clean(document);

""");
	except Exception as e:
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
		print "[ERROR] in removeVerbs()"
		raise Exception
def removeStopWords(data):
	"""Removes stop words"""
	try:
		return " ".join([i for i in data.split() if i not in stop])
	except Exception as e:
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
		print "[ERROR] in addWordsFromUrl()"
		raise Exception
def getOccuredWords(data):
	global __soup
	try:
		"""Returns words from data which are present in body"""
		return list(set(__soup.find_element_by_tag_name("body").text.lower().split(" ")).intersection(set(data.split(" "))))
	except Exception as e:
		print "[ERROR] in getOccuredWords()"
		raise Exception
def removeNonAscii(data):
	return str(filter(lambda x:ord(x)>31 and ord(x)<128,data))
def getStem(word):
	global lancaster_stemmer,__stem_cache
	try:
		return __stem_cache[word]
	except KeyError:
		temp=lancaster_stemmer.stem(word)
		__stem_cache[word]=temp
		return temp
def removeTag(tag):
	global __soup
	__soup.execute_script("""var element = document.getElementsByTagName('"""+tag+"""');
for (index = element.length - 1; index >= 0; index--) {
    element[index].parentNode.removeChild(element[index]);
}""")
def getWordsFromAnchorTags():
	pass
