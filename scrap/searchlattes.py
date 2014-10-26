#!/usr/bin/python
#-*- language: utf-8 -*-

#
# Preenche o formulario para a busca na base de curriculos e salva o resultado em arquivo
#

from urllib.request import urlopen,Request
from urllib.parse import urlencode

def searchCV(name):
	'''
	Preenche o formulario de pesquisa e retorna a pagina com os resultados da busca
	'''
	url="http://buscatextual.cnpq.br/buscatextual/busca.do"
	request = Request(url)
	request.add_header("Content-type","application/x-www-form-urlencoded")
	request.add_header("User-agent", "msbrowser")

	data=urlencode({
	'metodo':'buscar',
	'buscaAvancada':0,
	'buscaAssunto':'false',
	'buscaNome':'true', 
	'textoBusca':'"'+name+'"', 
	'buscarDoutores': 'true', 
	'buscarDemais': 'false', 
	'buscarBrasileiros': 'true',
	'buscarEstrangeiros':'true',
	'paisNascimento':'0'})
	
	# result é a pagina com o resultado da busca
	result = urlopen(request, data.encode('utf8')).read()
	#print("Fazendo busca na url: " + request.__str__() + ' / '+data.__str__())
	return result.decode('latin-1')
	# Daqui pode chamar o scraplattes em cima do arquivo de saida para pegar o curriculo de cada pesquisador

	p#rint("OK")