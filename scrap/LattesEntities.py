#-------------------------------------------------------------------------------
# Name:        module2
# Purpose:
#
# Author:      Andressa Alves
#
# Created:     14/02/2015
# Copyright:   (c) Andressa Alves 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------


class Institution(object):
    name = str()
    def __init__(self, name = None):
        self.name = name

class Periodic(object):
    name = str()
    issn = ()
    def __init__(self):
        pass

class Paper(object):
    title = str()
    year = int()
    authors = list()
    periodic = Periodic()
    def __init__(self):
        pass


class Researcher(object):
    name = str()
    citation = str()
    institution = Institution()
    def __init__(self):
        pass
