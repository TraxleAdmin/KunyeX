import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

FIREBASE_LICENSE_URL = "https://kunyex-lisans-default-rtdb.europe-west1.firebasedatabase.app"


class KunyeXUpdateError(Exception):
    pass


class SafeUpdateEngine:
    """Hash doğrulamalı ve rollback destekli güvenli güncelleme motoru.

    Bu dosya PDF/ODP okuma motorlarından tamamen bağımsızdır.
    Sadece güncelleme manifestini okur, yeni exe'yi indirir, SHA-256 doğrular
    ve çalışan exe kapandıktan sonra dosya değişimini yapacak bir .bat üretir.
    """

    def __init__(self, current_version="0.0.0", manifest_url=None, app_name="KunyeX"):
        self.current_version = str(current_version)
        self.manifest_url = manifest_url
        self.app_name = app_name
        self.timeout = 15

    @staticmethod
    def sha256_file(path):
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest().lower()

    @staticmethod
    def _version_tuple(value):
        parts = []
        for item in str(value).replace("v", "").split("."):
            try:
                parts.append(int(item))
            except ValueError:
                parts.append(0)
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts[:4])

    def _read_json_url(self, url):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "KunyeX-Updater/1.0",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
        return json.loads(raw) if raw else {}

    def fetch_manifest(self):
        if not self.manifest_url:
            return {}
        try:
            return self._read_json_url(self.manifest_url)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            raise KunyeXUpdateError(f"Güncelleme manifesti okunamadı: {exc}") from exc

    def is_update_available(self, manifest):
        latest_version = manifest.get("version") or manifest.get("latest_version")
        if not latest_version:
            return False
        return self._version_tuple(latest_version) > self._version_tuple(self.current_version)

    def _resolve_package(self, manifest, exe_name):
        files = manifest.get("files")
        if isinstance(files, dict):
            package = files.get(exe_name) or files.get("default") or next(iter(files.values()), None)
            if isinstance(package, dict):
                return package

        return {
            "url": manifest.get("url") or manifest.get("download_url") or manifest.get("exe_url"),
            "sha256": manifest.get("sha256") or manifest.get("hash") or manifest.get("checksum"),
            "size": manifest.get("size"),
        }

    def download_and_verify(self, manifest, exe_name=None):
        exe_name = exe_name or os.path.basename(sys.executable)
        package = self._resolve_package(manifest, exe_name)
        download_url = package.get("url")
        expected_hash = str(package.get("sha256") or "").lower().strip()

        if not download_url:
            raise KunyeXUpdateError("Manifest içinde indirme URL'si yok.")
        if not expected_hash:
            raise KunyeXUpdateError("Manifest içinde SHA-256 hash yok. Güvenli güncelleme durduruldu.")

        update_dir = os.path.join(tempfile.gettempdir(), "KunyeX_Update")
        os.makedirs(update_dir, exist_ok=True)
        target_name = exe_name if exe_name.lower().endswith(".exe") else "KunyeX_Update.exe"
        download_path = os.path.join(update_dir, target_name)
        partial_path = download_path + ".part"

        request = urllib.request.Request(download_url, headers={"User-Agent": "KunyeX-Updater/1.0"})
        with urllib.request.urlopen(request, timeout=self.timeout) as response, open(partial_path, "wb") as out:
            shutil.copyfileobj(response, out, length=1024 * 1024)

        calculated_hash = self.sha256_file(partial_path)
        if calculated_hash != expected_hash:
            try:
                os.remove(partial_path)
            except OSError:
                pass
            raise KunyeXUpdateError("İndirilen dosyanın hash değeri uyuşmadı. Güncelleme iptal edildi.")

        if os.path.exists(download_path):
            os.remove(download_path)
        os.replace(partial_path, download_path)
        return download_path

    def prepare_windows_swap(self, downloaded_exe_path, current_exe_path=None):
        if sys.platform != "win32":
            raise KunyeXUpdateError("Otomatik exe değişimi yalnızca Windows üzerinde desteklenir.")

        current_exe_path = current_exe_path or sys.executable
        if not os.path.exists(current_exe_path):
            raise KunyeXUpdateError("Mevcut exe bulunamadı.")
        if not os.path.exists(downloaded_exe_path):
            raise KunyeXUpdateError("İndirilen exe bulunamadı.")

        backup_path = current_exe_path + ".old"
        rollback_path = current_exe_path + ".rollback"
        bat_path = os.path.join(tempfile.gettempdir(), "KunyeX_Apply_Update.bat")

        script = f"""@echo off
setlocal
ping 127.0.0.1 -n 3 > nul
if exist "{rollback_path}" del /f /q "{rollback_path}" > nul 2>&1
if exist "{backup_path}" del /f /q "{backup_path}" > nul 2>&1
ren "{current_exe_path}" "{os.path.basename(backup_path)}"
if errorlevel 1 goto rollback
copy /y "{downloaded_exe_path}" "{current_exe_path}" > nul
if errorlevel 1 goto rollback
start "" "{current_exe_path}"
exit /b 0
:rollback
if exist "{backup_path}" copy /y "{backup_path}" "{current_exe_path}" > nul
start "" "{current_exe_path}"
exit /b 1
"""
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(script)
        return bat_path

    def apply_update_and_exit(self, bat_path):
        if sys.platform == "win32":
            subprocess.Popen(["cmd", "/c", bat_path], creationflags=0x08000000)
            time.sleep(0.2)
            os._exit(0)
        raise KunyeXUpdateError("Bu platformda otomatik yeniden başlatma desteklenmiyor.")

    def run_safe_update(self, manifest_url=None, current_exe_path=None):
        if manifest_url:
            self.manifest_url = manifest_url
        manifest = self.fetch_manifest()
        if not self.is_update_available(manifest):
            return {"updated": False, "message": "Güncel sürüm kullanılıyor."}
        downloaded = self.download_and_verify(manifest, os.path.basename(current_exe_path or sys.executable))
        bat_path = self.prepare_windows_swap(downloaded, current_exe_path)
        return {"updated": True, "manifest": manifest, "downloaded": downloaded, "apply_script": bat_path}
