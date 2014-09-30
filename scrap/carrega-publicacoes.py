from py2neo import neo4j,cypher
import sys
import time

from bs4 import BeautifulSoup
from urllib.request import urlopen

sys.path.append("C:\\devel\\python\\scrap")

from searchlattes import searchCV
from scraplattes import scraplattes
import parselattes2

print("Iniciando carga da base a partir de web")

# INICIO DA CARGA DOS AUTORES

print("Iniciando listagem de professores")

#TODO: acho que tem como obter um session fo graph_db
graph_db = neo4j.GraphDatabaseService()
session = cypher.Session("http://localhost:7474")

# Prepara a traducao de acentos para evitar problemas na busca
charOrigem="áâãéêíóôõú"
charDestino="aaaeeiooou"
tabelaTraducao= str.maketrans(charOrigem,charDestino)
#

def carrega_professor():
    soup = BeautifulSoup(urlopen("http://www.cic.unb.br/index.php?option=com_qcontacts&view=category&catid=0&Itemid=10").read())

    cont = 1
    professores = soup.find_all(attrs={"class": "category"})
    for prof in professores:
        tx = session.create_transaction()
        cont +=1

        nomeProfessor = prof.text.translate(tabelaTraducao)
        # Tenta resolver o problema das abreviações - Não funciona pois estamos procurando com aspas
        nomes = nomeProfessor.split()
        #for nome in nomes:
            #if nome.find('.') != -1:
            #    nomeProfessor=nomeProfessor.replace(nome+" ","")
        nomeProfessor = nomeProfessor.strip()
        print("Professor: %s" % nomeProfessor)
        tx.append("MERGE (a:Author {name:'%s'}) RETURN a" % nomeProfessor)
        tx.execute()
        tx.commit()

#FIM DA CARGA DOS AUTORES

def carrega_artigos():
    # INICIO DA CARGA DOS ARTIGOS
    queryAuthors = "MATCH (a:Author) RETURN a.name"
    professors,metadata = cypher.execute(graph_db, queryAuthors)

    for i in professors:
        profName = str(i[0]).strip()
        print("Pesquisando professor: " + profName)
    
        searchRes = searchCV(profName)    
        curriculums =  scraplattes(searchRes)
        
        if curriculums.__len__() > 1:
            print("Mais de um curriculo para o professor: " + profName)
        for curr in curriculums:
            nomeCitacoes,artigos = parselattes2.listaCitacoes(curr)
            # Atualiza os nomes usados para citação
            try:
                nodeAuthor,metadata = cypher.execute(graph_db, 
                                                     "MATCH (n:Author {name:'%s'}) SET n.citation = '%s',n.keylattes = '%s' RETURN n" %(profName, nomeCitacoes,curr))
            except Exception:
                print("Erro ao inserir nomes usados em citacao para pesquisador " + profName)
                        
            for artigo in artigos:
                #
                # TODO: É preciso tratar as aspas no nome das propriedades antes de
                # inserir o artigo no grafo
                #
                artNode, = graph_db.create(artigo)
                artNode.add_labels("Article")            
                if nodeAuthor and artNode:
                    try:
                        cypher.execute(graph_db, "MATCH (n:Author {name:'%s'}),(p:Article {titulo:'%s'}) MERGE (n)<-[r:AUTHORING]->(p)" % (profName, artigo["titulo"].replace("'","´")))
                    except Exception:
                        print("Erro ao criar relacionamento entre "+profName+" e " + artigo["issn"])
            # Esse sleep é para diminuir a frequencia de acesso ao lattes
            #time.sleep(2)

#carrega_professor()            
carrega_artigos()
print("FIM")