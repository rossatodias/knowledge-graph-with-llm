import os
from settings import (
    GOOGLE_API_KEY, 
    NEO4J_URI, 
    NEO4J_USERNAME, 
    NEO4J_PASSWORD)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_core.prompts import PromptTemplate

# Verifica se as variáveis de ambiente foram carregadas corretamente
if not GOOGLE_API_KEY or not NEO4J_URI:
    print("Erro: Variáveis de ambiente não encontradas no arquivo .env (settings.py).")
    exit()

# --- 1. Configurações ---

# Configura o LLM do Google
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0)

print("LLM configurado.")

# --- 2. Conectar ao Neo4j e obter esquema (LangChain faz isso internamente para GraphCypherQAChain) ---
try:
    graph = Neo4jGraph(
        url=NEO4J_URI,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
        enhanced_schema=False)

    # Teste de conexão e obtenção do esquema
    print("Schema do Grafo:")
    print(graph.schema)
    print("Conectado ao Neo4j com sucesso!")

    # Popula o banco de dados com os dados da BigCo
    graph.query("""
    MERGE (a:Person {name:'Anna'})
    MERGE (b:Person {name:'Barbara'}) 
    MERGE (c:Person {name:'Carol'})
    MERGE (d:Person {name:'Dawn'})
    MERGE (e:Person {name:'Elizabeth'})
    MERGE (j:Person {name:'Jill'})
    MERGE (m:Person {name:'Martin'})
    MERGE (p:Person {name:'Pramod'})
                
    MERGE (bigco:Company {name:'BigCo'})
                
    MERGE (book1:Book {title:'Refactoring'})
    MERGE (book2:Book {title:'NoSQL Distilled'})
    MERGE (book3:Book {title:'Database Refactoring'})
                
    MERGE (topic1:Topic {name:'Databases'})
        """)
    
    # Cria relacionamentos entre os nós
    graph.query("""
    MATCH (anna:Person {name:'Anna'}), 
        (barbara:Person {name:'Barbara'}), 
        (carol:Person {name:'Carol'}), 
        (bigco:Company {name:'BigCo'})
    MERGE (anna)-[:employee]->(bigco)
    MERGE (barbara)-[:employee]->(bigco)
    MERGE (carol)-[:employee]->(bigco)
        """)

    graph.query("""
    MATCH (anna:Person {name:'Anna'}), 
        (barbara:Person {name:'Barbara'}), 
        (carol:Person {name:'Carol'}), 
        (dawn:Person {name:'Dawn'}), 
        (elizabeth:Person {name:'Elizabeth'}), 
        (jill:Person {name:'Jill'}), 
        (martin:Person {name:'Martin'}), 
        (pramod:Person {name:'Pramod'})
    MERGE (barbara)-[:friend]->(anna)
    MERGE (barbara)-[:friend]->(carol)
    MERGE (barbara)-[:friend]->(elizabeth)
    MERGE (carol)-[:friend]->(dawn)
    MERGE (dawn)-[:friend]->(jill)
    MERGE (elizabeth)-[:friend]->(jill)
    MERGE (pramod)-[:friend]-(martin)
        """)

    graph.query("""
    MATCH (anna:Person {name:'Anna'}), 
        (barbara:Person {name:'Barbara'}), 
        (carol:Person {name:'Carol'}), 
        (dawn:Person {name:'Dawn'}), 
        (elizabeth:Person {name:'Elizabeth'}), 
        (refactoring:Book {title:'Refactoring'}), 
        (nosql:Book {title:'NoSQL Distilled'})
    MERGE (anna)-[:likes]->(refactoring)
    MERGE (barbara)-[:likes]->(refactoring)
    MERGE (barbara)-[:likes]->(nosql)
    MERGE (carol)-[:likes]->(nosql)
    MERGE (dawn)-[:likes]->(nosql)
    MERGE (elizabeth)-[:likes]->(nosql)
        """)

    graph.query("""
    MATCH (martin:Person {name:'Martin'}), 
        (pramod:Person {name:'Pramod'}), 
        (refactoring:Book {title:'Refactoring'}), 
        (nosql:Book {title:'NoSQL Distilled'}), 
        (dbref:Book {title:'Database Refactoring'})
    MERGE (refactoring)-[:author]->(martin)
    MERGE (nosql)-[:author]->(martin)
    MERGE (dbref)-[:author]->(pramod)
    MERGE (nosql)-[:author]->(pramod)
        """)

    graph.query("""
    MATCH (nosql:Book {title:'NoSQL Distilled'}), 
        (dbref:Book {title:'Database Refactoring'}), 
        (databases:Topic {name:'Databases'})
    MERGE (nosql)-[:category]->(databases)
    MERGE (dbref)-[:category]->(databases)
        """)

    print("Dados carregados/verificados.")

except Exception as e:
    print(f"Erro ao conectar ou popular o Neo4j: {e}")
    graph = None
    exit()


# --- 3. Construir a Cadeia de NL para Cypher (GraphCypherQAChain simplifica isso) ---
CYPHER_GENERATION_TEMPLATE = """
Você é um expert em Neo4j e Cypher. Dada uma pergunta em linguagem natural e um esquema de grafo,
gere uma query Cypher para responder à pergunta. NÃO RESPONDA A PERGUNTA, apenas gere a query.
Não use exemplos na query, apenas o que for necessário com base na pergunta e no esquema.
Não coloque a query dentro de blocos de código markdown. Retorne apenas a query Cypher.

Esquema do Grafo:
{schema}

Pergunta: {question}
Query Cypher:
"""
CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
)

# Prompt para gerar a resposta final com base nos resultados da query
QA_TEMPLATE = """Você é um assistente que ajuda a responder perguntas baseadas em dados de grafos.
O "Contexto" abaixo contém os resultados exatos obtidos de uma consulta ao banco de dados feita especificamente para responder à "Pergunta".
Não questione se o contexto pertence à pergunta. Apenas transforme os dados do contexto em uma resposta natural.
Se o contexto estiver vazio (lista vazia `[]`), diga que não encontrou a resposta.

Contexto:
{context}

Pergunta: {question}
Resposta útil:"""
QA_PROMPT = PromptTemplate(input_variables=["context", "question"], template=QA_TEMPLATE)

# --- 4, 5, 6: Executar Query, Formatar, Gerar Resposta (tudo encapsulado pela cadeia) ---
if graph:
    try:
        # `validate_cypher=True` (padrão) pode tentar corrigir pequenas falhas na query Cypher gerada usando o LLM.
        # `return_intermediate_steps=True` permite ver a query Cypher gerada.
        chain = GraphCypherQAChain.from_llm(
            graph=graph,
            llm=llm,
            cypher_prompt=CYPHER_GENERATION_PROMPT, # Opcional, para customizar
            qa_prompt=QA_PROMPT,                   # Opcional, para customizar
            validate_cypher=True,
            verbose=True, # Mostra os passos intermediários, incluindo a query Cypher
            return_intermediate_steps=True,
            allow_dangerous_requests=True,
            #top_k=5 # Limita o número de resultados do grafo a serem passados como contexto
        )
        print("Cadeia GraphCypherQAChain criada.")
    except Exception as e:
        print(f"Erro ao criar a GraphCypherQAChain: {e}")
        chain = None
        exit()


    # --- 7. Testar a Cadeia ---
    questions = [
        "Quem são os funcionários da BigCo?",
        "Quais são os livros que os funcionários da BigCo gostam?",
        "Quem são os autores dos livros que os funcionários da BigCo gostam?",
        "Quem gosta de livro da categoria Databases?",
        "Quais são os amigos de Barbara?",
        "Existe algum livro chamado 'Innovate Ltd'?" # Pergunta que não deve encontrar dados
    ]

    if chain:
        for question_text in questions:
            print(f"\n\n Perguntando: {question_text}")
            try:
                result = chain.invoke({"query": question_text})

                print("\n> Query Cypher Gerada (passo intermediário):")
                if result.get("intermediate_steps") and len(result["intermediate_steps"]) > 0:
                    print(result["intermediate_steps"][0].get("query", "Não disponível")) # A query está no primeiro passo
                else:
                    print("Query intermediária não encontrada.")

                print("\n> Contexto do Grafo (passo intermediário):")
                if result.get("intermediate_steps") and len(result["intermediate_steps"]) > 0:
                     print(result["intermediate_steps"][0].get("context", "Não disponível")) # O contexto está no primeiro passo

                print(f"\n> Resposta Final: {result['result']}")

            except Exception as e:
                print(f"Erro ao processar a pergunta '{question_text}': {e}")
                import traceback
                traceback.print_exc()
    else:
        print("A cadeia não foi inicializada devido a erros anteriores.")

else:
    print("A conexão com o Neo4j não foi estabelecida. Encerrando.")