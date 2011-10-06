import globals, lbc, pybookshare
import wx

"""
This file holds a bunch of classes that all subclass lbc.Dialog, so each of them needs a custom event handler to handle any events needed (what buttons do, what happens when a list selection changes, and so on). For the most part, I think this code is pretty clear, but I'll comment anything I think could be confusing.
"""

class AlertDialog(object):
 #somewhat easier DialogShow object, needing only title and message

 def __init__(self, title, message, *args, **kwords):
  self.title=title
  self.message=message
  lbc.DialogShow(title=self.title, message=self.message, *args, **kwords)


class ErrorDialog(AlertDialog):
 #a dialog that alerts, but has a flag set to show an error instead of a happier dialog type

 def __init__(self, *args, **kwords):
  return AlertDialog.__init__(self, style=wx.ICON_ERROR, *args, **kwords)


class MainDialog(lbc.Dialog):
 #the main dialog for the application

 def __init__(self, title=globals.appName, buttons=[], handler=None, *args, **kwords):
  lbc.Dialog.__init__(self, title=title, *args, **kwords)
  self.lst_favorites=self.AddListBox(label="Favorites", names=globals.favoriteDict.keys(), values=globals.favoriteDict.values())
  self.btn_open=self.AddButton(label="Open Favorite")
  self.btn_open.SetDefault()
  self.btn_delete=self.AddButton(label="Delete Favorite")
  self.btn_newSearch=self.AddButton(label="New &Search")
  self.AddBand()
  self.btn_viewLatest=self.AddButton(label="View &Latest Content")
  self.btn_mostPopular=self.AddButton(label="View Most &Popular Content")
  self.btn_options=self.AddButton(label="Set P&references")
  self.btn_close=self.AddButton(label="Close")
  if handler is None: handler=self.eventHandler
  self.Complete(buttons=buttons, handler=handler)

 def eventHandler(self, dlg, event, name):
  if self.lst_favorites.GetCount()==0: #hide the list and its "open" button
   self.lst_favorites.Hide()
   self.btn_open.Hide()
   self.btn_delete.Hide()
   self.Layout()
  favoriteIndex=self.lst_favorites.GetSelection() #which favorite was selected
  favorite=self.lst_favorites.GetStringSelection() #which favorite was selected
  if lbc.IsCloseEvent(event) or (name==self.btn_close.GetName() and lbc.IsButtonEvent(event)): return self.Destroy()
  elif name==self.btn_newSearch.GetName() and lbc.IsButtonEvent(event): #pop up new search dlg
   return NewSearchDialog()
  elif name==self.btn_open.GetName() and lbc.IsButtonEvent(event): #open selected favorite
   if self.lst_favorites.GetCount()==0: return ErrorDialog("No Favorites", "There are no favorites to open.")
   if favoriteIndex<0: favoriteIndex=0 #if none selected, select the first one
   return self.openFavorite(favorite)
  elif name==self.btn_delete.GetName() and lbc.IsButtonEvent(event): #delete selected favorite
   if lbc.DialogConfirm(title="Delete Favorite", message="Are you sure you want to delete this favorite?")=='Y':
    del globals.config['favorites'][favorite]
    globals.config.write()
    self.lst_favorites.Delete(favoriteIndex)
    self.lst_favorites.SetFocus()
    self.Layout()
  elif name==self.btn_mostPopular.GetName() and lbc.IsButtonEvent(event):
   if globals.canSpeak: globals.output("Loading most popular books, please wait.", 1)
   try:
    results=globals.bs.getPopular() #search for the text
   except pybookshare.ApiError, e:
    return ErrorDialog("Error!", e)
   return SearchResultsDialog(title="Most Popular Books", favoriteable=False, results=results)
  elif name==self.btn_viewLatest.GetName() and lbc.IsButtonEvent(event):
   if globals.canSpeak: globals.output("Loading a list of the latest additions to BookShare, please wait.", 1)
   try:
    results=globals.bs.getLatest() #search for the latest additions to Bookshare
   except pybookshare.ApiError, e:
    return ErrorDialog("Error!", e)
   return SearchResultsDialog(title="Most Recent Books", favoriteable=False, results=results)
  elif name==self.btn_options.GetName() and lbc.IsButtonEvent(event):
   return OptionsDialog()

 def openFavorite(self, fav):
  #uses info in config file to see which favorite is being opened, then re-searches
  text=globals.config['favorites'][fav][0]
  type=globals.config['favorites'][fav][1]
  category=globals.config['favorites'][fav][2]
  grade=globals.config['favorites'][fav][3]
  if type not in globals.searchTypes.keys(): return ErrorDialog("Error in Favorite", "The selected favorite cannot be opened; it seems to be corrupted somehow. Please delete it and re-save the favorite by performing the search again.")
  if globals.canSpeak: globals.output("Opening favorite, please wait.", 1)
  try: #perform the search again...
   results=globals.searchTypes[type](text, category=category, grade=grade) #search for the text
  except pybookshare.ApiError, e:
   return ErrorDialog("Error!", e.number+", "+e.message)
  return SearchResultsDialog(searchTerms=text, searchType=type, results=results, category=category, grade=grade)


class NewSearchDialog(lbc.Dialog):
 #dialog for performing a new search

 def __init__(self, title="New Search", buttons=[], handler=None, *args, **kwords):
  lbc.Dialog.__init__(self, title=title, *args, **kwords)
  self.txt_search=self.AddTextCtrl(label="Search Terms:")
  self.AddBand()
  self.lst_searchTypes=self.AddListBox(label="Search &Type:", names=globals.searchTypes.keys())
  self.lst_categories=self.AddListBox(label="Category:", names=globals.categories)
  self.lst_grades=self.AddListBox(label="Grade:", names=globals.grades)
  self.AddBand()
  self.btn_search=self.AddButton(label="Start Search")
  self.btn_search.SetDefault()
  self.btn_cancel=self.AddButton(label="Cancel")
  if handler is None: handler=self.eventHandler
  self.Complete(buttons=buttons, handler=handler)

 def eventHandler(self, dlg, event, name):
  if lbc.IsCloseEvent(event) or (name==self.btn_cancel.GetName() and lbc.IsButtonEvent(event)): return globals.destroy(self, self.txt_search.GetName(), [self.txt_search.GetName()])
  elif name==self.lst_searchTypes.GetName() and lbc.IsListChangeEvent(event): #show/hide category/grades depending on search type
   if self.lst_searchTypes.GetStringSelection() in globals.uncategorizedSearch:
    self.lst_categories.Hide()
    self.lst_grades.Hide()
   else: #show them in case they were hidden by passing over a search type that would hide them
    self.lst_categories.Show()
    self.lst_grades.Show()
   self.Layout()
  elif name==self.btn_search.GetName() and lbc.IsButtonEvent(event): #do the search
   text=self.txt_search.GetValue()
   grade=None
   category=None
   typeIndex=self.lst_searchTypes.GetSelection()
   categoryIndex=self.lst_categories.GetSelection()
   gradeIndex=self.lst_grades.GetSelection()
   if typeIndex<0: typeIndex=0
   #the next 2 say >0 because selection 0 is for leaving the option unspecified
   if categoryIndex>0: category=globals.categories[categoryIndex]
   if gradeIndex>0: grade=globals.grades[gradeIndex]
   searchType=globals.searchTypes.keys()[typeIndex]
   if text=="" and searchType!=globals.search_getBooksInCategory: #only category searches can be blank, since they just list all books in that category
    return ErrorDialog("No Search Terms", "You did not enter anything to search for. Please enter your search terms and try again.")
   if searchType==globals.search_getBooksInCategory:
    if categoryIndex==0: return ErrorDialog("No Category Selected", "You must select a category before the books in that category can be retrieved. Please choose a category and try again.")
    text="all books in "+category+" category"
   if globals.canSpeak: globals.output("Searching, please wait.", 1)
   try:
    results=globals.searchTypes[searchType](text, category=category, grade=grade) #search for the text
   except pybookshare.ApiError, e:
    return ErrorDialog("Error!", e.message)
   SearchResultsDialog(searchTerms=text, searchType=globals.searchTypes.keys()[typeIndex], results=results, category=category, grade=grade)
   return self.Destroy()


class SearchResultsDialog(lbc.Dialog):
 #dialog for showing search results

 def __init__(self, title=None, buttons=[], handler=None, searchTerms="", searchType="", results=None, favoriteable=True, category="", grade="", *args, **kwords):
  if title is None: title=results.message+" for "+str(searchTerms)
  self.favoriteable=favoriteable
  lbc.Dialog.__init__(self, title=title, *args, **kwords)
  self.results=results
  self.resultText=[]
  for res in self.results: self.resultText.append(res.title+", by "+res.authorStr)
  self.lst_results=self.AddListBox(label="Results", names=self.resultText)
  self.AddBand()
  self.memo_info=self.AddMemo(label="Book Info:", readonly=True)
  self.AddBand()
  self.btn_moreInfo=self.AddButton(label="More &Information")
  self.btn_download=self.AddButton(label="Download")
  self.btn_download.SetDefault()
  self.btn_author=self.AddButton(label="View All Books by This &Author")
  if self.favoriteable: self.btn_favorite=self.AddButton(label="Save Search to Favorites")
  self.AddBand()
  self.btn_prev=self.AddButton(label="Previous Results Page")
  self.btn_next=self.AddButton(label="Next Results Page")
  self.btn_first=self.AddButton(label="First Results Page")
  self.btn_last=self.AddButton(label="Last Results Page")
  self.btn_close=self.AddButton(label="Close")
  if self.results.page==1:
   self.btn_prev.Hide()
   self.btn_first.Hide()
  if self.results.page==self.results.pages:
   self.btn_next.Hide()
   self.btn_last.Hide()
  self.searchName=searchTerms+" ("+searchType+" search)"
  self.searchTerms=searchTerms
  self.searchType=searchType
  self.category=category
  self.grade=grade
  if self.category is None: self.category=""
  if self.grade is None: self.grade=""
  if handler is None: handler=self.eventHandler
  self.Complete(buttons=buttons, handler=handler)

 def eventHandler(self, dlg, event, name):
  result=self.lst_results.GetSelection()
  if lbc.IsCloseEvent(event) or (name==self.btn_close.GetName() and lbc.IsButtonEvent(event)): return globals.destroy(self, self.lst_results.GetName(), [self.lst_results.GetName()])
  elif name==self.lst_results.GetName() and (lbc.IsFocusEvent(event) or lbc.IsListChangeEvent(event)):
   #update info box with current item when user changes selection or lands on list
   self.memo_info.SetValue(self.getInfo(self, self.results[result], ["longSynopsis"]))
  elif self.favoriteable and name==self.btn_favorite.GetName() and lbc.IsButtonEvent(event): #save this search to the favorites section of config
   globals.config['favorites'][self.searchName]=[str(self.searchTerms), self.searchType, self.category, self.grade]
   try:
    globals.config.write()
    return AlertDialog("Success", "The favorite has been saved.")
   except:
    return ErrorDialog("Error", "There was an error trying to save the favorite. Please try closing the program and re-launching it, then search again.")
  elif name==self.btn_download.GetName() and lbc.IsButtonEvent(event):
   if globals.config['settings']['format']!=str(globals.prompt[1]): #download book in preferred format
    globals.download(self.results[result])
   else: return DownloadDialog(self.results[result])
  elif name==self.btn_moreInfo.GetName() and lbc.IsButtonEvent(event): #use an api call to show all info about the book
   return BookInfoDialog(self.results[result])
  elif name==self.btn_prev.GetName() and lbc.IsButtonEvent(event):
   if globals.canSpeak: globals.output("Loading previous "+str(globals.limit)+" results, please wait.", 1)
   self.results.prevPage()
   self.Destroy()
   return SearchResultsDialog(searchTerms=self.searchTerms, searchType=self.searchType, results=self.results, category=self.category, grade=self.grade)
  elif name==self.btn_next.GetName() and lbc.IsButtonEvent(event):
   if globals.canSpeak: globals.output("Loading next "+str(globals.limit)+" results, please wait.", 1)
   self.results.nextPage()
   self.Destroy()
   return SearchResultsDialog(searchTerms=self.searchTerms, searchType=self.searchType, results=self.results, category=self.category, grade=self.grade)
  elif name==self.btn_first.GetName() and lbc.IsButtonEvent(event):
   if globals.canSpeak: globals.output("Loading first "+str(globals.limit)+" results, please wait.", 1)
   self.results.getPage(1, True)
   self.Destroy()
   return SearchResultsDialog(searchTerms=self.searchTerms, searchType=self.searchType, results=self.results, category=self.category, grade=self.grade)
  elif name==self.btn_last.GetName() and lbc.IsButtonEvent(event):
   if globals.canSpeak: globals.output("Loading final results, please wait.", 1)
   self.results.getPage(self.results.pages, True)
   self.Destroy()
   return SearchResultsDialog(searchTerms=self.searchTerms, searchType=self.searchType, results=self.results, category=self.category, grade=self.grade)
  elif name==self.btn_author.GetName() and lbc.IsButtonEvent(event):
   if len(self.results[result].authorList)>1: author=lbc.DialogPick(title="Choose Author", names=self.results[result].authorList, values=self.results[result].authorList)
   else: author=self.results[result].authorList[0]
   if globals.canSpeak: globals.output("Searching for all books by "+author+", please wait.", 1)
   try:
    results=globals.searchTypes[globals.search_author](author, category=self.category, grade=self.grade) #search for the text
   except pybookshare.ApiError, e:
    return ErrorDialog("Error!", e)
   return SearchResultsDialog(searchTerms=author, searchType=globals.searchTypes.keys()[1], results=results, category=self.category, grade=self.grade)

 @staticmethod
 def getInfo(self, result, excludes=None):
  #returns basic info about the result, one piece per line, except var names in the excludes list.
  info="Title: "+result.title
  if "authorStr" not in excludes and result.authorStr!=result.unknown: info+="\nAuthor: "+result.authorStr
  if "shortSynopsis" not in excludes and result.shortSynopsis!=result.unknown: info+="\nShort Synopsis: "+result.shortSynopsis
  if "longSynopsis" not in excludes and result.longSynopsis!=result.unknown: info+="\nLong Synopsis: "+result.longSynopsis
  if "copyright" not in excludes and result.copyright!=result.unknown: info+="\nCopyright: "+result.copyright
  if "publisher" not in excludes and result.publisher!=result.unknown: info+="\nPublished by "+result.publisher
  if "size" not in excludes and result.size!=result.unknown: info+="\nBook File Size: "+str(globals.toBiggestBytes(int(result.size)))
  if "language" not in excludes and result.language!=result.unknown: info+="\nLanguage: "+result.language
  if "dateAdded" not in excludes and result.dateAdded!=result.unknown: info+="\nDate Added to Bookshare: "+globals.getDate(result.dateAdded)
  if "categoryStr" not in excludes and result.categoryStr!="" and result.categoryStr!=result.unknown: info+="\nCategories: "+result.categoryStr
  if "isbn" not in excludes and result.isbn!=result.unknown: info+="\nISBN: "+result.isbn
  #info.encode(wx.GetDefaultPyEncoding())
  return info

 def updateResults(self):
  #updates the dialog's results: self.results, self.resultText, and the listbox to display them
  self.resultText=[]
  self.lst_results.Clear()
  for res in self.results:
   txt=res.title+", by "+res.authorStr.encode(wx.GetDefaultPyEncoding())
   self.resultText.append(txt)
   self.lst_results.Append(txt)

class DownloadDialog(lbc.Dialog):

 def __init__(self, result, handler=None, *args, **kwords):
  title="Download "+result.title
  lbc.Dialog.__init__(self, title=title, *args, **kwords)
  self.result=result
  self.btn_brf=self.AddButton(label="Download &BRF")
  self.btn_daisy=self.AddButton(label="Download &DAISY")
  self.btn_cancel=self.AddButton(label="Cancel")
  if handler is None: handler=self.eventHandler
  self.Complete(buttons=[], handler=handler)

 def eventHandler(self, dlg, event, name):
  if lbc.IsCloseEvent(event) or (name==self.btn_cancel.GetName() and lbc.IsButtonEvent(event)): return globals.destroy(self)
  if name==self.btn_brf.GetName(): format=0
  if name==self.btn_daisy.GetName(): format=1
  if lbc.IsButtonEvent(event): #must be one of the formats available
   globals.download(self.result, format)
   return self.Destroy()


class BookInfoDialog(lbc.Dialog):
 #info about a particular book, using an api call to find all info

 def __init__(self, result, handler=None, *args, **kwords):
  if globals.canSpeak: globals.output("Retrieving book information, please wait.", 1)
  self.result=globals.bs.getMetaData(result)
  title=self.result.title
  lbc.Dialog.__init__(self, title=title, *args, **kwords)
  self.memo_basicInfo=self.AddMemo(label="Basic Information", value=SearchResultsDialog.getInfo(self, self.result, ["shortSynopsis", "longSynopsis"])) 
  self.AddBand()
  self.memo_shortSynopsis=self.AddMemo(label="Short Synopsis", value=self.result.shortSynopsis)
  self.AddBand()
  self.memo_longSynopsis=self.AddMemo(label="Long Synopsis", value=self.result.longSynopsis)
  self.AddBand()
  self.btn_download=self.AddButton(label="Download Book")
  self.btn_close=self.AddButton(label="Close")
  if handler is None: handler=self.eventHandler
  self.Complete(buttons=[], handler=handler)

 def eventHandler(self, dlg, event, name):
  if lbc.IsCloseEvent(event) or (name==self.btn_close.GetName() and lbc.IsButtonEvent(event)): return self.Destroy()
  elif name==self.btn_download.GetName() and lbc.IsButtonEvent(event): return DownloadDialog(self.result)

class LoginDialog(lbc.Dialog):

 def __init__(self, username=None, password=None, handler=None, *args, **kwords):
  title="Log into Bookshare"
  lbc.Dialog.__init__(self, title=title, *args, **kwords)
  if username is None: username="" #to avoid passing 'None' to SetValue()
  if password is None: password="" #same
  self.txt_username=self.AddTextCtrl(label="Bookshare Username: ", value=username)
  self.txt_password=self.AddTextCtrl(label="Bookshare Password: ", isPassword=True, value=password)
  self.AddBand()
  self.btn_login=self.AddButton(label="Log In")
  self.btn_login.SetDefault()
  self.btn_cancel=self.AddButton(label="Cancel")
  if handler is None: handler=self.eventHandler
  self.Complete(buttons=[], handler=handler)

 def eventHandler(self, dlg, event, name):
  username=self.txt_username.GetValue()
  password=self.txt_password.GetValue()
  if lbc.IsCloseEvent(event) or (name==self.btn_cancel.GetName() and lbc.IsButtonEvent(event)):
   globals.gaveUp=True
   return self.Destroy()
  elif name==self.btn_login.GetName() and lbc.IsButtonEvent(event):
   globals.bs.setCreds(username, password)
   if globals.canSpeak: globals.output("Checking username and password, please wait.", 1)
   try:
    info=globals.bs.getUserInfo() #if this throws no exception, we're good
    globals.loggedIn=True
    globals.config['settings']['username']=username
    globals.config['settings']['password']=password
    globals.config['settings']['name']=info['displayname']['value']
    globals.config.write()
    if globals.canSpeak: globals.output(info['displayname']['value']+" ("+username+") is authenticated.", 1)
    return self.Destroy()
   except pybookshare.ApiError:
    globals.loggedIn=False
    self.txt_password.Clear()
    return ErrorDialog("Login Failed", "login failed with username "+username+". Please try again, or click the Cancel button to exit.")

class WaitingDialog(lbc.Dialog):
 #basically a message box, but is modeless so other things can happen behind it

 def __init__(self, title, message):
  lbc.Dialog.__init__(self, title=title)
  self.txt_msg=self.AddTextCtrl(value=message)
  self.Show()

class OptionsDialog(lbc.Dialog):
 #for setting options like logins, file extension, and so on

 def __init__(self, title=None, handler=None, *args, **kwords):
  if title is None: title="Options"
  lbc.Dialog.__init__(self, title=title, *args, **kwords)
  self.txt_username=self.AddTextCtrl(label="Bookshare &Username:", value=globals.config['settings']['username'])
  self.txt_password=self.AddTextCtrl(label="Bookshare &Password", value=globals.config['settings']['password'], isPassword=True)
  self.AddBand()
  fileTypeOptions=[globals.zip, globals.bks2]
  self.lst_fileTypes=self.AddListBox(label="Select Download File &Type", names=fileTypeOptions)
  if globals.config['settings']['extension'] in fileTypeOptions: self.lst_fileTypes.SetStringSelection(globals.config['settings']['extension'])
  self.fileFormatOptions=[globals.prompt[0], globals.brf[0], globals.daisy[0]]
  self.fileFormatOptionNums=[globals.prompt[1], globals.brf[1], globals.daisy[1]]
  self.lst_fileFormats=self.AddListBox(label="Select Default Book &Format", names=self.fileFormatOptions)
  self.lst_fileFormats.SetSelection(self.fileFormatOptionNums.index(int(globals.config['settings']['format'])))
  self.btn_destination=self.AddButton(label="Destination for Downloaded Books (currently "+globals.config['settings']['downloadPath']+")")
  self.AddBand()
  self.cbx_autoUnzip=self.AddCheckBox(label="Automatically &unzip downloaded books", value=globals.config['settings']['autoUnzip']=='True')
  self.txt_limit=self.AddTextCtrl(label="Maximum Results to Show at Once (limit 250):", value=str(globals.config['settings']['limit']))
  self.cbx_speak=self.AddCheckBox(label="Speak &progress messages", value=globals.config['settings']['speakProgressMessages']=='True')
  self.AddBand()
  self.btn_save=self.AddButton(label="Save")
  self.btn_save.SetDefault()
  self.btn_cancel=self.AddButton(label="Cancel")
  self.path=None
  if handler is None: handler=self.eventHandler
  self.Complete(buttons=[], handler=handler)

 def eventHandler(self, dlg, event, name):
  if self.path is None: self.path=""
  if lbc.IsCloseEvent(event) or (name==self.btn_cancel.GetName() and lbc.IsButtonEvent(event)): return self.Destroy()
  elif name==self.btn_destination.GetName() and lbc.IsButtonEvent(event):
   self.path=lbc.DialogBrowseForFolder(message="Choose the folder in which downloaded books should be stored", value=globals.config['settings']['downloadPath'])
   if self.path!="": self.btn_destination.SetLabel("Path for Downloaded books (now "+self.path+")")
  elif name==self.btn_save.GetName() and lbc.IsButtonEvent(event):
   settings=globals.config['settings']
   settings['username']=self.txt_username.GetValue()
   settings['password']=self.txt_password.GetValue()
   settings['limit']=self.txt_limit.GetValue()
   settings['extension']=self.lst_fileTypes.GetStringSelection()
   settings['autoUnzip']=self.cbx_autoUnzip.GetValue()
   settings['speakProgressMessages']=self.cbx_speak.GetValue()
   format=self.lst_fileFormats.GetStringSelection()
   settings['format']=self.fileFormatOptionNums[self.fileFormatOptions.index(format)]
   if self.path!="": settings['downloadPath']=self.path
   try: globals.config.write()
   except: return ErrorDialog("Error", "An error occurred while trying to save your settings. Please close the program and try again.")
   globals.config.reload()
   globals.bs.limit=globals.config['settings']['limit']
   AlertDialog("Success", "Your settings have been saved.")
   return self.Destroy()