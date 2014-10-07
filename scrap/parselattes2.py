from bs4 import BeautifulSoup
from urllib.request import urlopen
from http.client import BadStatusLine
import json,re

protocolHost = "http://buscatextual.cnpq.br"
url_visualiza = protocolHost + "/buscatextual/visualizacv.do?id="

def carregaJCR(issn, resArt):
    '''
    @description Carrega as informações de JCR do artigo
    '''
    baseurl = "http://buscatextual.cnpq.br/buscatextual/visualizacao.do"
    query="metodo=ajax&acao=jcr&issn=" + issn
    url=baseurl+"?"+query

    try:
        pagina = urlopen(url).read().decode("utf-8")
        #print("Fazendo requisicao em: " +url)
        json_obj = json.loads(pagina)
        for i in json_obj.keys():
            #print(i + " : " + json_obj[i])
            resArt.update(json_obj)
    except ValueError as err:
        # Esse é o caso dos artigos que não possuem JCR
        print("Erro ao pegar jcr: ", err)
    except BadStatusLine as err:
        # Esse tratamento pega timeouts na urlopen	
        print("Erro de requisição no JCR: ", err)
    
def artigosPelaURL(soup):
    '''
    @description: Abordagem para pegar as informações das publicações pela url das citações
    para pegar as informações de jcr devo tratar as informações de <sup>
    
    @param soup Objeto BeautifulSoup que armazena o DOM do curriculo
    '''
    artigos = soup.find_all(attrs={"class": "citacoes"})
    resArtigos = list()
    citationPrefix= re.compile("(.*(\.)?[\d]{4}(\n)?)",re.IGNORECASE | re.MULTILINE)

    for artigo in artigos:
        fields = artigo['cvuri'].split("&")
        resArt = dict()
        #resArt["citacao"] = artigo.findParents()[0].text
        #resArt["citacao"] = resArt["citacao"].replace("'", '?')
        citationAsList = artigo.findParents()[0].text.replace("'", '?').split(" . ")
        prefixToRemove = citationPrefix.match(citationAsList[0])
        yearPublication = citationAsList[1].split(',')[-1].lstrip()
        citationAsString = citationPrefix.split(citationAsList[0])[4].lstrip()
        resArt["citacao"] = citationAsString
        resArt["ano"] = yearPublication
        for i in fields:
            if i.find("issn") != -1:
                issn_data=i.split('=')[1]
                resArt["issn"]=issn_data
                #print("issn: " + issn_data)
                carregaJCR(issn_data, resArt)
            if i.find("titulo") != -1:
                titulo = i.split('=')[1]
                resArt["titulo"]=titulo.replace("'", '´')
                print("titulo: " + resArt["titulo"])
            if i.find("nomePeriodico") != -1:
                nomePeriodico=i.split('=')[1]
                resArt["nomePeriodico"]=nomePeriodico
                #print("Nome do periódico: " + nomePeriodico)
            if i.find("doi") != -1:
                doi=i.split('=')[1]
                resArt["doi"]=doi
            
        print("")
        resArtigos.append(resArt)
    return resArtigos
	
	
def artigosPeloContexto(soup):
    '''
    @description Localiza uma div da classe pad-5 e verifica se ela contem um span com
    '''
    tags_pad = soup.find_all(attrs={"class": "layout-cell-pad-5"})
    for tag in tags_pad:
        tag_artigo = tag.find_all(attrs={"class": "informacao-artigo"})
        if tag_artigo.__len__() > 0:
            print("Div com artigo encontrada: " + tag.text)

def listaCitacoes(curriculo):
    #url="http://buscatextual.cnpq.br/buscatextual/visualizacv.do?id=K4793179D5"
    #url="http://buscatextual.cnpq.br/buscatextual/visualizacv.do?id=K4793137P2"

    soup = BeautifulSoup(urlopen(url_visualiza + curriculo).read())
    pads5 = soup.find_all(attrs={"class":"layout-cell-pad-5"})

    citacoes = pads5[3].text
    print("OS nomes usados nas citações são: " + citacoes)

	# Essa função retorna uma lista de dicionarios
    artigos = artigosPelaURL(soup)
    return (citacoes,artigos)
    #artigosPeloContexto(soup)
