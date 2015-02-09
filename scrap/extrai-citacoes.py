#from py2neo import neo4j,cypher,node
from py2neo import Graph
import re


graph_db = Graph()

queryArticles = "MATCH (a:Article) RETURN a.authors,a.year"
citations = graph_db.cypher.execute(queryArticles)
citationPrefix= re.compile("(.*(\.)?[\d]{4}(\n)?)",re.IGNORECASE | re.MULTILINE)

publications = dict()

for cit in citations:
    citationAsList = cit[0].split(" . ")
    #prefixToRemove = citationPrefix.match(citationAsList[0])
    
    #citationAsString = citationPrefix.split(citationAsList[0])[4].lstrip()
    #authors = citationAsString.split(" ; ")
    
    authors = citationAsList[0].split(" ; ")
    year = cit[1]
    authorNames = list()
    interno = 0
    externo = 0
    for author in authors:
        queryAuthor = "MATCH (a:Author) WHERE a.citation =~ '.*%s.*' RETURN a.name" % author.replace('\n','').replace('\t','')
        authorNode = graph_db.cypher.execute(queryAuthor)
        if authorNode.one is not None:
            authorNames.append(authorNode.one)
            interno += 1
        else:
            authorNames.append(author.replace('\n','').replace('\t',''))
            externo +=1
    #print("%s Autores (%i internos, %i externos): %s" % (year, interno, externo, authorNames))
    if publications.get(year) is None:
        publications[year] = {'ocorrencias':1,'interno':interno,'externo':externo}
    else:
        publications[year]['interno'] += interno
        publications[year]['externo'] += externo
        publications[year]['ocorrencias'] += 1
    #print("Titulo: %s \n" % citationAsList[1])
            
years = list(publications.keys())
years.sort()
for year in years:
    numPublicacoes = publications[year]['ocorrencias']
    numPubInter = publications[year]['interno']
    numPubExt = publications[year]['externo']
    print("Ano %s (%s): internas %s / %s externas - fator: %s" %(year,numPublicacoes, numPubInter, numPubExt, (numPubInter-numPubExt)/numPublicacoes))