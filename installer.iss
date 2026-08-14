#define tlAppName "Textbook Lending Tracker"
#define tlAppVersion "2.1.0"
#define tlAppPublisher "Bear"
#define tlAppExeName "TextbookLendingTracker.exe"

[Setup]
AppId={{12345678-ABCD-1234-ABCD-123456789ABC}}
AppName={#tlAppName}
AppVersion={#tlAppVersion}
AppPublisher={#tlAppPublisher}

DefaultDirName={autopf}\Textbook Lending Tracker
DefaultGroupName={#tlAppName}

OutputBaseFilename=TextbookLendingTrackerSetup-{#tlAppVersion}

Compression=lzma
SolidCompression=yes

PrivilegesRequired=admin


[Files]
Source: "dist\TextbookLendingTracker\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs


[Icons]
Name: "{group}\Textbook Lending Tracker"; Filename: "{app}\TextbookLendingTracker.exe"
Name: "{commondesktop}\Textbook Lending Tracker"; Filename: "{app}\TextbookLendingTracker.exe"


[Run]
Filename: "{app}\TextbookLendingTracker.exe"; Description: "Launch Textbook Lending Tracker"; Flags: nowait postinstall skipifsilent