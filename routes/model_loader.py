import re
from spacy.lang.pt.stop_words import STOP_WORDS 
from huggingface_hub import hf_hub_download
from safetensors.numpy import load_file
from gensim.models import KeyedVectors

print("📚 Iniciando carregamento inteligente (Smart Load)...")

# Filtra palavras inúteis do vocabulário
def palavra_eh_valida(palavra):
    """Retorna True se a palavra for útil para o jogo."""
    
    # Tamanho mínimo
    if len(palavra) < 2: return False

    # Sem espaços ou underscores
    if ' ' in palavra or '_' in palavra: return False
    
    # Preposições e artigos comuns
    if palavra in STOP_WORDS: return False

    # Caracteres inválidos (apenas letras minúsculas e acentuadas)
    if re.search(r'[^a-zááàâãéèêíïóôõöúçñ]', palavra): return False
    
    return True

# Carregamento e processamento
word2vec = None

try:
    # Verifica se os arquivos do modelo estão no cache ou faz o download
    emb_path = hf_hub_download(repo_id="nilc-nlp/fasttext-skip-gram-300d", filename="embeddings.safetensors")
    vocab_path = hf_hub_download(repo_id="nilc-nlp/fasttext-skip-gram-300d", filename="vocab.txt")

    indices_validos = []
    palavras_validas = []
    
    # Abre APENAS o vocabulário para leitura (sem criar arquivo de log)
    with open(vocab_path, "r", encoding="utf-8") as f_entrada:
        for i, line in enumerate(f_entrada):
            palavra = line.strip()
            
            # Verifica se a palavra serve para o jogo
            if palavra_eh_valida(palavra):
                palavras_validas.append(palavra)
                indices_validos.append(i) # Guarda a "coordenada" da linha

    print(f"✅ Filtro concluído! {len(palavras_validas)} palavras aprovadas.")

    # Carrega a matriz gigante de números
    dados_completos = load_file(emb_path)
    matriz_inteira = dados_completos["embeddings"]
    
    # Pega APENAS as linhas que correspondem às palavras aprovadas
    vetores_filtrados = matriz_inteira[indices_validos]

    # Cria o objeto final limpo
    word2vec = KeyedVectors(vector_size=300)
    word2vec.add_vectors(palavras_validas, vetores_filtrados)

    print("✅ Modelo Word2Vec carregado e filtrado com sucesso!")

except Exception as e:
    print(f"❌ Erro crítico: {e}")
    word2vec = None