[Setup]
#if PackageVersion == "0.2.0-rc.3"
AppId=OOT-REMAKE-AMD-Baseline-Research
#elif defined(StableRuntimeManifest)
AppId=OOT-REMAKE-AMD-Stable-GameImport
#else
AppId=OOT-REMAKE-AMD-GameImport
#endif
AppName=OOT-REMAKE-AMD Local Game Import
AppVersion={#PackageVersion}
DefaultDirName={localappdata}\Programs\OOT-REMAKE-AMD-Game
DefaultGroupName=OOT-REMAKE-AMD
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.22000
DisableProgramGroupPage=yes
Compression=lzma2
SolidCompression=yes
CloseApplications=no
RestartApplications=no

[Files]
Source: "{#Payload}\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
Source: "{#Payload}\scripts\Import-LocalGame.ps1"; Flags: dontcopy
#ifdef StableRuntimeManifest
Source: "{#Payload}\STABLE-RUNTIME-SHA256.txt"; Flags: dontcopy
#endif
Source: "{code:SourceGame}\hookshot.exe"; DestDir: "{app}"; Flags: external
Source: "{code:SourceGame}\hookshot_vk.dll"; DestDir: "{app}"; Flags: external
Source: "{code:SourceGame}\image.bin"; DestDir: "{app}"; Flags: external uninsneveruninstall
Source: "{code:SourceGame}\romfs\*"; DestDir: "{app}\romfs"; Flags: external recursesubdirs createallsubdirs uninsneveruninstall
Source: "{code:SourceGame}\hookshot_shaders.bin"; DestDir: "{app}"; Flags: external skipifsourcedoesntexist uninsneveruninstall
Source: "{code:SourceGame}\hookshot_pipeline_states_shipped.bin"; DestDir: "{app}"; Flags: external skipifsourcedoesntexist
Source: "{code:SourceGame}\hookshot_version.txt"; DestDir: "{app}"; Flags: external skipifsourcedoesntexist
Source: "{code:SourceGame}\SDL2.dll"; DestDir: "{app}"; Flags: external skipifsourcedoesntexist
Source: "{code:SourceGame}\SDL3.dll"; DestDir: "{app}"; Flags: external skipifsourcedoesntexist
Source: "{code:SourceGame}\libwinpthread-1.dll"; DestDir: "{app}"; Flags: external skipifsourcedoesntexist

[Tasks]
Name: "startmenu"; Description: "Create a Start Menu game shortcut"; Flags: unchecked

[Icons]
Name: "{group}\Hookshot"; Filename: "{app}\hookshot.exe"; WorkingDir: "{app}"; Tasks: startmenu

[Code]
var
  GamePage: TInputDirWizardPage;

procedure InitializeWizard;
begin
  GamePage := CreateInputDirPage(wpSelectDir, 'Select a local Hookshot build',
    'A completed build and your own game data are required.',
    'Choose the folder with hookshot.exe, hookshot_vk.dll, image.bin and romfs. The installed game opens directly from the destination.',
    False, '');
  GamePage.Add('Local game folder:');
  GamePage.Values[0] := ExpandConstant('{param:SOURCE|}');
end;

function SourceGame(Param: String): String;
begin
  Result := RemoveBackslashUnlessRoot(Trim(GamePage.Values[0]));
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  SourceDir, DestDir, CheckScript, ErrorPath, Args: String;
  ErrorCode: Integer;
  Details: AnsiString;
begin
  Result := '';
  SourceDir := SourceGame('');
  DestDir := RemoveBackslashUnlessRoot(ExpandConstant('{app}'));
  if not DirExists(SourceDir) then begin
    Result := 'Select a local Hookshot build folder first. See the installation guide.';
    Exit;
  end;
  if (CompareText(SourceDir, DestDir) = 0) or
     (Pos(Lowercase(AddBackslash(SourceDir)), Lowercase(AddBackslash(DestDir))) = 1) or
     (Pos(Lowercase(AddBackslash(DestDir)), Lowercase(AddBackslash(SourceDir))) = 1) then begin
    Result := 'Choose a destination separate from your local build.';
    Exit;
  end;
  if FileExists(AddBackslash(DestDir) + 'hookshot.exe') or DirExists(AddBackslash(DestDir) + 'romfs') then begin
    Result := 'Choose a new game destination. Setup preserves existing game installations.';
    Exit;
  end;
  ExtractTemporaryFile('Import-LocalGame.ps1');
  CheckScript := ExpandConstant('{tmp}\Import-LocalGame.ps1');
  ErrorPath := ExpandConstant('{tmp}\game-check.txt');
  SetPreviousData(0, 'unused', '');
  Args := '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "' + CheckScript + '" -CheckOnly -GameDirectory "' + SourceDir + '" -ErrorLog "' + ErrorPath + '"';
#ifdef StableRuntimeManifest
  ExtractTemporaryFile('STABLE-RUNTIME-SHA256.txt');
  Args := Args + ' -RuntimeManifest "' + ExpandConstant('{tmp}\STABLE-RUNTIME-SHA256.txt') + '"';
#endif
  if not Exec(ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe'), Args, '', SW_HIDE, ewWaitUntilTerminated, ErrorCode) or
      (ErrorCode <> 0) then begin
    if LoadStringFromFile(ErrorPath, Details) then begin
      Result := Trim(UTF8Decode(Details));
      Exit;
    end;
    Result := 'Local game validation failed. Check the supplied Windows x64 build, RomFS, media features and Vulkan driver. Run scripts\Import-LocalGame.ps1 -CheckOnly from the portable package for a specific error.';
  end;
end;
