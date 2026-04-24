@echo off
cd /d "%~dp0"
echo [1/3] Master EXE derleme islemi basliyor... (Lutfen bekleyin)
cd Kaynak_Kodlar
"C:\Python314\python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed --add-data "..\..\logo.png;." --icon="..\icon.ico" --hidden-import cryptography --hidden-import cv2 --hidden-import numpy --hidden-import charset_normalizer.cd --hidden-import charset_normalizer.md__mypyc --copy-metadata charset-normalizer --collect-all tkinterdnd2 --collect-all pdfplumber --collect-all charset_normalizer --collect-all pdf2image --collect-all PIL KunyeX_Master_Client.py

if not exist "dist\KunyeX_Master_Client.exe" (
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
echo Merkez Setup paketi uretiliyor...
mkdir "Dagitim_Paketleri\Merkez_PAKETI" >nul 2>&1
copy "Kaynak_Kodlar\dist\KunyeX_Master_Client.exe" "Dagitim_Paketleri\Merkez_PAKETI\KunyeX_Merkez.exe" >nul
xcopy "C:\Program Files\Tesseract-OCR" "Dagitim_Paketleri\Merkez_PAKETI\Tesseract-OCR\" /E /I /H /Y /Q >nul
xcopy "C:\poppler" "Dagitim_Paketleri\Merkez_PAKETI\poppler\" /E /I /H /Y /Q >nul
copy "..\mevsiminden.png" "Dagitim_Paketleri\Merkez_PAKETI\" >nul 2>&1
copy "..\yerli_uretim.png" "Dagitim_Paketleri\Merkez_PAKETI\" >nul 2>&1
copy "icon.ico" "Dagitim_Paketleri\Merkez_PAKETI\" >nul 2>&1
copy "logo.png" "Dagitim_Paketleri\Merkez_PAKETI\" >nul 2>&1
copy "Lisans_Anahtari_Merkez.txt" "Dagitim_Paketleri\Merkez_PAKETI\Lisans_Anahtari.txt" >nul
copy "Lisans_Anahtari_Merkez.txt" "Nihai_Setup_Dosyalari\Sifre_Merkez.txt" >nul
del "Lisans_Anahtari_Merkez.txt"
"C:\Program Files\Inno Setup 7\ISCC.exe" "Kurulum_Scriptleri\Merkez.iss" >nul
echo CIPLAKLI Setup paketi uretiliyor...
mkdir "Dagitim_Paketleri\CIPLAKLI_PAKETI" >nul 2>&1
copy "Kaynak_Kodlar\dist\KunyeX_Master_Client.exe" "Dagitim_Paketleri\CIPLAKLI_PAKETI\KunyeX_CIPLAKLI.exe" >nul
xcopy "C:\Program Files\Tesseract-OCR" "Dagitim_Paketleri\CIPLAKLI_PAKETI\Tesseract-OCR\" /E /I /H /Y /Q >nul
xcopy "C:\poppler" "Dagitim_Paketleri\CIPLAKLI_PAKETI\poppler\" /E /I /H /Y /Q >nul
copy "..\mevsiminden.png" "Dagitim_Paketleri\CIPLAKLI_PAKETI\" >nul 2>&1
copy "..\yerli_uretim.png" "Dagitim_Paketleri\CIPLAKLI_PAKETI\" >nul 2>&1
copy "icon.ico" "Dagitim_Paketleri\CIPLAKLI_PAKETI\" >nul 2>&1
copy "logo.png" "Dagitim_Paketleri\CIPLAKLI_PAKETI\" >nul 2>&1
copy "Lisans_Anahtari_CIPLAKLI.txt" "Dagitim_Paketleri\CIPLAKLI_PAKETI\Lisans_Anahtari.txt" >nul
copy "Lisans_Anahtari_CIPLAKLI.txt" "Nihai_Setup_Dosyalari\Sifre_CIPLAKLI.txt" >nul
del "Lisans_Anahtari_CIPLAKLI.txt"
"C:\Program Files\Inno Setup 7\ISCC.exe" "Kurulum_Scriptleri\CIPLAKLI.iss" >nul
echo DOSEMEALTI Setup paketi uretiliyor...
mkdir "Dagitim_Paketleri\DOSEMEALTI_PAKETI" >nul 2>&1
copy "Kaynak_Kodlar\dist\KunyeX_Master_Client.exe" "Dagitim_Paketleri\DOSEMEALTI_PAKETI\KunyeX_DOSEMEALTI.exe" >nul
xcopy "C:\Program Files\Tesseract-OCR" "Dagitim_Paketleri\DOSEMEALTI_PAKETI\Tesseract-OCR\" /E /I /H /Y /Q >nul
xcopy "C:\poppler" "Dagitim_Paketleri\DOSEMEALTI_PAKETI\poppler\" /E /I /H /Y /Q >nul
copy "..\mevsiminden.png" "Dagitim_Paketleri\DOSEMEALTI_PAKETI\" >nul 2>&1
copy "..\yerli_uretim.png" "Dagitim_Paketleri\DOSEMEALTI_PAKETI\" >nul 2>&1
copy "icon.ico" "Dagitim_Paketleri\DOSEMEALTI_PAKETI\" >nul 2>&1
copy "logo.png" "Dagitim_Paketleri\DOSEMEALTI_PAKETI\" >nul 2>&1
copy "Lisans_Anahtari_DOSEMEALTI.txt" "Dagitim_Paketleri\DOSEMEALTI_PAKETI\Lisans_Anahtari.txt" >nul
copy "Lisans_Anahtari_DOSEMEALTI.txt" "Nihai_Setup_Dosyalari\Sifre_DOSEMEALTI.txt" >nul
del "Lisans_Anahtari_DOSEMEALTI.txt"
"C:\Program Files\Inno Setup 7\ISCC.exe" "Kurulum_Scriptleri\DOSEMEALTI.iss" >nul
echo UNSAL Setup paketi uretiliyor...
mkdir "Dagitim_Paketleri\UNSAL_PAKETI" >nul 2>&1
copy "Kaynak_Kodlar\dist\KunyeX_Master_Client.exe" "Dagitim_Paketleri\UNSAL_PAKETI\KunyeX_UNSAL.exe" >nul
xcopy "C:\Program Files\Tesseract-OCR" "Dagitim_Paketleri\UNSAL_PAKETI\Tesseract-OCR\" /E /I /H /Y /Q >nul
xcopy "C:\poppler" "Dagitim_Paketleri\UNSAL_PAKETI\poppler\" /E /I /H /Y /Q >nul
copy "..\mevsiminden.png" "Dagitim_Paketleri\UNSAL_PAKETI\" >nul 2>&1
copy "..\yerli_uretim.png" "Dagitim_Paketleri\UNSAL_PAKETI\" >nul 2>&1
copy "icon.ico" "Dagitim_Paketleri\UNSAL_PAKETI\" >nul 2>&1
copy "logo.png" "Dagitim_Paketleri\UNSAL_PAKETI\" >nul 2>&1
copy "Lisans_Anahtari_UNSAL.txt" "Dagitim_Paketleri\UNSAL_PAKETI\Lisans_Anahtari.txt" >nul
copy "Lisans_Anahtari_UNSAL.txt" "Nihai_Setup_Dosyalari\Sifre_UNSAL.txt" >nul
del "Lisans_Anahtari_UNSAL.txt"
"C:\Program Files\Inno Setup 7\ISCC.exe" "Kurulum_Scriptleri\UNSAL.iss" >nul

echo .
echo [3/3] OPERASYON BASARIYLA TAMAMLANDI! 
echo Tum subelerin profesyonel Setup (Kurulum) EXE'leri ve Sifre Dosyalari "KunyeX_Uretim_Hatti\Nihai_Setup_Dosyalari" icinde hazir.
echo Firebase JSON dosyaniz "KunyeX_Uretim_Hatti\Firebase_Icin_Lisans_Veritabani.json" yolundadir.
pause
