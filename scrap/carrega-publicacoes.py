from py2neo import neo4j,cypher
import sys
import time

from bs4 import BeautifulSoup
from urllib.request import urlopen

from searchlattes import searchCV
from scraplattes import scraplattes
import parselattes2

print("Iniciando carga da base a partir de web")

#TODO: acho que tem como obter um session fo graph_db
#graph_db = neo4j.GraphDatabaseService("http://grafocolaboracao:1CmvfXNcEzyT78FwUHVU@grafocolaboracao.sb02.stations.graphenedb.com:24789/db/data/")
graph_db = neo4j.GraphDatabaseService()
#session = cypher.Session("http://grafocolaboracao:1CmvfXNcEzyT78FwUHVU@grafocolaboracao.sb02.stations.graphenedb.com:24789/db/data/")
session = cypher.Session()

# Prepara a traducao de acentos para evitar problemas na busca
charOrigem="áâãéêíóôõú"
charDestino="aaaeeiooou"
tabelaTraducao= str.maketrans(charOrigem,charDestino)


def carrega_professor():
    '''
    Pega a lista de nomes e os insere no grafo com o rótulo Author
    '''
    soup = BeautifulSoup(urlopen("http://www.cic.unb.br/index.php?option=com_qcontacts&view=category&catid=0&Itemid=10").read())

    cont = 1
    professores = soup.find_all(attrs={"class": "category"})
    for prof in professores:
        tx = session.create_transaction()
        cont +=1

        nomeProfessor = prof.text.translate(tabelaTraducao)
        nomes = nomeProfessor.split()
        
        nomeProfessor = nomeProfessor.strip()
        print("Professor: %s" % nomeProfessor)
        tx.append("MERGE (a:Author {name:'%s'}) RETURN a" % nomeProfessor)
        tx.execute()
        tx.commit()

    print("Author list loaded")

def carrega_artigos():
    '''
    Lista os vértices com rótulo Author pela propriedade name e faz a busca
    no lattes atualizando os nomes usados nas citações carrega vértices com
    o rótulo Article
    '''
    queryAuthors = "MATCH (a:Author) WHERE (a.keylattes is null) RETURN a.name"
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
            
            print("Nomes usados nas citacoes %s" %nomeCitacoes)
            nomeCitacoes = nomeCitacoes.replace("'",'"')
            # Atualiza os nomes usados para citação
            try:
                nodeAuthor, = cypher.execute(graph_db, 
                                                     '''MATCH (n:Author {name:'%s'})
    SET n.citation = '%s',n.keylattes = '%s',n.timestamp = timestamp()
    RETURN n''' %(profName, nomeCitacoes,curr))
            except Exception:
                print("Erro ao inserir nomes usados em citacao para pesquisador " + profName)
                        
            for artigo in artigos:                
                articleAsString = str()
                for key in artigo.keys():
                    articleAsString += "p." + key.replace('-','_') + " = '" +artigo[key] + "', "
                                   #(artigo["titulo"], articleAsString))
                try:
                    cypher.execute(graph_db,
                                   "MERGE (p:Article {titulo:'%s'}) ON CREATE SET %s p.lastUpdate = timestamp() RETURN p" %
                                   (artigo["titulo"], articleAsString)
                                   )
                except Exception as e:
                    print("Erro ao inserir artigo: ", e)
       
#carrega_professor()            
carrega_artigos()
print("FIM")
