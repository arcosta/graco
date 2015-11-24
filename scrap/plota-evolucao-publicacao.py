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

# -*- coding: latin-1 -*-
import matplotlib.pyplot as plt
from py2neo import Graph, Node, Relationship


fyear = 2004
lyear = 2014
consulta = "MATCH (a:Author)-[r:AUTHORING]-(p:Article) WHERE a.name IN %s AND toInt(p.year) >= %i AND toInt(p.year) <= %i RETURN p.year AS year, count( DISTINCT p) AS Publications ORDER BY year"

def allCitationsKnown(g = None):
    if not g:
        return

    citations = ''
    for author in g.find('Author'):
        if author['citation']:
            citations += author['citation'].lower() + ';'
        
    return citations

def authorSign(g = None):
    """
    Returns a dictionary with authors name as key and citations used
    by each author as value
    """
    if not g:
        return
    authors = g.find("Author")
    ret = dict()
    for author in authors:
        ret[author['name']] = author['citation'].replace('\n','').lower()
    return ret

def matchAuthorBySign(sign = None):
    """
    Returns true whether the sign is used by some known author
    """
    if not sign:
        return
    citations = allCitationsKnown(Graph())

    #print(citations + " == " + sign)
    if citations.find(sign.strip()) != -1:
        return True
    else:
        return False
    
def articleAuthorsByYear(g = None, year = None):
    """
    Returns a list of articles published at that year as a dictionary with title
    as key and authors as value
    """
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

    #"Jan Mendonca Correa",

    pNames = ['Alba Cristina Magalhães Alves de Melo', 'Aletéia Patrícia Favacho', 'Anderson Clayton Nascimento', 'André Costa Drummond', 'Bruno Luiggi Macchiavello Espinoza', 'Camilo Chang Dorea','Carla Denise Castanho','Cláudia Nalon','Célia Ghedini Ralha','Diego de Freitas Aranha','Flávio de Barros Vidal','Genaína Nunes Rodrigues','George Luiz Medeiros Teodoro','Jacir Luiz Bordim','Jorge Carlos Lucero','Li Weigang','Maria Emília Machado Telles Walter','Maristela Terto de Holanda','Maurício Ayala Rincón','Mylène C. Q. Farias','Priscila América Solís Mendez Barreto','Ricardo Lopes de Queiroz','Ricardo Pezzuol Jacobi','Vander Ramos Alves','Rodrigo Bonifacio de Almeida']

    resultSet = g.cypher.execute(consulta %(pNames, fyear, lyear))
    
    years=[int(x[0]) for x in resultSet]
    publications=[x[1] for x in resultSet]

    #authors = authorSign(g)
    for year in years:
        inte = 0
        exte = 0
        articles = articleAuthorsByYear(g, year)
        for pidx,paper in enumerate(articles.keys()):
            auth_list = articles[paper].split(';')

            for cit in auth_list:
                # FIXME: Always return false
                if matchAuthorBySign(cit):
                    inte += 1
                else:
                    exte += 1

        fac = (inte-exte)/len(articles)
        print("Ano %i : %i internos / %i externos %i artigos -> %f" %(year, inte, exte,len(articles), fac))
        internal.append(inte)
        external.append(exte)
        factor.append(10*fac)
                                
    fig = plt.figure()
    graph = fig.add_subplot(111)
    plt.title("Evolução das publicações do PPGInf/UnB")
    plt.xlabel("Anos")
    plt.ylabel("Publicações")

    pub, = graph.plot(years, publications, 'r--', label="Publicações")
    #fac, = graph.plot(years, factor, 'g-', label="Fator")
    intp, = graph.plot(years, internal, 'k^', label="Autorias internas")
    extp, = graph.plot(years, external, 'bo', label="Autorias externas")

    #plt.legend(handles=[pub, fac, intp, extp])
    plt.legend(handles=[pub, intp, extp])

    graph.set_xticks(years)
    graph.set_xticklabels(years)
    graph.axis([fyear - 1, lyear + 1, -40, 140])
    graph.grid(True)

    plt.show()

if __name__ == '__main__':
    main()
