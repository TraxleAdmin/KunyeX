import os
import hashlib
import random
import string
import json
import shutil
import sys

# ==============================================================
# ⚠️ DİKKAT: FIREBASE VERİTABANI LİNKİNİ BURAYA YAPIŞTIR
# ==============================================================
FIREBASE_URL = "https://kunyex-lisans-default-rtdb.europe-west1.firebasedatabase.app"

def tr_to_eng(text):
    return text.translate(str.maketrans("ÇĞİÖŞÜçğıöşü", "CGIOSUcgiosu"))

RAW_LOCATIONS = [
    "ÇIPLAKLI", "DÖŞEMEALTI", "ÜNSAL", "LİMAN", "ULUÇ", "FETHİYE", "KIZILTOPRAK", "SORGUN", "GÜZELOBA", "KUNDU", "ALANYA", 
    "GÖÇERLER", "YEŞİLBAYIR", "ERCİYES", "ALANYA-OBA", "UNCALI", "YENİ HAL", "KIZILARIK", "VARSAK", "ŞİRİNYALI", "GÜNEŞ",
    "KÜTÜKÇÜ", "FAKÜLTE", "ÇAĞLAYAN", "KONUKSEVER", "SANAYİ", "KUMLUCA", "MAZI DAĞI", "ALTINOVA", "GAZİPAŞA", "KARATAY",
    "CUMARTESİ PAZARI", "SERİK", "DOĞU GARAJI", "MEYDAN KAVAĞI", "GÜLVEREN", "GÖKSU", "PINARLI", "ŞARAMPOL", "YENİGÜN", "MASAL PARKI",
    "AHATLI", "ABDURRAHMANLAR", "AKSU", "DÜDEN", "KORKUTELİ2", "ELMALI", "BUCAK", "ANAMUR", "MOLLAYUSUF", "SÜTÇÜLER",
    "EĞİRDİR", "EMEK", "KÜLLİYE", "SERİK-SALI", "KEPEZ HASTANE", "BUCAK-TOKİ", "ŞAFAK", "ÇAMLIBEL", "NEBİLER", "AYANOĞLU",
    "KARŞIYAKA", "HABİBLER", "YENİ SANAYİ", "GÜLLÜK", "BELEK", "BOĞAZKENT", "FENER", "DÜZLERCAMİ", "ÇANKAYA",
    "BOZYAZI", "FİNİKE", "KUZEYYAKA", "DOKUMA", "KARAAĞAÇ", "DOLAPDERE", "ETİLER", "MEMUREVLERİ", "ULUS", "SERİK-OTOGAR", "ERENKÖY"
]

LOCATIONS = [tr_to_eng(loc) for loc in RAW_LOCATIONS]
EXE_NAMES = ["KunyeX_Merkez.exe"] + [f"KunyeX_{loc.replace(' ', '_')}.exe" for loc in LOCATIONS]
EXE_NAMES = EXE_NAMES[:4] # Hızlı test için Kademeli Dağıtım

TOTAL_LICENSES = len(EXE_NAMES)
OUTPUT_DIR = "KunyeX_Uretim_Hatti"
SOURCE_DIR = f"{OUTPUT_DIR}/Kaynak_Kodlar"
os.makedirs(SOURCE_DIR, exist_ok=True)

HAS_ICON = os.path.exists("icon.ico")
ICON_PYINSTALLER_CMD = '--icon="..\\icon.ico"' if HAS_ICON else ''
ICON_ISS_CMD = 'SetupIconFile=..\\icon.ico' if HAS_ICON else ''

PDF_CEVIRICI_MEVCUT = os.path.exists("kunye_extract_fhd_pdf.py")
if PDF_CEVIRICI_MEVCUT:
    shutil.copy("kunye_extract_fhd_pdf.py", f"{SOURCE_DIR}/kunye_extract_fhd_pdf.py")

# ==============================================================
# ANA ÜRETİM MOTORU VE OTOMATİK SETUP FABRİKASI
# ==============================================================

def generate_serial(is_admin=False):
    chars = string.ascii_uppercase + string.digits
    prefix = "KUNYEX-PRO"
    block1 = ''.join(random.choices(chars, k=4))
    block2 = ''.join(random.choices(chars, k=4))
    return f"{prefix}-{block1}-{block2}"

print(f"[*] KunyeX Toplu Dagitim Uretim Hatti Baslatildi...")
print(f"[*] Toplam {TOTAL_LICENSES} sube icin bagimsiz SETUP paketleri uretilecek.")

if HAS_ICON:
    try:
        shutil.copy("icon.ico", f"{OUTPUT_DIR}/icon.ico")
    except:
        pass

firebase_db = {
    "config": {
        "version": "1.6",
        "update_url": "https://www.traxleapp.com/guncelleme/KunyeX_Master_Client.exe"
    },
    "licenses": {}
}

for exe_name in EXE_NAMES:
    loc_name = exe_name.replace("KunyeX_", "").replace(".exe", "")
    is_admin = "Merkez" in exe_name
    serial_key = generate_serial(is_admin)
    
    firebase_db["licenses"][serial_key] = {
        "branch": loc_name.replace("_", " "),
        "status": "unused",
        "hwid": ""
    }
    
    with open(f"{OUTPUT_DIR}/Lisans_Anahtari_{loc_name}.txt", "w", encoding="utf-8") as lf:
        lf.write(f"ŞUBE: {loc_name.replace('_', ' ')}\nLİSANS ANAHTARI: {serial_key}\n\nBu şifreyi program ilk açıldığında ekrana kopyalayıp yapıştırın.")

with open(f"{OUTPUT_DIR}/Firebase_Icin_Lisans_Veritabani.json", "w", encoding="utf-8") as fb_file:
    json.dump(firebase_db, fb_file, ensure_ascii=False, indent=4)

# 🔥 MÜDAHALE: MONOLİTİK AYRIŞTIRMA (DIŞARIDAN DOSYA OKUMA)
master_client_path = "KunyeX_Master_Client.py"
if not os.path.exists(master_client_path):
    print(f"[!] KRİTİK HATA: '{master_client_path}' dosyası ana dizinde bulunamadı!")
    print(f"[!] Lütfen ana kodunuzu '{master_client_path}' adıyla builder.py'nin yanına kaydedin.")
    sys.exit(1)

with open(master_client_path, "r", encoding="utf-8") as f:
    client_code = f.read()

# Placeholder kalmışsa güvenliğe al
client_code = client_code.replace("{TARGET_FIREBASE_URL}", FIREBASE_URL)

with open(f"{SOURCE_DIR}/KunyeX_Master_Client.py", "w", encoding="utf-8") as py_file:
    py_file.write(client_code)

ISS_DIR = f"{OUTPUT_DIR}/Kurulum_Scriptleri"
SETUP_OUT_DIR = f"{OUTPUT_DIR}/Nihai_Setup_Dosyalari"
os.makedirs(ISS_DIR, exist_ok=True)
os.makedirs(SETUP_OUT_DIR, exist_ok=True)

bat_content = """@echo off
cd /d "%~dp0"
echo [1/3] Master EXE derleme islemi basliyor... (Lutfen bekleyin)
cd Kaynak_Kodlar\n"""

# 🔥 MÜDAHALE: UAC-ADMIN KALDIRILDI, UPX KALDIRILDI, LOGO.PNG EKLENDİ
bat_content += f"\"{sys.executable}\" -m PyInstaller --noconfirm --clean --onefile --windowed --add-data \"..\\..\\logo.png;.\" {ICON_PYINSTALLER_CMD} --hidden-import cryptography --hidden-import cv2 --hidden-import numpy --hidden-import charset_normalizer.cd --hidden-import charset_normalizer.md__mypyc --copy-metadata charset-normalizer --collect-all tkinterdnd2 --collect-all pdfplumber --collect-all charset_normalizer --collect-all pdf2image --collect-all PIL KunyeX_Master_Client.py\n"

if PDF_CEVIRICI_MEVCUT:
    bat_content += f"\"{sys.executable}\" -m PyInstaller --noconfirm --clean --onefile --windowed {ICON_PYINSTALLER_CMD} --name \"KunyeX_PDF_Cevirici\" kunye_extract_fhd_pdf.py\n"

bat_content += """
if not exist "dist\\KunyeX_Master_Client.exe" (
    echo.
    echo =========================================================
    echo KRITIK HATA: PyInstaller EXE dosyasini uretemedi!
    echo Yukaridaki kirmizi hata mesajlarinda hangi modulun
    echo eksik oldugunu gorebilirsiniz. Lutfen kontrol edin.
    echo =========================================================
    pause
    exit /b
)

echo [2/3] Sube Klasorleri ve Inno Setup derlemeleri basliyor...
cd ..
if not exist "Dagitim_Paketleri" mkdir Dagitim_Paketleri
"""

for exe_name in EXE_NAMES:
    loc_name = exe_name.replace("KunyeX_", "").replace(".exe", "")
    folder_name = f"Dagitim_Paketleri\\{loc_name}_PAKETI"
    
    bat_content += f"echo {loc_name} Setup paketi uretiliyor...\n"
    bat_content += f"mkdir \"{folder_name}\" >nul 2>&1\n"
    bat_content += f"copy \"Kaynak_Kodlar\\dist\\KunyeX_Master_Client.exe\" \"{folder_name}\\{exe_name}\" >nul\n"
    
    if PDF_CEVIRICI_MEVCUT:
        bat_content += f"copy \"Kaynak_Kodlar\\dist\\KunyeX_PDF_Cevirici.exe\" \"{folder_name}\\KunyeX_PDF_Cevirici.exe\" >nul\n"
        
    bat_content += f"xcopy \"C:\\Program Files\\Tesseract-OCR\" \"{folder_name}\\Tesseract-OCR\\\" /E /I /H /Y /Q >nul\n"
    bat_content += f"xcopy \"C:\\poppler\" \"{folder_name}\\poppler\\\" /E /I /H /Y /Q >nul\n"
    bat_content += f"copy \"..\\mevsiminden.png\" \"{folder_name}\\\" >nul 2>&1\n"
    bat_content += f"copy \"..\\yerli_uretim.png\" \"{folder_name}\\\" >nul 2>&1\n"
    
    if HAS_ICON:
        bat_content += f"copy \"icon.ico\" \"{folder_name}\\\" >nul 2>&1\n"

    # Logo.png Setup klasörüne de atılıyor ki sistem bulabilsin
    if os.path.exists("logo.png"):
        bat_content += f"copy \"logo.png\" \"{folder_name}\\\" >nul 2>&1\n"
    
    bat_content += f"copy \"Lisans_Anahtari_{loc_name}.txt\" \"{folder_name}\\Lisans_Anahtari.txt\" >nul\n"
    bat_content += f"copy \"Lisans_Anahtari_{loc_name}.txt\" \"Nihai_Setup_Dosyalari\\Sifre_{loc_name}.txt\" >nul\n"
    bat_content += f"del \"Lisans_Anahtari_{loc_name}.txt\"\n"

    iss_content = f"""[Setup]
AppName=KünyeX - {loc_name.replace('_', ' ')} Şubesi
AppVersion=1.6
DefaultDirName={{localappdata}}\\KunyeX
DefaultGroupName=KünyeX
OutputDir=..\\Nihai_Setup_Dosyalari
OutputBaseFilename=Setup_KunyeX_{loc_name}
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
{ICON_ISS_CMD}

[Tasks]
Name: "desktopicon"; Description: "KünyeX Ana Program masaüstü kısayolu oluştur"; GroupDescription: "Ek Görevler:"; Flags: unchecked
"""
    if PDF_CEVIRICI_MEVCUT:
        iss_content += 'Name: "pdficon"; Description: "KünyeX PDF Çevirici masaüstü kısayolu oluştur"; GroupDescription: "Ek Görevler:"; Flags: unchecked\n'

    iss_content += f"""
[Files]
Source: "..\\{folder_name}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{autodesktop}}\\KünyeX {loc_name.replace('_', ' ')}"; Filename: "{{app}}\\{exe_name}"; Tasks: desktopicon
Name: "{{group}}\\KünyeX {loc_name.replace('_', ' ')}"; Filename: "{{app}}\\{exe_name}"
Name: "{{group}}\\KünyeX Kaldır"; Filename: "{{uninstallexe}}"
"""
    if PDF_CEVIRICI_MEVCUT:
        iss_content += f"""Name: "{{autodesktop}}\\KünyeX PDF Çevirici"; Filename: "{{app}}\\KunyeX_PDF_Cevirici.exe"; Tasks: pdficon
Name: "{{group}}\\KünyeX PDF Çevirici"; Filename: "{{app}}\\KunyeX_PDF_Cevirici.exe"
"""

    iss_content += f"""
[Run]
Filename: "{{app}}\\{exe_name}"; Description: "KünyeX'i Başlat"; Flags: nowait postinstall skipifsilent shellexec
Filename: "{{app}}\\Lisans_Anahtari.txt"; Description: "Lisans Anahtarımı Göster"; Flags: postinstall shellexec skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{{commonappdata}}\\KunyeXPremium\\KunyeX_{loc_name}"
"""

    with open(f"{ISS_DIR}/{loc_name}.iss", "w", encoding="utf-8") as iss_file:
        iss_file.write(iss_content)
        
    bat_content += f"\"C:\\Program Files\\Inno Setup 7\\ISCC.exe\" \"Kurulum_Scriptleri\\{loc_name}.iss\" >nul\n"

bat_content += """
echo .
echo [3/3] OPERASYON BASARIYLA TAMAMLANDI! 
echo Tum subelerin profesyonel Setup (Kurulum) EXE'leri ve Sifre Dosyalari "KunyeX_Uretim_Hatti\\Nihai_Setup_Dosyalari" icinde hazir.
echo Firebase JSON dosyaniz "KunyeX_Uretim_Hatti\\Firebase_Icin_Lisans_Veritabani.json" yolundadir.
pause
"""

with open(f"{OUTPUT_DIR}/exe_derle.bat", "w", encoding="utf-8") as bat_file:
    bat_file.write(bat_content)

print(f"[✓] SAF DERLEME FABRİKASI AKTİF! Lütfen '{OUTPUT_DIR}' içindeki exe_derle.bat dosyasını çalıştırın.")