import customtkinter as ctk
import hashlib
import threading
import time
import sys
import os
import ctypes
import qrcode
from datetime import datetime
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- PREMIUM KURUMSAL AYARLAR ---
ctk.set_appearance_mode("dark")
BG_COLOR = "#0F1923"         
ACCENT_COLOR = "#007AFF"     
TEXT_COLOR = "#ECE8E1"       
SURFACE_COLOR = "#1F2B39"    
TRANSPARENT_KEY = "#0F1924"  

# TEST İÇİN GEÇERLİ HASH (TRXL-TEST-KEY-0000)
VALID_HASH = "f9dbbd3694f4a3de0ddbc2a98c11e74ebf4ffb41865c197ba759d57a2daed8b4"

class TraxlePrintEngine:
    def __init__(self):
        self.OUTPUT_DIR = "Baskı_Ciktilari"
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        
        try:
            pdfmetrics.registerFont(TTFont('Arial', 'C:\\Windows\\Fonts\\arial.ttf'))
            pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:\\Windows\\Fonts\\arialbd.ttf'))
            self.font_regular = 'Arial'
            self.font_bold = 'Arial-Bold'
        except:
            self.font_regular = 'Helvetica'
            self.font_bold = 'Helvetica-Bold'

        self.PAGE_WIDTH = 150 * mm
        self.PAGE_HEIGHT = 120 * mm
        
    def _generate_qr_temp(self, data):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=0)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        temp_path = os.path.join(self.OUTPUT_DIR, "temp_qr.png")
        img.save(temp_path)
        return temp_path

    def build_label(self, data_dict, filename="hks_kunye.pdf"):
        output_path = os.path.join(self.OUTPUT_DIR, filename)
        c = canvas.Canvas(output_path, pagesize=(self.PAGE_WIDTH, self.PAGE_HEIGHT))
        margin = 5 * mm
        
        # 1. ÜST BÖLÜM
        qr_size = 22 * mm 
        qr_path = self._generate_qr_temp(data_dict.get('kunye_no', 'TRAXLE'))
        c.drawImage(qr_path, self.PAGE_WIDTH - margin - qr_size, self.PAGE_HEIGHT - margin - qr_size, width=qr_size, height=qr_size)
        
        c.setFont(self.font_bold, 55) 
        title = data_dict.get('ana_baslik', 'BİBER KAPYA').upper()
        c.drawString(margin, self.PAGE_HEIGHT - margin - 16*mm, title)

        # 2. ORTA BÖLÜM
        mid_y = 66 * mm 
        c.setFont(self.font_bold, 65)
        c.drawCentredString(self.PAGE_WIDTH / 2, mid_y - 8*mm, "(KG)")
        
        # LOGOLAR (Dosya varsa basar, yoksa boş bırakır)
        if os.path.exists("mevsiminden.png"):
            c.drawImage("mevsiminden.png", margin, mid_y - 10*mm, width=40*mm, height=15*mm, mask='auto', preserveAspectRatio=True)
        else:
            c.setStrokeColorRGB(0.5,0.5,0.5); c.rect(margin, mid_y - 10*mm, 40*mm, 15*mm)

        right_logo_x = self.PAGE_WIDTH - margin - 35*mm
        if os.path.exists("yerli_uretim.png"):
            c.drawImage("yerli_uretim.png", right_logo_x, mid_y - 10*mm, width=35*mm, height=15*mm, mask='auto', preserveAspectRatio=True)
        else:
            c.setStrokeColorRGB(0.5,0.5,0.5); c.rect(right_logo_x, mid_y - 10*mm, 35*mm, 15*mm)

        # 3. ALT BÖLÜM (TABLO)
        table_data = [
            ["KÜNYE NO", data_dict.get('kunye_no', ''), "Gideceği Yer", data_dict.get('gidecegi_yer', '')],
            ["Tarihi", data_dict.get('tarih', ''), "Üreticinin Unvanı", data_dict.get('uretici', '')],
            ["Malın Adı", data_dict.get('malin_adi', ''), "Sahibinin Unvanı", data_dict.get('sahibi', '')],
            ["Malın Cinsi", data_dict.get('malin_cinsi', ''), "Bildirimcinin Unvanı", data_dict.get('bildirimci', '')],
            ["Malın Türü", data_dict.get('malin_turu', ''), "Malın Miktarı", data_dict.get('miktar', '')],
            ["Gümrük/Kapı Yeri", data_dict.get('uretildigi_yer', ''), "Araç Plaka", data_dict.get('plaka', '')]
        ]

        col_widths = [30*mm, 40*mm, 35*mm, 35*mm]
        t = Table(table_data, colWidths=col_widths, rowHeights=8*mm)
        
        t.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), self.font_regular),
            ('FONTSIZE', (0,0), (-1,-1), 5.5), 
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
            ('BACKGROUND', (2,0), (2,-1), colors.whitesmoke),
        ]))

        t.wrapOn(c, self.PAGE_WIDTH, self.PAGE_HEIGHT)
        t.drawOn(c, margin, margin) 

        c.save()
        if os.path.exists(qr_path): os.remove(qr_path)
        return output_path


class TraxlePremiumClient(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True) 
        self.geometry("480x340")
        self.wm_attributes("-transparentcolor", TRANSPARENT_KEY)
        self.configure(fg_color=TRANSPARENT_KEY)
        self.center_window(480, 340)

        self._offsetx = 0
        self._offsety = 0

        self.bg_frame = ctk.CTkFrame(self, fg_color=BG_COLOR, corner_radius=20)
        self.bg_frame.pack(fill="both", expand=True, padx=2, pady=2)

        self.build_custom_titlebar()
        self.build_login_elements()

        self.after(10, self.set_appwindow)
        
        self.print_engine = TraxlePrintEngine()

    def center_window(self, w, h):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{int((screen_width/2) - (w/2))}+{int((screen_height/2) - (h/2))}')

    def set_appwindow(self):
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        style = style & ~0x00000080 | 0x00040000
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
        self.wm_withdraw()
        self.after(10, self.wm_deiconify)

    def build_custom_titlebar(self):
        self.title_bar = ctk.CTkFrame(self.bg_frame, height=40, fg_color="transparent", corner_radius=20)
        self.title_bar.pack(side="top", fill="x", pady=(5, 0))
        self.title_bar.bind("<Button-1>", self.click_window)
        self.title_bar.bind("<B1-Motion>", self.drag_window)

        self.close_btn = ctk.CTkButton(self.title_bar, text="✕", width=40, height=40, fg_color="transparent", hover_color="#FF4655", text_color="gray", command=self.quit_app)
        self.close_btn.pack(side="right", padx=(0, 5))

        self.minimize_btn = ctk.CTkButton(self.title_bar, text="—", width=40, height=40, fg_color="transparent", hover_color=SURFACE_COLOR, text_color="gray", command=self.iconify)
        self.minimize_btn.pack(side="right")

        self.logo_label = ctk.CTkLabel(self.title_bar, text="TRAXLE IDENTITY", font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"), text_color="gray")
        self.logo_label.pack(side="left", padx=20)
        self.logo_label.bind("<Button-1>", self.click_window)
        self.logo_label.bind("<B1-Motion>", self.drag_window)

    def build_login_elements(self):
        self.main_frame = ctk.CTkFrame(self.bg_frame, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        self.header = ctk.CTkLabel(self.main_frame, text="Sistem Aktivasyonu", font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"), text_color=TEXT_COLOR)
        self.header.pack(pady=(10, 5))

        self.subheader = ctk.CTkLabel(self.main_frame, text="Size özel atanan lisans anahtarını girin.", font=ctk.CTkFont(family="Helvetica", size=12), text_color="gray")
        self.subheader.pack(pady=(0, 20))

        self.serial_entry = ctk.CTkEntry(self.main_frame, placeholder_text="XXXX-XXXX-XXXX-XXXX", width=300, height=45, font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"), justify="center", fg_color=SURFACE_COLOR, border_color=SURFACE_COLOR, corner_radius=12, text_color=TEXT_COLOR)
        self.serial_entry.pack(pady=10)
        self.serial_entry.bind("<KeyRelease>", self.format_serial)

        self.activate_btn = ctk.CTkButton(self.main_frame, text="DOĞRULA VE BAŞLAT", width=300, height=40, corner_radius=12, fg_color=ACCENT_COLOR, hover_color="#005ea6", font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"), command=self.start_verification)
        self.activate_btn.pack(pady=10)

        self.status_container = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=50, width=300)
        self.status_container.pack_propagate(False) 
        self.status_container.pack(pady=5)

        self.progress = ctk.CTkProgressBar(self.status_container, width=300, height=4, fg_color=SURFACE_COLOR, progress_color=ACCENT_COLOR)
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(self.status_container, text="", font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"))
        self.status_label.pack(side="bottom", pady=2)

    def format_serial(self, event):
        if event.keysym in ('BackSpace', 'Delete', 'Left', 'Right', 'Up', 'Down'): return
        text = self.serial_entry.get().replace("-", "").upper()
        clean_text = ''.join(e for e in text if e.isalnum())
        formatted = "-".join([clean_text[i:i+4] for i in range(0, len(clean_text), 4)])
        if len(formatted) > 19: formatted = formatted[:19]
        self.serial_entry.delete(0, "end")
        self.serial_entry.insert(0, formatted)

    def click_window(self, event):
        self._offsetx, self._offsety = event.x, event.y

    def drag_window(self, event):
        self.geometry(f"+{self.winfo_pointerx() - self._offsetx}+{self.winfo_pointery() - self._offsety}")

    def quit_app(self):
        self.destroy(); sys.exit()

    def start_verification(self):
        user_input = self.serial_entry.get().strip().upper()
        if len(user_input) < 19:
            self.show_status("Eksik lisans anahtarı. 16 haneli olmalıdır.", "#FF4655")
            return
        self.activate_btn.configure(state="disabled", text="ŞİFRELENİYOR...")
        self.serial_entry.configure(state="disabled")
        self.show_status("", "gray")
        self.progress.pack(side="top", pady=(0, 5))
        self.progress.start()
        threading.Thread(target=self.crypto_worker, args=(user_input,), daemon=True).start()

    def crypto_worker(self, user_input):
        time.sleep(1.0) 
        input_hash = hashlib.sha256(user_input.encode()).hexdigest()
        if input_hash == VALID_HASH:
            self.after(0, lambda: self.verification_success())
        else:
            self.after(0, lambda: self.verification_failed())

    def verification_failed(self):
        self.progress.stop(); self.progress.pack_forget() 
        self.activate_btn.configure(state="normal", text="DOĞRULA VE BAŞLAT")
        self.serial_entry.configure(state="normal")
        self.show_status("Geçersiz lisans. Lütfen tekrar deneyin.", "#FF4655")

    def show_status(self, message, color):
        self.status_label.configure(text=message, text_color=color)

    # ==============================================================
    # 2. FAZ: ARAYÜZ DEĞİŞİMİ VE VERİ GİRİŞ FORMU
    # ==============================================================
    def verification_success(self):
        self.progress.stop(); self.progress.set(1); self.progress.configure(progress_color="#00CC66") 
        self.activate_btn.configure(fg_color="#00CC66", text="ERİŞİM ONAYLANDI")
        self.show_status("Bağlantı güvenli. Sistem başlatılıyor...", "#00CC66")
        
        # 1 saniye sonra giriş ekranını sil ve asıl programa geç
        self.after(1000, self.transition_to_dashboard)

    def transition_to_dashboard(self):
        # Eski frame'i tamamen yok et
        self.main_frame.destroy()
        
        # Ekranı formu alacak kadar yumuşakça büyüt
        self.center_window(800, 650)
        self.logo_label.configure(text="TRAXLE IDENTITY | HKS KÜNYE MOTORU")

        # Formu Barındıracak Yeni Frame (Scrollable)
        self.dashboard_frame = ctk.CTkScrollableFrame(self.bg_frame, fg_color="transparent")
        self.dashboard_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Başlık
        form_header = ctk.CTkLabel(self.dashboard_frame, text="HKS Künye Oluşturucu", font=ctk.CTkFont(size=22, weight="bold"))
        form_header.grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="w")

        # Form Veri Sözlüğü (Input objelerini tutmak için)
        self.form_inputs = {}
        
        # Etiket ve Key listesi
        fields = [
            ("Ana Başlık (Örn: BİBER KAPYA):", "ana_baslik"),
            ("Künye No:", "kunye_no"),
            ("Malın Adı:", "malin_adi"),
            ("Malın Cinsi:", "malin_cinsi"),
            ("Malın Türü:", "malin_turu"),
            ("Miktar (Kg):", "miktar"),
            ("Üretici Unvanı:", "uretici"),
            ("Mal Sahibinin Unvanı:", "sahibi"),
            ("Bildirimcinin Unvanı:", "bildirimci"),
            ("Gümrük / Kapı Yeri:", "uretildigi_yer"),
            ("Gideceği Yer:", "gidecegi_yer"),
            ("Araç Plaka / Belge No:", "plaka")
        ]

        # Formu 2 sütun (grid) halinde çizdir
        row = 1
        col = 0
        for label_text, key in fields:
            # Container
            container = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
            container.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            # Label
            lbl = ctk.CTkLabel(container, text=label_text, font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
            lbl.pack(anchor="w")
            
            # Input
            inp = ctk.CTkEntry(container, width=320, height=35, fg_color=SURFACE_COLOR, border_width=1)
            inp.pack(anchor="w", pady=(2, 0))
            
            self.form_inputs[key] = inp

            col += 1
            if col > 1:
                col = 0
                row += 1

        # PDF Çıktı Butonu
        self.print_btn = ctk.CTkButton(self.dashboard_frame, text="PDF ÇIKTISI OLUŞTUR", height=45, fg_color="#00CC66", hover_color="#00994C", font=ctk.CTkFont(size=14, weight="bold"), command=self.generate_pdf)
        self.print_btn.grid(row=row, column=0, columnspan=2, pady=(30, 20))
        
        self.form_status = ctk.CTkLabel(self.dashboard_frame, text="", font=ctk.CTkFont(size=13, weight="bold"))
        self.form_status.grid(row=row+1, column=0, columnspan=2)

    def generate_pdf(self):
        # Butonu kilitle
        self.print_btn.configure(state="disabled", text="PDF OLUŞTURULUYOR...")
        self.form_status.configure(text="")
        
        # Inputlardaki verileri çek
        data_dict = {}
        for key, entry in self.form_inputs.items():
            data_dict[key] = entry.get().strip()

        # Tarihi otomatik ekle
        data_dict["tarih"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Motoru arka planda çalıştır ki arayüz donmasın
        threading.Thread(target=self.print_worker, args=(data_dict,), daemon=True).start()

    def print_worker(self, data_dict):
        try:
            filename = f"Kunye_{data_dict.get('kunye_no', 'Yeni')}.pdf"
            output_path = self.print_engine.build_label(data_dict, filename)
            self.after(0, lambda: self.print_success(output_path))
        except Exception as e:
            self.after(0, lambda: self.print_error(str(e)))

    def print_success(self, path):
        self.print_btn.configure(state="normal", text="YENİ PDF ÇIKTISI OLUŞTUR")
        self.form_status.configure(text=f"✓ Başarılı! Dosya '{path}' konumuna kaydedildi.", text_color="#00CC66")
        
        # Çıktı alındıktan sonra PDF'i otomatik aç (Windows için)
        try:
            os.startfile(path)
        except:
            pass

    def print_error(self, error_msg):
        self.print_btn.configure(state="normal", text="PDF ÇIKTISI OLUŞTUR")
        self.form_status.configure(text=f"✗ Hata oluştu: {error_msg}", text_color="#FF4655")

if __name__ == "__main__":
    app = TraxlePremiumClient()
    app.mainloop()