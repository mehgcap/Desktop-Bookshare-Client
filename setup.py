import globals
import accessible_output, os, py2exe
from distutils.core import setup
from glob import glob

data_files=[
 ("Microsoft.VC90.CRT", glob(os.path.join(globals.appPath, "system_dlls", "*.*"))),
 #("lib", glob(os.path.join(globals.appPath, "speech_dlls", "*.*"))),
 ("", glob(os.path.join(globals.appPath, "readme.html"))),
 ("", glob(os.path.join(globals.appPath, "license.txt")))
]+accessible_output.py2exe_datafiles()

setup(
 options={
  "py2exe":{
   "compressed": 1,
   "optimize": 2,
   "bundle_files": 3,
   "dll_excludes":['mswsock.dll', 'powrprof.dll', 'uxTheme.dll']}
  },
 zipfile = None,
 version=globals.appVersion,
 description = globals.appDescription,
 name = globals.appName,
 data_files=data_files,
 windows = [os.path.join(globals.appPath, "dbc.py")]
 )