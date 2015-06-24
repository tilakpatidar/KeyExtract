import json,re
from collections import Counter
import nltk
from urllib2 import urlparse as u
stop = nltk.corpus.stopwords.words('english')
#globals
__config={}
__key_store={}
__soup=None
__url=None
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
		__key_store["url"]=addWordsFromUrl(__url)#extracts keys from url
		__frequency=getFrequency()
		#get frequency from body tag only words above base_count defined in config.json will be obtained
		print __frequency
	except IOError as e:
		print "[ERROR] File not found :"+url
	except Exception as e:
		#Errors propagate here
		print e
def load_dom(dom,url):
	global __soup,__url
	__soup=dom
	__url=url
def getFrequency():
	"""Returns dic of keywords to the score"""
	try:
		list1=removeVerbs(filter_data(__soup.find_element_by_tag_name("body").text.lower()))
		counts1 = Counter(list1)
		vals=[]
		for k in __key_store.values():
			vals+=k
		count_dict=list(filter_data(" ".join(vals)).split(" "))
		counts2 = Counter(count_dict)
		temp={}
		temp["NORMAL_TAGS"]={}
		temp["SPECIAL_TAGS"]=dict(counts2)
		for c in counts1:
			if counts1[c]>=__config["BASE_COUNT"]:
				temp["NORMAL_TAGS"][c]=counts1[c]
		return temp
	except Exception as e:
		print "[ERROR] in getFrequency()"
		raise Exception
def createKeyStore():
	try:
		allowedTags=__config["ALLOWED"]
		#Finding all meta tags
		metas=__soup.find_elements_by_css_selector("meta")
		if not metas is None:
			__key_store["meta"]=[]
			temp=[]
			for meta in metas:
				temp+=meta.get_attribute("content").lower().split(" ")
			#__key_store["meta"]=getOccuredWords(filter_data(" ".join(temp)))
			__key_store["meta"]=list(set(temp))#Removing duplicates
			print __key_store["meta"]
		for allow in allowedTags:
			addTagKeyStore(allow)
		if len(__key_store.keys())==0:
			print "[ERROR] No tags found"
			raise Exception
	except Exception as e:
		print "[ERROR] in createKeyStore()"
		raise Exception
def addTagKeyStore(tag):
	"""Special tags are allowed.Be specific while selecting tag in config.json as taking tags which are usually
	used as parent tags will result is taking entire content Ex: allowing divs will have entire content"""
	try:
		ts=__soup.find_elements_by_css_selector(tag)
		if not ts is None:
			__key_store[tag]=[]
			for t in ts:
				__key_store[tag]=__key_store[tag]+filter_data(t.text.lower()).split(" ")
			__key_store[tag]=list(set(__key_store[tag]))#Removing duplicates
	except Exception as e:
		print "[ERROR] in addTagKeyStore()"
		raise Exception
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
		return filter_data(" ".join(t)).split(" ")
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
