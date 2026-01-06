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
        'lbl_bitrate': 'Битрейт аудио:',
        'lbl_video_settings': 'Настройки видео:',
        'bitrate_auto': 'Авто (рекомендуется)',
        'bitrate_320': '320 kbps (высокое)',
        'bitrate_192': '192 kbps (среднее)',
        'bitrate_128': '128 kbps (быстрое)',
        'video_settings_auto': 'Авто (рекомендуется)',
        'video_settings_fast': 'Быстрая обработка',
        'video_settings_quality': 'Качественная обработка',
        'chk_convert': 'Конвертировать в MP4 (Fix звука)',
        'btn_add_full': 'ДОБАВИТЬ В ОЧЕРЕДЬ (ПОЛНОЕ)',
        'btn_add_frag': 'ДОБАВИТЬ ФРАГМЕНТ',
        'btn_start': '▶ ЗАПУСТИТЬ',
        'btn_stop': '⏸ ПАУЗА / СТОП',
        'btn_clear': '🗑 ЖЕСТКИЙ СБРОС И ОЧИСТКА',
        'lbl_path': 'Папка сохранения:',
        'btn_change': 'Изменить...',
        'btn_open': '📂 Открыть',
        'status_ready': 'В ожидании',
        'status_work': 'Скачивание...',
        'status_paused': '⏸ Остановлено',
        'status_aborted': '⏹ Сброшено',
        'status_merge': 'Сборка MP4 (AAC)...',
        'sett_logs': 'Вести лог-файл',
        'sett_noproxy': 'Отключить прокси (исправить ошибку подключения)',
        'sett_js_runtime': 'JavaScript Runtime (для YouTube):',
        'sett_js_auto': 'Авто (определить автоматически)',
        'sett_js_not_found': '⚠️ JavaScript runtime не найден. Установите deno или nodejs',
        'sett_lang': 'Язык (Требует перезапуска):',
        'sett_update': '🛠 Обновить ядро',
        'sett_cookies': '🍪 Браузер для Cookies (при ошибке 403):',
        'version': 'Версия: 1.4 (Fragment Fix)',
        'err_url': 'Ошибка: Нет ссылки!',
        'err_time': 'Ошибка: Конец < Начала',
        'msg_done': 'Все задачи выполнены!',
        'msg_upd_start': 'Обновление запущено... Ждите.',
        'msg_upd_ok': 'Готово! Перезапустите программу.',
        'q_best': 'Лучшее (Авто)',
        'q_1080': '1080p (Full HD)',
        'q_720': '720p (HD)',
        'q_audio': 'Только звук (MP3)',
        'btn_exit': '🚪 Выход',
        'btn_restart': '🔄 Перезапуск',
        'btn_diagnostics': '🔍 Диагностика',
        'msg_exit_confirm': 'Идет скачивание. Вы уверены, что хотите выйти?',
        'msg_restart_confirm': 'Идет скачивание. Вы уверены, что хотите перезапустить?',
        'diag_title': 'Диагностика системы',
        'diag_ffmpeg': 'FFmpeg:',
        'diag_ffprobe': 'FFprobe:',
        'diag_deno': 'Deno (JavaScript Runtime):',
        'diag_ytdlp': 'yt-dlp:',
        'diag_path': 'Путь программы:',
        'diag_downloads': 'Папка загрузок:',
        'diag_env_path': 'PATH окружения:',
        'diag_found': '✅ Найден',
        'diag_not_found': '❌ Не найден',
        'diag_working': '✅ Работает',
        'diag_not_working': '❌ Не работает',
        'diag_version': 'Версия:',
        'diag_close': 'Закрыть'
    },
    'en': {
        'tab_full': 'Full Video',
        'tab_frag': 'Fragments',
        'tab_queue': 'Downloads',
        'tab_sett': '⚙ Settings',
        'lbl_url': 'Video URL:',
        'lbl_quality': 'Quality:',
        'lbl_bitrate': 'Audio Bitrate:',
        'lbl_video_settings': 'Video Settings:',
        'bitrate_auto': 'Auto (recommended)',
        'bitrate_320': '320 kbps (high)',
        'bitrate_192': '192 kbps (medium)',
        'bitrate_128': '128 kbps (fast)',
        'video_settings_auto': 'Auto (recommended)',
        'video_settings_fast': 'Fast processing',
        'video_settings_quality': 'Quality processing',
        'chk_convert': 'Convert to MP4 (Audio Fix)',
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
        'sett_noproxy': 'Disable Proxy (fix connection error)',
        'sett_js_runtime': 'JavaScript Runtime (for YouTube):',
        'sett_js_auto': 'Auto (detect automatically)',
        'sett_js_not_found': '⚠️ JavaScript runtime not found. Install deno or nodejs',
        'sett_lang': 'Language (Restart required):',
        'sett_update': '🛠 Update Core',
        'sett_cookies': '🍪 Cookie Source (Fix 403):',
        'version': 'Version: 1.4 (Fragment Fix)',
        'err_url': 'Error: No URL!',
        'err_time': 'Error: End < Start',
        'msg_done': 'All Done!',
        'msg_upd_start': 'Update started... Please wait.',
        'msg_upd_ok': 'Done! Please restart app.',
        'q_best': 'Best (Auto)',
        'q_1080': '1080p (Full HD)',
        'q_720': '720p (HD)',
        'q_audio': 'Audio Only (MP3)',
        'btn_exit': '🚪 Exit',
        'btn_restart': '🔄 Restart',
        'btn_diagnostics': '🔍 Diagnostics',
        'msg_exit_confirm': 'Download in progress. Are you sure you want to exit?',
        'msg_restart_confirm': 'Download in progress. Are you sure you want to restart?',
        'diag_title': 'System Diagnostics',
        'diag_ffmpeg': 'FFmpeg:',
        'diag_ffprobe': 'FFprobe:',
        'diag_deno': 'Deno (JavaScript Runtime):',
        'diag_ytdlp': 'yt-dlp:',
        'diag_path': 'Program Path:',
        'diag_downloads': 'Downloads Folder:',
        'diag_env_path': 'Environment PATH:',
        'diag_found': '✅ Found',
        'diag_not_found': '❌ Not Found',
        'diag_working': '✅ Working',
        'diag_not_working': '❌ Not Working',
        'diag_version': 'Version:',
        'diag_close': 'Close'
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
        self.disable_proxy = False 
        self.js_runtime = 'auto' 
        self.audio_bitrate = 'auto' 
        self.video_settings = 'auto'
        self.setup_logging()

        self.title("YT-DLP Ultimate v1.4")
        self.geometry("950x800")
        self.minsize(600, 500)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.base_path = self.get_base_path()
        self.ffmpeg_dir = self.base_path 
        self.ffmpeg_exe = os.path.join(self.base_path, 'ffmpeg.exe')
        self.ffprobe_exe = os.path.join(self.base_path, 'ffprobe.exe')
        self.deno_exe = os.path.join(self.base_path, 'deno.exe')
        
        env_path = os.environ.get('PATH', '')
        if self.base_path not in env_path:
            os.environ['PATH'] = self.base_path + os.pathsep + env_path

        default_dl = os.path.join(self.base_path, 'downloads')
        if not os.path.exists(default_dl): os.makedirs(default_dl)
        self.download_path_var = ctk.StringVar(value=default_dl)

        self.download_queue = [] 
        self.task_widgets = {} 
        self.last_ui_update = 0
        self.abort_flag = False 
        self.is_running = False
        self.js_runtime_paths = {}

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
        
        # Битрейт аудио
        ctk.CTkLabel(t, text=self.t('lbl_bitrate')).pack(anchor="w", padx=30, pady=(10, 0))
        bitrate_vals = [self.t('bitrate_auto'), self.t('bitrate_320'), self.t('bitrate_192'), self.t('bitrate_128')]
        self.combo_bitrate_full = ctk.CTkOptionMenu(t, values=bitrate_vals, width=250)
        self.combo_bitrate_full.set(self.t('bitrate_auto'))
        self.combo_bitrate_full.pack(anchor="w", padx=30, pady=(5, 5))
        
        # Настройки видео
        ctk.CTkLabel(t, text=self.t('lbl_video_settings')).pack(anchor="w", padx=30, pady=(10, 0))
        video_vals = [self.t('video_settings_auto'), self.t('video_settings_fast'), self.t('video_settings_quality')]
        self.combo_video_full = ctk.CTkOptionMenu(t, values=video_vals, width=250)
        self.combo_video_full.set(self.t('video_settings_auto'))
        self.combo_video_full.pack(anchor="w", padx=30, pady=(5, 5))
        
        self.chk_conv_full = ctk.CTkCheckBox(t, text=self.t('chk_convert'))
        self.chk_conv_full.select()
        self.chk_conv_full.pack(anchor="w", padx=30, pady=(5, 20))

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
        
        # Битрейт аудио
        ctk.CTkLabel(t, text=self.t('lbl_bitrate')).pack(anchor="w", padx=30, pady=(10, 0))
        bitrate_vals = [self.t('bitrate_auto'), self.t('bitrate_320'), self.t('bitrate_192'), self.t('bitrate_128')]
        self.combo_bitrate_frag = ctk.CTkOptionMenu(t, values=bitrate_vals, width=250)
        self.combo_bitrate_frag.set(self.t('bitrate_auto'))
        self.combo_bitrate_frag.pack(anchor="w", padx=30, pady=(5, 5))
        
        # Настройки видео
        ctk.CTkLabel(t, text=self.t('lbl_video_settings')).pack(anchor="w", padx=30, pady=(10, 0))
        video_vals = [self.t('video_settings_auto'), self.t('video_settings_fast'), self.t('video_settings_quality')]
        self.combo_video_frag = ctk.CTkOptionMenu(t, values=video_vals, width=250)
        self.combo_video_frag.set(self.t('video_settings_auto'))
        self.combo_video_frag.pack(anchor="w", padx=30, pady=(5, 5))
        
        self.chk_conv_frag = ctk.CTkCheckBox(t, text=self.t('chk_convert'))
        self.chk_conv_frag.select()
        self.chk_conv_frag.pack(anchor="w", padx=30, pady=(5, 10))
        
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
        
        self.chk_noproxy = ctk.CTkCheckBox(t, text=self.t('sett_noproxy'))
        if self.disable_proxy: self.chk_noproxy.select()
        self.chk_noproxy.configure(command=self.update_proxy_setting)
        self.chk_noproxy.pack(pady=10)
        
        ctk.CTkLabel(t, text=self.t('sett_js_runtime')).pack(pady=(10, 5))
        available_runtimes = self.detect_js_runtimes()
        runtime_values = [self.t('sett_js_auto')]
        if available_runtimes:
            runtime_values.extend(available_runtimes)
        else:
            runtime_values.extend(['deno', 'nodejs', 'quickjs']) 
        
        self.js_runtime_val = ctk.StringVar(value=self.js_runtime if self.js_runtime != 'auto' else self.t('sett_js_auto'))
        self.combo_js_runtime = ctk.CTkOptionMenu(t, values=runtime_values, variable=self.js_runtime_val, command=self.update_js_runtime)
        self.combo_js_runtime.pack(pady=5)
        
        if not available_runtimes:
            ctk.CTkLabel(t, text=self.t('sett_js_not_found'), 
                        text_color="orange", font=("Arial", 9)).pack(pady=(5, 10))
        
        ctk.CTkLabel(t, text=self.t('sett_lang')).pack(pady=(20, 5))
        self.lang_combo = ctk.CTkOptionMenu(t, values=["Русский", "English"], command=self.change_lang_req)
        self.lang_combo.set("Русский" if self.lang == 'ru' else "English")
        self.lang_combo.pack(pady=5)
        ctk.CTkLabel(t, text=self.t('version'), text_color="gray").pack(side="bottom", pady=20)

    def ui_footer(self):
        f = ctk.CTkFrame(self, height=50, fg_color="#222")
        f.grid(row=1, column=0, sticky="ew", padx=20, pady=20)
        f.grid_columnconfigure(1, weight=1)
        
        left_frame = ctk.CTkFrame(f, fg_color="transparent")
        left_frame.pack(side="left", padx=(15, 5))
        ctk.CTkLabel(left_frame, text=self.t('lbl_path'), text_color="gray").pack(side="left", padx=(0, 5))
        ctk.CTkEntry(left_frame, textvariable=self.download_path_var, width=200, state="readonly").pack(side="left", padx=5)
        ctk.CTkButton(left_frame, text=self.t('btn_change'), width=80, command=self.change_path, fg_color="#444").pack(side="left", padx=5)
        ctk.CTkButton(left_frame, text=self.t('btn_open'), width=80, command=self.open_path).pack(side="left", padx=5)
        
        self.lbl_status = ctk.CTkLabel(f, text=self.t('status_ready'), text_color="#aaa", font=("Roboto", 11))
        self.lbl_status.pack(side="left", padx=20, expand=True)
        
        right_frame = ctk.CTkFrame(f, fg_color="transparent")
        right_frame.pack(side="right", padx=(5, 15))
        ctk.CTkButton(right_frame, text=self.t('btn_diagnostics'), width=100, command=self.show_diagnostics, fg_color="#3498DB", hover_color="#2980B9").pack(side="left", padx=5)
        ctk.CTkButton(right_frame, text=self.t('btn_restart'), width=100, command=self.restart_app, fg_color="#E07A5F", hover_color="#D16040").pack(side="left", padx=5)
        ctk.CTkButton(right_frame, text=self.t('btn_exit'), width=100, command=self.exit_app, fg_color="#C0392B", hover_color="#A93226").pack(side="left", padx=5)

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
    def update_proxy_setting(self):
        self.disable_proxy = self.chk_noproxy.get()
    def update_js_runtime(self, value):
        if value == self.t('sett_js_auto'):
            self.js_runtime = 'auto'
        else:
            self.js_runtime = value
    def get_q_string(self, display_val):
        try:
            keys = ['q_best', 'q_1080', 'q_720', 'q_audio']
            vals = [self.t(k) for k in keys]
            return QUALITY_MAP[keys[vals.index(display_val)]]
        except: return QUALITY_MAP['q_best']
    def is_audio(self, val): return val == self.t('q_audio')

    def get_bitrate_value(self, display_val):
        if display_val == self.t('bitrate_auto'):
            return 'auto'
        elif display_val == self.t('bitrate_320'):
            return '320'
        elif display_val == self.t('bitrate_192'):
            return '192'
        elif display_val == self.t('bitrate_128'):
            return '128'
        return 'auto'
    
    def get_video_settings_value(self, display_val):
        if display_val == self.t('video_settings_auto'):
            return 'auto'
        elif display_val == self.t('video_settings_fast'):
            return 'fast'
        elif display_val == self.t('video_settings_quality'):
            return 'quality'
        return 'auto'
    
    def add_full_task(self):
        url = self.entry_url_full.get()
        if not url: return
        val = self.combo_q_full.get()
        bitrate = self.get_bitrate_value(self.combo_bitrate_full.get())
        video_settings = self.get_video_settings_value(self.combo_video_full.get())
        self.add_card(url, None, None, self.get_q_string(val), self.is_audio(val), val, 
                     self.chk_conv_full.get(), bitrate, video_settings)
        self.tabview.set(self.t('tab_queue'))

    def add_frag_task(self):
        url = self.entry_url_frag.get()
        if not url: return
        try:
            s = int(self.s_h.get())*3600 + int(self.s_m.get())*60 + int(self.s_s.get())
            e = int(self.e_h.get())*3600 + int(self.e_m.get())*60 + int(self.e_s.get())
            
            # ЛОГИРОВАНИЕ ВРЕМЕНИ (ПРОВЕРКА)
            logging.info(f"Adding fragment task: Start={s}s, End={e}s")
            print(f"DEBUG: Calculated Seconds -> Start: {s}, End: {e}")
            
            if e <= s: raise ValueError
        except: return messagebox.showerror("!", self.t('err_time'))
        val = self.combo_q_frag.get()
        bitrate = self.get_bitrate_value(self.combo_bitrate_frag.get())
        video_settings = self.get_video_settings_value(self.combo_video_frag.get())
        self.add_card(url, s, e, self.get_q_string(val), self.is_audio(val), val, 
                     self.chk_conv_frag.get(), bitrate, video_settings)
        self.tabview.set(self.t('tab_queue'))

    def add_card(self, url, s, e, fmt, is_audio, q_lbl, do_convert, bitrate='auto', video_settings='auto'):
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
        self.download_queue.append({
            'id': tid, 'url': url, 's': s, 'e': e, 'fmt': fmt, 'is_audio': is_audio, 
            'conv': do_convert, 'bitrate': bitrate, 'video_settings': video_settings,
            'done': False, 'error': None
        })
        threading.Thread(target=self.fetch_title, args=(tid, url)).start()

    def fetch_title(self, tid, url):
        try:
            fetch_opts = {
                'quiet': True,
                'remote_components': ['ejs:github'],
                'socket_timeout': 30,
            }
            if self.disable_proxy:
                fetch_opts['noproxy'] = '*'
                fetch_opts['proxy'] = ''
            if self.js_runtime != 'auto':
                fetch_opts['js_runtimes'] = [self.js_runtime]
            
            import signal
            def timeout_handler(signum, frame):
                raise TimeoutError("Timeout getting video info")
            
            result = [None]
            error = [None]
            
            def extract_info():
                try:
                    with yt_dlp.YoutubeDL(fetch_opts) as ydl:
                        result[0] = ydl.extract_info(url, download=False)
                except Exception as e:
                    error[0] = e
            
            thread = threading.Thread(target=extract_info, daemon=True)
            thread.start()
            thread.join(timeout=30)
            
            if thread.is_alive():
                self.task_widgets[tid]['t'].configure(text="⏱ Таймаут получения информации")
                return
            
            if error[0]:
                raise error[0]
            
            if result[0]:
                self.task_widgets[tid]['t'].configure(text=result[0].get('title','Unknown'))
        except Exception as e:
            self.task_widgets[tid]['t'].configure(text=f"❌ Ошибка: {str(e)[:50]}")

    def show_error(self, tid):
        err = self.download_queue[tid].get('error', 'Unknown error')
        messagebox.showerror("Error Details", f"{err}")

    def stop_download_only(self):
        if self.is_running:
            self.abort_flag = True
            self.lbl_status.configure(text="Stopping...", text_color="yellow")

    def hard_reset(self):
        self.abort_flag = True 
        def cleaner():
            time.sleep(0.5)
            self.download_queue = []
            for w in self.scroll_frame.winfo_children(): w.destroy()
            self.task_widgets = {}
            self.lbl_status.configure(text=self.t('status_ready'), text_color="#aaa")
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
    def exit_app(self):
        if self.is_running:
            title = "Выход" if self.lang == 'ru' else "Exit"
            if not messagebox.askyesno(title, self.t('msg_exit_confirm')):
                return
            self.abort_flag = True
        self.quit()
        self.destroy()
    def restart_app(self):
        if self.is_running:
            title = "Перезапуск" if self.lang == 'ru' else "Restart"
            if not messagebox.askyesno(title, self.t('msg_restart_confirm')):
                return
            self.abort_flag = True
        python = sys.executable
        os.execl(python, python, *sys.argv)
    
    def check_tool_version(self, tool_path, version_arg='--version'):
        try:
            if not os.path.exists(tool_path):
                return None, "Файл не найден"
            
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            result = subprocess.run(
                [tool_path, version_arg], 
                capture_output=True, 
                text=True, 
                timeout=15,
                startupinfo=startupinfo,
                encoding='utf-8', errors='replace' 
            )
            
            output = (result.stdout + result.stderr).strip()
            
            if "version" in output.lower():
                lines = output.split('\n')
                for line in lines:
                    if "version" in line.lower():
                        return True, line.strip()[:60] 
                return True, "Версия определена (см. лог)"
            
            if result.returncode == 0:
                return True, output.split('\n')[0] if output else "Версия неизвестна"
            else:
                return False, f"Ошибка выполнения: {output[:100]}"
                
        except subprocess.TimeoutExpired:
            return False, "Таймаут (Антивирус блокирует?)"
        except Exception as e:
            return False, f"Ошибка: {str(e)[:100]}"
    
    def show_diagnostics(self):
        """Показывает окно диагностики системы внутри вкладки"""
        tab_name = self.t('diag_title')
        
        try:
            self.tabview.delete(tab_name)
        except ValueError:
            pass 
            
        self.update_idletasks()
        
        self.tabview.add(tab_name)
        self.tabview.set(tab_name)
        t = self.tabview.tab(tab_name)
        
        scroll_frame = ctk.CTkScrollableFrame(t)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(scroll_frame, text=self.t('diag_title'), font=("Roboto", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        results = []
        
        ffmpeg_exists = os.path.exists(self.ffmpeg_exe)
        if ffmpeg_exists:
            ffmpeg_works, ffmpeg_version = self.check_tool_version(self.ffmpeg_exe)
            results.append((self.t('diag_ffmpeg'), ffmpeg_exists, ffmpeg_works, ffmpeg_version, self.ffmpeg_exe))
        else:
            results.append((self.t('diag_ffmpeg'), False, False, "Не найден", self.ffmpeg_exe))
        
        ffprobe_exists = os.path.exists(self.ffprobe_exe)
        if ffprobe_exists:
            ffprobe_works, ffprobe_version = self.check_tool_version(self.ffprobe_exe)
            results.append((self.t('diag_ffprobe'), ffprobe_exists, ffprobe_works, ffprobe_version, self.ffprobe_exe))
        else:
            results.append((self.t('diag_ffprobe'), False, False, "Не найден", self.ffprobe_exe))
        
        deno_exists = os.path.exists(self.deno_exe)
        if deno_exists:
            deno_works, deno_version = self.check_tool_version(self.deno_exe)
            results.append((self.t('diag_deno'), deno_exists, deno_works, deno_version, self.deno_exe))
        else:
            try:
                result = subprocess.run(['deno', '--version'], capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    deno_version = result.stdout.strip().split('\n')[0]
                    results.append((self.t('diag_deno'), True, True, deno_version, "Системный (в PATH)"))
                else:
                    results.append((self.t('diag_deno'), False, False, "Не найден", "Не найден локально и в системе"))
            except:
                results.append((self.t('diag_deno'), False, False, "Не найден", "Не найден локально и в системе"))
        
        try:
            import yt_dlp
            ytdlp_version = yt_dlp.version.__version__
            results.append((self.t('diag_ytdlp'), True, True, ytdlp_version, "Установлен"))
        except Exception as e:
            results.append((self.t('diag_ytdlp'), False, False, f"Ошибка: {str(e)[:50]}", "Не установлен"))
        
        for name, found, working, version, path in results:
            frame = ctk.CTkFrame(scroll_frame, fg_color="#2b2b2b")
            frame.pack(fill="x", pady=5, padx=10)
            
            name_label = ctk.CTkLabel(frame, text=name, font=("Roboto", 12, "bold"), anchor="w")
            name_label.pack(anchor="w", padx=10, pady=(10, 5))
            
            found_text = self.t('diag_found') if found else self.t('diag_not_found')
            found_color = "#4CAF50" if found else "#E74C3C"
            found_label = ctk.CTkLabel(frame, text=found_text, text_color=found_color, anchor="w")
            found_label.pack(anchor="w", padx=10, pady=2)
            
            if found:
                working_text = self.t('diag_working') if working else self.t('diag_not_working')
                working_color = "#4CAF50" if working else "#E74C3C"
                working_label = ctk.CTkLabel(frame, text=working_text, text_color=working_color, anchor="w")
                working_label.pack(anchor="w", padx=10, pady=2)
            
            version_label = ctk.CTkLabel(frame, text=f"{self.t('diag_version')} {version}", text_color="#aaa", anchor="w", font=("Arial", 10))
            version_label.pack(anchor="w", padx=10, pady=2)
            
            path_label = ctk.CTkLabel(frame, text=f"Путь: {path}", text_color="#888", anchor="w", font=("Arial", 9))
            path_label.pack(anchor="w", padx=10, pady=(2, 10))
        
        info_frame = ctk.CTkFrame(scroll_frame, fg_color="#2b2b2b")
        info_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(info_frame, text="Дополнительная информация:", font=("Roboto", 12, "bold"), anchor="w").pack(anchor="w", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(info_frame, text=f"{self.t('diag_path')} {self.base_path}", text_color="#aaa", anchor="w", font=("Arial", 9)).pack(anchor="w", padx=10, pady=2)
        
        downloads_path = self.download_path_var.get()
        ctk.CTkLabel(info_frame, text=f"{self.t('diag_downloads')} {downloads_path}", text_color="#aaa", anchor="w", font=("Arial", 9)).pack(anchor="w", padx=10, pady=2)
        
        env_path = os.environ.get('PATH', '')
        path_preview = env_path[:200] + "..." if len(env_path) > 200 else env_path
        ctk.CTkLabel(info_frame, text=f"{self.t('diag_env_path')} {path_preview}", text_color="#aaa", anchor="w", font=("Arial", 9)).pack(anchor="w", padx=10, pady=2)
        
        python_version = sys.version.split()[0]
        ctk.CTkLabel(info_frame, text=f"Python: {python_version}", text_color="#aaa", anchor="w", font=("Arial", 9)).pack(anchor="w", padx=10, pady=2)
        
        def close_tab():
            try:
                self.tabview.delete(tab_name)
            except: pass
            
        close_btn = ctk.CTkButton(t, text=self.t('diag_close'), command=close_tab, width=150, height=40)
        close_btn.pack(pady=20)

    def check_tools(self):
        if not os.path.exists(self.ffmpeg_exe) or not os.path.exists(self.ffprobe_exe):
            messagebox.showwarning("Warning", "ffmpeg/ffprobe missing!")
    
    def detect_js_runtimes(self):
        available = []
        runtime_paths = {}
        
        if os.path.exists(self.deno_exe):
            try:
                result = subprocess.run([self.deno_exe, '--version'], capture_output=True, timeout=2)
                if result.returncode == 0:
                    available.append('deno')
                    runtime_paths['deno'] = self.deno_exe
            except: pass
        
        if 'deno' not in available:
            try:
                result = subprocess.run(['deno', '--version'], capture_output=True, timeout=2)
                if result.returncode == 0:
                    available.append('deno')
                    runtime_paths['deno'] = 'deno'
            except: pass
        
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, timeout=2)
            if result.returncode == 0:
                available.append('nodejs')
                runtime_paths['nodejs'] = 'node'
        except: pass
        
        try:
            result = subprocess.run(['qjs', '--version'], capture_output=True, timeout=2)
            if result.returncode == 0:
                available.append('quickjs')
                runtime_paths['quickjs'] = 'qjs'
        except: pass
        
        self.js_runtime_paths = runtime_paths
        return available
    def start_download_thread(self):
        if self.is_running: return 
        self.is_running = True
        self.abort_flag = False
        self.btn_start.configure(state="disabled")
        threading.Thread(target=self.worker, daemon=True).start()

    def worker(self):
        save_path = self.download_path_var.get()
        cookie_browser = self.cookies_val.get()
        total_tasks = len([t for t in self.download_queue if not t['done']])
        current_task_num = 0
        
        for task in self.download_queue:
            if self.abort_flag: break
            if task['done']: continue
            
            current_task_num += 1
            tid = task['id']
            w = self.task_widgets.get(tid)
            if not w: continue
            
            task_title = w['t'].cget('text')
            if len(task_title) > 40:
                task_title = task_title[:37] + "..."
            self.lbl_status.configure(
                text=f"📥 Задача {current_task_num}/{total_tasks}: {task_title}",
                text_color="#4CAF50"
            )
            
            w['s'].configure(text="⏳ Получение информации...", text_color="yellow")
            w['err_btn'].pack_forget()
            
            self.lbl_status.configure(
                text=f"📥 [{current_task_num}/{total_tasks}] Подготовка к скачиванию...",
                text_color="#FF9800"
            )

            opts = {
                'ffmpeg_location': self.ffmpeg_dir,
                'quiet': True, 'no_warnings': True, 'noprogress': True,
                'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                'restrictfilenames': True,
                'retries': 10, 'fragment_retries': 10,
                'socket_timeout': 60,
                'remote_components': ['ejs:github'],
            }
            
            if self.disable_proxy:
                opts['noproxy'] = '*'
                opts['proxy'] = ''

            if self.js_runtime != 'auto':
                opts['js_runtimes'] = [self.js_runtime]

            if cookie_browser != "Disabled":
                opts['cookiesfrombrowser'] = (cookie_browser.lower(), )

            if task['s'] is not None:
                # ИСПОЛЬЗУЕМ БОЛЕЕ НАДЕЖНЫЙ МЕТОД ОБРЕЗКИ ЧЕРЕЗ СТРОКУ
                # Это позволяет yt-dlp самому решить, как лучше скачать фрагмент
                opts['download_sections'] = [f"*{task['s']}-{task['e']}"]
                opts['force_keyframes_at_cuts'] = True # Более точная обрезка
                opts['outtmpl'] = os.path.join(save_path, f'%(title)s_cut_{task["s"]}-{task["e"]}.%(ext)s')

            if task['is_audio']:
                opts['format'] = 'bestaudio/best'
                opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]
            else:
                opts['format'] = task['fmt']
                if task['conv']:
                    opts['merge_output_format'] = 'mp4'
                    
                    bitrate = task.get('bitrate', 'auto')
                    if bitrate == 'auto':
                        video_settings = task.get('video_settings', 'auto')
                        if video_settings == 'fast':
                            audio_bitrate = '128k'
                        elif video_settings == 'quality':
                            audio_bitrate = '192k'
                        else:
                            audio_bitrate = '128k'
                    else:
                        audio_bitrate = f'{bitrate}k'
                    
                    video_settings = task.get('video_settings', 'auto')
                    ffmpeg_args = [
                        '-c:v', 'copy',
                        '-c:a', 'aac',
                        '-b:a', audio_bitrate,
                        '-movflags', '+faststart',
                        '-threads', '0',
                        '-y'
                    ]
                    
                    if video_settings == 'quality':
                        ffmpeg_args.extend(['-q:a', '2'])
                    
                    opts['postprocessor_args'] = {'ffmpeg': ffmpeg_args}

            download_start_time = time.time()
            last_progress_time = time.time()
            max_idle_time = 300
            
            def hook(d):
                nonlocal last_progress_time
                if self.abort_flag: raise Exception("ABORTED_BY_USER")
                
                current_time = time.time()
                if current_time - last_progress_time > max_idle_time:
                    raise Exception("TIMEOUT: Download stalled for more than 5 minutes")
                
                if d['status'] == 'downloading':
                    last_progress_time = current_time
                    now = time.time()
                    if now - self.last_ui_update > 0.1: 
                        try:
                            # УЛУЧШЕННАЯ ЛОГИКА ПРОГРЕССА ДЛЯ ФРАГМЕНТОВ
                            downloaded = d.get('downloaded_bytes', 0)
                            total = d.get('total_bytes') or d.get('total_bytes_estimate')
                            
                            speed = d.get('_speed_str', 'N/A')
                            
                            if total:
                                # Если общий размер известен
                                percent_val = downloaded / total
                                w['p'].set(percent_val)
                                percent_str = f"{percent_val*100:.1f}%"
                                downloaded_mb = downloaded / (1024 * 1024)
                                total_mb = total / (1024 * 1024)
                                size_info = f"{downloaded_mb:.1f}MB / {total_mb:.1f}MB"
                            else:
                                # Если общий размер НЕИЗВЕСТЕН (часто бывает при фрагментах)
                                # Просто анимируем прогресс и показываем сколько скачано
                                import math
                                # Делаем "пульсирующий" прогресс бар
                                pulse = (math.sin(now * 3) + 1) / 2 
                                w['p'].set(0.1 + pulse * 0.1) # От 10% до 20%
                                
                                percent_str = "..."
                                downloaded_mb = downloaded / (1024 * 1024)
                                size_info = f"{downloaded_mb:.1f}MB"
                            
                            status_text = f"⬇ Скачивание: {percent_str} | {speed} | {size_info}"
                            w['s'].configure(text=status_text, text_color="yellow")
                            
                            task_title = w['t'].cget('text')
                            if len(task_title) > 30:
                                task_title = task_title[:27] + "..."
                            self.lbl_status.configure(
                                text=f"📥 [{current_task_num}/{total_tasks}] {percent_str} | {speed}",
                                text_color="#4CAF50"
                            )
                            self.last_ui_update = now
                        except: pass
                elif d['status'] == 'finished':
                     w['p'].set(0.95)
                     w['s'].configure(text="🔄 Обработка и сборка MP4...", text_color="cyan")
                     self.lbl_status.configure(
                         text=f"🔄 [{current_task_num}/{total_tasks}] Обработка MP4 (это может занять время)...",
                         text_color="#2196F3"
                     )
                     last_progress_time = current_time
                elif d['status'] == 'error':
                     w['s'].configure(text="❌ Ошибка при скачивании", text_color="red")

            opts['progress_hooks'] = [hook]

            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([task['url']])
                task['done'] = True
                w['s'].configure(text="✔ Готово!", text_color="green")
                w['p'].set(1)
                
                self.lbl_status.configure(
                    text=f"✅ [{current_task_num}/{total_tasks}] Завершено",
                    text_color="#4CAF50"
                )
            except Exception as e:
                if "ABORTED_BY_USER" in str(e):
                    w['s'].configure(text=self.t('status_paused'), text_color="orange")
                    break
                elif "TIMEOUT" in str(e):
                    err_msg = "Скачивание зависло (таймаут 5 минут). Попробуйте еще раз или проверьте соединение."
                    task['error'] = err_msg
                    w['s'].configure(text="⏱ Таймаут", text_color="red")
                    w['err_btn'].pack(side="right", padx=5)
                    logging.error(f"Timeout tid {tid}: {e}")
                else:
                    err_msg = str(e)
                    if "cookie" in err_msg.lower() or "locked" in err_msg.lower():
                        err_msg += "\n\n💡 ПОДСКАЗКА: Закройте браузер перед скачиванием!"
                    if "challenge" in err_msg.lower() or "js" in err_msg.lower():
                        err_msg += "\n\n💡 ПОДСКАЗКА: Убедитесь, что deno.exe доступен и компоненты загружены!"
                    
                    task['error'] = err_msg
                    w['s'].configure(text="❌ Error", text_color="red")
                    w['err_btn'].pack(side="right", padx=5)
                    logging.error(f"Error tid {tid}: {e}")

        self.is_running = False
        self.btn_start.configure(state="normal")
        
        if self.abort_flag:
            self.lbl_status.configure(text="⏹ Остановлено пользователем", text_color="orange")
            self.abort_flag = False
        else:
            completed = len([t for t in self.download_queue if t['done']])
            total = len(self.download_queue)
            self.lbl_status.configure(
                text=f"✅ Все задачи выполнены ({completed}/{total})",
                text_color="#4CAF50"
            )
            messagebox.showinfo("Info", self.t('msg_done'))

if __name__ == "__main__":
    app = ModernYouTubeCutter()
    app.mainloop()
