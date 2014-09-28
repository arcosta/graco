#!/usr/bin/python
#-*- language: utf-8 -*-

#
# extrai os elementos do curriculo
#

from bs4 import BeautifulSoup
from urllib.request import urlopen
import re

def scraplattes(resultPage):
	'''
	Faz um parse na pagina de resultados e retorna uma tupla com a chave do curriculo e o curriculo
	'''
	protocolHost = "http://buscatextual.cnpq.br"
	url_visualiza = protocolHost + "/buscatextual/visualizacv.do?id="
	soup = BeautifulSoup(resultPage)

	#Div com os links de paginação
	div_paginacao = soup.find_all(attrs={"class":"paginacao"})	

	# Expressões regulares para tratar a paginação
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
			urlResultados = protocolHost+"/buscatextual/busca.do?metodo=forwardPaginaResultados&registros="+str(regInicio)+";"+regPorPagina+queryPaginacao 	+ strLParPag + "&tipoOrdenacao=null&paginaOrigem=index.do&mostrarScore=false&mostrarBandeira=true&modoIndAdhoc=null"
			paginaResultados=BeautifulSoup(urlopen(urlResultados))
		#print("url: " + urlResultados)

		# Os resultados da busca ficam dentro de uma div cujo atributo class é resultado
		div_resultado = paginaResultados.find_all(attrs={"class":"resultado"})
		
		#parametro de retorno
		result = list()
		
		# Se tiver mais de uma ocorrencia tem algo errado na busca já que um pesquisador so pode ter um curriculo
		# vamos limitar o parse do primeiro resultado encontrado
		contador=0
		curriculos = div_resultado[0].find_all("li")
		if curriculos.__len__() == 0:
			print("Pesquisador não possui curriculo")
		for i in curriculos:
			if contador >= 1:
				print("Resultado duplicado encontrado !!!")
				break
			chamadaJS=i.b.a['href']
		
			#TODO: Trocar para regex
			chave_cur = chamadaJS.split("'")[1]

			print("Processando: " + chave_cur)
			# abre o curriculo
			#result.append((chave_cur,urlopen(url_visualiza + chave_cur).read()))
			result.append(chave_cur)
			contador += 1
		return result
        