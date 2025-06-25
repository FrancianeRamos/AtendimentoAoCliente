# Importando as bibliotecas necessárias
import random   # Biblioteca padrão do Python para gerar escolhas aleatórias, usada para respostas alternativas
import requests # Biblioteca para fazer requisições HTTP, usada para buscar informações externas na internet
# Importando as classes principais do ChatterBot
from chatterbot import ChatBot  # Classe principal para criar o chatbot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer  # Treinadores para ensinar o bot com corpus e listas personalizadas

# Função para buscar informações externas usando a API do DuckDuckGo
# Caso o chatbot não saiba responder, ele tenta buscar uma resposta na internet
def buscar_info_duckduckgo(pergunta):
    # URL da API pública do DuckDuckGo Instant Answer
    url = "https://api.duckduckgo.com/"
    # Parâmetros da requisição para obter resposta em JSON, sem HTML e sem ambiguidades
    params = {
        "q": pergunta,           # Pergunta feita pelo usuário
        "format": "json",        # Formato da resposta
        "no_html": 1,            # Remove tags HTML da resposta
        "skip_disambig": 1       # Ignora respostas ambíguas
    }
    # Fazendo a requisição GET para a API
    resposta = requests.get(url, params=params)
    # Verifica se a requisição foi bem-sucedida (código 200)
    if resposta.status_code == 200:
        try:
            # Tenta converter a resposta para JSON
            dados = resposta.json()
            # Busca o texto principal da resposta (campo "AbstractText")
            texto = dados.get("AbstractText")
            if texto:
                # Retorna o texto encontrado, se houver
                return texto
        except Exception:
            # Em caso de erro na conversão ou acesso ao JSON, retorna None
            return None
    # Se a requisição não foi bem-sucedida ou não encontrou resposta, retorna None
    return None

# Criando uma instância do chatbot para atendimento ao cliente de uma loja de sapatos
# Configura o armazenamento, banco de dados e adaptadores de lógica
chatbot = ChatBot(
    "Atendimento_Sapatos",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",  # Define o tipo de armazenamento
    database_uri="sqlite:///database.sqlite3",               # Caminho do banco de dados SQLite
    logic_adapters=[
        "chatterbot.logic.BestMatch",                       # Melhor correspondência de resposta
        "chatterbot.logic.MathematicalEvaluation",          # Avaliação matemática
        "chatterbot.logic.TimeLogicAdapter"                 # Respostas relacionadas a horário
    ],
    read_only=False                                         # Permite que o bot aprenda durante a execução
)

# Lista de perguntas e respostas personalizadas para o negócio de sapatos
conversas_personalizadas = [
    ["Quais sapatos vocês vendem?", "Vendemos tênis, botas, sandálias e sapatos sociais."],
    ["Quais tamanhos estão disponíveis?", "Temos tamanhos do 34 ao 44. Caso tenha dúvidas, consulte nossa tabela de medidas!"],
    ["Quanto tempo demora a entrega?", "O prazo de entrega varia entre 5 a 10 dias úteis, dependendo da sua região."],
    ["Como faço uma troca?", "Para trocas, você pode solicitar através do nosso site ou entrar em contato com nosso suporte."],
    ["Quais são as formas de pagamento?", "Aceitamos cartões de crédito, débito, boleto bancário e PIX."],
    ["Vocês têm desconto para compras em quantidade?", "Sim, oferecemos descontos para compras acima de 3 pares. Consulte nosso site para mais detalhes."],
    ["Vocês têm loja física?", "Sim, temos lojas em várias cidades. Consulte nosso site para encontrar a mais próxima de você."],
    ["Vocês fazem entrega internacional?", "Atualmente, fazemos entregas apenas no Brasil. Estamos trabalhando para expandir nossos serviços."],
    ["Como posso rastrear meu pedido?", "Você pode rastrear seu pedido através do link enviado por e-mail após a confirmação da compra."],
    ["Vocês têm garantia nos produtos?", "Sim, todos os nossos produtos têm garantia de 90 dias contra defeitos de fabricação."],
    ["Vocês aceitam devoluções?", "Sim, aceitamos devoluções em até 7 dias após o recebimento do produto, desde que esteja na embalagem original e sem uso."],
    ["Quais são os horários de atendimento?", "Nosso horário de atendimento é de segunda a sexta-feira, das 9h às 18h."],
    ["Vocês têm programa de fidelidade?", "Sim, temos um programa de fidelidade onde você acumula pontos a cada compra e pode trocar por descontos ou produtos."],
    ["Como posso entrar em contato com o suporte?", "Você pode entrar em contato conosco pelo e-mail"]
]

# Treinando o chatbot com as conversas personalizadas
list_trainer = ListTrainer(chatbot)
for conversa in conversas_personalizadas:
    list_trainer.train(conversa)

# Mensagem de resposta alternativa para perguntas que não foram treinadas
def resposta_padrao():
    sugestoes = [
        "Poderia reformular sua pergunta?",
        "Ainda não tenho essa informação, mas posso procurar mais!",
        "Você quer saber sobre tamanhos, entrega ou formas de pagamento?"
    ]
    return random.choice(sugestoes)

# Treinando o chatbot com corpus de português para interações mais gerais
corpus_trainer = ChatterBotCorpusTrainer(chatbot)
corpus_trainer.train("chatterbot.corpus.portuguese")

# Loop principal do chatbot para interação com o cliente
try:
    while True:
        pergunta = input("Você: ")
        resposta = chatbot.get_response(pergunta)

        # Se a confiança for baixa, busca nas APIs externas
        if resposta.confidence < 0.3: 
            resposta = buscar_info_duckduckgo(pergunta)
        
        print("Bot:", resposta if resposta else resposta_padrao())
except KeyboardInterrupt:
    print("\nEncerrando o chatbot.")
