from py2neo import Graph, Node
import sys
import time
import json

from bs4 import BeautifulSoup
from urllib.request import urlopen

from searchlattes import searchCV
import parselattes2

print("Iniciando carga da base a partir de web")

#TODO: acho que tem como obter um session fo graph_db
#graph_db = neo4j.GraphDatabaseService("http://grafocolaboracao:1CmvfXNcEzyT78FwUHVU@grafocolaboracao.sb02.stations.graphenedb.com:24789/db/data/")
#session = cypher.Session("http://grafocolaboracao:1CmvfXNcEzyT78FwUHVU@grafocolaboracao.sb02.stations.graphenedb.com:24789/db/data/")
graph_db = Graph()


# Prepara a traducao de acentos para evitar problemas na busca
charOrigem="áâãéêíóôõú"
charDestino="aaaeeiooou"
tabelaTraducao= str.maketrans(charOrigem,charDestino)

def loadFromFile():
    sqlFile=open("queryMergePRofessors.sql","r")
    while True:
        line = sqlFile.readline()
        if not line:
            break
        professors = graph_db.cypher.execute(graph_db, line)
    
def loadFromJSON(jsonfile):
    if not jsonfile:
        return
    print("Loading data from %s" %jsonfile)
    jsondata=''
    try:
        f = open(jsonfile,'r')
        jsondata = json.load(f)
        f.close()
    except IOError as e:
        print("Error loading json file")
        sys.exit(1)
    
    for entry in jsondata:
        print("Loading author: %s" % entry['name'])
        node = Node("Author", name=entry['name'], email=entry['email'], lattesurl=entry['lattesurl'])
        graph_db.create(node)
        
    print("All list have been processed")
        
def carrega_professor():
    '''
    Pega a lista de nomes e os insere no grafo com o rótulo Author
    '''
    soup = BeautifulSoup(urlopen("http://www.cic.unb.br/index.php?option=com_qcontacts&view=category&catid=0&Itemid=10").read())

    cont = 1
    professores = soup.find_all(attrs={"class": "category"})
    professorsFile = open("queryMergeProfessors-raw.sql","w")
    for prof in professores:
        #tx = session.create_transaction()
        cont +=1

        nomeProfessor = prof.text.translate(tabelaTraducao)
        nomes = nomeProfessor.split()
        
        nomeProfessor = nomeProfessor.strip()
        #print("Professor: %s" % nomeProfessor)
        #tx.append("MERGE (a:Author {name:'%s'}) RETURN a" % nomeProfessor)
        professorsFile.write("MERGE (a:Author {name:'%s'}) RETURN a\n" % nomeProfessor)
        #tx.execute()
        #tx.commit()
    professorsFile.close()
    print("Author list loaded")

def carrega_artigos():
    '''
    Lista os vértices com rótulo Author pela propriedade name e faz a busca
    no lattes atualizando os nomes usados nas citações carrega vértices com
    o rótulo Article
    '''
    queryAuthors = "MATCH (a:Author) WHERE (a.keylattes is null AND a.name =~ 'Fernanda.*') RETURN a.name"
    professors,metadata = cypher.execute(graph_db, queryAuthors)

    for i in professors:
        profName = str(i[0]).strip()        
        print("Pesquisando professor: " + profName)     
        curriculums =  searchCV(profName)
        
        if curriculums.__len__() > 1:
            print("Mais de um curriculo para o professor: " + profName)
            #FIXME: Dont insert the wrong curriculum 
            continue
        for curr in curriculums:
            nomeCitacoes,artigos = parselattes2.listaCitacoes(curr)
            
            print("Nomes usados nas citacoes %s" %nomeCitacoes)
            nomeCitacoes = nomeCitacoes.replace("'",'"')
            # Atualiza os nomes usados para citação
            try:
                nodeAuthor, = cypher.execute(graph_db, 
                                                     "MATCH (n:Author {name:'%s'}) SET n.citation = '%s',n.keylattes = '%s',n.timestamp = timestamp() RETURN n" %(profName, nomeCitacoes, curr))
            except Exception as e:
                print("Erro ao inserir nomes usados em citacao para pesquisador " + profName,e)                        
            for artigo in artigos:                
                articleAsString = str()
                for key in artigo.keys():
                    articleAsString += "p." + key.replace('-','_') + " = '" +artigo[key] + "', "                                   
                try:                
                    cypher.execute(graph_db,
                                   "MERGE (p:Article {title:'%s'}) ON CREATE SET %s p.lastUpdate = timestamp() RETURN p" %
                                   (artigo["title"], articleAsString)
                                   )
                    cypher.execute(graph_db,
                                    "MATCH (a:Author {name:'%s'}),(p:Article {title:'%s'}) MERGE (a)<-[r:AUTHORING]->(p)" %
                                    (profName, artigo["title"]))               
                except Exception as e:
                    print("Erro ao inserir artigo: ", e)
                    raise e
       
#loadFromFile()
#carrega_professor()            
#carrega_artigos()
loadFromJSON("C:\\devel\\python\\scrap\\docentes.json")
print("FIM")
