[Setup]
AppName=MP3 Splitter
AppVersion=1.0
DefaultDirName={pf}\MP3Splitter
DefaultGroupName=MP3 Splitter
OutputBaseFilename=MP3SplitterInstaller
Compression=lzma
SolidCompression=yes
SetupIconFile=c23f7c96-fdc7-4a59-bc0c-6ae1bb48a66a.ico

[Files]
; Main executable built with PyInstaller
Source: "dist\MP3Splitter.exe"; DestDir: "{app}"; Flags: ignoreversion

; FFmpeg binary
Source: "bin\ffmpeg.exe"; DestDir: "{app}\bin"; Flags: ignoreversion

; Custom icon (for shortcuts)
Source: "c23f7c96-fdc7-4a59-bc0c-6ae1bb48a66a.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu shortcut
Name: "{group}\MP3 Splitter"; Filename: "{app}\MP3Splitter.exe"; IconFilename: "{app}\c23f7c96-fdc7-4a59-bc0c-6ae1bb48a66a.ico"

; Desktop shortcut
Name: "{userdesktop}\MP3 Splitter"; Filename: "{app}\MP3Splitter.exe"; Tasks: desktopicon; IconFilename: "{app}\c23f7c96-fdc7-4a59-bc0c-6ae1bb48a66a.ico"

; Uninstall shortcut
Name: "{group}\Uninstall MP3 Splitter"; Filename: "{uninstallexe}"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\MP3Splitter.exe"; Description: "Launch MP3 Splitter"; Flags: nowait postinstall skipifsilent
