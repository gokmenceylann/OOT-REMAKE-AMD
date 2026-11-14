[Setup]
AppId=OOT-REMAKE-AMD-Tools
AppName=OOT-REMAKE-AMD Tools
AppVersion={#PackageVersion}
DefaultDirName={localappdata}\Programs\OOT-REMAKE-AMD-Tools
DefaultGroupName=OOT-REMAKE-AMD Tools
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
Compression=lzma2
SolidCompression=yes
UninstallDisplayName=OOT-REMAKE-AMD Tools
CloseApplications=no
RestartApplications=no

[Files]
Source: "{#Payload}\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Tasks]
Name: "desktop"; Description: "Create a desktop shortcut to the installation guide"; Flags: unchecked

[Icons]
Name: "{group}\Installation Guide"; Filename: "{app}\docs\install.md"
Name: "{userdesktop}\OOT-REMAKE-AMD Installation Guide"; Filename: "{app}\docs\install.md"; Tasks: desktop
