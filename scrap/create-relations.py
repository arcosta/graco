from py2neo import neo4j,cypher,node
from time import time

class Professor:
    def __init__(self, name, cit):
        self.citation=cit
        self.name = name
        
class Article:
    def __init__(self, subject, cit):
        self.citation=cit
        self.subject = subject


start_time = time()
graph_db = neo4j.GraphDatabaseService()
queryAuthors = "MATCH (a:Author) RETURN a"
queryArticle = "MATCH (p:Article) RETURN p"
professors,metadata = cypher.execute(graph_db, queryAuthors)
articles,metadata = cypher.execute(graph_db, queryArticle)

professorList = list()
articleList = list()

for prof in professors:
    pnode = node(prof[0])
    citation = pnode['citation']
    citationList = list()
    if citation is not None:
        citationList = citation.split(";")
        #print("Nome de citação: ", citationList)
        professorList.append(Professor(pnode['name'], set(citationList)))

for art in articles:
    anode = node(art[0])
    citation = node(art[0])['citacao']
    citationList = list()
    if citation is not None:
        citationList = citation.split(" ; ")
        #print("Citado no artigo:", citationList)
        articleList.append(Article(anode['titulo'],set(citationList)))


for p in professorList:
    for a in articleList:
        if p.citation.intersection(a.citation).__len__() > 0:
            print("Artigo %s - Autor: %s" %(a.subject, p.name))
            cypher.execute(graph_db,"MATCH (a:Author {name:'%s'}),(p:Article {titulo:'%s'}) MERGE (a)<-[r:AUTHORING]->(p)" %(p.name, a.subject))
    

stop_time = time()
print("Tempo decorrido em segundos: " +str(stop_time - start_time))
