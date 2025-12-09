from flask import Blueprint, render_template, request, jsonify
import numpy as np
from gensim.models import KeyedVectors
import unicodedata
from datetime import datetime, timedelta
import hashlib

# Arquivos auxiliares
from routes import teste_filtro
from routes.model_loader import word2vec

"""
===========================================================
🔍 COMO O WORD2VEC É USADO NESTE JOGO (EXPLICAÇÃO TÉCNICA)
===========================================================

Este jogo funciona comparando a palavra que o jogador digita
com a palavra secreta usando vetores gerados pelo modelo
Word2Vec especializado em TECNOLOGIA.

📌 1. VETORIZAÇÃO DAS PALAVRAS
--------------------------------
Quando uma palavra é enviada pelo jogador, chamamos a função:

    obter_vetor_word2vec(palavra)

Essa função tenta encontrar o vetor da palavra dentro do modelo
Word2Vec (word2vec_tecnologia.kv).

• Se a palavra existe no modelo → retornamos o vetor real treinado
• Se NÃO existe → criamos um vetor aleatório normalizado
  (isso impede erro e mantém o jogo funcionando)

Cada palavra vira um vetor de 300 dimensões, por exemplo:
[0.12, -0.88, 0.03, ..., 0.54]

Esses vetores representam o *significado* das palavras com base
nos textos de tecnologia usados durante o treinamento.

📌 2. COMPARAÇÃO ENTRE AS PALAVRAS
------------------------------------
A similaridade é calculada por:

    calcular_similaridade_cosseno(vetor_tentativa, vetor_secreto)

Esse cálculo gera um valor entre 0% e 100%, baseado no quanto
os vetores apontam para a mesma direção no espaço vetorial.

Quanto mais parecidas no "contexto tecnológico", maior a
similaridade.

Exemplos:
• “computador” x “processador” → alta similaridade
• “computador” x “bluetooth”   → média
• “computador” x “ransomware”  → baixa

📌 3. PALAVRA DO DIA
-----------------------
A função:

    obter_palavra_do_dia()

usa um seed baseado na data atual para escolher SEMPRE a mesma
palavra durante aquele dia, impedindo que o jogador reinicie a
partida.

📌 4. FILTRO DE PALAVRAS
---------------------------
A função:

    filtrar_palavras_no_modelo()

garante que só usamos:
    ✔ palavras únicas (sem espaço)
    ✔ palavras que EXISTEM dentro do Word2Vec

Isso melhora a qualidade do jogo, pois só comparamos vetores reais.

📌 5. POR QUE ISSO TUDO?
---------------------------
Porque o jogo funciona como o famoso “Contexto”: o jogador não
recebe letras, e sim um grau de proximidade semântica.

Exemplo:
Se a palavra secreta é "python" e você tenta “programação”,
o Word2Vec calcula que esses vetores são próximos → similaridade
alta. Isso orienta o jogador até acertar a palavra.

============================================================
RESUMO TÉCNICO FINAL
------------------------------------------------------------
• Word2Vec gera vetores que representam significados.
• A tentativa e a palavra secreta são convertidas em vetores.
• A similaridade entre eles diz o "quão perto" o jogador está.
• O jogo usa apenas palavras únicas e válidas do modelo.
• O desafio só reinicia à meia-noite (não pode reiniciar antes).

============================================================
"""

main_bp = Blueprint('main', __name__)

# 📚 Lista de palavras ÚNICAS de tecnologia (sem espaços)
PALAVRAS_TECNOLOGIA = [
    "algoritmo",
    "programação",
    "computador",
    "processador",
    "internet",
    "servidor",
    "blockchain",
    "criptomoeda",
    "automação",
    "cibersegurança",
    "firewall",
    "streaming",
    "drone",
    "smartphone",
    "wifi",
    "bluetooth",
    "sensor",
    "microcontrolador",
    "compilador",
    "framework",
    "biblioteca",
    "virtualização",
    "devops",
    "software",
    "hardware",
    "firmware",
    "malware",
    "antivirus",
    "backup",
    "cache",
    "cookie",
    "debug",
    "download",
    "upload",
    "firewall",
    "gateway",
    "hosting",
    "javascript",
    "python",
    "java",
    "kernel",
    "linux",
    "windows",
    "android",
    "mac",
    "interface",
    "database",
    "api",
    "Json",
    "xml",
    "html",
    "css",
    "pixel",
    "render",
    "router",
    "switch",
    "modem",
    "protocolo",
    "ethernet",
    "laptop",
    "tablet",
    "monitor",
    "teclado",
    "mouse",
    "webcam",
    "scanner",
    "impressora",
    "pendrive",
    "memória",
    "disco",
    "chipset",
    "transistor",
    "capacitor",
    "resistor",
    "diodo",
    "circuito",
    "eletrônica",
    "digital",
    "analógico",
    "binário",
    "hexadecimal",
    "byte",
    "megabyte",
    "gigabyte",
    "terabyte",
    "bandwidth",
    "latência",
    "throughput",
    "firewall",
    "antivírus",
    "malware",
    "phishing",
    "ransomware",
    "trojan",
    "spyware",
    "adware",
    "rootkit",
    "botnet",
    "ddos",
    "encryption",
    "decryption",
    "hash",
    "token",
    "autenticação",
    "autorização",
    "certificado",
    "ssl",
    "https",
    "firewall",
    "proxy",
    "vpn",
    "dns",
    "ip",
    "tcp",
    "udp",
    "http",
    "ftp",
    "smtp",
    "pop",
    "imap",
    "ssh",
    "telnet",
    "ping",
    "traceroute",
    "subnet",
    "gateway",
    "broadcast",
    "multicast",
    "unicast"
]

def normalizar_texto(texto):
    """Remove acentos e normaliza o texto para comparação"""
    texto = texto.lower().strip()
    # Remove acentos
    texto_norm = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto_norm

def obter_vetor_word2vec(palavra):
    """Obtém o vetor de uma palavra usando Word2Vec"""
    if word2vec is None:
        # Retorna vetor aleatório se modelo não carregou
        vetor = np.random.randn(300)
        return vetor / np.linalg.norm(vetor)
    
    palavra_norm = normalizar_texto(palavra)
    
    # Tenta diferentes variações da palavra
    variantes = [
        palavra_norm,
        palavra.lower().strip()
    ]
    
    for variante in variantes:
        try:
            if variante in word2vec:
                return word2vec[variante]
        except:
            continue
    
    # Se não encontrar no modelo, retorna vetor aleatório normalizado
    print(f"⚠️ Palavra '{palavra}' não encontrada no modelo")
    vetor = np.random.randn(300)
    return vetor / np.linalg.norm(vetor)

def calcular_similaridade_cosseno(vetor1, vetor2):
    """Calcula a similaridade do cosseno entre dois vetores"""
    # Normaliza os vetores
    norma1 = np.linalg.norm(vetor1)
    norma2 = np.linalg.norm(vetor2)
    
    if norma1 == 0 or norma2 == 0:
        return 0.0
    
    # Produto escalar normalizado
    similaridade = np.dot(vetor1, vetor2) / (norma1 * norma2)
    
    # Converte para porcentagem e limita entre 0 e 100
    similaridade_pct = max(0, min(100, similaridade * 100))
    
    return round(float(similaridade_pct), 2)

def filtrar_palavras_no_modelo():
    """Filtra apenas palavras ÚNICAS que existem no modelo Word2Vec"""
    if word2vec is None:
        # Filtra apenas palavras sem espaço
        return [p for p in PALAVRAS_TECNOLOGIA if ' ' not in p]
    
    palavras_validas = []
    for palavra in PALAVRAS_TECNOLOGIA:
        # Ignora palavras compostas (com espaço)
        if ' ' in palavra:
            continue
            
        variantes = [
            normalizar_texto(palavra),
            palavra.lower().strip()
        ]
        
        for variante in variantes:
            if variante in word2vec:
                palavras_validas.append(palavra)
                break
    
    print(f"📊 {len(palavras_validas)} palavras únicas válidas no modelo")
    return palavras_validas if palavras_validas else [p for p in PALAVRAS_TECNOLOGIA if ' ' not in p]

def obter_palavra_do_dia():
    """Gera a palavra do dia baseada na data atual"""
    # Obtém a data de hoje
    hoje = datetime.now().date()
    
    # Cria um seed determinístico baseado na data
    seed_str = f"{hoje.year}-{hoje.month:02d}-{hoje.day:02d}"
    seed_hash = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
    
    # Usa o seed para escolher a palavra
    palavras_validas = filtrar_palavras_no_modelo()
    indice = seed_hash % len(palavras_validas)
    
    return palavras_validas[indice], hoje

def obter_proximo_reset():
    """Retorna quando será o próximo reset (meia-noite do dia seguinte)"""
    agora = datetime.now()
    amanha = agora.date() + timedelta(days=1)
    meia_noite = datetime.combine(amanha, datetime.min.time())
    return meia_noite

def formatar_tempo_restante(tempo_reset):
    """Formata o tempo restante até o reset"""
    agora = datetime.now()
    diferenca = tempo_reset - agora
    
    horas = int(diferenca.total_seconds() // 3600)
    minutos = int((diferenca.total_seconds() % 3600) // 60)
    
    return f"{horas}h {minutos}min"

# 🔒 Estado global do jogo
palavra_secreta = ""
data_palavra = None
vetor_secreto = None
jogo_finalizado = False
tentativas_historico = []

def inicializar_jogo():
    """Inicializa o jogo com a palavra do dia"""
    global palavra_secreta, data_palavra, vetor_secreto, jogo_finalizado, tentativas_historico
    
    # Obtém palavra do dia
    palavra_secreta, data_palavra = obter_palavra_do_dia()
    vetor_secreto = obter_vetor_word2vec(palavra_secreta)
    jogo_finalizado = False
    tentativas_historico = []
    
    print(f"🎮 Palavra do dia: {palavra_secreta} (Data: {data_palavra})")

def verificar_reset_diario():
    """Verifica se precisa resetar o jogo para um novo dia"""
    global data_palavra
    
    hoje = datetime.now().date()
    if data_palavra != hoje:
        print(f"🔄 Novo dia detectado! Resetando jogo...")
        inicializar_jogo()

# Inicializa o jogo ao importar o módulo
inicializar_jogo()

@main_bp.route('/')
def index():
    """Renderiza a página principal"""
    verificar_reset_diario()
    return render_template('index.html')

@main_bp.route('/tentar', methods=['POST'])
def tentar():
    """Processa uma tentativa do jogador"""
    global jogo_finalizado, tentativas_historico
    
    verificar_reset_diario()

    if jogo_finalizado:
        tempo_reset = obter_proximo_reset()
        tempo_restante = formatar_tempo_restante(tempo_reset)
        return jsonify({
            "erro": f"Você já completou o desafio de hoje! Volte em {tempo_restante} para uma nova palavra."
        })

    # Obtém a palavra tentada
    tentativa = request.json.get('palavra', '').lower().strip()

    tentativa = teste_filtro.remover_aumentativo(tentativa)

    tentativa = teste_filtro.remover_diminutivo(tentativa)

    tentativa = teste_filtro.obter_singular(tentativa)

    if teste_filtro.possui_caracteres_invalidos(tentativa):
        return jsonify({"erro": "Não utilize números ou símbolos, apenas letras!"})

    if not teste_filtro.palavra_existe(tentativa):
        return jsonify({"erro": "Palavra desconhecida ou inválida! Verifique a ortografia."})
    

    if not tentativa:
        return jsonify({"erro": "Digite uma palavra válida."})
    
    # Verifica se é palavra única
    if ' ' in tentativa:
        return jsonify({"erro": "Apenas palavras únicas são aceitas (sem espaços)."})
    
    # Verifica se já tentou essa palavra
    if tentativa in tentativas_historico:
        return jsonify({"erro": "Você já tentou essa palavra!"})
    
    # Obtém vetor da tentativa
    vetor_tentativa = obter_vetor_word2vec(tentativa)
    
    # Calcula similaridade
    similaridade = calcular_similaridade_cosseno(vetor_tentativa, vetor_secreto)
    
    # Verifica vitória
    venceu = normalizar_texto(tentativa) == normalizar_texto(palavra_secreta)
    
    if venceu:
        jogo_finalizado = True
    
    # Adiciona ao histórico
    tentativas_historico.append(tentativa)
    
    print(f"🎯 Tentativa: '{tentativa}' | Similaridade: {similaridade}% | Venceu: {venceu}")

    response = {
        "similaridade": similaridade,
        "venceu": venceu,
        "palavra_exibida": tentativa,
        "palavra_secreta": palavra_secreta if venceu else None,
        "total_tentativas": len(tentativas_historico)
    }
    
    if venceu:
        tempo_reset = obter_proximo_reset()
        tempo_restante = formatar_tempo_restante(tempo_reset)
        response["tempo_proximo"] = tempo_restante
    
    return jsonify(response)

# @main_bp.route('/dica', methods=['GET'])
# def dica():
#     """Retorna uma dica sobre a palavra secreta"""
#     verificar_reset_diario()
    
#     if jogo_finalizado:
#         return jsonify({"erro": "Você já completou o desafio de hoje!"})
    
#     try:
#         if word2vec and normalizar_texto(palavra_secreta) in word2vec:
#             # Busca palavras mais similares no modelo
#             palavra_norm = normalizar_texto(palavra_secreta)
            
#             if palavra_norm in word2vec:
#                 similares = word2vec.most_similar(palavra_norm, topn=5)
#                 palavra_similar = similares[0][0].replace('_', ' ')
#                 return jsonify({
#                     "dica": f"💡 A palavra é similar a: {palavra_similar}"
#                 })
        
#         # Dica genérica
#         dica_texto = f"💡 A palavra tem {len(palavra_secreta)} caracteres"
        
#         return jsonify({"dica": dica_texto})
        
#     except Exception as e:
#         print(f"❌ Erro ao gerar dica: {e}")
#         return jsonify({"dica": f"💡 A palavra tem {len(palavra_secreta)} caracteres"})

@main_bp.route('/reiniciar', methods=['POST'])
def reiniciar():
    """Não permite reiniciar - apenas no dia seguinte"""
    verificar_reset_diario()
    
    tempo_reset = obter_proximo_reset()
    tempo_restante = formatar_tempo_restante(tempo_reset)
    
    return jsonify({
        "erro": f"Você só pode jogar novamente em {tempo_restante}",
        "proximo_reset": tempo_reset.isoformat()
    })

@main_bp.route('/stats', methods=['GET'])
def stats():
    """Retorna estatísticas do jogo atual"""
    verificar_reset_diario()
    
    tempo_reset = obter_proximo_reset()
    tempo_restante = formatar_tempo_restante(tempo_reset)
    
    return jsonify({
        "total_tentativas": len(tentativas_historico),
        "jogo_finalizado": jogo_finalizado,
        "palavras_no_modelo": len(word2vec) if word2vec else 0,
        "data_palavra": str(data_palavra),
        "proximo_reset": tempo_restante
    })

@main_bp.route('/desistir', methods=['POST'])
def desistir():
    """Revela a palavra secreta quando o jogador desiste"""
    global jogo_finalizado
    verificar_reset_diario()
    
    jogo_finalizado = True
    tempo_reset = obter_proximo_reset()
    tempo_restante = formatar_tempo_restante(tempo_reset)
    
    return jsonify({
        "palavra_secreta": palavra_secreta,
        "total_tentativas": len(tentativas_historico),
        "tempo_proximo": tempo_restante
    })