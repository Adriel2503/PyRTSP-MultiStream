[Setup]
AppName=Welltep
AppVersion=1.0
AppPublisher=Tu Empresa
AppPublisherURL=https://welltep.com
AppSupportURL=https://welltep.com/soporte
AppUpdatesURL=https://welltep.com/actualizaciones
DefaultDirName={autopf}\Welltep
DefaultGroupName=Welltep
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=installers
OutputBaseFilename=WelltepInstaller
SetupIconFile=assets\icons\welltep.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\Welltep\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Welltep"; Filename: "{app}\Welltep.exe"
Name: "{group}\{cm:UninstallProgram,Welltep}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Welltep"; Filename: "{app}\Welltep.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Welltep"; Filename: "{app}\Welltep.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\Welltep.exe"; Description: "{cm:LaunchProgram,Welltep}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
var
  GStreamerPath: String;
begin
  Result := True;
  
  // Verificar si GStreamer está instalado
  if not RegQueryStringValue(HKLM, 'SOFTWARE\GStreamer\1.0\x86_64', 'InstallDir', GStreamerPath) then
  begin
    if MsgBox('GStreamer no está instalado. ¿Desea descargarlo e instalarlo?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      ShellExec('open', 'https://gstreamer.freedesktop.org/download/', '', '', SW_SHOWNORMAL, ewNoWait, 0);
      MsgBox('Por favor, instale GStreamer y luego ejecute este instalador nuevamente.', mbInformation, MB_OK);
      Result := False;
    end
    else
      Result := False;
  end;
end; 