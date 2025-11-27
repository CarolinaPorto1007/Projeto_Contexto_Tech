# limpar_unificar_corpus.py
import glob
import re

arquivos = glob.glob("corpus_*.txt")

with open("corpus_tecnologia.txt", "w", encoding="utf8") as saida:
    for arquivo in arquivos:
        with open(arquivo, "r", encoding="utf8") as f:
            texto = f.read()
            texto = texto.lower()
            texto = re.sub(r"http\S+", " ", texto)
            texto = re.sub(r"[^a-zà-ú0-9\s]", " ", texto)
            texto = re.sub(r"\s+", " ", texto)
            saida.write(texto + "\n")

print("✅ corpus_tecnologia.txt final criado!")
