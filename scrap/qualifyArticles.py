from py2neo import neo4j,cypher,node
import qualisService

graph_db = neo4j.GraphDatabaseService()
queryArticle = "MATCH (p:Article) WHERE p.qualis is null RETURN p"

articles,metadata = cypher.execute(graph_db, queryArticle)
faltam = len(articles)
for article in articles:
    issn = node(article[0])['issn']
    #corrige o issn
    old_issn = issn
    if issn.find('-') == -1:
        issn = issn[:4]+'-'+issn[4:]
    
    qualification = qualisService.getStratus(issn.strip())
    print("Pesquisando ISSN %s: %s" % (old_issn.strip(),qualification))
    print("Faltam %i" %faltam)
    if qualification is not None:
        cypher.execute(graph_db, "MATCH (p:Article) WHERE p.issn='%s' SET p.qualis='%s' RETURN 'ok'" % (old_issn,qualification))
    faltam -= 1
    