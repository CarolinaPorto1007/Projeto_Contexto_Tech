# baixar_blogs_tecnologia.py
import requests
from bs4 import BeautifulSoup

sites = [
    "https://www.canaltech.com.br/ultimas/",
    "https://www.tecmundo.com.br/novidades",
    "https://olhardigital.com.br/category/tecnologia/"
]

with open("corpus_blogs_tecnologia.txt", "w", encoding="utf8") as f:
    for url in sites:
        print("📰 Acessando:", url)
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        textos = soup.find_all("p")
        for p in textos:
            f.write(p.get_text() + "\n")

print("✅ Corpus de blogs salvo em corpus_blogs_tecnologia.txt")
