from flask import Blueprint, render_template, request, jsonify
import random
import numpy as np
import requests
from gensim.models import KeyedVectors
from gensim.utils import simple_preprocess
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)

main_bp = Blueprint('main', __name__)

# --- Carregamento Global do Modelo Word2Vec ---
# O KeyedVectors só precisa ser carregado UMA VEZ na inicialização do app.
try:
    # Ajuste o caminho se o arquivo .kv não estiver na pasta raiz do app.py
    # Se word2vec_tecnologia.kv estiver em um subdiretório 'word2vec/', use 'word2vec/word2vec_tecnologia.kv'
    word2vec = KeyedVectors.load("word2vec_tecnologia.kv")
    VOCAB = set(word2vec.index_to_key)
    logging.info(f"✅ Modelo Word2Vec carregado. Vocabulário: {len(VOCAB)} palavras.")
except FileNotFoundError:
    logging.error("❌ ERRO: Arquivo 'word2vec_tecnologia.kv' não encontrado. Verifique o caminho.")
    word2vec = None
except Exception as e:
    logging.error(f"❌ ERRO ao carregar o modelo Word2Vec: {e}")
    word2vec = None

# --- Funções de Vetorização e Similaridade ---

def get_word_vector(palavra_ou_frase):
    """
    Calcula o vetor de uma palavra ou frase, tirando a média dos vetores das palavras individuais.
    Retorna None se nenhuma palavra da frase estiver no vocabulário.
    """
    if not word2vec:
        return None
        
    # Tokeniza a frase usando a mesma lógica de pré-processamento do treinamento
    tokens = simple_preprocess(palavra_ou_frase)
    
    # Filtra apenas os tokens que estão no vocabulário do Word2Vec
    vetores_validos = [word2vec[t] for t in tokens if t in VOCAB]
    
    if not vetores_validos:
        return None
    
    # Retorna o vetor médio da frase
    return np.mean(vetores_validos, axis=0)

def buscar_palavras_tecnologia():
    """
    Busca automaticamente títulos da Wikipédia sobre tecnologia, filtrando
    para retornar APENAS palavras únicas (não compostas).
    """
    url = "https://pt.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": "Categoria:Tecnologia",
        "cmlimit": "500",
        "format": "json"
    }

    # 🧠 Cabeçalho que evita bloqueio (403 Forbidden)
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; ContextoTech/1.0; +https://github.com/CarolinaPorto1007)"
    }
    
    # Lista reserva com palavras *únicas* que o seu modelo *provavelmente* conhece
    palavras_reserva = [
        "algoritmo", "servidor", "protocolo", "criptografia", "hardware", 
        "software", "internet", "automação", "robótica",
        "nuvem", "digital", "vetor", "rede", "pixel", "computacao"
    ]

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "query" not in data or "categorymembers" not in data["query"]:
            raise ValueError("Resposta inesperada da Wikipédia")

        artigos = [item["title"].lower() for item in data["query"]["categorymembers"]]
        
        # Filtra apenas artigos que são palavras únicas E podem ser vetorizadas
        palavras_validas = [
            a for a in artigos 
            if get_word_vector(a) is not None and len(a.split()) == 1 # Apenas palavras únicas
        ]

        if not palavras_validas:
            raise ValueError("Lista filtrada vazia. Usando reserva.")

        return palavras_validas

    except Exception as e:
        logging.warning(f"⚠️ Erro ao buscar palavras online: {e}. Usando lista de reserva.")
        
        # Garante que a lista reserva só contém palavras vetorizáveis
        return [p for p in palavras_reserva if get_word_vector(p) is not None]


# 🔒 Estado inicial do jogo
PALAVRAS_TEC = []
palavra_secreta = ""
vetor_secreto = None
jogo_finalizado = False

def inicializar_jogo():
    global PALAVRAS_TEC, palavra_secreta, vetor_secreto, jogo_finalizado
    if not word2vec:
        logging.error("O jogo não pode iniciar: Modelo Word2Vec está indisponível.")
        PALAVRAS_TEC = []
        palavra_secreta = "erro"
        vetor_secreto = None
        jogo_finalizado = True
        return
        
    PALAVRAS_TEC = buscar_palavras_tecnologia()
    if not PALAVRAS_TEC:
        logging.error("Nenhuma palavra de tecnologia válida foi encontrada. Usando palavra genérica.")
        PALAVRAS_TEC = ["computacao"]
    
    # Escolhe e vetoriza a palavra secreta
    palavra_secreta = random.choice(PALAVRAS_TEC)
    vetor_secreto = get_word_vector(palavra_secreta)
    
    if vetor_secreto is None:
        # Se por algum motivo a vetorização falhar, reinicia a escolha
        inicializar_jogo()
        return

    jogo_finalizado = False
    logging.info(f"✨ Novo jogo iniciado. Palavra secreta: '{palavra_secreta}'")

# Inicializa o jogo na importação
inicializar_jogo()

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/tentar', methods=['POST'])
def tentar():
    global jogo_finalizado

    if jogo_finalizado:
        return jsonify({"erro": "O jogo já terminou! Clique em Reiniciar para jogar novamente."})
        
    if vetor_secreto is None:
        return jsonify({"erro": "O vetor secreto não está definido. O jogo falhou ao inicializar."}), 500

    tentativa = request.json['palavra'].lower().strip()
    
    # 1. Obtém o vetor da tentativa (usando a função de média)
    vetor_tentativa = get_word_vector(tentativa)

    if vetor_tentativa is None:
        return jsonify({"similaridade": 0, "feedback": f"Palavra ou frase '{tentativa}' não é reconhecida no vocabulário de tecnologia."})

    # 2. CÁLCULO DE SIMILARIDADE DE COSSENOS (AGORA USANDO SOMENTE NUMPY)
    # A lógica de similaridade de cosseno está correta com numpy
    produto_escalar = np.dot(vetor_tentativa, vetor_secreto)
    norma_tentativa = np.linalg.norm(vetor_tentativa)
    norma_secreto = np.linalg.norm(vetor_secreto)
    
    # Garante que não há divisão por zero
    if norma_tentativa == 0 or norma_secreto == 0:
        similaridade = 0.0
    else:
        similaridade = produto_escalar / (norma_tentativa * norma_secreto)
        
    similaridade_porcentagem = round(float(similaridade * 100), 2)

    venceu = tentativa == palavra_secreta
    if venceu:
        jogo_finalizado = True

    # 3. Adiciona feedback de proximidade
    if similaridade_porcentagem >= 95:
        feedback = "🔥🔥🔥 INCRÍVEL! É praticamente a palavra secreta!"
    elif similaridade_porcentagem >= 80:
        feedback = "🔥 Quente! Está muito próximo do contexto."
    elif similaridade_porcentagem >= 50:
        feedback = "🟡 Morno. No contexto, mas ainda longe."
    else:
        feedback = "🧊 Frio. Tente mudar o contexto tecnológico."
        
    return jsonify({
        "similaridade": similaridade_porcentagem,
        "venceu": venceu,
        "feedback": feedback,
        "palavra_secreta": palavra_secreta if venceu else None
    })

@main_bp.route('/reiniciar', methods=['POST'])
def reiniciar():
    inicializar_jogo()
    return jsonify({"nova_palavra": palavra_secreta})