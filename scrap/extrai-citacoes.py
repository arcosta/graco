#from py2neo import neo4j,cypher,node
from py2neo import Graph
import re


graph_db = Graph()

queryArticles = "MATCH (a:Article) RETURN a.authors"
citations = graph_db.cypher.execute(queryArticles)
citationPrefix= re.compile("(.*(\.)?[\d]{4}(\n)?)",re.IGNORECASE | re.MULTILINE)


for cit in citations:
    citationAsList = cit[0].split(" . ")
    #prefixToRemove = citationPrefix.match(citationAsList[0])
    
    #citationAsString = citationPrefix.split(citationAsList[0])[4].lstrip()
    #authors = citationAsString.split(" ; ")
    
    authors = citationAsList[0].split(" ; ")
    print("Autores(%i): %s" % (len(authors), [a.replace('\n','').replace('\t','') for a in authors]))
    #print("Titulo: %s \n" % citationAsList[1])
            