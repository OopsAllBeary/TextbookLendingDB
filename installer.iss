[Setup]
AppName=Textbook Lending Tracker
AppVersion=1.0
DefaultDirName={autopf}\Textbook Lending Tracker
DefaultGroupName=Textbook Lending Tracker
OutputBaseFilename=TextbookLendingTrackerSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\TextbookLendingTracker\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Textbook Lending Tracker"; Filename: "{app}\TextbookLendingTracker.exe"
Name: "{commondesktop}\Textbook Lending Tracker"; Filename: "{app}\TextbookLendingTracker.exe"

[Run]
Filename: "{app}\TextbookLendingTracker.exe"; Description: "Launch Textbook Lending Tracker"; Flags: nowait postinstall skipifsilent