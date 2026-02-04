import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import os
import threading
import sys  # <--- BARDZO WAŻNE

# Importujemy Twoją logikę z plików pomocniczych
from translator import translate_files
from prompt_profiles import PROFILES, DEFAULT_PROFILE

# --- FUNKCJA DO OBSŁUGI PLIKÓW W .EXE ---
def resource_path(relative_path):
    """ Pobiera ścieżkę do zasobów, działa dla skryptu i dla .exe """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

SETTINGS_FILE = "settings_win.json"

class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kirek SRT Translator GPT - Windows v1.0.1")
        self.root.geometry("620x580") # Zwiększyłem wysokość na większe logo
        self.root.resizable(False, False)

        self.settings = self.load_settings()
        self.setup_ui()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return {"api_key": "", "model": "gpt-4o-mini", "profile": DEFAULT_PROFILE}

    def save_settings(self):
        self.settings["api_key"] = self.api_entry.get().strip()
        self.settings["model"] = self.model_combo.get()
        self.settings["profile"] = self.profile_combo.get()
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=2)

    def toggle_api_visibility(self):
        if self.api_entry.cget('show') == '':
            self.api_entry.config(show='*')
            self.show_btn.config(text="👁 Pokaż")
        else:
            self.api_entry.config(show='')
            self.show_btn.config(text="🙈 Ukryj")

    def show_help(self):
        help_text = (
            "Ten translator powstał dlatego, iż dostępne free (ale i płatne) modele AI "
            "w większości nie przetłumaczą dołączanych plików .SRT w całości, dzielą je na porcje, "
            "kombinują na różne sposoby, albo wręcz twierdzą, że nie tłumaczą napisów lub liczba "
            "znaków jest za duża.\n\n"
            "W translatorze zastosowałem szereg promptów, które maksymalnie usprawniają maszynowe "
            "tłumaczenie z języka angielskiego na polski - język jest w miarę potoczny, model językowy "
            "lepiej tłumaczy idiomy, mniej myli płcie itp. itd. Szybkość tłumaczenia nie oszałamia, "
            "ale chodziło mi o to, aby wysyłane tłumaczone i odbierane było więcej linii z pliku, "
            "aby GPT korzystał z kontekstu dialogów i akcji.\n\n"
            "--------------------------------------------------\n\n"
            "Możemy wybrać GPT do tłumaczenia, ale program prosi o API Key, aby się uwiarygodnić. "
            "Wystarczy tylko 'wykupić' sobie w OpenAI dostęp do API Key za kilka dolarów, "
            "wprowadzić go do programu i mamy możliwość bardzo przyzwoitego przetłumaczenia "
            "co najmniej kilkuset plików z napisami.\n\n"
            "Jak zdobyć API Key?\n"
            "Wejdź na stronę: https://platform.openai.com. Zaloguj się na to samo konto, "
            "którego używasz w ChatGPT (lub załóż, gdy nie masz). Kliknij ikonę profilu (prawy górny róg). "
            "Wybierz View API keys / API keys. Kliknij Create new secret key. Skopiuj klucz od razu, "
            "(zaczyna się zwykle od sk-...) Tego klucza później nie da się podejrzeć, tylko usunąć i "
            "wygenerować nowy. Więc lepiej sobie zachować w pliku.\n\n"
            "--------------------------------------------------\n"
            "Wersja dla Kodi dostępna na GitHub:\n"
            "👉 https://github.com/Kirek66/script.kodi.srt.translator/releases/tag/v1.0.1"
        )
        messagebox.showinfo("Informacja o programie", help_text)

    def setup_ui(self):
        # --- PASEK GÓRNY Z LOGO ---
        top_bar = tk.Frame(self.root)
        top_bar.pack(fill="x", padx=25, pady=(15, 5))

        # WIĘKSZA IKONA (LOGO) WEWNĄTRZ INTERFEJSU
        try:
            from PIL import Image, ImageTk
            icon_img_path = resource_path("icon.ico")
            full_img = Image.open(icon_img_path)
            # Tutaj ustawiamy wielkość logo w oknie (np. 48x48)
            full_img = full_img.resize((48, 48), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(full_img)
            tk.Label(top_bar, image=self.logo_img).pack(side="left", padx=(0, 10))
        except:
            pass # Jeśli nie ma Pillow lub ikony, po prostu nie pokaże obrazka

        tk.Label(top_bar, text="Konfiguracja programu:", font=("Arial", 11, "bold")).pack(side="left", pady=10)
        
        tk.Button(top_bar, text="Informacja o programie", command=self.show_help, 
                  bg="#F0C040", fg="black", font=("Arial", 8, "bold"), 
                  relief="flat", padx=10).pack(side="right")

        # --- API KEY ---
        api_frame = tk.Frame(self.root)
        api_frame.pack(fill="x", padx=25, pady=5)
        tk.Label(api_frame, text="Poniżej wklej swój OpenAI API Key:", font=("Arial", 9)).pack(anchor="w")
        entry_inner_frame = tk.Frame(api_frame)
        entry_inner_frame.pack(fill="x", pady=2)
        self.api_entry = tk.Entry(entry_inner_frame, font=("Consolas", 10), show="*")
        self.api_entry.insert(0, self.settings.get("api_key", ""))
        self.api_entry.pack(side="left", fill="x", expand=True, ipady=3)
        self.show_btn = tk.Button(entry_inner_frame, text="👁 Pokaż", command=self.toggle_api_visibility, font=("Arial", 8), width=8)
        self.show_btn.pack(side="right", padx=(5, 0))

        # --- MODEL & PROFILE ---
        selection_frame = tk.Frame(self.root)
        selection_frame.pack(fill="x", padx=25, pady=15)
        model_sub = tk.Frame(selection_frame)
        model_sub.pack(side="left", fill="x", expand=True)
        tk.Label(model_sub, text="Model AI:").pack(anchor="w")
        self.model_combo = ttk.Combobox(model_sub, values=["gpt-4o-mini", "gpt-4o"], state="readonly")
        self.model_combo.set(self.settings.get("model", "gpt-4o-mini"))
        self.model_combo.pack(anchor="w", pady=2)
        style_sub = tk.Frame(selection_frame)
        style_sub.pack(side="right", fill="x", expand=True)
        tk.Label(style_sub, text="Styl tłumaczenia:").pack(anchor="w")
        self.profile_combo = ttk.Combobox(style_sub, values=list(PROFILES.keys()), state="readonly")
        self.profile_combo.set(self.settings.get("profile", DEFAULT_PROFILE))
        self.profile_combo.pack(anchor="w", pady=2)

        # --- ROZDZIELACZ ---
        tk.Frame(self.root, height=1, bg="#ddd").pack(fill="x", padx=25, pady=10)
        
        # --- WYBÓR FOLDERU ---
        folder_frame = tk.Frame(self.root)
        folder_frame.pack(fill="x", padx=25, pady=10)
        self.folder_path = tk.StringVar(value="Wybierz folder z filmami/napisami...")
        tk.Label(folder_frame, textvariable=self.folder_path, fg="#757575", font=("Arial", 8, "italic")).pack(pady=2)
        tk.Button(folder_frame, text="📁 WYBIERZ FOLDER Z NAPISAMI SRT", command=self.browse_folder, bg="#0277BD", fg="white", height=2, font=("Arial", 10, "bold"), relief="flat").pack(fill="x")

        # --- POSTĘP ---
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(fill="x", padx=25, pady=10)
        self.progress_label = tk.Label(progress_frame, text="Postęp tłumaczenia", font=("Arial", 9))
        self.progress_label.pack()
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=500, mode="determinate")
        self.progress_bar.pack(fill="x", pady=5)

        # --- START ---
        self.start_btn = tk.Button(self.root, text="🚀 ROZPOCZNIJ TŁUMACZENIE", command=self.start_thread, bg="#2E7D32", fg="white", font=("Arial", 12, "bold"), height=2, relief="flat")
        self.start_btn.pack(fill="x", padx=25, pady=20)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def start_thread(self):
        threading.Thread(target=self.run_translation, daemon=True).start()

    def run_translation(self):
        api_key = self.api_entry.get().strip()
        folder = self.folder_path.get()
        if not api_key or "Wybierz folder" in folder:
            messagebox.showwarning("Brak danych", "Podaj klucz API OpenAI oraz wybierz folder!")
            return
        self.save_settings()
        self.start_btn.config(state="disabled", text="⏳ TŁUMACZENIE W TOKU...")
        try:
            files = [f for f in os.listdir(folder) if f.lower().endswith(".srt") and not f.lower().endswith(".pl.srt")]
        except:
            messagebox.showerror("Błąd", "Nie można otworzyć folderu.")
            self.reset_button()
            return
        if not files:
            messagebox.showinfo("Brak plików", "Nie znaleziono nowych napisów do przetłumaczenia.")
            self.reset_button()
            return
        try:
            def update_progress(current, text):
                percent = int((current / len(files)) * 100)
                self.progress_bar["value"] = percent
                self.progress_label.config(text=f"Przetwarzanie: {text}")
                self.root.update_idletasks()
            translate_files(api_key, folder, files, update_progress, self.settings["profile"], self.settings["model"])
            messagebox.showinfo("Gotowe!", f"Przetłumaczono plików: {len(files)}")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))
        self.reset_button()
        self.progress_label.config(text="Postęp tłumaczenia: Zakończono.")

    def reset_button(self):
        self.start_btn.config(state="normal", text="🚀 ROZPOCZNIJ TŁUMACZENIE")

if __name__ == "__main__":
    root = tk.Tk()
    
    # --- POPRAWIONA SEKCJA IKONY SYSTEMOWEJ ---
    icon_final_path = resource_path("icon.ico")
    if os.path.exists(icon_final_path):
        try:
            root.iconbitmap(icon_final_path)
        except:
            pass
    
    app = TranslatorApp(root)
    root.mainloop()