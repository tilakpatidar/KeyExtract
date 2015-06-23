from selenium import webdriver
__driver=None
def initBrowser(no_css,no_images):
	global __driver
	options = []
	if no_images:
		options.append('--load-images=false')
	__driver = webdriver.PhantomJS('/usr/local/bin/phantomjs',service_args=options)
def closeBrowser():
	__driver.quit()
def fetch(url):
	"""Return page source and dom object"""
	global __driver
	__driver.get(url)
	return __driver.page_source,__driver
