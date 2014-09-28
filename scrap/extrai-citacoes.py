from py2neo import neo4j,cypher,node
import re


graph_db = neo4j.GraphDatabaseService()
queryArticles = "MATCH (a:Article) RETURN a.citacao"
citations,metadata = cypher.execute(graph_db, queryArticles)
citationPrefix= re.compile("(.*(\.)?[\d]{4}(\n)?)",re.IGNORECASE | re.MULTILINE)


for cit in citations:
    citationAsList = cit[0].split(" . ")
    prefixToRemove = citationPrefix.match(citationAsList[0])
    citationAsString = citationPrefix.split(citationAsList[0])[4].lstrip()
    print("Autores: %s" % citationAsString.split(" ; "))
    print("Titulo: %s \n" % citationAsList[1])
            
