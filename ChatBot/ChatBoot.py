import random
import requests
import urllib.parse
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer

# Função para buscar informações na API DuckDuckGo
def buscar_info_duckduckgo(pergunta):
    url = "https://api.duckduckgo.com/"
    params = {
        "q": pergunta,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1
    }
    resposta = requests.get(url, params=params)
    if resposta.status_code == 200:
        try:
            dados = resposta.json()
            texto = dados.get("AbstractText")
            if texto:
                return texto
        except Exception:
            return None
    return None

# Função para buscar informações na API Wikipedia
def buscar_info_wikipedia(pergunta):
    pergunta_formatada = urllib.parse.quote(pergunta.replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{pergunta_formatada}"
    resposta = requests.get(url)

    if resposta.status_code == 200:
        dados = resposta.json()
        return dados.get("extract", "Não encontrei informações sobre isso.")
    
    return f"Erro na API Wikipedia: {resposta.status_code}"

# Testando a função
print(buscar_info_wikipedia("Brasil"))

# Função que verifica ambas as APIs antes de dar uma resposta
def buscar_info(pergunta):
    resposta_duckduckgo = buscar_info_duckduckgo(pergunta)
    if resposta_duckduckgo:
        return resposta_duckduckgo
    
    resposta_wikipedia = buscar_info_wikipedia(pergunta)
    if resposta_wikipedia:
        return resposta_wikipedia
    
    return "Não encontrei informações sobre isso."

# Criando o chatbot
chatbot = ChatBot(
    "MeuBot",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    database_uri="sqlite:///database.sqlite3",
    logic_adapters=[
        "chatterbot.logic.BestMatch",
        "chatterbot.logic.MathematicalEvaluation",
        "chatterbot.logic.TimeLogicAdapter"
    ],
    read_only=False
)


#Qual montanha é considerada a mais alta do mundo?|Monte Everest (8.848 m).
#Em qual continente fica o Deserto do Saara?|África.
#Qual é o oceano mais profundo do planeta?|Oceano Pacífico (Fossa das Marianas).
#Qual é a capital do Japão?|Tóquio.


# Carregando dados de treinamento personalizados
conversas_personalizadas = []
try:
    with open("C:/Users/franc/OneDrive/Documentos/Papinho/ChatBot/conversas.txt", encoding="utf-8") as f:
        for linha in f:
            partes = linha.strip().split("|", 1)
            if len(partes) == 2:
                conversas_personalizadas.append([partes[0], partes[1]])
except FileNotFoundError:
    print("Arquivo 'conversas.txt' não encontrado. Nenhuma conversa personalizada será carregada.")

# Treinando com conversas personalizadas
list_trainer = ListTrainer(chatbot)
for conversa in conversas_personalizadas:
    list_trainer.train(conversa) 

# Mensagem de resposta alternativa
def resposta_padrao():
    sugestoes = [
        "Poderia reformular sua pergunta?",
        "Ainda não tenho essa informação, mas posso procurar mais!",
        "Você quer saber sobre [tema similar]?"
    ]
    return random.choice(sugestoes)

# Treinando com corpus de conhecimento geral
corpus_trainer = ChatterBotCorpusTrainer(chatbot)
corpus_trainer.train("chatterbot.corpus.portuguese")

# Loop principal do chatbot
try:
    while True:
        pergunta = input("Você: ")
        resposta = chatbot.get_response(pergunta)
        
        # Se a confiança for baixa, busca nas APIs externas
        if resposta.confidence < 0.3: 
            resposta = buscar_info(pergunta)
        
        print("Bot:", resposta)
except KeyboardInterrupt:
    print("\nEncerrando o chatbot.")