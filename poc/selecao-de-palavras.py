import wikipediaapi
import nltk

nltk.download('punkt_tab')

# Configuração obrigatória (User-Agent)
wiki_wiki = wikipediaapi.Wikipedia(
    user_agent='MeuBotWord2Vec/1.0 (costawilliam971@gmail.com)',
    language='pt'
)

lista_frases_tech = []
limite_paginas = 20  # Limite para o exemplo não demorar

def processar_categoria(nome_categoria):
    cat = wiki_wiki.page(nome_categoria)
    contador = 0

    # Itera sobre as páginas que pertencem a essa categoria
    for membro in cat.categorymembers.values():
        if membro.ns == wikipediaapi.Namespace.MAIN: # Apenas artigos, ignora subcategorias
            frases = nltk.sent_tokenize(membro.text)

            # Filtra e adiciona frases
            for f in frases:
                if len(f.split()) > 5:
                    lista_frases_tech.append(f)

            contador += 1
            print(f"Processado: {membro.title}")

        if contador >= limite_paginas:
            break

print("Acessando Categoria:Ciência da computação...")
processar_categoria("Categoria:Ciência da computação")

print(f"\nTotal de frases coletadas: {len(lista_frases_tech)}")
for i, frase in enumerate(lista_frases_tech):
    print(f'{i + 1}: {frase}')
