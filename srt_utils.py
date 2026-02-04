import re

# Ulepszone wyrażenie regularne dla bloków SRT
# Wyłapuje: Numer, Czas, Tekst (do następnej pustej linii lub końca pliku)
SRT_BLOCK_RE = re.compile(
    r"(\d+\s*\n\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}\s*\n.*?)(?=\n\s*\n|\Z)",
    re.DOTALL
)

def read_srt(path):
    """Odczytuje plik SRT z obsługą BOM (UTF-8-SIG) i normalizacją znaków końca linii."""
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            content = f.read()
            # Normalizacja końcówek linii na standardowe \n
            return content.replace('\r\n', '\n').strip()
    except Exception:
        return ""

def write_srt(path, content):
    """Zapisuje przetłumaczone napisy w formacie UTF-8."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            # Upewniamy się, że plik kończy się jedną pustą linią (standard SRT)
            f.write(content.strip() + "\n")
    except Exception:
        pass

def split_srt_into_chunks(srt_text, max_chars=5000):
    """
    Dzieli napisy na większe paczki (chunki) dla API.
    Dba o to, by nie rozbijać pojedynczych bloków napisów 
    i zachowywać odstępy \n\n między nimi.
    """
    if not srt_text:
        return []

    # Znajdujemy wszystkie bloki SRT
    blocks = SRT_BLOCK_RE.findall(srt_text)
    chunks = []
    current_chunk_blocks = []
    current_length = 0

    for block in blocks:
        block_stripped = block.strip()
        # Sprawdzamy, czy dodanie bloku przekroczy limit znaków
        # +2 uwzględnia dodanie "\n\n" między blokami
        if current_length + len(block_stripped) + 2 > max_chars and current_chunk_blocks:
            # Zamykamy obecny chunk
            chunks.append("\n\n".join(current_chunk_blocks))
            current_chunk_blocks = [block_stripped]
            current_length = len(block_stripped)
        else:
            current_chunk_blocks.append(block_stripped)
            current_length += len(block_stripped) + 2

    # Dodajemy ostatni chunk, jeśli nie jest pusty
    if current_chunk_blocks:
        chunks.append("\n\n".join(current_chunk_blocks))

    return chunks