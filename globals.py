import configobj, lbc, os, sys, zipfile
from collections import OrderedDict
if sys.platform.startswith('win'): #only import this if we're on windows
 import accessible_output
 s=accessible_output.speech.Speaker()

def getAppPath():
 """ This will get us the program's directory,
 even if we are frozen using py2exe
 This is from http://www.py2exe.org/index.cgi/WhereAmI """
 if hasattr(sys, "frozen"):
  return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
 return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))

#vars for describing the app
appName="Desktop Bookshare Client"
appDescription="A desktop client to search and download from http://www.bookshare.org."
appVersion="1.01"
appPath=getAppPath()
isBeta=True #when false, "beta software" warning is not shown on startup

import dialogs, pybookshare #down here to avoid circular import problems, sorry

#file extension and book type constants:
zip=".zip"
bks2=".bks2"
brf=["BRF", 0] #the 0 is the Bookshare-required int for this format
daisy=["DAISY", 1] #the 1 is the same but for daisy
prompt=["ask each time", 2] #the 2 is just there since a function in another file always checks numbers, not string values

loggedIn=False
gaveUp=False

#default configuration
defaultConfig={
 'settings':{
  'username': "",
  'password': "",
  'limit':250,
  'extension':zip,
  'format':prompt[1],
  'autoUnzip':True,
  'speakProgressMessages':True,
  'downloadPath':""
 },
 'favorites':{}
}

#load the config file, if it exists
if os.path.exists(os.path.join(appPath, "config.ini")):
 config=configobj.ConfigObj(os.path.join(appPath, "config.ini"))
else:
 #assume first run of app, and so set download location before anything else
 defaultConfig['settings']['downloadPath']=lbc.DialogBrowseForFolder(message="Choose the folder in which downloaded books should be stored")
 #now load defaults since we have no file on which to fall back
 config=configobj.ConfigObj(defaultConfig)
 config.filename=os.path.join(appPath, "config.ini")
 config.write() #create the ini file with default settings

#the following are all used by other files; they are convenience variables since accessing settings is long when you do it a lot
favoriteDict=config['favorites']
username=config['settings']['username']
password=config['settings']['password']
limit=config['settings']['limit']
canSpeak=config['settings']['speakProgressMessages']=='True'
extension=config['settings']['extension']

#create the api object to talk to bookshare
#obviously, do *NOT* use the below key; get your own!
key="zftyt9h75pwxvcxqng534m3g"
bs=pybookshare.BookshareApi(username, password, key=key, limit=limit)

#search string constants and a dict to map them to bsApi search functions:
search_title="Title"
search_author="Author"
search_titleAndAuthor="Title and Author"
search_full="Full"
search_getBooksByAuthor="Get Books by Author"
search_getBooksInCategory="Get All Books in a Category"
#list of search types where category/grade is invalid, so if one of these is selected grade/category will not work
uncategorizedSearch=[search_getBooksByAuthor]
#okay, now map those to the actual api wrapper functions
searchTypes=OrderedDict([
 (search_title, bs.search_title),
 (search_author, bs.search_author),
 (search_titleAndAuthor, bs.search_title_author),
 (search_full, bs.search),
 (search_getBooksByAuthor, bs.getBooksBy),
 (search_getBooksInCategory, bs.getBooksInCategory)
])

#I hard-code this, but use the api wrapper to grab the category list if you want. I figured it'd rarely change, though.
categories=[
 "All Categories",
 "Animals",
 "Art and Architecture",
 "Biographies and Memoirs",
 "Business and Finance",
 "Children's Books",
 "Computers and Internet",
 "Cooking, Food and Wine",
 "Disability-Related",
 "Educational Materials",
 "Entertainment",
 "Gay and Lesbian",
 "Health, Mind and Body",
 "History",
 "Home and Garden",
 "Horror",
 "Literature and Fiction",
 "Military",
 "Mystery and Thrillers",
 "Nonfiction",
 "Outdoors and Nature",
 "Parenting and Family",
 "Poetry",
 "Professional and Technical",
 "Reference",
 "Religion and Spirituality",
 "Romance",
 "Science",
 "Science Fiction and Fantasy",
 "Self-Help",
 "Sports",
 "Teens",
 "Textbooks",
 "Travel",
 "Westerns"
]

grades=[
 "All Grades",
 "Kindergarten",
 "First grade",
 "Second grade",
 "Third grade",
 "Fourth grade",
 "Fifth grade",
 "Sixth grade",
 "Seventh grade",
 "Eighth grade",
 "Ninth grade",
 "Tenth grade",
 "Eleventh grade",
 "Twelfth grade",
 "College Freshman",
 "College Sophomore",
 "College Junior",
 "College Senior",
 "Graduate Student",
 "Adult Ed",
 "Pre-Kindergarten"
]

#used in date function
months={
 '01': 'January',
 '02': 'February',
 '03': 'March',
 '04': 'April',
 '05': 'May',
 '06': 'June',
 '07': 'July',
 '08': 'August',
 '09': 'September',
 '10': 'October',
 '11': 'November',
 '12': 'December'
}

def destroy(dlg, focus=None, clear=None):
 #focuses on the "focus" ctrl name, clears everything in clear, then uses Show(false) to hide dlg
 if focus is not None: dlg.Controls[focus].SetFocus()
 if clear is not None:
  for ctrl in clear:
   dlg.Controls[ctrl].Clear()
  else:
   for ctrl in dlg.Controls:
    if "TextCtrl_" in dlg.Controls[ctrl].GetName(): dlg.Controls[ctrl].Clear()
 return dlg.Show(False)

def getDate(nums):
 #returns a real date from mmddyyyy string of ints
 month=nums[0:2]
 day=nums[2:4]
 year=nums[4:]
 return months[month]+" "+str(day)+", "+str(year)

def testLogin():
 try:
  bs.getUserInfo()
 except pybookshare.ApiError:
  login()

def login(username="", password=""):
 if not loggedIn: dlg_login=dialogs.LoginDialog(username=username, password=password)

def toBiggestBytes(n, x=1, unit='short'):
 #returns a string where n, rounded to x, is in the largest logical measure possible
 i=0 #counter
 units=[" bytes","kb","mb","gb","tb"]
 longUnits=[" bytes","kilobytes","megabytes","gigabytes","terrabytes"]
 n=float(n)
 while(n>=1024):
  n=n/1024.0
  i=i+1
 final=str(round(n, x))
 unit=units[i] if unit=='short' else " "+longUnits[i]
 return final+unit

def download(book, format=None):
 #wraps the pybookshare function to allow for the desired format, logging in, prompting for a format if set to do so, and so on
 if format is None: format=config['settings']['format']
 if config['settings']['username']=="" or config['settings']['password']=="": login()
 if format==brf and not book.brf: #book is only available in daisy...
  downloadAnyway=lbc.DialogConfirm("Format Not Available", "This book is not available in BRF format. Would you like to download the DAISY version instead?")
  if downloadAnyway: format=daisy
  else: return False #no point if user doesn't want daisy book, so exit
 if canSpeak: s.output("Downloading book, please wait.", 1)
 try:
  fileName=bs.download(book, destination=config['settings']['downloadPath'], format=format, extension=config['settings']['extension'])
 except pybookshare.ApiError, e:
  return dialogs.ErrorDialog("Error Downloading Book", e)
 if config['settings']['autoUnzip']=='False': #don't unzip, just finish
  return dialogs.AlertDialog("Book Downloaded", book.title+" was successfully downloaded to "+config['settings']['downloadPath']+".")
 #we returned, so if we got this far, just keep going with the unzip
 if canSpeak: s.output("Book downloaded, now unzipping.", 1)
 fullPath=os.path.join(config['settings']['downloadPath'], fileName+config['settings']['extension'])
 try:
  zf=zipfile.ZipFile(fullPath, 'r')
  zf.setpassword(config['settings']['password'])
  fileCount=len(zf.infolist()) #how many files in zip archive?
  if fileCount==1: #assume brf, so unzip to current dir
   zf.extractall(config['settings']['downloadPath'])
   zf.close() #Windows throws an exception if the file is open when we remove it on the next line
   os.remove(fullPath) #delete zipped book
  else: #assume it is a daisy book
   zf.extractall(os.path.join(config['settings']['downloadPath'], fileName))
   zf.close() #Windows throws an exception if the file is open when we remove it on the next line
   os.remove(fullPath) #delete zipped book
 except zipfile.BadZipfile:
  return dialogs.ErrorDialog("Unzip Error", "The zip file seems to be corrupted. Please try re-downloading it. It may also help to manually delete the current file before attempting to download it again.")
 zf.close() #likely unnecessary, but it never hurts...
 return dialogs.AlertDialog("Success", book.title+" was successfully downloaded and unzipped to "+config['settings']['downloadPath']+".")

def output(text, interrupt):
 #if this fails because "s" is not defined, we're not on windows so accessible_output isn't loaded
 try:
  s.output(text, interrupt)
 except NameError: pass