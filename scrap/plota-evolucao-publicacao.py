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

import numpy as np
import datetime as DT
import matplotlib.pyplot as plt


def main():
    years = [2009, 2010, 2011, 2012, 2013, 2014]
    publications = [20, 20, 19, 21, 36, 25]
    factor = [-1.25, -0.85, -1.3157, -1.2380, -1.7222, -1.24]
    internal = [23, 26, 23, 26, 28, 27]
    external = [48,43,48,52,100,58]

    fig = plt.figure()
    graph = fig.add_subplot(111)
    #plt.xticks(np.arange(min(anos), max(anos)+1, 10.0))
    graph.plot(years, publications, 'r--', years, factor, 'g-', years, internal, 'k^', years, external, 'bo')

    plt.title("Evolução das publicações")
    #plt.ylabel("Número de publicações")
    plt.xlabel("Anos")
    graph.set_xticks(years)
    graph.set_xticklabels(years)
    graph.axis([2008, 2015, -10, 110])
    graph.grid(True)

    plt.show()



if __name__ == '__main__':
    main()
