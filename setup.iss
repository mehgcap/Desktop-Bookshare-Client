; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Desktop Bookshare Client"
#define MyAppVersion "1.01"
#define MyAppExeName "dbc.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppID={{3DD81609-AD5B-49EE-A644-31D110B388CA}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputBaseFilename=DBC_1_0_1Beta_Setup
Compression=lzma/Max
SolidCompression=true
AppCopyright=2011 Alex Hall
LicenseFile=license.txt
AppVerName={#MyAppName} version {#MyAppVersion} Beta

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
Source: "c:\prog\bookshare\dbc\dist\dbc.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\prog\bookshare\dbc\dist\_ctypes.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\prog\bookshare\dbc\dist\_hashlib.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\prog\bookshare\dbc\dist\_socket.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\prog\bookshare\dbc\dist\_ssl.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\prog\bookshare\dbc\dist\_win32sysloader.pyd"; DestDir: "{app}"; Flags: ignoreversion
;Source: "C:\prog\bookshare\dbc\dist\API-MS-Win-Core-LocalRegistry-L1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
;Source: "C:\prog\bookshare\dbc\dist\API-MS-Win-Core-ProcessThreads-L1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
;Source: "C:\prog\bookshare\dbc\dist\API-MS-Win-Security-Base-L1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\prog\bookshare\dbc\dist\bz2.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\prog\bookshare\dbc\dist\dbc.exe"; DestDir: "{app}"; Flags: ignoreversion
;Source: "c:\prog\bookshare\dbc\dist\POWRPROF.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\pyexpat.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\python27.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\pythoncom27.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\pywintypes27.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\readme.html"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\select.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\unicodedata.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\win32api.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\win32gui.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\win32ui.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\wx._controls_.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\wx._core_.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\wx._gdi_.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\wx._misc_.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\wx._windows_.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\wxbase28uh_net_vc.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\wxbase28uh_vc.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\wxmsw28uh_adv_vc.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\wxmsw28uh_core_vc.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\wxmsw28uh_html_vc.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\prog\bookshare\dbc\dist\Microsoft.VC90.CRT\*"; DestDir: "{app}\Microsoft.VC90.CRT"; Flags: ignoreversion recursesubdirs createallsubdirs
;Source: "c:\prog\bookshare\dbc\dist\lib\*"; DestDir: "{app}\lib"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "c:\prog\bookshare\dbc\dist\accessible_output\lib\*"; DestDir: "{app}\accessible_output\lib"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: {group}\Read the Readme; Filename: {app}\readme.html
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, "&", "&&")}}"; Flags: nowait postinstall skipifsilent
