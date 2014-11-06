from bs4 import BeautifulSoup
from urllib.request import build_opener,HTTPCookieProcessor
from urllib.parse import urlencode
from http.cookiejar import CookieJar
from http import cookies


def getStratus(issn):        
    cj = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cj))

    urlStartDance = "http://qualis.capes.gov.br/webqualis/publico/pesquisaPublicaClassificacao.seam?conversationPropagation=begin"
    title = "IEEE Signal Processing Letters"
    #issn="0018-9340"
    stratus = ""

    data = urlencode({
        "consultaPublicaClassificacaoForm":"consultaPublicaClassificacaoForm",
        "consultaPublicaClassificacaoForm:issn":issn,
        "consultaPublicaClassificacaoForm:btnPesquisarISSN":"Pesquisar",
        "javax.faces.ViewState":"j_id1"    
    })

    # Begin the dance
    opener.open(urlStartDance)
    jsessionid = ""
    for cookie in cj:
        jsessionid = cookie.value

    urlSearch="http://qualis.capes.gov.br/webqualis/publico/pesquisaPublicaClassificacao.seam;jsessionid=" + jsessionid
    opener.addheaders = [("Origin","http://qualis.capes.gov.br"),
        ("Host","qualis.capes.gov.br"),
        ("Cache-Control", "no-cache"),
        ("Cache-Control","no-cache"),
        ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"),
        ("Accept-Encoding", "gzip,deflate"),
        ("Accept-Language", "pt-BR,pt;q=0.8,en-US;q=0.6,en;q=0.4"),
        ("Referer",urlStartDance),
        ("Content-Type","application/x-www-form-urlencoded"),
        ("User-agent", "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36")
        ]

    connectionHandler = opener.open(urlSearch, data.encode('UTF-8'))
    
    resultPage = connectionHandler.read()
    soup = BeautifulSoup(resultPage)

    tableResult = soup.find(attrs={"id":"consultaPublicaClassificacaoForm:listaVeiculosIssn:tb"})
    if tableResult is None:
        return
    
    for row in tableResult.find_all("tr"):
        cells = row.find_all("td")
        if cells[3].text.find("NCIA DA COMPUTA") != -1:
            stratus = cells[2].text

    return stratus