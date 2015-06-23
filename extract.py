import parse as Parse
import browser as Browser
import sys
__url=None
def __main__():
	Browser.initBrowser(no_css=True,no_images=True)#start phantomJS
	data=Browser.fetch(__url)#fetch the rendered page
	#Saving rendered page for future use
	fil=open("./crawlNEW/"+__url.replace("/","##"),"w")
	fil.write(__url+"###split###")
	fil.write(Parse.removeNonAscii(data[0])+"\n")
	fil.close()
	#Passing the driver object to the parser
	Parse.load_dom(data[1],__url)
	Parse.getKeywords()
	Browser.closeBrowser()
if __name__=="__main__":
	__url=sys.argv[1]
	__main__()
