from py2neo import neo4j,cypher,node
from time import time

#
# Script to make authoring relationships for professors and articles 
# previously loaded into Graph database.  
#

class Professor:
    def __init__(self, name, cit):
        '''
        Initialize a Professor object.
        @param name Professor's name
        @param cit A data structure Set with names used for citations
        '''
        self.citation=cit
        self.name = name
        
class Article:
    def __init__(self, subject, cit):
        '''
        Initialize an Article object.
        @param subject The title of the publication
        @param cit A data structure Set with names of authors 
        '''
        self.citation=cit
        self.subject = subject

start_time = time()

#Connect to neo4j and run queries
#graph_db = neo4j.GraphDatabaseService("http://grafocolaboracao:1CmvfXNcEzyT78FwUHVU@grafocolaboracao.sb02.stations.graphenedb.com:24789/db/data/")
graph_db = neo4j.GraphDatabaseService()
queryAuthors = "MATCH (a:Author) RETURN a"
queryArticle = "MATCH (p:Article) RETURN p"
professors,metadata = cypher.execute(graph_db, queryAuthors)
articles,metadata = cypher.execute(graph_db, queryArticle)

# Initialize lists
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
        articleList.append(Article(anode['title'],set(citationList)))


for p in professorList:
    for a in articleList:
        if p.citation.intersection(a.citation).__len__() > 0:
            print("Artigo %s - Autor: %s" %(a.subject, p.name))
            cypher.execute(graph_db,"MATCH (a:Author {name:'%s'}),(p:Article {title:'%s'}) MERGE (a)<-[r:AUTHORING]->(p)" %(p.name, a.subject))
    

stop_time = time()
print("Tempo decorrido em segundos: " +str(stop_time - start_time))
