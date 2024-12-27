import tkinter as tk
import sys
import os
import math
import time
import random
from ctypes import windll
import webbrowser
import pyautogui
import pyperclip
import keyboard
import speech_recognition as sr
import threading
import urllib.parse
import subprocess
import requests
from datetime import datetime
import json

def force_quit():
    os._exit(0)

def get_weather():
    try:
        # Google'da Akyazı hava durumu araması yap
        search_url = "https://www.google.com/search?q=akyazı+hava+durumu"
        webbrowser.open(search_url)
        return "Akyazı hava durumu açılıyor..."
    except:
        return "Hava durumu açılamadı"

def save_note(note):
    try:
        # Masaüstü yolunu al
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        # Notlar.txt dosyasının tam yolu
        note_file = os.path.join(desktop, "Notlar.txt")
        
        # Tarih ve saat ile birlikte notu kaydet
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
        with open(note_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {note}\n")
        
        return "Not kaydedildi!"
    except Exception as e:
        print(f"Not kaydedilirken hata: {e}")
        return "Not kaydedilemedi!"

def open_whatsapp_desktop():
    try:
        # WhatsApp masaüstü uygulamasını aç
        whatsapp_path = os.path.expandvars("%LocalAppData%\\WhatsApp\\WhatsApp.exe")
        subprocess.Popen([whatsapp_path])
        time.sleep(2)  # Uygulamanın açılmasını bekle
        
        # Arama kutusuna odaklan
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"WhatsApp açılırken hata: {e}")
        return False

def select_whatsapp_contact(contact_number):
    try:
        # Tab tuşuna contact_number kadar bas (her basışta bir sonraki sohbete geçer)
        for _ in range(contact_number):
            time.sleep(0.2)
            pyautogui.press('tab')
        time.sleep(0.2)
        pyautogui.press('enter')
        return True
    except Exception as e:
        print(f"Kişi seçilirken hata: {e}")
        return False

def send_whatsapp_message(message):
    try:
        time.sleep(0.5)
        pyperclip.copy(message)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        return True
    except Exception as e:
        print(f"Mesaj gönderilirken hata: {e}")
        return False

class VoiceRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 3000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.is_listening = False
        self.callback = None
        
    def start_listening(self, callback):
        self.callback = callback
        self.is_listening = True
        
    def stop_listening(self):
        self.is_listening = False
    
    def listen_once(self):
        try:
            with sr.Microphone() as source:
                print("Dinleniyor...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                try:
                    text = self.recognizer.recognize_google(audio, language='tr-TR')
                    print(f"Algılanan: {text}")
                    if self.callback and self.is_listening:
                        self.callback(text.lower())
                except sr.UnknownValueError:
                    print("Anlaşılamadı")
                except sr.RequestError as e:
                    print(f"Hata: {e}")
        except Exception as e:
            print(f"Mikrofon hatası: {e}")

class DraggableWindow:
    def __init__(self, root):
        self.root = root
        self.root.bind('<Button-3>', self.show_popup)
        self.root.bind('<Control-q>', lambda e: force_quit())
        
    def show_popup(self, event):
        popup = tk.Menu(self.root, tearoff=0)
        popup.add_command(label="Kapat", command=force_quit)
        popup.tk_popup(event.x_root, event.y_root)

class SimpleTurtle:
    def __init__(self, canvas):
        self.canvas = canvas
        self.parts = []
        self.expression = "normal"
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        self.rotation = 0
        self.size = 40
        self.smoke_time = 0
        self.whatsapp_state = None  # wp, wp_contact, wp_message
        self.whatsapp_contact = 0
        self.whatsapp_message = ""
        
        # Animasyon başlat
        self.animate()
    
    def draw(self):
        # Önceki çizimleri temizle
        for part in self.parts:
            self.canvas.delete(part)
        self.parts.clear()
        
        # Dönüş açısını güncelle
        if self.expression == "listening":
            self.rotation += 8  # Hızlı dönüş (sağa)
        else:
            self.rotation += 1  # Yavaş dönüş (sağa)
        
        # Kaplumbağa çizimi
        angle = math.radians(self.rotation)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # Kabuk noktaları
        shell_points = []
        for i in range(8):
            a = math.radians(i * 45 + self.rotation)
            x = self.x + self.size * math.cos(a)
            y = self.y + self.size * 0.8 * math.sin(a)
            shell_points.extend([x, y])
        
        # Kabuk çizimi
        self.parts.append(self.canvas.create_polygon(
            shell_points,
            fill='#90EE90',
            outline='black',
            width=2,
            smooth=True))
        
        # İç desen
        inner_size = self.size * 0.7
        inner_points = []
        for i in range(6):
            a = math.radians(i * 60 + self.rotation)
            x = self.x + inner_size * math.cos(a)
            y = self.y + inner_size * 0.8 * math.sin(a)
            inner_points.extend([x, y])
        
        self.parts.append(self.canvas.create_polygon(
            inner_points,
            fill='#006400',
            outline='black',
            width=1,
            smooth=True))
        
        # Baş
        head_x = self.x + self.size * cos_a
        head_y = self.y + self.size * sin_a
        self.parts.append(self.canvas.create_oval(
            head_x - 10, head_y - 10,
            head_x + 10, head_y + 10,
            fill='#90EE90',
            outline='black',
            width=2))
        
        # Sigara
        sigara_uzunluk = 15
        sigara_açı = angle + math.pi/6  # Biraz yukarı doğru
        sigara_x = head_x + 8 * math.cos(sigara_açı)
        sigara_y = head_y + 8 * math.sin(sigara_açı)
        sigara_uç_x = sigara_x + sigara_uzunluk * math.cos(sigara_açı)
        sigara_uç_y = sigara_y + sigara_uzunluk * math.sin(sigara_açı)
        
        # Sigara çizimi (beyaz kısım)
        self.parts.append(self.canvas.create_line(
            sigara_x, sigara_y,
            sigara_uç_x, sigara_uç_y,
            fill='white', width=3))
        
        # Sigara ucu (kırmızı)
        self.parts.append(self.canvas.create_oval(
            sigara_uç_x - 2, sigara_uç_y - 2,
            sigara_uç_x + 2, sigara_uç_y + 2,
            fill='red', outline='red'))
        
        # Duman efekti
        self.smoke_time += 0.1
        for i in range(3):
            t = self.smoke_time + i * 2
            smoke_x = sigara_uç_x + (10 + i * 5) * math.cos(sigara_açı) + math.sin(t + i) * 5
            smoke_y = sigara_uç_y + (10 + i * 5) * math.sin(sigara_açı) + math.cos(t + i) * 5
            smoke_size = 3 + i * 2
            self.parts.append(self.canvas.create_oval(
                smoke_x - smoke_size, smoke_y - smoke_size,
                smoke_x + smoke_size, smoke_y + smoke_size,
                fill='#DDDDDD', outline=''))
        
        # Bacaklar
        leg_positions = [45, 135, 225, 315]
        for angle_deg in leg_positions:
            a = math.radians(angle_deg + self.rotation)
            leg_x = self.x + self.size * 0.8 * math.cos(a)
            leg_y = self.y + self.size * 0.8 * math.sin(a)
            self.parts.append(self.canvas.create_oval(
                leg_x - 8, leg_y - 8,
                leg_x + 8, leg_y + 8,
                fill='#90EE90',
                outline='black',
                width=2))
        
        # Kuyruk
        tail_x = self.x - self.size * cos_a
        tail_y = self.y - self.size * sin_a
        self.parts.append(self.canvas.create_oval(
            tail_x - 5, tail_y - 5,
            tail_x + 5, tail_y + 5,
            fill='#90EE90',
            outline='black',
            width=2))
    
    def animate(self):
        self.draw()
        self.canvas.after(50, self.animate)  # Daha yavaş animasyon için 50ms

try:
    # Ekran boyutlarını al
    user32 = windll.user32
    SCREEN_WIDTH = user32.GetSystemMetrics(0)
    SCREEN_HEIGHT = user32.GetSystemMetrics(1)
    
    # Pencere boyutu
    WINDOW_WIDTH = 400
    WINDOW_HEIGHT = 200  # Daha küçük pencere
    
    # Ana pencereyi oluştur
    root = tk.Tk()
    root.overrideredirect(True)
    
    # Pencereyi sağ alt köşeye yerleştir
    x_pos = SCREEN_WIDTH - WINDOW_WIDTH - 20
    y_pos = SCREEN_HEIGHT - WINDOW_HEIGHT - 40
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x_pos}+{y_pos}")
    
    # Pencere ayarları
    root.configure(bg='')  # Boş arka plan rengi
    root.attributes('-alpha', 1.0)  # Tam opaklık
    root.attributes('-topmost', True)
    root.attributes('-transparentcolor', 'white')  # Beyaz rengi saydam yap
    
    # Canvas oluştur (saydam arka plan için)
    canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT,
                      bg='white', highlightthickness=0)
    canvas.pack(expand=True, fill='both')
    
    # Kaplumbağayı oluştur
    turtle = SimpleTurtle(canvas)
    
    # Ses algılama için özel işleyici
    def start_listening():
        turtle.expression = "listening"  # Sağa dönmeye başla
        threading.Thread(target=listen_continuously, daemon=True).start()
    
    def stop_listening():
        turtle.expression = "normal"  # Sola dönmeye başla
    
    def listen_continuously():
        while turtle.expression == "listening":
            try:
                with sr.Microphone() as source:
                    recognizer = sr.Recognizer()
                    recognizer.adjust_for_ambient_noise(source, duration=0.2)
                    print("Dinleniyor...")
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    try:
                        text = recognizer.recognize_google(audio, language='tr-TR')
                        print(f"Algılanan: {text}")
                        
                        # WhatsApp durumunu kontrol et
                        if turtle.whatsapp_state == "wp":
                            # Kişi numarasını al
                            try:
                                if "bir" in text.lower():
                                    turtle.whatsapp_contact = 1
                                elif "iki" in text.lower():
                                    turtle.whatsapp_contact = 2
                                elif "üç" in text.lower():
                                    turtle.whatsapp_contact = 3
                                elif "dört" in text.lower():
                                    turtle.whatsapp_contact = 4
                                elif "beş" in text.lower():
                                    turtle.whatsapp_contact = 5
                                
                                if turtle.whatsapp_contact > 0:
                                    if select_whatsapp_contact(turtle.whatsapp_contact):
                                        turtle.whatsapp_state = "wp_message"
                                        print("Mesajınızı söyleyin...")
                            except:
                                print("Kişi seçilemedi")
                                turtle.whatsapp_state = None
                        
                        elif turtle.whatsapp_state == "wp_message":
                            # Mesajı gönder
                            if send_whatsapp_message(text):
                                print("Mesaj gönderildi!")
                            turtle.whatsapp_state = None
                        
                        # Normal komutları işle
                        elif "vip" in text.lower():
                            if open_whatsapp_desktop():
                                turtle.whatsapp_state = "wp"
                                print("Kaçıncı kişiye mesaj göndermek istiyorsunuz? (bir, iki, üç, dört, beş)")
                        
                        elif "hava" in text.lower():
                            webbrowser.open("https://www.google.com/search?q=akyazı+hava+durumu")
                        elif "yok" in text.lower():
                            pyautogui.hotkey('ctrl', 'w')
                        elif "kimya" in text.lower():
                            webbrowser.open("https://www.youtube.com/results?search_query=görkem+şahin")
                        elif "fizik" in text.lower():
                            webbrowser.open("https://www.youtube.com/results?search_query=özcan+aykın")
                        elif "yol" in text.lower():
                            webbrowser.open("https://www.google.com/search?q=leyla+ile+mecnun")
                        elif "not ekle" in text.lower():
                            note = text.split("ekle")[-1].strip()
                            if note:
                                save_note(note)
                        elif "selam" in text.lower():
                            print("Kapatılıyor...")
                            force_quit()
                            
                    except sr.UnknownValueError:
                        print("Anlaşılamadı")
                    except sr.RequestError as e:
                        print(f"Hata: {e}")
            except Exception as e:
                print(f"Mikrofon hatası: {e}")
            time.sleep(0.1)
    
    # CTRL+1 ve CTRL+2 kombinasyonları için
    keyboard.add_hotkey('ctrl+1', start_listening)
    keyboard.add_hotkey('ctrl+2', stop_listening)
    
    # Pencere kontrolü
    DraggableWindow(root)
    
    # ESC ile kapatma
    root.bind('<Escape>', lambda e: force_quit())
    
    # Uygulamayı başlat
    root.mainloop()

except Exception as e:
    print(f"Hata oluştu: {str(e)}")
    input("Devam etmek için bir tuşa basın...")
    force_quit()
