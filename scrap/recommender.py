#-------------------------------------------------------------------------------
# Name:        recommender
# Purpose:      Generate recommendation for a given Researcher
#
# Author:      aurelio
#
# Created:     14/02/2015
# Copyright:   (c) aurelio 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from py2neo import Graph, Node, Relationship
from math import exp
from time import time, localtime
import operator

class Recommender(object):
    '''
    @description Class with recommendation methods
    '''
    def __init__(self):
        pass

    def rho(self, year = None):
        '''
        @description Cumputes the time influence of an article
        '''
        if not year:
            return
        curr_year = localtime(time())[0]
        ret = 1 / exp(curr_year - int(year))
        return ret


    def recommend(self, users = None, itens = None, active_key = None):
        '''
        @description Make recommendations based on collaboration
        filtering aproach
        '''
        if users == None or itens == None:
            return
        simili_matrix = dict()

        #create similarity matrix
        for user in users:

            periodicDict = dict()
            for authoring in user.match(rel_type='AUTHORING'):
                article = authoring.end_node

                rho = self.rho(article['year'])
                periodic = article['periodic']
                if periodicDict.get(periodic):
                    periodicDict[periodic] += rho
                else:
                    periodicDict[periodic] = rho

            simili_matrix[user['keylattes']] = periodicDict

        # similarity matrix ready
        # begin test section

        #active_key = 'K4793137P2' # celia
        active_key = 'K4797106D2' # Alba

        active_periodics = list(simili_matrix.get(active_key).keys())

        recommended = dict()
        for sk in simili_matrix.keys():
            if active_key == sk:
                continue
            score = 0
            for p in simili_matrix.get(sk).keys():
                try:
                    if active_periodics.index(p) != 0:
                        score += simili_matrix.get(active_key).get(p)
                except ValueError as e:
                    pass
            recommended[sk] = score
        sorted_x = sorted(recommended.items(), key=operator.itemgetter(1), reverse = True)
        neighbor1 = graph.cypher.execute("MATCH p=(a:Author {keylattes:'%s'})-[r:AUTHORING*2]-(b:Author) RETURN DISTINCT b.name" % active_key)
        neighbor_list = list()

        # cast RecordList to list
        [neighbor_list.append(x[0]) for x in neighbor1]

        for i in sorted_x[:10]:
            n = graph.find_one("Author", property_key='keylattes', property_value=i[0])
            try:
                if neighbor_list.index(n['name']) != -1:
                    print('[**] ' + n['name'] + ' - ' + str(i[1]))
            except ValueError:
                print(n['name'] + ' - ' + str(i[1]))

if __name__ == '__main__':
    r = Recommender()

    graph = Graph()
    authors = graph.find("Author")
    publications = graph.find("Article")

    r.recommend(authors, publications)
