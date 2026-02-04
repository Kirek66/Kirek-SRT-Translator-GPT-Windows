import os
import json

from srt_utils import read_srt, write_srt, split_srt_into_chunks
from openai_client import translate_text
from prompt_profiles import PROFILES, DEFAULT_PROFILE

# =========================
# ŚCIEŻKI DANYCH (WINDOWS / KODI)
# =========================

# Sprawdzamy, czy jesteśmy w Kodi, czy na Windowsie
try:
    import xbmcvfs
    ADDON_DATA_PATH = xbmcvfs.translatePath("special://profile/addon_data/script.kodi.srt.translator/")
except ImportError:
    # Jeśli nie ma Kodi, stwórz folder 'data' w folderze programu
    ADDON_DATA_PATH = os.path.join(os.getcwd(), "data")

STATE_FILE = os.path.join(ADDON_DATA_PATH, "resume_state.json")

def ensure_data_dir():
    """Upewnia się, że folder na dane istnieje."""
    if not os.path.exists(ADDON_DATA_PATH):
        try:
            os.makedirs(ADDON_DATA_PATH)
        except:
            pass

# =========================
# STAN (RESUME)
# =========================

def load_state():
    ensure_data_dir()
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_state(state):
    ensure_data_dir()
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except:
        pass

# =========================
# TŁUMACZENIE
# =========================

def translate_files(api_key, folder, srt_files, progress_callback=None, profile_key=None, model_key=None):
    """Główna funkcja - teraz przyjmuje też profil i model bezpośrednio z GUI."""
    state = load_state()

    # Wybór profilu: 
    # 1. Z okienka (Windows) 2. Z ustawień Kodi (jeśli byśmy je dopisali) 3. Domyślny
    p_key = profile_key or DEFAULT_PROFILE
    profile = PROFILES.get(p_key, PROFILES[DEFAULT_PROFILE])
    system_prompt = profile["prompt"]

    # Wybór modelu
    m_key = model_key or "gpt-4o-mini"

    for file_index, filename in enumerate(srt_files, start=1):
        input_path = os.path.join(folder, filename)
        output_path = os.path.join(folder, filename.rsplit('.', 1)[0] + ".PL.srt")

        original_text = read_srt(input_path)
        if not original_text:
            continue

        chunks = split_srt_into_chunks(original_text)
        file_state = state.get(filename, {})
        last_chunk = file_state.get("last_chunk", 0)
        translated_chunks = file_state.get("translated_chunks", [])
        total_chunks = len(chunks)

        # Kontynuacja (Resume)
        if last_chunk >= total_chunks and total_chunks > 0:
            final_text = "\n\n".join(translated_chunks)
            write_srt(output_path, final_text)
            continue

        for chunk_index in range(last_chunk, total_chunks):
            translated = translate_text(api_key, chunks[chunk_index], system_prompt, m_key)

            if translated:
                translated_chunks.append(translated)
                state[filename] = {
                    "last_chunk": chunk_index + 1,
                    "translated_chunks": translated_chunks
                }
                save_state(state)
            else:
                raise Exception(f"Błąd API w pliku {filename}")

            if progress_callback:
                # Informacja dla okienka o postępie
                progress_callback(file_index - 1 + (chunk_index + 1) / total_chunks, filename)

        # Zapis finalny
        final_text = "\n\n".join(translated_chunks)
        write_srt(output_path, final_text)

        if filename in state:
            del state[filename]
            save_state(state)