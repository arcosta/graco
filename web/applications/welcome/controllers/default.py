# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from py2neo import neo4j,cypher

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    return dict(message='ComGra')


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())


@request.restful()
def publication()
    response.view = 'generic.json'
    def GET(*args, **vars):
        patterns=[
            "/publications[publications]"
        ]
        try:
            #graph_db = neo4j.GraphDatabaseService("http://grafocolaboracao:1CmvfXNcEzyT78FwUHVU@grafocolaboracao.sb02.stations.graphenedb.com:24789/db/data/")
            graph_db = neo4j.GraphDatabaseService()
            queryArticles = "MATCH (p:Article) RETURN p"
            articles,metadata = cypher.execute(graph_db, queryArticles)
            
            authoring = list()
            if articles.__len__() < 10:
                raise Exception("Few articles")
            for p in articles:
                authoring.append({"nomePeriodico":p[0]["nomePeriodico"],
                                    "size":1,
                                    "author":p[4]["citacao"]}
                )
        except Exception,e:
            return dict(authoring="ERROR: " + e.__str__())        
        return dict(children=authoring)
        
@request.restful()
def api():
    response.view = 'generic.json'
    def GET(*args,**vars):
        # Retorne uma lista de nos dessa forma dessa forma
        # {source: "Nokia", target: "Qualcomm", type: "suit"}
        patterns = [
            "/relations[relations]",
            "/researcher/{researchers.name.startswith}",
            "/researcher/{researchers.id}/:field"            
            ]
        
        try:
            graph_db = neo4j.GraphDatabaseService("http://grafocolaboracao:1CmvfXNcEzyT78FwUHVU@grafocolaboracao.sb02.stations.graphenedb.com:24789/db/data/")
            queryRelations = "MATCH (a:Author)<-[r:AUTHORING]->(p:Article) RETURN a,p"
            relations,metadata = cypher.execute(graph_db, queryRelations)
            
            links = list()
            if relations.__len__() < 10:
                raise Exception("Few nodes")
            for r in relations:
                links.append({"source":r[0]["name"], 
                                        "target":r[1]["issn"], 
                                        "size":6}
                )
        except Exception,e:
             return dict(links="ERROR: " + e.__str__())
        # Na view pode usar um forEach no json    
        return dict(children=links)
        
    return locals()