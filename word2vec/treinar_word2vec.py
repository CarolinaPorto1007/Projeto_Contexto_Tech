from gensim.models import Word2Vec
from gensim.utils import simple_preprocess
import os

# === 1) Verifica se o corpus existe ===
if not os.path.exists("corpus_tecnologia.txt"):
    print("❌ ERRO: 'corpus_tecnologia.txt' não encontrado!")
    exit()

print("📖 Carregando corpus...")
with open("corpus_tecnologia.txt", "r", encoding="utf8") as f:
    linhas = f.readlines()

# === 2) Tokeniza ===
print("🔤 Preparando dados...")
sentencas = [simple_preprocess(linha) for linha in linhas]

# === 3) Treina o modelo ===
print("🧠 Treinando modelo Word2Vec...")
modelo = Word2Vec(
    sentences=sentencas,
    vector_size=300,
    window=8,
    min_count=3,
    sg=1,
    workers=4,
    epochs=20
)

# === 4) Cria pasta word2vec caso não exista ===
if not os.path.exists("word2vec"):
    os.makedirs("word2vec")
    print("📁 Pasta 'word2vec' criada.")

# === 5) Salvando o arquivo correto ===
print("💾 Salvando modelo...")
modelo.wv.save("word2vec/word2vec_tecnologia.kv")

print("✅ Terminado! Arquivo salvo em: word2vec/word2vec_tecnologia.kv")
