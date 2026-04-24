[Setup]
AppName=KünyeX - UNSAL Şubesi
AppVersion=1.6
DefaultDirName={localappdata}\KunyeX
DefaultGroupName=KünyeX
OutputDir=..\Nihai_Setup_Dosyalari
OutputBaseFilename=Setup_KunyeX_UNSAL
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
SetupIconFile=..\icon.ico

[Tasks]
Name: "desktopicon"; Description: "KünyeX Ana Program masaüstü kısayolu oluştur"; GroupDescription: "Ek Görevler:"; Flags: unchecked

[Files]
Source: "..\Dagitim_Paketleri\UNSAL_PAKETI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autodesktop}\KünyeX UNSAL"; Filename: "{app}\KunyeX_UNSAL.exe"; Tasks: desktopicon
Name: "{group}\KünyeX UNSAL"; Filename: "{app}\KunyeX_UNSAL.exe"
Name: "{group}\KünyeX Kaldır"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\KunyeX_UNSAL.exe"; Description: "KünyeX'i Başlat"; Flags: nowait postinstall skipifsilent shellexec
Filename: "{app}\Lisans_Anahtari.txt"; Description: "Lisans Anahtarımı Göster"; Flags: postinstall shellexec skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{commonappdata}\KunyeXPremium\KunyeX_UNSAL"
