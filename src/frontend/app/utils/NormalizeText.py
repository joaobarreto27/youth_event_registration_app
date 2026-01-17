import re
import unicodedata


# Função para normalizar o texto
def normalizar_texto(texto):
    texto = str(texto).lower()
    texto = (
        unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8")
    )  # Remove acentos
    texto = re.sub(r"\s+", " ", texto)  # Substitui múltiplos espaços por um só
    texto = texto.strip()
    return texto
