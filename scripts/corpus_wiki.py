import requests
import time

WIKI_API = "https://pt.wikipedia.org/w/api.php"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
}

categorias = [
    "Tecnologia",
    "Tecnologias modernistas",
    "Informática",
    "Ciência da computação",
    "Computação",
    "Engenharia elétrica",
    "Robótica",
    "Internet das coisas",
    "Inteligência artificial",
    "Aprendizado de máquina",
    "Computação em nuvem",
    "Redes de computadores",
    "Cibersegurança",
    "Sistemas embarcados",
    "Eletrônica"
]

def listar_paginas_categoria(categoria):
    """Retorna lista de páginas dentro de uma categoria da Wikipédia."""
    paginas = []
    cmcontinue = None

    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": f"Categoria:{categoria}",
            "cmlimit": "500",
            "format": "json"
        }

        if cmcontinue:
            params["cmcontinue"] = cmcontinue

        try:
            resposta = requests.get(WIKI_API, params=params, headers=headers)
            data = resposta.json()
        except Exception:
            print("⚠ A Wikipedia bloqueou momentaneamente. Aguardando 5s...")
            time.sleep(5)
            continue

        membros = data["query"]["categorymembers"]
        paginas.extend(membros)

        if "continue" in data:
            cmcontinue = data["continue"]["cmcontinue"]
        else:
            break

    return paginas


def baixar_texto_pagina(titulo):
    """Baixa o texto de uma página específica."""
    params = {
        "action": "query",
        "prop": "extracts",
        "titles": titulo,
        "format": "json",
        "explaintext": True
    }

    try:
        resposta = requests.get(WIKI_API, params=params, headers=headers)
        data = resposta.json()
    except Exception:
        print(f"⚠ Erro ao baixar {titulo}. Tentando novamente...")
        time.sleep(3)
        return baixar_texto_pagina(titulo)

    page = next(iter(data["query"]["pages"].values()))
    return page.get("extract", "")


arquivo_saida = open("corpus_wiki_tecnologia.txt", "w", encoding="utf8")

for categoria in categorias:
    print(f"\n📘 Baixando categoria: {categoria}")

    paginas = listar_paginas_categoria(categoria)

    for p in paginas:
        if p["ns"] == 0:  # página normal
            print(" -", p["title"])
            texto = baixar_texto_pagina(p["title"])
            arquivo_saida.write(texto + "\n")

arquivo_saida.close()
print("\n✅ Corpus Wikipedia salvo em corpus_wiki_tecnologia.txt")
