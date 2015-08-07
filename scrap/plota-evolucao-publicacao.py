#-------------------------------------------------------------------------------
# Name:        plota-evolucao-publicacao.py
# Purpose:
#
# Author:      Aurelio.Costa
#
# Created:     30/01/2015
# Copyright:   (c) Aurelio.Costa 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#-*- coding: latin-1 -*-
import numpy as np
import datetime as DT
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from py2neo import Graph, Node, Relationship


consulta = "MATCH (a:Author)-[r:AUTHORING]-(p:Article) WHERE toInt(p.year) >= 2004 RETURN p.year AS year, count( DISTINCT p) AS Publications ORDER BY year"

def allCitationsKnown(g = None):
    if not g:
        return

    citations = ''
    for author in g.find('Author'):
        citations += author['citation'].lower() + ';'
        
    return citations

def authorSign(g = None):
    '''
    Returns a dictionary with authors name as key and citations used
    by each author as value
    '''
    if not g:
        return
    authors = g.find("Author")
    ret = dict()
    for author in authors:
        ret[author['name']] = author['citation'].replace('\n','').lower()
    return ret

def matchAuthorBySign(sign = None):
    '''
    Returns true whether the sign is used by some known author
    '''
    if not sign:
        return
    citations = allCitationsKnown(Graph())

    #print(citations + " == " + sign)
    if citations.find(sign.strip()) != -1:
        return True
    else:
        return False
    
def articleAuthorsByYear(g = None, year = None):
    '''
    Returns a list of articles published at that year as a dictionary with title
    as key and authors as value
    '''
    if not g:
        return
    articles = g.find("Article", property_key='year', property_value=str(year))
    ret = dict()
    for article in articles:
        ret[article['title']] = article['authors'].replace('\n','').lower()
    return ret
    

def main():
    g = Graph()
    factor=list()
    internal=list()
    external=list()

    resultSet = g.cypher.execute(consulta)
    
    years=[int(x[0]) for x in resultSet]
    publications=[x[1] for x in resultSet]

    #authors = authorSign(g)
    for year in years:
        inte = 0
        exte = 0
        articles = articleAuthorsByYear(g, year)
        for pidx,paper in enumerate(articles.keys()):
            auth_list = articles[paper].split(';')
            

            #print("Artigo %i do ano %i tem %i autores" %(pidx, int(year), len(auth_list)))
            for cit in auth_list:
                # FIXME: Always return false
                if matchAuthorBySign(cit):
                    inte += 1
                else:
                    exte += 1
            #print('Ano %s: artigo %i - %i internos / %i externos: %s' % (year, pidx, internal,external, articles[paper]))    
        fac = (inte-exte)/len(articles)
        print("Ano %i : %i internos / %i externos %i artigos -> %f" %(year, inte, exte,len(articles), fac))
        internal.append(inte)
        external.append(exte)
        factor.append(10*fac)
                                
    fig = plt.figure()
    graph = fig.add_subplot(111)
    #plt.xticks(np.arange(min(anos), max(anos)+1, 10.0))
    
    [pub,fac,inter,exter]= graph.plot(years, publications, 'r--',
               years, factor, 'g-',
               years, internal, 'k^',
               years, external, 'bo')

    graph.legend((pub,fac,inter,exter),
                 ('publicações','fator de coautoria','internas','externas'),
                 loc=2)

    plt.title("Evolução das publicações")
    plt.xlabel("Anos")
    plt.ylabel("Publicações")
    graph.set_xticks(years)
    graph.set_xticklabels(years)
    graph.axis([2003, 2015, -30, 140])
    graph.grid(True)

    plt.show()

if __name__ == '__main__':
    main()
