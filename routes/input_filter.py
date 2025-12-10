import bisect
import os



# DEFININDO O CAMINHO DOS ARQUIVOS DE PALAVRAS
DIRETORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
CAMINHO_ARQUIVO = os.path.join(DIRETORIO_SCRIPT, "..", "base_palavras", "com_acento.txt")
CAMINHO_TECH = os.path.normpath(os.path.join(DIRETORIO_SCRIPT, "..", "base_palavras", "palavras_tecnologia.txt"))

# CARREGANDO TABELA DE PALAVRAS ORDENADAS
try:
    with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as f:
        # Carrega removendo espaços e quebras de linha
        TABELA_PALAVRAS_ORDENADAS = [linha.strip() for linha in f]
    print(f"📚 Tabela de dados carregada: {len(TABELA_PALAVRAS_ORDENADAS)} palavras.")
except FileNotFoundError:
    print(f"❌ ERRO CRÍTICO: Arquivo não encontrado no caminho:\n{CAMINHO_ARQUIVO}")
    TABELA_PALAVRAS_ORDENADAS = []

# CARREGANDO TABELA DE PALAVRAS DE TECNOLOGIA
try:
    with open(CAMINHO_TECH, "r", encoding="utf-8") as f:
        TABELA_PALAVRAS_TECNOLOGIA = {linha.strip().lower() for linha in f if linha.strip()}
except FileNotFoundError:
    TABELA_PALAVRAS_TECNOLOGIA = set()



# INICIANDO FILTRAGEM E PADRONIZAÇÃO DE PALAVRAS
def palavra_existe(palavra):
    """
    Verifica se a palavra existe nas tabelas de dados usando busca binária.
    Complexidade: O(log N) - Extremamente rápido.
    """
    if not TABELA_PALAVRAS_ORDENADAS:
        return False
        
    if palavra in TABELA_PALAVRAS_TECNOLOGIA:
        return palavra
    
    # Normaliza a entrada com tudo minúsculo e sem espaços nas pontas
    palavra = palavra.lower().strip()
    
    # O bisect_left encontra a posição de inserção para manter a ordem
    index = bisect.bisect_left(TABELA_PALAVRAS_ORDENADAS, palavra)
    
    # Se o índice retornado estiver dentro da lista e a palavra for igual, ACHAMOS!
    if index < len(TABELA_PALAVRAS_ORDENADAS) and TABELA_PALAVRAS_ORDENADAS[index] == palavra:
        return palavra
        
    return False

def padronizar_plural(palavra):
    """
    Tenta transformar plural em singular.
    Retorna o singular SE ele existir no banco.
    Caso contrário, retorna a palavra original.
    """
    original = palavra.lower().strip()
    
    # Se a palavra original já não termina em 's', provavelmente é singular
    # (Exceção: palavras que não seguem regra padrão, mas vamos focar no 's' final)
    if not original.endswith('s'):
        return original

    candidato_sing = "" # candidato_singidato a singular

    # --- REGRA 1: Terminações em -NS (Nuvens -> Nuvem) ---
    if original.endswith('ns'):
        candidato_sing = original[:-2] + 'm'
        if palavra_existe(candidato_sing): return candidato_sing

    # --- REGRA 2: Terminações em -ÕES, -ÃES, -ÃOS ---
    if original.endswith(('ões', 'ães', 'ãos')):
        # Tenta trocar tudo por 'ão' (Corações -> Coração, Pães -> Pão)
        candidato_sing = original[:-3] + 'ão' 
        if palavra_existe(candidato_sing): return candidato_sing

    # --- REGRA 3: Terminações em -IS (Complexo: animais, faróis, funis) ---
    if original.endswith('is'):
        # Caso -AIS -> -AL (Animais -> Animal)
        if original.endswith('ais'):
            candidato_sing = original[:-3] + 'al'
            if palavra_existe(candidato_sing): return candidato_sing
        
        # Caso -ÉIS -> -EL (Papéis -> Papel) - Remove acento
        if original.endswith('éis'):
            candidato_sing = original[:-3] + 'el'
            if palavra_existe(candidato_sing): return candidato_sing
            
        # Caso -ÓIS -> -OL (Anzóis -> Anzol) - Remove acento
        if original.endswith('óis'):
            candidato_sing = original[:-3] + 'ol'
            if palavra_existe(candidato_sing): return candidato_sing
        
        # Caso -IS -> -IL (Barris -> Barril)
        if original.endswith('is'):
            candidato_sing = original[:-2] + 'il'
            if palavra_existe(candidato_sing): return candidato_sing

    # --- REGRA 4: Terminações em -ES (Flores -> Flor, Luzes -> Luz) ---
    if original.endswith('es'):
        # Tenta remover apenas o 'es' (Muitas vezes funciona para R e Z)
        candidato_sing = original[:-2]
        if palavra_existe(candidato_sing): return candidato_sing

    # --- REGRA 5: Plural Simples (Remove apenas o 's') ---
    if original.endswith('s'):
        candidato_sing = original[:-1]
        if palavra_existe(candidato_sing): return candidato_sing

    # Se falhou em tudo (Ex: 'Ônibus' -> tira 's' vira 'Ônibu' que não existe),
    # assume que a palavra já é a base ou é invariável.
    return original

def padronizar_genero(palavra):
    """
    Tenta converter feminino para masculino.
    Contém Lista de Proteção para evitar mudanças de sentido (Ex: Casa -> Caso).
    """
    original = palavra.lower().strip()
    
    # Se não termina em 'a' ou 'ã', provavelmente já é masculino ou invariável
    if not original.endswith(('a', 'ã')):
        return original

    # --- LISTA DE PROTEÇÃO (Falsos Femininos) ---
    # Palavras terminadas em 'a' que mudam de sentido se virarem 'o',
    # ou que simplesmente não têm masculino por flexão direta.
    protegidas = [
        'casa',   # Evita 'caso'
        'bola',   # Evita 'bolo'
        'mala',   # Evita 'malo' (arcaico/espanhol)
        'fala',   # Evita 'falo' (verbo/substantivo anatômico)
        'bota',   # Evita 'boto' (animal)
        'cola',   # Evita 'colo'
        'mola',   # Evita 'molo'
        'sola',   # Evita 'solo'
        'lata',   # Evita 'lato' (amplo)
        'mata',   # Evita 'mato' (grama)
        'vela',   # Evita 'velo' (lã)
        'pipa',   # Evita 'pipo'
        'rosa',   # Evita 'roso'
        'palha',  # Evita 'palho'
        'folha',  # Evita 'folho'
        'caixa',  # Evita 'caixo'
        'cabra',  # Evita 'cabro'
        'fera',   # Evita 'fero'
        'brasa',  # Evita 'braso'
        'tropa',  # Evita 'tropo'
        'prata',  # Evita 'prato'
        'cama',   # Evita 'camo'
        'lama',   # Evita 'lamo'
        'grama',  # Evita 'gramo'
        'dama',   # Evita 'damo' (embora exista, raramente é o par desejado)
        'baleia', # Evita 'baleio'
        'aranha', # Evita 'aranho'
        'faca'    # Evita 'faco' (se existir no banco)
    ]

    if original in protegidas:
        return original

    # --- TENTATIVAS (Candidatos a Masculino) ---

    # 1. Regra -ESA/-ESSA (Portuguesa -> Português)
    if original.endswith('esa'):
        candidato = original[:-3] + 'ês'
        if palavra_existe(candidato): return candidato

    if original.endswith('essa'):
        candidato = original[:-4] + 'e' # Abadessa -> Abade, Condessa -> Conde
        if palavra_existe(candidato): return candidato

    # 2. Regra -ONA (Valentona -> Valentão)
    if original.endswith('ona'):
        candidato = original[:-3] + 'ão'
        if palavra_existe(candidato): return candidato
        
    # 3. Regra -Ã (Irmã -> Irmão)
    if original.endswith('ã'):
        candidato = original[:-1] + 'ão'
        if palavra_existe(candidato): return candidato

    # 4. Regra Geral: Troca 'a' por 'o' (Menina -> Menino)
    if original.endswith('a'):
        candidato = original[:-1] + 'o'
        if palavra_existe(candidato): return candidato

    # 5. Regra de Corte: Apenas tira o 'a' (Professora -> Professor)
    candidato = original[:-1]
    if len(candidato) > 2 and palavra_existe(candidato): 
        return candidato

    return original

def padronizar_grau(palavra):
    """
    Remove diminutivos/aumentativos e tenta restaurar acentos perdidos.
    Ex: Pezão -> Pé, Cafezinho -> Café.
    """
    original = palavra.lower().strip()
    
    if len(original) < 4:
        return original

    # --- REGRA 1: Diminutivos com -ZINHO / -ZINHA ---
    if original.endswith(('zinho', 'zinha')):
        # Tenta remover o sufixo inteiro (Pezinho -> Pe)
        base = original[:-5]
        
        if palavra_existe(base): return base
        
        # Tenta repor acentos (Pezinho -> Pe -> Pé / Cafezinho -> Cafe -> Café)
        if base and base[-1] in 'aeo':
            # Tenta Agudo (á, é, ó)
            mapa_agudo = {'a': 'á', 'e': 'é', 'o': 'ó'}
            candidato = base[:-1] + mapa_agudo[base[-1]]
            if palavra_existe(candidato): return candidato
            
            # Tenta Circunflexo (â, ê, ô)
            mapa_circ = {'a': 'â', 'e': 'ê', 'o': 'ô'}
            candidato = base[:-1] + mapa_circ[base[-1]]
            if palavra_existe(candidato): return candidato

    # --- REGRA 2: Diminutivos com -INHO / -INHA ---
    if original.endswith(('inho', 'inha')):
        base = original[:-4]
        # Ex: Gatinho -> Gato, Casinha -> Casa
        for vogal in ['o', 'a', 'e']:
            if palavra_existe(base + vogal): return base + vogal
        if palavra_existe(base): return base

    # --- REGRA 3: Aumentativos com -ZÃO / -ZONA ---
    if original.endswith(('zão', 'zona')):
        # Remove 'zão'/'zona' (Pezão -> Pe)
        sufixo = 3 if original.endswith('zão') else 4
        base = original[:-sufixo]

        if palavra_existe(base): return base

        # Tenta repor acentos (Pezão -> Pe -> Pé)
        if base and base[-1] in 'aeo':
            mapa_agudo = {'a': 'á', 'e': 'é', 'o': 'ó'}
            candidato = base[:-1] + mapa_agudo[base[-1]]
            if palavra_existe(candidato): return candidato
            
            mapa_circ = {'a': 'â', 'e': 'ê', 'o': 'ô'}
            candidato = base[:-1] + mapa_circ[base[-1]]
            if palavra_existe(candidato): return candidato

    # --- REGRA 4: Aumentativos com -ÃO / -ONA ---
    # (Rapazão -> Rapaz, Mulherona -> Mulher)
    if original.endswith('ão'):
        base = original[:-2]
        # Gatão -> Gato
        if palavra_existe(base + 'o'): return base + 'o'
        # Rapazão -> Rapaz (base pura)
        if palavra_existe(base): return base

    if original.endswith('ona'):
        base = original[:-3]
        if palavra_existe(base + 'a'): return base + 'a'
        if palavra_existe(base): return base

    # --- REGRA 5: Sufixos -ITO / -ITA ---
    if original.endswith(('ito', 'ita')):
        base = original[:-3]
        if palavra_existe(base + 'o'): return base + 'o'
        if palavra_existe(base + 'a'): return base + 'a'

    return original

def padronizar_verbo(palavra):
    """
    Tenta converter verbos conjugados para o INFINITIVO.
    Retorna o infinitivo SE ele existir no banco.
    """
    original = palavra.lower().strip()

    # --- 1. Mesóclise e Ênclise (Hífens) ---
    # Ex: falar-lhe-ei, dar-se-á, chamá-lo
    if '-' in original:
        partes = original.split('-')
        raiz = partes[0]
        
        # Caso simples: o verbo está inteiro antes do hífen (ex: mandar-lhe)
        if palavra_existe(raiz): return raiz
        
        # Caso com acento final (ex: amá-lo -> amar)
        # Remove acento da última letra e adiciona 'r'
        if raiz.endswith(('á', 'é')):
            mapa_acento = {'á': 'ar', 'é': 'er'}
            candidato = raiz[:-1] + mapa_acento[raiz[-1]]
            if palavra_existe(candidato): return candidato

        # Mesóclise (ex: falar-lhe-ei -> raiz é 'falar')
        # Tenta validar se a primeira parte + 'r' forma um verbo (dir-se-ia -> dir -> dizer é irregular, difícil pegar sem mapa)
        if palavra_existe(raiz + 'r'): return raiz + 'r'

    # --- 2. Gerúndio (-NDO) ---
    if original.endswith('ando'): # Amando -> Amar
        candidato = original[:-4] + 'ar'
        if palavra_existe(candidato): return candidato

    if original.endswith('endo'): # Correndo -> Correr
        candidato = original[:-4] + 'er'
        if palavra_existe(candidato): return candidato

    if original.endswith('indo'): # Partindo -> Partir
        candidato = original[:-4] + 'ir'
        if palavra_existe(candidato): return candidato

    # --- 3. Particípio (-DO) ---
    if original.endswith('ado'): # Amado -> Amar
        candidato = original[:-3] + 'ar'
        if palavra_existe(candidato): return candidato

    if original.endswith('ido'): # Comido/Partido -> Comer/Partir
        # Tenta -er primeiro
        candidato = original[:-3] + 'er'
        if palavra_existe(candidato): return candidato
        # Tenta -ir
        candidato = original[:-3] + 'ir'
        if palavra_existe(candidato): return candidato

    # --- 4. Pretéritos e Futuros (Sufixos diversos) ---
    
    # Terminações em -RAM (Pretérito Perfeito/Mais-que-perfeito)
    if original.endswith('aram'): # Falaram -> Falar
        candidato = original[:-4] + 'ar'
        if palavra_existe(candidato): return candidato
        
    if original.endswith('eram'): # Comeram -> Comer
        candidato = original[:-4] + 'er'
        if palavra_existe(candidato): return candidato
        
    if original.endswith('iram'): # Partiram -> Partir
        candidato = original[:-4] + 'ir'
        if palavra_existe(candidato): return candidato

    # Terminações em -AVA (Imperfeito 1ª conj)
    if original.endswith('ava'): # Amava -> Amar
        candidato = original[:-3] + 'ar'
        if palavra_existe(candidato): return candidato

    # Terminações em -IA (Imperfeito 2ª/3ª conj)
    if original.endswith('ia'): # Corria/Partia
        if palavra_existe(original[:-2] + 'er'): return original[:-2] + 'er'
        if palavra_existe(original[:-2] + 'ir'): return original[:-2] + 'ir'

    # Terminações Curtas (-OU, -EU, -IU)
    if original.endswith('ou'): # Falou -> Falar
        candidato = original[:-2] + 'ar'
        if palavra_existe(candidato): return candidato

    if original.endswith('eu'): # Correu -> Correr
        candidato = original[:-2] + 'er'
        if palavra_existe(candidato): return candidato

    if original.endswith('iu'): # Partiu -> Partir
        candidato = original[:-2] + 'ir'
        if palavra_existe(candidato): return candidato

    # Terminação -EI (Pretérito Perfeito 1ª p.s.)
    if original.endswith('ei'): # Amei -> Amar
        candidato = original[:-2] + 'ar'
        if palavra_existe(candidato): return candidato

    # Terminação -ÃO (Futuro)
    if original.endswith('ão'): 
        # Tenta arão -> ar
        if original.endswith('arão'):
            if palavra_existe(original[:-4] + 'ar'): return original[:-4] + 'ar'
        # Genérico (terão -> ter)
        if palavra_existe(original[:-2] + 'r'): return original[:-2] + 'r' 

    return original

def padronizar_derivacoes(palavra):
    """
    Tenta remover sufixos nominais (profissão, qualidade, ação) para encontrar a palavra raiz.
    Contém proteção contra "falsos positivos" (ex: Coração não vira Corar).
    """
    original = palavra.lower().strip()
    
    # Trava de segurança para palavras muito curtas (pão, mão, céu, lei)
    if len(original) < 4:
        return original

    # --- 1. BLOCO DE TRATAMENTO DE -ÃO / -ÇÃO (O mais crítico) ---
    if original.endswith('ão'):
        # A. LISTA DE PROTEÇÃO (Colisões Semânticas)
        # Palavras que parecem derivadas/aumentativos, mas se mudar o sufixo,
        # viram outra palavra com sentido totalmente errado.
        protegidas = [
            'coração', 'coracao', # Evita 'corar'
            'nação', 'nacao',     # Evita 'nar' (se existisse) ou 'naça'
            'ração', 'racao',     # Evita 'rar'
            'fração', 'fracao',
            'canção', 'cancao',
            'feijão', 'feijao',
            'violão', 'violao',   # Evita 'viola' (sentido diferente)
            'avião', 'aviao',
            'verão', 'verao',     # Evita 'ver'
            'melão', 'melao',     # Evita 'melar'
            'leão', 'leao',
            'camaleão', 'camaleao',
            'furacão', 'furacao', # Evita 'furar'
            'tubarão', 'tubarao',
            'mão', 'mao', 'pão', 'pao', 'chão', 'chao' # Curtas já barram no len, mas reforçando
        ]
        
        if original in protegidas:
            return original

        base_sem_ao = original[:-2]

        # B. TENTATIVA: AUMENTATIVO MASCULINO (-ÃO -> -O)
        # Prioridade: Substantivo (Portão -> Porta, Prato -> Pratão)
        candidato = base_sem_ao + 'o'
        if palavra_existe(candidato): return candidato

        # C. TENTATIVA: AUMENTATIVO FEMININO (-ÃO -> -A)
        # Prioridade: Substantivo (Muralhão -> Muralha)
        candidato = base_sem_ao + 'a'
        if palavra_existe(candidato): return candidato

        # D. TENTATIVA: DERIVAÇÃO VERBAL (-ÇÃO -> -R / -AR)
        # Só entra aqui se não for aumentativo de nada existente
        if original.endswith('ção'):
            base_sem_cao = original[:-3]
            # Ex: Criação -> Criar
            if palavra_existe(base_sem_cao + 'r'): return base_sem_cao + 'r'
            # Ex: Navegação -> Navegar
            if palavra_existe(base_sem_cao + 'ar'): return base_sem_cao + 'ar'

        # Se falhou em tudo, retorna original (Ex: Balão -> Balo? Bala? Balar? Não.)
        return original

    # --- 2. AÇÃO E RESULTADO (-MENTO) ---
    if original.endswith('mento'):
        base = original[:-5]
        if palavra_existe(base + 'r'): return base + 'r' # Casamento -> Casar
        if palavra_existe(base): return base # Monitoramento -> Monitor

    # --- 3. ADVÉRBIOS (-MENTE) ---
    if original.endswith('mente'):
        base = original[:-5]
        if palavra_existe(base): return base
        if base.endswith('a'):
            candidato = base[:-1] + 'o'
            if palavra_existe(candidato): return candidato

    # --- 4. PROFISSÕES E ÁRVORES (-EIRO / -EIRA / -ISTA) ---
    if original.endswith(('eiro', 'eira')):
        base = original[:-4]
        if palavra_existe(base + 'a'): return base + 'a' # Pedr-a
        if palavra_existe(base + 'o'): return base + 'o' # Livr-o
        if palavra_existe(base + 'e'): return base + 'e' # Leit-e
        if base.endswith('o') and palavra_existe(base[:-1] + 'ão'): 
            return base[:-1] + 'ão' # Limão -> Limoeiro

    if original.endswith('ista'):
        base = original[:-4]
        if palavra_existe(base): return base # Jornal
        if palavra_existe(base + 'a'): return base + 'a' 
        if palavra_existe(base + 'o'): return base + 'o'

    # --- 5. QUALIDADE E ESTADO (-EZ / -EZA / -DADE / -URA / -ISMO) ---
    if original.endswith(('eza', 'ez')):
        tamanho = 3 if original.endswith('eza') else 2
        base = original[:-tamanho]
        if palavra_existe(base + 'o'): return base + 'o' # Bel-o
        if palavra_existe(base): return base # Lucid-ez

    if original.endswith('dade'):
        base = original[:-4]
        if base.endswith('ci'): # Felicidade -> Feliz
            if palavra_existe(base[:-2] + 'z'): return base[:-2] + 'z'
        if base.endswith('n'): # Bondade -> Bom
             if palavra_existe(base[:-1] + 'm'): return base[:-1] + 'm'
        if palavra_existe(base): return base # Leal
        if base.endswith('i') and palavra_existe(base[:-1] + 'il'): return base[:-1] + 'il' # Habilidade

    if original.endswith('ismo'):
        base = original[:-4]
        if palavra_existe(base): return base
        if palavra_existe(base + 'o'): return base + 'o'

    if original.endswith('ura'):
        base = original[:-3]
        if palavra_existe(base + 'o'): return base + 'o'
        if palavra_existe(base + 'e'): return base + 'e'

    # --- 6. ADJETIVOS (-OSO / -AL / -VEL) ---
    if original.endswith(('oso', 'osa')):
        base = original[:-3]
        if palavra_existe(base + 'o'): return base + 'o'
        if palavra_existe(base + 'a'): return base + 'a'

    if original.endswith('al'):
        base = original[:-2]
        if palavra_existe(base + 'o'): return base + 'o'

    if original.endswith('vel'): # Amável -> Amar
        base = original[:-3]
        if base.endswith(('á', 'í', 'e')): 
             mapa = {'á': 'a', 'í': 'i', 'é': 'e'}
             sem_acento = base[:-1] + mapa.get(base[-1], base[-1])
             if palavra_existe(sem_acento + 'r'): return sem_acento + 'r'
             if palavra_existe(sem_acento + 'er'): return sem_acento + 'er'

    return original



# FORMATANDO PALAVRA PARA EXIBIÇÃO NO FRONTEND
def formatar_palavra(palavra, inputUsuario = True):
    """
    Formata a palavra para exibição (primeira letra maiúscula).
    """
    if not(palavra_existe(palavra)) and inputUsuario:
        return False
    
    palavra = padronizar_plural(palavra)
    palavra = padronizar_genero(palavra)
    palavra = padronizar_grau(palavra)
    palavra = padronizar_verbo(palavra)
    palavra = padronizar_derivacoes(palavra)

    return palavra



# TESTES RÁPIDOS
def testar_palavra_existe():
    print("\n\n==================== TESTANDO PALAVRA_EXISTE ====================\n")

    testes = ["casa", "Casa s", "abacaxi", "xpto123"]
    for t in testes:
        resultado = "✅ Existe" if palavra_existe(t) else "❌ Não existe"
        print(f"Palavra '{t}': {resultado}")

def testar_padronizar_plural():
    print("\n\n==================== TESTANDO PADRONIZAR_PLURAL ====================\n")

    lista_testes = [
        # --- Regra 1: -ns -> -m ---
        "nuvens",          # Deve virar: nuvem
        "jardins",         # Deve virar: jardim

        # --- Regra 2: -ões, -ães, -ãos -> -ão ---
        "corações",        # Deve virar: coração
        "pães",            # Deve virar: pão
        "mãos",            # Deve virar: mão

        # --- Regra 3: Variações de -is ---
        "animais",         # (-ais -> -al) animal
        "papéis",          # (-éis -> -el) papel
        "anzóis",          # (-óis -> -ol) anzol
        "barris",          # (-is -> -il) barril

        # --- Regra 4: -es (geralmente após R e Z) ---
        "flores",          # Deve virar: flor
        "luzes",           # Deve virar: luz
        "colheres",        # Deve virar: colher

        # --- Regra 5: Plural Simples (apenas -s) ---
        "casas",           # Deve virar: casa
        "livros",          # Deve virar: livro

        # --- Casos de Controle / Invariáveis ---
        # A função tenta tirar o 's', vê que a base (ex: 'ônibu') não existe
        # e devolve a original.
        "ônibus",          
        "lápis",           
        "tênis",           
        "vírus",           
        
        # --- Caso sem terminação 's' ---
        "computador"       # Retorna imediatamente
    ]

    print(f"{'ENTRADA':<25} | {'SAÍDA PADRONIZADA (PLURAL)'}")
    print("-" * 60)
    for t in lista_testes:
        res = padronizar_plural(t)
        # Indicador visual para facilitar a leitura
        status = "✨ Mudou" if res != t else "  Mantido"
        print(f"{t:<25} | {res:<20} {status}")

def testar_padronizar_genero():
    print("\n\n==================== TESTANDO PADRONIZAR_GENEROL ====================\n")

    lista_testes = [
        # --- Regra 1: -esa -> -ês ---
        "portuguesa",     # Deve virar: português
        "camponesa",      # Deve virar: camponês
        
        # --- Regra 2: -ona -> -ão ---
        "valentona",      # Deve virar: valentão
        "solteirona",     # Deve virar: solteirão
        
        # --- Regra 3: Troca -a por -o ---
        "menina",         # Deve virar: menino
        "gata",           # Deve virar: gato
        "médica",         # Deve virar: médico
        
        # --- Regra 4: Corte do -a (Geralmente terminados em r/z) ---
        "professora",     # Deve virar: professor
        "cantora",        # Deve virar: cantor
        "juíza",          # Deve virar: juiz
        
        # --- Casos de Controle (Substantivos femininos sem par ou objetos) ---
        # O algoritmo tenta "meso" ou "mes", falha na verificação e mantém "mesa"
        "mesa",           
        "cadeira",
        "pessoa",         # Invariável (Sobrecomum)
        "abelha",         # Irregular (masc. é zangão, regra não cobre)
        
        # --- Casos de Retorno Imediato (Não terminam em a/ã) ---
        "menino",
        "ator"
    ]

    print(f"{'ENTRADA':<25} | {'SAÍDA PADRONIZADA (GÊNERO)'}")
    print("-" * 60)
    for t in lista_testes:
        res = padronizar_genero(t)
        # Indicador visual
        status = "✨ Mudou" if res != t else "  Mantido"
        print(f"{t:<25} | {res:<20} {status}")

def testar_padronizar_grau():
    print("\n\n==================== TESTANDO PADRONIZAR_GRAU ====================\n")

    lista_testes = [
        # --- Regra 1: -zinho / -zinha ---
        "pezinho",        # Deve virar: pé
        "florzinha",      # Deve virar: flor
        
        # --- Regra 2: -inho / -inha ---
        "gatinho",        # Tenta base+o: gato
        "casinha",        # Tenta base+a: casa
        "coelhinho",      # Tenta base+o: coelho
        "pastorinho",     # Tenta base pura: pastor
        
        # --- Regra 3: -zão / -zona ---
        "pezão",          # Deve virar: pé
        "cafezão",        # Deve virar: café
        
        # --- Regra 4: -ão / -ona ---
        "gatão",          # Tenta base+o: gato
        "mulherão",       # Tenta base pura: mulher
        "gatona",         # Tenta base+a: gata
        "grandona",       # Tenta base pura ou +a (depende do dicionário)
        
        # --- Regra 5: -ito / -ita ---
        "livrito",        # Tenta base+o: livro
        
        # --- Casos de Controle (Não devem mudar) ---
        "vizinho",        # Palavra normal terminada em inho
        "rainha",         # Palavra normal terminada em inha
        "cão",            # Muito curta (< 4)
        "mão",            # Muito curta (< 4)
        "coracao",        # Falso positivo (se não tiver til) ou palavra base
        "xptozinho"       # Base não existe, deve retornar original
    ]

    print(f"{'ENTRADA':<25} | {'SAÍDA PADRONIZADA (GRAU)'}")
    print("-" * 60)
    for t in lista_testes:
        res = padronizar_grau(t)
        # Adicionei um indicador visual caso a palavra tenha sido alterada
        status = "✨ Mudou" if res != t else "  Mantido"
        print(f"{t:<25} | {res:<20} {status}")

def testar_padronizar_verbo():
    print("\n\n==================== TESTANDO PADRONIZAR_VERBO ====================\n")

    lista_testes = [
        # --- 1. Mesóclise e Ênclise (Hífens) ---
        "mandar-lhe",     # Raiz simples: mandar
        "amá-lo",         # Raiz acentuada á: amar
        "vendê-lo",       # Raiz acentuada é: vender
        
        # --- 2. Gerúndio (-ndo) ---
        "cantando",       # -ando -> cantar
        "correndo",       # -endo -> correr
        "sorrindo",       # -indo -> sorrir
        
        # --- 3. Particípio (-do) ---
        "parado",         # -ado -> parar
        "comido",         # -ido -> tenta comer
        "partido",        # -ido -> tenta partir (se comer falhar)
        
        # --- 4. Pretéritos -RAM ---
        "falaram",        # -aram -> falar
        "beberam",        # -eram -> beber
        "abriram",        # -iram -> abrir
        
        # --- 5. Imperfeito -AVA / -IA ---
        "sonhava",        # -ava -> sonhar
        "corria",         # -ia -> tenta correr
        "partia",         # -ia -> tenta partir
        
        # --- 6. Terminações Curtas (-ou, -eu, -iu, -ei) ---
        "olhou",          # -ou -> olhar
        "moveu",          # -eu -> mover
        "saiu",           # -iu -> sair
        "falei",          # -ei -> falar
        
        # --- 7. Futuro -ÃO ---
        "amarão",         # -arão -> amar
        
        # --- Casos de Controle / Falsos Positivos ---
        "bando",          # Termina em -ando, mas é subst. (palavra_existe('bar')? Não)
        "lindo",          # Termina em -indo
        "dia",            # Termina em -ia
        "falar",          # Já está no infinitivo
        "museu"           # Termina em -eu
    ]

    print(f"{'ENTRADA':<25} | {'SAÍDA PADRONIZADA (VERBO)'}")
    print("-" * 60)
    for t in lista_testes:
        res = padronizar_verbo(t)
        status = "✨ Mudou" if res != t else "  Mantido"
        print(f"{t:<25} | {res:<20} {status}")

def testar_formatar_palavra_completo():
    print("\n" + "="*80)
    print(f"{'TESTE UNIFICADO: FORMATAR_PALAVRA (PIPELINE COMPLETO)':^80}")
    print("="*80 + "\n")

    # Lista de Tuplas: (Entrada, Saída Esperada)
    lista_testes = [
        # --- PLURAL (Padronizar Plural) ---
        ("nuvens", "nuvem"),
        ("jardins", "jardim"),
        ("corações", "coração"),
        ("pães", "pão"),
        ("mãos", "mão"),
        ("animais", "animal"),
        ("papéis", "papel"),
        ("anzóis", "anzol"),
        ("barris", "barril"),
        ("flores", "flor"),
        ("luzes", "luz"),
        ("colheres", "colher"),
        ("casas", "casa"),
        ("livros", "livro"),
        ("ônibus", "ônibus"),   # Invariável
        ("lápis", "lápis"),     # Invariável
        ("tênis", "tênis"),     # Invariável
        ("vírus", "vírus"),     # Invariável
        ("computador", "computador"),

        # --- GÊNERO (Padronizar Gênero) ---
        ("portuguesa", "português"),
        ("camponesa", "camponês"),
        ("valentona", "valentão"),
        ("solteirona", "solteirão"),
        ("menina", "menino"),
        ("gata", "gato"),
        ("médica", "médico"),
        ("professora", "professor"),
        ("cantora", "cantor"),
        ("juíza", "juiz"),
        ("mesa", "mesa"),       # Objeto fem.
        ("cadeira", "cadeira"), # Objeto fem.
        ("pessoa", "pessoa"),   # Sobrecomum
        ("abelha", "abelha"),   # Irregular
        ("menino", "menino"),   # Já masc.
        ("ator", "ator"),       # Já masc.

        # --- GRAU (Padronizar Grau) ---
        ("pezinho", "pé"),
        ("florzinha", "flor"),
        ("gatinho", "gato"),    # Grau + Gênero implícito
        ("casinha", "casa"),
        ("coelhinho", "coelho"),
        ("pastorinho", "pastor"),
        ("pezão", "pé"),
        ("cafezão", "café"),
        ("gatão", "gato"),
        ("mulherão", "mulher"),
        ("gatona", "gata"),     # Nota: Pode virar Gato se passar pelo gênero depois
        ("grandona", "grandona"), # Depende se 'grande' está no mock
        ("livrito", "livro"),
        ("vizinho", "vizinho"), # Falso positivo
        ("rainha", "rainha"),   # Falso positivo
        ("cão", "cão"),         # Curta
        ("coracao", "coracao"), # Sem acento/original
        ("xptozinho", "xptozinho"),

        # --- VERBOS (Padronizar Verbos) ---
        ("mandar-lhe", "mandar"),
        ("amá-lo", "amar"),
        ("vendê-lo", "vender"),
        ("cantando", "cantar"),
        ("correndo", "correr"),
        ("sorrindo", "sorrir"),
        ("parado", "parar"),
        ("comido", "comer"),
        ("partido", "partir"),
        ("falaram", "falar"),
        ("beberam", "beber"),
        ("abriram", "abrir"),
        ("sonhava", "sonhar"),
        ("corria", "correr"),
        ("partia", "partir"),
        ("olhou", "olhar"),
        ("moveu", "mover"),
        ("saiu", "sair"),
        ("falei", "falar"),
        ("amarão", "amar"),
        ("bando", "bando"),     # Subst.
        ("lindo", "lindo"),     # Adj.
        ("dia", "dia"),         # Subst.
        ("falar", "falar"),     # Infinitivo
        ("museu", "museu"),     # Subst.

        # --- DERIVAÇÕES (Padronizar Derivações) ---
        ("rapidamente", "rápido"), # Volta ao masc.
        ("felizmente", "feliz"),
        ("pedreiro", "pedra"),
        ("limoeiro", "limão"),
        ("dentista", "dentista"),
        ("jornalista", "jornal"),
        ("beleza", "belo"),
        ("rapidez", "rápido"),
        ("felicidade", "feliz"),
        ("bondade", "bom"),
        ("altura", "alto"),
        ("casamento", "casar"),
        ("criação", "criar"),
        ("navegação", "navegar"),
        ("famoso", "fama"),
        ("mundial", "mundo"),
        ("amável", "amar"),
        
        # --- COMBINAÇÕES COMPLEXAS (Teste de Fogo) ---
        ("gatinhas", "gato"),     # Plural -> Gatinha -> Grau -> Gata -> Gênero -> Gato
        ("amavam", "amar"),       # Verbo imperfeito
        ("casinhas", "casa"),     # Plural -> Grau
        ("rapidamente", "rápido")
    ]

    print(f"{'ENTRADA':<20} | {'RESULTADO':<15} | {'STATUS':<10}")
    print("-" * 60)

    contador = 0

    for entrada, esperado in lista_testes:
        resultado = formatar_palavra(entrada)
        
        # Lógica de validação
        if resultado == esperado:
            status = "✅ OK"
        else:
            contador += 1
            status = f"❌ Deu: {resultado}"
            
        print(f"{entrada:<20} | {esperado:<15} | {status}")
    
    print(contador, "testes falharam." if contador > 0 else "Todos os testes passaram com sucesso!")

def teste_unitario():
    print("\n" + "="*80)
    print(f"{'TESTE UNIFICADO: FORMATAR_PALAVRA (PIPELINE COMPLETO)':^80}")
    print("="*80 + "\n")
    
    print("PADRONIZAR_PLURAL:     ", padronizar_plural("casas"))
    print("PADRONIZAR_GÊNERO:     ", padronizar_genero("casa"))
    print("PADRONIZAR_GRAU:       ", padronizar_grau("casa"))
    print("PADRONIZAR_VERBO :     ", padronizar_verbo("casa"))
    print("PADRONIZAR_DERIVAÇÕES: ", padronizar_derivacoes("casa"))

if __name__ == "__main__":
    # testar_palavra_existe()
    # testar_padronizar_plural()
    # testar_padronizar_genero()
    # testar_padronizar_grau()
    # testar_padronizar_verbo()
    # testar_padronizar_derivacoes()
    # testar_formatar_palavra_completo()
    # teste_unitario()
    pass