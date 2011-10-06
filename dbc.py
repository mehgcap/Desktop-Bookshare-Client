import dialogs, globals, lbc
"""DBC: desktop Bookshare Client, a desktop client for browsing and downloading from http://www.bookshare.org."""

app=lbc.App()
if globals.config['settings']['username']=="": globals.login()

#give the beta warning, if necessary
if globals.isBeta:
 dialogs.AlertDialog("Beta Software", "Please remember that this is beta software. In my tests, it worked fine, but you, faithful beta tester, may find bugs or other problems I missed. Please email bug reports, feature suggestions, and so on to mehgcap@gmail.com. Also remember that this is free, so I am not obligated to do anything with it. Of course, I plan to enhance it according to your feedback, but just remember that I make no money off of it. Anyway, thanks for being willing to give this a try, and I hope you enjoy!")

#create the main dialog:
main_dlg=dialogs.MainDialog()
app.Exit()