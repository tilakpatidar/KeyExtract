from selenium import webdriver
__driver=None
def initBrowser():
	__driver = webdriver.PhantomJS()
def closeBrowser():
	__driver.quit()
def fetch(url,no_css,no_images):
	"""Return page source and dom object"""
	global __driver
	__driver.get(url)
	return __driver.page_source,__driver
