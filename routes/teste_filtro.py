import bisect
import os

# SIGLAS VÁLIDAS
WHITELIST_CURTAS = {
    "api", "app", "web", "bot", "bug", "dev", "git", "hub", "net", 
    "sql", "ssl", "ssh", "tcp", "udp", "vpn", "wan", "lan", "dns",
    "mac", "ip",  "cpu", "gpu", "ram", "rom", "ssd", "hdd", "usb", 
    "led", "lcd", "iot", "xml", "json", "jar", "zip", "rar", "exe",
    "bin", "hex", "bit", "byte", "log", "npm", "pip", "kde", "gnome",
    "ux",  "ui",  "seo", "aws", "gcp", "azure", "poo", "mvc", "dao"
}

# DEFINIÇÃO DO CAMINHO DO ARQUIVO DE PALAVRAS
DIRETORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
CAMINHO_ARQUIVO = os.path.join(DIRETORIO_SCRIPT, "..", "base_palavras", "com_acento.txt")
CAMINHO_ARQUIVO = os.path.normpath(CAMINHO_ARQUIVO)


# CARREGAMENTO DO BANCO DE DADOS
try:
    with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as f:
        # Carrega removendo espaços e quebras de linha
        TABELA_PALAVRAS_ORDENADAS = [linha.strip() for linha in f]
    print(f"📚 Tabela de dados carregada: {len(TABELA_PALAVRAS_ORDENADAS)} palavras.")
except FileNotFoundError:
    print(f"❌ ERRO CRÍTICO: Arquivo não encontrado no caminho:\n{CAMINHO_ARQUIVO}")
    TABELA_PALAVRAS_ORDENADAS = []




# BUSCA BINÁRIA NA TABELA DE PALAVRAS
def palavra_existe(palavra):
    """
    Verifica se a palavra existe no banco de dados usando Busca Binária.
    Complexidade: O(log N) - Extremamente rápido.
    """
    if not TABELA_PALAVRAS_ORDENADAS:
        return False
        
    # Normaliza a entrada: tudo minúsculo e sem espaços nas pontas
    palavra = palavra.lower().strip()
    
    # O bisect_left encontra a posição de inserção para manter a ordem
    index = bisect.bisect_left(TABELA_PALAVRAS_ORDENADAS, palavra)
    
    # Se o índice retornado estiver dentro da lista e a palavra for igual, ACHAMOS!
    if index < len(TABELA_PALAVRAS_ORDENADAS) and TABELA_PALAVRAS_ORDENADAS[index] == palavra:
        return palavra
        
    return False

# TESTES RÁPIDOS
def testar_palavra_existe():
    print("\n\n==================== TESTANDO PALAVRA_EXISTE ====================\n")

    testes = ["casa", "Casa s", "abacaxi", "xpto123"]
    for t in testes:
        resultado = "✅ Existe" if palavra_existe(t) else "❌ Não existe"
        print(f"Palavra '{t}': {resultado}")

if __name__ == "__main__":
    # testar_palavra_existe()

    pass