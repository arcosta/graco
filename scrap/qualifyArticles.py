from py2neo import Graph,Node
import qualisService

'''
Update qualis field of articles 
'''

graph_db = Graph()
queryArticle = "MATCH (p:Article) WHERE p.qualis is null RETURN p"
queryArticlebyIssn = "MATCH (p:Article) WHERE p.issn='%s' SET p.qualis='%s' RETURN 'ok'"

articles = graph_db.cypher.execute(queryArticle)
missing = len(articles)
for article in articles:
    issn = article['issn']
    #fix issn
    old_issn = issn
    if issn.find('-') == -1:
        issn = issn[:4]+'-'+issn[4:]

    qualification = qualisService.getStratus(issn.strip())
    print("Searching ISSN %s: %s" % (old_issn.strip(),qualification))
    print("Missing %i" % missing)
    if qualification is not None:
        graph_db.cypher.execute(queryArticlebyIssn % (old_issn,qualification))
    missing -= 1
