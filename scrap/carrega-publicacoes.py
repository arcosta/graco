#!/usr/bin/python

from py2neo import Graph, Node
import sys
import time
import json

from bs4 import BeautifulSoup
from urllib.request import urlopen

import searchlattes
import parselattes2

print("Iniciando carga da base a partir de web")

graph_db = Graph()

# Prepara a traducao de acentos para evitar problemas na busca
charOrigem="áâãéêíóôõú"
charDestino="aaaeeiooou"
tabelaTraducao= str.maketrans(charOrigem,charDestino)

def loadFromFile():
    """
    Load the researchers from a file with insert query
    """
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
    """
    Inserts each element of a list with label Author
    """
    soup = BeautifulSoup(urlopen("http://www.cic.unb.br/index.php?option=com_qcontacts&view=category&catid=0&Itemid=10").read())

    cont = 1
    professores = soup.find_all(attrs={"class": "category"})
    professorsFile = open("queryMergeProfessors-raw.sql","w")
    for prof in professores:
        cont +=1

        nomeProfessor = prof.text.translate(tabelaTraducao)
        nomes = nomeProfessor.split()
        
        nomeProfessor = nomeProfessor.strip()
        professorsFile.write("MERGE (a:Author {name:'%s'}) RETURN a\n" % nomeProfessor)

    professorsFile.close()
    print("Author list loaded")

def carrega_artigos():
    """
    Lista os vértices com rótulo Author pela propriedade name e faz a busca
    no lattes atualizando os nomes usados nas citações carrega vértices com
    o rótulo Article
    """
    #queryAuthors = "MATCH (a:Author) WHERE (a.keylattes is null) RETURN a"
    queryAuthors = "MATCH (a:Author) WHERE (a.citation =~ '') RETURN a"
    professors = graph_db.cypher.execute(queryAuthors)

    print("Encontrados %i professores" % professors.__len__())

    for i in professors:
        profName = str(i[0]['name'])
        print("Pesquisando professor: " + profName)     
        curriculums =  searchlattes.searchCV(profName)

        if not curriculums or len(curriculums) == 0:
            lattesUrl = str(i[0]['lattesurl']).strip()
            if lattesUrl:
                curriculums = searchlattes.getCVbyURL(lattesUrl)
            else:
                continue

        if len(curriculums) > 1:
            print("Mais de um curriculo para o professor: " + profName)
            # FIXME: Dont insert the wrong curriculum. Need to call disambiguation
            continue
        # FIXME: This loop is unnecessary
        for curr in curriculums:
            nomeCitacoes,artigos = parselattes2.listaCitacoes(curr)
            
            print("Nomes usados nas citacoes %s" %nomeCitacoes)
            nomeCitacoes = nomeCitacoes.replace("'",'"')
            # Atualiza os nomes usados para citação
            try:
                nodeAuthor = graph_db.cypher.execute(
                                                     "MATCH (n:Author {name:'%s'}) SET n.citation = '%s',n.keylattes = '%s',n.timestamp = timestamp() RETURN n" %(profName, nomeCitacoes, curr))
            except Exception as e:
                print("Erro ao inserir nomes usados em citacao para pesquisador " + profName,e)
                raise e
            for artigo in artigos:                
                articleAsString = str()
                for key in artigo.keys():
                    articleAsString += "p." + key.replace('-','_') + " = '" +artigo[key] + "', "                                   
                try:                
                    graph_db.cypher.execute(
                                   "MERGE (p:Article {title:'%s'}) ON CREATE SET %s p.lastUpdate = timestamp() RETURN p" %
                                   (artigo["title"], articleAsString)
                                   )
                    graph_db.cypher.execute(
                                    "MATCH (a:Author {name:'%s'}),(p:Article {title:'%s'}) MERGE (a)<-[r:AUTHORING]->(p)" %
                                    (profName, artigo["title"]))               
                except Exception as e:
                    print("Erro ao inserir artigo: ", e)
                    raise e

#loadFromJSON("docentes.json")
#loadFromFile()
#carrega_professor()
carrega_artigos()
print("FIM")
