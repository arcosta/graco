#-*- coding: latin-1 -*-
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import URLError
from http.client import BadStatusLine
import json,re, time


#
# Parse curriculum
#

protocolHost = "http://buscatextual.cnpq.br"
url_visualiza = protocolHost + "/buscatextual/visualizacv.do?id="

def titleToKey(title):
    '''
    @description Transform the title to remove latin and punction symbols and spaces.
    @param title The title of the publication as informed in curriculum
    '''
    translationTable = str.maketrans("çáâãéêóôõúñ", "caaaeeoooun", ": '`{}[])(@?!_-/")
    return title.lower().translate(translationTable)

def carregaJCR(issn, resArt):
    '''
    @description Load JCR informations from article
    '''
    baseurl = protocolHost + "/buscatextual/visualizacao.do"
    query="metodo=ajax&acao=jcr&issn=" + issn
    url=baseurl+"?"+query

    count = 0
    maxtry=12
    while count <= maxtry:
        count +=1
        try:
            pagina = urlopen(url).read().decode("utf-8")
            json_obj = json.loads(pagina)
            for i in json_obj.keys():
                #print(i + " : " + json_obj[i])
                resArt.update(json_obj)
            break
        except ValueError as err:
            # Esse é o caso dos artigos que não possuem JCR
            msg = "Erro ao pegar jcr: "+ err.__str__()
        except BadStatusLine as err:
            # Esse tratamento pega timeouts na urlopen
            print("Erro de requisição no JCR: ", err)
        except URLError as err:
            pass

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
        try:
            fields = artigo['cvuri'].split("&")
            resArt = dict()

            citationAsList = artigo.findParents()[0].text.replace("'", '?').split(" . ")
            prefixToRemove = citationPrefix.match(citationAsList[0])
            yearPublication = re.search(r' (\d\d\d\d)[,\.]{1}', citationAsList[1]).group(1)
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
        except IndexError as e:
            print("Error inserting article %s" %citationAsString)
    return resArtigos


def artigosPeloContexto(soup):
    '''
    @description Localiza uma div da classe pad-5 e verifica se ela contem um span com
    '''
    result = list()
    citationPrefix= re.compile("(.*(\.)?[\d]{4}(\n)?)",re.IGNORECASE | re.MULTILINE)

    secaoArtigosCompletos = soup.find(attrs={"id": "artigos-completos"})
    if secaoArtigosCompletos == None:
        # there is no article published
        return []
    div_completeArticle = secaoArtigosCompletos.find_all(attrs={"class": "artigo-completo"})
    print("%i artigos encontrados" %len(div_completeArticle))
    for article in div_completeArticle:
        tag_article = article.find_all(attrs={"class": "layout-cell-pad-5"})[1]

        articleEntry = tag_article.text
        resArt = dict()

        articleEntryAsList = articleEntry.split(" . ")
        if len(articleEntryAsList) < 2:
            articleEntryAsList = articleEntry.split(" ; ")
        prefixToRemove = citationPrefix.match(articleEntryAsList[0])
        authors = articleEntryAsList[0].replace(prefixToRemove.group(),'')

        resArt['authors'] = authors.replace("'","`")
        titleInfos = articleEntryAsList[1:]
        title = titleInfos[0].split(". ")[0]
        resArt['title'] = title.replace("'","`")
        resArt['key'] = titleToKey(title)

        if len(titleInfos) > 1:
            resArt['periodic'] = titleInfos[1].split(", ")[0]
        else:
            resArt['periodic'] = titleInfos[0].split(". ")[1]
        resArt['year'] = re.search(r'(\d\d\d\d)', articleEntryAsList[0]).group(1)

        try:
            citado = article.find(attrs={"class":"citacoes"})
            cvuriFields = citado['cvuri'].split('&')
            for i in cvuriFields:
                if i.find("issn") != -1:
                    issn_data=i.split('=')[1]
                    resArt["issn"]=issn_data
                    carregaJCR(issn_data, resArt)
                if i.find("doi") != -1:
                    doi=i.split('=')[1]
                    resArt["doi"]=doi
        except TypeError as e:
            print(tag_article)

        result.append(resArt)
    return result

def listaCitacoes(curriculo):
    """
    @description List names used in citation 'and production'
    """
    soup=''
    MAXTRY = 12
    tries=0
    citacoes=''
    
    while tries <= MAXTRY:
        try:
            time.sleep(2)
            print("Try: %i" % tries)
            tries += 1
            soup = BeautifulSoup(urlopen(url_visualiza + curriculo).read())
            if soup.find_all(attrs={"class":"divCaptcha"}).__len__() > 0:
                continue
            else:
                print("Acesso liberado !")
                break
            if tries == MAXTRY:
                print("Numero de tentativas excedido")
                return
        except IOError as err:
            print("Captcha error %s" % str(err))
            
    pads5 = soup.find_all(attrs={"class":"layout-cell-pad-5"})
    
    if pads5.__len__() > 0:
        citacoes = pads5[3].text
        print("OS nomes usados nas citações são: " + citacoes)
    else:
        print("Nenhum nome de citação encontrado")

    # This method returns a dictionary list
    # artigos = artigosPelaURL(soup)
    artigos = artigosPeloContexto(soup)
    return (citacoes,artigos)
