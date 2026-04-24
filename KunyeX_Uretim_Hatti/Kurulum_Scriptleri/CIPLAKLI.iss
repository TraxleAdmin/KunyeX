[Setup]
AppName=KünyeX - CIPLAKLI Şubesi
AppVersion=1.6
DefaultDirName={localappdata}\KunyeX
DefaultGroupName=KünyeX
OutputDir=..\Nihai_Setup_Dosyalari
OutputBaseFilename=Setup_KunyeX_CIPLAKLI
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
SetupIconFile=..\icon.ico

[Tasks]
Name: "desktopicon"; Description: "KünyeX Ana Program masaüstü kısayolu oluştur"; GroupDescription: "Ek Görevler:"; Flags: unchecked

[Files]
Source: "..\Dagitim_Paketleri\CIPLAKLI_PAKETI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autodesktop}\KünyeX CIPLAKLI"; Filename: "{app}\KunyeX_CIPLAKLI.exe"; Tasks: desktopicon
Name: "{group}\KünyeX CIPLAKLI"; Filename: "{app}\KunyeX_CIPLAKLI.exe"
Name: "{group}\KünyeX Kaldır"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\KunyeX_CIPLAKLI.exe"; Description: "KünyeX'i Başlat"; Flags: nowait postinstall skipifsilent shellexec
Filename: "{app}\Lisans_Anahtari.txt"; Description: "Lisans Anahtarımı Göster"; Flags: postinstall shellexec skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{commonappdata}\KunyeXPremium\KunyeX_CIPLAKLI"
