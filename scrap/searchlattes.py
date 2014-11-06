#!/usr/bin/python
#-*- language: utf-8 -*-

#
# Feed search form of curriculums
# Preenche o formulario para a busca na base de curriculos e salva o resultado em arquivo
#

from urllib.request import urlopen,Request
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import re

def searchCV(name):
    '''
    Feed form to search curriculums based on researchers name and returns the id of curriculums 
    '''
    protocolHost = "http://buscatextual.cnpq.br"
    url_busca = protocolHost + "/buscatextual/busca.do"    
    url_visualiza = protocolHost + "/buscatextual/visualizacv.do?id="
    
    result = list()
    
    request = Request(url_busca)
    request.add_header("Content-type","application/x-www-form-urlencoded")
    request.add_header("User-agent", "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36")

    #TODO: This can be externally configured
    data=urlencode({
    'metodo':'buscar',
    'buscaAvancada':0,
    'buscaAssunto':'false',
    'filtros.buscaNome':'true', 
    'textoBusca':'"'+name+'"', 
    'buscarDoutores': 'true', 
    'buscarDemais': 'false', 
    'buscarBrasileiros': 'true',
    'buscarEstrangeiros':'true',
    'paisNascimento':'0',
    'buscarDoutoresAvancada':'true',
    'buscarBrasileirosAvancada':'true',
    'buscarEstrangeirosAvancada':'true'
    })
    
    #FIXME: Is this coding soup correct ?
    resultPage = urlopen(request, data.encode('utf8')).read()
    soup = BeautifulSoup(resultPage.decode('latin-1'))

    #print("REQUEST",request.get_full_url(),data)
    
    div_paginacao = soup.find_all(attrs={"class":"paginacao"})  

    # Treat pagination
    try:
        totalRegistros = re.search(r"var intLTotReg = (\d+)", div_paginacao.__str__()).group(1)
        regPorPagina = re.search(r"var intLRegPagina = (\d+)", div_paginacao.__str__()).group(1)
        queryPaginacao = re.search(r"var strLQuery = '([^;]+)'", div_paginacao.__str__()).group(1)
        queryBase = re.search(r'href=\'([^"]+)', div_paginacao.__str__()).group(1)
        links = re.findall('var (\w+)', div_paginacao.__str__())
        range_paginacao = int(int(totalRegistros)/int(regPorPagina))
    except AttributeError:
        range_paginacao = 1
    
    for pagina in range(range_paginacao):
        paginaResultados = None
        urlResultados = ''
        if range_paginacao == 1:
            paginaResultados = soup
        else:
            regInicio = (pagina * int(regPorPagina)) - int(regPorPagina)
            strLParPag = "&numeroPagina=" + str(pagina)
            urlResultados = protocolHost+"/buscatextual/busca.do?metodo=forwardPaginaResultados&registros="+str(regInicio)+";"+regPorPagina+queryPaginacao  + strLParPag + "&tipoOrdenacao=null&paginaOrigem=index.do&mostrarScore=false&mostrarBandeira=true&modoIndAdhoc=null"
            paginaResultados=BeautifulSoup(urlopen(urlResultados))

        # Os resultados da busca ficam dentro de uma div cujo atributo class é resultado
        div_resultado = paginaResultados.find_all(attrs={"class":"resultado"})

        #print(div_resultado[0].text)
        curriculos = div_resultado[0].find_all("li")
        if len(curriculos) == 0:
            print("Curriculum not found for: %s" % name)
            print(curriculos)
        for i in curriculos:            
            chamadaJS=i.b.a['href']
        
            #TODO: Trocar para regex
            chave_cur = chamadaJS.split("'")[1]

            print("Processando: " + chave_cur)
            result.append(chave_cur)
    return result