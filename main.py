import sys
import os
import threading
import yt_dlp
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import platform

class LetoltoTk(tk.Tk):
    def __init__(self):
        super().__init__()
        self.translations = {
            'hu': {
                'title': 'Videó Letöltő',
                'video_url': 'Videó URL:',
                'download_mode': 'Letöltési mód:',
                'video_audio': 'Videó + Hang',
                'audio_only': 'Csak Hang (mp3)',
                'video_only': 'Csak Videó',
                'resolution': 'Felbontás:',
                'select_output': 'Kimeneti mappa kiválasztása',
                'download': 'Letöltés',
                'download_choose_folder': 'Letöltés (Előbb válaszd ki a kimeneti mapát)',
                'status': '',
                'resolutions_need_url': 'Elérhető felbontásokhoz URL-t adj meg!',
                'fetching_resolutions': 'Felbontások lekérése...',
                'no_resolution': 'Nem található felbontás',
                'invalid_url': 'Hibás vagy nem támogatott URL',
                'error': 'Hiba',
                'missing_url': 'Add meg a YouTube videó URL-jét!',
                'missing_folder': 'Válassz kimeneti mappát!',
                'start_download': 'Letöltés indítása...',
                'speed': 'Sebesség',
                'remaining_time': 'Hátralévő idő',
                'download_complete': 'Letöltés kész!',
                'success': 'Sikeres letöltés',
                'download_finished': 'A letöltés befejeződött!',
                'language': 'Nyelv:',
                'english': 'Angol',
                'hungarian': 'Magyar',
                'menu_language': 'Language',
            },
            'en': {
                'title': 'Video Downloader',
                'video_url': 'Video URL:',
                'download_mode': 'Download mode:',
                'video_audio': 'Video + Audio',
                'audio_only': 'Audio Only (mp3)',
                'video_only': 'Video Only',
                'resolution': 'Resolution:',
                'select_output': 'Select output folder',
                'download': 'Download',
                'download_choose_folder': 'Download (Select output folder first)',
                'status': '',
                'resolutions_need_url': 'Enter URL to get available resolutions!',
                'fetching_resolutions': 'Fetching resolutions...',
                'no_resolution': 'No resolution found',
                'invalid_url': 'Invalid or unsupported URL',
                'error': 'Error',
                'missing_url': 'Please enter the YouTube video URL!',
                'missing_folder': 'Please select output folder!',
                'start_download': 'Starting download...',
                'speed': 'Speed',
                'remaining_time': 'Remaining time',
                'download_complete': 'Download complete!',
                'success': 'Download successful',
                'download_finished': 'Download finished!',
                'language': 'Language:',
                'english': 'English',
                'hungarian': 'Hungarian',
                'menu_language': 'Language',
            }
        }
        self._load_more_languages()
        self.language = 'en'
        self.config_path = self._get_config_path()
        self._load_language()
        self.title(self._t('title'))
        self.geometry('400x340')
        self.resizable(False, False)
        self.kimeneti_mappa = ''
        self._create_menu()
        self._felulet()

    def _load_more_languages(self):
        prog_dir = os.path.dirname(sys.argv[0])
        lang_path = os.path.join(prog_dir, 'more_languages.json')
        if os.path.isfile(lang_path):
            try:
                with open(lang_path, 'r', encoding='utf-8') as f:
                    langs = json.load(f)
                    if isinstance(langs, dict):
                        self.translations.update(langs)
            except Exception:
                pass

    def _get_config_path(self):
        if platform.system() == 'Windows':
            appdata = os.getenv('APPDATA')
        else:
            appdata = os.path.expanduser('~/.config')
        config_dir = os.path.join(appdata, 'zviddown')
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, 'settings.json')

    def _save_language(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({'language': self.language}, f)
        except Exception:
            pass

    def _load_language(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'language' in data:
                    self.language = data['language']
        except Exception:
            self.language = 'en'

    def _t(self, key):
        return self.translations[self.language].get(key, key)

    def _create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        more_menu = tk.Menu(menubar, tearoff=0)
        lang_menu = tk.Menu(more_menu, tearoff=0)
        self.lang_var = tk.StringVar(value=self.language)
        for lang_code in self.translations.keys():
            lang_menu.add_radiobutton(label=lang_code, value=lang_code, variable=self.lang_var, command=lambda c=lang_code: self._set_language(c))
        more_menu.add_cascade(label=self._t('menu_language'), menu=lang_menu)
        menubar.add_cascade(label='⋮', menu=more_menu)

    def _set_language(self, lang):
        self.language = lang
        self._save_language()
        self._refresh_ui()

    def _felulet(self):
        pady = 4
        self.cimke_url = tk.Label(self, text=self._t('video_url'))
        self.cimke_url.pack(anchor='w', padx=10, pady=(10,0))
        self.mezo_url = tk.Entry(self, width=50)
        self.mezo_url.pack(padx=10, pady=(0,pady))
        self.mezo_url.bind('<KeyRelease>', lambda e: self.felbontasok())

        self.cimke_mod = tk.Label(self, text=self._t('download_mode'))
        self.cimke_mod.pack(anchor='w', padx=10)
        self.mod_valaszto = ttk.Combobox(self, values=[self._t('video_audio'), self._t('audio_only'), self._t('video_only')], state='readonly')
        self.mod_valaszto.current(0)
        self.mod_valaszto.pack(padx=10, pady=(0,pady))

        self.cimke_felbontas = tk.Label(self, text=self._t('resolution'))
        self.cimke_felbontas.pack(anchor='w', padx=10)
        self.felbontas_valaszto = ttk.Combobox(self, values=[self._t('resolutions_need_url')], state='disabled')
        self.felbontas_valaszto.pack(padx=10, pady=(0,pady))

        self.gomb_kimenet = tk.Button(self, text=self._t('select_output'), command=self.kimenet)
        self.gomb_kimenet.pack(padx=10, pady=(0,pady))

        self.gomb_letoltes = tk.Button(self, text=self._t('download_choose_folder'), command=self.letoltes)
        self.gomb_letoltes.pack(padx=10, pady=(0,pady))

        self.cimke_allapot = tk.Label(self, text='')
        self.cimke_allapot.pack(anchor='w', padx=10)
        self.sav = ttk.Progressbar(self, orient='horizontal', length=370, mode='determinate')
        self.sav.pack(padx=10, pady=(0,pady))
        self.cimke_statusz = tk.Label(self, text='')
        self.cimke_statusz.pack(anchor='w', padx=10)

    def _refresh_ui(self):
        self.title(self._t('title'))
        self.cimke_url.config(text=self._t('video_url'))
        self.cimke_mod.config(text=self._t('download_mode'))
        current_mode = self.mod_valaszto.get()
        modes = [self._t('video_audio'), self._t('audio_only'), self._t('video_only')]
        self.mod_valaszto['values'] = modes
        if current_mode not in modes:
            self.mod_valaszto.set(modes[0])
        else:
            self.mod_valaszto.set(current_mode)
        self.cimke_felbontas.config(text=self._t('resolution'))
        if not self.mezo_url.get().strip():
            self.felbontas_valaszto['values'] = [self._t('resolutions_need_url')]
            self.felbontas_valaszto.set(self._t('resolutions_need_url'))
            self.felbontas_valaszto.config(state='disabled')
        self.gomb_kimenet.config(text=self._t('select_output'))
        if not self.kimeneti_mappa:
            self.gomb_letoltes.config(text=self._t('download_choose_folder'))
        else:
            self.gomb_letoltes.config(text=self._t('download'))

    def felbontasok(self):
        url = self.mezo_url.get().strip()
        if not url:
            self.felbontas_valaszto['values'] = [self._t('resolutions_need_url')]
            self.felbontas_valaszto.set(self._t('resolutions_need_url'))
            self.felbontas_valaszto.config(state='disabled')
            return
        self.felbontas_valaszto['values'] = [self._t('fetching_resolutions')]
        self.felbontas_valaszto.set(self._t('fetching_resolutions'))
        self.felbontas_valaszto.config(state='disabled')
        def formatok():
            try:
                ffmpeg_path = 'ffmpeg.exe'
                if hasattr(sys, '_MEIPASS'):
                    ffmpeg_path = os.path.join(sys._MEIPASS, 'ffmpeg.exe')
                ydl_opts = {'quiet': True, 'skip_download': True, 'ffmpeg_location': ffmpeg_path}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                formatok_lista = info.get('formats', [])
                felbontasok = []
                for f in formatok_lista:
                    if f.get('vcodec') != 'none':
                        res = f.get('format_note') or (str(f.get('height')) + 'p' if f.get('height') else None)
                        if res and res not in felbontasok:
                            felbontasok.append(res)
                if felbontasok:
                    self.felbontas_valaszto['values'] = felbontasok
                    self.felbontas_valaszto.set(felbontasok[0])
                    self.felbontas_valaszto.config(state='readonly')
                else:
                    self.felbontas_valaszto['values'] = [self._t('no_resolution')]
                    self.felbontas_valaszto.set(self._t('no_resolution'))
                    self.felbontas_valaszto.config(state='disabled')
            except Exception:
                self.felbontas_valaszto['values'] = [self._t('invalid_url')]
                self.felbontas_valaszto.set(self._t('invalid_url'))
                self.felbontas_valaszto.config(state='disabled')
        threading.Thread(target=formatok, daemon=True).start()

    def kimenet(self):
        mappa = filedialog.askdirectory(title=self._t('select_output'))
        if mappa:
            self.kimeneti_mappa = mappa
            self.gomb_letoltes.config(text=self._t('download'))

    def letoltes(self):
        url = self.mezo_url.get().strip()
        if not url:
            messagebox.showwarning(self._t('error'), self._t('missing_url'))
            return
        if not self.kimeneti_mappa:
            messagebox.showwarning(self._t('error'), self._t('missing_folder'))
            return
        mod = self.mod_valaszto.get()
        felbontas = self.felbontas_valaszto.get() if self.felbontas_valaszto['state'] == 'readonly' else None
        self.sav['value'] = 0
        self.cimke_statusz.config(text=self._t('start_download'))
        threading.Thread(target=self.folyamat, args=(url, mod, felbontas), daemon=True).start()

    def folyamat(self, url, mod, felbontas):
        def horog(d):
            if d.get('status') == 'downloading':
                szazalek = d.get('_percent_str', '0.0%').replace('%','').strip()
                try:
                    szazalek_ertek = float(szazalek)
                except:
                    szazalek_ertek = 0
                self.sav['value'] = int(szazalek_ertek)
                sebesseg = d.get('speed')
                ido = d.get('eta')
                sebesseg_szoveg = f'{sebesseg/1024:.2f} KB/s' if sebesseg else ''
                ido_szoveg = f'{ido} s' if ido else ''
                self.cimke_statusz.config(text=f"{self._t('speed')}: {sebesseg_szoveg} | {self._t('remaining_time')}: {ido_szoveg}")
            elif d.get('status') == 'finished':
                self.sav['value'] = 100
                self.cimke_statusz.config(text=self._t('download_complete'))
        ffmpeg_path = 'ffmpeg.exe'
        if hasattr(sys, '_MEIPASS'):
            ffmpeg_path = os.path.join(sys._MEIPASS, 'ffmpeg.exe')

        beallitasok = {
            'outtmpl': f'{self.kimeneti_mappa}/%(title)s.%(ext)s',
            'progress_hooks': [horog],
            'ffmpeg_location': ffmpeg_path,
        }
        video_audio = self._t('video_audio')
        audio_only = self._t('audio_only')
        video_only = self._t('video_only')
        if mod == video_audio:
            if felbontas and felbontas.endswith('p') and felbontas[:-1].isdigit():
                beallitasok['format'] = f'bestvideo[height={felbontas[:-1]}]+bestaudio/best'
            else:
                beallitasok['format'] = 'bestvideo+bestaudio/best'
        elif mod == audio_only:
            beallitasok['format'] = 'bestaudio/best'
            beallitasok['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        elif mod == video_only:
            if felbontas and felbontas.endswith('p') and felbontas[:-1].isdigit():
                beallitasok['format'] = f'bestvideo[height={felbontas[:-1]}]'
            else:
                beallitasok['format'] = 'bestvideo'
        try:
            with yt_dlp.YoutubeDL(beallitasok) as ydl:
                ydl.download([url])
            messagebox.showinfo(self._t('success'), self._t('download_finished'))
        except Exception as e:
            messagebox.showerror(self._t('error'), f"{self._t('error')}: {str(e)}")

def main():
    app = LetoltoTk()
    app.mainloop()

if __name__ == '__main__':
    main()

