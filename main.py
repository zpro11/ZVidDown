import sys
import os
import threading
import yt_dlp
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class LetoltoTk(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Videó Letöltő')
        self.geometry('400x320')
        self.resizable(False, False)
        self.kimeneti_mappa = ''
        self._felulet()

    def _felulet(self):
        pady = 4
        self.cimke_url = tk.Label(self, text='Videó URL:')
        self.cimke_url.pack(anchor='w', padx=10, pady=(10,0))
        self.mezo_url = tk.Entry(self, width=50)
        self.mezo_url.pack(padx=10, pady=(0,pady))
        self.mezo_url.bind('<KeyRelease>', lambda e: self.felbontasok())

        self.cimke_mod = tk.Label(self, text='Letöltési mód:')
        self.cimke_mod.pack(anchor='w', padx=10)
        self.mod_valaszto = ttk.Combobox(self, values=['Videó + Hang', 'Csak Hang (mp3)', 'Csak Videó'], state='readonly')
        self.mod_valaszto.current(0)
        self.mod_valaszto.pack(padx=10, pady=(0,pady))

        self.cimke_felbontas = tk.Label(self, text='Felbontás:')
        self.cimke_felbontas.pack(anchor='w', padx=10)
        self.felbontas_valaszto = ttk.Combobox(self, values=['Elérhető felbontásokhoz URL kell.'], state='disabled')
        self.felbontas_valaszto.pack(padx=10, pady=(0,pady))

        self.gomb_kimenet = tk.Button(self, text='Kimeneti mappa kiválasztása', command=self.kimenet)
        self.gomb_kimenet.pack(padx=10, pady=(0,pady))

        self.gomb_letoltes = tk.Button(self, text='Letöltés (Előbb válaszd ki a kimeneti mapát)', command=self.letoltes)
        self.gomb_letoltes.pack(padx=10, pady=(0,pady))

        self.cimke_allapot = tk.Label(self, text='')
        self.cimke_allapot.pack(anchor='w', padx=10)
        self.sav = ttk.Progressbar(self, orient='horizontal', length=370, mode='determinate')
        self.sav.pack(padx=10, pady=(0,pady))
        self.cimke_statusz = tk.Label(self, text='')
        self.cimke_statusz.pack(anchor='w', padx=10)

    def felbontasok(self):
        url = self.mezo_url.get().strip()
        if not url:
            self.felbontas_valaszto['values'] = ['Elérhető felbontásokhoz URL-t adj meg!']
            self.felbontas_valaszto.set('Elérhető felbontásokhoz URL-t adj meg!')
            self.felbontas_valaszto.config(state='disabled')
            return
        self.felbontas_valaszto['values'] = ['Felbontások lekérése...']
        self.felbontas_valaszto.set('Felbontások lekérése...')
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
                    self.felbontas_valaszto['values'] = ['Nem található felbontás']
                    self.felbontas_valaszto.set('Nem található felbontás')
                    self.felbontas_valaszto.config(state='disabled')
            except Exception:
                self.felbontas_valaszto['values'] = ['Hibás vagy nem támogatott URL']
                self.felbontas_valaszto.set('Hibás vagy nem támogatott URL')
                self.felbontas_valaszto.config(state='disabled')
        threading.Thread(target=formatok, daemon=True).start()

    def kimenet(self):
        mappa = filedialog.askdirectory(title='Kimeneti mappa kiválasztása')
        if mappa:
            self.kimeneti_mappa = mappa
            self.gomb_letoltes.config(text='Letöltés')

    def letoltes(self):
        url = self.mezo_url.get().strip()
        if not url:
            messagebox.showwarning('Hiba', 'Add meg a YouTube videó URL-jét!')
            return
        if not self.kimeneti_mappa:
            messagebox.showwarning('Hiba', 'Válassz kimeneti mappát!')
            return
        mod = self.mod_valaszto.get()
        felbontas = self.felbontas_valaszto.get() if self.felbontas_valaszto['state'] == 'readonly' else None
        self.sav['value'] = 0
        self.cimke_statusz.config(text='Letöltés indítása...')
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
                self.cimke_statusz.config(text=f'Sebesség: {sebesseg_szoveg} | Hátralévő idő: {ido_szoveg}')
            elif d.get('status') == 'finished':
                self.sav['value'] = 100
                self.cimke_statusz.config(text='Letöltés kész!')
        ffmpeg_path = 'ffmpeg.exe'
        if hasattr(sys, '_MEIPASS'):
            ffmpeg_path = os.path.join(sys._MEIPASS, 'ffmpeg.exe')

        beallitasok = {
            'outtmpl': f'{self.kimeneti_mappa}/%(title)s.%(ext)s',
            'progress_hooks': [horog],
            'ffmpeg_location': ffmpeg_path,
        }
        if mod == 'Videó + Hang':
            if felbontas and felbontas.endswith('p') and felbontas[:-1].isdigit():
                beallitasok['format'] = f'bestvideo[height={felbontas[:-1]}]+bestaudio/best'
            else:
                beallitasok['format'] = 'bestvideo+bestaudio/best'
        elif mod == 'Csak Hang (mp3)':
            beallitasok['format'] = 'bestaudio/best'
            beallitasok['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        elif mod == 'Csak Videó':
            if felbontas and felbontas.endswith('p') and felbontas[:-1].isdigit():
                beallitasok['format'] = f'bestvideo[height={felbontas[:-1]}]'
            else:
                beallitasok['format'] = 'bestvideo'
        try:
            with yt_dlp.YoutubeDL(beallitasok) as ydl:
                ydl.download([url])
            messagebox.showinfo('Sikeres letöltés', 'A letöltés befejeződött!')
        except Exception as e:
            messagebox.showerror('Hiba', f'Hiba történt: {str(e)}')

def main():
    app = LetoltoTk()
    app.mainloop()

if __name__ == '__main__':
    main()

