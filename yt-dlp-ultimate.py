import customtkinter as ctk
from tkinter import messagebox, filedialog
import yt_dlp
import threading
import os
import sys
import logging
import datetime
import subprocess
import time

# --- КОНФИГУРАЦИЯ ---
LOCALE = {
    'ru': {
        'tab_full': 'Полное видео',
        'tab_frag': 'Фрагменты',
        'tab_queue': 'Загрузки',
        'tab_sett': '⚙ Настройки',
        'lbl_url': 'Ссылка на видео:',
        'lbl_quality': 'Качество / Формат:',
        'chk_convert': 'Конвертировать в MP4 (Fix звука)', # НОВАЯ СТРОКА
        'btn_add_full': 'ДОБАВИТЬ В ОЧЕРЕДЬ (ПОЛНОЕ)',
        'btn_add_frag': 'ДОБАВИТЬ ФРАГМЕНТ',
        'btn_start': '▶ ЗАПУСТИТЬ',
        'btn_stop': '⏸ ПАУЗА / СТОП',
        'btn_clear': '🗑 ЖЕСТКИЙ СБРОС И ОЧИСТКА', # ИЗМЕНИЛ ТЕКСТ
        'lbl_path': 'Папка сохранения:',
        'btn_change': 'Изменить...',
        'btn_open': '📂 Открыть',
        'status_ready': 'В ожидании',
        'status_work': 'Скачивание...',
        'status_paused': '⏸ Остановлено',
        'status_aborted': '⏹ Сброшено',
        'status_merge': 'Сборка MP4 (AAC)...',
        'sett_logs': 'Вести лог-файл',
        'sett_lang': 'Язык (Требует перезапуска):',
        'sett_update': '🛠 Обновить ядро',
        'sett_cookies': '🍪 Браузер для Cookies (при ошибке 403):',
        'version': 'Версия: 1.2 (Stability Fix)',
        'err_url': 'Ошибка: Нет ссылки!',
        'err_time': 'Ошибка: Конец < Начала',
        'msg_done': 'Все задачи выполнены!',
        'msg_upd_start': 'Обновление запущено... Ждите.',
        'msg_upd_ok': 'Готово! Перезапустите программу.',
        'q_best': 'Лучшее (Авто)',
        'q_1080': '1080p (Full HD)',
        'q_720': '720p (HD)',
        'q_audio': 'Только звук (MP3)'
    },
    'en': {
        'tab_full': 'Full Video',
        'tab_frag': 'Fragments',
        'tab_queue': 'Downloads',
        'tab_sett': '⚙ Settings',
        'lbl_url': 'Video URL:',
        'lbl_quality': 'Quality:',
        'chk_convert': 'Convert to MP4 (Audio Fix)', # NEW
        'btn_add_full': 'ADD FULL VIDEO',
        'btn_add_frag': 'ADD FRAGMENT',
        'btn_start': '▶ START',
        'btn_stop': '⏸ PAUSE / STOP',
        'btn_clear': '🗑 HARD RESET & CLEAR',
        'lbl_path': 'Save Path:',
        'btn_change': 'Change...',
        'btn_open': '📂 Open',
        'status_ready': 'Waiting',
        'status_work': 'Downloading...',
        'status_paused': '⏸ Paused',
        'status_aborted': '⏹ Reset',
        'status_merge': 'Merging MP4 (AAC)...',
        'sett_logs': 'Enable Logs',
        'sett_lang': 'Language (Restart required):',
        'sett_update': '🛠 Update Core',
        'sett_cookies': '🍪 Cookie Source (Fix 403):',
        'version': 'Version: 1.2 (Stability Fix)',
        'err_url': 'Error: No URL!',
        'err_time': 'Error: End < Start',
        'msg_done': 'All Done!',
        'msg_upd_start': 'Update started... Please wait.',
        'msg_upd_ok': 'Done! Please restart app.',
        'q_best': 'Best (Auto)',
        'q_1080': '1080p (Full HD)',
        'q_720': '720p (HD)',
        'q_audio': 'Audio Only (MP3)'
    }
}

QUALITY_MAP = {
    'q_best': 'bestvideo+bestaudio/best', 
    'q_1080': 'bestvideo[height=1080]+bestaudio/best[height=1080]',
    'q_720': 'bestvideo[height=720]+bestaudio/best[height=720]',
    'q_audio': 'audio'
}

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ModernYouTubeCutter(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.lang = 'ru'
        self.logging_enabled = True
        self.setup_logging()

        self.title("YT-DLP Ultimate v1.2")
        self.geometry("950x800") # Чуть увеличил высоту для галочек
        self.minsize(600, 500)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.base_path = self.get_base_path()
        self.ffmpeg_dir = self.base_path 
        self.ffmpeg_exe = os.path.join(self.base_path, 'ffmpeg.exe')
        self.ffprobe_exe = os.path.join(self.base_path, 'ffprobe.exe')

        default_dl = os.path.join(self.base_path, 'downloads')
        if not os.path.exists(default_dl): os.makedirs(default_dl)
        self.download_path_var = ctk.StringVar(value=default_dl)

        self.download_queue = [] 
        self.task_widgets = {} 
        self.last_ui_update = 0
        self.abort_flag = False 
        self.is_running = False

        self.create_ui()
        self.check_tools()

    def setup_logging(self):
        for h in logging.root.handlers[:]: logging.root.removeHandler(h)
        if self.logging_enabled:
            logging.basicConfig(filename='app_log.txt', level=logging.INFO, 
                                format='%(asctime)s - %(message)s', encoding='utf-8')

    def get_base_path(self):
        if getattr(sys, 'frozen', False): return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))

    def t(self, key):
        return LOCALE[self.lang].get(key, key)

    def force_paste(self, event):
        try:
            text = self.clipboard_get()
            widget = self.focus_get()
            if isinstance(widget, ctk.CTkEntry):
                widget.insert('insert', text)
                return "break"
        except: pass

    def check_ctrl_v(self, event):
        if event.keycode == 86: self.force_paste(event)

    def create_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="nsew")
        
        self.tab_full = self.tabview.add(self.t('tab_full'))
        self.tab_frag = self.tabview.add(self.t('tab_frag'))
        self.tab_queue = self.tabview.add(self.t('tab_queue'))
        self.tab_sett = self.tabview.add(self.t('tab_sett'))

        self.ui_full_tab()
        self.ui_frag_tab()
        self.ui_queue_tab()
        self.ui_settings_tab()
        self.ui_footer()

        self.bind_all("<Control-KeyPress>", self.check_ctrl_v)

    def ui_full_tab(self):
        t = self.tab_full
        t.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(t, text=self.t('lbl_url'), font=("Roboto", 14, "bold")).pack(anchor="w", pady=(20, 5), padx=30)
        self.entry_url_full = ctk.CTkEntry(t, height=40)
        self.entry_url_full.pack(fill="x", padx=30, pady=(0, 20))
        
        ctk.CTkLabel(t, text=self.t('lbl_quality')).pack(anchor="w", padx=30)
        vals = [self.t(k) for k in ['q_best', 'q_1080', 'q_720', 'q_audio']]
        self.combo_q_full = ctk.CTkOptionMenu(t, values=vals, width=250)
        self.combo_q_full.pack(anchor="w", padx=30, pady=(5, 5))
        
        # --- НОВАЯ ГАЛОЧКА (ПОЛНОЕ) ---
        self.chk_conv_full = ctk.CTkCheckBox(t, text=self.t('chk_convert'))
        self.chk_conv_full.select() # По умолчанию включено
        self.chk_conv_full.pack(anchor="w", padx=30, pady=(5, 20))
        # ------------------------------

        ctk.CTkButton(t, text=self.t('btn_add_full'), height=50, command=self.add_full_task).pack(fill="x", padx=50)

    def ui_frag_tab(self):
        t = self.tab_frag
        t.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(t, text=self.t('lbl_url'), font=("Roboto", 14, "bold")).pack(anchor="w", pady=(10, 5), padx=30)
        self.entry_url_frag = ctk.CTkEntry(t, height=40)
        self.entry_url_frag.pack(fill="x", padx=30, pady=(0, 20))
        
        tf = ctk.CTkFrame(t, fg_color="transparent")
        tf.pack(fill="x", padx=30, pady=10)
        self.s_h, self.s_m, self.s_s = self.create_time(tf, "Start", 0)
        ctk.CTkLabel(tf, text="➔", font=("Arial", 20)).grid(row=1, column=1, padx=20)
        self.e_h, self.e_m, self.e_s = self.create_time(tf, "End", 2)
        
        ctk.CTkLabel(t, text=self.t('lbl_quality')).pack(anchor="w", padx=30, pady=(10, 0))
        vals = [self.t(k) for k in ['q_best', 'q_1080', 'q_720', 'q_audio']]
        self.combo_q_frag = ctk.CTkOptionMenu(t, values=vals, width=250)
        self.combo_q_frag.pack(anchor="w", padx=30, pady=(5, 5))
        
        # --- НОВАЯ ГАЛОЧКА (ФРАГМЕНТЫ) ---
        self.chk_conv_frag = ctk.CTkCheckBox(t, text=self.t('chk_convert'))
        self.chk_conv_frag.select()
        self.chk_conv_frag.pack(anchor="w", padx=30, pady=(5, 10))
        # ---------------------------------
        
        ctk.CTkButton(t, text=self.t('btn_add_frag'), height=50, fg_color="#1f6aa5", command=self.add_frag_task).pack(fill="x", padx=50, pady=20)

    def create_time(self, p, title, c):
        f = ctk.CTkFrame(p); f.grid(row=1, column=c)
        ctk.CTkLabel(p, text=title).grid(row=0, column=c, pady=5)
        h = ctk.CTkEntry(f, width=40, justify="center"); h.insert(0,"00"); h.pack(side="left", padx=1)
        ctk.CTkLabel(f, text=":").pack(side="left")
        m = ctk.CTkEntry(f, width=40, justify="center"); m.insert(0,"00"); m.pack(side="left", padx=1)
        ctk.CTkLabel(f, text=":").pack(side="left")
        s = ctk.CTkEntry(f, width=40, justify="center"); s.insert(0,"00"); s.pack(side="left", padx=1)
        return h, m, s

    def ui_queue_tab(self):
        t = self.tab_queue
        self.scroll_frame = ctk.CTkScrollableFrame(t)
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        ctrl = ctk.CTkFrame(t, fg_color="transparent")
        ctrl.pack(fill="x", padx=10, pady=5)
        
        # Кнопка очистки теперь выполняет HARD RESET
        self.btn_clear = ctk.CTkButton(ctrl, text=self.t('btn_clear'), fg_color="#C0392B", hover_color="#A93226", command=self.hard_reset)
        self.btn_clear.pack(side="left", fill="x", expand=True, padx=5)
        
        self.btn_stop = ctk.CTkButton(ctrl, text=self.t('btn_stop'), fg_color="#D4AC0D", hover_color="#B7950B", command=self.stop_download_only)
        self.btn_stop.pack(side="right", fill="x", expand=True, padx=5)
        
        self.btn_start = ctk.CTkButton(t, text=self.t('btn_start'), height=50, fg_color="green", command=self.start_download_thread)
        self.btn_start.pack(fill="x", padx=10, pady=10)

    def ui_settings_tab(self):
        t = self.tab_sett
        ctk.CTkLabel(t, text=self.t('tab_sett'), font=("Arial", 20)).pack(pady=30)
        ctk.CTkButton(t, text=self.t('sett_update'), fg_color="#E07A5F", hover_color="#D16040", command=self.update_ytdlp).pack(pady=20)
        
        ctk.CTkLabel(t, text=self.t('sett_cookies')).pack(pady=(10, 5))
        self.cookies_val = ctk.StringVar(value="Disabled")
        browsers = ["Disabled", "Chrome", "Edge", "Firefox", "Opera", "Yandex"]
        self.combo_cookies = ctk.CTkOptionMenu(t, values=browsers, variable=self.cookies_val)
        self.combo_cookies.pack(pady=5)
        
        self.chk_logs = ctk.CTkCheckBox(t, text=self.t('sett_logs'))
        if self.logging_enabled: self.chk_logs.select()
        self.chk_logs.pack(pady=10)
        ctk.CTkLabel(t, text=self.t('sett_lang')).pack(pady=(20, 5))
        self.lang_combo = ctk.CTkOptionMenu(t, values=["Русский", "English"], command=self.change_lang_req)
        self.lang_combo.set("Русский" if self.lang == 'ru' else "English")
        self.lang_combo.pack(pady=5)
        ctk.CTkLabel(t, text=self.t('version'), text_color="gray").pack(side="bottom", pady=20)

    def ui_footer(self):
        f = ctk.CTkFrame(self, height=50, fg_color="#222")
        f.grid(row=1, column=0, sticky="ew", padx=20, pady=20)
        ctk.CTkLabel(f, text=self.t('lbl_path'), text_color="gray").pack(side="left", padx=(15, 5))
        ctk.CTkEntry(f, textvariable=self.download_path_var, width=200, state="readonly").pack(side="left", padx=5)
        ctk.CTkButton(f, text=self.t('btn_change'), width=80, command=self.change_path, fg_color="#444").pack(side="left", padx=5)
        ctk.CTkButton(f, text=self.t('btn_open'), width=80, command=self.open_path).pack(side="left", padx=5)
        self.lbl_status = ctk.CTkLabel(f, text=self.t('status_ready'), text_color="#aaa")
        self.lbl_status.pack(side="right", padx=20)

    def update_ytdlp(self):
        self.lbl_status.configure(text="Updating...")
        messagebox.showinfo("Update", self.t('msg_upd_start'))
        def run_upd():
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])
                messagebox.showinfo("Success", self.t('msg_upd_ok'))
            except Exception as e:
                messagebox.showerror("Error", f"Update failed: {e}")
            self.lbl_status.configure(text=self.t('status_ready'))
        threading.Thread(target=run_upd, daemon=True).start()

    def change_lang_req(self, v): messagebox.showinfo("Info", "Restart app to apply language.")
    def get_q_string(self, display_val):
        try:
            keys = ['q_best', 'q_1080', 'q_720', 'q_audio']
            vals = [self.t(k) for k in keys]
            return QUALITY_MAP[keys[vals.index(display_val)]]
        except: return QUALITY_MAP['q_best']
    def is_audio(self, val): return val == self.t('q_audio')

    def add_full_task(self):
        url = self.entry_url_full.get()
        if not url: return
        val = self.combo_q_full.get()
        # Передаем состояние галочки конвертации
        self.add_card(url, None, None, self.get_q_string(val), self.is_audio(val), val, self.chk_conv_full.get())
        self.tabview.set(self.t('tab_queue'))

    def add_frag_task(self):
        url = self.entry_url_frag.get()
        if not url: return
        try:
            s = int(self.s_h.get())*3600 + int(self.s_m.get())*60 + int(self.s_s.get())
            e = int(self.e_h.get())*3600 + int(self.e_m.get())*60 + int(self.e_s.get())
            if e <= s: raise ValueError
        except: return messagebox.showerror("!", self.t('err_time'))
        val = self.combo_q_frag.get()
        # Передаем состояние галочки конвертации
        self.add_card(url, s, e, self.get_q_string(val), self.is_audio(val), val, self.chk_conv_frag.get())
        self.tabview.set(self.t('tab_queue'))

    def add_card(self, url, s, e, fmt, is_audio, q_lbl, do_convert):
        tid = len(self.download_queue)
        c = ctk.CTkFrame(self.scroll_frame, fg_color="#2b2b2b")
        c.pack(fill="x", pady=5)
        
        info = ctk.CTkFrame(c, fg_color="transparent")
        info.pack(fill="x", padx=10, pady=5)
        t_lbl = ctk.CTkLabel(info, text="...", font=("Roboto",12,"bold"), anchor="w")
        t_lbl.pack(side="left", fill="x", expand=True)
        
        desc = "FULL" if s is None else f"{str(datetime.timedelta(seconds=s))}-{str(datetime.timedelta(seconds=e))}"
        icon = "🎵" if is_audio else "🎬"
        ctk.CTkLabel(info, text=f"{icon} {desc} | {q_lbl}", text_color="gray").pack(side="right")
        
        p = ctk.CTkProgressBar(c, height=10); p.set(0); p.pack(fill="x", padx=10, pady=5)
        st = ctk.CTkLabel(c, text=self.t('status_ready'), font=("Arial",10), anchor="w")
        st.pack(fill="x", padx=10, pady=(0,5))
        
        err_btn = ctk.CTkButton(c, text="Показать ошибку", fg_color="red", height=20, command=lambda: self.show_error(tid))
        
        self.task_widgets[tid] = {'t': t_lbl, 'p': p, 's': st, 'err_btn': err_btn, 'card': c}
        # Сохраняем 'conv': do_convert
        self.download_queue.append({'id': tid, 'url': url, 's': s, 'e': e, 'fmt': fmt, 'is_audio': is_audio, 'conv': do_convert, 'done': False, 'error': None})
        threading.Thread(target=self.fetch_title, args=(tid, url)).start()

    def fetch_title(self, tid, url):
        try:
            with yt_dlp.YoutubeDL({'quiet':True}) as ydl:
                r = ydl.extract_info(url, download=False)
                self.task_widgets[tid]['t'].configure(text=r.get('title','Unknown'))
        except: pass

    def show_error(self, tid):
        err = self.download_queue[tid].get('error', 'Unknown error')
        messagebox.showerror("Error Details", f"{err}")

    def stop_download_only(self):
        """Пауза - останавливает скачивание, но не очищает список"""
        if self.is_running:
            self.abort_flag = True
            self.lbl_status.configure(text="Stopping...", text_color="yellow")

    def hard_reset(self): # ПЕРЕИМЕНОВАЛ stop_and_clear_all
        """ПОЛНЫЙ СБРОС (Hard Reset)"""
        self.abort_flag = True 
        def cleaner():
            time.sleep(0.5) # Даем время хукам выбросить Exception
            self.download_queue = []
            for w in self.scroll_frame.winfo_children(): w.destroy()
            self.task_widgets = {}
            self.lbl_status.configure(text=self.t('status_ready'), text_color="#aaa")
            # Сбрасываем флаги
            self.is_running = False
            self.abort_flag = False
            self.btn_start.configure(state="normal")
        threading.Thread(target=cleaner).start()

    def change_path(self):
        d = filedialog.askdirectory()
        if d: self.download_path_var.set(d)
    def open_path(self):
        p = self.download_path_var.get()
        if os.path.exists(p): os.startfile(p)
    def check_tools(self):
        if not os.path.exists(self.ffmpeg_exe) or not os.path.exists(self.ffprobe_exe):
            messagebox.showwarning("Warning", "ffmpeg/ffprobe missing!")
    def start_download_thread(self):
        if self.is_running: return 
        self.is_running = True
        self.abort_flag = False
        self.btn_start.configure(state="disabled")
        threading.Thread(target=self.worker, daemon=True).start()

    def worker(self):
        save_path = self.download_path_var.get()
        cookie_browser = self.cookies_val.get()
        
        for task in self.download_queue:
            if self.abort_flag: break
            if task['done']: continue
            
            tid = task['id']
            w = self.task_widgets.get(tid)
            if not w: continue
            
            w['s'].configure(text=self.t('status_work'), text_color="yellow")
            w['err_btn'].pack_forget()

            opts = {
                'ffmpeg_location': self.ffmpeg_dir,
                'quiet': True, 'no_warnings': True, 'noprogress': True,
                'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                'restrictfilenames': True,
                'retries': 10, 'fragment_retries': 10,
                'socket_timeout': 30,
            }

            if cookie_browser != "Disabled":
                opts['cookiesfrombrowser'] = (cookie_browser.lower(), )

            if task['s'] is not None:
                opts['download_ranges'] = yt_dlp.utils.download_range_func(None, [(task['s'], task['e'])])
                opts['force_keyframes_at_cuts'] = True
                opts['outtmpl'] = os.path.join(save_path, f'%(title)s_cut_{task["s"]}-{task["e"]}.%(ext)s')

            if task['is_audio']:
                opts['format'] = 'bestaudio/best'
                opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]
            else:
                opts['format'] = task['fmt']
                # ЛОГИКА КОНВЕРТАЦИИ: Только если это видео И стоит галочка
                if task['conv']:
                    opts['merge_output_format'] = 'mp4'
                    # ВАЖНО: Принудительное перекодирование звука в AAC, чтобы был звук в MP4
                    opts['postprocessor_args'] = {'ffmpeg': ['-c:v', 'copy', '-c:a', 'aac']}

            def hook(d):
                if self.abort_flag: raise Exception("ABORTED_BY_USER")
                if d['status'] == 'downloading':
                    now = time.time()
                    if now - self.last_ui_update > 0.1: 
                        try:
                            p = float(d.get('_percent_str','0%').strip('%'))/100
                            w['p'].set(p)
                            w['s'].configure(text=f"{d.get('_percent_str')} | {d.get('_speed_str')}")
                            self.last_ui_update = now
                        except: pass
                elif d['status'] == 'finished':
                     w['s'].configure(text=self.t('status_merge'), text_color="cyan")

            opts['progress_hooks'] = [hook]

            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([task['url']])
                task['done'] = True
                w['s'].configure(text="✔ OK", text_color="green")
                w['p'].set(1)
            except Exception as e:
                if "ABORTED_BY_USER" in str(e):
                    w['s'].configure(text=self.t('status_paused'), text_color="orange")
                    break
                else:
                    err_msg = str(e)
                    if "cookie" in err_msg.lower() or "locked" in err_msg.lower():
                        err_msg += "\n\n💡 ПОДСКАЗКА: Закройте браузер перед скачиванием!"
                    
                    task['error'] = err_msg
                    w['s'].configure(text="❌ Error", text_color="red")
                    w['err_btn'].pack(side="right", padx=5)
                    logging.error(f"Error tid {tid}: {e}")

        # СБРОС ФЛАГОВ ПОСЛЕ ЗАВЕРШЕНИЯ
        self.is_running = False
        self.btn_start.configure(state="normal")
        
        if self.abort_flag:
            self.lbl_status.configure(text=self.t('status_aborted'), text_color="orange")
            self.abort_flag = False # Сбрасываем флаг, чтобы кнопка Старт работала снова
        else:
            messagebox.showinfo("Info", self.t('msg_done'))
            self.lbl_status.configure(text=self.t('status_ready'))

if __name__ == "__main__":
    app = ModernYouTubeCutter()
    app.mainloop()
