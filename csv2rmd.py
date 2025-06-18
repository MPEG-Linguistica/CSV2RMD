
import textwrap
import pandas as pd
import os
import unicodedata
import locale
import markdown2
import subprocess
import base64
import shutil
from datetime import datetime
import inquirer
import sys
import traceback




def testa_final(string, remove_ponto: bool = False):
    string = string.strip()
    
    if string == "":
        return ""
    
    if remove_ponto:
        if string.endswith("."):
            return string[:-1]
        return string
    else:
        if not string.endswith("."):
            return string + "."
        return string


def strip_accents(s):
	return ''.join(c for c in unicodedata.normalize('NFD', s)
				   if unicodedata.category(c) != 'Mn')


configuracoes = 'configuracao.txt'
colunas_padrao = [
	'ID',
	'ITEM_LEXICAL',
	'IMAGEM',
	"LEGENDA_IMAGEM",
	'ARQUIVO_SONORO',
	'TRANSCRICAO_FONEMICA',
	'TRANSCRICAO_FONETICA',
	'CLASSE_GRAMATICAL',
	'TRADUCAO_SIGNIFICADO',
	'DESCRICAO',
	'ARQUIVO_SONORO_EXEMPLO',
	'TRANSCRICAO_EXEMPLO',
	'TRADUCAO_EXEMPLO',
	'ARQUIVO_VIDEO',
	'CAMPO_SEMANTICO',
	"SUB_CAMPO_SEMANTICO",
	 "ITENS_RELACIONADOS"]
posicao = {
	'ID': 0,
				'ITEM_LEXICAL': 1,
				'IMAGEM': 2,
				'LEGENDA_IMAGEM': 3,
				'ARQUIVO_SONORO': 4,
				'TRANSCRICAO_FONEMICA': 5,
				'TRANSCRICAO_FONETICA': 6,
				'CLASSE_GRAMATICAL': 7,
				'TRADUCAO_SIGNIFICADO': 8,
				'DESCRICAO': 9,
				'ARQUIVO_SONORO_EXEMPLO': 10,
				'TRANSCRICAO_EXEMPLO': 11,
				'TRADUCAO_EXEMPLO': 12,
				'ARQUIVO_VIDEO': 13,
				'CAMPO_SEMANTICO': 14,
				'SUB_CAMPO_SEMANTICO': 15,
				'ITENS_RELACIONADOS': 16,
				'TEXTO_AUDIO': 17
}

# Função auxiliar para mapear caracteres para ordenação personalizada
def mapear_caractere(caractere, ordem):
	return ordem.get(caractere, len(ordem))

# salva as respostas em txt para as proximas execuções
def salvar_parametros(parametros):
	# Carrega os parâmetros existentes do arquivo se ele existir
	existing_params = carregar_parametros() if os.path.exists(configuracoes) else {}

	# Atualiza os parâmetros existentes com os novos valores
	existing_params.update(parametros)

	with open(configuracoes, 'w', encoding="UTF-8") as arquivo:
		for chave, valor in existing_params.items():
			arquivo.write(f"{chave}={valor}\n")

def preencher_listas(*listas):
	# Descobrir o tamanho da maior lista
	max_len = max(len(lista) for lista in listas)

	# Preencher as listas com o valor padrão ("") até que todas tenham o mesmo
	# tamanho
	listas_preenchidas = [lista + [""] *
		(max_len - len(lista)) for lista in listas]

	return listas_preenchidas

def carregar_parametros():
	parametros = {}
	try:
		with open(configuracoes, 'r', encoding="UTF-8") as arquivo:
			linhas = arquivo.readlines()
			for linha in linhas:
				chave, valor = linha.strip().split('=')
				parametros[chave] = valor
	except BaseException:
		pass
	return parametros
def verificar_e_executar(chave):
	parametros = carregar_parametros()
	if chave in parametros:
		valor = parametros[chave]
		return valor
	else:
		return False

# menu inicial e funções para gerar menus
def dividir_texto(texto, tamanho_max):
	palavras = texto.split()
	linhas = []
	linha_atual = ""

	for palavra in palavras:
		if len(linha_atual + palavra) + 1 <= tamanho_max:
			linha_atual += " " + palavra
		else:
			linhas.append(linha_atual.ljust(tamanho_max))
			linha_atual = palavra

	if linha_atual:
		linhas.append(linha_atual.ljust(tamanho_max))

	return linhas

def imprimir_menu(titulo, opcoes, texto_explicativo=None, tamanho=77):
	"""
	Função para exibir um menu com opções usando inquirer, com bordas e texto explicativo.
	
	Args:
		titulo (str): Título do menu.
		opcoes (list): Lista de opções do menu.
		texto_explicativo (str, opcional): Texto explicativo, exibido abaixo do título.
		tamanho (int, opcional): Largura da borda, padrão 77 caracteres.
	
	Returns:
		str: O número da opção selecionada.
	"""
	
	# Cabeçalho do menu
	print("+" + "-" * tamanho + "+")
	print("\u2502" + " " * tamanho + "\u2502")
	print("\u2502" + titulo.center(tamanho) + "\u2502")
	print("\u2502" + " " * tamanho + "\u2502")
	print("+" + "-" * tamanho + "+")
	
	# Exibe o texto explicativo, se houver
	if texto_explicativo:
		linhas = dividir_texto(texto_explicativo, tamanho)
		for linha in linhas:
			print("\u2502" + linha.ljust(tamanho) + "\u2502")
		print("+" + "-" * tamanho + "+")

	# Borda acima das opções
	msg = f'''Opções'''

	# Exibe as opções usando inquirer
	pergunta = [
		inquirer.List('escolha',
					  message=msg,
					  choices=opcoes)
	]
	
	resposta = inquirer.prompt(pergunta)

	# Retorna o índice da escolha feita pelo usuário (ajustado para ser 1-indexado)
	return str(opcoes.index(resposta['escolha']) + 1)

def menu_simples(
	titulo,
	lista_referencia=None,
	texto_explicativo=None,
	tamanho=77,
	 resposta_obrigatoria=True):
	print("+" + "-" * tamanho + "+")
	print("\u2502" + titulo.ljust(tamanho) + "\u2502")
	print("+" + "-" * tamanho + "+")

	if texto_explicativo is not None:
		linhas = dividir_texto(texto_explicativo, tamanho)
		for linha in linhas:
			print("\u2502" + linha + "\u2502")
		print("+" + "-" * tamanho + "+")

	while True:
		if lista_referencia:
			resposta = input(
				"Digite sua resposta (separe os elementos por vírgula): ")
		else:
			resposta = input("Digite sua resposta: ")

		# Se a lista de referência for None, aceitamos qualquer resposta
		if lista_referencia is None:
			return resposta

		# Converter a lista de referência para um conjunto para facilitar a
		# verificação
		conjunto_referencia = set(map(str, lista_referencia))

		# Dividir a resposta do usuário em elementos individuais por vírgula
		elementos_resposta = set(resposta.split(','))

		# Verificar se todos os elementos da resposta estão no conjunto de
		# referência
		if resposta_obrigatoria and not elementos_resposta.issuperset(
			conjunto_referencia):
			print("A resposta deve conter todos os elementos da lista de referência.")
		else:
			# Verificar se não há elementos em excesso na sequência
			elementos_excesso = elementos_resposta - conjunto_referencia

			if elementos_excesso:
				print("Elementos em excesso na sequência:",
					  ', '.join(sorted(elementos_excesso)))
			else:
				return resposta

def organiza_dados_dicionario(lista_dados,lista_campos,dicionario_subcampos):
		categorias_organizadas = {}
		for categoria in lista_campos:
				categorias_organizadas [categoria] = {}
				for chave,subcampos in dicionario_subcampos.items():
						if chave == categoria:
								for subcampo in subcampos:
										categorias_organizadas[categoria][subcampo]= []
		for chave,valor in categorias_organizadas.items():
				if valor == {}:
						categorias_organizadas[chave]["SEM_SUB_CAMPOS"] = []

		for item in lista_dados:
				if type(item) == list:
						campo = item[0]["CAMPO_SEMANTICO"]
						subcampo = item[0]["SUB_CAMPO_SEMANTICO"]
				else:
						campo = item["CAMPO_SEMANTICO"]
						subcampo = item["SUB_CAMPO_SEMANTICO"]           
				
				if subcampo == "":
						categorias_organizadas[campo]["SEM_SUB_CAMPOS"].append(item)
				else:
						categorias_organizadas[campo][subcampo].append(item)

		return categorias_organizadas

def titulo_autor(formato):
	# Pergunta do Título
	if formato == "html":
		chave_parametro = "Titulo-html"
	if formato == "pdf":
		chave_parametro = "Titulo-pdf"

	valor_parametro = verificar_e_executar(chave_parametro)
	if valor_parametro:
		titulo = valor_parametro
	else:
		titulo = menu_simples("Digite o título do documento")
		salvar_parametros({chave_parametro: titulo})

	# Pergunta do Autor(es)
	chave_parametro = "Autor(es)"
	valor_parametro = verificar_e_executar(chave_parametro)
	if valor_parametro:
		autor = valor_parametro
	else:
		autor = menu_simples("Digite o nome do(s) autor(es) do documento")
		salvar_parametros({chave_parametro: autor})

	# Pergunta da Versão (opcional)
	chave_parametro = "Versão"
	valor_parametro = verificar_e_executar(chave_parametro)
	if valor_parametro != False:
		versao = valor_parametro
	else:
		versao = menu_simples(
			"Digite a versão do dicionário (deixe em branco se não houver)")
		if versao:  # Só salvar se o valor não estiver em branco
			salvar_parametros({chave_parametro: versao})
		else:
			salvar_parametros({chave_parametro: ""})

	# Pergunta da Data do Dicionário (opcional)
	chave_parametro = "Data do Dicionário"
	valor_parametro = verificar_e_executar(chave_parametro)
	if valor_parametro != False:
		data = valor_parametro
	else:
		data = menu_simples(
			"Digite a data do dicionário (deixe em branco se não houver)")
		if data:  # Só salvar se o valor não estiver em branco
			salvar_parametros({chave_parametro: data})
		else:
			salvar_parametros({chave_parametro: ""})

	return titulo, autor, versao, data

def abrearquivo():
	arquivo = os.path.join(os.getcwd(), "dicionario.csv")
	try:
		df_temp = pd.read_csv(arquivo)
		df_temp = df_temp.fillna('').astype(str)

		df_temp.columns = df_temp.columns.str.upper()
		df_temp.columns = df_temp.columns.str.strip()
		colunas_df = list(df_temp.columns)

		# Filtrar colunas que não começam com '#'
		colunas_df = [
	coluna for coluna in df_temp.columns if not coluna.startswith('#')]

		if colunas_padrao == colunas_df:
			lista = df_temp.to_dict(orient='records')
			for item in lista:
				item["CAMPO_SEMANTICO"] = item["CAMPO_SEMANTICO"].capitalize().strip()
				item["SUB_CAMPO_SEMANTICO"] = item["SUB_CAMPO_SEMANTICO"].capitalize().strip()

			for dicionario in lista:
				for chave, valor in dicionario.items():
					dicionario[chave] = valor.strip()
			return lista
		else:
			df = pd.DataFrame(columns=colunas_padrao).fillna('')
			for coluna in colunas_padrao:
				if coluna in colunas_df:
					df[coluna] = df_temp[coluna].values
					colunas_df.remove(coluna)

			for coluna in colunas_df:
				df[coluna] = df_temp[coluna].values
			lista = (df.fillna('')).to_dict(orient='records')

			for item in lista:
				item["CAMPO_SEMANTICO"] = item["CAMPO_SEMANTICO"].capitalize().strip()
				item["SUB_CAMPO_SEMANTICO"] = item["SUB_CAMPO_SEMANTICO"].capitalize().strip()

			for indice, dicionario in enumerate(lista):
				for chave, valor in dicionario.items():
					dicionario[chave] = str(valor).strip()
			return lista

	except (FileNotFoundError, IOError):
		resposta = '99999999244885'
		while resposta != '1':
			resposta = imprimir_menu(
	"Erro de arquivo",
	["sair"],
	"arquivo não encontrado - Caminho não encontrado: " +
	 arquivo)
		sys.exit()

def listar_campos_semanticos(lista_dic, opcao_ordem=False):
	# Conjunto para armazenar valores únicos
	valores_unicos_campo = set()
	valores_unicos_subcampo = set()
	# Dicionário para mapear campos a seus subcampos
	dicionario_campos_subcampos = {}

	# Iterar sobre a lista de dicionários
	for dicionario in lista_dic:
		campo_semantico = dicionario.get('CAMPO_SEMANTICO')
		sub_campo_semantico = dicionario.get('SUB_CAMPO_SEMANTICO')

		# Adiciona campo semântico ao conjunto
		if campo_semantico:
			valores_unicos_campo.add(campo_semantico.capitalize().strip())
			# Inicializa a lista de subcampos para o campo semântico
			if campo_semantico not in dicionario_campos_subcampos:
				# Use um set para evitar duplicatas
				dicionario_campos_subcampos[campo_semantico] = set()

		# Adiciona subcampo semântico ao conjunto e ao dicionário
		if sub_campo_semantico and campo_semantico:  # Verifica se existe um campo semântico
			dicionario_campos_subcampos[campo_semantico].add(
				sub_campo_semantico.capitalize().strip())

	# Converter os conjuntos de volta para listas
	lista_campos = list(valores_unicos_campo)
	lista_subcampos = list(set(subcampo for subcampos in dicionario_campos_subcampos.values(
	) for subcampo in subcampos))  # Lista de subcampos únicos

	campos = sorted(lista_campos)

	campos_semanticos_normalizado = []

	if opcao_ordem:
		# Geração dos campos padrão com suas respectivas posições
		campospadrao = ", ".join(
	f"{i} - {campo}" for i,
	 campo in enumerate(campos))
		numeros_campos = list(range(len(campos)))

		# Verificação do parâmetro para alterar a ordem dos campos
		chave_parametro = "Alterar ordem dos campos"
		valor_parametro = verificar_e_executar(chave_parametro)

		# Se não houver valor pré-definido, exibe o menu
		if valor_parametro:
			opcao = valor_parametro
		else:
			opcao = imprimir_menu(
							"Ordem atual dos campos",
							["Não alterar ordem", "Sim, alterar a ordem"],
							"A ordem atual dos campos é: " + campospadrao
			)
			salvar_parametros({chave_parametro: opcao})
		print(type(opcao))
		# Se a opção for para alterar a ordem
		if opcao == "2":
			chave_parametro = "Ordem dos campos"
			valor_parametro = verificar_e_executar(chave_parametro)

			# Se não houver valor pré-definido, solicita a nova ordem
			if valor_parametro:
				novaordem = valor_parametro
			else:
				novaordem = menu_simples(
	"Digite uma sequência numérica reordenando os números referentes a cada campo",
	numeros_campos,
	"Ordem atual: " +
	campospadrao +
	 " Digite uma sequência numérica reordenando os números referentes a cada campo. Por exemplo: 5,4,2,3,1,0")
				salvar_parametros({chave_parametro: novaordem})

			# Reordenação dos campos conforme a nova ordem fornecida
			camposnovaordem = [campos[int(i)] for i in novaordem.split(",")]
			campos = camposnovaordem

		for campo in campos:
			campos_semanticos_normalizado.append(
				strip_accents(campo.replace(' ', '-').capitalize()))

	# Organizar os subcampos, colocando os que começam com 'Outr' no final
	for campo, subcampos in dicionario_campos_subcampos.items():
		subcampos = sorted(subcampos)  # Ordenar os subcampos normalmente
		outros_subcampos = [subcampo for subcampo in subcampos if subcampo.lower(
		).startswith('outr')]  # Filtrar os 'Outr'
		subcampos = [subcampo for subcampo in subcampos if not subcampo.lower(
		).startswith('outr')]  # Remover os 'Outr' da lista principal
		subcampos.extend(outros_subcampos)  # Adicionar os 'Outr' no final
		# Atualizar a lista no dicionário
		dicionario_campos_subcampos[campo] = subcampos

	return campos, campos_semanticos_normalizado, dicionario_campos_subcampos

def ordenar_dicionarios(
	lista_dicionarios,
	chave_ordem,
	categorias=None,
	 mudar_id=True):
	"""
	Ordena uma lista de dicionários com base na chave fornecida e na ordem alfabética padrão ou personalizada.
	Se 'categorias' for especificado, ordena apenas essas categorias.
	Adiciona IDs temporários na ordem ordenada e depois restaura a ordem original.
	"""
	# Configurar locale para ordenação correta (incluindo acentos)
	locale.setlocale(locale.LC_ALL, '')

	# Tentativa de carregar a ordem alfabética personalizada
	try:
		with open("ordem-alfabeto.txt", "r", encoding="UTF-8") as alfabeto:
			alfabeto_string = alfabeto.read().strip()
			alfabeto_separado = [letra.strip()
											 for letra in alfabeto_string.split(",")]
			ordem = {letra: idx for idx, letra in enumerate(alfabeto_separado)}

		# Função de ordenação baseada na ordem personalizada
		def custom_key(item):
			valor = strip_accents(item[chave_ordem].split("|")[0].lower())
			return [ordem.get(c, len(ordem)) for c in valor]

	except FileNotFoundError:
		# Se o arquivo não for encontrado, usa a ordenação padrão do sistema
		def custom_key(item):
			valor = strip_accents(item[chave_ordem].split("|")[0].lower())
			return locale.strxfrm(valor)

	# Salvar a ordem original
	for idx, item in enumerate(lista_dicionarios):
		item['_original_index'] = idx

	if mudar_id:
		lista_dicionarios = sorted(lista_dicionarios, key=custom_key)
		for idx, item in enumerate(lista_dicionarios):
			item['ID'] = f"ID-{idx:04d}"


	# Restaurar a ordem original
	lista_dicionarios = sorted(
	lista_dicionarios,
	 key=lambda x: x['_original_index'])

	# Remover a chave de índice original
	for item in lista_dicionarios:
		del item['_original_index']



	# Ordenar a lista
	if categorias:
		lista_ordenada = []
		for categoria in categorias:
			# Filtrar itens que pertencem à categoria atual
			itens_categoria = [item for item in lista_dicionarios if item.get(
				'CAMPO_SEMANTICO') == categoria]
			# Ordenar os itens dentro da categoria
			itens_categoria_ordenados = sorted(itens_categoria, key=custom_key)
			
			lista_ordenada.extend(itens_categoria_ordenados)
		# Adicionar itens que não pertencem às categorias especificadas, sem
		# reordenar
		lista_nao_ordenada = [item for item in lista_dicionarios if item.get(
			'CAMPO_SEMANTICO') not in categorias]
		lista_ordenada.extend(lista_nao_ordenada)
	else:
		# Ordenar toda a lista se não houver categorias especificadas
		lista_ordenada = sorted(lista_dicionarios, key=custom_key)


	return lista_ordenada

def listar_novas_colunas(lista_dicionarios):
	colunas_dicionario_verificar = set()
	colunas_dicionario = []
	for coluna in lista_dicionarios[0].keys():
		colunas_dicionario_verificar.add(coluna)
		colunas_dicionario.append(coluna)
	colunas_sobrando = list(colunas_dicionario_verificar - set(colunas_padrao))
	dicionario_colunas_adicionais = {}
	for indice, coluna in enumerate(colunas_dicionario):
		if coluna in colunas_sobrando:
			dicionario_colunas_adicionais[coluna] = indice

	return dicionario_colunas_adicionais

def elevar_numero(texto, numero):
	# Mapeamento de dígitos para seus correspondentes sobrescritos
	sobrescritos = {
		'0': '\u2070',  # Sobrescrito 0
					'1': '\u00B9',  # Sobrescrito 1
					'2': '\u00B2',  # Sobrescrito 2
					'3': '\u00B3',  # Sobrescrito 3
					'4': '\u2074',  # Sobrescrito 4
					'5': '\u2075',  # Sobrescrito 5
					'6': '\u2076',  # Sobrescrito 6
					'7': '\u2077',  # Sobrescrito 7
					'8': '\u2078',  # Sobrescrito 8
					'9': '\u2079'   # Sobrescrito 9
	}

	# Converter o número em string e substituí-lo pelos dígitos sobrescritos
	numero_sobrescrito = ''.join(
	sobrescritos[digito] for digito in str(numero))

	# Retornar o texto com o número sobrescrito
	return f"{texto}{numero_sobrescrito}"

def agrupar_dicionarios(lista):
	chaves = []
	agrupados = []

	# Agrupar elementos semelhantes e separar os que possuem '%' no início
	for index, item in enumerate(lista):

		item_lexical = item['ITEM_LEXICAL']
		if item_lexical.startswith('%'):
			chave = (item['ITEM_LEXICAL'][1:],
	item['CAMPO_SEMANTICO'],
	item['CLASSE_GRAMATICAL'],
	 item['SUB_CAMPO_SEMANTICO'])
			item['ITEM_LEXICAL'] = item['ITEM_LEXICAL'][1:]
			agrupados.append([item])
			chaves.append(chave)
		else:
			chave = (
	item['ITEM_LEXICAL'],
	item['CAMPO_SEMANTICO'],
	item['CLASSE_GRAMATICAL'],
	 item['SUB_CAMPO_SEMANTICO'])
			if chave not in chaves:
				agrupados.append([item])
				chaves.append(chave)
			else:
				indices = []

				# Loop para encontrar os índices
				for indice, valor in enumerate(chaves):
					if valor == chave:
						indices.append(indice)

				agrupados[indices[0]].append(item)
	tratadas = []
	for chave in chaves:
		if chave not in tratadas:
			tratadas.append(chave)

			indices = []
			for indice, valor in enumerate(chaves):
				if valor == chave:
					indices.append(indice)
			if len(indices) > 1:
				for i in indices:
					for x, elemento in enumerate(agrupados[i]):
						elemento['ITEM_LEXICAL'] = elevar_numero(
							elemento['ITEM_LEXICAL'], indices.index(i) + 1)

	return agrupados

def cria_intro(formato='html'):
    try:
        # Define os arquivos para cada formato
        if formato == 'html':
            intro_file = "intro_html.txt"
        elif formato == 'pdf':
            intro_file = "intro_pdf.txt"
        else:
            return "Formato não suportado. Escolha 'html' ou 'pdf'."
        
        # Abre o arquivo correspondente
        with open(intro_file, "r", encoding="UTF-8") as introducao:
            introducao_conteudo = introducao.read()

            if formato == 'html':
                # Converte o markdown para HTML
                converter = markdown2.Markdown(extras=["tables", "fenced-code-blocks"])
                introducao_html = converter.convert(introducao_conteudo)
                return introducao_html

            elif formato == 'pdf':
                # O conteúdo do arquivo já está em LaTeX, então apenas retorna o conteúdo
                return introducao_conteudo

    except FileNotFoundError:
        # Retorna um texto padrão caso o arquivo não seja encontrado
        introducao_default = "<p>SUA INTRODUÇÃO VAI AQUI</p>" if formato == 'html' else "SUA INTRODUÇÃO VAI AQUI"
        return introducao_default


# arquivos para o pdf
def cria_pdf(opcao_simples=True):
	titulo, autor, versao, data = titulo_autor(formato="pdf")
	if opcao_simples:
		lista_lingua = abrearquivo()
		campos_semanticos, campos_semanticos_normalizado, dicionario_sub_campos = listar_campos_semanticos(lista_lingua)
		categorias_ordenar = None
	else:
		lista_lingua = abrearquivo()
		campos_semanticos, campos_semanticos_normalizado, dicionario_sub_campos = listar_campos_semanticos(lista_lingua, opcao_ordem=True)
		categorias_ordenar = selecionar_campos_semanticos("Selecão de campos para ordem alfabética",campos_semanticos)

	novas_colunas = listar_novas_colunas(lista_lingua)


	# Escrever arquivo com entrada lingua
	lista_lingua = ordenar_dicionarios(lista_lingua,"ITEM_LEXICAL",categorias=categorias_ordenar)
	lista_lingua = agrupar_dicionarios(lista_lingua)

	dados_organizados = organiza_dados_dicionario(lista_lingua, campos_semanticos,dicionario_sub_campos)

	string_entradas_pdf = ""
	for chave, valor in dados_organizados.items():
		string_entradas_pdf += "\n\n"
		string_entradas_pdf += fr"""\chapter{{{chave}}}\label{{{chave.lower()}}}

"""
		for sub, i in valor.items(): 
			if sub != "SEM_SUB_CAMPOS":
				string_entradas_pdf += "\n\n"
				string_entradas_pdf += fr"""\section{{{sub}}}\label{{{sub.lower()}}}

"""
			for entrada in i:
				entrada_latex = gerar_entrada_pdf(entrada,novas_colunas)
				string_entradas_pdf += entrada_latex


	if not os.path.exists(os.getcwd() + '/pdf/'):
		os.makedirs(os.getcwd() + '/pdf/')

	texto_latex = estrutura_pdf(string_entradas_pdf, titulo,autor,versao,data)
	arquivo_tex = os.path.join(os.getcwd(), "pdf","dicionario.tex")
	with open(arquivo_tex, mode="a+", encoding="utf-8") as arquivo:
		arquivo.write(texto_latex)

	output_dir = "pdf/"
	try:
		original_dir = os.getcwd()
		# Muda para o diretório de saída
		os.chdir(output_dir)

		# Passo 1: Compilar o LaTeX para gerar o arquivo .idx
		run_command(["lualatex", arquivo_tex])

		# Passo 2: Executar makeindex para gerar o arquivo .ind
		idx_file = "dicionario.idx"
		ind_file = "dicionario.ind"

		#run_command(["makeindex", "-o", ind_file, idx_file])

		# Passo 3: Compilar o LaTeX novamente para incluir o índice gerado
		run_command(["lualatex", arquivo_tex])
		#run_command(["lualatex", arquivo_tex])

		

	except Exception as e:
		print("Erro ao gerar o PDF:", e)
		sys.exit()

	finally:
		# Retorna ao diretório original
		os.chdir(original_dir)

def run_command(command):
	process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,encoding="utf-8")

	for line in iter(process.stdout.readline, ''):
		print(line, end='', flush=True)

	for line in iter(process.stderr.readline, ''):
		print(line, end='', flush=True)

	process.stdout.close()
	process.stderr.close()
	process.wait()
	
def estrutura_pdf(entradas_latex, titulo, autor, versao, data):
	introducao = cria_intro(formato="pdf")

	if versao != "":
		versao = f"\\large {versao}"



	string_pdf = rf"""
% Options for packages loaded elsewhere
\PassOptionsToPackage{{unicode}}{{hyperref}}
\PassOptionsToPackage{{hyphens}}{{url}}
%
\documentclass[
  10pt,
  a4paper,
]{{book}}
\usepackage{{amsmath,amssymb}}
\usepackage{{setspace}}
\usepackage{{iftex}}
\ifPDFTeX
  \usepackage[T1]{{fontenc}}
  \usepackage[utf8]{{inputenc}}
  \usepackage{{textcomp}} % provide euro and other symbols
\else % if luatex or xetex
  \usepackage{{unicode-math}} % this also loads fontspec
  \defaultfontfeatures{{Scale=MatchLowercase}}
  \defaultfontfeatures[\rmfamily]{{Ligatures=TeX,Scale=1}}
\fi
\usepackage{{lmodern}}
\ifPDFTeX\else
  % xetex/luatex font selection
\fi
% Use upquote if available, for straight quotes in verbatim environments
\IfFileExists{{upquote.sty}}{{\usepackage{{upquote}}}}{{}}
\IfFileExists{{microtype.sty}}{{% use microtype if available
  \usepackage[]{{microtype}}
  \UseMicrotypeSet[protrusion]{{basicmath}} % disable protrusion for tt fonts
}}{{}}
\makeatletter
\@ifundefined{{KOMAClassName}}{{% if non-KOMA class
  \IfFileExists{{parskip.sty}}{{%
    \usepackage{{parskip}}
  }}{{% else
    \setlength{{\parindent}}{{0pt}}
    \setlength{{\parskip}}{{6pt plus 2pt minus 1pt}}}}
}}{{% if KOMA class
  \KOMAoptions{{parskip=half}}}}
\makeatother
\usepackage{{xcolor}}
\usepackage{{longtable,booktabs,array}}
\usepackage{{calc}} % for calculating minipage widths
% Correct order of tables after \paragraph or \subparagraph
\usepackage{{etoolbox}}
\makeatletter
\patchcmd\longtable{{\par}}{{\if@noskipsec\mbox{{}}\fi\par}}{{}}{{}}
\makeatother
% Allow footnotes in longtable head/foot
\IfFileExists{{footnotehyper.sty}}{{\usepackage{{footnotehyper}}}}{{\usepackage{{footnote}}}}
\makesavenoteenv{{longtable}}
\usepackage{{graphicx}}
\makeatletter
\def\maxwidth{{\ifdim\Gin@nat@width>\linewidth\linewidth\else\Gin@nat@width\fi}}
\def\maxheight{{\ifdim\Gin@nat@height>\textheight\textheight\else\Gin@nat@height\fi}}
\makeatother
% Scale images if necessary, so that they will not overflow the page
% margins by default, and it is still possible to overwrite the defaults
% using explicit options in \includegraphics[width, height, ...]{{}}
\setkeys{{Gin}}{{width=\maxwidth,height=\maxheight,keepaspectratio}}
% Set default figure placement to htbp
\makeatletter
\def\fps@figure{{htbp}}
\makeatother
\setlength{{\emergencystretch}}{{3em}} % prevent overfull lines
\providecommand{{\tightlist}}{{%
  \setlength{{\itemsep}}{{0pt}}\setlength{{\parskip}}{{0pt}}}}
\setcounter{{secnumdepth}}{{5}}
% preamble.tex
\usepackage{{booktabs}}
\usepackage[Brazil]{{babel}}
\usepackage[twoside,top=3.5cm,bottom=3.5cm,left=2cm,right=2cm,columnsep=50pt]{{geometry}} 
\usepackage{{textcomp}} 
\usepackage{{fancyhdr}}
\usepackage{{parskip}}
\usepackage{{marvosym}}
\usepackage{{ragged2e}}
\usepackage[T1]{{fontenc}}
\usepackage{{titlesec}}
\usepackage{{emptypage}}
\usepackage{{lastpage}} % Obter o número total de páginas
\usepackage{{fontspec}}
\usepackage{{titling}}
\usepackage{{float}}


% Pacote para criar o índice
\usepackage{{imakeidx}}
\makeindex[columns=3, title=Índice Alfabético, intoc]

% Configuração dos títulos dos capítulos
\titleformat{{\chapter}}[display]
  {{\normalfont\huge\bfseries}}{{\chaptertitlename\ \thechapter}}{{20pt}}{{\Huge}}
\titlespacing*{{\chapter}}{{0pt}}{{50pt}}{{40pt}}

% Configuração das seções (section)
\titleformat{{\section}}
  {{\normalfont\Large\bfseries}}{{\thesection}}{{1em}}{{}}
\titlespacing*{{\section}}{{0pt}}{{20pt}}{{10pt}}

% Configuração das subseções (subsection)
\titleformat{{\subsection}}
  {{\normalfont\large\bfseries}}{{\thesubsection}}{{1em}}{{}}
\titlespacing*{{\subsection}}{{0pt}}{{15pt}}{{5pt}}

% Configuração de cabeçalho e rodapé
\fancyhf{{}} % Limpa todos os campos de cabeçalho e rodapé
\fancyhead[L]{{\textsf{{\rightmark}}}} % Cabeçalho esquerdo (capítulo)
\fancyhead[R]{{\textsf{{\leftmark}}}} % Cabeçalho direito (seção)
\fancyfoot[C]{{\textbf{{\textsf{{\thepage}}}}}} % Rodapé central (número da página)
\renewcommand{{\headrulewidth}}{{1.1pt}} % Linha horizontal no cabeçalho
\renewcommand{{\footrulewidth}}{{1.1pt}} % Linha horizontal no rodapé
\pagestyle{{fancy}} % Define o estilo de página como "fancy"
\setlength{{\headheight}}{{12.28003pt}}
% Fonte principal do documento (Arial)
\setmainfont[% OK7
UprightFont = * ,
BoldFont = *bd ,
ItalicFont = *i ,
BoldItalicFont = *bi,
]{{Arial}}

% Comando personalizado
\newcommand{{\negritoetamanhogrande}}[1]{{\textbf{{\large #1}}}}
\ifLuaTeX
  \usepackage{{selnolig}}  % disable illegal ligatures
\fi
\IfFileExists{{bookmark.sty}}{{\usepackage{{bookmark}}}}{{\usepackage{{hyperref}}}}
\IfFileExists{{xurl.sty}}{{\usepackage{{xurl}}}}{{}} % add URL line breaks if available
\urlstyle{{same}}

\hypersetup{{
	pdftitle={{{titulo}}},
	pdfauthor={{{autor}}},
	hidelinks,
	pdfcreator={{LaTeX via pandoc}}}}




\title{{{titulo}}}
\author{{{autor}}}
\date{{{data}}}




% Personalização do \maketitle para centralizar e ajustar
\renewcommand{{\maketitle}}{{%
  \thispagestyle{{empty}} % Remove o cabeçalho e rodapé da primeira página
  \vspace*{{\fill}}  % Preenche o espaço acima do conteúdo e empurra o conteúdo para o centro
  \begin{{center}}
    \LARGE \textbf{{\thetitle}}\par
    \vskip 1em
    \large \theauthor \par
    \large \thedate \par
    \vspace{{1em}}  % Espaço entre data e o elemento adicional
    {{{versao}}}
  \end{{center}}
  \vspace*{{\fill}}  % Preenche o espaço abaixo do conteúdo e assegura que fique centralizado
}}




\begin{{document}}
\maketitle



{{
\setcounter{{tocdepth}}{{1}}
\tableofcontents
}}
\setstretch{{1}}
\chapter{{Introdução}}\label{{introduuxe7uxe3o}}

{introducao}

\twocolumn


{entradas_latex}

\onecolumn
\printindex

\end{{document}}

"""

	return string_pdf

def gerar_entrada_pdf(dicionarios,novas_colunas={}):
	latex_entrada = ""

	# Pegar informações comuns do primeiro dicionário
	item = dicionarios[0].get("ITEM_LEXICAL", "")
	trans_fon = dicionarios[0].get("TRANSCRICAO_FONEMICA", "")
	trans_fonet = dicionarios[0].get("TRANSCRICAO_FONETICA", "")
	classe = dicionarios[0].get("CLASSE_GRAMATICAL", "")

	item_lista = []
	if "|" in item:
		for i in item.split("|"):
			item_lista.append(escape_latex_special_chars(i.strip()))
		item = " \\textasciitilde ~".join(item_lista)
	else:
		item = escape_latex_special_chars(item)

	trans_fon_lista = []
	if "|" in trans_fon and trans_fon != "":
		for i in trans_fon.split("|"):
			trans_fon_lista.append(escape_latex_special_chars(f'/{i.strip()}/'))
		trans_fon = " \\textasciitilde ~".join(trans_fon_lista)
	else:
		if trans_fon != "":
			trans_fon = escape_latex_special_chars(f'/{trans_fon}/')

	trans_fonet_lista = []
	if "|" in trans_fonet and trans_fonet != "":
		for i in trans_fonet.split("|"):
			trans_fonet_lista.append(escape_latex_special_chars(f'[{i.strip()}]'))
		trans_fonet = " \\textasciitilde ~".join(trans_fonet_lista)
	else:
		if trans_fonet != "":
			trans_fonet = escape_latex_special_chars(f'[{trans_fonet}]')
		



	# Início da entrada LaTeX
	latex_entrada += f'''\n\n\\markboth{{{item.strip("~").strip()}}}{{{item.strip("~").strip()}}}\n'''
	for i, dic in enumerate(dicionarios, 1):
		traducao = escape_latex_special_chars(dic.get("TRADUCAO_SIGNIFICADO", ""))
		latex_entrada += f'''\n\n\\index{{\\markboth{{{traducao}}}{{{traducao}}}{traducao} ({item.strip("~").strip()})}}\n'''
	latex_entrada += f"\\negritoetamanhogrande{{{item}}}"

	# Apenas adicionar transcrição fonêmica e fonética se não forem vazias
	if trans_fon != "":
		latex_entrada += f" {trans_fon}"
	if trans_fonet != "":
		latex_entrada += f" {trans_fonet}"

	if classe:
		latex_entrada += f" \\textit{{{classe}}} "

	# Verificar quantos significados existem
	qtd_significados = len(dicionarios)

	# Adicionar cada significado em sequência
	for i, dic in enumerate(dicionarios, 1):
		traducao = testa_final(escape_latex_special_chars(dic.get("TRADUCAO_SIGNIFICADO", "")),remove_ponto=True)
		descricao = testa_final(escape_latex_special_chars( dic.get("DESCRICAO", "")),remove_ponto=True)
		exemplos_trans = dic.get("TRANSCRICAO_EXEMPLO", "").split("|")
		exemplos = dic.get("TRADUCAO_EXEMPLO", "").split("|")
		relacionado = dic.get("ITENS_RELACIONADOS", "")
		imagens = dic.get("IMAGEM", "").split("|")
		legendas_imagens = dic.get("LEGENDA_IMAGEM", "").split("|")

		# Adicionar numeração apenas se houver mais de um significado
		if qtd_significados > 1:
			latex_entrada += f"{i}. "

		# Adicionar tradução e descrição somente se não estiverem vazias
		if traducao:
			latex_entrada += f" {traducao}"
		if descricao:
			latex_entrada += f". {descricao}"
		latex_entrada += ". " if traducao or descricao else ""

		# Processar exemplos
		for transcricao, traducao_ex in zip(exemplos_trans, exemplos):
			if traducao_ex and transcricao:  # Evitar adicionar pares vazios
				latex_entrada += f"\\textbf{{\\textit{{{testa_final(escape_latex_special_chars(transcricao))}}}}} {testa_final(escape_latex_special_chars(traducao_ex))} "

		# Adicionar itens relacionados, se houver
		if relacionado:
			latex_entrada += f"Itens relacionados: {escape_latex_special_chars(relacionado)}."

		# Adicionar imagens, se houver
		imagens_pasta = os.listdir(os.path.join(os.getcwd(), "foto"))
		for indice, imagem in enumerate(imagens):
			if imagem in imagens_pasta:
				if imagem.strip():  # Evitar imagens vazias
					if legendas_imagens != [""]:
						latex_entrada += f"\n\\begin{{figure}}[H]\\centering\\vspace{{-0.2cm}}\\includegraphics[width=0.65\\linewidth, height=0.65\\textheight]{{../foto/{imagem.strip()}}}\\vspace{{-0.2cm}}\\begin{{center}}\\textnormal{{{escape_latex_special_chars(legendas_imagens[indice]).strip()}}}\\end{{center}}\\end{{figure}}"

					else:
						latex_entrada += f"\n\\begin{{center}}\\vspace{{-0.2cm}}\\includegraphics[width=0.65\\linewidth,height=0.65\\textheight]{{../foto/{imagem.strip()}}}\\vspace{{-0.2cm}}\\end{{center}}\n"
						


	for chave in novas_colunas.keys():
		latex_entrada += f"\n\n{escape_latex_special_chars(dic.get(chave, ""))}"


	return latex_entrada

def escape_latex_special_chars(text):
	# Lista de caracteres especiais e seus escapes
	special_chars = {
					'_': r'\textunderscore ',
					'&': r'\&',
					'%': r'\%',
					'$': r'\$',
					'#': r'\#',
					'{': r'\{',
					'}': r'\}',
					'~': r'\textasciitilde ',
					'^': r'\textasciicircum '
	}

	# Substitui caracteres especiais
	for char, escape in special_chars.items():
		text = text.replace(char, escape)

	return text

# arquivos para html unico
def cria_html(opcao_simples=True, midia_inclusa=True): 
	titulo, autor, versao, data = titulo_autor(formato="html")
	if opcao_simples:
		lista_lingua = abrearquivo()
		campos_semanticos, campos_semanticos_normalizado, dicionario_sub_campos = listar_campos_semanticos(lista_lingua)
		categorias_ordenar = None
	else:
		lista_lingua = abrearquivo()
		campos_semanticos, campos_semanticos_normalizado, dicionario_sub_campos = listar_campos_semanticos(lista_lingua, opcao_ordem=True)
		categorias_ordenar = selecionar_campos_semanticos("Selecão de campos para ordem alfabética",campos_semanticos)

	novas_colunas = listar_novas_colunas(lista_lingua)


	# Escrever arquivo com entrada lingua
	id = 0
	contador = 0
	lista_lingua = ordenar_dicionarios(lista_lingua, "ITEM_LEXICAL",categorias=categorias_ordenar)
	lista_portugues = ordenar_dicionarios(lista_lingua,"TRADUCAO_SIGNIFICADO",mudar_id=False)
	lista_lingua = agrupar_dicionarios(lista_lingua)


	dados_organizados = organiza_dados_dicionario(lista_lingua, campos_semanticos,dicionario_sub_campos)

	string_entradas_HTML = ""

	for chave, valor in dados_organizados.items():
		string_entradas_HTML += f'''<section class="section level1" id="CATEGORIA_{strip_accents(chave).replace(" ", "")}">'''
		string_entradas_HTML += f'\n\n<div class="div-link">\n<p><a class="link-entrada" name="{chave.replace(" ", "")}"></a></p>\n</div>\n'
		string_entradas_HTML += f"\n\n<h1>{chave}</h1>\n\n"
		string_entradas_HTML += '<p><a href="#ini">Voltar para o começo</a></p>\n\n'
		for sub, i in valor.items(): 
			if sub != "SEM_SUB_CAMPOS":
				string_entradas_HTML += "\n\n"
				string_entradas_HTML += f'''\n<div class="level2">\n<span class="sub-c" class="section level2">{sub} </span>\n'''

			for entrada in i:
				entrada_html = gera_entrada_html(entrada, midia_inclusa=midia_inclusa,novas_colunas=novas_colunas)
				string_entradas_HTML += entrada_html
			
			if sub != "SEM_SUB_CAMPOS":
				string_entradas_HTML += "</div>"
		string_entradas_HTML += "</section>"

	string_entradas_HTML += "\n\n\n\n\n</div>\n"


	string_entradas_HTML += '''<div class="ordem-alfabetica"></div>'''
	string_entradas_HTML += '<div class="div-link">\n'
	string_entradas_HTML += '<a class="link-entrada" name="lista-significados"></a>\n'
	string_entradas_HTML += '</div>\n'
	string_entradas_HTML += "<hr>"
	string_entradas_HTML += "<h1> Entradas ordenadas por significado</h1><br>\n\n\n\n"
	string_entradas_HTML += '<div id="div-significados">\n'
	for i in lista_portugues:
		string_entradas_HTML += '''<p><a class="significado-az" onclick='navegarParaAncora("''' + str(i["ID"]) +'''")'><h5>'''+ i['TRADUCAO_SIGNIFICADO'].replace(i['TRADUCAO_SIGNIFICADO'] + ". ","") + " (" + i[
						'ITEM_LEXICAL'] + ')</h5></a></p>\n'
	string_entradas_HTML += '</div><hr></div>'    

	if midia_inclusa:
		midias_script_tag = gerar_script_tags_audio()
		html_string = estrutura_html(string_entradas_HTML, titulo,autor,data,versao,campos_semanticos,midias_tag=midias_script_tag)
	else:
		html_string = estrutura_html(string_entradas_HTML, titulo,autor,data,versao,campos_semanticos)

	if not os.path.exists(os.getcwd() + '/html/'):
		os.makedirs(os.getcwd() + '/html/')

	with open("html/dicionario.html", "+a",encoding="utf-8") as arquivo:
		arquivo.write(html_string)

	if not midia_inclusa:
		diretorio_atual = os.path.dirname(os.path.abspath(__file__))	
		pastas_para_copiar = ['audio\\', 'foto\\', 'video\\']	 
		destino = os.path.join(diretorio_atual, 'html')




		for pasta in pastas_para_copiar:
			caminho_origem = os.path.join(diretorio_atual, pasta)
			caminho_destino = os.path.join(destino, pasta)

			# Cria a pasta de destino se não existir
			if not os.path.exists(caminho_destino):
				os.makedirs(caminho_destino)

			# Verifica se a pasta de origem existe
			if os.path.exists(caminho_origem):
				# Itera sobre os arquivos na raiz da pasta (ignora subpastas)
				for item in os.listdir(caminho_origem):
					caminho_item = os.path.join(caminho_origem, item)
					if os.path.isfile(caminho_item):  # Copia apenas arquivos, não diretórios
						shutil.copy(caminho_item, caminho_destino)
						print(f"Arquivo '{item}' copiado para '{caminho_destino}'")

def file_to_base64(file_path):
	with open(file_path, "rb") as file:
		encoded_string = base64.b64encode(file.read()).decode('utf-8')
	return encoded_string

def generate_media_tag(file_path, media_type, slide=False, midia_inclusa=True):
	if midia_inclusa == False:
		if media_type == 'audio':
			return f'''<button class="audio_play_botao" onclick="playAudio2('{file_path}')"></button>'''
		elif media_type == 'video':
			return f'<br><video width="500" height="500" preload="none" controls><source src="video/{file_path}" type="video/mp4"></video>'
		elif media_type == "image" and slide:
			return f'<img src="foto/{file_path}" alt="image" class="clickable-image" onclick="openModal(this.src)">'
		elif media_type == 'image':
			return f'''<br>
			<div class="image-container">
				<img loading="lazy" src="foto/{file_path}" alt="image" class="clickable-image" onclick="openModal(this.src)">
			</div>'''

	else:
		print(f"Convertendo o arquivo {os.path.basename(file_path)}...")
		if media_type == 'audio':
			encoded_data = file_to_base64("audio/" + file_path)
			return f'''<button class="audio_play_botao" data-audio-id="{os.path.basename(file_path)}"></button>'''
		elif media_type == 'video':
			encoded_data = file_to_base64("video/" + file_path)
			return f'<br><video width="500" height="500" preload="none" controls><source src="data:video/mp4;base64,{encoded_data}" type="video/mp4"></video>'
		elif media_type == "image" and slide:
			encoded_data = file_to_base64("foto/" + file_path)
			return f'<img src="data:image/jpeg;base64,{encoded_data}" alt="image" class="clickable-image" onclick="openModal(this.src)">'
		elif media_type == 'image':
			encoded_data = file_to_base64("foto/" + file_path)
			return f'''<br>
			<div class="image-container">
				<img loading="lazy" src="data:image/jpeg;base64,{encoded_data}" alt="image" class="clickable-image" onclick="openModal(this.src)">
			</div>'''

def estrutura_html(entradas_html_string, titulo,autor,data,versao,campos_semanticos, midias_tag=None):
	html_string = r'''<!DOCTYPE html>

<html>

<head>

<meta charset="utf-8" />
<meta name="''' + autor + r'''" content="''' + titulo + rf'''" />
<meta name="date" content="{data}" />
<title>''' + titulo + r'''</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style type="text/css">@font-face {
font-family: 'Georgia';
font-style: normal;
font-weight: 400;
src: url(data:font/ttf;base64,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ABIAOv/4ABIAQf/1ABIAQv/1ABIAQ//6ABIARP/vABIAUQAHABIAY//+ABIAcf/+ABIAdP/8ABIAiQAIABIAigANABIAlf//ABIAmf/+ABIAvP/9ABIAwf/6ABIAw//+ABIAyv//ABIA1P//ABIA1v//ABIA2v//ABUAG//6ABUAIf/cABUAK//nABUANP/uABUAOf//ABUAOv/fABUAQf/oABUAQv/oABUAQ//kABUARP/ZABUARv/wABUAR//6ABUAVf/yABUAcf/+ABUAfP/5ABUAhf//ABUAh///ABUAlf/7ABUAqv/0ABUArP/vABUAtv/6ABUAuf/3ABUAvP/+ABUAwf/cABUAyv//ABUA1P//ABUA1f/2ABUA1v/+ABUA2v/+ABYALf/0ABYAOf/0ABYAR//5ABYAY//tABYAcf/sABYAdP/wABYAg//zABYAhv/yABYAiQAIABYAigALABYAlf/8ABYAmf/tABYAvP/7ABYAv//wABYAw//zABYAyv/zABYA0//qABYA1P/pABYA1v/nABwAxf/5AB0AA//qAB0AIf9/AB0AK/+9AB0ALf/vAB0ANP/IAB0AOf/oAB0AR//DAB0AUQAGAB0AUv/5AB0AYP/zAB0AY//iAB0AZ//iAB0Acf/UAB0AdP/wAB0Adf/qAB0Adv/qAB0Ad//qAB0Aev/vAB0AfP/UAB0Af//0AB0Ag//tAB0AhP/vAB0Ahv/pAB0AiP/8AB0AiQAQAB0AigATAB0AiwAGAB0Alf/iAB0Amf/iAB0An//zAB0AqgABAB0ArP+1AB0AvP/cAB0Av//rAB0Awf+JAB0Aw//4AB0Axf/tAB0AyP/oAB0Ayv/nAB0A0//pAB0A1P/oAB0A1f/kAB0A1v/oAB0A2v/gAB4AOv/oAB4AQf/sAB4AQv/rAB4ARP/iAB4AVf/8AB4Acf//AB4AdP/6AB4Auf/4AB4Aw//6AB4A0//0AB4A1P/zAB4A1v/0ACAAR//5ACAAY//4ACAAcf/2ACAAdP/4ACAAigAFACAAmf/3ACAAvP/6ACAAw//4ACAA1v//ACAA2v//ACEAIf/xACEAK//wACEANP/8ACEAR//2ACEAY//3ACEAcf/0ACEAdP/5ACEAhf//ACEAh///ACEAiQAEACEAigAHACEAjv//ACEAlf/+ACEAmf/3ACEArP/3ACEAvP/1ACEAwf/sACEAw//6ACEAyv/+ACEA1f//ACEA2v/9ACQAVgADACYAA//zACYAIQABACYALf/eACYAM//6ACYANAAJACYAOf/3ACYAR//+ACYAUQAHACYAVQAEACYAWAAFACYAWgAGACYAYQAGACYAYv/xACYAY//kACYAcf/nACYAdP/0ACYAfAAKACYAg//xACYAhAABACYAhv/mACYAiQAEACYAigAXACYAiwAIACYAmf/jACYApf/6ACYAqgAKACYAswAGACYAtAAGACYAu//xACYAvgADACYAw//1ACYAyAAGACYAyv/wACYA0//dACYA1P/bACYA1v/dACYA2//5ACcAA//lACcAKP9rACcALf/TACcAOf/7ACcAOv+OACcAPP/VACcAQf+WACcAQv+UACcARP+LACcAUf+SACcAVf+pACcAYv/qACcAY//oACcAcf/uACcAdP/1ACcAg//RACcAhv++ACcAmf/pACcAo/+UACcApP+TACcAsP/vACcAtv+TACcAuP+UACcAuf+WACcAu//qACcAv//3ACcAwQAEACcAw//vACcAyv/1ACcA0/+2ACcA1P+xACcA1v+wACgAfP/tACgAjv/aACgAn//tACgAv//lACgAxf/gACgAyP/0ACsAA//hACsAG//7ACsALf/mACsAM//8ACsANAAGACsAOf/1ACsAOv+5ACsAPP/jACsAQf/JACsAQv/IACsARP+3ACsAR//4ACsATf/yACsAUf++ACsAUv/2ACsAVf/DACsAWgABACsAYQABACsAYv/qACsAY//vACsAbf/yACsAcf/xACsAdP/yACsAfAAGACsAg//xACsAhv/xACsAjv/+ACsAmf/vACsAo//TACsApP/OACsAqgAGACsAsP/nACsAswABACsAtAABACsAtv+7ACsAuP+8ACsAuf+7ACsAu//qACsAvP/6ACsAv//oACsAwP/wACsAw//pACsAyAADACsAyv/zACsA0//gACsA1P/dACsA1v/dACsA2//vAC0AG//5AC0AIf/cAC0AK//mAC0ANP/tAC0AOf//AC0AOv/eAC0AQf/nAC0AQv/mAC0AQ//kAC0ARP/WAC0ARv/tAC0AR//5AC0AUf/6AC0AVf/wAC0Acf/+AC0AfP/4AC0Ahf//AC0Ah//7AC0Alf/7AC0Aqv/yAC0ArP/tAC0Atv/5AC0AuP/6AC0Auf/zAC0AvP/+AC0Awf/ZAC0Ayv//AC0A1P//AC0A1f/0AC0A1v/8AC0A2v/+ADMAQf/8ADMAQv/8ADMAQ//7ADMARP/5ADMAUQAGADMAVQADADMAqgAEADQAIf+wADQAK//AADQALf/tADQANP8RADQAOf/8ADQAQQAGADQAQgAGADQAQwAHADQARAAHADQAR//iADQAY//aADQAbf/8ADQAcf/YADQAdP/7ADQAev/fADQAfP+0ADQAigAQADQAiwACADQAlf/qADQAlv/kADQAmf/bADQAn//tADQAvP/gADQAwP/yADQAwf+jADQAxf/nADQAyP/qADQAyv/rADQA0//wADQA1P/wADQA1f/8ADQA1v/xADQA2v/5ADQA2//cADYAA//lADYAIf+fADYAK//RADYANP/KADYAOv/8ADYAQf/0ADYAQv/0ADYAQ//vADYARP/wADYARv/3ADYAR//2ADYAY//0ADYAcf/pADYAev/8ADYAfP/eADYAg//zADYAhv/wADYAiQAEADYAigAJADYAmf/zADYAqv/8ADYArP+1ADYAvP/5ADYAwf+iADYA0wADADYA1AAEADYA1QACADYA1gAFADcAIf/8ADcAK//9ADcANAAGADcAQ//8ADcAWAADADcAWgADADcAYQADADcAfAAHADcAqgAHADcAswADADcAtAADADcAwf/6ADcAyAAEADcA1v/+ADgAG//+ADgAK//4ADgALf/8ADgANAADADgAOv/vADgAPP/9ADgAQf/sADgAQv/rADgARP/lADgAR//2ADgAVf/6ADgAY//tADgAcf/nADgAdP/8ADgAfAADADgAg//xADgAhf/7ADgAhv/5ADgAh//5ADgAjv/6ADgAlf/5ADgAmf/sADgAqgADADgAuP/+ADgAvP/7ADgAw//8ADgAyv/3ADgA0//8ADgA1P/8ADgA1v/8ADkAK//yADkAOv/4ADkAQf/xADkAQv/xADkAQ//3ADkARP/tADkAR///ADkAcf//ADkAdP/1ADkAhf//ADkAh///ADkAiQAHADkAigAKADkAjv//ADkAlf/+ADkAo//4ADkAvP/9ADkAv//2ADkAwf/9ADkAw//1ADkAyv/+ADkA0//qADkA1P/qADkA1f/3ADkA1v/qADkA2v/9ADoAA//lADoAIf+VADoAK/+5ADoALf/fADoANP/DADoAOf/3ADoAR/+dADoATf/4ADoAUQAPADoAUv/GADoAU/+pADoAYP/TADoAYv/oADoAY/+YADoAZ/+mADoAbf/5ADoAcf+oADoAdP/iADoAdf/dADoAdv/dADoAd//SADoAeP/nADoAev/IADoAfP++ADoAf//rADoAg/+/ADoAhP/NADoAhv+9ADoAiP/6ADoAiQAQADoAigAUADoAiwAGADoAlf+mADoAlv/IADoAmf+XADoAn//MADoAqgABADoArP+7ADoAu//oADoAvP+bADoAv//dADoAwP/xADoAwf+oADoAw//3ADoAxf/OADoAyP/RADoAyv+gADoA0/+0ADoA1P+0ADoA1f+6ADoA1v+2ADoA2v+wADoA2//KADsAG///ADsAIf/NADsAK//lADsANP/oADsAOf//ADsAOv/GADsAQf/iADsAQv/iADsAQ//TADsARP/HADsARv/nADsAR///ADsAUf/qADsAVf/nADsAWP/8ADsAWv/8ADsAhv/6ADsAqv/vADsArP/hADsAsP/3ADsAtv/gADsAuP/jADsAuf/PADsAwf/TADsA1P/8ADsA1f/5ADsA1v/6ADwAIf/iADwAK//jADwANP/tADwAR//zADwAY//1ADwAcf/yADwAdP/5ADwAfP/2ADwAhf/6ADwAh//6ADwAiQAEADwAigAIADwAjv/6ADwAlf/6ADwAmf/1ADwArP/uADwAvP/yADwAwf/UADwAw//7ADwAyv/4ADwA1f//ADwA2v/6AEEAA//dAEEAG//7AEEAIf+rAEEAK//JAEEALf/mAEEANP/BAEEAOf/vAEEAR//NAEEATf/sAEEAUQAKAEEAUv/aAEEAU//zAEEAVQAGAEEAWgABAEEAYP/xAEEAYv/qAEEAY//DAEEAZ//ZAEEAbf/vAEEAcf+9AEEAdP/pAEEAev/eAEEAfP/BAEEAf//qAEEAg//VAEEAhP/kAEEAhv/VAEEAiP/4AEEAiQANAEEAigAYAEEAiwALAEEAlf/ZAEEAlv/jAEEAmf/CAEEAn//uAEEAqgAGAEEArP+3AEEAtgABAEEAuAACAEEAu//qAEEAvP/OAEEAwP/sAEEAwf+pAEEAw//3AEEAxf/qAEEAyP/rAEEAyv/aAEEA0//wAEEA1P/xAEEA1f/zAEEA1v/yAEEA2v/uAEEA2//gAEIAA//dAEIAG//7AEIAIf+rAEIAK//IAEIALf/mAEIANP/AAEIAOf/vAEIAR//NAEIASv/zAEIATf/sAEIAUQAJAEIAUv/ZAEIAU//zAEIAVQAGAEIAWAABAEIAWgACAEIAYP/xAEIAYv/qAEIAY//CAEIAZ//ZAEIAbf/vAEIAcf+8AEIAdP/pAEIAev/eAEIAfP/AAEIAf//qAEIAg//UAEIAhP/kAEIAhv/VAEIAiP/4AEIAiQANAEIAigAZAEIAiwALAEIAlf/ZAEIAlv/iAEIAmf/BAEIAn//tAEIAqgAHAEIArP+2AEIAtgADAEIAuAADAEIAu//qAEIAvP/MAEIAwP/sAEIAwf+pAEIAw//3AEIAxf/qAEIAyP/rAEIAyv/ZAEIA0//wAEIA1P/xAEIA1f/yAEIA1v/yAEIA2v/uAEIA2//gAEMAA//4AEMALf/jAEMAM//6AEMANAAEAEMAOf/5AEMAR//8AEMAUQAKAEMAVQAHAEMAWAACAEMAWgADAEMAYv/yAEMAY//eAEMAZ//9AEMAcf/fAEMAdP/zAEMAfAAFAEMAf//9AEMAg//uAEMAhv/kAEMAiP/9AEMAiQAIAEMAigAZAEMAiwALAEMAlf/6AEMAmf/cAEMApf/3AEMAqgAIAEMAtgADAEMAuAADAEMAu//yAEMAw//6AEMAyAABAEMAyv/qAEMA0//iAEMA1P/hAEMA1v/jAEMA2//0AEQAA//aAEQAG//7AEQAIf+jAEQAK/+3AEQALf/XAEQANP+9AEQAOf/qAEQAR/+sAEQASv/0AEQATf/nAEQAUQAKAEQAUv/IAEQAU//yAEQAVQAHAEQAWAADAEQAWgADAEQAYP/kAEQAYv/fAEQAY/+rAEQAZ/+/AEQAa//sAEQAbf/pAEQAcf+nAEQAdP/dAEQAev/UAEQAfP+1AEQAf//gAEQAg/++AEQAhP/SAEQAhv+8AEQAiP/2AEQAiQALAEQAigAaAEQAiwANAEQAlf+/AEQAlv/TAEQAmf+pAEQAnP/sAEQAn//dAEQAqgAIAEQArP+wAEQAtgAEAEQAuAAEAEQAu//fAEQAvP+qAEQAwP/kAEQAwf+YAEQAw//wAEQAxf/dAEQAyP/dAEQAyv/CAEQA0//YAEQA1P/ZAEQA1f/dAEQA1v/bAEQA2v/ZAEQA2//RAEYALf/uAEYAR//7AEYAYv/0AEYAY//uAEYAZ//6AEYAcf/wAEYAdP/zAEYAg//2AEYAhv/xAEYAiQAIAEYAigALAEYAlf/4AEYAmf/uAEYAu//0AEYAvP//AEYAw//3AEYAyv/xAEYA0//qAEYA1P/rAEYA1v/rAEYA2//5AEcAG//5AEcAIP//AEcALf/5AEcAOf/8AEcAOv+WAEcAPP/1AEcAQf/JAEcAQv/IAEcARP+sAEcARv/8AEcAUf/mAEcAVf/YAEcAdP//AEcAo//8AEcApP/1AEcAsP/0AEcAtv/oAEcAuP/pAEcAuf/uAEcAw//5AEcA0//uAEcA1P/tAEcA1v/vAE0AIQAGAE0AKwANAE0AMwALAE0AOv/WAE0APP/8AE0AQf/VAE0AQv/VAE0AQwAQAE0ARP/KAE0ARgAEAE0ApQAEAE0AuP/ZAE0Auf/YAE0AvAAEAE0AwQAcAE0A0//tAE0A1P/tAE0A1QAMAE0A1v/sAE0A2gAEAFEAIf+oAFEAK/++AFEALf/5AFEAOgAPAFEAQQABAFEAQgAJAFEAQwAKAFEARAAKAFEAR//yAFEAY//TAFEAcf/NAFEAdP/6AFEAiQARAFEAigAUAFEAiwAEAFEAmf/hAFEAvP/uAFEAwf+gAFEA0wAGAFEA1AAHAFEA1QAHAFIAK//1AFIAOv/IAFIAQf/bAFIAQv/bAFIARP/KAFIAuP/eAFIAuf/eAFQAG//1AFQAIP/4AFQAIf/qAFQAK//wAFQAOf/4AFQAOv+YAFQAPP/1AFQAQf/CAFQAQv/CAFQAQ//dAFQARP+rAFQARv/rAFQAUf/UAFQAVf/aAFQAdP/9AFQAo//6AFQApP/xAFQAqv/vAFQArP/6AFQAsP/yAFQAtv/DAFQAuP/HAFQAuf+3AFQAvP//AFQAwf/rAFQAw//5AFQA0//uAFQA1P/tAFQA1f/tAFQA1v/uAFQA2v/0AFUAIQACAFUAKwAFAFUALf/uAFUAMwADAFUAOv/EAFUAPP/uAFUAQf/DAFUAQv/BAFUAQwAEAFUARP++AFUAuP+sAFUAuf+qAFUAv//yAFUAwP/9AFUAwQAKAFUAw//8AFUA0//gAFUA1P/dAFUA1QAEAFUA1v/eAFUA2//9AFYAJAADAFYAiQACAFYAigAGAFYAjAA/AFcAQgABAFcAQwACAFcARAADAFcAiQAIAFcAigAMAFcAjAAJAFcAwQAGAFkAKwABAFkAQQABAFkAQgACAFkAQwADAFkARAADAFkAiQAIAFkAigAMAFkAjAALAFkAwQAGAF0AG//6AF0AK//6AF0ALf/7AF0AOf/4AF0AOv+gAF0APP/4AF0AQf/JAF0AQv/JAF0AQ//8AF0ARP+0AF0ARv//AF0AUf/uAF0AVf/kAF0AY//6AF0Acf/5AF0Ag//0AF0Ahv/vAF0Amf/6AF0AsP/5AF0Atv/vAF0AuP/xAF0Auf/4AF0AvP/7AF0Awf//AF0A0//5AF0A1P/3AF0A1f/8AF0A1v/2AF4AjAAGAGAAOv/TAGAAQf/xAGAAQv/xAGAARP/kAGEAjAAKAGMAG//+AGMALf/6AGMAOv/8AGMAPP/4AGMAQf/8AGMAQv/8AGMARP/8AGMAw///AGMA0//+AGMA1P/9AGMA1v//AGQAev/tAGQAfP+qAGQAlv/mAGQAn//0AGQAxf/wAGQA2//tAGYAv//2AGYAxf/1AGgAG//3AGgAIP/5AGgAIf/vAGgAK//yAGgAOf/6AGgAOv+ZAGgAPP/4AGgAQf/HAGgAQv/GAGgAQ//qAGgARP+cAGgARv/vAGgAUf/kAGgAVf/cAGgApP/6AGgAqv/yAGgAsP/zAGgAtv/lAGgAuP/oAGgAuf/sAGgAwf/uAGgAw//7AGgA0//yAGgA1P/wAGgA1f/sAGgA1v/wAGgA2v/4AG0AK//xAG0AOv/4AG0AQf/vAG0AQv/vAG0ARP/oAG0Arf/5AG0Awf/xAHAAfP/3AHAAn//zAHAAv//tAHAAxf/pAHEAG//4AHEAIP/6AHEAIf/pAHEAK//uAHEANP/8AHEAOf/5AHEAOv/iAHEAPP/3AHEAQf/jAHEAQv/iAHEAQ//lAHEARP/cAHEARv/lAHEAUf/zAHEAVf/5AHEAqv/4AHEAtv/0AHEAuP/0AHEAuf/1AHEAwf/pAHEAw//9AHEA0//0AHEA1P/zAHEA1f/xAHEA1v/zAHEA2v/6AHMAigAEAHQAA//vAHQAIf/FAHQAK//ZAHQANP/lAHQAOf//AHQAOgAbAHQAQQAgAHQAQgAgAHQAQwAoAHQARAAlAHQARgAIAHQAR//4AHQAUQAMAHQAVQAWAHQAWAAIAHQAWgAJAHQAY//6AHQAcf/pAHQAg//oAHQAhv/kAHQAiQARAHQAigApAHQAiwASAHQAmf/5AHQAqgAWAHQArP/fAHQAtgADAHQAuAADAHQAwf/SAHQA2v/8AHUAigAGAHYAigADAHgAigADAHoAKP/0AHoAKwAEAHoAOv/UAHoAQf/zAHoAQv/zAHoARP/qAHoAVf/6AHoAhv/1AHoAkv/4AHoArf/nAHoAwQAEAHsAfP/0AHwAKP/xAHwAKwAEAHwAOv/JAHwAQf/gAHwAQv/gAHwAQwACAHwARP/WAHwAVf/jAHwAYQADAHwAZP/zAHwAhv/4AHwAkv/7AHwArf/xAHwAuf/8AHwAv//1AHwAwQAIAH4ALf/7AH4AOf//AH4AOv+lAH4APP/6AH4AQf/ZAH4AQv/XAH4AQ//6AH4ARP+/AH4ARv/5AH4AjAAlAH8AG//0AH8AIP/3AH8AIf/4AH8AK//0AH8ALf/6AH8AOf/9AH8AOv/fAH8APP/zAH8AQf/fAH8AQv/fAH8AQ//qAH8ARP/UAH8ARv/1AH8AUf/2AH8AVf/0AH8AdP/6AH8Ao//6AH8Atv/3AH8AuP/2AH8Auf/1AH8AvP//AH8Awf/0AH8Aw//5AH8A0//vAH8A1P/uAH8A1f/vAH8A1v/vAH8A2v/5AIMAOv/NAIMAQf/kAIMAQv/kAIMARP/RAIQAG//5AIQAIf/nAIQAK//xAIQAOv+/AIQAQf/UAIQAQv/UAIQAQ//uAIQARP++AIQARv/1AIQAdP/4AIQAuP/qAIQAuf/6AIQAvP/4AIQAwf/pAIQAw//3AIQA0//nAIQA1P/lAIQA1f/kAIQA1v/mAIQA2v/pAIUALf/7AIUAOf/7AIUAOv+YAIUAPP/3AIUAQf/MAIUAQv/LAIUAQ//9AIUARP+zAIUARv/4AIUAUf/eAIUAVf/fAIUApP/4AIUAsP/0AIUAtv/RAIUAuP/TAIUAuf+9AIUAw//8AIUA0//1AIUA1P/0AIUA1v/1AIYAIf/EAIYAK//xAIYAOv+9AIYAQf/VAIYAQv/VAIYAQ//kAIYARP+8AIYARv/yAIYAdP/6AIYAfP/vAIYAn//pAIYAvP/5AIYAv//iAIYAwf/wAIYAw//5AIYAxf/VAIYAyP/5AIYA0//qAIYA1P/pAIYA1f/hAIYA1v/p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ALgAcf/NALgAdP/6ALgAg//tALgAiQAEALgAigAIALgAmf/oALgArP9+ALgAvP/3ALgAwf+gALkAA//iALkAIf+rALkAK/+7ALkALf/zALkANP+jALkAR//4ALkAUv/bALkAY/+3ALkAcf/IALkAdP/6ALkAev/xALkAfP+sALkAg//6ALkAiQAEALkAigAIALkAlv/wALkAmf/qALkArP+HALkAvP/8ALkAwf+fALkAxf/3ALkA2//1ALoAA//qALoAIP//ALoAIf+vALoAK//TALoANP/aALoAOf//ALoAOv++ALoAQf/3ALoAQv/2ALoAQ//jALoARP/jALoARv/nALoAR//2ALoAUv/0ALoAY//pALoAcf/dALoAg//YALoAhP/yALoAhv/bALoAmf/oALoAqv/8ALoArP/QALoAvP/7ALoAwf/KALwAG//4ALwAIP/6ALwAK//3ALwALf/+ALwAOv+iALwAPP/1ALwAQf/SALwAQv/RALwAQ//8ALwARP+5ALwARv/8ALwAUf/4ALwAVf/mALwAdP//ALwAhv/4ALwAtv/6ALwAuP/6ALwAw///ALwA0//2ALwA1P/0ALwA1f/6ALwA1v/0AL4AjAAIAL8AIf/LAL8AKP/rAL8AK//YAL8ANP/OAL8AOv/rAL8ARv/0AL8AX//wAL8AZAABAL8AcP/0AL8Aev/xAL8AfP/QAL8Ahv/mAL8Akv/tAL8ArP+/AL8Arf/1AL8AvwADAL8Awf/LAMAAK//yAMAAOv/2AMAAQf/vAMAAQv/vAMAARP/pAMAAwf/vAMAAxf/8AMMAIP//AMMALf/3AMMAOv/NAMMAPP/1AMMAQf/lAMMAQv/kAMMARP/QAMMAVf/yAMMAY//1AMMAcf/0AMMAdP//AMMAg//sAMMAhv/yAMMAmf/1AMMAtv/5AMMAuP/6AMMAuf/xAMMAw///AMMA0///AMMA1P//AMMA1v//AMUAOv/MAMUAQf/kAMUAQv/kAMUAQwAEAMUARP/WAMUAVf/kAMUAZP/rAMUAuf/0AMUAv//3AMUAwQAIAMgAOv/NAMgAQf/mAMgAQv/mAMgARP/aAMgAVf/oAMgAwQAEAMoAG//+AMoALf/6AMoAOv+fAMoAPP/4AMoAQf/YAMoAQv/XAMoARP+6AMoARv/8AMoAUf/9AMoAVf/nAMoAtv/9AMoAuP/8AMoAw///AMoA0//+AMoA1P/9AMoA1v//ANMAA//lANMAG//4ANMAIf+1ANMAK//fANMANP/fANMAOv+zANMAQf/wANMAQv/wANMAQ//iANMARP/XANMARv/pANMAR//zANMAUQAGANMAUv/5ANMAVf/zANMAY//vANMAcf/mANMAg//nANMAhv/qANMAmf/uANMApAABANMAqv/zANMArP/SANMAvP/zANMAwf/NANQAA//kANQAG//4ANQAIf+wANQAK//dANQALf//ANQANP/cANQAOf//ANQAOv+0ANQAQf/xANQAQv/xANQAQ//hANQARP/YANQARv/pANQAR//yANQAUQAHANQAUv/5ANQAVf/yANQAY//tANQAcf/jANQAg//lANQAhv/pANQAmf/sANQApAACANQAqv/yANQArP/PANQAvP/yANQAwf/MANUALf/0ANUANAAEANUAOv+6ANUAPP//ANUAQf/zANUAQv/yANUARP/dANUAR//3ANUAUQAHANUAY//tANUAcf/oANUAdP//ANUAg//kANUAhv/hANUAmf/sANUAqgAEANUAvP/7ANYAA//lANYAG//3ANYAIP/8ANYAIf+1ANYAK//eANYANP/fANYAOf//ANYAOv+xANYAQf/uANYAQv/uANYAQ//fANYARP/UANYARv/mANYAR//yANYATf/5ANYAUv/4ANYAVf/xANYAY//tANYAcf/kANYAg//mANYAhv/qANYAmf/sANYAqv/xANYArP/RANYAvP/yANYAwf/MANoAG//6ANoAIP//ANoALf/+ANoAOv+xANoAPP/5ANoAQf/qANoAQv/pANoARP/SANoAVf/6ANoAY//0ANoAcf/vANoAg//pANoAhv/lANoAmf/0ANsAIf/2ANsAK//vANsANP/8ANsAOv/JANsAQf/gANsAQv/fANsAQ//zANsARP/RANsARv/0ANsAVf/gANsAZP/tANsAqv/xANsAuf/1ANsAv//yANsAwf/rAAAAAAAHAFoAAwABBAkAAQAOAAAAAwABBAkAAgAOAA4AAwABBAkAAwB6ABwAAwABBAkABAAOAAAAAwABBAkABQBcAJYAAwABBAkABgAOAAAAAwABBAkADgA0APIAUgBhAGwAZQB3AGEAeQBSAGUAZwB1AGwAYQByAE0AYQB0AHQATQBjAEkAbgBlAHIAbgBlAHkALABQAGEAYgBsAG8ASQBtAHAAYQBsAGwAYQByAGkALABSAG8AZAByAGkAZwBvAEYAdQBlAG4AegBhAGwAaQBkAGEAOgAgAFIAYQBsAGUAdwBhAHkAOgAgADIAMAAxADIAVgBlAHIAcwBpAG8AbgAgADIALgAwADAAMQA7ACAAdAB0AGYAYQB1AHQAbwBoAGkAbgB0ACAAKAB2ADAALgA4ACkAIAAtAEcAIAAyADAAMAAgAC0AcgAgADUAMABoAHQAdABwADoALwAvAHMAYwByAGkAcAB0AHMALgBzAGkAbAAuAG8AcgBnAC8ATwBGAEwAAgAAAAAAAP+1ADIAAAAAAAAAAAAAAAAAAAAAAAAAAADcAAABAgACAAMAjQDJAMcA2ABiAI4ArQBDANoAYwDdAK4A2QAlACYAZADeACcAKABlAMgAygDLAOkBAwApACoAKwAsAC0AzADNAM4AzwAuAC8AwwAwADEAJABmADIAsADQANEAZwDTAJEAEgCvADMANAA1ADYANwDtADgA1ADVAGgA1gA5ADoAOwA8AOsAPQBEAGkAawBsAKAAagAJAG4AQQBhAA0AIwBtAEUAPwBfAF4AYAA+AEAA6ACHAEYAbwCEAB0ADwCLAEcAgwC4AAcA1wBIAHAAcgBzAHEAGwCzALIAIADqAAQAowBJAQQBBQEGAQcBCAAYALwAFwEJAEoAiQAhAKkAqgC+AL8ASwAQAEwAdAB2AHcAdQBNAE4ATwAfAKQAUADvAJcA8ABRABwAeAAGAFIAeQB7AHwAsQB6ABQA8QD0APUAnQCeAKEAfQBTAIgACwAMAAgAEQAOAJMAVAAiAKIABQDFAMQAtAC2ALUAtwAKAFUAigBWAIYAHgAaABkAkACFAFcA7gAWAPMA9gAVAPIAWAB+AIAAgQB/AEIBCgELAQwAWQBaAFsAXADsALoAlgBdABMETlVMTARFdXJvA2ZfZgVmX2ZfaQVmX2ZfbANmX2kDZl9sDGZvdXJzdXBlcmlvcgd1bmkwMEEwB3VuaTAwQUQHdW5pMjIxNQAAAAABAAH//wAPAAEAAAAKAB4ALAABbGF0bgAIAAQAAAAA//8AAQAAAAFrZXJuAAgAAAABAAAAAQAEAAIAAAABAAgAAQDaAAQAAABoAa4B6AJSArADJgN0A3oELAReBIgE3gTkBXoF/AYWBtgHVgd0B/4IcAiqCSQJjgpkCtILLAwCDOANdg5cDrIPEA9iD7gP1hBUEKoQvBDaEQARchF4GgoRihG4EdIR3BJKEmgSehLkEuoTZBNqE2oTcBOeE6QT5hQQFIIUlBTmFTgVkhWsFcIWABZGFkwWthc0F0YXlBe2F7wYMhh8GIIY6BkuGUgZghoEGgoaChoQGkYajBrmG0gbohuoG+4cDBxiHIwcphzoHU4dvB4CHmwepgABAGgAAwARABIAFQAWABwAHQAeACAAIQAkACYAJwAoACsALQAzADQANgA3ADgAOQA6ADsAPABBAEIAQwBEAEYARwBNAFEAUgBUAFUAVgBXAFkAXQBeAGAAYQBjAGQAZgBoAG0AcABxAHMAdAB1AHYAeAB6AHsAfAB+AH8AgwCEAIUAhgCHAIgAiQCKAIwAjQCOAJIAlQCWAJgAmQCfAKUAqQCsAK0ArwCxALIAswC0ALYAuAC5ALoAvAC+AL8AwADDAMUAyADKANMA1ADVANYA2gDbAA4AIf/kACv/4QA6/+UAQf/dAEL/3QBD//gARP/bALL/4QC4/+MAuf/iAMH/3QDT/+UA1P/kANb/5QAaACH/8QAr//IAOv/fAEH/7ABC/+sAQ//wAET/4wBG//sAY///AHH//wB0//YAiQAEAIoABQCV//8Amf//ALz//QC///QAwf/2AMP/9wDF//kAyv//ANP/9wDU//YA1f/zANb/9gDa//4AFwAr//YALf/4ADn/+wA6//gAQf/1AEL/9QBD//oARP/vAFEABwBj//4Acf/+AHT//ACJAAgAigANAJX//wCZ//4AvP/9AMH/+gDD//4Ayv//ANT//wDW//8A2v//AB0AG//6ACH/3AAr/+cANP/uADn//wA6/98AQf/oAEL/6ABD/+QARP/ZAEb/8ABH//oAVf/yAHH//gB8//kAhf//AIf//wCV//sAqv/0AKz/7wC2//oAuf/3ALz//gDB/9wAyv//ANT//wDV//YA1v/+ANr//gATAC3/9AA5//QAR//5AGP/7QBx/+wAdP/wAIP/8wCG//IAiQAIAIoACwCV//wAmf/tALz/+wC///AAw//zAMr/8wDT/+oA1P/pANb/5wABAMX/+QAsAAP/6gAh/38AK/+9AC3/7wA0/8gAOf/oAEf/wwBRAAYAUv/5AGD/8wBj/+IAZ//iAHH/1AB0//AAdf/qAHb/6gB3/+oAev/vAHz/1AB///QAg//tAIT/7wCG/+kAiP/8AIkAEACKABMAiwAGAJX/4gCZ/+IAn//zAKoAAQCs/7UAvP/cAL//6wDB/4kAw//4AMX/7QDI/+gAyv/nANP/6QDU/+gA1f/kANb/6ADa/+AADAA6/+gAQf/sAEL/6wBE/+IAVf/8AHH//wB0//oAuf/4AMP/+gDT//QA1P/zANb/9AAKAEf/+QBj//gAcf/2AHT/+ACKAAUAmf/3ALz/+gDD//gA1v//ANr//wAVACH/8QAr//AANP/8AEf/9gBj//cAcf/0AHT/+QCF//8Ah///AIkABACKAAcAjv//AJX//gCZ//cArP/3ALz/9QDB/+wAw//6AMr//gDV//8A2v/9AAEAVgADACUAA//zACEAAQAt/94AM//6ADQACQA5//cAR//+AFEABwBVAAQAWAAFAFoABgBhAAYAYv/xAGP/5ABx/+cAdP/0AHwACgCD//EAhAABAIb/5gCJAAQAigAXAIsACACZ/+MApf/6AKoACgCzAAYAtAAGALv/8QC+AAMAw//1AMgABgDK//AA0//dANT/2wDW/90A2//5ACAAA//lACj/awAt/9MAOf/7ADr/jgA8/9UAQf+WAEL/lABE/4sAUf+SAFX/qQBi/+oAY//oAHH/7gB0//UAg//RAIb/vgCZ/+kAo/+UAKT/kwCw/+8Atv+TALj/lAC5/5YAu//qAL//9wDBAAQAw//vAMr/9QDT/7YA1P+xANb/sAAGAHz/7QCO/9oAn//tAL//5QDF/+AAyP/0ADAAA//hABv/+wAt/+YAM//8ADQABgA5//UAOv+5ADz/4wBB/8kAQv/IAET/twBH//gATf/yAFH/vgBS//YAVf/DAFoAAQBhAAEAYv/qAGP/7wBt//IAcf/xAHT/8gB8AAYAg//xAIb/8QCO//4Amf/vAKP/0wCk/84AqgAGALD/5wCzAAEAtAABALb/uwC4/7wAuf+7ALv/6gC8//oAv//oAMD/8ADD/+kAyAADAMr/8wDT/+AA1P/dANb/3QDb/+8AHwAb//kAIf/cACv/5gA0/+0AOf//ADr/3gBB/+cAQv/mAEP/5ABE/9YARv/tAEf/+QBR//oAVf/wAHH//gB8//gAhf//AIf/+wCV//sAqv/yAKz/7QC2//kAuP/6ALn/8wC8//4Awf/ZAMr//wDU//8A1f/0ANb//ADa//4ABwBB//wAQv/8AEP/+wBE//kAUQAGAFUAAwCqAAQAIgAh/7AAK//AAC3/7QA0/xEAOf/8AEEABgBCAAYAQwAHAEQABwBH/+IAY//aAG3//ABx/9gAdP/7AHr/3wB8/7QAigAQAIsAAgCV/+oAlv/kAJn/2wCf/+0AvP/gAMD/8gDB/6MAxf/nAMj/6gDK/+sA0//wANT/8ADV//wA1v/xANr/+QDb/9wAHAAD/+UAIf+fACv/0QA0/8oAOv/8AEH/9ABC//QAQ//vAET/8ABG//cAR//2AGP/9ABx/+kAev/8AHz/3gCD//MAhv/wAIkABACKAAkAmf/zAKr//ACs/7UAvP/5AMH/ogDTAAMA1AAEANUAAgDWAAUADgAh//wAK//9ADQABgBD//wAWAADAFoAAwBhAAMAfAAHAKoABwCzAAMAtAADAMH/+gDIAAQA1v/+AB4AG//+ACv/+AAt//wANAADADr/7wA8//0AQf/sAEL/6wBE/+UAR//2AFX/+gBj/+0Acf/nAHT//AB8AAMAg//xAIX/+wCG//kAh//5AI7/+gCV//kAmf/sAKoAAwC4//4AvP/7AMP//ADK//cA0//8ANT//ADW//wAGgAr//IAOv/4AEH/8QBC//EAQ//3AET/7QBH//8Acf//AHT/9QCF//8Ah///AIkABwCKAAoAjv//AJX//gCj//gAvP/9AL//9gDB//0Aw//1AMr//gDT/+oA1P/qANX/9wDW/+oA2v/9ADUAA//lACH/lQAr/7kALf/fADT/wwA5//cAR/+dAE3/+ABRAA8AUv/GAFP/qQBg/9MAYv/oAGP/mABn/6YAbf/5AHH/qAB0/+IAdf/dAHb/3QB3/9IAeP/nAHr/yAB8/74Af//rAIP/vwCE/80Ahv+9AIj/+gCJABAAigAUAIsABgCV/6YAlv/IAJn/lwCf/8wAqgABAKz/uwC7/+gAvP+bAL//3QDA//EAwf+oAMP/9wDF/84AyP/RAMr/oADT/7QA1P+0ANX/ugDW/7YA2v+wANv/ygAbABv//wAh/80AK//lADT/6AA5//8AOv/GAEH/4gBC/+IAQ//TAET/xwBG/+cAR///AFH/6gBV/+cAWP/8AFr//ACG//oAqv/vAKz/4QCw//cAtv/gALj/4wC5/88Awf/TANT//ADV//kA1v/6ABYAIf/iACv/4wA0/+0AR//zAGP/9QBx//IAdP/5AHz/9gCF//oAh//6AIkABACKAAgAjv/6AJX/+gCZ//UArP/uALz/8gDB/9QAw//7AMr/+ADV//8A2v/6ADUAA//dABv/+wAh/6sAK//JAC3/5gA0/8EAOf/vAEf/zQBN/+wAUQAKAFL/2gBT//MAVQAGAFoAAQBg//EAYv/qAGP/wwBn/9kAbf/vAHH/vQB0/+kAev/eAHz/wQB//+oAg//VAIT/5ACG/9UAiP/4AIkADQCKABgAiwALAJX/2QCW/+MAmf/CAJ//7gCqAAYArP+3ALYAAQC4AAIAu//qALz/zgDA/+wAwf+pAMP/9wDF/+oAyP/rAMr/2gDT//AA1P/xANX/8wDW//IA2v/uANv/4AA3AAP/3QAb//sAIf+rACv/yAAt/+YANP/AADn/7wBH/80ASv/zAE3/7ABRAAkAUv/ZAFP/8wBVAAYAWAABAFoAAgBg//EAYv/qAGP/wgBn/9kAbf/vAHH/vAB0/+kAev/eAHz/wAB//+oAg//UAIT/5ACG/9UAiP/4AIkADQCKABkAiwALAJX/2QCW/+IAmf/BAJ//7QCqAAcArP+2ALYAAwC4AAMAu//qALz/zADA/+wAwf+pAMP/9wDF/+oAyP/rAMr/2QDT//AA1P/xANX/8gDW//IA2v/uANv/4AAlAAP/+AAt/+MAM//6ADQABAA5//kAR//8AFEACgBVAAcAWAACAFoAAwBi//IAY//eAGf//QBx/98AdP/zAHwABQB///0Ag//uAIb/5ACI//0AiQAIAIoAGQCLAAsAlf/6AJn/3ACl//cAqgAIALYAAwC4AAMAu//yAMP/+gDIAAEAyv/qANP/4gDU/+EA1v/jANv/9AA5AAP/2gAb//sAIf+jACv/twAt/9cANP+9ADn/6gBH/6wASv/0AE3/5wBRAAoAUv/IAFP/8gBVAAcAWAADAFoAAwBg/+QAYv/fAGP/qwBn/78Aa//sAG3/6QBx/6cAdP/dAHr/1AB8/7UAf//gAIP/vgCE/9IAhv+8AIj/9gCJAAsAigAaAIsADQCV/78Alv/TAJn/qQCc/+wAn//dAKoACACs/7AAtgAEALgABAC7/98AvP+qAMD/5ADB/5gAw//wAMX/3QDI/90Ayv/CANP/2ADU/9kA1f/dANb/2wDa/9kA2//RABUALf/uAEf/+wBi//QAY//uAGf/+gBx//AAdP/zAIP/9gCG//EAiQAIAIoACwCV//gAmf/uALv/9AC8//8Aw//3AMr/8QDT/+oA1P/rANb/6wDb//kAFwAb//kAIP//AC3/+QA5//wAOv+WADz/9QBB/8kAQv/IAET/rABG//wAUf/mAFX/2AB0//8Ao//8AKT/9QCw//QAtv/oALj/6QC5/+4Aw//5ANP/7gDU/+0A1v/vABQAIQAGACsADQAzAAsAOv/WADz//ABB/9UAQv/VAEMAEABE/8oARgAEAKUABAC4/9kAuf/YALwABADBABwA0//tANT/7QDVAAwA1v/sANoABAAVACH/qAAr/74ALf/5ADoADwBBAAEAQgAJAEMACgBEAAoAR//yAGP/0wBx/80AdP/6AIkAEQCKABQAiwAEAJn/4QC8/+4Awf+gANMABgDUAAcA1QAHAAcAK//1ADr/yABB/9sAQv/bAET/ygC4/94Auf/eAB8AG//1ACD/+AAh/+oAK//wADn/+AA6/5gAPP/1AEH/wgBC/8IAQ//dAET/qwBG/+sAUf/UAFX/2gB0//0Ao//6AKT/8QCq/+8ArP/6ALD/8gC2/8MAuP/HALn/twC8//8Awf/rAMP/+QDT/+4A1P/tANX/7QDW/+4A2v/0ABUAIQACACsABQAt/+4AMwADADr/xAA8/+4AQf/DAEL/wQBDAAQARP++ALj/rAC5/6oAv//yAMD//QDBAAoAw//8ANP/4ADU/90A1QAEANb/3gDb//0ABAAkAAMAiQACAIoABgCMAD8ABwBCAAEAQwACAEQAAwCJAAgAigAMAIwACQDBAAYACQArAAEAQQABAEIAAgBDAAMARAADAIkACACKAAwAjAALAMEABgAcABv/+gAr//oALf/7ADn/+AA6/6AAPP/4AEH/yQBC/8kAQ//8AET/tABG//8AUf/uAFX/5ABj//oAcf/5AIP/9ACG/+8Amf/6ALD/+QC2/+8AuP/xALn/+AC8//sAwf//ANP/+QDU//cA1f/8ANb/9gABAIwABgAEADr/0wBB//EAQv/xAET/5AALABv//gAt//oAOv/8ADz/+ABB//wAQv/8AET//ADD//8A0//+ANT//QDW//8ABgB6/+0AfP+qAJb/5gCf//QAxf/wANv/7QACAL//9gDF//UAGwAb//cAIP/5ACH/7wAr//IAOf/6ADr/mQA8//gAQf/HAEL/xgBD/+oARP+cAEb/7wBR/+QAVf/cAKT/+gCq//IAsP/zALb/5QC4/+gAuf/sAMH/7gDD//sA0//yANT/8ADV/+wA1v/wANr/+AAHACv/8QA6//gAQf/vAEL/7wBE/+gArf/5AMH/8QAEAHz/9wCf//MAv//tAMX/6QAaABv/+AAg//oAIf/pACv/7gA0//wAOf/5ADr/4gA8//cAQf/jAEL/4gBD/+UARP/cAEb/5QBR//MAVf/5AKr/+AC2//QAuP/0ALn/9QDB/+kAw//9ANP/9ADU//MA1f/xANb/8wDa//oAAQCKAAQAHgAD/+8AIf/FACv/2QA0/+UAOf//ADoAGwBBACAAQgAgAEMAKABEACUARgAIAEf/+ABRAAwAVQAWAFgACABaAAkAY//6AHH/6QCD/+gAhv/kAIkAEQCKACkAiwASAJn/+QCqABYArP/fALYAAwC4AAMAwf/SANr//AABAIoABgABAIoAAwALACj/9AArAAQAOv/UAEH/8wBC//MARP/qAFX/+gCG//UAkv/4AK3/5wDBAAQAAQB8//QAEAAo//EAKwAEADr/yQBB/+AAQv/gAEMAAgBE/9YAVf/jAGEAAwBk//MAhv/4AJL/+wCt//EAuf/8AL//9QDBAAgACgAt//sAOf//ADr/pQA8//oAQf/ZAEL/1wBD//oARP+/AEb/+QCMACUAHAAb//QAIP/3ACH/+AAr//QALf/6ADn//QA6/98APP/zAEH/3wBC/98AQ//qAET/1ABG//UAUf/2AFX/9AB0//oAo//6ALb/9wC4//YAuf/1ALz//wDB//QAw//5ANP/7wDU/+4A1f/vANb/7wDa//kABAA6/80AQf/kAEL/5ABE/9EAFAAb//kAIf/nACv/8QA6/78AQf/UAEL/1ABD/+4ARP++AEb/9QB0//gAuP/qALn/+gC8//gAwf/pAMP/9wDT/+cA1P/lANX/5ADW/+YA2v/pABQALf/7ADn/+wA6/5gAPP/3AEH/zABC/8sAQ//9AET/swBG//gAUf/eAFX/3wCk//gAsP/0ALb/0QC4/9MAuf+9AMP//ADT//UA1P/0ANb/9QAWACH/xAAr//EAOv+9AEH/1QBC/9UAQ//kAET/vABG//IAdP/6AHz/7wCf/+kAvP/5AL//4gDB//AAw//5AMX/1QDI//kA0//qANT/6QDV/+EA1v/pANr/4gAGAC3//wA5//8APP/6AEb/+gCJAAUAigAIAAUAUQADAFUAAwCqAAcAtgACALgAAgAPAFEAEQBWAAIAWAAIAFoACAB/AAIAhQAFAIcABQCOAAYAowADAKQABwCqAAQAsAAHALYACAC4AAgAuQAEABEAUQAUAFUAEABWAAYAWAAMAFoADAByAAQAfwAGAIUACACHAAgAjgAJAKMACQCkAA0AqgASALAADQC2AA0AuAANALkACAABAIwAIAAaAC3/8wA0AAYAOv+4ADz//gBB//IAQv/yAET/2wBH//cAUQAGAFgAAQBaAAEAYQADAGP/6ABx/+MAdP//AIP/4wCG/94Amf/nAKX/+gCqAAYAswADALQAAwC2//QAuP/4ALn/1gC8//sAHwAD/+QAIP/+ACj/uAAt//IANAAMADr/6QA8/+8AQf/oAEL/5wBE/+YAUf/sAFX/8wBi//kAY///AHH//wB0//wAg//wAIb/8QCZ//8Ao//uAKT/7gCqAAcAtv/tALj/7QC5/+4Au//5AMEAAQDD//oA0//wANT/7QDW//AABAB8/+wAn//tAL//5gDF/98AEwAt//sAOf/7ADr/mQA8//cAQf/MAEL/ywBD//0ARP+1AEb/+ABR/+4AVf/gALD/9gC2//EAuP/yALn/9gDD//wA0//2ANT/9gDW//YACAA6/8cAQf/fAEL/3wBE/9AAVf/gAGT/4wC5/+oAv//zAAEAfP/4AB0AG//1ACD/9wAh/+oAK//vADn/+AA6/5YAPP/1AEH/wgBC/8EAQ//cAET/qQBG/+sAUf/hAFX/2wB0//wApP/4AKr/7wCw//MAtv/jALj/5QC5/+oAvP//AMH/6gDD//gA0//uANT/7ADV/+wA1v/tANr/8wASACj/7AArAAQAOv/GADz/+ABB/9kAQv/ZAEMABABE/88AVf/bAGT/7QBw//cAhv/xAJL/7gCYAAMArf/rALn/8QC///YAwQAJAAEAUf/+ABkAIQADACsABgAt//EAMwAEADoAAQBBAAcAQgAHAEMACABEAAgAY//vAHH/8AB0//0AiQAEAIoAEgCLAAcAjAAIAJn/8ADA//0AwQALAMr/+ADT//MA1P/yANUABADW//UA2//xABEALf/tADr/uwA8/+0AQf+3AEL/tgBE/7EAY//6AHT//gC2/3kAuP98ALn/hwC//+AAwQABAMP//QDT/9IA1P/PANb/0AAGAG3/+QB8/94An//3AL//6wDF/+4AyP/4AA4ALf/7ADn//wA6/6UAPP/6AEH/2QBC/9cAQ//6AET/vwBG//kAYQAEAIwAXgCzAAQAtAAEAL4AAgAgABv/7AAg//MAIf/iACv/7AAt/+sAOf/tADr/vAA8/+sAQf/OAEL/zgBD/+8ARP/CAEb/6wBH/+gAY//pAHH/6AB0/+0Ahf/vAIf/7wCMAFkAjv/tAJX/7wCZ/+kAvP/oAMH/7gDD/+sAyv/sANP/4ADU/98A1f/wANb/6ADa/+8AAQAD/+EAAQCMAAoADQAh/6kAK/+/AC3/+gBH//QAY//KAHH/zgB0//oAiQAEAIoACgCZ/+kArP9/ALz/+ADB/6EAEQAD/+QAIf+pACv/vgAt//kANP+nAEf/9ABS/90AY//JAHH/zQB0//oAg//tAIkABACKAAgAmf/oAKz/fgC8//cAwf+gABYAA//iACH/qwAr/7sALf/zADT/owBH//gAUv/bAGP/twBx/8gAdP/6AHr/8QB8/6wAg//6AIkABACKAAgAlv/wAJn/6gCs/4cAvP/8AMH/nwDF//cA2//1ABgAA//qACD//wAh/68AK//TADT/2gA5//8AOv++AEH/9wBC//YAQ//jAET/4wBG/+cAR//2AFL/9ABj/+kAcf/dAIP/2ACE//IAhv/bAJn/6ACq//wArP/QALz/+wDB/8oAFgAb//gAIP/6ACv/9wAt//4AOv+iADz/9QBB/9IAQv/RAEP//ABE/7kARv/8AFH/+ABV/+YAdP//AIb/+AC2//oAuP/6AMP//wDT//YA1P/0ANX/+gDW//QAAQCMAAgAEQAh/8sAKP/rACv/2AA0/84AOv/rAEb/9ABf//AAZAABAHD/9AB6//EAfP/QAIb/5gCS/+0ArP+/AK3/9QC/AAMAwf/LAAcAK//yADr/9gBB/+8AQv/vAET/6QDB/+8Axf/8ABUAIP//AC3/9wA6/80APP/1AEH/5QBC/+QARP/QAFX/8gBj//UAcf/0AHT//wCD/+wAhv/yAJn/9QC2//kAuP/6ALn/8QDD//8A0///ANT//wDW//8ACgA6/8wAQf/kAEL/5ABDAAQARP/WAFX/5ABk/+sAuf/0AL//9wDBAAgABgA6/80AQf/mAEL/5gBE/9oAVf/oAMEABAAQABv//gAt//oAOv+fADz/+ABB/9gAQv/XAET/ugBG//wAUf/9AFX/5wC2//0AuP/8AMP//wDT//4A1P/9ANb//wAZAAP/5QAb//gAIf+1ACv/3wA0/98AOv+zAEH/8ABC//AAQ//iAET/1wBG/+kAR//zAFEABgBS//kAVf/zAGP/7wBx/+YAg//nAIb/6gCZ/+4ApAABAKr/8wCs/9IAvP/zAMH/zQAbAAP/5AAb//gAIf+wACv/3QAt//8ANP/cADn//wA6/7QAQf/xAEL/8QBD/+EARP/YAEb/6QBH//IAUQAHAFL/+QBV//IAY//tAHH/4wCD/+UAhv/pAJn/7ACkAAIAqv/yAKz/zwC8//IAwf/MABEALf/0ADQABAA6/7oAPP//AEH/8wBC//IARP/dAEf/9wBRAAcAY//tAHH/6AB0//8Ag//kAIb/4QCZ/+wAqgAEALz/+wAaAAP/5QAb//cAIP/8ACH/tQAr/94ANP/fADn//wA6/7EAQf/uAEL/7gBD/98ARP/UAEb/5gBH//IATf/5AFL/+ABV//EAY//tAHH/5ACD/+YAhv/qAJn/7ACq//EArP/RALz/8gDB/8wADgAb//oAIP//AC3//gA6/7EAPP/5AEH/6gBC/+kARP/SAFX/+gBj//QAcf/vAIP/6QCG/+UAmf/0AA8AIf/2ACv/7wA0//wAOv/JAEH/4ABC/98AQ//zAET/0QBG//QAVf/gAGT/7QCq//EAuf/1AL//8gDB/+sAAQAAAAoAHgAsAAFsYXRuAAgABAAAAAD//wABAAAAAWxpZ2EACAAAAAEAAAABAAQABAAAAAEACAABADYAAQAIAAUADAAUABwAIgAoAHYAAwB0AIcAdwADAHQAjgB1AAIAdAB4AAIAhwB5AAIAjgABAAEAdA==) format('truetype');}
@font-face {
font-family: 'Georgia';
font-style: normal;
font-weight: 700;
src: url(data:font/ttf;base64,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ABEAK//yABEAOv/rABEAQf/sABEAQv/rABEAQ//yABEARP/jABEARv/+ABEAY//9ABEAcf/8ABEAdP/0ABEAiQAKABEAigAMABEAlf/9ABEAmf/9ABEAvP/5ABEAv//7ABEAwf/1ABEAw//1ABEAxf/9ABEAyv/9ABEA0//3ABEA1P/1ABEA1f/zABEA1v/2ABEA2v/7ABIAK//2ABIALf/4ABIAOf/+ABIAOv/8ABIAQf/1ABIAQv/1ABIAQ//6ABIARP/vABIAUQARABIAY//7ABIAcf/7ABIAdP/4ABIAiQASABIAigAfABIAlf/9ABIAmf/7ABIAvP/6ABIAwf/4ABIAw//7ABIAyv/9ABIA1P/9ABIA1v/8ABIA2v/8ABUAG//6ABUAIf/jABUAK//nABUANP/rABUAOf/8ABUAOv/qABUAQf/oABUAQv/mABUAQ//kABUARP/ZABUARv/zABUAR//4ABUAVf/xABUAcf/7ABUAfP/9ABUAhf/9ABUAh//9ABUAlf/7ABUAqv/0ABUArP/4ABUAtv/9ABUAuf/8ABUAvP/7ABUAwf/ZABUAyv/9ABUA1P/9ABUA1f/2ABUA1v/7ABUA2v/7ABYALf/0ABYAOf/3ABYAR//9ABYAY//yABYAcf/yABYAdP/yABYAg//6ABYAhv/5ABYAiQASABYAigAbABYAlf/+ABYAmf/yABYAvP/+ABYAv//5ABYAw//2ABYAyv/3ABYA0//2ABYA1P/yABYA1v/xABwAxf/9AB0AA//pAB0AIf+gAB0AK//HAB0ALf/yAB0ANP/LAB0AOf/vAB0AR//XAB0AUQAPAB0AUv/9AB0AYP/6AB0AY//lAB0AZ//rAB0Acf/bAB0AdP/zAB0Adf/2AB0Adv/2AB0Ad//2AB0Aev/zAB0AfP/eAB0Af//7AB0Ag//3AB0AhP/4AB0Ahv/2AB0AiP/4AB0AiQAlAB0AigAtAB0AiwANAB0Alf/rAB0Amf/lAB0An//6AB0AqgAEAB0ArP/LAB0AvP/fAB0Av//3AB0Awf+jAB0Aw//8AB0Axf/3AB0AyP/1AB0Ayv/uAB0A0//2AB0A1P/1AB0A1f/zAB0A1v/1AB0A2v/rAB4AOv/uAB4AQf/pAB4AQv/oAB4ARP/gAB4AVf/4AB4Acf/9AB4AdP/6AB4Auf/8AB4Aw//5AB4A0//0AB4A1P/yAB4A1v/0ACAAR//5ACAAY//4ACAAcf/1ACAAdP/4ACAAigAMACAAmf/3ACAAvP/6ACAAw//4ACAA1v/9ACAA2v/8ACEAIf/xACEAK//vACEANP/2ACEAR//2ACEAY//3ACEAcf/0ACEAdP/5ACEAhf/9ACEAh//9ACEAiQAJACEAigARACEAjv/9ACEAlf/7ACEAmf/3ACEArP/8ACEAvP/0ACEAwf/oACEAw//6ACEAyv/7ACEA1f/8ACEA2v/6ACQAVgAHACYAA//zACYAIQAEACYALf/bACYAM//yACYANAAWACYAOf/2ACYAR//7ACYAUQARACYAVQAKACYAWAAMACYAWgANACYAYQANACYAYv/xACYAY//hACYAcf/kACYAdP/tACYAfAAXACYAg//0ACYAhAAEACYAhv/pACYAiQAKACYAigA2ACYAiwAVACYAmf/gACYApf/xACYAqgAXACYAswANACYAtAANACYAu//xACYAvgAHACYAw//uACYAyAAPACYAyv/wACYA0//aACYA1P/XACYA1v/bACYA2//9ACcAA//lACcAKP+CACcALf/kACcAOf/+ACcAOv+cACcAPP/jACcAQf+mACcAQv+hACcARP+YACcAUf+bACcAVf+vACcAYv/2ACcAY//1ACcAcf/4ACcAdP/vACcAg//rACcAhv/iACcAmf/2ACcAo/+eACcApP+dACcAsP/4ACcAtv+cACcAuP+dACcAuf+eACcAu//2ACcAv//8ACcAwQAKACcAw//qACcAyv/7ACcA0//HACcA1P+7ACcA1v/DACgAfP/3ACgAjv/dACgAn//3ACgAv//zACgAxf/sACgAyP/7ACsAA//hACsAG//+ACsALf/mACsAM//3ACsANAANACsAOf/4ACsAOv++ACsAPP/kACsAQf/JACsAQv/IACsARP+7ACsAR//4ACsATf/zACsAUf/HACsAUv/8ACsAVf/GACsAWgADACsAYQAEACsAYv/tACsAY//vACsAbf/zACsAcf/xACsAdP/vACsAfAANACsAg//0ACsAhv/0ACsAjv/7ACsAmf/vACsAo//XACsApP/TACsAqgAOACsAsP/0ACsAswAEACsAtAAEACsAtv/EACsAuP/FACsAuf/FACsAu//tACsAvP/9ACsAv//1ACsAwP/xACsAw//lACsAyAAGACsAyv/1ACsA0//hACsA1P/dACsA1v/fACsA2//xAC0AG//5AC0AIf/jAC0AK//mAC0ANP/rAC0AOf/8AC0AOv/oAC0AQf/nAC0AQv/lAC0AQ//kAC0ARP/YAC0ARv/xAC0AR//4AC0AUf/9AC0AVf/vAC0Acf/7AC0AfP/8AC0Ahf/9AC0Ah//7AC0Alf/7AC0Aqv/yAC0ArP/3AC0Atv/9AC0AuP/9AC0Auf/6AC0AvP/7AC0Awf/XAC0Ayv/9AC0A1P/9AC0A1f/0AC0A1v/+AC0A2v/7ADMAQf/3ADMAQv/2ADMAQ//0ADMARP/wADMAUQAPADMAVQAHADMAqgAKADQAIf+2ADQAK//DADQALf/rADQANP74ADQAOf/3ADQAQQAOADQAQgAPADQAQwAQADQARAARADQAR//iADQAY//aADQAbf/4ADQAcf/cADQAdP/0ADQAev/cADQAfP+0ADQAigAmADQAiwAFADQAlf/pADQAlv/hADQAmf/aADQAn//qADQAvP/dADQAwP/wADQAwf+hADQAxf/nADQAyP/pADQAyv/qADQA0//wADQA1P/wADQA1f/2ADQA1v/xADQA2v/wADQA2//ZADYAA//lADYAIf+pADYAK//NADYANP/GADYAOv/+ADYAQf/0ADYAQv/0ADYAQ//sADYARP/wADYARv/5ADYAR//2ADYAY//0ADYAcf/oADYAev/3ADYAfP/eADYAg//0ADYAhv/0ADYAiQALADYAigAWADYAmf/zADYAqv/1ADYArP+/ADYAvP/3ADYAwf+pADYA0wAHADYA1AAJADYA1QAFADYA1gAMADcAIf/2ADcAK//5ADcANAAPADcAQ//1ADcAWAAGADcAWgAHADcAYQAHADcAfAARADcAqgARADcAswAHADcAtAAHADcAwf/zADcAyAAJADcA1v/7ADgAG//7ADgAK//8ADgALf/4ADgANAAGADgAOv/vADgAPP/5ADgAQf/lADgAQv/kADgARP/dADgAR//0ADgAVf/yADgAY//rADgAcf/lADgAdP/3ADgAfAAHADgAg//0ADgAhf/7ADgAhv/9ADgAh//5ADgAjv/3ADgAlf/5ADgAmf/qADgAqgAHADgAuP/7ADgAvP/+ADgAw//2ADgAyv/1ADgA0//4ADgA1P/2ADgA1v/3ADkAK//yADkAOv/8ADkAQf/xADkAQv/xADkAQ//3ADkARP/tADkAR//9ADkAcf/9ADkAdP/zADkAhf/9ADkAh//9ADkAiQAQADkAigAXADkAjv/9ADkAlf/7ADkAo//8ADkAvP/5ADkAv//8ADkAwf/5ADkAw//yADkAyv/7ADkA0//sADkA1P/qADkA1f/1ADkA1v/sADkA2v/6ADoAA//kADoAIf+iADoAK/++ADoALf/pADoANP/KADoAOf/5ADoAR/+wADoATf/8ADoAUQATADoAUv/VADoAU//BADoAYP/rADoAYv/1ADoAY/+pADoAZ//NADoAbf/9ADoAcf+vADoAdP/hADoAdf/wADoAdv/wADoAd//WADoAeP/0ADoAev/cADoAfP/FADoAf//3ADoAg//MADoAhP/oADoAhv/DADoAiP/zADoAiQAlADoAigAuADoAiwANADoAlf/NADoAlv/aADoAmf+nADoAn//hADoAqgAEADoArP/BADoAu//1ADoAvP+rADoAv//wADoAwP/5ADoAwf+rADoAw//8ADoAxf/pADoAyP/rADoAyv+9ADoA0//RADoA1P/RADoA1f/UADoA1v/TADoA2v/EADoA2//dADsAG//8ADsAIf/gADsAK//lADsANP/kADsAOf/8ADsAOv/cADsAQf/hADsAQv/gADsAQ//VADsARP/KADsARv/uADsAR//8ADsAUf/wADsAVf/kADsAWP/3ADsAWv/2ADsAhv/9ADsAqv/sADsArP/rADsAsP/8ADsAtv/nADsAuP/qADsAuf/iADsAwf/QADsA1P/+ADsA1f/4ADsA1v/6ADwAIf/kADwAK//lADwANP/rADwAR//zADwAY//1ADwAcf/yADwAdP/5ADwAfP/8ADwAhf/6ADwAh//6ADwAiQALADwAigAUADwAjv/6ADwAlf/3ADwAmf/1ADwArP/yADwAvP/yADwAwf/UADwAw//7ADwAyv/4ADwA1f/8ADwA2v/3AEEAA//dAEEAG//+AEEAIf+uAEEAK//JAEEALf/mAEEANP/EAEEAOf/tAEEAR//LAEEATf/vAEEAUQAYAEEAUv/dAEEAU//gAEEAVQANAEEAWgADAEEAYP/vAEEAYv/tAEEAY//GAEEAZ//XAEEAbf/xAEEAcf+/AEEAdP/lAEEAev/gAEEAfP/IAEEAf//qAEEAg//ZAEEAhP/qAEEAhv/bAEEAiP/tAEEAiQAeAEEAigA5AEEAiwAZAEEAlf/XAEEAlv/mAEEAmf/EAEEAn//uAEEAqgAPAEEArP/BAEEAtgAEAEEAuAAFAEEAu//tAEEAvP/MAEEAwP/vAEEAwf+rAEEAw//0AEEAxf/uAEEAyP/uAEEAyv/aAEEA0//yAEEA1P/0AEEA1f/zAEEA1v/0AEEA2v/lAEEA2//jAEIAA//dAEIAG//+AEIAIf+uAEIAK//IAEIALf/lAEIANP/BAEIAOf/sAEIAR//LAEIASv/gAEIATf/vAEIAUQAWAEIAUv/cAEIAU//gAEIAVQAPAEIAWAAEAEIAWgAFAEIAYP/uAEIAYv/tAEIAY//CAEIAZ//WAEIAbf/xAEIAcf+8AEIAdP/jAEIAev/fAEIAfP/HAEIAf//qAEIAg//YAEIAhP/pAEIAhv/ZAEIAiP/tAEIAiQAeAEIAigA8AEIAiwAbAEIAlf/WAEIAlv/kAEIAmf/BAEIAn//tAEIAqgARAEIArP++AEIAtgAGAEIAuAAGAEIAu//tAEIAvP/JAEIAwP/vAEIAwf+pAEIAw//0AEIAxf/uAEIAyP/uAEIAyv/YAEIA0//yAEIA1P/zAEIA1f/yAEIA1v/0AEIA2v/kAEIA2//jAEMAA//8AEMALf/jAEMAM//zAEMANAAKAEMAOf/5AEMAR//2AEMAUQAXAEMAVQAQAEMAWAAFAEMAWgAGAEMAYv/yAEMAY//bAEMAZ//5AEMAcf/cAEMAdP/rAEMAfAAMAEMAf//6AEMAg//wAEMAhv/nAEMAiP/5AEMAiQAUAEMAigA8AEMAiwAbAEMAlf/3AEMAmf/ZAEMApf/qAEMAqgASAEMAtgAHAEMAuAAHAEMAu//yAEMAw//yAEMAyAADAEMAyv/qAEMA0//iAEMA1P/gAEMA1v/jAEMA2//0AEQAA//aAEQAG//+AEQAIf+nAEQAK/+7AEQALf/ZAEQANP/BAEQAOf/mAEQAR/+zAEQASv/jAEQATf/qAEQAUQAYAEQAUv/PAEQAU//eAEQAVQARAEQAWAAHAEQAWgAHAEQAYP/kAEQAYv/kAEQAY/+xAEQAZ//GAEQAa//RAEQAbf/rAEQAcf+uAEQAdP/ZAEQAev/YAEQAfP+9AEQAf//hAEQAg//GAEQAhP/bAEQAhv/GAEQAiP/oAEQAiQAaAEQAigA+AEQAiwAeAEQAlf/GAEQAlv/YAEQAmf+vAEQAnP/RAEQAn//hAEQAqgAUAEQArP+3AEQAtgAJAEQAuAAKAEQAu//kAEQAvP+uAEQAwP/oAEQAwf+cAEQAw//tAEQAxf/kAEQAyP/kAEQAyv/IAEQA0//fAEQA1P/gAEQA1f/hAEQA1v/jAEQA2v/SAEQA2//WAEYALf/yAEYAR//7AEYAYv/7AEYAY//xAEYAZ//9AEYAcf/zAEYAdP/wAEYAg//8AEYAhv/5AEYAiQATAEYAigAbAEYAlf/4AEYAmf/xAEYAu//7AEYAvP/9AEYAw//0AEYAyv/0AEYA0//xAEYA1P/yAEYA1v/yAEYA2//9AEcAG//9AEcAIP/9AEcALf/3AEcAOf/+AEcAOv+qAEcAPP/xAEcAQf/JAEcAQv/HAEcARP+vAEcARv/+AEcAUf/kAEcAVf/RAEcAdP/9AEcAo//3AEcApP/xAEcAsP/7AEcAtv/hAEcAuP/lAEcAuf/nAEcAw//3AEcA0//rAEcA1P/mAEcA1v/sAE0AIQAPAE0AKwAgAE0AMwAaAE0AOv/WAE0APP/3AE0AQf/XAE0AQv/VAE0AQwAfAE0ARP/NAE0ARgAIAE0ApQALAE0AuP/dAE0Auf/bAE0AvAAIAE0AwQAwAE0A0//wAE0A1P/tAE0A1QAcAE0A1v/vAE0A2gAJAFEAIf+vAFEAK//HAFEALf/9AFEAOgATAFEAQQAEAFEAQgAWAFEAQwAXAFEARAAXAFEAR//5AFEAY//eAFEAcf/WAFEAdP/9AFEAiQApAFEAigAxAFEAiwALAFEAmf/lAFEAvP/uAFEAwf+nAFEA0wANAFEA1AAQAFEA1QARAFIAK//1AFIAOv/WAFIAQf/eAFIAQv/dAFIARP/QAFIAuP/lAFIAuf/mAFQAG//7AFQAIP/4AFQAIf/xAFQAK//wAFQAOf/2AFQAOv+pAFQAPP/1AFQAQf/FAFQAQv/CAFQAQ//bAFQARP+yAFQARv/uAFQAUf/eAFQAVf/aAFQAdP//AFQAo//9AFQApP/0AFQAqv/vAFQArP/9AFQAsP/5AFQAtv/TAFQAuP/YAFQAuf/RAFQAvP/9AFQAwf/rAFQAw//5AFQA0//wAFQA1P/tAFQA1f/tAFQA1v/wAFQA2v/3AFUAIQAFAFUAKwAMAFUALf/uAFUAMwAHAFUAOv/LAFUAPP/tAFUAQf/GAFUAQv/DAFUAQwAKAFUARP/DAFUAuP+vAFUAuf+uAFUAv//5AFUAwP/5AFUAwQAXAFUAw//3AFUA0//kAFUA1P/dAFUA1QAJAFUA1v/hAFUA2//5AFYAJAAHAFYAiQAFAFYAigAOAFYAjABEAFcAQgAEAFcAQwAFAFcARAAGAFcAiQAUAFcAigAcAFcAjAAWAFcAwQANAFkAKwADAFkAQQAEAFkAQgAFAFkAQwAGAFkARAAGAFkAiQAUAFkAigAcAFkAjAAaAFkAwQAOAF0AG//9AF0AK//6AF0ALf/7AF0AOf/4AF0AOv+wAF0APP/4AF0AQf/LAF0AQv/LAF0AQ//3AF0ARP+7AF0ARv/9AF0AUf/yAF0AVf/jAF0AY//6AF0Acf/5AF0Ag//7AF0Ahv/4AF0Amf/6AF0AsP/9AF0Atv/yAF0AuP/0AF0Auf/8AF0AvP/7AF0Awf/9AF0A0//5AF0A1P/3AF0A1f/8AF0A1v/2AF4AjAAOAGAAOv/rAGAAQf/vAGAAQv/uAGAARP/kAGEAjAAXAGMAG//7AGMALf/3AGMAOv/2AGMAPP/1AGMAQf/3AGMAQv/3AGMARP/2AGMAw//8AGMA0//7AGMA1P/5AGMA1v/8AGQAev/tAGQAfP+uAGQAlv/qAGQAn//7AGQAxf/5AGQA2//yAGYAv//8AGYAxf/1AGgAG//8AGgAIP/5AGgAIf/zAGgAK//yAGgAOf/3AGgAOv+kAGgAPP/4AGgAQf/IAGgAQv/GAGgAQ//lAGgARP+jAGgARv/vAGgAUf/oAGgAVf/bAGgApP/9AGgAqv/yAGgAsP/6AGgAtv/oAGgAuP/rAGgAuf/tAGgAwf/sAGgAw//7AGgA0//yAGgA1P/uAGgA1f/sAGgA1v/wAGgA2v/5AG0AK//zAG0AOv/8AG0AQf/xAG0AQv/xAG0ARP/rAG0Arf/9AG0Awf/xAHAAfP/8AHAAn//6AHAAv//3AHAAxf/2AHEAG//8AHEAIP/4AHEAIf/uAHEAK//uAHEANP/3AHEAOf/3AHEAOv/nAHEAPP/3AHEAQf/mAHEAQv/lAHEAQ//jAHEARP/fAHEARv/sAHEAUf/6AHEAVf/9AHEAqv/8AHEAtv/7AHEAuP/7AHEAuf/7AHEAwf/mAHEAw///AHEA0//2AHEA1P/zAHEA1f/xAHEA1v/0AHEA2v/6AHMAigAIAHQAA//vAHQAIf/JAHQAK//bAHQANP/pAHQAOf/9AHQAOgAfAHQAQQAsAHQAQgAtAHQAQwAxAHQARAAwAHQARgAEAHQAR//4AHQAUQANAHQAVQAWAHQAWAAIAHQAWgAJAHQAY//9AHQAcf/yAHQAg//1AHQAhv/zAHQAiQAoAHQAigBGAHQAiwAgAHQAmf/9AHQAqgAdAHQArP/jAHQAtgAHAHQAuAAHAHQAwf/SAHQA2v/+AHUAigADAHYAigAGAHgAigAHAHoAKP/7AHoAKwAKAHoAOv/sAHoAQf/xAHoAQv/xAHoARP/qAHoAVf/yAHoAhv/7AHoAkv/8AHoArf/0AHoAwQAJAHsAfP/kAHwAKP/zAHwAKwAIAHwAOv/dAHwAQf/hAHwAQv/gAHwAQwAFAHwARP/ZAHwAVf/gAHwAYQAHAHwAZP/yAHwAhv/8AHwAkv/0AHwArf/xAHwAuf/1AHwAv//7AHwAwQATAH4ALf/7AH4AOf/9AH4AOv/JAH4APP/3AH4AQf/XAH4AQv/UAH4AQ//3AH4ARP/GAH4ARv/5AH4AjAAhAH8AG//7AH8AIP/3AH8AIf/8AH8AK//0AH8ALf/6AH8AOf/5AH8AOv/lAH8APP/zAH8AQf/dAH8AQv/dAH8AQ//nAH8ARP/UAH8ARv/2AH8AUf/3AH8AVf/0AH8AdP/6AH8Ao//9AH8Atv/3AH8AuP/2AH8Auf/2AH8AvP/9AH8Awf/zAH8Aw//3AH8A0//wAH8A1P/uAH8A1f/wAH8A1v/vAH8A2v/6AIMAOv/oAIMAQf/qAIMAQv/pAIMARP/aAIQAG//9AIQAIf/0AIQAK//0AIQAOv/MAIQAQf/YAIQAQv/YAIQAQ//wAIQARP/GAIQARv/7AIQAdP/8AIQAuP/qAIQAuf/zAIQAvP/8AIQAwf/tAIQAw//8AIQA0//tAIQA1P/oAIQA1f/oAIQA1v/tAIQA2v/2AIUALf/7AIUAOf/7AIUAOv+vAIUAPP/0AIUAQf/MAIUAQv/LAIUAQ//5AIUARP+6AIUARv/4AIUAUf/nAIUAVf/fAIUApP/8AIUAsP/7AIUAtv/fAIUAuP/hAIUAuf/YAIUAw//+AIUA0//4AIUA1P/2AIUA1v/4AIYAIf/lAIYAK//0AIYAOv/CAIYAQf/bAIYAQv/ZAIYAQ//nAIYARP/GAIYARv/5AIYAdP/9AIYAfP/4AIYAn//2AIYAvP/9AIYAv//yAIYAwf/wAIYAw//9AIYAxf/fAIYAyP/9AIYA0//xAIYA1P/tAIYA1f/oAIYA1v/wAIYA2v/yAIcALf/8AIcAOf/9AIcAPP/6AIcARv/6AIcAiQAMAIcAigAUAIgAUQAGAIgAVQAGAIgAqgARAIgAtgAFAIgAuAAFAIkAUQApAIkAVgAFAIkAWAAUAIkAWgAUAIkAfwAFAIkAhQAMAIkAhwAMAIkAjgANAIkAowAGAIkApAARAIkAqgAJAIkAsAARAIkAtgAVAIkAuAAVAIkAuQAKAIoAUQAxAIoAVQAnAIoAVgAOAIoAWAAcAIoAWgAcAIoAcgAIAIoAfwANAIoAhQAUAIoAhwAUAIoAjgAWAIoAowAWAIoApAAeAIoAqgArAIoAsAAfAIoAtgAeAIoAuAAeAIoAuQATAIwAjAAkAI0ALf/xAI0ANAANAI0AOv/RAI0APP/7AI0AQf/wAI0AQv/vAI0ARP/eAI0AR//2AI0AUQANAI0AWAADAI0AWgAEAI0AYQAHAI0AY//oAI0Acf/jAI0AdP/9AI0Ag//oAI0Ahv/lAI0Amf/nAI0Apf/zAI0AqgAPAI0AswAHAI0AtAAHAI0Atv/7AI0AuP/8AI0Auf/tAI0AvP/7AI4AA//oAI4AIP/7AI4AKP+8AI4ALf/rAI4ANAAFAI4AOv/cAI4APP/mAI4AQf/XAI4AQv/WAI4ARP/TAI4AUf/pAI4AVf/vAI4AYv/9AI4AY//8AI4Acf/9AI4AdP/2AI4Ag//5AI4Ahv/5AI4Amf/8AI4Ao//rAI4ApP/rAI4AqgAIAI4Atv/qAI4AuP/qAI4Auf/qAI4Au//9AI4AwQADAI4Aw//zAI4A0//nAI4A1P/hAI4A1v/mAJIAfP/uAJIAn//3AJIAv//0AJIAxf/xAJUALf/7AJUAOf/7AJUAOv+vAJUAPP/0AJUAQf/MAJUAQv/LAJUAQ//5AJUARP+8AJUARv/4AJUAUf/xAJUAVf/fAJUAsP/8AJUAtv/xAJUAuP/yAJUAuf/2AJUAw//+AJUA0//4AJUA1P/2AJUA1v/4AJYAOv/YAJYAQf/hAJYAQv/hAJYARP/UAJYAVf/dAJYAZP/mAJYAuf/tAJYAv//6AJgAfP/8AJkAG//7AJkAIP/3AJkAIf/xAJkAK//vAJkAOf/1AJkAOv+mAJkAPP/1AJkAQf/DAJkAQv/BAJkAQ//ZAJkARP+vAJkARv/uAJkAUf/lAJkAVf/aAJkAdP/8AJkApP/8AJkAqv/vAJkAsP/6AJkAtv/kAJkAuP/oAJkAuf/qAJkAvP/9AJkAwf/pAJkAw//4AJkA0//wAJkA1P/sAJkA1f/rAJkA1v/vAJkA2v/2AJ8AKP/yAJ8AKwALAJ8AOv/WAJ8APP/8AJ8AQf/aAJ8AQv/ZAJ8AQwAIAJ8ARP/SAJ8AVf/YAJ8AZP/qAJ8AcP/8AJ8Ahv/5AJ8Akv/uAJ8AmAAGAJ8Arf/uAJ8Auf/sAJ8Av//8AJ8AwQAWAKUAUf/7AKkAIQAGAKkAKwAPAKkALf/xAKkAMwAJAKkAOgAEAKkAQQARAKkAQgARAKkAQwASAKkARAATAKkAY//vAKkAcf/yAKkAdP/5AKkAiQAJAKkAigArAKkAiwARAKkAjAAUAKkAmf/wAKkAwP/5AKkAwQAZAKkAyv/8AKkA0//zAKkA1P/yAKkA1QAKAKkA1v/7AKkA2//xAKwALf/3AKwAOv/BAKwAPP/yAKwAQf/AAKwAQv++AKwARP+4AKwAY//9AKwAdP/7AKwAtv+AAKwAuP+FAKwAuf+JAKwAv//nAKwAwQADAKwAw//5AKwA0//cAKwA1P/WAKwA1v/aAK0Abf/9AK0AfP/oAK0An//8AK0Av//3AK0Axf/4AK0AyP/8AK8ALf/7AK8AOf/9AK8AOv/JAK8APP/3AK8AQf/XAK8AQv/UAK8AQ//3AK8ARP/GAK8ARv/5AK8AYQAKAK8AjAB4AK8AswAKAK8AtAAKAK8AvgAFALEAG//3ALEAIP/6ALEAIf/rALEAK//3ALEALf/3ALEAOf/3ALEAOv/XALEAPP/3ALEAQf/aALEAQv/aALEAQ//4ALEARP/QALEARv/3ALEAR//1ALEAY//2ALEAcf/1ALEAdP/3ALEAhf/4ALEAh//4ALEAjABSALEAjv/3ALEAlf/4ALEAmf/2ALEAvP/1ALEAwf/4ALEAw//3ALEAyv/3ALEA0//sALEA1P/pALEA1f/5ALEA1v/1ALEA2v/4ALIAA//yALMAjAAXALQAjAAXALYAIf+vALYAK//LALYALf/9ALYAR//7ALYAY//eALYAcf/bALYAdP/9ALYAiQAKALYAigAYALYAmf/wALYArP+LALYAvP/8ALYAwf+qALgAA//rALgAIf+vALgAK//JALgALf/9ALgANP+qALgAR//7ALgAUv/qALgAY//dALgAcf/aALgAdP/9ALgAg//xALgAiQALALgAigAVALgAmf/vALgArP+KALgAvP/8ALgAwf+pALkAA//pALkAIf+wALkAK//FALkALf/6ALkANP+kALkAR//8ALkAUv/lALkAY//RALkAcf/VALkAdP/9ALkAev/wALkAfP+zALkAg//zALkAiQAKALkAigATALkAlv/zALkAmf/qALkArP+JALkAvP/1ALkAwf+mALkAxf/8ALkA2//7ALoAA//sALoAIP/8ALoAIf+2ALoAK//TALoANP/cALoAOf/8ALoAOv/TALoAQf/0ALoAQv/zALoAQ//cALoARP/jALoARv/sALoAR//4ALoAUv/7ALoAY//zALoAcf/pALoAg//nALoAhP/5ALoAhv/vALoAmf/yALoAqv/2ALoArP/SALoAvP/+ALoAwf/JALwAG//8ALwAIP/6ALwAK//3ALwALf/7ALwAOv+5ALwAPP/1ALwAQf/RALwAQv/OALwAQ//3ALwARP/AALwARv/+ALwAUf/8ALwAVf/mALwAdP/8ALwAhv/8ALwAtv/9ALwAuP/9ALwAw//9ALwA0//4ALwA1P/0ALwA1f/6ALwA1v/0AL4AjAATAL8AIf/PAL8AKP/vAL8AK//cAL8ANP/OAL8AOgAFAL8ARv/7AL8AX//wAL8AZAADAL8AcP/7AL8Aev/xAL8AfP/TAL8Ahv/oAL8Akv/xAL8ArP/GAL8Arf/7AL8AvwAHAL8Awf/OAMAAK//yAMAAOv/8AMAAQf/yAMAAQv/yAMAARP/tAMAAwf/vAMAAxf/4AMMAIP/9AMMALf/3AMMAOv/bAMMAPP/0AMMAQf/eAMMAQv/cAMMARP/LAMMAVf/uAMMAY//4AMMAcf/3AMMAdP/9AMMAg//3AMMAhv/5AMMAmf/4AMMAtv/9AMMAuP/9AMMAuf/5AMMAw//9AMMA0//9AMMA1P/9AMMA1v/9AMUAOv/hAMUAQf/oAMUAQv/nAMUAQwALAMUARP/bAMUAVf/iAMUAZP/xAMUAuf/7AMUAv//8AMUAwQAUAMgAOv/iAMgAQf/pAMgAQv/oAMgARP/dAMgAVf/lAMgAwQALAMoAG//7AMoALf/3AMoAOv+6AMoAPP/1AMoAQf/VAMoAQv/TAMoARP+8AMoARv/+AMoAUf/5AMoAVf/kAMoAtv/5AMoAuP/4AMoAw//8AMoA0//7AMoA1P/5AMoA1v/8ANMAA//mANMAG//8ANMAIf/CANMAK//hANMANP/iANMAOv/QANMAQf/zANMAQv/yANMAQ//iANMARP/eANMARv/wANMAR//0ANMAUQANANMAUv/9ANMAVf/1ANMAY//xANMAcf/nANMAg//tANMAhv/xANMAmf/wANMApAAEANMAqv/zANMArP/cANMAvP/zANMAwf/NANQAA//kANQAG//8ANQAIf+3ANQAK//dANQALf/9ANQANP/cANQAOf/8ANQAOv/RANQAQf/0ANQAQv/zANQAQ//gANQARP/gANQARv/wANQAR//yANQAUQAQANQAUv/9ANQAVf/0ANQAY//tANQAcf/iANQAg//oANQAhv/tANQAmf/sANQApAAFANQAqv/yANQArP/WANQAvP/wANQAwf/KANUALf/0ANUANAAJANUAOv/UANUAPP/8ANUAQf/zANUAQv/yANUARP/hANUAR//3ANUAUQARANUAY//tANUAcf/mANUAdP/9ANUAg//oANUAhv/oANUAmf/rANUAqgAKANUAvP/7ANYAA//nANYAG//8ANYAIP/+ANYAIf/EANYAK//hANYANP/lANYAOf/9ANYAOv/NANYAQf/vANYAQv/uANYAQ//fANYARP/aANYARv/vANYAR//0ANYATf/9ANYAUv/8ANYAVf/zANYAY//wANYAcf/nANYAg//tANYAhv/xANYAmf/vANYAqv/zANYArP/dANYAvP/yANYAwf/OANoAG//9ANoAIP/8ANoALf/7ANoAOv/GANoAPP/3ANoAQf/jANoAQv/iANoARP/PANoAVf/zANoAY//3ANoAcf/zANoAg//2ANoAhv/zANoAmf/3ANsAIf/2ANsAK//xANsANP/4ANsAOv/cANsAQf/jANsAQv/hANsAQ//zANsARP/WANsARv/7ANsAVf/eANsAZP/yANsAqv/xANsAuf/7ANsAv//5ANsAwf/sAAAAAAAHAFoAAwABBAkAAQAOAAAAAwABBAkAAgAIAA4AAwABBAkAAwCEABYAAwABBAkABAAYAJoAAwABBAkABQBcALIAAwABBAkABgAYAQ4AAwABBAkADgA0ASYAUgBhAGwAZQB3AGEAeQBCAG8AbABkAE0AYQB0AHQATQBjAEkAbgBlAHIAbgBlAHkALABQAGEAYgBsAG8ASQBtAHAAYQBsAGwAYQByAGkALABSAG8AZAByAGkAZwBvAEYAdQBlAG4AegBhAGwAaQBkAGEAOgAgAFIAYQBsAGUAdwBhAHkAIABCAG8AbABkADoAIAAyADAAMQAyAFIAYQBsAGUAdwBhAHkAIABCAG8AbABkAFYAZQByAHMAaQBvAG4AIAAyAC4AMAAwADEAOwAgAHQAdABmAGEAdQB0AG8AaABpAG4AdAAgACgAdgAwAC4AOAApACAALQBHACAAMgAwADAAIAAtAHIAIAA1ADAAUgBhAGwAZQB3AGEAeQAtAEIAbwBsAGQAaAB0AHQAcAA6AC8ALwBzAGMAcgBpAHAAdABzAC4AcwBpAGwALgBvAHIAZwAvAE8ARgBMAAIAAAAAAAD/tQAyAAAAAAAAAAAAAAAAAAAAAAAAAAAA3AAAAQIAAgADAI0AyQDHANgAYgCOAK0AQwDaAGMA3QCuANkAJQAmAGQA3gAnACgAZQDIAMoAywDpAQMAKQAqACsALAAtAMwAzQDOAM8ALgAvAMMAMAAxACQAZgAyALAA0ADRAGcA0wCRABIArwAzADQANQA2ADcA7QA4ANQA1QBoANYAOQA6ADsAPADrAD0ARABpAGsAbACgAGoACQBuAEEAYQANACMAbQBFAD8AXwBeAGAAPgBAAOgAhwBGAG8AhAAdAA8AiwBHAIMAuAAHANcASABwAHIAcwBxABsAswCyACAA6gAEAKMASQEEAQUBBgEHAQgAGAC8ABcBCQBKAIkAIQCpAKoAvgC/AEsAEABMAHQAdgB3AHUATQBOAE8AHwCkAFAA7wCXAPAAUQAcAHgABgBSAHkAewB8ALEAegAUAPEA9AD1AJ0AngChAH0AUwCIAAsADAAIABEADgCTAFQAIgCiAAUAxQDEALQAtgC1ALcACgBVAIoAVgCGAB4AGgAZAJAAhQBXAO4AFgDzAPYAFQDyAFgAfgCAAIEAfwBCAQoBCwEMAFkAWgBbAFwA7AC6AJYAXQATBE5VTEwERXVybwNmX2YFZl9mX2kFZl9mX2wDZl9pA2ZfbAxmb3Vyc3VwZXJpb3IHdW5pMDBBMAd1bmkwMEFEB3VuaTIyMTUAAAAAAQAB//8ADwABAAAACgAeACwAAWxhdG4ACAAEAAAAAP//AAEAAAABa2VybgAIAAAAAQAAAAEABAACAAAAAQAIAAEA2gAEAAAAaAGuAegCUgKwAyYDdAN6BCwEXgSIBN4E5AV6BfwGFgbYB1YHdAf+CHAIqgkkCY4KZArSCywMAgzgDXYOXA6yDxAPYg+4D9YQVBCqELwQ2hEAEXIReBoQEYoRuBHSEdwSShJoEnoS5BLqE2QTahNwE3YTpBOqE+wUFhSIFJoU7BU+FZgVshXIFgYWTBZSFrwXOhdMF5oXvBfCGDgYghiIGO4ZNBlOGYgaChoQGhAaFhpMGpIa7BtOG6gbrhv0HBIcaBySHKwc7h1UHcIeCB5yHqwAAQBoAAMAEQASABUAFgAcAB0AHgAgACEAJAAmACcAKAArAC0AMwA0ADYANwA4ADkAOgA7ADwAQQBCAEMARABGAEcATQBRAFIAVABVAFYAVwBZAF0AXgBgAGEAYwBkAGYAaABtAHAAcQBzAHQAdQB2AHgAegB7AHwAfgB/AIMAhACFAIYAhwCIAIkAigCMAI0AjgCSAJUAlgCYAJkAnwClAKkArACtAK8AsQCyALMAtAC2ALgAuQC6ALwAvgC/AMAAwwDFAMgAygDTANQA1QDWANoA2wAOACH/4wAr/+EAOv/kAEH/3QBC/90AQ//8AET/2wCy//IAuP/qALn/6QDB/90A0//mANT/5ADW/+UAGgAh//kAK//yADr/6wBB/+wAQv/rAEP/8gBE/+MARv/+AGP//QBx//wAdP/0AIkACgCKAAwAlf/9AJn//QC8//kAv//7AMH/9QDD//UAxf/9AMr//QDT//cA1P/1ANX/8wDW//YA2v/7ABcAK//2AC3/+AA5//4AOv/8AEH/9QBC//UAQ//6AET/7wBRABEAY//7AHH/+wB0//gAiQASAIoAHwCV//0Amf/7ALz/+gDB//gAw//7AMr//QDU//0A1v/8ANr//AAdABv/+gAh/+MAK//nADT/6wA5//wAOv/qAEH/6ABC/+YAQ//kAET/2QBG//MAR//4AFX/8QBx//sAfP/9AIX//QCH//0Alf/7AKr/9ACs//gAtv/9ALn//AC8//sAwf/ZAMr//QDU//0A1f/2ANb/+wDa//sAEwAt//QAOf/3AEf//QBj//IAcf/yAHT/8gCD//oAhv/5AIkAEgCKABsAlf/+AJn/8gC8//4Av//5AMP/9gDK//cA0//2ANT/8gDW//EAAQDF//0ALAAD/+kAIf+gACv/xwAt//IANP/LADn/7wBH/9cAUQAPAFL//QBg//oAY//lAGf/6wBx/9sAdP/zAHX/9gB2//YAd//2AHr/8wB8/94Af//7AIP/9wCE//gAhv/2AIj/+ACJACUAigAtAIsADQCV/+sAmf/lAJ//+gCqAAQArP/LALz/3wC///cAwf+jAMP//ADF//cAyP/1AMr/7gDT//YA1P/1ANX/8wDW//UA2v/rAAwAOv/uAEH/6QBC/+gARP/gAFX/+ABx//0AdP/6ALn//ADD//kA0//0ANT/8gDW//QACgBH//kAY//4AHH/9QB0//gAigAMAJn/9wC8//oAw//4ANb//QDa//wAFQAh//EAK//vADT/9gBH//YAY//3AHH/9AB0//kAhf/9AIf//QCJAAkAigARAI7//QCV//sAmf/3AKz//AC8//QAwf/oAMP/+gDK//sA1f/8ANr/+gABAFYABwAlAAP/8wAhAAQALf/bADP/8gA0ABYAOf/2AEf/+wBRABEAVQAKAFgADABaAA0AYQANAGL/8QBj/+EAcf/kAHT/7QB8ABcAg//0AIQABACG/+kAiQAKAIoANgCLABUAmf/gAKX/8QCqABcAswANALQADQC7//EAvgAHAMP/7gDIAA8Ayv/wANP/2gDU/9cA1v/bANv//QAgAAP/5QAo/4IALf/kADn//gA6/5wAPP/jAEH/pgBC/6EARP+YAFH/mwBV/68AYv/2AGP/9QBx//gAdP/vAIP/6wCG/+IAmf/2AKP/ngCk/50AsP/4ALb/nAC4/50Auf+eALv/9gC///wAwQAKAMP/6gDK//sA0//HANT/uwDW/8MABgB8//cAjv/dAJ//9wC///MAxf/sAMj/+wAwAAP/4QAb//4ALf/mADP/9wA0AA0AOf/4ADr/vgA8/+QAQf/JAEL/yABE/7sAR//4AE3/8wBR/8cAUv/8AFX/xgBaAAMAYQAEAGL/7QBj/+8Abf/zAHH/8QB0/+8AfAANAIP/9ACG//QAjv/7AJn/7wCj/9cApP/TAKoADgCw//QAswAEALQABAC2/8QAuP/FALn/xQC7/+0AvP/9AL//9QDA//EAw//lAMgABgDK//UA0//hANT/3QDW/98A2//xAB8AG//5ACH/4wAr/+YANP/rADn//AA6/+gAQf/nAEL/5QBD/+QARP/YAEb/8QBH//gAUf/9AFX/7wBx//sAfP/8AIX//QCH//sAlf/7AKr/8gCs//cAtv/9ALj//QC5//oAvP/7AMH/1wDK//0A1P/9ANX/9ADW//4A2v/7AAcAQf/3AEL/9gBD//QARP/wAFEADwBVAAcAqgAKACIAIf+2ACv/wwAt/+sANP74ADn/9wBBAA4AQgAPAEMAEABEABEAR//iAGP/2gBt//gAcf/cAHT/9AB6/9wAfP+0AIoAJgCLAAUAlf/pAJb/4QCZ/9oAn//qALz/3QDA//AAwf+hAMX/5wDI/+kAyv/qANP/8ADU//AA1f/2ANb/8QDa//AA2//ZABwAA//lACH/qQAr/80ANP/GADr//gBB//QAQv/0AEP/7ABE//AARv/5AEf/9gBj//QAcf/oAHr/9wB8/94Ag//0AIb/9ACJAAsAigAWAJn/8wCq//UArP+/ALz/9wDB/6kA0wAHANQACQDVAAUA1gAMAA4AIf/2ACv/+QA0AA8AQ//1AFgABgBaAAcAYQAHAHwAEQCqABEAswAHALQABwDB//MAyAAJANb/+wAeABv/+wAr//wALf/4ADQABgA6/+8APP/5AEH/5QBC/+QARP/dAEf/9ABV//IAY//rAHH/5QB0//cAfAAHAIP/9ACF//sAhv/9AIf/+QCO//cAlf/5AJn/6gCqAAcAuP/7ALz//gDD//YAyv/1ANP/+ADU//YA1v/3ABoAK//yADr//ABB//EAQv/xAEP/9wBE/+0AR//9AHH//QB0//MAhf/9AIf//QCJABAAigAXAI7//QCV//sAo//8ALz/+QC///wAwf/5AMP/8gDK//sA0//sANT/6gDV//UA1v/sANr/+gA1AAP/5AAh/6IAK/++AC3/6QA0/8oAOf/5AEf/sABN//wAUQATAFL/1QBT/8EAYP/rAGL/9QBj/6kAZ//NAG3//QBx/68AdP/hAHX/8AB2//AAd//WAHj/9AB6/9wAfP/FAH//9wCD/8wAhP/oAIb/wwCI//MAiQAlAIoALgCLAA0Alf/NAJb/2gCZ/6cAn//hAKoABACs/8EAu//1ALz/qwC///AAwP/5AMH/qwDD//wAxf/pAMj/6wDK/70A0//RANT/0QDV/9QA1v/TANr/xADb/90AGwAb//wAIf/gACv/5QA0/+QAOf/8ADr/3ABB/+EAQv/gAEP/1QBE/8oARv/uAEf//ABR//AAVf/kAFj/9wBa//YAhv/9AKr/7ACs/+sAsP/8ALb/5wC4/+oAuf/iAMH/0ADU//4A1f/4ANb/+gAWACH/5AAr/+UANP/rAEf/8wBj//UAcf/yAHT/+QB8//wAhf/6AIf/+gCJAAsAigAUAI7/+gCV//cAmf/1AKz/8gC8//IAwf/UAMP/+wDK//gA1f/8ANr/9wA1AAP/3QAb//4AIf+uACv/yQAt/+YANP/EADn/7QBH/8sATf/vAFEAGABS/90AU//gAFUADQBaAAMAYP/vAGL/7QBj/8YAZ//XAG3/8QBx/78AdP/lAHr/4AB8/8gAf//qAIP/2QCE/+oAhv/bAIj/7QCJAB4AigA5AIsAGQCV/9cAlv/mAJn/xACf/+4AqgAPAKz/wQC2AAQAuAAFALv/7QC8/8wAwP/vAMH/qwDD//QAxf/uAMj/7gDK/9oA0//yANT/9ADV//MA1v/0ANr/5QDb/+MANwAD/90AG//+ACH/rgAr/8gALf/lADT/wQA5/+wAR//LAEr/4ABN/+8AUQAWAFL/3ABT/+AAVQAPAFgABABaAAUAYP/uAGL/7QBj/8IAZ//WAG3/8QBx/7wAdP/jAHr/3wB8/8cAf//qAIP/2ACE/+kAhv/ZAIj/7QCJAB4AigA8AIsAGwCV/9YAlv/kAJn/wQCf/+0AqgARAKz/vgC2AAYAuAAGALv/7QC8/8kAwP/vAMH/qQDD//QAxf/uAMj/7gDK/9gA0//yANT/8wDV//IA1v/0ANr/5ADb/+MAJQAD//wALf/jADP/8wA0AAoAOf/5AEf/9gBRABcAVQAQAFgABQBaAAYAYv/yAGP/2wBn//kAcf/cAHT/6wB8AAwAf//6AIP/8ACG/+cAiP/5AIkAFACKADwAiwAbAJX/9wCZ/9kApf/qAKoAEgC2AAcAuAAHALv/8gDD//IAyAADAMr/6gDT/+IA1P/gANb/4wDb//QAOQAD/9oAG//+ACH/pwAr/7sALf/ZADT/wQA5/+YAR/+zAEr/4wBN/+oAUQAYAFL/zwBT/94AVQARAFgABwBaAAcAYP/kAGL/5ABj/7EAZ//GAGv/0QBt/+sAcf+uAHT/2QB6/9gAfP+9AH//4QCD/8YAhP/bAIb/xgCI/+gAiQAaAIoAPgCLAB4Alf/GAJb/2ACZ/68AnP/RAJ//4QCqABQArP+3ALYACQC4AAoAu//kALz/rgDA/+gAwf+cAMP/7QDF/+QAyP/kAMr/yADT/98A1P/gANX/4QDW/+MA2v/SANv/1gAVAC3/8gBH//sAYv/7AGP/8QBn//0Acf/zAHT/8ACD//wAhv/5AIkAEwCKABsAlf/4AJn/8QC7//sAvP/9AMP/9ADK//QA0//xANT/8gDW//IA2//9ABcAG//9ACD//QAt//cAOf/+ADr/qgA8//EAQf/JAEL/xwBE/68ARv/+AFH/5ABV/9EAdP/9AKP/9wCk//EAsP/7ALb/4QC4/+UAuf/nAMP/9wDT/+sA1P/mANb/7AAUACEADwArACAAMwAaADr/1gA8//cAQf/XAEL/1QBDAB8ARP/NAEYACAClAAsAuP/dALn/2wC8AAgAwQAwANP/8ADU/+0A1QAcANb/7wDaAAkAFQAh/68AK//HAC3//QA6ABMAQQAEAEIAFgBDABcARAAXAEf/+QBj/94Acf/WAHT//QCJACkAigAxAIsACwCZ/+UAvP/uAMH/pwDTAA0A1AAQANUAEQAHACv/9QA6/9YAQf/eAEL/3QBE/9AAuP/lALn/5gAfABv/+wAg//gAIf/xACv/8AA5//YAOv+pADz/9QBB/8UAQv/CAEP/2wBE/7IARv/uAFH/3gBV/9oAdP//AKP//QCk//QAqv/vAKz//QCw//kAtv/TALj/2AC5/9EAvP/9AMH/6wDD//kA0//wANT/7QDV/+0A1v/wANr/9wAVACEABQArAAwALf/uADMABwA6/8sAPP/tAEH/xgBC/8MAQwAKAET/wwC4/68Auf+uAL//+QDA//kAwQAXAMP/9wDT/+QA1P/dANUACQDW/+EA2//5AAQAJAAHAIkABQCKAA4AjABEAAcAQgAEAEMABQBEAAYAiQAUAIoAHACMABYAwQANAAkAKwADAEEABABCAAUAQwAGAEQABgCJABQAigAcAIwAGgDBAA4AHAAb//0AK//6AC3/+wA5//gAOv+wADz/+ABB/8sAQv/LAEP/9wBE/7sARv/9AFH/8gBV/+MAY//6AHH/+QCD//sAhv/4AJn/+gCw//0Atv/yALj/9AC5//wAvP/7AMH//QDT//kA1P/3ANX//ADW//YAAQCMAA4ABAA6/+sAQf/vAEL/7gBE/+QACwAb//sALf/3ADr/9gA8//UAQf/3AEL/9wBE//YAw//8ANP/+wDU//kA1v/8AAYAev/tAHz/rgCW/+oAn//7AMX/+QDb//IAAgC///wAxf/1ABsAG//8ACD/+QAh//MAK//yADn/9wA6/6QAPP/4AEH/yABC/8YAQ//lAET/owBG/+8AUf/oAFX/2wCk//0Aqv/yALD/+gC2/+gAuP/rALn/7QDB/+wAw//7ANP/8gDU/+4A1f/sANb/8ADa//kABwAr//MAOv/8AEH/8QBC//EARP/rAK3//QDB//EABAB8//wAn//6AL//9wDF//YAGgAb//wAIP/4ACH/7gAr/+4ANP/3ADn/9wA6/+cAPP/3AEH/5gBC/+UAQ//jAET/3wBG/+wAUf/6AFX//QCq//wAtv/7ALj/+wC5//sAwf/mAMP//wDT//YA1P/zANX/8QDW//QA2v/6AAEAigAIAB4AA//vACH/yQAr/9sANP/pADn//QA6AB8AQQAsAEIALQBDADEARAAwAEYABABH//gAUQANAFUAFgBYAAgAWgAJAGP//QBx//IAg//1AIb/8wCJACgAigBGAIsAIACZ//0AqgAdAKz/4wC2AAcAuAAHAMH/0gDa//4AAQCKAAMAAQCKAAYAAQCKAAcACwAo//sAKwAKADr/7ABB//EAQv/xAET/6gBV//IAhv/7AJL//ACt//QAwQAJAAEAfP/kABAAKP/zACsACAA6/90AQf/hAEL/4ABDAAUARP/ZAFX/4ABhAAcAZP/yAIb//ACS//QArf/xALn/9QC///sAwQATAAoALf/7ADn//QA6/8kAPP/3AEH/1wBC/9QAQ//3AET/xgBG//kAjAAhABwAG//7ACD/9wAh//wAK//0AC3/+gA5//kAOv/lADz/8wBB/90AQv/dAEP/5wBE/9QARv/2AFH/9wBV//QAdP/6AKP//QC2//cAuP/2ALn/9gC8//0Awf/zAMP/9wDT//AA1P/uANX/8ADW/+8A2v/6AAQAOv/oAEH/6gBC/+kARP/aABQAG//9ACH/9AAr//QAOv/MAEH/2ABC/9gAQ//wAET/xgBG//sAdP/8ALj/6gC5//MAvP/8AMH/7QDD//wA0//tANT/6ADV/+gA1v/tANr/9gAUAC3/+wA5//sAOv+vADz/9ABB/8wAQv/LAEP/+QBE/7oARv/4AFH/5wBV/98ApP/8ALD/+wC2/98AuP/hALn/2ADD//4A0//4ANT/9gDW//gAFgAh/+UAK//0ADr/wgBB/9sAQv/ZAEP/5wBE/8YARv/5AHT//QB8//gAn//2ALz//QC///IAwf/wAMP//QDF/98AyP/9ANP/8QDU/+0A1f/oANb/8ADa//IABgAt//wAOf/9ADz/+gBG//oAiQAMAIoAFAAFAFEABgBVAAYAqgARALYABQC4AAUADwBRACkAVgAFAFgAFABaABQAfwAFAIUADACHAAwAjgANAKMABgCkABEAqgAJALAAEQC2ABUAuAAVALkACgARAFEAMQBVACcAVgAOAFgAHABaABwAcgAIAH8ADQCFABQAhwAUAI4AFgCjABYApAAeAKoAKwCwAB8AtgAeALgAHgC5ABMAAQCMACQAGgAt//EANAANADr/0QA8//sAQf/wAEL/7wBE/94AR//2AFEADQBYAAMAWgAEAGEABwBj/+gAcf/jAHT//QCD/+gAhv/lAJn/5wCl//MAqgAPALMABwC0AAcAtv/7ALj//AC5/+0AvP/7AB8AA//oACD/+wAo/7wALf/rADQABQA6/9wAPP/mAEH/1wBC/9YARP/TAFH/6QBV/+8AYv/9AGP//ABx//0AdP/2AIP/+QCG//kAmf/8AKP/6wCk/+sAqgAIALb/6gC4/+oAuf/qALv//QDBAAMAw//zANP/5wDU/+EA1v/mAAQAfP/uAJ//9wC///QAxf/xABMALf/7ADn/+wA6/68APP/0AEH/zABC/8sAQ//5AET/vABG//gAUf/xAFX/3wCw//wAtv/xALj/8gC5//YAw//+ANP/+ADU//YA1v/4AAgAOv/YAEH/4QBC/+EARP/UAFX/3QBk/+YAuf/tAL//+gABAHz//AAdABv/+wAg//cAIf/xACv/7wA5//UAOv+m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) format('truetype');}
html{font-family:sans-serif;-ms-text-size-adjust:100%;-webkit-text-size-adjust:100%}body{margin:0}article,aside,details,figcaption,figure,footer,header,hgroup,main,menu,nav,section,summary{display:block}audio,canvas,progress,video{display:inline-block;vertical-align:baseline}audio:not([controls]){display:none;height:0}[hidden],template{display:none}a{background-color:transparent}a:active,a:hover{outline:0}abbr[title]{border-bottom:1px dotted}b,strong{font-weight:bold}dfn{font-style:italic}h1{font-size:2em;margin:0.67em 0}mark{background:#ff0;color:#000}small{font-size:80%}sub,sup{font-size:75%;line-height:0;position:relative;vertical-align:baseline}sup{top:-0.5em}sub{bottom:-0.25em}img{border:0}svg:not(:root){overflow:hidden}figure{margin:1em 40px}hr{-webkit-box-sizing:content-box;-moz-box-sizing:content-box;box-sizing:content-box;height:0}pre{overflow:auto}code,kbd,pre,samp{font-family:monospace, monospace;font-size:1em}button,input,optgroup,select,textarea{color:inherit;font:inherit;margin:0}button{overflow:visible}button,select{text-transform:none}button,html input[type="button"],input[type="reset"],input[type="submit"]{-webkit-appearance:button;cursor:pointer}button[disabled],html input[disabled]{cursor:default}button::-moz-focus-inner,input::-moz-focus-inner{border:0;padding:0}input{line-height:normal}input[type="checkbox"],input[type="radio"]{-webkit-box-sizing:border-box;-moz-box-sizing:border-box;box-sizing:border-box;padding:0}input[type="number"]::-webkit-inner-spin-button,input[type="number"]::-webkit-outer-spin-button{height:auto}input[type="search"]{-webkit-appearance:textfield;-webkit-box-sizing:content-box;-moz-box-sizing:content-box;box-sizing:content-box}input[type="search"]::-webkit-search-cancel-button,input[type="search"]::-webkit-search-decoration{-webkit-appearance:none}fieldset{border:1px solid #c0c0c0;margin:0 2px;padding:0.35em 0.625em 0.75em}legend{border:0;padding:0}textarea{overflow:auto}optgroup{font-weight:bold}table{border-collapse:collapse;border-spacing:0}td,th{padding:0}@media print{*,*:before,*:after{background:transparent !important;color:#000 !important;-webkit-box-shadow:none !important;box-shadow:none !important;text-shadow:none !important}a,a:visited{text-decoration:underline}a[href]:after{content:" (" attr(href) ")"}abbr[title]:after{content:" (" attr(title) ")"}a[href^="#"]:after,a[href^="javascript:"]:after{content:""}pre,blockquote{border:1px solid #999;page-break-inside:avoid}thead{display:table-header-group}tr,img{page-break-inside:avoid}img{max-width:100% !important}p,h2,h3{orphans:3;widows:3}h2,h3{page-break-after:avoid}.navbar{display:none}.btn>.caret,.dropup>.btn>.caret{border-top-color:#000 !important}.label{border:1px solid #000}.table{border-collapse:collapse !important}.table td,.table th{background-color:#fff !important}.table-bordered th,.table-bordered td{border:1px solid #ddd !important}}@font-face{font-family:'Glyphicons Halflings';src:url(data:application/vnd.ms-fontobject;base64,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);src:url(data:application/vnd.ms-fontobject;base64,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) format('embedded-opentype'),url(data:font/woff;base64,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) format('woff'),url(data:font/ttf;base64,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JbwmFCZ+JuYnUCe8J/goNChwKKwpoCnMKiYqSiqEKworeiwILGgsuizsLRwtiC30LiguZi6iLtgvDi9GL34vsi/4MD4whDDSMRIxYDGuMegyJDJeMpoy3jMiMz4zaDO2NBg0YDSoNNI1LDWeNeg2PjZ8Ntw3GjdON5I31DgQOEI4hjjIOQo5SjmIOcw6HDpsOpo63jugO9w8GDxQPKI8+D0yPew+Oj6MPtQ/KD9uP6o/+kBIQIBAxkECQX5CGEKoQu5DGENCQ3ZDoEPKRBBEYESuRPZFWkW2RgZGdEa0RvZHNkd2R7ZH9kgWSDJITkhqSIZIzEkSSThJXkmESapKAkouSlIAAQAAARcApwARAAAAAAACAAAAAQABAAAAQAAuAAAAAAAAABAAxgABAAAAAAATABIAAAADAAEECQAAAGoAEgADAAEECQABACgAfAADAAEECQACAA4ApAADAAEECQADAEwAsgADAAEECQAEADgA/gADAAEECQAFAHgBNgADAAEECQAGADYBrgADAAEECQAIABYB5AADAAEECQAJABYB+gADAAEECQALACQCEAADAAEECQAMACQCNAADAAEECQATACQCWAADAAEECQDIABYCfAADAAEECQDJADACkgADAAEECdkDABoCwnd3dy5nbHlwaGljb25zLmNvbQBDAG8AcAB5AHIAaQBnAGgAdAAgAKkAIAAyADAAMQA0ACAAYgB5ACAASgBhAG4AIABLAG8AdgBhAHIAaQBrAC4AIABBAGwAbAAgAHIAaQBnAGgAdABzACAAcgBlAHMAZQByAHYAZQBkAC4ARwBMAFkAUABIAEkAQwBPAE4AUwAgAEgAYQBsAGYAbABpAG4AZwBzAFIAZQBnAHUAbABhAHIAMQAuADAAMAA5ADsAVQBLAFcATgA7AEcATABZAFAASABJAEMATwBOAFMASABhAGwAZgBsAGkAbgBnAHMALQBSAGUAZwB1AGwAYQByAEcATABZAFAASABJAEMATwBOAFMAIABIAGEAbABmAGwAaQBuAGcAcwAgAFIAZQBnAHUAbABhAHIAVgBlAHIAcwBpAG8AbgAgADEALgAwADAAOQA7AFAAUwAgADAAMAAxAC4AMAAwADkAOwBoAG8AdABjAG8AbgB2ACAAMQAuADAALgA3ADAAOwBtAGEAawBlAG8AdABmAC4AbABpAGIAMgAuADUALgA1ADgAMwAyADkARwBMAFkAUABIAEkAQwBPAE4AUwBIAGEAbABmAGwAaQBuAGcAcwAtAFIAZQBnAHUAbABhAHIASgBhAG4AIABLAG8AdgBhAHIAaQBrAEoAYQBuACAASwBvAHYAYQByAGkAawB3AHcAdwAuAGcAbAB5AHAAaABpAGMAbwBuAHMALgBjAG8AbQB3AHcAdwAuAGcAbAB5AHAAaABpAGMAbwBuAHMALgBjAG8AbQB3AHcAdwAuAGcAbAB5AHAAaABpAGMAbwBuAHMALgBjAG8AbQBXAGUAYgBmAG8AbgB0ACAAMQAuADAAVwBlAGQAIABPAGMAdAAgADIAOQAgADAANgA6ADMANgA6ADAANwAgADIAMAAxADQARgBvAG4AdAAgAFMAcQB1AGkAcgByAGUAbAAAAAIAAAAAAAD/tQAyAAAAAAAAAAAAAAAAAAAAAAAAAAABFwAAAQIBAwADAA0ADgEEAJYBBQEGAQcBCAEJAQoBCwEMAQ0BDgEPARABEQESARMA7wEUARUBFgEXARgBGQEaARsBHAEdAR4BHwEgASEBIgEjASQBJQEmAScBKAEpASoBKwEsAS0BLgEvATABMQEyATMBNAE1ATYBNwE4ATkBOgE7ATwBPQE+AT8BQAFBAUIBQwFEAUUBRgFHAUgBSQFKAUsBTAFNAU4BTwFQAVEBUgFTAVQBVQFWAVcBWAFZAVoBWwFcAV0BXgFfAWABYQFiAWMBZAFlAWYBZwFoAWkBagFrAWwBbQFuAW8BcAFxAXIBcwF0AXUBdgF3AXgBeQF6AXsBfAF9AX4BfwGAAYEBggGDAYQBhQGGAYcBiAGJAYoBiwGMAY0BjgGPAZABkQGSAZMBlAGVAZYBlwGYAZkBmgGbAZwBnQGeAZ8BoAGhAaIBowGkAaUBpgGnAagBqQGqAasBrAGtAa4BrwGwAbEBsgGzAbQBtQG2AbcBuAG5AboBuwG8Ab0BvgG/AcABwQHCAcMBxAHFAcYBxwHIAckBygHLAcwBzQHOAc8B0AHRAdIB0wHUAdUB1gHXAdgB2QHaAdsB3AHdAd4B3wHgAeEB4gHjAeQB5QHmAecB6AHpAeoB6wHsAe0B7gHvAfAB8QHyAfMB9AH1AfYB9wH4AfkB+gH7AfwB/QH+Af8CAAIBAgICAwIEAgUCBgIHAggCCQIKAgsCDAINAg4CDwIQAhECEgZnbHlwaDEGZ2x5cGgyB3VuaTAwQTAHdW5pMjAwMAd1bmkyMDAxB3VuaTIwMDIHdW5pMjAwMwd1bmkyMDA0B3VuaTIwMDUHdW5pMjAwNgd1bmkyMDA3B3VuaTIwMDgHdW5pMjAwOQd1bmkyMDBBB3VuaTIwMkYHdW5pMjA1RgRFdXJvB3VuaTIwQkQHdW5pMjMxQgd1bmkyNUZDB3VuaTI2MDEHdW5pMjZGQQd1bmkyNzA5B3VuaTI3MEYHdW5pRTAwMQd1bmlFMDAyB3VuaUUwMDMHdW5pRTAwNQd1bmlFMDA2B3VuaUUwMDcHdW5pRTAwOAd1bmlFMDA5B3VuaUUwMTAHdW5pRTAxMQd1bmlFMDEyB3VuaUUwMTMHdW5pRTAxNAd1bmlFMDE1B3VuaUUwMTYHdW5pRTAxNwd1bmlFMDE4B3VuaUUwMTkHdW5pRTAyMAd1bmlFMDIxB3VuaUUwMjIHdW5pRTAyMwd1bmlFMDI0B3VuaUUwMjUHdW5pRTAyNgd1bmlFMDI3B3VuaUUwMjgHdW5pRTAyOQd1bmlFMDMwB3VuaUUwMzEHdW5pRTAzMgd1bmlFMDMzB3VuaUUwMzQHdW5pRTAzNQd1bmlFMDM2B3VuaUUwMzcHdW5pRTAzOAd1bmlFMDM5B3VuaUUwNDAHdW5pRTA0MQd1bmlFMDQyB3VuaUUwNDMHdW5pRTA0NAd1bmlFMDQ1B3VuaUUwNDYHdW5pRTA0Nwd1bmlFMDQ4B3VuaUUwNDkHdW5pRTA1MAd1bmlFMDUxB3VuaUUwNTIHdW5pRTA1Mwd1bmlFMDU0B3VuaUUwNTUHdW5pRTA1Ngd1bmlFMDU3B3VuaUUwNTgHdW5pRTA1OQd1bmlFMDYwB3VuaUUwNjIHdW5pRTA2Mwd1bmlFMDY0B3VuaUUwNjUHdW5pRTA2Ngd1bmlFMDY3B3VuaUUwNjgHdW5pRTA2OQd1bmlFMDcwB3VuaUUwNzEHdW5pRTA3Mgd1bmlFMDczB3VuaUUwNzQHdW5pRTA3NQd1bmlFMDc2B3VuaUUwNzcHdW5pRTA3OAd1bmlFMDc5B3VuaUUwODAHdW5pRTA4MQd1bmlFMDgyB3VuaUUwODMHdW5pRTA4NAd1bmlFMDg1B3VuaUUwODYHdW5pRTA4Nwd1bmlFMDg4B3VuaUUwODkHdW5pRTA5MAd1bmlFMDkxB3VuaUUwOTIHdW5pRTA5Mwd1bmlFMDk0B3VuaUUwOTUHdW5pRTA5Ngd1bmlFMDk3B3VuaUUxMDEHdW5pRTEwMgd1bmlFMTAzB3VuaUUxMDQHdW5pRTEwNQd1bmlFMTA2B3VuaUUxMDcHdW5pRTEwOAd1bmlFMTA5B3VuaUUxMTAHdW5pRTExMQd1bmlFMTEyB3VuaUUxMTMHdW5pRTExNAd1bmlFMTE1B3VuaUUxMTYHdW5pRTExNwd1bmlFMTE4B3VuaUUxMTkHdW5pRTEyMAd1bmlFMTIxB3VuaUUxMjIHdW5pRTEyMwd1bmlFMTI0B3VuaUUxMjUHdW5pRTEyNgd1bmlFMTI3B3VuaUUxMjgHdW5pRTEyOQd1bmlFMTMwB3VuaUUxMzEHdW5pRTEzMgd1bmlFMTMzB3VuaUUxMzQHdW5pRTEzNQd1bmlFMTM2B3VuaUUxMzcHdW5pRTEzOAd1bmlFMTM5B3VuaUUxNDAHdW5pRTE0MQd1bmlFMTQyB3VuaUUxNDMHdW5pRTE0NAd1bmlFMTQ1B3VuaUUxNDYHdW5pRTE0OAd1bmlFMTQ5B3VuaUUxNTAHdW5pRTE1MQd1bmlFMTUyB3VuaUUxNTMHdW5pRTE1NAd1bmlFMTU1B3VuaUUxNTYHdW5pRTE1Nwd1bmlFMTU4B3VuaUUxNTkHdW5pRTE2MAd1bmlFMTYxB3VuaUUxNjIHdW5pRTE2Mwd1bmlFMTY0B3VuaUUxNjUHdW5pRTE2Ngd1bmlFMTY3B3VuaUUxNjgHdW5pRTE2OQd1bmlFMTcwB3VuaUUxNzEHdW5pRTE3Mgd1bmlFMTczB3VuaUUxNzQHdW5pRTE3NQd1bmlFMTc2B3VuaUUxNzcHdW5pRTE3OAd1bmlFMTc5B3VuaUUxODAHdW5pRTE4MQd1bmlFMTgyB3VuaUUxODMHdW5pRTE4NAd1bmlFMTg1B3VuaUUxODYHdW5pRTE4Nwd1bmlFMTg4B3VuaUUxODkHdW5pRTE5MAd1bmlFMTkxB3VuaUUxOTIHdW5pRTE5Mwd1bmlFMTk0B3VuaUUxOTUHdW5pRTE5Nwd1bmlFMTk4B3VuaUUxOTkHdW5pRTIwMAd1bmlFMjAxB3VuaUUyMDIHdW5pRTIwMwd1bmlFMjA0B3VuaUUyMDUHdW5pRTIwNgd1bmlFMjA5B3VuaUUyMTAHdW5pRTIxMQd1bmlFMjEyB3VuaUUyMTMHdW5pRTIxNAd1bmlFMjE1B3VuaUUyMTYHdW5pRTIxOAd1bmlFMjE5B3VuaUUyMjEHdW5pRTIyMwd1bmlFMjI0B3VuaUUyMjUHdW5pRTIyNgd1bmlFMjI3B3VuaUUyMzAHdW5pRTIzMQd1bmlFMjMyB3VuaUUyMzMHdW5pRTIzNAd1bmlFMjM1B3VuaUUyMzYHdW5pRTIzNwd1bmlFMjM4B3VuaUUyMzkHdW5pRTI0MAd1bmlFMjQxB3VuaUUyNDIHdW5pRTI0Mwd1bmlFMjQ0B3VuaUUyNDUHdW5pRTI0Ngd1bmlFMjQ3B3VuaUUyNDgHdW5pRTI0OQd1bmlFMjUwB3VuaUUyNTEHdW5pRTI1Mgd1bmlFMjUzB3VuaUUyNTQHdW5pRTI1NQd1bmlFMjU2B3VuaUUyNTcHdW5pRTI1OAd1bmlFMjU5B3VuaUUyNjAHdW5pRjhGRgZ1MUY1MTEGdTFGNkFBAAAAAAFUUMMXAAA=) format('truetype'),url(data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBzdGFuZGFsb25lPSJubyI/Pgo8IURPQ1RZUEUgc3ZnIFBVQkxJQyAiLS8vVzNDLy9EVEQgU1ZHIDEuMS8vRU4iICJodHRwOi8vd3d3LnczLm9yZy9HcmFwaGljcy9TVkcvMS4xL0RURC9zdmcxMS5kdGQiID4KPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8bWV0YWRhdGE+PC9tZXRhZGF0YT4KPGRlZnM+Cjxmb250IGlkPSJnbHlwaGljb25zX2hhbGZsaW5nc3JlZ3VsYXIiIGhvcml6LWFkdi14PSIxMjAwIiA+Cjxmb250LWZhY2UgdW5pdHMtcGVyLWVtPSIxMjAwIiBhc2NlbnQ9Ijk2MCIgZGVzY2VudD0iLTI0MCIgLz4KPG1pc3NpbmctZ2x5cGggaG9yaXotYWR2LXg9IjUwMCIgLz4KPGdseXBoIGhvcml6LWFkdi14PSIwIiAvPgo8Z2x5cGggaG9yaXotYWR2LXg9IjQwMCIgLz4KPGdseXBoIHVuaWNvZGU9IiAiIC8+CjxnbHlwaCB1bmljb2RlPSIqIiBkPSJNNjAwIDExMDBxMTUgMCAzNCAtMS41dDMwIC0zLjVsMTEgLTFxMTAgLTIgMTcuNSAtMTAuNXQ3LjUgLTE4LjV2LTIyNGwxNTggMTU4cTcgNyAxOCA4dDE5IC02bDEwNiAtMTA2cTcgLTggNiAtMTl0LTggLTE4bC0xNTggLTE1OGgyMjRxMTAgMCAxOC41IC03LjV0MTAuNSAtMTcuNXE2IC00MSA2IC03NXEwIC0xNSAtMS41IC0zNHQtMy41IC0zMGwtMSAtMTFxLTIgLTEwIC0xMC41IC0xNy41dC0xOC41IC03LjVoLTIyNGwxNTggLTE1OCBxNyAtNyA4IC0xOHQtNiAtMTlsLTEwNiAtMTA2cS04IC03IC0xOSAtNnQtMTggOGwtMTU4IDE1OHYtMjI0cTAgLTEwIC03LjUgLTE4LjV0LTE3LjUgLTEwLjVxLTQxIC02IC03NSAtNnEtMTUgMCAtMzQgMS41dC0zMCAzLjVsLTExIDFxLTEwIDIgLTE3LjUgMTAuNXQtNy41IDE4LjV2MjI0bC0xNTggLTE1OHEtNyAtNyAtMTggLTh0LTE5IDZsLTEwNiAxMDZxLTcgOCAtNiAxOXQ4IDE4bDE1OCAxNThoLTIyNHEtMTAgMCAtMTguNSA3LjUgdC0xMC41IDE3LjVxLTYgNDEgLTYgNzVxMCAxNSAxLjUgMzR0My41IDMwbDEgMTFxMiAxMCAxMC41IDE3LjV0MTguNSA3LjVoMjI0bC0xNTggMTU4cS03IDcgLTggMTh0NiAxOWwxMDYgMTA2cTggNyAxOSA2dDE4IC04bDE1OCAtMTU4djIyNHEwIDEwIDcuNSAxOC41dDE3LjUgMTAuNXE0MSA2IDc1IDZ6IiAvPgo8Z2x5cGggdW5pY29kZT0iKyIgZD0iTTQ1MCAxMTAwaDIwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMzUwaDM1MHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMjAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0zNTB2LTM1MHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtMjAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYzNTBoLTM1MHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MjAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNSBoMzUwdjM1MHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4YTA7IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4YTU7IiBkPSJNODI1IDExMDBoMjUwcTEwIDAgMTIuNSAtNXQtNS41IC0xM2wtMzY0IC0zNjRxLTYgLTYgLTExIC0xOGgyNjhxMTAgMCAxMyAtNnQtMyAtMTRsLTEyMCAtMTYwcS02IC04IC0xOCAtMTR0LTIyIC02aC0xMjV2LTEwMGgyNzVxMTAgMCAxMyAtNnQtMyAtMTRsLTEyMCAtMTYwcS02IC04IC0xOCAtMTR0LTIyIC02aC0xMjV2LTE3NHEwIC0xMSAtNy41IC0xOC41dC0xOC41IC03LjVoLTE0OHEtMTEgMCAtMTguNSA3LjV0LTcuNSAxOC41djE3NCBoLTI3NXEtMTAgMCAtMTMgNnQzIDE0bDEyMCAxNjBxNiA4IDE4IDE0dDIyIDZoMTI1djEwMGgtMjc1cS0xMCAwIC0xMyA2dDMgMTRsMTIwIDE2MHE2IDggMTggMTR0MjIgNmgxMThxLTUgMTIgLTExIDE4bC0zNjQgMzY0cS04IDggLTUuNSAxM3QxMi41IDVoMjUwcTI1IDAgNDMgLTE4bDE2NCAtMTY0cTggLTggMTggLTh0MTggOGwxNjQgMTY0cTE4IDE4IDQzIDE4eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeDIwMDA7IiBob3Jpei1hZHYteD0iNjUwIiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4MjAwMTsiIGhvcml6LWFkdi14PSIxMzAwIiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4MjAwMjsiIGhvcml6LWFkdi14PSI2NTAiIC8+CjxnbHlwaCB1bmljb2RlPSImI3gyMDAzOyIgaG9yaXotYWR2LXg9IjEzMDAiIC8+CjxnbHlwaCB1bmljb2RlPSImI3gyMDA0OyIgaG9yaXotYWR2LXg9IjQzMyIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeDIwMDU7IiBob3Jpei1hZHYteD0iMzI1IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4MjAwNjsiIGhvcml6LWFkdi14PSIyMTYiIC8+CjxnbHlwaCB1bmljb2RlPSImI3gyMDA3OyIgaG9yaXotYWR2LXg9IjIxNiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeDIwMDg7IiBob3Jpei1hZHYteD0iMTYyIiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4MjAwOTsiIGhvcml6LWFkdi14PSIyNjAiIC8+CjxnbHlwaCB1bmljb2RlPSImI3gyMDBhOyIgaG9yaXotYWR2LXg9IjcyIiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4MjAyZjsiIGhvcml6LWFkdi14PSIyNjAiIC8+CjxnbHlwaCB1bmljb2RlPSImI3gyMDVmOyIgaG9yaXotYWR2LXg9IjMyNSIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeDIwYWM7IiBkPSJNNzQ0IDExOThxMjQyIDAgMzU0IC0xODlxNjAgLTEwNCA2NiAtMjA5aC0xODFxMCA0NSAtMTcuNSA4Mi41dC00My41IDYxLjV0LTU4IDQwLjV0LTYwLjUgMjR0LTUxLjUgNy41cS0xOSAwIC00MC41IC01LjV0LTQ5LjUgLTIwLjV0LTUzIC0zOHQtNDkgLTYyLjV0LTM5IC04OS41aDM3OWwtMTAwIC0xMDBoLTMwMHEtNiAtNTAgLTYgLTEwMGg0MDZsLTEwMCAtMTAwaC0zMDBxOSAtNzQgMzMgLTEzMnQ1Mi41IC05MXQ2MS41IC01NC41dDU5IC0yOSB0NDcgLTcuNXEyMiAwIDUwLjUgNy41dDYwLjUgMjQuNXQ1OCA0MXQ0My41IDYxdDE3LjUgODBoMTc0cS0zMCAtMTcxIC0xMjggLTI3OHEtMTA3IC0xMTcgLTI3NCAtMTE3cS0yMDYgMCAtMzI0IDE1OHEtMzYgNDggLTY5IDEzM3QtNDUgMjA0aC0yMTdsMTAwIDEwMGgxMTJxMSA0NyA2IDEwMGgtMjE4bDEwMCAxMDBoMTM0cTIwIDg3IDUxIDE1My41dDYyIDEwMy41cTExNyAxNDEgMjk3IDE0MXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3gyMGJkOyIgZD0iTTQyOCAxMjAwaDM1MHE2NyAwIDEyMCAtMTN0ODYgLTMxdDU3IC00OS41dDM1IC01Ni41dDE3IC02NC41dDYuNSAtNjAuNXQwLjUgLTU3di0xNi41di0xNi41cTAgLTM2IC0wLjUgLTU3dC02LjUgLTYxdC0xNyAtNjV0LTM1IC01N3QtNTcgLTUwLjV0LTg2IC0zMS41dC0xMjAgLTEzaC0xNzhsLTIgLTEwMGgyODhxMTAgMCAxMyAtNnQtMyAtMTRsLTEyMCAtMTYwcS02IC04IC0xOCAtMTR0LTIyIC02aC0xMzh2LTE3NXEwIC0xMSAtNS41IC0xOCB0LTE1LjUgLTdoLTE0OXEtMTAgMCAtMTcuNSA3LjV0LTcuNSAxNy41djE3NWgtMjY3cS0xMCAwIC0xMyA2dDMgMTRsMTIwIDE2MHE2IDggMTggMTR0MjIgNmgxMTd2MTAwaC0yNjdxLTEwIDAgLTEzIDZ0MyAxNGwxMjAgMTYwcTYgOCAxOCAxNHQyMiA2aDExN3Y0NzVxMCAxMCA3LjUgMTcuNXQxNy41IDcuNXpNNjAwIDEwMDB2LTMwMGgyMDNxNjQgMCA4Ni41IDMzdDIyLjUgMTE5cTAgODQgLTIyLjUgMTE2dC04Ni41IDMyaC0yMDN6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4MjIxMjsiIGQ9Ik0yNTAgNzAwaDgwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMjAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC04MDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djIwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4MjMxYjsiIGQ9Ik0xMDAwIDEyMDB2LTE1MHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtNTB2LTEwMHEwIC05MSAtNDkuNSAtMTY1LjV0LTEzMC41IC0xMDkuNXE4MSAtMzUgMTMwLjUgLTEwOS41dDQ5LjUgLTE2NS41di0xNTBoNTBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTE1MGgtODAwdjE1MHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjVoNTB2MTUwcTAgOTEgNDkuNSAxNjUuNXQxMzAuNSAxMDkuNXEtODEgMzUgLTEzMC41IDEwOS41IHQtNDkuNSAxNjUuNXYxMDBoLTUwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYxNTBoODAwek00MDAgMTAwMHYtMTAwcTAgLTYwIDMyLjUgLTEwOS41dDg3LjUgLTczLjVxMjggLTEyIDQ0IC0zN3QxNiAtNTV0LTE2IC01NXQtNDQgLTM3cS01NSAtMjQgLTg3LjUgLTczLjV0LTMyLjUgLTEwOS41di0xNTBoNDAwdjE1MHEwIDYwIC0zMi41IDEwOS41dC04Ny41IDczLjVxLTI4IDEyIC00NCAzN3QtMTYgNTV0MTYgNTV0NDQgMzcgcTU1IDI0IDg3LjUgNzMuNXQzMi41IDEwOS41djEwMGgtNDAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeDI1ZmM7IiBob3Jpei1hZHYteD0iNTAwIiBkPSJNMCAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeDI2MDE7IiBkPSJNNTAzIDEwODlxMTEwIDAgMjAwLjUgLTU5LjV0MTM0LjUgLTE1Ni41cTQ0IDE0IDkwIDE0cTEyMCAwIDIwNSAtODYuNXQ4NSAtMjA2LjVxMCAtMTIxIC04NSAtMjA3LjV0LTIwNSAtODYuNWgtNzUwcS03OSAwIC0xMzUuNSA1N3QtNTYuNSAxMzdxMCA2OSA0Mi41IDEyMi41dDEwOC41IDY3LjVxLTIgMTIgLTIgMzdxMCAxNTMgMTA4IDI2MC41dDI2MCAxMDcuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3gyNmZhOyIgZD0iTTc3NCAxMTkzLjVxMTYgLTkuNSAyMC41IC0yN3QtNS41IC0zMy41bC0xMzYgLTE4N2w0NjcgLTc0NmgzMHEyMCAwIDM1IC0xOC41dDE1IC0zOS41di00MmgtMTIwMHY0MnEwIDIxIDE1IDM5LjV0MzUgMTguNWgzMGw0NjggNzQ2bC0xMzUgMTgzcS0xMCAxNiAtNS41IDM0dDIwLjUgMjh0MzQgNS41dDI4IC0yMC41bDExMSAtMTQ4bDExMiAxNTBxOSAxNiAyNyAyMC41dDM0IC01ek02MDAgMjAwaDM3N2wtMTgyIDExMmwtMTk1IDUzNHYtNjQ2eiAiIC8+CjxnbHlwaCB1bmljb2RlPSImI3gyNzA5OyIgZD0iTTI1IDExMDBoMTE1MHExMCAwIDEyLjUgLTV0LTUuNSAtMTNsLTU2NCAtNTY3cS04IC04IC0xOCAtOHQtMTggOGwtNTY0IDU2N3EtOCA4IC01LjUgMTN0MTIuNSA1ek0xOCA4ODJsMjY0IC0yNjRxOCAtOCA4IC0xOHQtOCAtMThsLTI2NCAtMjY0cS04IC04IC0xMyAtNS41dC01IDEyLjV2NTUwcTAgMTAgNSAxMi41dDEzIC01LjV6TTkxOCA2MThsMjY0IDI2NHE4IDggMTMgNS41dDUgLTEyLjV2LTU1MHEwIC0xMCAtNSAtMTIuNXQtMTMgNS41IGwtMjY0IDI2NHEtOCA4IC04IDE4dDggMTh6TTgxOCA0ODJsMzY0IC0zNjRxOCAtOCA1LjUgLTEzdC0xMi41IC01aC0xMTUwcS0xMCAwIC0xMi41IDV0NS41IDEzbDM2NCAzNjRxOCA4IDE4IDh0MTggLThsMTY0IC0xNjRxOCAtOCAxOCAtOHQxOCA4bDE2NCAxNjRxOCA4IDE4IDh0MTggLTh6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4MjcwZjsiIGQ9Ik0xMDExIDEyMTBxMTkgMCAzMyAtMTNsMTUzIC0xNTNxMTMgLTE0IDEzIC0zM3QtMTMgLTMzbC05OSAtOTJsLTIxNCAyMTRsOTUgOTZxMTMgMTQgMzIgMTR6TTEwMTMgODAwbC02MTUgLTYxNGwtMjE0IDIxNGw2MTQgNjE0ek0zMTcgOTZsLTMzMyAtMTEybDExMCAzMzV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTAwMTsiIGQ9Ik03MDAgNjUwdi01NTBoMjUwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di01MGgtODAwdjUwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNWgyNTB2NTUwbC01MDAgNTUwaDEyMDB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTAwMjsiIGQ9Ik0zNjggMTAxN2w2NDUgMTYzcTM5IDE1IDYzIDB0MjQgLTQ5di04MzFxMCAtNTUgLTQxLjUgLTk1LjV0LTExMS41IC02My41cS03OSAtMjUgLTE0NyAtNC41dC04NiA3NXQyNS41IDExMS41dDEyMi41IDgycTcyIDI0IDEzOCA4djUyMWwtNjAwIC0xNTV2LTYwNnEwIC00MiAtNDQgLTkwdC0xMDkgLTY5cS03OSAtMjYgLTE0NyAtNS41dC04NiA3NS41dDI1LjUgMTExLjV0MTIyLjUgODIuNXE3MiAyNCAxMzggN3Y2MzlxMCAzOCAxNC41IDU5IHQ1My41IDM0eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwMDM7IiBkPSJNNTAwIDExOTFxMTAwIDAgMTkxIC0zOXQxNTYuNSAtMTA0LjV0MTA0LjUgLTE1Ni41dDM5IC0xOTFsLTEgLTJsMSAtNXEwIC0xNDEgLTc4IC0yNjJsMjc1IC0yNzRxMjMgLTI2IDIyLjUgLTQ0LjV0LTIyLjUgLTQyLjVsLTU5IC01OHEtMjYgLTIwIC00Ni41IC0yMHQtMzkuNSAyMGwtMjc1IDI3NHEtMTE5IC03NyAtMjYxIC03N2wtNSAxbC0yIC0xcS0xMDAgMCAtMTkxIDM5dC0xNTYuNSAxMDQuNXQtMTA0LjUgMTU2LjV0LTM5IDE5MSB0MzkgMTkxdDEwNC41IDE1Ni41dDE1Ni41IDEwNC41dDE5MSAzOXpNNTAwIDEwMjJxLTg4IDAgLTE2MiAtNDN0LTExNyAtMTE3dC00MyAtMTYydDQzIC0xNjJ0MTE3IC0xMTd0MTYyIC00M3QxNjIgNDN0MTE3IDExN3Q0MyAxNjJ0LTQzIDE2MnQtMTE3IDExN3QtMTYyIDQzeiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwMDU7IiBkPSJNNjQ5IDk0OXE0OCA2OCAxMDkuNSAxMDR0MTIxLjUgMzguNXQxMTguNSAtMjB0MTAyLjUgLTY0dDcxIC0xMDAuNXQyNyAtMTIzcTAgLTU3IC0zMy41IC0xMTcuNXQtOTQgLTEyNC41dC0xMjYuNSAtMTI3LjV0LTE1MCAtMTUyLjV0LTE0NiAtMTc0cS02MiA4NSAtMTQ1LjUgMTc0dC0xNTAgMTUyLjV0LTEyNi41IDEyNy41dC05My41IDEyNC41dC0zMy41IDExNy41cTAgNjQgMjggMTIzdDczIDEwMC41dDEwNCA2NHQxMTkgMjAgdDEyMC41IC0zOC41dDEwNC41IC0xMDR6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTAwNjsiIGQ9Ik00MDcgODAwbDEzMSAzNTNxNyAxOSAxNy41IDE5dDE3LjUgLTE5bDEyOSAtMzUzaDQyMXEyMSAwIDI0IC04LjV0LTE0IC0yMC41bC0zNDIgLTI0OWwxMzAgLTQwMXE3IC0yMCAtMC41IC0yNS41dC0yNC41IDYuNWwtMzQzIDI0NmwtMzQyIC0yNDdxLTE3IC0xMiAtMjQuNSAtNi41dC0wLjUgMjUuNWwxMzAgNDAwbC0zNDcgMjUxcS0xNyAxMiAtMTQgMjAuNXQyMyA4LjVoNDI5eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwMDc7IiBkPSJNNDA3IDgwMGwxMzEgMzUzcTcgMTkgMTcuNSAxOXQxNy41IC0xOWwxMjkgLTM1M2g0MjFxMjEgMCAyNCAtOC41dC0xNCAtMjAuNWwtMzQyIC0yNDlsMTMwIC00MDFxNyAtMjAgLTAuNSAtMjUuNXQtMjQuNSA2LjVsLTM0MyAyNDZsLTM0MiAtMjQ3cS0xNyAtMTIgLTI0LjUgLTYuNXQtMC41IDI1LjVsMTMwIDQwMGwtMzQ3IDI1MXEtMTcgMTIgLTE0IDIwLjV0MjMgOC41aDQyOXpNNDc3IDcwMGgtMjQwbDE5NyAtMTQybC03NCAtMjI2IGwxOTMgMTM5bDE5NSAtMTQwbC03NCAyMjlsMTkyIDE0MGgtMjM0bC03OCAyMTF6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTAwODsiIGQ9Ik02MDAgMTIwMHExMjQgMCAyMTIgLTg4dDg4IC0yMTJ2LTI1MHEwIC00NiAtMzEgLTk4dC02OSAtNTJ2LTc1cTAgLTEwIDYgLTIxLjV0MTUgLTE3LjVsMzU4IC0yMzBxOSAtNSAxNSAtMTYuNXQ2IC0yMS41di05M3EwIC0xMCAtNy41IC0xNy41dC0xNy41IC03LjVoLTExNTBxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXY5M3EwIDEwIDYgMjEuNXQxNSAxNi41bDM1OCAyMzBxOSA2IDE1IDE3LjV0NiAyMS41djc1cS0zOCAwIC02OSA1MiB0LTMxIDk4djI1MHEwIDEyNCA4OCAyMTJ0MjEyIDg4eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwMDk7IiBkPSJNMjUgMTEwMGgxMTUwcTEwIDAgMTcuNSAtNy41dDcuNSAtMTcuNXYtMTA1MHEwIC0xMCAtNy41IC0xNy41dC0xNy41IC03LjVoLTExNTBxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXYxMDUwcTAgMTAgNy41IDE3LjV0MTcuNSA3LjV6TTEwMCAxMDAwdi0xMDBoMTAwdjEwMGgtMTAwek04NzUgMTAwMGgtNTUwcS0xMCAwIC0xNy41IC03LjV0LTcuNSAtMTcuNXYtMzUwcTAgLTEwIDcuNSAtMTcuNXQxNy41IC03LjVoNTUwIHExMCAwIDE3LjUgNy41dDcuNSAxNy41djM1MHEwIDEwIC03LjUgMTcuNXQtMTcuNSA3LjV6TTEwMDAgMTAwMHYtMTAwaDEwMHYxMDBoLTEwMHpNMTAwIDgwMHYtMTAwaDEwMHYxMDBoLTEwMHpNMTAwMCA4MDB2LTEwMGgxMDB2MTAwaC0xMDB6TTEwMCA2MDB2LTEwMGgxMDB2MTAwaC0xMDB6TTEwMDAgNjAwdi0xMDBoMTAwdjEwMGgtMTAwek04NzUgNTAwaC01NTBxLTEwIDAgLTE3LjUgLTcuNXQtNy41IC0xNy41di0zNTBxMCAtMTAgNy41IC0xNy41IHQxNy41IC03LjVoNTUwcTEwIDAgMTcuNSA3LjV0Ny41IDE3LjV2MzUwcTAgMTAgLTcuNSAxNy41dC0xNy41IDcuNXpNMTAwIDQwMHYtMTAwaDEwMHYxMDBoLTEwMHpNMTAwMCA0MDB2LTEwMGgxMDB2MTAwaC0xMDB6TTEwMCAyMDB2LTEwMGgxMDB2MTAwaC0xMDB6TTEwMDAgMjAwdi0xMDBoMTAwdjEwMGgtMTAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwMTA7IiBkPSJNNTAgMTEwMGg0MDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTQwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtNDAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXY0MDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek02NTAgMTEwMGg0MDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTQwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtNDAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXY0MDAgcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNNTAgNTAwaDQwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtNDAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC00MDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djQwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTY1MCA1MDBoNDAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di00MDBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTQwMCBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djQwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTAxMTsiIGQ9Ik01MCAxMTAwaDIwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMjAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0yMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djIwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTQ1MCAxMTAwaDIwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMjAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0yMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djIwMCBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek04NTAgMTEwMGgyMDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTIwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtMjAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYyMDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek01MCA3MDBoMjAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0yMDBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTIwMCBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djIwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTQ1MCA3MDBoMjAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0yMDBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTIwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MjAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNODUwIDcwMGgyMDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTIwMCBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTIwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MjAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNNTAgMzAwaDIwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMjAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0yMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djIwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTQ1MCAzMDBoMjAwIHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMjAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0yMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djIwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTg1MCAzMDBoMjAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0yMDBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTIwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MjAwcTAgMjEgMTQuNSAzNS41IHQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTAxMjsiIGQ9Ik01MCAxMTAwaDIwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMjAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0yMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djIwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTQ1MCAxMTAwaDcwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMjAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC03MDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djIwMCBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek01MCA3MDBoMjAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0yMDBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTIwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MjAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNNDUwIDcwMGg3MDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTIwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtNzAwIHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MjAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNNTAgMzAwaDIwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMjAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0yMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djIwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTQ1MCAzMDBoNzAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0yMDAgcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC03MDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djIwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTAxMzsiIGQ9Ik00NjUgNDc3bDU3MSA1NzFxOCA4IDE4IDh0MTcgLThsMTc3IC0xNzdxOCAtNyA4IC0xN3QtOCAtMThsLTc4MyAtNzg0cS03IC04IC0xNy41IC04dC0xNy41IDhsLTM4NCAzODRxLTggOCAtOCAxOHQ4IDE3bDE3NyAxNzdxNyA4IDE3IDh0MTggLThsMTcxIC0xNzFxNyAtNyAxOCAtN3QxOCA3eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwMTQ7IiBkPSJNOTA0IDEwODNsMTc4IC0xNzlxOCAtOCA4IC0xOC41dC04IC0xNy41bC0yNjcgLTI2OGwyNjcgLTI2OHE4IC03IDggLTE3LjV0LTggLTE4LjVsLTE3OCAtMTc4cS04IC04IC0xOC41IC04dC0xNy41IDhsLTI2OCAyNjdsLTI2OCAtMjY3cS03IC04IC0xNy41IC04dC0xOC41IDhsLTE3OCAxNzhxLTggOCAtOCAxOC41dDggMTcuNWwyNjcgMjY4bC0yNjcgMjY4cS04IDcgLTggMTcuNXQ4IDE4LjVsMTc4IDE3OHE4IDggMTguNSA4dDE3LjUgLTggbDI2OCAtMjY3bDI2OCAyNjhxNyA3IDE3LjUgN3QxOC41IC03eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwMTU7IiBkPSJNNTA3IDExNzdxOTggMCAxODcuNSAtMzguNXQxNTQuNSAtMTAzLjV0MTAzLjUgLTE1NC41dDM4LjUgLTE4Ny41cTAgLTE0MSAtNzggLTI2MmwzMDAgLTI5OXE4IC04IDggLTE4LjV0LTggLTE4LjVsLTEwOSAtMTA4cS03IC04IC0xNy41IC04dC0xOC41IDhsLTMwMCAyOTlxLTExOSAtNzcgLTI2MSAtNzdxLTk4IDAgLTE4OCAzOC41dC0xNTQuNSAxMDN0LTEwMyAxNTQuNXQtMzguNSAxODh0MzguNSAxODcuNXQxMDMgMTU0LjUgdDE1NC41IDEwMy41dDE4OCAzOC41ek01MDYuNSAxMDIzcS04OS41IDAgLTE2NS41IC00NHQtMTIwIC0xMjAuNXQtNDQgLTE2NnQ0NCAtMTY1LjV0MTIwIC0xMjB0MTY1LjUgLTQ0dDE2NiA0NHQxMjAuNSAxMjB0NDQgMTY1LjV0LTQ0IDE2NnQtMTIwLjUgMTIwLjV0LTE2NiA0NHpNNDI1IDkwMGgxNTBxMTAgMCAxNy41IC03LjV0Ny41IC0xNy41di03NWg3NXExMCAwIDE3LjUgLTcuNXQ3LjUgLTE3LjV2LTE1MHEwIC0xMCAtNy41IC0xNy41IHQtMTcuNSAtNy41aC03NXYtNzVxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC0xNTBxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXY3NWgtNzVxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXYxNTBxMCAxMCA3LjUgMTcuNXQxNy41IDcuNWg3NXY3NXEwIDEwIDcuNSAxNy41dDE3LjUgNy41eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwMTY7IiBkPSJNNTA3IDExNzdxOTggMCAxODcuNSAtMzguNXQxNTQuNSAtMTAzLjV0MTAzLjUgLTE1NC41dDM4LjUgLTE4Ny41cTAgLTE0MSAtNzggLTI2MmwzMDAgLTI5OXE4IC04IDggLTE4LjV0LTggLTE4LjVsLTEwOSAtMTA4cS03IC04IC0xNy41IC04dC0xOC41IDhsLTMwMCAyOTlxLTExOSAtNzcgLTI2MSAtNzdxLTk4IDAgLTE4OCAzOC41dC0xNTQuNSAxMDN0LTEwMyAxNTQuNXQtMzguNSAxODh0MzguNSAxODcuNXQxMDMgMTU0LjUgdDE1NC41IDEwMy41dDE4OCAzOC41ek01MDYuNSAxMDIzcS04OS41IDAgLTE2NS41IC00NHQtMTIwIC0xMjAuNXQtNDQgLTE2NnQ0NCAtMTY1LjV0MTIwIC0xMjB0MTY1LjUgLTQ0dDE2NiA0NHQxMjAuNSAxMjB0NDQgMTY1LjV0LTQ0IDE2NnQtMTIwLjUgMTIwLjV0LTE2NiA0NHpNMzI1IDgwMGgzNTBxMTAgMCAxNy41IC03LjV0Ny41IC0xNy41di0xNTBxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC0zNTBxLTEwIDAgLTE3LjUgNy41IHQtNy41IDE3LjV2MTUwcTAgMTAgNy41IDE3LjV0MTcuNSA3LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTAxNzsiIGQ9Ik01NTAgMTIwMGgxMDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTQwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtMTAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXY0MDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek04MDAgOTc1djE2NnExNjcgLTYyIDI3MiAtMjA5LjV0MTA1IC0zMzEuNXEwIC0xMTcgLTQ1LjUgLTIyNHQtMTIzIC0xODQuNXQtMTg0LjUgLTEyM3QtMjI0IC00NS41dC0yMjQgNDUuNSB0LTE4NC41IDEyM3QtMTIzIDE4NC41dC00NS41IDIyNHEwIDE4NCAxMDUgMzMxLjV0MjcyIDIwOS41di0xNjZxLTEwMyAtNTUgLTE2NSAtMTU1dC02MiAtMjIwcTAgLTExNiA1NyAtMjE0LjV0MTU1LjUgLTE1NS41dDIxNC41IC01N3QyMTQuNSA1N3QxNTUuNSAxNTUuNXQ1NyAyMTQuNXEwIDEyMCAtNjIgMjIwdC0xNjUgMTU1eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwMTg7IiBkPSJNMTAyNSAxMjAwaDE1MHExMCAwIDE3LjUgLTcuNXQ3LjUgLTE3LjV2LTExNTBxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC0xNTBxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXYxMTUwcTAgMTAgNy41IDE3LjV0MTcuNSA3LjV6TTcyNSA4MDBoMTUwcTEwIDAgMTcuNSAtNy41dDcuNSAtMTcuNXYtNzUwcTAgLTEwIC03LjUgLTE3LjV0LTE3LjUgLTcuNWgtMTUwcS0xMCAwIC0xNy41IDcuNXQtNy41IDE3LjV2NzUwIHEwIDEwIDcuNSAxNy41dDE3LjUgNy41ek00MjUgNTAwaDE1MHExMCAwIDE3LjUgLTcuNXQ3LjUgLTE3LjV2LTQ1MHEwIC0xMCAtNy41IC0xNy41dC0xNy41IC03LjVoLTE1MHEtMTAgMCAtMTcuNSA3LjV0LTcuNSAxNy41djQ1MHEwIDEwIDcuNSAxNy41dDE3LjUgNy41ek0xMjUgMzAwaDE1MHExMCAwIDE3LjUgLTcuNXQ3LjUgLTE3LjV2LTI1MHEwIC0xMCAtNy41IC0xNy41dC0xNy41IC03LjVoLTE1MHEtMTAgMCAtMTcuNSA3LjV0LTcuNSAxNy41IHYyNTBxMCAxMCA3LjUgMTcuNXQxNy41IDcuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDE5OyIgZD0iTTYwMCAxMTc0cTMzIDAgNzQgLTVsMzggLTE1Mmw1IC0xcTQ5IC0xNCA5NCAtMzlsNSAtMmwxMzQgODBxNjEgLTQ4IDEwNCAtMTA1bC04MCAtMTM0bDMgLTVxMjUgLTQ0IDM5IC05M2wxIC02bDE1MiAtMzhxNSAtNDMgNSAtNzNxMCAtMzQgLTUgLTc0bC0xNTIgLTM4bC0xIC02cS0xNSAtNDkgLTM5IC05M2wtMyAtNWw4MCAtMTM0cS00OCAtNjEgLTEwNCAtMTA1bC0xMzQgODFsLTUgLTNxLTQ0IC0yNSAtOTQgLTM5bC01IC0ybC0zOCAtMTUxIHEtNDMgLTUgLTc0IC01cS0zMyAwIC03NCA1bC0zOCAxNTFsLTUgMnEtNDkgMTQgLTk0IDM5bC01IDNsLTEzNCAtODFxLTYwIDQ4IC0xMDQgMTA1bDgwIDEzNGwtMyA1cS0yNSA0NSAtMzggOTNsLTIgNmwtMTUxIDM4cS02IDQyIC02IDc0cTAgMzMgNiA3M2wxNTEgMzhsMiA2cTEzIDQ4IDM4IDkzbDMgNWwtODAgMTM0cTQ3IDYxIDEwNSAxMDVsMTMzIC04MGw1IDJxNDUgMjUgOTQgMzlsNSAxbDM4IDE1MnE0MyA1IDc0IDV6TTYwMCA4MTUgcS04OSAwIC0xNTIgLTYzdC02MyAtMTUxLjV0NjMgLTE1MS41dDE1MiAtNjN0MTUyIDYzdDYzIDE1MS41dC02MyAxNTEuNXQtMTUyIDYzeiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwMjA7IiBkPSJNNTAwIDEzMDBoMzAwcTQxIDAgNzAuNSAtMjkuNXQyOS41IC03MC41di0xMDBoMjc1cTEwIDAgMTcuNSAtNy41dDcuNSAtMTcuNXYtNzVoLTExMDB2NzVxMCAxMCA3LjUgMTcuNXQxNy41IDcuNWgyNzV2MTAwcTAgNDEgMjkuNSA3MC41dDcwLjUgMjkuNXpNNTAwIDEyMDB2LTEwMGgzMDB2MTAwaC0zMDB6TTExMDAgOTAwdi04MDBxMCAtNDEgLTI5LjUgLTcwLjV0LTcwLjUgLTI5LjVoLTcwMHEtNDEgMCAtNzAuNSAyOS41dC0yOS41IDcwLjUgdjgwMGg5MDB6TTMwMCA4MDB2LTcwMGgxMDB2NzAwaC0xMDB6TTUwMCA4MDB2LTcwMGgxMDB2NzAwaC0xMDB6TTcwMCA4MDB2LTcwMGgxMDB2NzAwaC0xMDB6TTkwMCA4MDB2LTcwMGgxMDB2NzAwaC0xMDB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTAyMTsiIGQ9Ik0xOCA2MThsNjIwIDYwOHE4IDcgMTguNSA3dDE3LjUgLTdsNjA4IC02MDhxOCAtOCA1LjUgLTEzdC0xMi41IC01aC0xNzV2LTU3NXEwIC0xMCAtNy41IC0xNy41dC0xNy41IC03LjVoLTI1MHEtMTAgMCAtMTcuNSA3LjV0LTcuNSAxNy41djM3NWgtMzAwdi0zNzVxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC0yNTBxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXY1NzVoLTE3NXEtMTAgMCAtMTIuNSA1dDUuNSAxM3oiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDIyOyIgZD0iTTYwMCAxMjAwdi00MDBxMCAtNDEgMjkuNSAtNzAuNXQ3MC41IC0yOS41aDMwMHYtNjUwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC04MDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djExMDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41aDQ1MHpNMTAwMCA4MDBoLTI1MHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MjUweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwMjM7IiBkPSJNNjAwIDExNzdxMTE3IDAgMjI0IC00NS41dDE4NC41IC0xMjN0MTIzIC0xODQuNXQ0NS41IC0yMjR0LTQ1LjUgLTIyNHQtMTIzIC0xODQuNXQtMTg0LjUgLTEyM3QtMjI0IC00NS41dC0yMjQgNDUuNXQtMTg0LjUgMTIzdC0xMjMgMTg0LjV0LTQ1LjUgMjI0dDQ1LjUgMjI0dDEyMyAxODQuNXQxODQuNSAxMjN0MjI0IDQ1LjV6TTYwMCAxMDI3cS0xMTYgMCAtMjE0LjUgLTU3dC0xNTUuNSAtMTU1LjV0LTU3IC0yMTQuNXQ1NyAtMjE0LjUgdDE1NS41IC0xNTUuNXQyMTQuNSAtNTd0MjE0LjUgNTd0MTU1LjUgMTU1LjV0NTcgMjE0LjV0LTU3IDIxNC41dC0xNTUuNSAxNTUuNXQtMjE0LjUgNTd6TTUyNSA5MDBoNTBxMTAgMCAxNy41IC03LjV0Ny41IC0xNy41di0yNzVoMTc1cTEwIDAgMTcuNSAtNy41dDcuNSAtMTcuNXYtNTBxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC0yNTBxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXYzNTBxMCAxMCA3LjUgMTcuNXQxNy41IDcuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDI0OyIgZD0iTTEzMDAgMGgtNTM4bC00MSA0MDBoLTI0MmwtNDEgLTQwMGgtNTM4bDQzMSAxMjAwaDIwOWwtMjEgLTMwMGgxNjJsLTIwIDMwMGgyMDh6TTUxNSA4MDBsLTI3IC0zMDBoMjI0bC0yNyAzMDBoLTE3MHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDI1OyIgZD0iTTU1MCAxMjAwaDIwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtNDUwaDE5MXEyMCAwIDI1LjUgLTExLjV0LTcuNSAtMjcuNWwtMzI3IC00MDBxLTEzIC0xNiAtMzIgLTE2dC0zMiAxNmwtMzI3IDQwMHEtMTMgMTYgLTcuNSAyNy41dDI1LjUgMTEuNWgxOTF2NDUwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNMTEyNSA0MDBoNTBxMTAgMCAxNy41IC03LjV0Ny41IC0xNy41di0zNTBxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41IGgtMTA1MHEtMTAgMCAtMTcuNSA3LjV0LTcuNSAxNy41djM1MHEwIDEwIDcuNSAxNy41dDE3LjUgNy41aDUwcTEwIDAgMTcuNSAtNy41dDcuNSAtMTcuNXYtMTc1aDkwMHYxNzVxMCAxMCA3LjUgMTcuNXQxNy41IDcuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDI2OyIgZD0iTTYwMCAxMTc3cTExNyAwIDIyNCAtNDUuNXQxODQuNSAtMTIzdDEyMyAtMTg0LjV0NDUuNSAtMjI0dC00NS41IC0yMjR0LTEyMyAtMTg0LjV0LTE4NC41IC0xMjN0LTIyNCAtNDUuNXQtMjI0IDQ1LjV0LTE4NC41IDEyM3QtMTIzIDE4NC41dC00NS41IDIyNHQ0NS41IDIyNHQxMjMgMTg0LjV0MTg0LjUgMTIzdDIyNCA0NS41ek02MDAgMTAyN3EtMTE2IDAgLTIxNC41IC01N3QtMTU1LjUgLTE1NS41dC01NyAtMjE0LjV0NTcgLTIxNC41IHQxNTUuNSAtMTU1LjV0MjE0LjUgLTU3dDIxNC41IDU3dDE1NS41IDE1NS41dDU3IDIxNC41dC01NyAyMTQuNXQtMTU1LjUgMTU1LjV0LTIxNC41IDU3ek01MjUgOTAwaDE1MHExMCAwIDE3LjUgLTcuNXQ3LjUgLTE3LjV2LTI3NWgxMzdxMjEgMCAyNiAtMTEuNXQtOCAtMjcuNWwtMjIzIC0yNzVxLTEzIC0xNiAtMzIgLTE2dC0zMiAxNmwtMjIzIDI3NXEtMTMgMTYgLTggMjcuNXQyNiAxMS41aDEzN3YyNzVxMCAxMCA3LjUgMTcuNXQxNy41IDcuNXogIiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTAyNzsiIGQ9Ik02MDAgMTE3N3ExMTcgMCAyMjQgLTQ1LjV0MTg0LjUgLTEyM3QxMjMgLTE4NC41dDQ1LjUgLTIyNHQtNDUuNSAtMjI0dC0xMjMgLTE4NC41dC0xODQuNSAtMTIzdC0yMjQgLTQ1LjV0LTIyNCA0NS41dC0xODQuNSAxMjN0LTEyMyAxODQuNXQtNDUuNSAyMjR0NDUuNSAyMjR0MTIzIDE4NC41dDE4NC41IDEyM3QyMjQgNDUuNXpNNjAwIDEwMjdxLTExNiAwIC0yMTQuNSAtNTd0LTE1NS41IC0xNTUuNXQtNTcgLTIxNC41dDU3IC0yMTQuNSB0MTU1LjUgLTE1NS41dDIxNC41IC01N3QyMTQuNSA1N3QxNTUuNSAxNTUuNXQ1NyAyMTQuNXQtNTcgMjE0LjV0LTE1NS41IDE1NS41dC0yMTQuNSA1N3pNNjMyIDkxNGwyMjMgLTI3NXExMyAtMTYgOCAtMjcuNXQtMjYgLTExLjVoLTEzN3YtMjc1cTAgLTEwIC03LjUgLTE3LjV0LTE3LjUgLTcuNWgtMTUwcS0xMCAwIC0xNy41IDcuNXQtNy41IDE3LjV2Mjc1aC0xMzdxLTIxIDAgLTI2IDExLjV0OCAyNy41bDIyMyAyNzVxMTMgMTYgMzIgMTYgdDMyIC0xNnoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDI4OyIgZD0iTTIyNSAxMjAwaDc1MHExMCAwIDE5LjUgLTd0MTIuNSAtMTdsMTg2IC02NTJxNyAtMjQgNyAtNDl2LTQyNXEwIC0xMiAtNCAtMjd0LTkgLTE3cS0xMiAtNiAtMzcgLTZoLTExMDBxLTEyIDAgLTI3IDR0LTE3IDhxLTYgMTMgLTYgMzhsMSA0MjVxMCAyNSA3IDQ5bDE4NSA2NTJxMyAxMCAxMi41IDE3dDE5LjUgN3pNODc4IDEwMDBoLTU1NnEtMTAgMCAtMTkgLTd0LTExIC0xOGwtODcgLTQ1MHEtMiAtMTEgNCAtMTh0MTYgLTdoMTUwIHExMCAwIDE5LjUgLTd0MTEuNSAtMTdsMzggLTE1MnEyIC0xMCAxMS41IC0xN3QxOS41IC03aDI1MHExMCAwIDE5LjUgN3QxMS41IDE3bDM4IDE1MnEyIDEwIDExLjUgMTd0MTkuNSA3aDE1MHExMCAwIDE2IDd0NCAxOGwtODcgNDUwcS0yIDExIC0xMSAxOHQtMTkgN3oiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDI5OyIgZD0iTTYwMCAxMTc3cTExNyAwIDIyNCAtNDUuNXQxODQuNSAtMTIzdDEyMyAtMTg0LjV0NDUuNSAtMjI0dC00NS41IC0yMjR0LTEyMyAtMTg0LjV0LTE4NC41IC0xMjN0LTIyNCAtNDUuNXQtMjI0IDQ1LjV0LTE4NC41IDEyM3QtMTIzIDE4NC41dC00NS41IDIyNHQ0NS41IDIyNHQxMjMgMTg0LjV0MTg0LjUgMTIzdDIyNCA0NS41ek02MDAgMTAyN3EtMTE2IDAgLTIxNC41IC01N3QtMTU1LjUgLTE1NS41dC01NyAtMjE0LjV0NTcgLTIxNC41IHQxNTUuNSAtMTU1LjV0MjE0LjUgLTU3dDIxNC41IDU3dDE1NS41IDE1NS41dDU3IDIxNC41dC01NyAyMTQuNXQtMTU1LjUgMTU1LjV0LTIxNC41IDU3ek01NDAgODIwbDI1MyAtMTkwcTE3IC0xMiAxNyAtMzB0LTE3IC0zMGwtMjUzIC0xOTBxLTE2IC0xMiAtMjggLTYuNXQtMTIgMjYuNXY0MDBxMCAyMSAxMiAyNi41dDI4IC02LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTAzMDsiIGQ9Ik05NDcgMTA2MGwxMzUgMTM1cTcgNyAxMi41IDV0NS41IC0xM3YtMzYycTAgLTEwIC03LjUgLTE3LjV0LTE3LjUgLTcuNWgtMzYycS0xMSAwIC0xMyA1LjV0NSAxMi41bDEzMyAxMzNxLTEwOSA3NiAtMjM4IDc2cS0xMTYgMCAtMjE0LjUgLTU3dC0xNTUuNSAtMTU1LjV0LTU3IC0yMTQuNXQ1NyAtMjE0LjV0MTU1LjUgLTE1NS41dDIxNC41IC01N3QyMTQuNSA1N3QxNTUuNSAxNTUuNXQ1NyAyMTQuNWgxNTBxMCAtMTE3IC00NS41IC0yMjQgdC0xMjMgLTE4NC41dC0xODQuNSAtMTIzdC0yMjQgLTQ1LjV0LTIyNCA0NS41dC0xODQuNSAxMjN0LTEyMyAxODQuNXQtNDUuNSAyMjR0NDUuNSAyMjR0MTIzIDE4NC41dDE4NC41IDEyM3QyMjQgNDUuNXExOTIgMCAzNDcgLTExN3oiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDMxOyIgZD0iTTk0NyAxMDYwbDEzNSAxMzVxNyA3IDEyLjUgNXQ1LjUgLTEzdi0zNjFxMCAtMTEgLTcuNSAtMTguNXQtMTguNSAtNy41aC0zNjFxLTExIDAgLTEzIDUuNXQ1IDEyLjVsMTM0IDEzNHEtMTEwIDc1IC0yMzkgNzVxLTExNiAwIC0yMTQuNSAtNTd0LTE1NS41IC0xNTUuNXQtNTcgLTIxNC41aC0xNTBxMCAxMTcgNDUuNSAyMjR0MTIzIDE4NC41dDE4NC41IDEyM3QyMjQgNDUuNXExOTIgMCAzNDcgLTExN3pNMTAyNyA2MDBoMTUwIHEwIC0xMTcgLTQ1LjUgLTIyNHQtMTIzIC0xODQuNXQtMTg0LjUgLTEyM3QtMjI0IC00NS41cS0xOTIgMCAtMzQ4IDExOGwtMTM0IC0xMzRxLTcgLTggLTEyLjUgLTUuNXQtNS41IDEyLjV2MzYwcTAgMTEgNy41IDE4LjV0MTguNSA3LjVoMzYwcTEwIDAgMTIuNSAtNS41dC01LjUgLTEyLjVsLTEzMyAtMTMzcTExMCAtNzYgMjQwIC03NnExMTYgMCAyMTQuNSA1N3QxNTUuNSAxNTUuNXQ1NyAyMTQuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDMyOyIgZD0iTTEyNSAxMjAwaDEwNTBxMTAgMCAxNy41IC03LjV0Ny41IC0xNy41di0xMTUwcTAgLTEwIC03LjUgLTE3LjV0LTE3LjUgLTcuNWgtMTA1MHEtMTAgMCAtMTcuNSA3LjV0LTcuNSAxNy41djExNTBxMCAxMCA3LjUgMTcuNXQxNy41IDcuNXpNMTA3NSAxMDAwaC04NTBxLTEwIDAgLTE3LjUgLTcuNXQtNy41IC0xNy41di04NTBxMCAtMTAgNy41IC0xNy41dDE3LjUgLTcuNWg4NTBxMTAgMCAxNy41IDcuNXQ3LjUgMTcuNXY4NTAgcTAgMTAgLTcuNSAxNy41dC0xNy41IDcuNXpNMzI1IDkwMGg1MHExMCAwIDE3LjUgLTcuNXQ3LjUgLTE3LjV2LTUwcTAgLTEwIC03LjUgLTE3LjV0LTE3LjUgLTcuNWgtNTBxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXY1MHEwIDEwIDcuNSAxNy41dDE3LjUgNy41ek01MjUgOTAwaDQ1MHExMCAwIDE3LjUgLTcuNXQ3LjUgLTE3LjV2LTUwcTAgLTEwIC03LjUgLTE3LjV0LTE3LjUgLTcuNWgtNDUwcS0xMCAwIC0xNy41IDcuNXQtNy41IDE3LjV2NTAgcTAgMTAgNy41IDE3LjV0MTcuNSA3LjV6TTMyNSA3MDBoNTBxMTAgMCAxNy41IC03LjV0Ny41IC0xNy41di01MHEwIC0xMCAtNy41IC0xNy41dC0xNy41IC03LjVoLTUwcS0xMCAwIC0xNy41IDcuNXQtNy41IDE3LjV2NTBxMCAxMCA3LjUgMTcuNXQxNy41IDcuNXpNNTI1IDcwMGg0NTBxMTAgMCAxNy41IC03LjV0Ny41IC0xNy41di01MHEwIC0xMCAtNy41IC0xNy41dC0xNy41IC03LjVoLTQ1MHEtMTAgMCAtMTcuNSA3LjV0LTcuNSAxNy41djUwIHEwIDEwIDcuNSAxNy41dDE3LjUgNy41ek0zMjUgNTAwaDUwcTEwIDAgMTcuNSAtNy41dDcuNSAtMTcuNXYtNTBxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC01MHEtMTAgMCAtMTcuNSA3LjV0LTcuNSAxNy41djUwcTAgMTAgNy41IDE3LjV0MTcuNSA3LjV6TTUyNSA1MDBoNDUwcTEwIDAgMTcuNSAtNy41dDcuNSAtMTcuNXYtNTBxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC00NTBxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXY1MCBxMCAxMCA3LjUgMTcuNXQxNy41IDcuNXpNMzI1IDMwMGg1MHExMCAwIDE3LjUgLTcuNXQ3LjUgLTE3LjV2LTUwcTAgLTEwIC03LjUgLTE3LjV0LTE3LjUgLTcuNWgtNTBxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXY1MHEwIDEwIDcuNSAxNy41dDE3LjUgNy41ek01MjUgMzAwaDQ1MHExMCAwIDE3LjUgLTcuNXQ3LjUgLTE3LjV2LTUwcTAgLTEwIC03LjUgLTE3LjV0LTE3LjUgLTcuNWgtNDUwcS0xMCAwIC0xNy41IDcuNXQtNy41IDE3LjV2NTAgcTAgMTAgNy41IDE3LjV0MTcuNSA3LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTAzMzsiIGQ9Ik05MDAgODAwdjIwMHEwIDgzIC01OC41IDE0MS41dC0xNDEuNSA1OC41aC0zMDBxLTgyIDAgLTE0MSAtNTl0LTU5IC0xNDF2LTIwMGgtMTAwcS00MSAwIC03MC41IC0yOS41dC0yOS41IC03MC41di02MDBxMCAtNDEgMjkuNSAtNzAuNXQ3MC41IC0yOS41aDkwMHE0MSAwIDcwLjUgMjkuNXQyOS41IDcwLjV2NjAwcTAgNDEgLTI5LjUgNzAuNXQtNzAuNSAyOS41aC0xMDB6TTQwMCA4MDB2MTUwcTAgMjEgMTUgMzUuNXQzNSAxNC41aDIwMCBxMjAgMCAzNSAtMTQuNXQxNSAtMzUuNXYtMTUwaC0zMDB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTAzNDsiIGQ9Ik0xMjUgMTEwMGg1MHExMCAwIDE3LjUgLTcuNXQ3LjUgLTE3LjV2LTEwNzVoLTEwMHYxMDc1cTAgMTAgNy41IDE3LjV0MTcuNSA3LjV6TTEwNzUgMTA1MnE0IDAgOSAtMnExNiAtNiAxNiAtMjN2LTQyMXEwIC02IC0zIC0xMnEtMzMgLTU5IC02Ni41IC05OXQtNjUuNSAtNTh0LTU2LjUgLTI0LjV0LTUyLjUgLTYuNXEtMjYgMCAtNTcuNSA2LjV0LTUyLjUgMTMuNXQtNjAgMjFxLTQxIDE1IC02MyAyMi41dC01Ny41IDE1dC02NS41IDcuNSBxLTg1IDAgLTE2MCAtNTdxLTcgLTUgLTE1IC01cS02IDAgLTExIDNxLTE0IDcgLTE0IDIydjQzOHEyMiA1NSA4MiA5OC41dDExOSA0Ni41cTIzIDIgNDMgMC41dDQzIC03dDMyLjUgLTguNXQzOCAtMTN0MzIuNSAtMTFxNDEgLTE0IDYzLjUgLTIxdDU3IC0xNHQ2My41IC03cTEwMyAwIDE4MyA4N3E3IDggMTggOHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDM1OyIgZD0iTTYwMCAxMTc1cTExNiAwIDIyNyAtNDkuNXQxOTIuNSAtMTMxdDEzMSAtMTkyLjV0NDkuNSAtMjI3di0zMDBxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC01MHEtMTAgMCAtMTcuNSA3LjV0LTcuNSAxNy41djMwMHEwIDEyNyAtNzAuNSAyMzEuNXQtMTg0LjUgMTYxLjV0LTI0NSA1N3QtMjQ1IC01N3QtMTg0LjUgLTE2MS41dC03MC41IC0yMzEuNXYtMzAwcTAgLTEwIC03LjUgLTE3LjV0LTE3LjUgLTcuNWgtNTAgcS0xMCAwIC0xNy41IDcuNXQtNy41IDE3LjV2MzAwcTAgMTE2IDQ5LjUgMjI3dDEzMSAxOTIuNXQxOTIuNSAxMzF0MjI3IDQ5LjV6TTIyMCA1MDBoMTYwcTggMCAxNCAtNnQ2IC0xNHYtNDYwcTAgLTggLTYgLTE0dC0xNCAtNmgtMTYwcS04IDAgLTE0IDZ0LTYgMTR2NDYwcTAgOCA2IDE0dDE0IDZ6TTgyMCA1MDBoMTYwcTggMCAxNCAtNnQ2IC0xNHYtNDYwcTAgLTggLTYgLTE0dC0xNCAtNmgtMTYwcS04IDAgLTE0IDZ0LTYgMTR2NDYwIHEwIDggNiAxNHQxNCA2eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwMzY7IiBkPSJNMzIxIDgxNGwyNTggMTcycTkgNiAxNSAyLjV0NiAtMTMuNXYtNzUwcTAgLTEwIC02IC0xMy41dC0xNSAyLjVsLTI1OCAxNzJxLTIxIDE0IC00NiAxNGgtMjUwcS0xMCAwIC0xNy41IDcuNXQtNy41IDE3LjV2MzUwcTAgMTAgNy41IDE3LjV0MTcuNSA3LjVoMjUwcTI1IDAgNDYgMTR6TTkwMCA2NjhsMTIwIDEyMHE3IDcgMTcgN3QxNyAtN2wzNCAtMzRxNyAtNyA3IC0xN3QtNyAtMTdsLTEyMCAtMTIwbDEyMCAtMTIwcTcgLTcgNyAtMTcgdC03IC0xN2wtMzQgLTM0cS03IC03IC0xNyAtN3QtMTcgN2wtMTIwIDExOWwtMTIwIC0xMTlxLTcgLTcgLTE3IC03dC0xNyA3bC0zNCAzNHEtNyA3IC03IDE3dDcgMTdsMTE5IDEyMGwtMTE5IDEyMHEtNyA3IC03IDE3dDcgMTdsMzQgMzRxNyA4IDE3IDh0MTcgLTh6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTAzNzsiIGQ9Ik0zMjEgODE0bDI1OCAxNzJxOSA2IDE1IDIuNXQ2IC0xMy41di03NTBxMCAtMTAgLTYgLTEzLjV0LTE1IDIuNWwtMjU4IDE3MnEtMjEgMTQgLTQ2IDE0aC0yNTBxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXYzNTBxMCAxMCA3LjUgMTcuNXQxNy41IDcuNWgyNTBxMjUgMCA0NiAxNHpNNzY2IDkwMGg0cTEwIC0xIDE2IC0xMHE5NiAtMTI5IDk2IC0yOTBxMCAtMTU0IC05MCAtMjgxcS02IC05IC0xNyAtMTBsLTMgLTFxLTkgMCAtMTYgNiBsLTI5IDIzcS03IDcgLTguNSAxNi41dDQuNSAxNy41cTcyIDEwMyA3MiAyMjlxMCAxMzIgLTc4IDIzOHEtNiA4IC00LjUgMTh0OS41IDE3bDI5IDIycTcgNSAxNSA1eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwMzg7IiBkPSJNOTY3IDEwMDRoM3ExMSAtMSAxNyAtMTBxMTM1IC0xNzkgMTM1IC0zOTZxMCAtMTA1IC0zNCAtMjA2LjV0LTk4IC0xODUuNXEtNyAtOSAtMTcgLTEwaC0zcS05IDAgLTE2IDZsLTQyIDM0cS04IDYgLTkgMTZ0NSAxOHExMTEgMTUwIDExMSAzMjhxMCA5MCAtMjkuNSAxNzZ0LTg0LjUgMTU3cS02IDkgLTUgMTl0MTAgMTZsNDIgMzNxNyA1IDE1IDV6TTMyMSA4MTRsMjU4IDE3MnE5IDYgMTUgMi41dDYgLTEzLjV2LTc1MHEwIC0xMCAtNiAtMTMuNSB0LTE1IDIuNWwtMjU4IDE3MnEtMjEgMTQgLTQ2IDE0aC0yNTBxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXYzNTBxMCAxMCA3LjUgMTcuNXQxNy41IDcuNWgyNTBxMjUgMCA0NiAxNHpNNzY2IDkwMGg0cTEwIC0xIDE2IC0xMHE5NiAtMTI5IDk2IC0yOTBxMCAtMTU0IC05MCAtMjgxcS02IC05IC0xNyAtMTBsLTMgLTFxLTkgMCAtMTYgNmwtMjkgMjNxLTcgNyAtOC41IDE2LjV0NC41IDE3LjVxNzIgMTAzIDcyIDIyOXEwIDEzMiAtNzggMjM4IHEtNiA4IC00LjUgMTguNXQ5LjUgMTYuNWwyOSAyMnE3IDUgMTUgNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDM5OyIgZD0iTTUwMCA5MDBoMTAwdi0xMDBoLTEwMHYtMTAwaC00MDB2LTEwMGgtMTAwdjYwMGg1MDB2LTMwMHpNMTIwMCA3MDBoLTIwMHYtMTAwaDIwMHYtMjAwaC0zMDB2MzAwaC0yMDB2MzAwaC0xMDB2MjAwaDYwMHYtNTAwek0xMDAgMTEwMHYtMzAwaDMwMHYzMDBoLTMwMHpNODAwIDExMDB2LTMwMGgzMDB2MzAwaC0zMDB6TTMwMCA5MDBoLTEwMHYxMDBoMTAwdi0xMDB6TTEwMDAgOTAwaC0xMDB2MTAwaDEwMHYtMTAwek0zMDAgNTAwaDIwMHYtNTAwIGgtNTAwdjUwMGgyMDB2MTAwaDEwMHYtMTAwek04MDAgMzAwaDIwMHYtMTAwaC0xMDB2LTEwMGgtMjAwdjEwMGgtMTAwdjEwMGgxMDB2MjAwaC0yMDB2MTAwaDMwMHYtMzAwek0xMDAgNDAwdi0zMDBoMzAwdjMwMGgtMzAwek0zMDAgMjAwaC0xMDB2MTAwaDEwMHYtMTAwek0xMjAwIDIwMGgtMTAwdjEwMGgxMDB2LTEwMHpNNzAwIDBoLTEwMHYxMDBoMTAwdi0xMDB6TTEyMDAgMGgtMzAwdjEwMGgzMDB2LTEwMHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDQwOyIgZD0iTTEwMCAyMDBoLTEwMHYxMDAwaDEwMHYtMTAwMHpNMzAwIDIwMGgtMTAwdjEwMDBoMTAwdi0xMDAwek03MDAgMjAwaC0yMDB2MTAwMGgyMDB2LTEwMDB6TTkwMCAyMDBoLTEwMHYxMDAwaDEwMHYtMTAwMHpNMTIwMCAyMDBoLTIwMHYxMDAwaDIwMHYtMTAwMHpNNDAwIDBoLTMwMHYxMDBoMzAwdi0xMDB6TTYwMCAwaC0xMDB2OTFoMTAwdi05MXpNODAwIDBoLTEwMHY5MWgxMDB2LTkxek0xMTAwIDBoLTIwMHY5MWgyMDB2LTkxeiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwNDE7IiBkPSJNNTAwIDEyMDBsNjgyIC02ODJxOCAtOCA4IC0xOHQtOCAtMThsLTQ2NCAtNDY0cS04IC04IC0xOCAtOHQtMTggOGwtNjgyIDY4MmwxIDQ3NXEwIDEwIDcuNSAxNy41dDE3LjUgNy41aDQ3NHpNMzE5LjUgMTAyNC41cS0yOS41IDI5LjUgLTcxIDI5LjV0LTcxIC0yOS41dC0yOS41IC03MS41dDI5LjUgLTcxLjV0NzEgLTI5LjV0NzEgMjkuNXQyOS41IDcxLjV0LTI5LjUgNzEuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDQyOyIgZD0iTTUwMCAxMjAwbDY4MiAtNjgycTggLTggOCAtMTh0LTggLTE4bC00NjQgLTQ2NHEtOCAtOCAtMTggLTh0LTE4IDhsLTY4MiA2ODJsMSA0NzVxMCAxMCA3LjUgMTcuNXQxNy41IDcuNWg0NzR6TTgwMCAxMjAwbDY4MiAtNjgycTggLTggOCAtMTh0LTggLTE4bC00NjQgLTQ2NHEtOCAtOCAtMTggLTh0LTE4IDhsLTU2IDU2bDQyNCA0MjZsLTcwMCA3MDBoMTUwek0zMTkuNSAxMDI0LjVxLTI5LjUgMjkuNSAtNzEgMjkuNXQtNzEgLTI5LjUgdC0yOS41IC03MS41dDI5LjUgLTcxLjV0NzEgLTI5LjV0NzEgMjkuNXQyOS41IDcxLjV0LTI5LjUgNzEuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDQzOyIgZD0iTTMwMCAxMjAwaDgyNXE3NSAwIDc1IC03NXYtOTAwcTAgLTI1IC0xOCAtNDNsLTY0IC02NHEtOCAtOCAtMTMgLTUuNXQtNSAxMi41djk1MHEwIDEwIC03LjUgMTcuNXQtMTcuNSA3LjVoLTcwMHEtMjUgMCAtNDMgLTE4bC02NCAtNjRxLTggLTggLTUuNSAtMTN0MTIuNSAtNWg3MDBxMTAgMCAxNy41IC03LjV0Ny41IC0xNy41di05NTBxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC04NTBxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXY5NzUgcTAgMjUgMTggNDNsMTM5IDEzOXExOCAxOCA0MyAxOHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDQ0OyIgZD0iTTI1MCAxMjAwaDgwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMTE1MGwtNDUwIDQ0NGwtNDUwIC00NDV2MTE1MXEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA0NTsiIGQ9Ik04MjIgMTIwMGgtNDQ0cS0xMSAwIC0xOSAtNy41dC05IC0xNy41bC03OCAtMzAxcS03IC0yNCA3IC00NWw1NyAtMTA4cTYgLTkgMTcuNSAtMTV0MjEuNSAtNmg0NTBxMTAgMCAyMS41IDZ0MTcuNSAxNWw2MiAxMDhxMTQgMjEgNyA0NWwtODMgMzAxcS0xIDEwIC05IDE3LjV0LTE5IDcuNXpNMTE3NSA4MDBoLTE1MHEtMTAgMCAtMjEgLTYuNXQtMTUgLTE1LjVsLTc4IC0xNTZxLTQgLTkgLTE1IC0xNS41dC0yMSAtNi41aC01NTAgcS0xMCAwIC0yMSA2LjV0LTE1IDE1LjVsLTc4IDE1NnEtNCA5IC0xNSAxNS41dC0yMSA2LjVoLTE1MHEtMTAgMCAtMTcuNSAtNy41dC03LjUgLTE3LjV2LTY1MHEwIC0xMCA3LjUgLTE3LjV0MTcuNSAtNy41aDE1MHExMCAwIDE3LjUgNy41dDcuNSAxNy41djE1MHEwIDEwIDcuNSAxNy41dDE3LjUgNy41aDc1MHExMCAwIDE3LjUgLTcuNXQ3LjUgLTE3LjV2LTE1MHEwIC0xMCA3LjUgLTE3LjV0MTcuNSAtNy41aDE1MHExMCAwIDE3LjUgNy41IHQ3LjUgMTcuNXY2NTBxMCAxMCAtNy41IDE3LjV0LTE3LjUgNy41ek04NTAgMjAwaC01MDBxLTEwIDAgLTE5LjUgLTd0LTExLjUgLTE3bC0zOCAtMTUycS0yIC0xMCAzLjUgLTE3dDE1LjUgLTdoNjAwcTEwIDAgMTUuNSA3dDMuNSAxN2wtMzggMTUycS0yIDEwIC0xMS41IDE3dC0xOS41IDd6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA0NjsiIGQ9Ik01MDAgMTEwMGgyMDBxNTYgMCAxMDIuNSAtMjAuNXQ3Mi41IC01MHQ0NCAtNTl0MjUgLTUwLjVsNiAtMjBoMTUwcTQxIDAgNzAuNSAtMjkuNXQyOS41IC03MC41di02MDBxMCAtNDEgLTI5LjUgLTcwLjV0LTcwLjUgLTI5LjVoLTEwMDBxLTQxIDAgLTcwLjUgMjkuNXQtMjkuNSA3MC41djYwMHEwIDQxIDI5LjUgNzAuNXQ3MC41IDI5LjVoMTUwcTIgOCA2LjUgMjEuNXQyNCA0OHQ0NSA2MXQ3MiA0OHQxMDIuNSAyMS41ek05MDAgODAwdi0xMDAgaDEwMHYxMDBoLTEwMHpNNjAwIDczMHEtOTUgMCAtMTYyLjUgLTY3LjV0LTY3LjUgLTE2Mi41dDY3LjUgLTE2Mi41dDE2Mi41IC02Ny41dDE2Mi41IDY3LjV0NjcuNSAxNjIuNXQtNjcuNSAxNjIuNXQtMTYyLjUgNjcuNXpNNjAwIDYwM3E0MyAwIDczIC0zMHQzMCAtNzN0LTMwIC03M3QtNzMgLTMwdC03MyAzMHQtMzAgNzN0MzAgNzN0NzMgMzB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA0NzsiIGQ9Ik02ODEgMTE5OWwzODUgLTk5OHEyMCAtNTAgNjAgLTkycTE4IC0xOSAzNi41IC0yOS41dDI3LjUgLTExLjVsMTAgLTJ2LTY2aC00MTd2NjZxNTMgMCA3NSA0My41dDUgODguNWwtODIgMjIyaC0zOTFxLTU4IC0xNDUgLTkyIC0yMzRxLTExIC0zNCAtNi41IC01N3QyNS41IC0zN3Q0NiAtMjB0NTUgLTZ2LTY2aC0zNjV2NjZxNTYgMjQgODQgNTJxMTIgMTIgMjUgMzAuNXQyMCAzMS41bDcgMTNsMzk5IDEwMDZoOTN6TTQxNiA1MjFoMzQwIGwtMTYyIDQ1N3oiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDQ4OyIgZD0iTTc1MyA2NDFxNSAtMSAxNC41IC00LjV0MzYgLTE1LjV0NTAuNSAtMjYuNXQ1My41IC00MHQ1MC41IC01NC41dDM1LjUgLTcwdDE0LjUgLTg3cTAgLTY3IC0yNy41IC0xMjUuNXQtNzEuNSAtOTcuNXQtOTguNSAtNjYuNXQtMTA4LjUgLTQwLjV0LTEwMiAtMTNoLTUwMHY4OXE0MSA3IDcwLjUgMzIuNXQyOS41IDY1LjV2ODI3cTAgMjQgLTAuNSAzNHQtMy41IDI0dC04LjUgMTkuNXQtMTcgMTMuNXQtMjggMTIuNXQtNDIuNSAxMS41djcxIGw0NzEgLTFxNTcgMCAxMTUuNSAtMjAuNXQxMDggLTU3dDgwLjUgLTk0dDMxIC0xMjQuNXEwIC01MSAtMTUuNSAtOTYuNXQtMzggLTc0LjV0LTQ1IC01MC41dC0zOC41IC0zMC41ek00MDAgNzAwaDEzOXE3OCAwIDEzMC41IDQ4LjV0NTIuNSAxMjIuNXEwIDQxIC04LjUgNzAuNXQtMjkuNSA1NS41dC02Mi41IDM5LjV0LTEwMy41IDEzLjVoLTExOHYtMzUwek00MDAgMjAwaDIxNnE4MCAwIDEyMSA1MC41dDQxIDEzMC41cTAgOTAgLTYyLjUgMTU0LjUgdC0xNTYuNSA2NC41aC0xNTl2LTQwMHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDQ5OyIgZD0iTTg3NyAxMjAwbDIgLTU3cS04MyAtMTkgLTExNiAtNDUuNXQtNDAgLTY2LjVsLTEzMiAtODM5cS05IC00OSAxMyAtNjl0OTYgLTI2di05N2gtNTAwdjk3cTE4NiAxNiAyMDAgOThsMTczIDgzMnEzIDE3IDMgMzB0LTEuNSAyMi41dC05IDE3LjV0LTEzLjUgMTIuNXQtMjEuNSAxMHQtMjYgOC41dC0zMy41IDEwcS0xMyAzIC0xOSA1djU3aDQyNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDUwOyIgZD0iTTEzMDAgOTAwaC01MHEwIDIxIC00IDM3dC05LjUgMjYuNXQtMTggMTcuNXQtMjIgMTF0LTI4LjUgNS41dC0zMSAydC0zNyAwLjVoLTIwMHYtODUwcTAgLTIyIDI1IC0zNC41dDUwIC0xMy41bDI1IC0ydi0xMDBoLTQwMHYxMDBxNCAwIDExIDAuNXQyNCAzdDMwIDd0MjQgMTV0MTEgMjQuNXY4NTBoLTIwMHEtMjUgMCAtMzcgLTAuNXQtMzEgLTJ0LTI4LjUgLTUuNXQtMjIgLTExdC0xOCAtMTcuNXQtOS41IC0yNi41dC00IC0zN2gtNTB2MzAwIGgxMDAwdi0zMDB6TTE3NSAxMDAwaC03NXYtODAwaDc1bC0xMjUgLTE2N2wtMTI1IDE2N2g3NXY4MDBoLTc1bDEyNSAxNjd6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA1MTsiIGQ9Ik0xMTAwIDkwMGgtNTBxMCAyMSAtNCAzN3QtOS41IDI2LjV0LTE4IDE3LjV0LTIyIDExdC0yOC41IDUuNXQtMzEgMnQtMzcgMC41aC0yMDB2LTY1MHEwIC0yMiAyNSAtMzQuNXQ1MCAtMTMuNWwyNSAtMnYtMTAwaC00MDB2MTAwcTQgMCAxMSAwLjV0MjQgM3QzMCA3dDI0IDE1dDExIDI0LjV2NjUwaC0yMDBxLTI1IDAgLTM3IC0wLjV0LTMxIC0ydC0yOC41IC01LjV0LTIyIC0xMXQtMTggLTE3LjV0LTkuNSAtMjYuNXQtNCAtMzdoLTUwdjMwMCBoMTAwMHYtMzAwek0xMTY3IDUwbC0xNjcgLTEyNXY3NWgtODAwdi03NWwtMTY3IDEyNWwxNjcgMTI1di03NWg4MDB2NzV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA1MjsiIGQ9Ik01MCAxMTAwaDYwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMTAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC02MDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djEwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTUwIDgwMGgxMDAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0xMDBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTEwMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djEwMCBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek01MCA1MDBoODAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0xMDBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTgwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MTAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNNTAgMjAwaDExMDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTEwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtMTEwMCBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djEwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA1MzsiIGQ9Ik0yNTAgMTEwMGg3MDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTEwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtNzAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYxMDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek01MCA4MDBoMTEwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMTAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0xMTAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYxMDAgcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNMjUwIDUwMGg3MDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTEwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtNzAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYxMDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek01MCAyMDBoMTEwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMTAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0xMTAwIHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MTAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDU0OyIgZD0iTTUwMCA5NTB2MTAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNWg2MDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTEwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtNjAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXpNMTAwIDY1MHYxMDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41aDEwMDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTEwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtMTAwMCBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41ek0zMDAgMzUwdjEwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjVoODAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0xMDBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTgwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV6TTAgNTB2MTAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNWgxMTAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0xMDAgcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0xMTAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDU1OyIgZD0iTTUwIDExMDBoMTEwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMTAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0xMTAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYxMDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek01MCA4MDBoMTEwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMTAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0xMTAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYxMDAgcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNNTAgNTAwaDExMDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTEwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtMTEwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MTAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNNTAgMjAwaDExMDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTEwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtMTEwMCBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djEwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA1NjsiIGQ9Ik01MCAxMTAwaDEwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMTAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0xMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djEwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTM1MCAxMTAwaDgwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMTAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC04MDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djEwMCBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek01MCA4MDBoMTAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0xMDBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTEwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MTAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNMzUwIDgwMGg4MDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTEwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtODAwIHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MTAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNNTAgNTAwaDEwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMTAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0xMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djEwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTM1MCA1MDBoODAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0xMDAgcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC04MDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djEwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTUwIDIwMGgxMDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTEwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtMTAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYxMDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek0zNTAgMjAwaDgwMCBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTEwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtODAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYxMDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwNTc7IiBkPSJNNDAwIDBoLTEwMHYxMTAwaDEwMHYtMTEwMHpNNTUwIDExMDBoMTAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0xMDBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTEwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MTAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNNTUwIDgwMGg1MDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTEwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtNTAwIHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MTAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNMjY3IDU1MGwtMTY3IC0xMjV2NzVoLTIwMHYxMDBoMjAwdjc1ek01NTAgNTAwaDMwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMTAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0zMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djEwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTU1MCAyMDBoNjAwIHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMTAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC02MDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djEwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA1ODsiIGQ9Ik01MCAxMTAwaDEwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMTAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0xMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djEwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTkwMCAwaC0xMDB2MTEwMGgxMDB2LTExMDB6TTUwIDgwMGg1MDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTEwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtNTAwIHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MTAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNMTEwMCA2MDBoMjAwdi0xMDBoLTIwMHYtNzVsLTE2NyAxMjVsMTY3IDEyNXYtNzV6TTUwIDUwMGgzMDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTEwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtMzAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYxMDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek01MCAyMDBoNjAwIHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMTAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC02MDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djEwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA1OTsiIGQ9Ik03NSAxMDAwaDc1MHEzMSAwIDUzIC0yMnQyMiAtNTN2LTY1MHEwIC0zMSAtMjIgLTUzdC01MyAtMjJoLTc1MHEtMzEgMCAtNTMgMjJ0LTIyIDUzdjY1MHEwIDMxIDIyIDUzdDUzIDIyek0xMjAwIDMwMGwtMzAwIDMwMGwzMDAgMzAwdi02MDB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA2MDsiIGQ9Ik00NCAxMTAwaDExMTJxMTggMCAzMSAtMTN0MTMgLTMxdi0xMDEycTAgLTE4IC0xMyAtMzF0LTMxIC0xM2gtMTExMnEtMTggMCAtMzEgMTN0LTEzIDMxdjEwMTJxMCAxOCAxMyAzMXQzMSAxM3pNMTAwIDEwMDB2LTczN2wyNDcgMTgybDI5OCAtMTMxbC03NCAxNTZsMjkzIDMxOGwyMzYgLTI4OHY1MDBoLTEwMDB6TTM0MiA4ODRxNTYgMCA5NSAtMzl0MzkgLTk0LjV0LTM5IC05NXQtOTUgLTM5LjV0LTk1IDM5LjV0LTM5IDk1dDM5IDk0LjUgdDk1IDM5eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwNjI7IiBkPSJNNjQ4IDExNjlxMTE3IDAgMjE2IC02MHQxNTYuNSAtMTYxdDU3LjUgLTIxOHEwIC0xMTUgLTcwIC0yNThxLTY5IC0xMDkgLTE1OCAtMjI1LjV0LTE0MyAtMTc5LjVsLTU0IC02MnEtOSA4IC0yNS41IDI0LjV0LTYzLjUgNjcuNXQtOTEgMTAzdC05OC41IDEyOHQtOTUuNSAxNDhxLTYwIDEzMiAtNjAgMjQ5cTAgODggMzQgMTY5LjV0OTEuNSAxNDJ0MTM3IDk2LjV0MTY2LjUgMzZ6TTY1Mi41IDk3NHEtOTEuNSAwIC0xNTYuNSAtNjUgdC02NSAtMTU3dDY1IC0xNTYuNXQxNTYuNSAtNjQuNXQxNTYuNSA2NC41dDY1IDE1Ni41dC02NSAxNTd0LTE1Ni41IDY1eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwNjM7IiBkPSJNNjAwIDExNzdxMTE3IDAgMjI0IC00NS41dDE4NC41IC0xMjN0MTIzIC0xODQuNXQ0NS41IC0yMjR0LTQ1LjUgLTIyNHQtMTIzIC0xODQuNXQtMTg0LjUgLTEyM3QtMjI0IC00NS41dC0yMjQgNDUuNXQtMTg0LjUgMTIzdC0xMjMgMTg0LjV0LTQ1LjUgMjI0dDQ1LjUgMjI0dDEyMyAxODQuNXQxODQuNSAxMjN0MjI0IDQ1LjV6TTYwMCAxNzN2ODU0cS0xMTYgMCAtMjE0LjUgLTU3dC0xNTUuNSAtMTU1LjV0LTU3IC0yMTQuNXQ1NyAtMjE0LjUgdDE1NS41IC0xNTUuNXQyMTQuNSAtNTd6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA2NDsiIGQ9Ik01NTQgMTI5NXEyMSAtNzIgNTcuNSAtMTQzLjV0NzYgLTEzMHQ4MyAtMTE4dDgyLjUgLTExN3Q3MCAtMTE2dDQ5LjUgLTEyNnQxOC41IC0xMzYuNXEwIC03MSAtMjUuNSAtMTM1dC02OC41IC0xMTF0LTk5IC04MnQtMTE4LjUgLTU0dC0xMjUuNSAtMjNxLTg0IDUgLTE2MS41IDM0dC0xMzkuNSA3OC41dC05OSAxMjV0LTM3IDE2NC41cTAgNjkgMTggMTM2LjV0NDkuNSAxMjYuNXQ2OS41IDExNi41dDgxLjUgMTE3LjV0ODMuNSAxMTkgdDc2LjUgMTMxdDU4LjUgMTQzek0zNDQgNzEwcS0yMyAtMzMgLTQzLjUgLTcwLjV0LTQwLjUgLTEwMi41dC0xNyAtMTIzcTEgLTM3IDE0LjUgLTY5LjV0MzAgLTUydDQxIC0zN3QzOC41IC0yNC41dDMzIC0xNXEyMSAtNyAzMiAtMXQxMyAyMmw2IDM0cTIgMTAgLTIuNSAyMnQtMTMuNSAxOXEtNSA0IC0xNCAxMnQtMjkuNSA0MC41dC0zMi41IDczLjVxLTI2IDg5IDYgMjcxcTIgMTEgLTYgMTFxLTggMSAtMTUgLTEweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwNjU7IiBkPSJNMTAwMCAxMDEzbDEwOCAxMTVxMiAxIDUgMnQxMyAydDIwLjUgLTF0MjUgLTkuNXQyOC41IC0yMS41cTIyIC0yMiAyNyAtNDN0MCAtMzJsLTYgLTEwbC0xMDggLTExNXpNMzUwIDExMDBoNDAwcTUwIDAgMTA1IC0xM2wtMTg3IC0xODdoLTM2OHEtNDEgMCAtNzAuNSAtMjkuNXQtMjkuNSAtNzAuNXYtNTAwcTAgLTQxIDI5LjUgLTcwLjV0NzAuNSAtMjkuNWg1MDBxNDEgMCA3MC41IDI5LjV0MjkuNSA3MC41djE4MmwyMDAgMjAwdi0zMzIgcTAgLTE2NSAtOTMuNSAtMjU3LjV0LTI1Ni41IC05Mi41aC00MDBxLTE2NSAwIC0yNTcuNSA5Mi41dC05Mi41IDI1Ny41djQwMHEwIDE2NSA5Mi41IDI1Ny41dDI1Ny41IDkyLjV6TTEwMDkgODAzbC0zNjIgLTM2MmwtMTYxIC01MGw1NSAxNzBsMzU1IDM1NXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDY2OyIgZD0iTTM1MCAxMTAwaDM2MXEtMTY0IC0xNDYgLTIxNiAtMjAwaC0xOTVxLTQxIDAgLTcwLjUgLTI5LjV0LTI5LjUgLTcwLjV2LTUwMHEwIC00MSAyOS41IC03MC41dDcwLjUgLTI5LjVoNTAwcTQxIDAgNzAuNSAyOS41dDI5LjUgNzAuNWwyMDAgMTUzdi0xMDNxMCAtMTY1IC05Mi41IC0yNTcuNXQtMjU3LjUgLTkyLjVoLTQwMHEtMTY1IDAgLTI1Ny41IDkyLjV0LTkyLjUgMjU3LjV2NDAwcTAgMTY1IDkyLjUgMjU3LjV0MjU3LjUgOTIuNXogTTgyNCAxMDczbDMzOSAtMzAxcTggLTcgOCAtMTcuNXQtOCAtMTcuNWwtMzQwIC0zMDZxLTcgLTYgLTEyLjUgLTR0LTYuNSAxMXYyMDNxLTI2IDEgLTU0LjUgMHQtNzguNSAtNy41dC05MiAtMTcuNXQtODYgLTM1dC03MCAtNTdxMTAgNTkgMzMgMTA4dDUxLjUgODEuNXQ2NSA1OC41dDY4LjUgNDAuNXQ2NyAyNC41dDU2IDEzLjV0NDAgNC41djIxMHExIDEwIDYuNSAxMi41dDEzLjUgLTQuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDY3OyIgZD0iTTM1MCAxMTAwaDM1MHE2MCAwIDEyNyAtMjNsLTE3OCAtMTc3aC0zNDlxLTQxIDAgLTcwLjUgLTI5LjV0LTI5LjUgLTcwLjV2LTUwMHEwIC00MSAyOS41IC03MC41dDcwLjUgLTI5LjVoNTAwcTQxIDAgNzAuNSAyOS41dDI5LjUgNzAuNXY2OWwyMDAgMjAwdi0yMTlxMCAtMTY1IC05Mi41IC0yNTcuNXQtMjU3LjUgLTkyLjVoLTQwMHEtMTY1IDAgLTI1Ny41IDkyLjV0LTkyLjUgMjU3LjV2NDAwcTAgMTY1IDkyLjUgMjU3LjV0MjU3LjUgOTIuNXogTTY0MyA2MzlsMzk1IDM5NXE3IDcgMTcuNSA3dDE3LjUgLTdsMTAxIC0xMDFxNyAtNyA3IC0xNy41dC03IC0xNy41bC01MzEgLTUzMnEtNyAtNyAtMTcuNSAtN3QtMTcuNSA3bC0yNDggMjQ4cS03IDcgLTcgMTcuNXQ3IDE3LjVsMTAxIDEwMXE3IDcgMTcuNSA3dDE3LjUgLTdsMTExIC0xMTFxOCAtNyAxOCAtN3QxOCA3eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwNjg7IiBkPSJNMzE4IDkxOGwyNjQgMjY0cTggOCAxOCA4dDE4IC04bDI2MCAtMjY0cTcgLTggNC41IC0xM3QtMTIuNSAtNWgtMTcwdi0yMDBoMjAwdjE3M3EwIDEwIDUgMTJ0MTMgLTVsMjY0IC0yNjBxOCAtNyA4IC0xNy41dC04IC0xNy41bC0yNjQgLTI2NXEtOCAtNyAtMTMgLTV0LTUgMTJ2MTczaC0yMDB2LTIwMGgxNzBxMTAgMCAxMi41IC01dC00LjUgLTEzbC0yNjAgLTI2NHEtOCAtOCAtMTggLTh0LTE4IDhsLTI2NCAyNjRxLTggOCAtNS41IDEzIHQxMi41IDVoMTc1djIwMGgtMjAwdi0xNzNxMCAtMTAgLTUgLTEydC0xMyA1bC0yNjQgMjY1cS04IDcgLTggMTcuNXQ4IDE3LjVsMjY0IDI2MHE4IDcgMTMgNXQ1IC0xMnYtMTczaDIwMHYyMDBoLTE3NXEtMTAgMCAtMTIuNSA1dDUuNSAxM3oiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDY5OyIgZD0iTTI1MCAxMTAwaDEwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtNDM4bDQ2NCA0NTNxMTUgMTQgMjUuNSAxMHQxMC41IC0yNXYtMTAwMHEwIC0yMSAtMTAuNSAtMjV0LTI1LjUgMTBsLTQ2NCA0NTN2LTQzOHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtMTAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYxMDAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDcwOyIgZD0iTTUwIDExMDBoMTAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di00MzhsNDY0IDQ1M3ExNSAxNCAyNS41IDEwdDEwLjUgLTI1di00MzhsNDY0IDQ1M3ExNSAxNCAyNS41IDEwdDEwLjUgLTI1di0xMDAwcTAgLTIxIC0xMC41IC0yNXQtMjUuNSAxMGwtNDY0IDQ1M3YtNDM4cTAgLTIxIC0xMC41IC0yNXQtMjUuNSAxMGwtNDY0IDQ1M3YtNDM4cTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0xMDBxLTIxIDAgLTM1LjUgMTQuNSB0LTE0LjUgMzUuNXYxMDAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDcxOyIgZD0iTTEyMDAgMTA1MHYtMTAwMHEwIC0yMSAtMTAuNSAtMjV0LTI1LjUgMTBsLTQ2NCA0NTN2LTQzOHEwIC0yMSAtMTAuNSAtMjV0LTI1LjUgMTBsLTQ5MiA0ODBxLTE1IDE0IC0xNSAzNXQxNSAzNWw0OTIgNDgwcTE1IDE0IDI1LjUgMTB0MTAuNSAtMjV2LTQzOGw0NjQgNDUzcTE1IDE0IDI1LjUgMTB0MTAuNSAtMjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA3MjsiIGQ9Ik0yNDMgMTA3NGw4MTQgLTQ5OHExOCAtMTEgMTggLTI2dC0xOCAtMjZsLTgxNCAtNDk4cS0xOCAtMTEgLTMwLjUgLTR0LTEyLjUgMjh2MTAwMHEwIDIxIDEyLjUgMjh0MzAuNSAtNHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDczOyIgZD0iTTI1MCAxMDAwaDIwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtODAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0yMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djgwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTY1MCAxMDAwaDIwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtODAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0yMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djgwMCBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwNzQ7IiBkPSJNMTEwMCA5NTB2LTgwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtODAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXY4MDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41aDgwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDc1OyIgZD0iTTUwMCA2MTJ2NDM4cTAgMjEgMTAuNSAyNXQyNS41IC0xMGw0OTIgLTQ4MHExNSAtMTQgMTUgLTM1dC0xNSAtMzVsLTQ5MiAtNDgwcS0xNSAtMTQgLTI1LjUgLTEwdC0xMC41IDI1djQzOGwtNDY0IC00NTNxLTE1IC0xNCAtMjUuNSAtMTB0LTEwLjUgMjV2MTAwMHEwIDIxIDEwLjUgMjV0MjUuNSAtMTB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA3NjsiIGQ9Ik0xMDQ4IDExMDJsMTAwIDFxMjAgMCAzNSAtMTQuNXQxNSAtMzUuNWw1IC0xMDAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41bC0xMDAgLTFxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41bC0yIDQzN2wtNDYzIC00NTRxLTE0IC0xNSAtMjQuNSAtMTAuNXQtMTAuNSAyNS41bC0yIDQzN2wtNDYyIC00NTVxLTE1IC0xNCAtMjUuNSAtOS41dC0xMC41IDI0LjVsLTUgMTAwMHEwIDIxIDEwLjUgMjUuNXQyNS41IC0xMC41bDQ2NiAtNDUwIGwtMiA0MzhxMCAyMCAxMC41IDI0LjV0MjUuNSAtOS41bDQ2NiAtNDUxbC0yIDQzOHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA3NzsiIGQ9Ik04NTAgMTEwMGgxMDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTEwMDBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTEwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2NDM4bC00NjQgLTQ1M3EtMTUgLTE0IC0yNS41IC0xMHQtMTAuNSAyNXYxMDAwcTAgMjEgMTAuNSAyNXQyNS41IC0xMGw0NjQgLTQ1M3Y0MzhxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwNzg7IiBkPSJNNjg2IDEwODFsNTAxIC01NDBxMTUgLTE1IDEwLjUgLTI2dC0yNi41IC0xMWgtMTA0MnEtMjIgMCAtMjYuNSAxMXQxMC41IDI2bDUwMSA1NDBxMTUgMTUgMzYgMTV0MzYgLTE1ek0xNTAgNDAwaDEwMDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTEwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtMTAwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MTAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDc5OyIgZD0iTTg4NSA5MDBsLTM1MiAtMzUzbDM1MiAtMzUzbC0xOTcgLTE5OGwtNTUyIDU1Mmw1NTIgNTUweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwODA7IiBkPSJNMTA2NCA1NDdsLTU1MSAtNTUxbC0xOTggMTk4bDM1MyAzNTNsLTM1MyAzNTNsMTk4IDE5OHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDgxOyIgZD0iTTYwMCAxMTc3cTExNyAwIDIyNCAtNDUuNXQxODQuNSAtMTIzdDEyMyAtMTg0LjV0NDUuNSAtMjI0dC00NS41IC0yMjR0LTEyMyAtMTg0LjV0LTE4NC41IC0xMjN0LTIyNCAtNDUuNXQtMjI0IDQ1LjV0LTE4NC41IDEyM3QtMTIzIDE4NC41dC00NS41IDIyNHQ0NS41IDIyNHQxMjMgMTg0LjV0MTg0LjUgMTIzdDIyNCA0NS41ek02NTAgOTAwaC0xMDBxLTIxIDAgLTM1LjUgLTE0LjV0LTE0LjUgLTM1LjV2LTE1MGgtMTUwIHEtMjEgMCAtMzUuNSAtMTQuNXQtMTQuNSAtMzUuNXYtMTAwcTAgLTIxIDE0LjUgLTM1LjV0MzUuNSAtMTQuNWgxNTB2LTE1MHEwIC0yMSAxNC41IC0zNS41dDM1LjUgLTE0LjVoMTAwcTIxIDAgMzUuNSAxNC41dDE0LjUgMzUuNXYxNTBoMTUwcTIxIDAgMzUuNSAxNC41dDE0LjUgMzUuNXYxMDBxMCAyMSAtMTQuNSAzNS41dC0zNS41IDE0LjVoLTE1MHYxNTBxMCAyMSAtMTQuNSAzNS41dC0zNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA4MjsiIGQ9Ik02MDAgMTE3N3ExMTcgMCAyMjQgLTQ1LjV0MTg0LjUgLTEyM3QxMjMgLTE4NC41dDQ1LjUgLTIyNHQtNDUuNSAtMjI0dC0xMjMgLTE4NC41dC0xODQuNSAtMTIzdC0yMjQgLTQ1LjV0LTIyNCA0NS41dC0xODQuNSAxMjN0LTEyMyAxODQuNXQtNDUuNSAyMjR0NDUuNSAyMjR0MTIzIDE4NC41dDE4NC41IDEyM3QyMjQgNDUuNXpNODUwIDcwMGgtNTAwcS0yMSAwIC0zNS41IC0xNC41dC0xNC41IC0zNS41di0xMDBxMCAtMjEgMTQuNSAtMzUuNSB0MzUuNSAtMTQuNWg1MDBxMjEgMCAzNS41IDE0LjV0MTQuNSAzNS41djEwMHEwIDIxIC0xNC41IDM1LjV0LTM1LjUgMTQuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDgzOyIgZD0iTTYwMCAxMTc3cTExNyAwIDIyNCAtNDUuNXQxODQuNSAtMTIzdDEyMyAtMTg0LjV0NDUuNSAtMjI0dC00NS41IC0yMjR0LTEyMyAtMTg0LjV0LTE4NC41IC0xMjN0LTIyNCAtNDUuNXQtMjI0IDQ1LjV0LTE4NC41IDEyM3QtMTIzIDE4NC41dC00NS41IDIyNHQ0NS41IDIyNHQxMjMgMTg0LjV0MTg0LjUgMTIzdDIyNCA0NS41ek03NDEuNSA5MTNxLTEyLjUgMCAtMjEuNSAtOWwtMTIwIC0xMjBsLTEyMCAxMjBxLTkgOSAtMjEuNSA5IHQtMjEuNSAtOWwtMTQxIC0xNDFxLTkgLTkgLTkgLTIxLjV0OSAtMjEuNWwxMjAgLTEyMGwtMTIwIC0xMjBxLTkgLTkgLTkgLTIxLjV0OSAtMjEuNWwxNDEgLTE0MXE5IC05IDIxLjUgLTl0MjEuNSA5bDEyMCAxMjBsMTIwIC0xMjBxOSAtOSAyMS41IC05dDIxLjUgOWwxNDEgMTQxcTkgOSA5IDIxLjV0LTkgMjEuNWwtMTIwIDEyMGwxMjAgMTIwcTkgOSA5IDIxLjV0LTkgMjEuNWwtMTQxIDE0MXEtOSA5IC0yMS41IDl6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA4NDsiIGQ9Ik02MDAgMTE3N3ExMTcgMCAyMjQgLTQ1LjV0MTg0LjUgLTEyM3QxMjMgLTE4NC41dDQ1LjUgLTIyNHQtNDUuNSAtMjI0dC0xMjMgLTE4NC41dC0xODQuNSAtMTIzdC0yMjQgLTQ1LjV0LTIyNCA0NS41dC0xODQuNSAxMjN0LTEyMyAxODQuNXQtNDUuNSAyMjR0NDUuNSAyMjR0MTIzIDE4NC41dDE4NC41IDEyM3QyMjQgNDUuNXpNNTQ2IDYyM2wtODQgODVxLTcgNyAtMTcuNSA3dC0xOC41IC03bC0xMzkgLTEzOXEtNyAtOCAtNyAtMTh0NyAtMTggbDI0MiAtMjQxcTcgLTggMTcuNSAtOHQxNy41IDhsMzc1IDM3NXE3IDcgNyAxNy41dC03IDE4LjVsLTEzOSAxMzlxLTcgNyAtMTcuNSA3dC0xNy41IC03eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwODU7IiBkPSJNNjAwIDExNzdxMTE3IDAgMjI0IC00NS41dDE4NC41IC0xMjN0MTIzIC0xODQuNXQ0NS41IC0yMjR0LTQ1LjUgLTIyNHQtMTIzIC0xODQuNXQtMTg0LjUgLTEyM3QtMjI0IC00NS41dC0yMjQgNDUuNXQtMTg0LjUgMTIzdC0xMjMgMTg0LjV0LTQ1LjUgMjI0dDQ1LjUgMjI0dDEyMyAxODQuNXQxODQuNSAxMjN0MjI0IDQ1LjV6TTU4OCA5NDFxLTI5IDAgLTU5IC01LjV0LTYzIC0yMC41dC01OCAtMzguNXQtNDEuNSAtNjN0LTE2LjUgLTg5LjUgcTAgLTI1IDIwIC0yNWgxMzFxMzAgLTUgMzUgMTFxNiAyMCAyMC41IDI4dDQ1LjUgOHEyMCAwIDMxLjUgLTEwLjV0MTEuNSAtMjguNXEwIC0yMyAtNyAtMzR0LTI2IC0xOHEtMSAwIC0xMy41IC00dC0xOS41IC03LjV0LTIwIC0xMC41dC0yMiAtMTd0LTE4LjUgLTI0dC0xNS41IC0zNXQtOCAtNDZxLTEgLTggNS41IC0xNi41dDIwLjUgLTguNWgxNzNxNyAwIDIyIDh0MzUgMjh0MzcuNSA0OHQyOS41IDc0dDEyIDEwMHEwIDQ3IC0xNyA4MyB0LTQyLjUgNTd0LTU5LjUgMzQuNXQtNjQgMTh0LTU5IDQuNXpNNjc1IDQwMGgtMTUwcS0xMCAwIC0xNy41IC03LjV0LTcuNSAtMTcuNXYtMTUwcTAgLTEwIDcuNSAtMTcuNXQxNy41IC03LjVoMTUwcTEwIDAgMTcuNSA3LjV0Ny41IDE3LjV2MTUwcTAgMTAgLTcuNSAxNy41dC0xNy41IDcuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDg2OyIgZD0iTTYwMCAxMTc3cTExNyAwIDIyNCAtNDUuNXQxODQuNSAtMTIzdDEyMyAtMTg0LjV0NDUuNSAtMjI0dC00NS41IC0yMjR0LTEyMyAtMTg0LjV0LTE4NC41IC0xMjN0LTIyNCAtNDUuNXQtMjI0IDQ1LjV0LTE4NC41IDEyM3QtMTIzIDE4NC41dC00NS41IDIyNHQ0NS41IDIyNHQxMjMgMTg0LjV0MTg0LjUgMTIzdDIyNCA0NS41ek02NzUgMTAwMGgtMTUwcS0xMCAwIC0xNy41IC03LjV0LTcuNSAtMTcuNXYtMTUwcTAgLTEwIDcuNSAtMTcuNSB0MTcuNSAtNy41aDE1MHExMCAwIDE3LjUgNy41dDcuNSAxNy41djE1MHEwIDEwIC03LjUgMTcuNXQtMTcuNSA3LjV6TTY3NSA3MDBoLTI1MHEtMTAgMCAtMTcuNSAtNy41dC03LjUgLTE3LjV2LTUwcTAgLTEwIDcuNSAtMTcuNXQxNy41IC03LjVoNzV2LTIwMGgtNzVxLTEwIDAgLTE3LjUgLTcuNXQtNy41IC0xNy41di01MHEwIC0xMCA3LjUgLTE3LjV0MTcuNSAtNy41aDM1MHExMCAwIDE3LjUgNy41dDcuNSAxNy41djUwcTAgMTAgLTcuNSAxNy41IHQtMTcuNSA3LjVoLTc1djI3NXEwIDEwIC03LjUgMTcuNXQtMTcuNSA3LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA4NzsiIGQ9Ik01MjUgMTIwMGgxNTBxMTAgMCAxNy41IC03LjV0Ny41IC0xNy41di0xOTRxMTAzIC0yNyAxNzguNSAtMTAyLjV0MTAyLjUgLTE3OC41aDE5NHExMCAwIDE3LjUgLTcuNXQ3LjUgLTE3LjV2LTE1MHEwIC0xMCAtNy41IC0xNy41dC0xNy41IC03LjVoLTE5NHEtMjcgLTEwMyAtMTAyLjUgLTE3OC41dC0xNzguNSAtMTAyLjV2LTE5NHEwIC0xMCAtNy41IC0xNy41dC0xNy41IC03LjVoLTE1MHEtMTAgMCAtMTcuNSA3LjV0LTcuNSAxNy41djE5NCBxLTEwMyAyNyAtMTc4LjUgMTAyLjV0LTEwMi41IDE3OC41aC0xOTRxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXYxNTBxMCAxMCA3LjUgMTcuNXQxNy41IDcuNWgxOTRxMjcgMTAzIDEwMi41IDE3OC41dDE3OC41IDEwMi41djE5NHEwIDEwIDcuNSAxNy41dDE3LjUgNy41ek03MDAgODkzdi0xNjhxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC0xNTBxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXYxNjhxLTY4IC0yMyAtMTE5IC03NCB0LTc0IC0xMTloMTY4cTEwIDAgMTcuNSAtNy41dDcuNSAtMTcuNXYtMTUwcTAgLTEwIC03LjUgLTE3LjV0LTE3LjUgLTcuNWgtMTY4cTIzIC02OCA3NCAtMTE5dDExOSAtNzR2MTY4cTAgMTAgNy41IDE3LjV0MTcuNSA3LjVoMTUwcTEwIDAgMTcuNSAtNy41dDcuNSAtMTcuNXYtMTY4cTY4IDIzIDExOSA3NHQ3NCAxMTloLTE2OHEtMTAgMCAtMTcuNSA3LjV0LTcuNSAxNy41djE1MHEwIDEwIDcuNSAxNy41dDE3LjUgNy41aDE2OCBxLTIzIDY4IC03NCAxMTl0LTExOSA3NHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDg4OyIgZD0iTTYwMCAxMTc3cTExNyAwIDIyNCAtNDUuNXQxODQuNSAtMTIzdDEyMyAtMTg0LjV0NDUuNSAtMjI0dC00NS41IC0yMjR0LTEyMyAtMTg0LjV0LTE4NC41IC0xMjN0LTIyNCAtNDUuNXQtMjI0IDQ1LjV0LTE4NC41IDEyM3QtMTIzIDE4NC41dC00NS41IDIyNHQ0NS41IDIyNHQxMjMgMTg0LjV0MTg0LjUgMTIzdDIyNCA0NS41ek02MDAgMTAyN3EtMTE2IDAgLTIxNC41IC01N3QtMTU1LjUgLTE1NS41dC01NyAtMjE0LjV0NTcgLTIxNC41IHQxNTUuNSAtMTU1LjV0MjE0LjUgLTU3dDIxNC41IDU3dDE1NS41IDE1NS41dDU3IDIxNC41dC01NyAyMTQuNXQtMTU1LjUgMTU1LjV0LTIxNC41IDU3ek03NTkgODIzbDY0IC02NHE3IC03IDcgLTE3LjV0LTcgLTE3LjVsLTEyNCAtMTI0bDEyNCAtMTI0cTcgLTcgNyAtMTcuNXQtNyAtMTcuNWwtNjQgLTY0cS03IC03IC0xNy41IC03dC0xNy41IDdsLTEyNCAxMjRsLTEyNCAtMTI0cS03IC03IC0xNy41IC03dC0xNy41IDdsLTY0IDY0IHEtNyA3IC03IDE3LjV0NyAxNy41bDEyNCAxMjRsLTEyNCAxMjRxLTcgNyAtNyAxNy41dDcgMTcuNWw2NCA2NHE3IDcgMTcuNSA3dDE3LjUgLTdsMTI0IC0xMjRsMTI0IDEyNHE3IDcgMTcuNSA3dDE3LjUgLTd6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA4OTsiIGQ9Ik02MDAgMTE3N3ExMTcgMCAyMjQgLTQ1LjV0MTg0LjUgLTEyM3QxMjMgLTE4NC41dDQ1LjUgLTIyNHQtNDUuNSAtMjI0dC0xMjMgLTE4NC41dC0xODQuNSAtMTIzdC0yMjQgLTQ1LjV0LTIyNCA0NS41dC0xODQuNSAxMjN0LTEyMyAxODQuNXQtNDUuNSAyMjR0NDUuNSAyMjR0MTIzIDE4NC41dDE4NC41IDEyM3QyMjQgNDUuNXpNNjAwIDEwMjdxLTExNiAwIC0yMTQuNSAtNTd0LTE1NS41IC0xNTUuNXQtNTcgLTIxNC41dDU3IC0yMTQuNSB0MTU1LjUgLTE1NS41dDIxNC41IC01N3QyMTQuNSA1N3QxNTUuNSAxNTUuNXQ1NyAyMTQuNXQtNTcgMjE0LjV0LTE1NS41IDE1NS41dC0yMTQuNSA1N3pNNzgyIDc4OGwxMDYgLTEwNnE3IC03IDcgLTE3LjV0LTcgLTE3LjVsLTMyMCAtMzIxcS04IC03IC0xOCAtN3QtMTggN2wtMjAyIDIwM3EtOCA3IC04IDE3LjV0OCAxNy41bDEwNiAxMDZxNyA4IDE3LjUgOHQxNy41IC04bDc5IC03OWwxOTcgMTk3cTcgNyAxNy41IDd0MTcuNSAtN3oiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDkwOyIgZD0iTTYwMCAxMTc3cTExNyAwIDIyNCAtNDUuNXQxODQuNSAtMTIzdDEyMyAtMTg0LjV0NDUuNSAtMjI0dC00NS41IC0yMjR0LTEyMyAtMTg0LjV0LTE4NC41IC0xMjN0LTIyNCAtNDUuNXQtMjI0IDQ1LjV0LTE4NC41IDEyM3QtMTIzIDE4NC41dC00NS41IDIyNHQ0NS41IDIyNHQxMjMgMTg0LjV0MTg0LjUgMTIzdDIyNCA0NS41ek02MDAgMTAyN3EtMTE2IDAgLTIxNC41IC01N3QtMTU1LjUgLTE1NS41dC01NyAtMjE0LjVxMCAtMTIwIDY1IC0yMjUgbDU4NyA1ODdxLTEwNSA2NSAtMjI1IDY1ek05NjUgODE5bC01ODQgLTU4NHExMDQgLTYyIDIxOSAtNjJxMTE2IDAgMjE0LjUgNTd0MTU1LjUgMTU1LjV0NTcgMjE0LjVxMCAxMTUgLTYyIDIxOXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDkxOyIgZD0iTTM5IDU4Mmw1MjIgNDI3cTE2IDEzIDI3LjUgOHQxMS41IC0yNnYtMjkxaDU1MHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMjAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC01NTB2LTI5MXEwIC0yMSAtMTEuNSAtMjZ0LTI3LjUgOGwtNTIyIDQyN3EtMTYgMTMgLTE2IDMydDE2IDMyeiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUwOTI7IiBkPSJNNjM5IDEwMDlsNTIyIC00MjdxMTYgLTEzIDE2IC0zMnQtMTYgLTMybC01MjIgLTQyN3EtMTYgLTEzIC0yNy41IC04dC0xMS41IDI2djI5MWgtNTUwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYyMDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41aDU1MHYyOTFxMCAyMSAxMS41IDI2dDI3LjUgLTh6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA5MzsiIGQ9Ik02ODIgMTE2MWw0MjcgLTUyMnExMyAtMTYgOCAtMjcuNXQtMjYgLTExLjVoLTI5MXYtNTUwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0yMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djU1MGgtMjkxcS0yMSAwIC0yNiAxMS41dDggMjcuNWw0MjcgNTIycTEzIDE2IDMyIDE2dDMyIC0xNnoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDk0OyIgZD0iTTU1MCAxMjAwaDIwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtNTUwaDI5MXEyMSAwIDI2IC0xMS41dC04IC0yNy41bC00MjcgLTUyMnEtMTMgLTE2IC0zMiAtMTZ0LTMyIDE2bC00MjcgNTIycS0xMyAxNiAtOCAyNy41dDI2IDExLjVoMjkxdjU1MHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTA5NTsiIGQ9Ik02MzkgMTEwOWw1MjIgLTQyN3ExNiAtMTMgMTYgLTMydC0xNiAtMzJsLTUyMiAtNDI3cS0xNiAtMTMgLTI3LjUgLTh0LTExLjUgMjZ2MjkxcS05NCAtMiAtMTgyIC0yMHQtMTcwLjUgLTUydC0xNDcgLTkyLjV0LTEwMC41IC0xMzUuNXE1IDEwNSAyNyAxOTMuNXQ2Ny41IDE2N3QxMTMgMTM1dDE2NyA5MS41dDIyNS41IDQydjI2MnEwIDIxIDExLjUgMjZ0MjcuNSAtOHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDk2OyIgZD0iTTg1MCAxMjAwaDMwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMzAwcTAgLTIxIC0xMC41IC0yNXQtMjQuNSAxMGwtOTQgOTRsLTI0OSAtMjQ5cS04IC03IC0xOCAtN3QtMTggN2wtMTA2IDEwNnEtNyA4IC03IDE4dDcgMThsMjQ5IDI0OWwtOTQgOTRxLTE0IDE0IC0xMCAyNC41dDI1IDEwLjV6TTM1MCAwaC0zMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djMwMHEwIDIxIDEwLjUgMjV0MjQuNSAtMTBsOTQgLTk0bDI0OSAyNDkgcTggNyAxOCA3dDE4IC03bDEwNiAtMTA2cTcgLTggNyAtMTh0LTcgLTE4bC0yNDkgLTI0OWw5NCAtOTRxMTQgLTE0IDEwIC0yNC41dC0yNSAtMTAuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMDk3OyIgZD0iTTEwMTQgMTEyMGwxMDYgLTEwNnE3IC04IDcgLTE4dC03IC0xOGwtMjQ5IC0yNDlsOTQgLTk0cTE0IC0xNCAxMCAtMjQuNXQtMjUgLTEwLjVoLTMwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MzAwcTAgMjEgMTAuNSAyNXQyNC41IC0xMGw5NCAtOTRsMjQ5IDI0OXE4IDcgMTggN3QxOCAtN3pNMjUwIDYwMGgzMDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTMwMHEwIC0yMSAtMTAuNSAtMjV0LTI0LjUgMTBsLTk0IDk0IGwtMjQ5IC0yNDlxLTggLTcgLTE4IC03dC0xOCA3bC0xMDYgMTA2cS03IDggLTcgMTh0NyAxOGwyNDkgMjQ5bC05NCA5NHEtMTQgMTQgLTEwIDI0LjV0MjUgMTAuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTAxOyIgZD0iTTYwMCAxMTc3cTExNyAwIDIyNCAtNDUuNXQxODQuNSAtMTIzdDEyMyAtMTg0LjV0NDUuNSAtMjI0dC00NS41IC0yMjR0LTEyMyAtMTg0LjV0LTE4NC41IC0xMjN0LTIyNCAtNDUuNXQtMjI0IDQ1LjV0LTE4NC41IDEyM3QtMTIzIDE4NC41dC00NS41IDIyNHQ0NS41IDIyNHQxMjMgMTg0LjV0MTg0LjUgMTIzdDIyNCA0NS41ek03MDQgOTAwaC0yMDhxLTIwIDAgLTMyIC0xNC41dC04IC0zNC41bDU4IC0zMDJxNCAtMjAgMjEuNSAtMzQuNSB0MzcuNSAtMTQuNWg1NHEyMCAwIDM3LjUgMTQuNXQyMS41IDM0LjVsNTggMzAycTQgMjAgLTggMzQuNXQtMzIgMTQuNXpNNjc1IDQwMGgtMTUwcS0xMCAwIC0xNy41IC03LjV0LTcuNSAtMTcuNXYtMTUwcTAgLTEwIDcuNSAtMTcuNXQxNy41IC03LjVoMTUwcTEwIDAgMTcuNSA3LjV0Ny41IDE3LjV2MTUwcTAgMTAgLTcuNSAxNy41dC0xNy41IDcuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTAyOyIgZD0iTTI2MCAxMjAwcTkgMCAxOSAtMnQxNSAtNGw1IC0ycTIyIC0xMCA0NCAtMjNsMTk2IC0xMThxMjEgLTEzIDM2IC0yNHEyOSAtMjEgMzcgLTEycTExIDEzIDQ5IDM1bDE5NiAxMThxMjIgMTMgNDUgMjNxMTcgNyAzOCA3cTIzIDAgNDcgLTE2LjV0MzcgLTMzLjVsMTMgLTE2cTE0IC0yMSAxOCAtNDVsMjUgLTEyM2w4IC00NHExIC05IDguNSAtMTQuNXQxNy41IC01LjVoNjFxMTAgMCAxNy41IC03LjV0Ny41IC0xNy41di01MCBxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC01MHEtMTAgMCAtMTcuNSAtNy41dC03LjUgLTE3LjV2LTE3NWgtNDAwdjMwMGgtMjAwdi0zMDBoLTQwMHYxNzVxMCAxMCAtNy41IDE3LjV0LTE3LjUgNy41aC01MHEtMTAgMCAtMTcuNSA3LjV0LTcuNSAxNy41djUwcTAgMTAgNy41IDE3LjV0MTcuNSA3LjVoNjFxMTEgMCAxOCAzdDcgOHEwIDQgOSA1MmwyNSAxMjhxNSAyNSAxOSA0NXEyIDMgNSA3dDEzLjUgMTV0MjEuNSAxOS41dDI2LjUgMTUuNSB0MjkuNSA3ek05MTUgMTA3OWwtMTY2IC0xNjJxLTcgLTcgLTUgLTEydDEyIC01aDIxOXExMCAwIDE1IDd0MiAxN2wtNTEgMTQ5cS0zIDEwIC0xMSAxMnQtMTUgLTZ6TTQ2MyA5MTdsLTE3NyAxNTdxLTggNyAtMTYgNXQtMTEgLTEybC01MSAtMTQzcS0zIC0xMCAyIC0xN3QxNSAtN2gyMzFxMTEgMCAxMi41IDV0LTUuNSAxMnpNNTAwIDBoLTM3NXEtMTAgMCAtMTcuNSA3LjV0LTcuNSAxNy41djM3NWg0MDB2LTQwMHpNMTEwMCA0MDB2LTM3NSBxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC0zNzV2NDAwaDQwMHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTAzOyIgZD0iTTExNjUgMTE5MHE4IDMgMjEgLTYuNXQxMyAtMTcuNXEtMiAtMTc4IC0yNC41IC0zMjMuNXQtNTUuNSAtMjQ1LjV0LTg3IC0xNzQuNXQtMTAyLjUgLTExOC41dC0xMTggLTY4LjV0LTExOC41IC0zM3QtMTIwIC00LjV0LTEwNSA5LjV0LTkwIDE2LjVxLTYxIDEyIC03OCAxMXEtNCAxIC0xMi41IDB0LTM0IC0xNC41dC01Mi41IC00MC41bC0xNTMgLTE1M3EtMjYgLTI0IC0zNyAtMTQuNXQtMTEgNDMuNXEwIDY0IDQyIDEwMnE4IDggNTAuNSA0NSB0NjYuNSA1OHExOSAxNyAzNSA0N3QxMyA2MXEtOSA1NSAtMTAgMTAyLjV0NyAxMTF0MzcgMTMwdDc4IDEyOS41cTM5IDUxIDgwIDg4dDg5LjUgNjMuNXQ5NC41IDQ1dDExMy41IDM2dDEyOSAzMXQxNTcuNSAzN3QxODIgNDcuNXpNMTExNiAxMDk4cS04IDkgLTIyLjUgLTN0LTQ1LjUgLTUwcS0zOCAtNDcgLTExOSAtMTAzLjV0LTE0MiAtODkuNWwtNjIgLTMzcS01NiAtMzAgLTEwMiAtNTd0LTEwNCAtNjh0LTEwMi41IC04MC41dC04NS41IC05MSB0LTY0IC0xMDQuNXEtMjQgLTU2IC0zMSAtODZ0MiAtMzJ0MzEuNSAxNy41dDU1LjUgNTkuNXEyNSAzMCA5NCA3NS41dDEyNS41IDc3LjV0MTQ3LjUgODFxNzAgMzcgMTE4LjUgNjl0MTAyIDc5LjV0OTkgMTExdDg2LjUgMTQ4LjVxMjIgNTAgMjQgNjB0LTYgMTl6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTEwNDsiIGQ9Ik02NTMgMTIzMXEtMzkgLTY3IC01NC41IC0xMzF0LTEwLjUgLTExNC41dDI0LjUgLTk2LjV0NDcuNSAtODB0NjMuNSAtNjIuNXQ2OC41IC00Ni41dDY1IC0zMHEtNCA3IC0xNy41IDM1dC0xOC41IDM5LjV0LTE3IDM5LjV0LTE3IDQzdC0xMyA0MnQtOS41IDQ0LjV0LTIgNDJ0NCA0M3QxMy41IDM5dDIzIDM4LjVxOTYgLTQyIDE2NSAtMTA3LjV0MTA1IC0xMzh0NTIgLTE1NnQxMyAtMTU5dC0xOSAtMTQ5LjVxLTEzIC01NSAtNDQgLTEwNi41IHQtNjggLTg3dC03OC41IC02NC41dC03Mi41IC00NXQtNTMgLTIycS03MiAtMjIgLTEyNyAtMTFxLTMxIDYgLTEzIDE5cTYgMyAxNyA3cTEzIDUgMzIuNSAyMXQ0MSA0NHQzOC41IDYzLjV0MjEuNSA4MS41dC02LjUgOTQuNXQtNTAgMTA3dC0xMDQgMTE1LjVxMTAgLTEwNCAtMC41IC0xODl0LTM3IC0xNDAuNXQtNjUgLTkzdC04NCAtNTJ0LTkzLjUgLTExdC05NSAyNC41cS04MCAzNiAtMTMxLjUgMTE0dC01My41IDE3MXEtMiAyMyAwIDQ5LjUgdDQuNSA1Mi41dDEzLjUgNTZ0MjcuNSA2MHQ0NiA2NC41dDY5LjUgNjguNXEtOCAtNTMgLTUgLTEwMi41dDE3LjUgLTkwdDM0IC02OC41dDQ0LjUgLTM5dDQ5IC0ycTMxIDEzIDM4LjUgMzZ0LTQuNSA1NXQtMjkgNjQuNXQtMzYgNzV0LTI2IDc1LjVxLTE1IDg1IDIgMTYxLjV0NTMuNSAxMjguNXQ4NS41IDkyLjV0OTMuNSA2MXQ4MS41IDI1LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTEwNTsiIGQ9Ik02MDAgMTA5NHE4MiAwIDE2MC41IC0yMi41dDE0MCAtNTl0MTE2LjUgLTgyLjV0OTQuNSAtOTV0NjggLTk1dDQyLjUgLTgyLjV0MTQgLTU3LjV0LTE0IC01Ny41dC00MyAtODIuNXQtNjguNSAtOTV0LTk0LjUgLTk1dC0xMTYuNSAtODIuNXQtMTQwIC01OXQtMTU5LjUgLTIyLjV0LTE1OS41IDIyLjV0LTE0MCA1OXQtMTE2LjUgODIuNXQtOTQuNSA5NXQtNjguNSA5NXQtNDMgODIuNXQtMTQgNTcuNXQxNCA1Ny41dDQyLjUgODIuNXQ2OCA5NSB0OTQuNSA5NXQxMTYuNSA4Mi41dDE0MCA1OXQxNjAuNSAyMi41ek04ODggODI5cS0xNSAxNSAtMTggMTJ0NSAtMjJxMjUgLTU3IDI1IC0xMTlxMCAtMTI0IC04OCAtMjEydC0yMTIgLTg4dC0yMTIgODh0LTg4IDIxMnEwIDU5IDIzIDExNHE4IDE5IDQuNSAyMnQtMTcuNSAtMTJxLTcwIC02OSAtMTYwIC0xODRxLTEzIC0xNiAtMTUgLTQwLjV0OSAtNDIuNXEyMiAtMzYgNDcgLTcxdDcwIC04MnQ5Mi41IC04MXQxMTMgLTU4LjV0MTMzLjUgLTI0LjUgdDEzMy41IDI0dDExMyA1OC41dDkyLjUgODEuNXQ3MCA4MS41dDQ3IDcwLjVxMTEgMTggOSA0Mi41dC0xNCA0MS41cS05MCAxMTcgLTE2MyAxODl6TTQ0OCA3MjdsLTM1IC0zNnEtMTUgLTE1IC0xOS41IC0zOC41dDQuNSAtNDEuNXEzNyAtNjggOTMgLTExNnExNiAtMTMgMzguNSAtMTF0MzYuNSAxN2wzNSAzNHExNCAxNSAxMi41IDMzLjV0LTE2LjUgMzMuNXEtNDQgNDQgLTg5IDExN3EtMTEgMTggLTI4IDIwdC0zMiAtMTJ6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTEwNjsiIGQ9Ik01OTIgMGgtMTQ4bDMxIDEyMHEtOTEgMjAgLTE3NS41IDY4LjV0LTE0My41IDEwNi41dC0xMDMuNSAxMTl0LTY2LjUgMTEwdC0yMiA3NnEwIDIxIDE0IDU3LjV0NDIuNSA4Mi41dDY4IDk1dDk0LjUgOTV0MTE2LjUgODIuNXQxNDAgNTl0MTYwLjUgMjIuNXE2MSAwIDEyNiAtMTVsMzIgMTIxaDE0OHpNOTQ0IDc3MGw0NyAxODFxMTA4IC04NSAxNzYuNSAtMTkydDY4LjUgLTE1OXEwIC0yNiAtMTkuNSAtNzF0LTU5LjUgLTEwMnQtOTMgLTExMiB0LTEyOSAtMTA0LjV0LTE1OCAtNzUuNWw0NiAxNzNxNzcgNDkgMTM2IDExN3Q5NyAxMzFxMTEgMTggOSA0Mi41dC0xNCA0MS41cS01NCA3MCAtMTA3IDEzMHpNMzEwIDgyNHEtNzAgLTY5IC0xNjAgLTE4NHEtMTMgLTE2IC0xNSAtNDAuNXQ5IC00Mi41cTE4IC0zMCAzOSAtNjB0NTcgLTcwLjV0NzQgLTczdDkwIC02MXQxMDUgLTQxLjVsNDEgMTU0cS0xMDcgMTggLTE3OC41IDEwMS41dC03MS41IDE5My41cTAgNTkgMjMgMTE0cTggMTkgNC41IDIyIHQtMTcuNSAtMTJ6TTQ0OCA3MjdsLTM1IC0zNnEtMTUgLTE1IC0xOS41IC0zOC41dDQuNSAtNDEuNXEzNyAtNjggOTMgLTExNnExNiAtMTMgMzguNSAtMTF0MzYuNSAxN2wxMiAxMWwyMiA4NmwtMyA0cS00NCA0NCAtODkgMTE3cS0xMSAxOCAtMjggMjB0LTMyIC0xMnoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTA3OyIgZD0iTS05MCAxMDBsNjQyIDEwNjZxMjAgMzEgNDggMjguNXQ0OCAtMzUuNWw2NDIgLTEwNTZxMjEgLTMyIDcuNSAtNjcuNXQtNTAuNSAtMzUuNWgtMTI5NHEtMzcgMCAtNTAuNSAzNHQ3LjUgNjZ6TTE1NSAyMDBoMzQ1djc1cTAgMTAgNy41IDE3LjV0MTcuNSA3LjVoMTUwcTEwIDAgMTcuNSAtNy41dDcuNSAtMTcuNXYtNzVoMzQ1bC00NDUgNzIzek00OTYgNzAwaDIwOHEyMCAwIDMyIC0xNC41dDggLTM0LjVsLTU4IC0yNTIgcS00IC0yMCAtMjEuNSAtMzQuNXQtMzcuNSAtMTQuNWgtNTRxLTIwIDAgLTM3LjUgMTQuNXQtMjEuNSAzNC41bC01OCAyNTJxLTQgMjAgOCAzNC41dDMyIDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTEwODsiIGQ9Ik02NTAgMTIwMHE2MiAwIDEwNiAtNDR0NDQgLTEwNnYtMzM5bDM2MyAtMzI1cTE1IC0xNCAyNiAtMzguNXQxMSAtNDQuNXYtNDFxMCAtMjAgLTEyIC0yNi41dC0yOSA1LjVsLTM1OSAyNDl2LTI2M3ExMDAgLTkzIDEwMCAtMTEzdi02NHEwIC0yMSAtMTMgLTI5dC0zMiAxbC0yMDUgMTI4bC0yMDUgLTEyOHEtMTkgLTkgLTMyIC0xdC0xMyAyOXY2NHEwIDIwIDEwMCAxMTN2MjYzbC0zNTkgLTI0OXEtMTcgLTEyIC0yOSAtNS41dC0xMiAyNi41djQxIHEwIDIwIDExIDQ0LjV0MjYgMzguNWwzNjMgMzI1djMzOXEwIDYyIDQ0IDEwNnQxMDYgNDR6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTEwOTsiIGQ9Ik04NTAgMTIwMGgxMDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTUwaDUwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0xNTBoLTExMDB2MTUwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNWg1MHY1MHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjVoMTAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di01MGg1MDB2NTBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek0xMTAwIDgwMHYtNzUwcTAgLTIxIC0xNC41IC0zNS41IHQtMzUuNSAtMTQuNWgtMTAwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2NzUwaDExMDB6TTEwMCA2MDB2LTEwMGgxMDB2MTAwaC0xMDB6TTMwMCA2MDB2LTEwMGgxMDB2MTAwaC0xMDB6TTUwMCA2MDB2LTEwMGgxMDB2MTAwaC0xMDB6TTcwMCA2MDB2LTEwMGgxMDB2MTAwaC0xMDB6TTkwMCA2MDB2LTEwMGgxMDB2MTAwaC0xMDB6TTEwMCA0MDB2LTEwMGgxMDB2MTAwaC0xMDB6TTMwMCA0MDB2LTEwMGgxMDB2MTAwaC0xMDB6TTUwMCA0MDAgdi0xMDBoMTAwdjEwMGgtMTAwek03MDAgNDAwdi0xMDBoMTAwdjEwMGgtMTAwek05MDAgNDAwdi0xMDBoMTAwdjEwMGgtMTAwek0xMDAgMjAwdi0xMDBoMTAwdjEwMGgtMTAwek0zMDAgMjAwdi0xMDBoMTAwdjEwMGgtMTAwek01MDAgMjAwdi0xMDBoMTAwdjEwMGgtMTAwek03MDAgMjAwdi0xMDBoMTAwdjEwMGgtMTAwek05MDAgMjAwdi0xMDBoMTAwdjEwMGgtMTAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxMTA7IiBkPSJNMTEzNSAxMTY1bDI0OSAtMjMwcTE1IC0xNCAxNSAtMzV0LTE1IC0zNWwtMjQ5IC0yMzBxLTE0IC0xNCAtMjQuNSAtMTB0LTEwLjUgMjV2MTUwaC0xNTlsLTYwMCAtNjAwaC0yOTFxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djEwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjVoMjA5bDYwMCA2MDBoMjQxdjE1MHEwIDIxIDEwLjUgMjV0MjQuNSAtMTB6TTUyMiA4MTlsLTE0MSAtMTQxbC0xMjIgMTIyaC0yMDlxLTIxIDAgLTM1LjUgMTQuNSB0LTE0LjUgMzUuNXYxMDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41aDI5MXpNMTEzNSA1NjVsMjQ5IC0yMzBxMTUgLTE0IDE1IC0zNXQtMTUgLTM1bC0yNDkgLTIzMHEtMTQgLTE0IC0yNC41IC0xMHQtMTAuNSAyNXYxNTBoLTI0MWwtMTgxIDE4MWwxNDEgMTQxbDEyMiAtMTIyaDE1OXYxNTBxMCAyMSAxMC41IDI1dDI0LjUgLTEweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxMTE7IiBkPSJNMTAwIDExMDBoMTAwMHE0MSAwIDcwLjUgLTI5LjV0MjkuNSAtNzAuNXYtNjAwcTAgLTQxIC0yOS41IC03MC41dC03MC41IC0yOS41aC01OTZsLTMwNCAtMzAwdjMwMGgtMTAwcS00MSAwIC03MC41IDI5LjV0LTI5LjUgNzAuNXY2MDBxMCA0MSAyOS41IDcwLjV0NzAuNSAyOS41eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxMTI7IiBkPSJNMTUwIDEyMDBoMjAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0yNTBoLTMwMHYyNTBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek04NTAgMTIwMGgyMDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTI1MGgtMzAwdjI1MHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTExMDAgODAwdi0zMDBxMCAtNDEgLTMgLTc3LjV0LTE1IC04OS41dC0zMiAtOTZ0LTU4IC04OXQtODkgLTc3dC0xMjkgLTUxdC0xNzQgLTIwdC0xNzQgMjAgdC0xMjkgNTF0LTg5IDc3dC01OCA4OXQtMzIgOTZ0LTE1IDg5LjV0LTMgNzcuNXYzMDBoMzAwdi0yNTB2LTI3di00Mi41dDEuNSAtNDF0NSAtMzh0MTAgLTM1dDE2LjUgLTMwdDI1LjUgLTI0LjV0MzUgLTE5dDQ2LjUgLTEydDYwIC00dDYwIDQuNXQ0Ni41IDEyLjV0MzUgMTkuNXQyNSAyNS41dDE3IDMwLjV0MTAgMzV0NSAzOHQyIDQwLjV0LTAuNSA0MnYyNXYyNTBoMzAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxMTM7IiBkPSJNMTEwMCA0MTFsLTE5OCAtMTk5bC0zNTMgMzUzbC0zNTMgLTM1M2wtMTk3IDE5OWw1NTEgNTUxeiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxMTQ7IiBkPSJNMTEwMSA3ODlsLTU1MCAtNTUxbC01NTEgNTUxbDE5OCAxOTlsMzUzIC0zNTNsMzUzIDM1M3oiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTE1OyIgZD0iTTQwNCAxMDAwaDc0NnEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtNTUxaDE1MHEyMSAwIDI1IC0xMC41dC0xMCAtMjQuNWwtMjMwIC0yNDlxLTE0IC0xNSAtMzUgLTE1dC0zNSAxNWwtMjMwIDI0OXEtMTQgMTQgLTEwIDI0LjV0MjUgMTAuNWgxNTB2NDAxaC0zODF6TTEzNSA5ODRsMjMwIC0yNDlxMTQgLTE0IDEwIC0yNC41dC0yNSAtMTAuNWgtMTUwdi00MDBoMzg1bDIxNSAtMjAwaC03NTBxLTIxIDAgLTM1LjUgMTQuNSB0LTE0LjUgMzUuNXY1NTBoLTE1MHEtMjEgMCAtMjUgMTAuNXQxMCAyNC41bDIzMCAyNDlxMTQgMTUgMzUgMTV0MzUgLTE1eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxMTY7IiBkPSJNNTYgMTIwMGg5NHExNyAwIDMxIC0xMXQxOCAtMjdsMzggLTE2Mmg4OTZxMjQgMCAzOSAtMTguNXQxMCAtNDIuNWwtMTAwIC00NzVxLTUgLTIxIC0yNyAtNDIuNXQtNTUgLTIxLjVoLTYzM2w0OCAtMjAwaDUzNXEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXQtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtNTB2LTUwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41dC0zNS41IDE0LjV0LTE0LjUgMzUuNXY1MGgtMzAwdi01MCBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjV0LTM1LjUgMTQuNXQtMTQuNSAzNS41djUwaC0zMXEtMTggMCAtMzIuNSAxMHQtMjAuNSAxOWwtNSAxMGwtMjAxIDk2MWgtNTRxLTIwIDAgLTM1IDE0LjV0LTE1IDM1LjV0MTUgMzUuNXQzNSAxNC41eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxMTc7IiBkPSJNMTIwMCAxMDAwdi0xMDBoLTEyMDB2MTAwaDIwMHEwIDQxIDI5LjUgNzAuNXQ3MC41IDI5LjVoMzAwcTQxIDAgNzAuNSAtMjkuNXQyOS41IC03MC41aDUwMHpNMCA4MDBoMTIwMHYtODAwaC0xMjAwdjgwMHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTE4OyIgZD0iTTIwMCA4MDBsLTIwMCAtNDAwdjYwMGgyMDBxMCA0MSAyOS41IDcwLjV0NzAuNSAyOS41aDMwMHE0MiAwIDcxIC0yOS41dDI5IC03MC41aDUwMHYtMjAwaC0xMDAwek0xNTAwIDcwMGwtMzAwIC03MDBoLTEyMDBsMzAwIDcwMGgxMjAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxMTk7IiBkPSJNNjM1IDExODRsMjMwIC0yNDlxMTQgLTE0IDEwIC0yNC41dC0yNSAtMTAuNWgtMTUwdi02MDFoMTUwcTIxIDAgMjUgLTEwLjV0LTEwIC0yNC41bC0yMzAgLTI0OXEtMTQgLTE1IC0zNSAtMTV0LTM1IDE1bC0yMzAgMjQ5cS0xNCAxNCAtMTAgMjQuNXQyNSAxMC41aDE1MHY2MDFoLTE1MHEtMjEgMCAtMjUgMTAuNXQxMCAyNC41bDIzMCAyNDlxMTQgMTUgMzUgMTV0MzUgLTE1eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxMjA7IiBkPSJNOTM2IDg2NGwyNDkgLTIyOXExNCAtMTUgMTQgLTM1LjV0LTE0IC0zNS41bC0yNDkgLTIyOXEtMTUgLTE1IC0yNS41IC0xMC41dC0xMC41IDI0LjV2MTUxaC02MDB2LTE1MXEwIC0yMCAtMTAuNSAtMjQuNXQtMjUuNSAxMC41bC0yNDkgMjI5cS0xNCAxNSAtMTQgMzUuNXQxNCAzNS41bDI0OSAyMjlxMTUgMTUgMjUuNSAxMC41dDEwLjUgLTI1LjV2LTE0OWg2MDB2MTQ5cTAgMjEgMTAuNSAyNS41dDI1LjUgLTEwLjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTEyMTsiIGQ9Ik0xMTY5IDQwMGwtMTcyIDczMnEtNSAyMyAtMjMgNDUuNXQtMzggMjIuNWgtNjcycS0yMCAwIC0zOCAtMjB0LTIzIC00MWwtMTcyIC03MzloMTEzOHpNMTEwMCAzMDBoLTEwMDBxLTQxIDAgLTcwLjUgLTI5LjV0LTI5LjUgLTcwLjV2LTEwMHEwIC00MSAyOS41IC03MC41dDcwLjUgLTI5LjVoMTAwMHE0MSAwIDcwLjUgMjkuNXQyOS41IDcwLjV2MTAwcTAgNDEgLTI5LjUgNzAuNXQtNzAuNSAyOS41ek04MDAgMTAwdjEwMGgxMDB2LTEwMGgtMTAwIHpNMTAwMCAxMDB2MTAwaDEwMHYtMTAwaC0xMDB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTEyMjsiIGQ9Ik0xMTUwIDExMDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTg1MHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNXQtMzUuNSAxNC41dC0xNC41IDM1LjV2ODUwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNMTAwMCAyMDBsLTY3NSAyMDBoLTM4bDQ3IC0yNzZxMyAtMTYgLTUuNSAtMjB0LTI5LjUgLTRoLTdoLTg0cS0yMCAwIC0zNC41IDE0dC0xOC41IDM1cS01NSAzMzcgLTU1IDM1MXYyNTB2NnEwIDE2IDEgMjMuNXQ2LjUgMTQgdDE3LjUgNi41aDIwMGw2NzUgMjUwdi04NTB6TTAgNzUwdi0yNTBxLTQgMCAtMTEgMC41dC0yNCA2dC0zMCAxNXQtMjQgMzB0LTExIDQ4LjV2NTBxMCAyNiAxMC41IDQ2dDI1IDMwdDI5IDE2dDI1LjUgN3oiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTIzOyIgZD0iTTU1MyAxMjAwaDk0cTIwIDAgMjkgLTEwLjV0MyAtMjkuNWwtMTggLTM3cTgzIC0xOSAxNDQgLTgyLjV0NzYgLTE0MC41bDYzIC0zMjdsMTE4IC0xNzNoMTdxMTkgMCAzMyAtMTQuNXQxNCAtMzV0LTEzIC00MC41dC0zMSAtMjdxLTggLTQgLTIzIC05LjV0LTY1IC0xOS41dC0xMDMgLTI1dC0xMzIuNSAtMjB0LTE1OC41IC05cS01NyAwIC0xMTUgNXQtMTA0IDEydC04OC41IDE1LjV0LTczLjUgMTcuNXQtNTQuNSAxNnQtMzUuNSAxMmwtMTEgNCBxLTE4IDggLTMxIDI4dC0xMyA0MC41dDE0IDM1dDMzIDE0LjVoMTdsMTE4IDE3M2w2MyAzMjdxMTUgNzcgNzYgMTQwdDE0NCA4M2wtMTggMzJxLTYgMTkgMy41IDMydDI4LjUgMTN6TTQ5OCAxMTBxNTAgLTYgMTAyIC02cTUzIDAgMTAyIDZxLTEyIC00OSAtMzkuNSAtNzkuNXQtNjIuNSAtMzAuNXQtNjMgMzAuNXQtMzkgNzkuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTI0OyIgZD0iTTgwMCA5NDZsMjI0IDc4bC03OCAtMjI0bDIzNCAtNDVsLTE4MCAtMTU1bDE4MCAtMTU1bC0yMzQgLTQ1bDc4IC0yMjRsLTIyNCA3OGwtNDUgLTIzNGwtMTU1IDE4MGwtMTU1IC0xODBsLTQ1IDIzNGwtMjI0IC03OGw3OCAyMjRsLTIzNCA0NWwxODAgMTU1bC0xODAgMTU1bDIzNCA0NWwtNzggMjI0bDIyNCAtNzhsNDUgMjM0bDE1NSAtMTgwbDE1NSAxODB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTEyNTsiIGQ9Ik02NTAgMTIwMGg1MHE0MCAwIDcwIC00MC41dDMwIC04NC41di0xNTBsLTI4IC0xMjVoMzI4cTQwIDAgNzAgLTQwLjV0MzAgLTg0LjV2LTEwMHEwIC00NSAtMjkgLTc0bC0yMzggLTM0NHEtMTYgLTI0IC0zOCAtNDAuNXQtNDUgLTE2LjVoLTI1MHEtNyAwIC00MiAyNXQtNjYgNTBsLTMxIDI1aC02MXEtNDUgMCAtNzIuNSAxOHQtMjcuNSA1N3Y0MDBxMCAzNiAyMCA2M2wxNDUgMTk2bDk2IDE5OHExMyAyOCAzNy41IDQ4dDUxLjUgMjB6IE02NTAgMTEwMGwtMTAwIC0yMTJsLTE1MCAtMjEzdi0zNzVoMTAwbDEzNiAtMTAwaDIxNGwyNTAgMzc1djEyNWgtNDUwbDUwIDIyNXYxNzVoLTUwek01MCA4MDBoMTAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di01MDBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTEwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2NTAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTI2OyIgZD0iTTYwMCAxMTAwaDI1MHEyMyAwIDQ1IC0xNi41dDM4IC00MC41bDIzOCAtMzQ0cTI5IC0yOSAyOSAtNzR2LTEwMHEwIC00NCAtMzAgLTg0LjV0LTcwIC00MC41aC0zMjhxMjggLTExOCAyOCAtMTI1di0xNTBxMCAtNDQgLTMwIC04NC41dC03MCAtNDAuNWgtNTBxLTI3IDAgLTUxLjUgMjB0LTM3LjUgNDhsLTk2IDE5OGwtMTQ1IDE5NnEtMjAgMjcgLTIwIDYzdjQwMHEwIDM5IDI3LjUgNTd0NzIuNSAxOGg2MXExMjQgMTAwIDEzOSAxMDB6IE01MCAxMDAwaDEwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtNTAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0xMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djUwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTYzNiAxMDAwbC0xMzYgLTEwMGgtMTAwdi0zNzVsMTUwIC0yMTNsMTAwIC0yMTJoNTB2MTc1bC01MCAyMjVoNDUwdjEyNWwtMjUwIDM3NWgtMjE0eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxMjc7IiBkPSJNMzU2IDg3M2wzNjMgMjMwcTMxIDE2IDUzIC02bDExMCAtMTEycTEzIC0xMyAxMy41IC0zMnQtMTEuNSAtMzRsLTg0IC0xMjFoMzAycTg0IDAgMTM4IC0zOHQ1NCAtMTEwdC01NSAtMTExdC0xMzkgLTM5aC0xMDZsLTEzMSAtMzM5cS02IC0yMSAtMTkuNSAtNDF0LTI4LjUgLTIwaC0zNDJxLTcgMCAtOTAgODF0LTgzIDk0djUyNXEwIDE3IDE0IDM1LjV0MjggMjguNXpNNDAwIDc5MnYtNTAzbDEwMCAtODloMjkzbDEzMSAzMzkgcTYgMjEgMTkuNSA0MXQyOC41IDIwaDIwM3EyMSAwIDMwLjUgMjV0MC41IDUwdC0zMSAyNWgtNDU2aC03aC02aC01LjV0LTYgMC41dC01IDEuNXQtNSAydC00IDIuNXQtNCA0dC0yLjUgNC41cS0xMiAyNSA1IDQ3bDE0NiAxODNsLTg2IDgzek01MCA4MDBoMTAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di01MDBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTEwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2NTAwIHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTEyODsiIGQ9Ik00NzUgMTEwM2wzNjYgLTIzMHEyIC0xIDYgLTMuNXQxNCAtMTAuNXQxOCAtMTYuNXQxNC41IC0yMHQ2LjUgLTIyLjV2LTUyNXEwIC0xMyAtODYgLTk0dC05MyAtODFoLTM0MnEtMTUgMCAtMjguNSAyMHQtMTkuNSA0MWwtMTMxIDMzOWgtMTA2cS04NSAwIC0xMzkuNSAzOXQtNTQuNSAxMTF0NTQgMTEwdDEzOCAzOGgzMDJsLTg1IDEyMXEtMTEgMTUgLTEwLjUgMzR0MTMuNSAzMmwxMTAgMTEycTIyIDIyIDUzIDZ6TTM3MCA5NDVsMTQ2IC0xODMgcTE3IC0yMiA1IC00N3EtMiAtMiAtMy41IC00LjV0LTQgLTR0LTQgLTIuNXQtNSAtMnQtNSAtMS41dC02IC0wLjVoLTZoLTYuNWgtNmgtNDc1di0xMDBoMjIxcTE1IDAgMjkgLTIwdDIwIC00MWwxMzAgLTMzOWgyOTRsMTA2IDg5djUwM2wtMzQyIDIzNnpNMTA1MCA4MDBoMTAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di01MDBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTEwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjUgdjUwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTEyOTsiIGQ9Ik01NTAgMTI5NHE3MiAwIDExMSAtNTV0MzkgLTEzOXYtMTA2bDMzOSAtMTMxcTIxIC02IDQxIC0xOS41dDIwIC0yOC41di0zNDJxMCAtNyAtODEgLTkwdC05NCAtODNoLTUyNXEtMTcgMCAtMzUuNSAxNHQtMjguNSAyOGwtOSAxNGwtMjMwIDM2M3EtMTYgMzEgNiA1M2wxMTIgMTEwcTEzIDEzIDMyIDEzLjV0MzQgLTExLjVsMTIxIC04NHYzMDJxMCA4NCAzOCAxMzh0MTEwIDU0ek02MDAgOTcydjIwM3EwIDIxIC0yNSAzMC41dC01MCAwLjUgdC0yNSAtMzF2LTQ1NnYtN3YtNnYtNS41dC0wLjUgLTZ0LTEuNSAtNXQtMiAtNXQtMi41IC00dC00IC00dC00LjUgLTIuNXEtMjUgLTEyIC00NyA1bC0xODMgMTQ2bC04MyAtODZsMjM2IC0zMzloNTAzbDg5IDEwMHYyOTNsLTMzOSAxMzFxLTIxIDYgLTQxIDE5LjV0LTIwIDI4LjV6TTQ1MCAyMDBoNTAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0xMDBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTUwMCBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djEwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTEzMDsiIGQ9Ik0zNTAgMTEwMGg1MDBxMjEgMCAzNS41IDE0LjV0MTQuNSAzNS41djEwMHEwIDIxIC0xNC41IDM1LjV0LTM1LjUgMTQuNWgtNTAwcS0yMSAwIC0zNS41IC0xNC41dC0xNC41IC0zNS41di0xMDBxMCAtMjEgMTQuNSAtMzUuNXQzNS41IC0xNC41ek02MDAgMzA2di0xMDZxMCAtODQgLTM5IC0xMzl0LTExMSAtNTV0LTExMCA1NHQtMzggMTM4djMwMmwtMTIxIC04NHEtMTUgLTEyIC0zNCAtMTEuNXQtMzIgMTMuNWwtMTEyIDExMCBxLTIyIDIyIC02IDUzbDIzMCAzNjNxMSAyIDMuNSA2dDEwLjUgMTMuNXQxNi41IDE3dDIwIDEzLjV0MjIuNSA2aDUyNXExMyAwIDk0IC04M3Q4MSAtOTB2LTM0MnEwIC0xNSAtMjAgLTI4LjV0LTQxIC0xOS41ek0zMDggOTAwbC0yMzYgLTMzOWw4MyAtODZsMTgzIDE0NnEyMiAxNyA0NyA1cTIgLTEgNC41IC0yLjV0NCAtNHQyLjUgLTR0MiAtNXQxLjUgLTV0MC41IC02di01LjV2LTZ2LTd2LTQ1NnEwIC0yMiAyNSAtMzF0NTAgMC41dDI1IDMwLjUgdjIwM3EwIDE1IDIwIDI4LjV0NDEgMTkuNWwzMzkgMTMxdjI5M2wtODkgMTAwaC01MDN6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTEzMTsiIGQ9Ik02MDAgMTE3OHExMTggMCAyMjUgLTQ1LjV0MTg0LjUgLTEyM3QxMjMgLTE4NC41dDQ1LjUgLTIyNXQtNDUuNSAtMjI1dC0xMjMgLTE4NC41dC0xODQuNSAtMTIzdC0yMjUgLTQ1LjV0LTIyNSA0NS41dC0xODQuNSAxMjN0LTEyMyAxODQuNXQtNDUuNSAyMjV0NDUuNSAyMjV0MTIzIDE4NC41dDE4NC41IDEyM3QyMjUgNDUuNXpNOTE0IDYzMmwtMjc1IDIyM3EtMTYgMTMgLTI3LjUgOHQtMTEuNSAtMjZ2LTEzN2gtMjc1IHEtMTAgMCAtMTcuNSAtNy41dC03LjUgLTE3LjV2LTE1MHEwIC0xMCA3LjUgLTE3LjV0MTcuNSAtNy41aDI3NXYtMTM3cTAgLTIxIDExLjUgLTI2dDI3LjUgOGwyNzUgMjIzcTE2IDEzIDE2IDMydC0xNiAzMnoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTMyOyIgZD0iTTYwMCAxMTc4cTExOCAwIDIyNSAtNDUuNXQxODQuNSAtMTIzdDEyMyAtMTg0LjV0NDUuNSAtMjI1dC00NS41IC0yMjV0LTEyMyAtMTg0LjV0LTE4NC41IC0xMjN0LTIyNSAtNDUuNXQtMjI1IDQ1LjV0LTE4NC41IDEyM3QtMTIzIDE4NC41dC00NS41IDIyNXQ0NS41IDIyNXQxMjMgMTg0LjV0MTg0LjUgMTIzdDIyNSA0NS41ek01NjEgODU1bC0yNzUgLTIyM3EtMTYgLTEzIC0xNiAtMzJ0MTYgLTMybDI3NSAtMjIzcTE2IC0xMyAyNy41IC04IHQxMS41IDI2djEzN2gyNzVxMTAgMCAxNy41IDcuNXQ3LjUgMTcuNXYxNTBxMCAxMCAtNy41IDE3LjV0LTE3LjUgNy41aC0yNzV2MTM3cTAgMjEgLTExLjUgMjZ0LTI3LjUgLTh6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTEzMzsiIGQ9Ik02MDAgMTE3OHExMTggMCAyMjUgLTQ1LjV0MTg0LjUgLTEyM3QxMjMgLTE4NC41dDQ1LjUgLTIyNXQtNDUuNSAtMjI1dC0xMjMgLTE4NC41dC0xODQuNSAtMTIzdC0yMjUgLTQ1LjV0LTIyNSA0NS41dC0xODQuNSAxMjN0LTEyMyAxODQuNXQtNDUuNSAyMjV0NDUuNSAyMjV0MTIzIDE4NC41dDE4NC41IDEyM3QyMjUgNDUuNXpNODU1IDYzOWwtMjIzIDI3NXEtMTMgMTYgLTMyIDE2dC0zMiAtMTZsLTIyMyAtMjc1cS0xMyAtMTYgLTggLTI3LjUgdDI2IC0xMS41aDEzN3YtMjc1cTAgLTEwIDcuNSAtMTcuNXQxNy41IC03LjVoMTUwcTEwIDAgMTcuNSA3LjV0Ny41IDE3LjV2Mjc1aDEzN3EyMSAwIDI2IDExLjV0LTggMjcuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTM0OyIgZD0iTTYwMCAxMTc4cTExOCAwIDIyNSAtNDUuNXQxODQuNSAtMTIzdDEyMyAtMTg0LjV0NDUuNSAtMjI1dC00NS41IC0yMjV0LTEyMyAtMTg0LjV0LTE4NC41IC0xMjN0LTIyNSAtNDUuNXQtMjI1IDQ1LjV0LTE4NC41IDEyM3QtMTIzIDE4NC41dC00NS41IDIyNXQ0NS41IDIyNXQxMjMgMTg0LjV0MTg0LjUgMTIzdDIyNSA0NS41ek02NzUgOTAwaC0xNTBxLTEwIDAgLTE3LjUgLTcuNXQtNy41IC0xNy41di0yNzVoLTEzN3EtMjEgMCAtMjYgLTExLjUgdDggLTI3LjVsMjIzIC0yNzVxMTMgLTE2IDMyIC0xNnQzMiAxNmwyMjMgMjc1cTEzIDE2IDggMjcuNXQtMjYgMTEuNWgtMTM3djI3NXEwIDEwIC03LjUgMTcuNXQtMTcuNSA3LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTEzNTsiIGQ9Ik02MDAgMTE3NnExMTYgMCAyMjIuNSAtNDZ0MTg0IC0xMjMuNXQxMjMuNSAtMTg0dDQ2IC0yMjIuNXQtNDYgLTIyMi41dC0xMjMuNSAtMTg0dC0xODQgLTEyMy41dC0yMjIuNSAtNDZ0LTIyMi41IDQ2dC0xODQgMTIzLjV0LTEyMy41IDE4NHQtNDYgMjIyLjV0NDYgMjIyLjV0MTIzLjUgMTg0dDE4NCAxMjMuNXQyMjIuNSA0NnpNNjI3IDExMDFxLTE1IC0xMiAtMzYuNSAtMjAuNXQtMzUuNSAtMTJ0LTQzIC04dC0zOSAtNi41IHEtMTUgLTMgLTQ1LjUgMHQtNDUuNSAtMnEtMjAgLTcgLTUxLjUgLTI2LjV0LTM0LjUgLTM0LjVxLTMgLTExIDYuNSAtMjIuNXQ4LjUgLTE4LjVxLTMgLTM0IC0yNy41IC05MXQtMjkuNSAtNzlxLTkgLTM0IDUgLTkzdDggLTg3cTAgLTkgMTcgLTQ0LjV0MTYgLTU5LjVxMTIgMCAyMyAtNXQyMy41IC0xNXQxOS41IC0xNHExNiAtOCAzMyAtMTV0NDAuNSAtMTV0MzQuNSAtMTJxMjEgLTkgNTIuNSAtMzJ0NjAgLTM4dDU3LjUgLTExIHE3IC0xNSAtMyAtMzR0LTIyLjUgLTQwdC05LjUgLTM4cTEzIC0yMSAyMyAtMzQuNXQyNy41IC0yNy41dDM2LjUgLTE4cTAgLTcgLTMuNSAtMTZ0LTMuNSAtMTR0NSAtMTdxMTA0IC0yIDIyMSAxMTJxMzAgMjkgNDYuNSA0N3QzNC41IDQ5dDIxIDYzcS0xMyA4IC0zNyA4LjV0LTM2IDcuNXEtMTUgNyAtNDkuNSAxNXQtNTEuNSAxOXEtMTggMCAtNDEgLTAuNXQtNDMgLTEuNXQtNDIgLTYuNXQtMzggLTE2LjVxLTUxIC0zNSAtNjYgLTEyIHEtNCAxIC0zLjUgMjUuNXQwLjUgMjUuNXEtNiAxMyAtMjYuNSAxNy41dC0yNC41IDYuNXExIDE1IC0wLjUgMzAuNXQtNyAyOHQtMTguNSAxMS41dC0zMSAtMjFxLTIzIC0yNSAtNDIgNHEtMTkgMjggLTggNThxNiAxNiAyMiAyMnE2IC0xIDI2IC0xLjV0MzMuNSAtNHQxOS41IC0xMy41cTcgLTEyIDE4IC0yNHQyMS41IC0yMC41dDIwIC0xNXQxNS41IC0xMC41bDUgLTNxMiAxMiA3LjUgMzAuNXQ4IDM0LjV0LTAuNSAzMnEtMyAxOCAzLjUgMjkgdDE4IDIyLjV0MTUuNSAyNC41cTYgMTQgMTAuNSAzNXQ4IDMxdDE1LjUgMjIuNXQzNCAyMi41cS02IDE4IDEwIDM2cTggMCAyNCAtMS41dDI0LjUgLTEuNXQyMCA0LjV0MjAuNSAxNS41cS0xMCAyMyAtMzEgNDIuNXQtMzcuNSAyOS41dC00OSAyN3QtNDMuNSAyM3EwIDEgMiA4dDMgMTEuNXQxLjUgMTAuNXQtMSA5LjV0LTQuNSA0LjVxMzEgLTEzIDU4LjUgLTE0LjV0MzguNSAyLjVsMTIgNXE1IDI4IC05LjUgNDZ0LTM2LjUgMjR0LTUwIDE1IHQtNDEgMjBxLTE4IC00IC0zNyAwek02MTMgOTk0cTAgLTE3IDggLTQydDE3IC00NXQ5IC0yM3EtOCAxIC0zOS41IDUuNXQtNTIuNSAxMHQtMzcgMTYuNXEzIDExIDE2IDI5LjV0MTYgMjUuNXExMCAtMTAgMTkgLTEwdDE0IDZ0MTMuNSAxNC41dDE2LjUgMTIuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTM2OyIgZD0iTTc1NiAxMTU3cTE2NCA5MiAzMDYgLTlsLTI1OSAtMTM4bDE0NSAtMjMybDI1MSAxMjZxNiAtODkgLTM0IC0xNTYuNXQtMTE3IC0xMTAuNXEtNjAgLTM0IC0xMjcgLTM5LjV0LTEyNiAxNi41bC01OTYgLTU5NnEtMTUgLTE2IC0zNi41IC0xNnQtMzYuNSAxNmwtMTExIDExMHEtMTUgMTUgLTE1IDM2LjV0MTUgMzcuNWw2MDAgNTk5cS0zNCAxMDEgNS41IDIwMS41dDEzNS41IDE1NC41eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxMzc7IiBob3Jpei1hZHYteD0iMTIyMCIgZD0iTTEwMCAxMTk2aDEwMDBxNDEgMCA3MC41IC0yOS41dDI5LjUgLTcwLjV2LTEwMHEwIC00MSAtMjkuNSAtNzAuNXQtNzAuNSAtMjkuNWgtMTAwMHEtNDEgMCAtNzAuNSAyOS41dC0yOS41IDcwLjV2MTAwcTAgNDEgMjkuNSA3MC41dDcwLjUgMjkuNXpNMTEwMCAxMDk2aC0yMDB2LTEwMGgyMDB2MTAwek0xMDAgNzk2aDEwMDBxNDEgMCA3MC41IC0yOS41dDI5LjUgLTcwLjV2LTEwMHEwIC00MSAtMjkuNSAtNzAuNXQtNzAuNSAtMjkuNWgtMTAwMCBxLTQxIDAgLTcwLjUgMjkuNXQtMjkuNSA3MC41djEwMHEwIDQxIDI5LjUgNzAuNXQ3MC41IDI5LjV6TTExMDAgNjk2aC01MDB2LTEwMGg1MDB2MTAwek0xMDAgMzk2aDEwMDBxNDEgMCA3MC41IC0yOS41dDI5LjUgLTcwLjV2LTEwMHEwIC00MSAtMjkuNSAtNzAuNXQtNzAuNSAtMjkuNWgtMTAwMHEtNDEgMCAtNzAuNSAyOS41dC0yOS41IDcwLjV2MTAwcTAgNDEgMjkuNSA3MC41dDcwLjUgMjkuNXpNMTEwMCAyOTZoLTMwMHYtMTAwaDMwMHYxMDB6ICIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxMzg7IiBkPSJNMTUwIDEyMDBoOTAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41dC0xNC41IC0zNS41dC0zNS41IC0xNC41aC05MDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41dDE0LjUgMzUuNXQzNS41IDE0LjV6TTcwMCA1MDB2LTMwMGwtMjAwIC0yMDB2NTAwbC0zNTAgNTAwaDkwMHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTM5OyIgZD0iTTUwMCAxMjAwaDIwMHE0MSAwIDcwLjUgLTI5LjV0MjkuNSAtNzAuNXYtMTAwaDMwMHE0MSAwIDcwLjUgLTI5LjV0MjkuNSAtNzAuNXYtNDAwaC01MDB2MTAwaC0yMDB2LTEwMGgtNTAwdjQwMHEwIDQxIDI5LjUgNzAuNXQ3MC41IDI5LjVoMzAwdjEwMHEwIDQxIDI5LjUgNzAuNXQ3MC41IDI5LjV6TTUwMCAxMTAwdi0xMDBoMjAwdjEwMGgtMjAwek0xMjAwIDQwMHYtMjAwcTAgLTQxIC0yOS41IC03MC41dC03MC41IC0yOS41aC0xMDAwIHEtNDEgMCAtNzAuNSAyOS41dC0yOS41IDcwLjV2MjAwaDEyMDB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTE0MDsiIGQ9Ik01MCAxMjAwaDMwMHEyMSAwIDI1IC0xMC41dC0xMCAtMjQuNWwtOTQgLTk0bDE5OSAtMTk5cTcgLTggNyAtMTh0LTcgLTE4bC0xMDYgLTEwNnEtOCAtNyAtMTggLTd0LTE4IDdsLTE5OSAxOTlsLTk0IC05NHEtMTQgLTE0IC0yNC41IC0xMHQtMTAuNSAyNXYzMDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek04NTAgMTIwMGgzMDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTMwMHEwIC0yMSAtMTAuNSAtMjV0LTI0LjUgMTBsLTk0IDk0IGwtMTk5IC0xOTlxLTggLTcgLTE4IC03dC0xOCA3bC0xMDYgMTA2cS03IDggLTcgMTh0NyAxOGwxOTkgMTk5bC05NCA5NHEtMTQgMTQgLTEwIDI0LjV0MjUgMTAuNXpNMzY0IDQ3MGwxMDYgLTEwNnE3IC04IDcgLTE4dC03IC0xOGwtMTk5IC0xOTlsOTQgLTk0cTE0IC0xNCAxMCAtMjQuNXQtMjUgLTEwLjVoLTMwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MzAwcTAgMjEgMTAuNSAyNXQyNC41IC0xMGw5NCAtOTRsMTk5IDE5OSBxOCA3IDE4IDd0MTggLTd6TTEwNzEgMjcxbDk0IDk0cTE0IDE0IDI0LjUgMTB0MTAuNSAtMjV2LTMwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtMzAwcS0yMSAwIC0yNSAxMC41dDEwIDI0LjVsOTQgOTRsLTE5OSAxOTlxLTcgOCAtNyAxOHQ3IDE4bDEwNiAxMDZxOCA3IDE4IDd0MTggLTd6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTE0MTsiIGQ9Ik01OTYgMTE5MnExMjEgMCAyMzEuNSAtNDcuNXQxOTAgLTEyN3QxMjcgLTE5MHQ0Ny41IC0yMzEuNXQtNDcuNSAtMjMxLjV0LTEyNyAtMTkwLjV0LTE5MCAtMTI3dC0yMzEuNSAtNDd0LTIzMS41IDQ3dC0xOTAuNSAxMjd0LTEyNyAxOTAuNXQtNDcgMjMxLjV0NDcgMjMxLjV0MTI3IDE5MHQxOTAuNSAxMjd0MjMxLjUgNDcuNXpNNTk2IDEwMTBxLTExMiAwIC0yMDcuNSAtNTUuNXQtMTUxIC0xNTF0LTU1LjUgLTIwNy41dDU1LjUgLTIwNy41IHQxNTEgLTE1MXQyMDcuNSAtNTUuNXQyMDcuNSA1NS41dDE1MSAxNTF0NTUuNSAyMDcuNXQtNTUuNSAyMDcuNXQtMTUxIDE1MXQtMjA3LjUgNTUuNXpNNDU0LjUgOTA1cTIyLjUgMCAzOC41IC0xNnQxNiAtMzguNXQtMTYgLTM5dC0zOC41IC0xNi41dC0zOC41IDE2LjV0LTE2IDM5dDE2IDM4LjV0MzguNSAxNnpNNzU0LjUgOTA1cTIyLjUgMCAzOC41IC0xNnQxNiAtMzguNXQtMTYgLTM5dC0zOCAtMTYuNXEtMTQgMCAtMjkgMTBsLTU1IC0xNDUgcTE3IC0yMyAxNyAtNTFxMCAtMzYgLTI1LjUgLTYxLjV0LTYxLjUgLTI1LjV0LTYxLjUgMjUuNXQtMjUuNSA2MS41cTAgMzIgMjAuNSA1Ni41dDUxLjUgMjkuNWwxMjIgMTI2bDEgMXEtOSAxNCAtOSAyOHEwIDIzIDE2IDM5dDM4LjUgMTZ6TTM0NS41IDcwOXEyMi41IDAgMzguNSAtMTZ0MTYgLTM4LjV0LTE2IC0zOC41dC0zOC41IC0xNnQtMzguNSAxNnQtMTYgMzguNXQxNiAzOC41dDM4LjUgMTZ6TTg1NC41IDcwOXEyMi41IDAgMzguNSAtMTYgdDE2IC0zOC41dC0xNiAtMzguNXQtMzguNSAtMTZ0LTM4LjUgMTZ0LTE2IDM4LjV0MTYgMzguNXQzOC41IDE2eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxNDI7IiBkPSJNNTQ2IDE3M2w0NjkgNDcwcTkxIDkxIDk5IDE5MnE3IDk4IC01MiAxNzUuNXQtMTU0IDk0LjVxLTIyIDQgLTQ3IDRxLTM0IDAgLTY2LjUgLTEwdC01Ni41IC0yM3QtNTUuNSAtMzh0LTQ4IC00MS41dC00OC41IC00Ny41cS0zNzYgLTM3NSAtMzkxIC0zOTBxLTMwIC0yNyAtNDUgLTQxLjV0LTM3LjUgLTQxdC0zMiAtNDYuNXQtMTYgLTQ3LjV0LTEuNSAtNTYuNXE5IC02MiA1My41IC05NXQ5OS41IC0zM3E3NCAwIDEyNSA1MWw1NDggNTQ4IHEzNiAzNiAyMCA3NXEtNyAxNiAtMjEuNSAyNnQtMzIuNSAxMHEtMjYgMCAtNTAgLTIzcS0xMyAtMTIgLTM5IC0zOGwtMzQxIC0zMzhxLTE1IC0xNSAtMzUuNSAtMTUuNXQtMzQuNSAxMy41dC0xNCAzNC41dDE0IDM0LjVxMzI3IDMzMyAzNjEgMzY3cTM1IDM1IDY3LjUgNTEuNXQ3OC41IDE2LjVxMTQgMCAyOSAtMXE0NCAtOCA3NC41IC0zNS41dDQzLjUgLTY4LjVxMTQgLTQ3IDIgLTk2LjV0LTQ3IC04NC41cS0xMiAtMTEgLTMyIC0zMiB0LTc5LjUgLTgxdC0xMTQuNSAtMTE1dC0xMjQuNSAtMTIzLjV0LTEyMyAtMTE5LjV0LTk2LjUgLTg5dC01NyAtNDVxLTU2IC0yNyAtMTIwIC0yN3EtNzAgMCAtMTI5IDMydC05MyA4OXEtNDggNzggLTM1IDE3M3Q4MSAxNjNsNTExIDUxMXE3MSA3MiAxMTEgOTZxOTEgNTUgMTk4IDU1cTgwIDAgMTUyIC0zM3E3OCAtMzYgMTI5LjUgLTEwM3Q2Ni41IC0xNTRxMTcgLTkzIC0xMSAtMTgzLjV0LTk0IC0xNTYuNWwtNDgyIC00NzYgcS0xNSAtMTUgLTM2IC0xNnQtMzcgMTR0LTE3LjUgMzR0MTQuNSAzNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTQzOyIgZD0iTTY0OSA5NDlxNDggNjggMTA5LjUgMTA0dDEyMS41IDM4LjV0MTE4LjUgLTIwdDEwMi41IC02NHQ3MSAtMTAwLjV0MjcgLTEyM3EwIC01NyAtMzMuNSAtMTE3LjV0LTk0IC0xMjQuNXQtMTI2LjUgLTEyNy41dC0xNTAgLTE1Mi41dC0xNDYgLTE3NHEtNjIgODUgLTE0NS41IDE3NHQtMTUwIDE1Mi41dC0xMjYuNSAxMjcuNXQtOTMuNSAxMjQuNXQtMzMuNSAxMTcuNXEwIDY0IDI4IDEyM3Q3MyAxMDAuNXQxMDQgNjR0MTE5IDIwIHQxMjAuNSAtMzguNXQxMDQuNSAtMTA0ek04OTYgOTcycS0zMyAwIC02NC41IC0xOXQtNTYuNSAtNDZ0LTQ3LjUgLTUzLjV0LTQzLjUgLTQ1LjV0LTM3LjUgLTE5dC0zNiAxOXQtNDAgNDUuNXQtNDMgNTMuNXQtNTQgNDZ0LTY1LjUgMTlxLTY3IDAgLTEyMi41IC01NS41dC01NS41IC0xMzIuNXEwIC0yMyAxMy41IC01MXQ0NiAtNjV0NTcuNSAtNjN0NzYgLTc1bDIyIC0yMnExNSAtMTQgNDQgLTQ0dDUwLjUgLTUxdDQ2IC00NHQ0MSAtMzV0MjMgLTEyIHQyMy41IDEydDQyLjUgMzZ0NDYgNDR0NTIuNSA1MnQ0NCA0M3E0IDQgMTIgMTNxNDMgNDEgNjMuNSA2MnQ1MiA1NXQ0NiA1NXQyNiA0NnQxMS41IDQ0cTAgNzkgLTUzIDEzMy41dC0xMjAgNTQuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTQ0OyIgZD0iTTc3Ni41IDEyMTRxOTMuNSAwIDE1OS41IC02NmwxNDEgLTE0MXE2NiAtNjYgNjYgLTE2MHEwIC00MiAtMjggLTk1LjV0LTYyIC04Ny41bC0yOSAtMjlxLTMxIDUzIC03NyA5OWwtMTggMThsOTUgOTVsLTI0NyAyNDhsLTM4OSAtMzg5bDIxMiAtMjEybC0xMDUgLTEwNmwtMTkgMThsLTE0MSAxNDFxLTY2IDY2IC02NiAxNTl0NjYgMTU5bDI4MyAyODNxNjUgNjYgMTU4LjUgNjZ6TTYwMCA3MDZsMTA1IDEwNXExMCAtOCAxOSAtMTdsMTQxIC0xNDEgcTY2IC02NiA2NiAtMTU5dC02NiAtMTU5bC0yODMgLTI4M3EtNjYgLTY2IC0xNTkgLTY2dC0xNTkgNjZsLTE0MSAxNDFxLTY2IDY2IC02NiAxNTkuNXQ2NiAxNTkuNWw1NSA1NXEyOSAtNTUgNzUgLTEwMmwxOCAtMTdsLTk1IC05NWwyNDcgLTI0OGwzODkgMzg5eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxNDU7IiBkPSJNNjAzIDEyMDBxODUgMCAxNjIgLTE1dDEyNyAtMzh0NzkgLTQ4dDI5IC00NnYtOTUzcTAgLTQxIC0yOS41IC03MC41dC03MC41IC0yOS41aC02MDBxLTQxIDAgLTcwLjUgMjkuNXQtMjkuNSA3MC41djk1M3EwIDIxIDMwIDQ2LjV0ODEgNDh0MTI5IDM3LjV0MTYzIDE1ek0zMDAgMTAwMHYtNzAwaDYwMHY3MDBoLTYwMHpNNjAwIDI1NHEtNDMgMCAtNzMuNSAtMzAuNXQtMzAuNSAtNzMuNXQzMC41IC03My41dDczLjUgLTMwLjV0NzMuNSAzMC41IHQzMC41IDczLjV0LTMwLjUgNzMuNXQtNzMuNSAzMC41eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxNDY7IiBkPSJNOTAyIDExODVsMjgzIC0yODJxMTUgLTE1IDE1IC0zNnQtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNXQtMzUgMTVsLTM2IDM1bC0yNzkgLTI2N3YtMzAwbC0yMTIgMjEwbC0zMDggLTMwN2wtMjgwIC0yMDNsMjAzIDI4MGwzMDcgMzA4bC0yMTAgMjEyaDMwMGwyNjcgMjc5bC0zNSAzNnEtMTUgMTQgLTE1IDM1dDE0LjUgMzUuNXQzNS41IDE0LjV0MzUgLTE1eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxNDg7IiBkPSJNNzAwIDEyNDh2LTc4cTM4IC01IDcyLjUgLTE0LjV0NzUuNSAtMzEuNXQ3MSAtNTMuNXQ1MiAtODR0MjQgLTExOC41aC0xNTlxLTQgMzYgLTEwLjUgNTl0LTIxIDQ1dC00MCAzNS41dC02NC41IDIwLjV2LTMwN2w2NCAtMTNxMzQgLTcgNjQgLTE2LjV0NzAgLTMydDY3LjUgLTUyLjV0NDcuNSAtODB0MjAgLTExMnEwIC0xMzkgLTg5IC0yMjR0LTI0NCAtOTd2LTc3aC0xMDB2NzlxLTE1MCAxNiAtMjM3IDEwM3EtNDAgNDAgLTUyLjUgOTMuNSB0LTE1LjUgMTM5LjVoMTM5cTUgLTc3IDQ4LjUgLTEyNnQxMTcuNSAtNjV2MzM1bC0yNyA4cS00NiAxNCAtNzkgMjYuNXQtNzIgMzZ0LTYzIDUydC00MCA3Mi41dC0xNiA5OHEwIDcwIDI1IDEyNnQ2Ny41IDkydDk0LjUgNTd0MTEwIDI3djc3aDEwMHpNNjAwIDc1NHYyNzRxLTI5IC00IC01MCAtMTF0LTQyIC0yMS41dC0zMS41IC00MS41dC0xMC41IC02NXEwIC0yOSA3IC01MC41dDE2LjUgLTM0dDI4LjUgLTIyLjV0MzEuNSAtMTR0MzcuNSAtMTAgcTkgLTMgMTMgLTR6TTcwMCA1NDd2LTMxMHEyMiAyIDQyLjUgNi41dDQ1IDE1LjV0NDEuNSAyN3QyOSA0MnQxMiA1OS41dC0xMi41IDU5LjV0LTM4IDQ0LjV0LTUzIDMxdC02Ni41IDI0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTE0OTsiIGQ9Ik01NjEgMTE5N3E4NCAwIDE2MC41IC00MHQxMjMuNSAtMTA5LjV0NDcgLTE0Ny41aC0xNTNxMCA0MCAtMTkuNSA3MS41dC00OS41IDQ4LjV0LTU5LjUgMjZ0LTU1LjUgOXEtMzcgMCAtNzkgLTE0LjV0LTYyIC0zNS41cS00MSAtNDQgLTQxIC0xMDFxMCAtMjYgMTMuNSAtNjN0MjYuNSAtNjF0MzcgLTY2cTYgLTkgOSAtMTRoMjQxdi0xMDBoLTE5N3E4IC01MCAtMi41IC0xMTV0LTMxLjUgLTk1cS00NSAtNjIgLTk5IC0xMTIgcTM0IDEwIDgzIDE3LjV0NzEgNy41cTMyIDEgMTAyIC0xNnQxMDQgLTE3cTgzIDAgMTM2IDMwbDUwIC0xNDdxLTMxIC0xOSAtNTggLTMwLjV0LTU1IC0xNS41dC00MiAtNC41dC00NiAtMC41cS0yMyAwIC03NiAxN3QtMTExIDMyLjV0LTk2IDExLjVxLTM5IC0zIC04MiAtMTZ0LTY3IC0yNWwtMjMgLTExbC01NSAxNDVxNCAzIDE2IDExdDE1LjUgMTAuNXQxMyA5dDE1LjUgMTJ0MTQuNSAxNHQxNy41IDE4LjVxNDggNTUgNTQgMTI2LjUgdC0zMCAxNDIuNWgtMjIxdjEwMGgxNjZxLTIzIDQ3IC00NCAxMDRxLTcgMjAgLTEyIDQxLjV0LTYgNTUuNXQ2IDY2LjV0MjkuNSA3MC41dDU4LjUgNzFxOTcgODggMjYzIDg4eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxNTA7IiBkPSJNNDAwIDMwMGgxNTBxMjEgMCAyNSAtMTF0LTEwIC0yNWwtMjMwIC0yNTBxLTE0IC0xNSAtMzUgLTE1dC0zNSAxNWwtMjMwIDI1MHEtMTQgMTQgLTEwIDI1dDI1IDExaDE1MHY5MDBoMjAwdi05MDB6TTkzNSAxMTg0bDIzMCAtMjQ5cTE0IC0xNCAxMCAtMjQuNXQtMjUgLTEwLjVoLTE1MHYtOTAwaC0yMDB2OTAwaC0xNTBxLTIxIDAgLTI1IDEwLjV0MTAgMjQuNWwyMzAgMjQ5cTE0IDE1IDM1IDE1dDM1IC0xNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTUxOyIgZD0iTTEwMDAgNzAwaC0xMDB2MTAwaC0xMDB2LTEwMGgtMTAwdjUwMGgzMDB2LTUwMHpNNDAwIDMwMGgxNTBxMjEgMCAyNSAtMTF0LTEwIC0yNWwtMjMwIC0yNTBxLTE0IC0xNSAtMzUgLTE1dC0zNSAxNWwtMjMwIDI1MHEtMTQgMTQgLTEwIDI1dDI1IDExaDE1MHY5MDBoMjAwdi05MDB6TTgwMSAxMTAwdi0yMDBoMTAwdjIwMGgtMTAwek0xMDAwIDM1MGwtMjAwIC0yNTBoMjAwdi0xMDBoLTMwMHYxNTBsMjAwIDI1MGgtMjAwdjEwMGgzMDB2LTE1MHogIiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTE1MjsiIGQ9Ik00MDAgMzAwaDE1MHEyMSAwIDI1IC0xMXQtMTAgLTI1bC0yMzAgLTI1MHEtMTQgLTE1IC0zNSAtMTV0LTM1IDE1bC0yMzAgMjUwcS0xNCAxNCAtMTAgMjV0MjUgMTFoMTUwdjkwMGgyMDB2LTkwMHpNMTAwMCAxMDUwbC0yMDAgLTI1MGgyMDB2LTEwMGgtMzAwdjE1MGwyMDAgMjUwaC0yMDB2MTAwaDMwMHYtMTUwek0xMDAwIDBoLTEwMHYxMDBoLTEwMHYtMTAwaC0xMDB2NTAwaDMwMHYtNTAwek04MDEgNDAwdi0yMDBoMTAwdjIwMGgtMTAweiAiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTUzOyIgZD0iTTQwMCAzMDBoMTUwcTIxIDAgMjUgLTExdC0xMCAtMjVsLTIzMCAtMjUwcS0xNCAtMTUgLTM1IC0xNXQtMzUgMTVsLTIzMCAyNTBxLTE0IDE0IC0xMCAyNXQyNSAxMWgxNTB2OTAwaDIwMHYtOTAwek0xMDAwIDcwMGgtMTAwdjQwMGgtMTAwdjEwMGgyMDB2LTUwMHpNMTEwMCAwaC0xMDB2MTAwaC0yMDB2NDAwaDMwMHYtNTAwek05MDEgNDAwdi0yMDBoMTAwdjIwMGgtMTAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxNTQ7IiBkPSJNNDAwIDMwMGgxNTBxMjEgMCAyNSAtMTF0LTEwIC0yNWwtMjMwIC0yNTBxLTE0IC0xNSAtMzUgLTE1dC0zNSAxNWwtMjMwIDI1MHEtMTQgMTQgLTEwIDI1dDI1IDExaDE1MHY5MDBoMjAwdi05MDB6TTExMDAgNzAwaC0xMDB2MTAwaC0yMDB2NDAwaDMwMHYtNTAwek05MDEgMTEwMHYtMjAwaDEwMHYyMDBoLTEwMHpNMTAwMCAwaC0xMDB2NDAwaC0xMDB2MTAwaDIwMHYtNTAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxNTU7IiBkPSJNNDAwIDMwMGgxNTBxMjEgMCAyNSAtMTF0LTEwIC0yNWwtMjMwIC0yNTBxLTE0IC0xNSAtMzUgLTE1dC0zNSAxNWwtMjMwIDI1MHEtMTQgMTQgLTEwIDI1dDI1IDExaDE1MHY5MDBoMjAwdi05MDB6TTkwMCAxMDAwaC0yMDB2MjAwaDIwMHYtMjAwek0xMDAwIDcwMGgtMzAwdjIwMGgzMDB2LTIwMHpNMTEwMCA0MDBoLTQwMHYyMDBoNDAwdi0yMDB6TTEyMDAgMTAwaC01MDB2MjAwaDUwMHYtMjAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxNTY7IiBkPSJNNDAwIDMwMGgxNTBxMjEgMCAyNSAtMTF0LTEwIC0yNWwtMjMwIC0yNTBxLTE0IC0xNSAtMzUgLTE1dC0zNSAxNWwtMjMwIDI1MHEtMTQgMTQgLTEwIDI1dDI1IDExaDE1MHY5MDBoMjAwdi05MDB6TTEyMDAgMTAwMGgtNTAwdjIwMGg1MDB2LTIwMHpNMTEwMCA3MDBoLTQwMHYyMDBoNDAwdi0yMDB6TTEwMDAgNDAwaC0zMDB2MjAwaDMwMHYtMjAwek05MDAgMTAwaC0yMDB2MjAwaDIwMHYtMjAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxNTc7IiBkPSJNMzUwIDExMDBoNDAwcTE2MiAwIDI1NiAtOTMuNXQ5NCAtMjU2LjV2LTQwMHEwIC0xNjUgLTkzLjUgLTI1Ny41dC0yNTYuNSAtOTIuNWgtNDAwcS0xNjUgMCAtMjU3LjUgOTIuNXQtOTIuNSAyNTcuNXY0MDBxMCAxNjUgOTIuNSAyNTcuNXQyNTcuNSA5Mi41ek04MDAgOTAwaC01MDBxLTQxIDAgLTcwLjUgLTI5LjV0LTI5LjUgLTcwLjV2LTUwMHEwIC00MSAyOS41IC03MC41dDcwLjUgLTI5LjVoNTAwcTQxIDAgNzAuNSAyOS41dDI5LjUgNzAuNSB2NTAwcTAgNDEgLTI5LjUgNzAuNXQtNzAuNSAyOS41eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxNTg7IiBkPSJNMzUwIDExMDBoNDAwcTE2NSAwIDI1Ny41IC05Mi41dDkyLjUgLTI1Ny41di00MDBxMCAtMTY1IC05Mi41IC0yNTcuNXQtMjU3LjUgLTkyLjVoLTQwMHEtMTYzIDAgLTI1Ni41IDkyLjV0LTkzLjUgMjU3LjV2NDAwcTAgMTYzIDk0IDI1Ni41dDI1NiA5My41ek04MDAgOTAwaC01MDBxLTQxIDAgLTcwLjUgLTI5LjV0LTI5LjUgLTcwLjV2LTUwMHEwIC00MSAyOS41IC03MC41dDcwLjUgLTI5LjVoNTAwcTQxIDAgNzAuNSAyOS41dDI5LjUgNzAuNSB2NTAwcTAgNDEgLTI5LjUgNzAuNXQtNzAuNSAyOS41ek00NDAgNzcwbDI1MyAtMTkwcTE3IC0xMiAxNyAtMzB0LTE3IC0zMGwtMjUzIC0xOTBxLTE2IC0xMiAtMjggLTYuNXQtMTIgMjYuNXY0MDBxMCAyMSAxMiAyNi41dDI4IC02LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTE1OTsiIGQ9Ik0zNTAgMTEwMGg0MDBxMTYzIDAgMjU2LjUgLTk0dDkzLjUgLTI1NnYtNDAwcTAgLTE2NSAtOTIuNSAtMjU3LjV0LTI1Ny41IC05Mi41aC00MDBxLTE2NSAwIC0yNTcuNSA5Mi41dC05Mi41IDI1Ny41djQwMHEwIDE2MyA5Mi41IDI1Ni41dDI1Ny41IDkzLjV6TTgwMCA5MDBoLTUwMHEtNDEgMCAtNzAuNSAtMjkuNXQtMjkuNSAtNzAuNXYtNTAwcTAgLTQxIDI5LjUgLTcwLjV0NzAuNSAtMjkuNWg1MDBxNDEgMCA3MC41IDI5LjV0MjkuNSA3MC41IHY1MDBxMCA0MSAtMjkuNSA3MC41dC03MC41IDI5LjV6TTM1MCA3MDBoNDAwcTIxIDAgMjYuNSAtMTJ0LTYuNSAtMjhsLTE5MCAtMjUzcS0xMiAtMTcgLTMwIC0xN3QtMzAgMTdsLTE5MCAyNTNxLTEyIDE2IC02LjUgMjh0MjYuNSAxMnoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTYwOyIgZD0iTTM1MCAxMTAwaDQwMHExNjUgMCAyNTcuNSAtOTIuNXQ5Mi41IC0yNTcuNXYtNDAwcTAgLTE2MyAtOTIuNSAtMjU2LjV0LTI1Ny41IC05My41aC00MDBxLTE2MyAwIC0yNTYuNSA5NHQtOTMuNSAyNTZ2NDAwcTAgMTY1IDkyLjUgMjU3LjV0MjU3LjUgOTIuNXpNODAwIDkwMGgtNTAwcS00MSAwIC03MC41IC0yOS41dC0yOS41IC03MC41di01MDBxMCAtNDEgMjkuNSAtNzAuNXQ3MC41IC0yOS41aDUwMHE0MSAwIDcwLjUgMjkuNXQyOS41IDcwLjUgdjUwMHEwIDQxIC0yOS41IDcwLjV0LTcwLjUgMjkuNXpNNTgwIDY5M2wxOTAgLTI1M3ExMiAtMTYgNi41IC0yOHQtMjYuNSAtMTJoLTQwMHEtMjEgMCAtMjYuNSAxMnQ2LjUgMjhsMTkwIDI1M3ExMiAxNyAzMCAxN3QzMCAtMTd6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTE2MTsiIGQ9Ik01NTAgMTEwMGg0MDBxMTY1IDAgMjU3LjUgLTkyLjV0OTIuNSAtMjU3LjV2LTQwMHEwIC0xNjUgLTkyLjUgLTI1Ny41dC0yNTcuNSAtOTIuNWgtNDAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYxMDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41aDQ1MHE0MSAwIDcwLjUgMjkuNXQyOS41IDcwLjV2NTAwcTAgNDEgLTI5LjUgNzAuNXQtNzAuNSAyOS41aC00NTBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djEwMCBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek0zMzggODY3bDMyNCAtMjg0cTE2IC0xNCAxNiAtMzN0LTE2IC0zM2wtMzI0IC0yODRxLTE2IC0xNCAtMjcgLTl0LTExIDI2djE1MGgtMjUwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYyMDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41aDI1MHYxNTBxMCAyMSAxMSAyNnQyNyAtOXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTYyOyIgZD0iTTc5MyAxMTgybDkgLTlxOCAtMTAgNSAtMjdxLTMgLTExIC03OSAtMjI1LjV0LTc4IC0yMjEuNWwzMDAgMXEyNCAwIDMyLjUgLTE3LjV0LTUuNSAtMzUuNXEtMSAwIC0xMzMuNSAtMTU1dC0yNjcgLTMxMi41dC0xMzguNSAtMTYyLjVxLTEyIC0xNSAtMjYgLTE1aC05bC05IDhxLTkgMTEgLTQgMzJxMiA5IDQyIDEyMy41dDc5IDIyNC41bDM5IDExMGgtMzAycS0yMyAwIC0zMSAxOXEtMTAgMjEgNiA0MXE3NSA4NiAyMDkuNSAyMzcuNSB0MjI4IDI1N3Q5OC41IDExMS41cTkgMTYgMjUgMTZoOXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTYzOyIgZD0iTTM1MCAxMTAwaDQwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMTAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC00NTBxLTQxIDAgLTcwLjUgLTI5LjV0LTI5LjUgLTcwLjV2LTUwMHEwIC00MSAyOS41IC03MC41dDcwLjUgLTI5LjVoNDUwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0xMDBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTQwMHEtMTY1IDAgLTI1Ny41IDkyLjV0LTkyLjUgMjU3LjV2NDAwIHEwIDE2NSA5Mi41IDI1Ny41dDI1Ny41IDkyLjV6TTkzOCA4NjdsMzI0IC0yODRxMTYgLTE0IDE2IC0zM3QtMTYgLTMzbC0zMjQgLTI4NHEtMTYgLTE0IC0yNyAtOXQtMTEgMjZ2MTUwaC0yNTBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djIwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjVoMjUwdjE1MHEwIDIxIDExIDI2dDI3IC05eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxNjQ7IiBkPSJNNzUwIDEyMDBoNDAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di00MDBxMCAtMjEgLTEwLjUgLTI1dC0yNC41IDEwbC0xMDkgMTA5bC0zMTIgLTMxMnEtMTUgLTE1IC0zNS41IC0xNXQtMzUuNSAxNWwtMTQxIDE0MXEtMTUgMTUgLTE1IDM1LjV0MTUgMzUuNWwzMTIgMzEybC0xMDkgMTA5cS0xNCAxNCAtMTAgMjQuNXQyNSAxMC41ek00NTYgOTAwaC0xNTZxLTQxIDAgLTcwLjUgLTI5LjV0LTI5LjUgLTcwLjV2LTUwMCBxMCAtNDEgMjkuNSAtNzAuNXQ3MC41IC0yOS41aDUwMHE0MSAwIDcwLjUgMjkuNXQyOS41IDcwLjV2MTQ4bDIwMCAyMDB2LTI5OHEwIC0xNjUgLTkzLjUgLTI1Ny41dC0yNTYuNSAtOTIuNWgtNDAwcS0xNjUgMCAtMjU3LjUgOTIuNXQtOTIuNSAyNTcuNXY0MDBxMCAxNjUgOTIuNSAyNTcuNXQyNTcuNSA5Mi41aDMwMHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTY1OyIgZD0iTTYwMCAxMTg2cTExOSAwIDIyNy41IC00Ni41dDE4NyAtMTI1dDEyNSAtMTg3dDQ2LjUgLTIyNy41dC00Ni41IC0yMjcuNXQtMTI1IC0xODd0LTE4NyAtMTI1dC0yMjcuNSAtNDYuNXQtMjI3LjUgNDYuNXQtMTg3IDEyNXQtMTI1IDE4N3QtNDYuNSAyMjcuNXQ0Ni41IDIyNy41dDEyNSAxODd0MTg3IDEyNXQyMjcuNSA0Ni41ek02MDAgMTAyMnEtMTE1IDAgLTIxMiAtNTYuNXQtMTUzLjUgLTE1My41dC01Ni41IC0yMTJ0NTYuNSAtMjEyIHQxNTMuNSAtMTUzLjV0MjEyIC01Ni41dDIxMiA1Ni41dDE1My41IDE1My41dDU2LjUgMjEydC01Ni41IDIxMnQtMTUzLjUgMTUzLjV0LTIxMiA1Ni41ek02MDAgNzk0cTgwIDAgMTM3IC01N3Q1NyAtMTM3dC01NyAtMTM3dC0xMzcgLTU3dC0xMzcgNTd0LTU3IDEzN3Q1NyAxMzd0MTM3IDU3eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxNjY7IiBkPSJNNDUwIDEyMDBoMjAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0zNTBoMjQ1cTIwIDAgMjUgLTExdC05IC0yNmwtMzgzIC00MjZxLTE0IC0xNSAtMzMuNSAtMTV0LTMyLjUgMTVsLTM3OSA0MjZxLTEzIDE1IC04LjUgMjZ0MjUuNSAxMWgyNTB2MzUwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNNTAgMzAwaDEwMDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTI1MGgtMTEwMHYyNTBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41eiBNOTAwIDIwMHYtNTBoMTAwdjUwaC0xMDB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTE2NzsiIGQ9Ik01ODMgMTE4MmwzNzggLTQzNXExNCAtMTUgOSAtMzF0LTI2IC0xNmgtMjQ0di0yNTBxMCAtMjAgLTE3IC0zNXQtMzkgLTE1aC0yMDBxLTIwIDAgLTMyIDE0LjV0LTEyIDM1LjV2MjUwaC0yNTBxLTIwIDAgLTI1LjUgMTYuNXQ4LjUgMzEuNWwzODMgNDMxcTE0IDE2IDMzLjUgMTd0MzMuNSAtMTR6TTUwIDMwMGgxMDAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0yNTBoLTExMDB2MjUwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXogTTkwMCAyMDB2LTUwaDEwMHY1MGgtMTAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxNjg7IiBkPSJNMzk2IDcyM2wzNjkgMzY5cTcgNyAxNy41IDd0MTcuNSAtN2wxMzkgLTEzOXE3IC04IDcgLTE4LjV0LTcgLTE3LjVsLTUyNSAtNTI1cS03IC04IC0xNy41IC04dC0xNy41IDhsLTI5MiAyOTFxLTcgOCAtNyAxOHQ3IDE4bDEzOSAxMzlxOCA3IDE4LjUgN3QxNy41IC03ek01MCAzMDBoMTAwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMjUwaC0xMTAwdjI1MHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTkwMCAyMDB2LTUwaDEwMHY1MCBoLTEwMHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTY5OyIgZD0iTTEzNSAxMDIzbDE0MiAxNDJxMTQgMTQgMzUgMTR0MzUgLTE0bDc3IC03N2wtMjEyIC0yMTJsLTc3IDc2cS0xNCAxNSAtMTQgMzZ0MTQgMzV6TTY1NSA4NTVsMjEwIDIxMHExNCAxNCAyNC41IDEwdDEwLjUgLTI1bC0yIC01OTlxLTEgLTIwIC0xNS41IC0zNXQtMzUuNSAtMTVsLTU5NyAtMXEtMjEgMCAtMjUgMTAuNXQxMCAyNC41bDIwOCAyMDhsLTE1NCAxNTVsMjEyIDIxMnpNNTAgMzAwaDEwMDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjUgdi0yNTBoLTExMDB2MjUwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNOTAwIDIwMHYtNTBoMTAwdjUwaC0xMDB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTE3MDsiIGQ9Ik0zNTAgMTIwMGw1OTkgLTJxMjAgLTEgMzUgLTE1LjV0MTUgLTM1LjVsMSAtNTk3cTAgLTIxIC0xMC41IC0yNXQtMjQuNSAxMGwtMjA4IDIwOGwtMTU1IC0xNTRsLTIxMiAyMTJsMTU1IDE1NGwtMjEwIDIxMHEtMTQgMTQgLTEwIDI0LjV0MjUgMTAuNXpNNTI0IDUxMmwtNzYgLTc3cS0xNSAtMTQgLTM2IC0xNHQtMzUgMTRsLTE0MiAxNDJxLTE0IDE0IC0xNCAzNXQxNCAzNWw3NyA3N3pNNTAgMzAwaDEwMDBxMjEgMCAzNS41IC0xNC41IHQxNC41IC0zNS41di0yNTBoLTExMDB2MjUwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNOTAwIDIwMHYtNTBoMTAwdjUwaC0xMDB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTE3MTsiIGQ9Ik0xMjAwIDEwM2wtNDgzIDI3NmwtMzE0IC0zOTl2NDIzaC0zOTlsMTE5NiA3OTZ2LTEwOTZ6TTQ4MyA0MjR2LTIzMGw2ODMgOTUzeiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxNzI7IiBkPSJNMTEwMCAxMDAwdi04NTBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTE1MHY0MDBoLTcwMHYtNDAwaC0xNTBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djEwMDBxMCAyMCAxNC41IDM1dDM1LjUgMTVoMjUwdi0zMDBoNTAwdjMwMGgxMDB6TTcwMCAxMDAwaC0xMDB2MjAwaDEwMHYtMjAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxNzM7IiBkPSJNMTEwMCAxMDAwbC0yIC0xNDlsLTI5OSAtMjk5bC05NSA5NXEtOSA5IC0yMS41IDl0LTIxLjUgLTlsLTE0OSAtMTQ3aC0zMTJ2LTQwMGgtMTUwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYxMDAwcTAgMjAgMTQuNSAzNXQzNS41IDE1aDI1MHYtMzAwaDUwMHYzMDBoMTAwek03MDAgMTAwMGgtMTAwdjIwMGgxMDB2LTIwMHpNMTEzMiA2MzhsMTA2IC0xMDZxNyAtNyA3IC0xNy41dC03IC0xNy41bC00MjAgLTQyMXEtOCAtNyAtMTggLTcgdC0xOCA3bC0yMDIgMjAzcS04IDcgLTggMTcuNXQ4IDE3LjVsMTA2IDEwNnE3IDggMTcuNSA4dDE3LjUgLThsNzkgLTc5bDI5NyAyOTdxNyA3IDE3LjUgN3QxNy41IC03eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxNzQ7IiBkPSJNMTEwMCAxMDAwdi0yNjlsLTEwMyAtMTAzbC0xMzQgMTM0cS0xNSAxNSAtMzMuNSAxNi41dC0zNC41IC0xMi41bC0yNjYgLTI2NmgtMzI5di00MDBoLTE1MHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MTAwMHEwIDIwIDE0LjUgMzV0MzUuNSAxNWgyNTB2LTMwMGg1MDB2MzAwaDEwMHpNNzAwIDEwMDBoLTEwMHYyMDBoMTAwdi0yMDB6TTEyMDIgNTcybDcwIC03MHExNSAtMTUgMTUgLTM1LjV0LTE1IC0zNS41bC0xMzEgLTEzMSBsMTMxIC0xMzFxMTUgLTE1IDE1IC0zNS41dC0xNSAtMzUuNWwtNzAgLTcwcS0xNSAtMTUgLTM1LjUgLTE1dC0zNS41IDE1bC0xMzEgMTMxbC0xMzEgLTEzMXEtMTUgLTE1IC0zNS41IC0xNXQtMzUuNSAxNWwtNzAgNzBxLTE1IDE1IC0xNSAzNS41dDE1IDM1LjVsMTMxIDEzMWwtMTMxIDEzMXEtMTUgMTUgLTE1IDM1LjV0MTUgMzUuNWw3MCA3MHExNSAxNSAzNS41IDE1dDM1LjUgLTE1bDEzMSAtMTMxbDEzMSAxMzFxMTUgMTUgMzUuNSAxNSB0MzUuNSAtMTV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTE3NTsiIGQ9Ik0xMTAwIDEwMDB2LTMwMGgtMzUwcS0yMSAwIC0zNS41IC0xNC41dC0xNC41IC0zNS41di0xNTBoLTUwMHYtNDAwaC0xNTBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djEwMDBxMCAyMCAxNC41IDM1dDM1LjUgMTVoMjUwdi0zMDBoNTAwdjMwMGgxMDB6TTcwMCAxMDAwaC0xMDB2MjAwaDEwMHYtMjAwek04NTAgNjAwaDEwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMjUwaDE1MHEyMSAwIDI1IC0xMC41dC0xMCAtMjQuNSBsLTIzMCAtMjMwcS0xNCAtMTQgLTM1IC0xNHQtMzUgMTRsLTIzMCAyMzBxLTE0IDE0IC0xMCAyNC41dDI1IDEwLjVoMTUwdjI1MHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTE3NjsiIGQ9Ik0xMTAwIDEwMDB2LTQwMGwtMTY1IDE2NXEtMTQgMTUgLTM1IDE1dC0zNSAtMTVsLTI2MyAtMjY1aC00MDJ2LTQwMGgtMTUwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYxMDAwcTAgMjAgMTQuNSAzNXQzNS41IDE1aDI1MHYtMzAwaDUwMHYzMDBoMTAwek03MDAgMTAwMGgtMTAwdjIwMGgxMDB2LTIwMHpNOTM1IDU2NWwyMzAgLTIyOXExNCAtMTUgMTAgLTI1LjV0LTI1IC0xMC41aC0xNTB2LTI1MHEwIC0yMCAtMTQuNSAtMzUgdC0zNS41IC0xNWgtMTAwcS0yMSAwIC0zNS41IDE1dC0xNC41IDM1djI1MGgtMTUwcS0yMSAwIC0yNSAxMC41dDEwIDI1LjVsMjMwIDIyOXExNCAxNSAzNSAxNXQzNSAtMTV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTE3NzsiIGQ9Ik01MCAxMTAwaDExMDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTE1MGgtMTIwMHYxNTBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek0xMjAwIDgwMHYtNTUwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0xMTAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXY1NTBoMTIwMHpNMTAwIDUwMHYtMjAwaDQwMHYyMDBoLTQwMHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTc4OyIgZD0iTTkzNSAxMTY1bDI0OCAtMjMwcTE0IC0xNCAxNCAtMzV0LTE0IC0zNWwtMjQ4IC0yMzBxLTE0IC0xNCAtMjQuNSAtMTB0LTEwLjUgMjV2MTUwaC00MDB2MjAwaDQwMHYxNTBxMCAyMSAxMC41IDI1dDI0LjUgLTEwek0yMDAgODAwaC01MHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MTAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNWg1MHYtMjAwek00MDAgODAwaC0xMDB2MjAwaDEwMHYtMjAwek0xOCA0MzVsMjQ3IDIzMCBxMTQgMTQgMjQuNSAxMHQxMC41IC0yNXYtMTUwaDQwMHYtMjAwaC00MDB2LTE1MHEwIC0yMSAtMTAuNSAtMjV0LTI0LjUgMTBsLTI0NyAyMzBxLTE1IDE0IC0xNSAzNXQxNSAzNXpNOTAwIDMwMGgtMTAwdjIwMGgxMDB2LTIwMHpNMTAwMCA1MDBoNTFxMjAgMCAzNC41IC0xNC41dDE0LjUgLTM1LjV2LTEwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzQuNSAtMTQuNWgtNTF2MjAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxNzk7IiBkPSJNODYyIDEwNzNsMjc2IDExNnEyNSAxOCA0My41IDh0MTguNSAtNDF2LTExMDZxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTIwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2Mzk3cS00IDEgLTExIDV0LTI0IDE3LjV0LTMwIDI5dC0yNCA0MnQtMTEgNTYuNXYzNTlxMCAzMSAxOC41IDY1dDQzLjUgNTJ6TTU1MCAxMjAwcTIyIDAgMzQuNSAtMTIuNXQxNC41IC0yNC41bDEgLTEzdi00NTBxMCAtMjggLTEwLjUgLTU5LjUgdC0yNSAtNTZ0LTI5IC00NXQtMjUuNSAtMzEuNWwtMTAgLTExdi00NDdxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTIwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2NDQ3cS00IDQgLTExIDExLjV0LTI0IDMwLjV0LTMwIDQ2dC0yNCA1NXQtMTEgNjB2NDUwcTAgMiAwLjUgNS41dDQgMTJ0OC41IDE1dDE0LjUgMTJ0MjIuNSA1LjVxMjAgMCAzMi41IC0xMi41dDE0LjUgLTI0LjVsMyAtMTN2LTM1MGgxMDB2MzUwdjUuNXQyLjUgMTIgdDcgMTV0MTUgMTJ0MjUuNSA1LjVxMjMgMCAzNS41IC0xMi41dDEzLjUgLTI0LjVsMSAtMTN2LTM1MGgxMDB2MzUwcTAgMiAwLjUgNS41dDMgMTJ0NyAxNXQxNSAxMnQyNC41IDUuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTgwOyIgZD0iTTEyMDAgMTEwMHYtNTZxLTQgMCAtMTEgLTAuNXQtMjQgLTN0LTMwIC03LjV0LTI0IC0xNXQtMTEgLTI0di04ODhxMCAtMjIgMjUgLTM0LjV0NTAgLTEzLjVsMjUgLTJ2LTU2aC00MDB2NTZxNzUgMCA4Ny41IDYuNXQxMi41IDQzLjV2Mzk0aC01MDB2LTM5NHEwIC0zNyAxMi41IC00My41dDg3LjUgLTYuNXYtNTZoLTQwMHY1NnE0IDAgMTEgMC41dDI0IDN0MzAgNy41dDI0IDE1dDExIDI0djg4OHEwIDIyIC0yNSAzNC41dC01MCAxMy41IGwtMjUgMnY1Nmg0MDB2LTU2cS03NSAwIC04Ny41IC02LjV0LTEyLjUgLTQzLjV2LTM5NGg1MDB2Mzk0cTAgMzcgLTEyLjUgNDMuNXQtODcuNSA2LjV2NTZoNDAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxODE7IiBkPSJNNjc1IDEwMDBoMzc1cTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0xNTBoLTEwNWwtMjk1IC05OHY5OGwtMjAwIDIwMGgtNDAwbDEwMCAxMDBoMzc1ek0xMDAgOTAwaDMwMHE0MSAwIDcwLjUgLTI5LjV0MjkuNSAtNzAuNXYtNTAwcTAgLTQxIC0yOS41IC03MC41dC03MC41IC0yOS41aC0zMDBxLTQxIDAgLTcwLjUgMjkuNXQtMjkuNSA3MC41djUwMHEwIDQxIDI5LjUgNzAuNXQ3MC41IDI5LjV6TTEwMCA4MDB2LTIwMGgzMDB2MjAwIGgtMzAwek0xMTAwIDUzNWwtNDAwIC0xMzN2MTYzbDQwMCAxMzN2LTE2M3pNMTAwIDUwMHYtMjAwaDMwMHYyMDBoLTMwMHpNMTEwMCAzOTh2LTI0OHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtMzc1bC0xMDAgLTEwMGgtMzc1bC0xMDAgMTAwaDQwMGwyMDAgMjAwaDEwNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTgyOyIgZD0iTTE3IDEwMDdsMTYyIDE2MnExNyAxNyA0MCAxNHQzNyAtMjJsMTM5IC0xOTRxMTQgLTIwIDExIC00NC41dC0yMCAtNDEuNWwtMTE5IC0xMThxMTAyIC0xNDIgMjI4IC0yNjh0MjY3IC0yMjdsMTE5IDExOHExNyAxNyA0Mi41IDE5dDQ0LjUgLTEybDE5MiAtMTM2cTE5IC0xNCAyMi41IC0zNy41dC0xMy41IC00MC41bC0xNjMgLTE2MnEtMyAtMSAtOS41IC0xdC0yOS41IDJ0LTQ3LjUgNnQtNjIuNSAxNC41dC03Ny41IDI2LjV0LTkwIDQyLjUgdC0xMDEuNSA2MHQtMTExIDgzdC0xMTkgMTA4LjVxLTc0IDc0IC0xMzMuNSAxNTAuNXQtOTQuNSAxMzguNXQtNjAgMTE5LjV0LTM0LjUgMTAwdC0xNSA3NC41dC00LjUgNDh6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTE4MzsiIGQ9Ik02MDAgMTEwMHE5MiAwIDE3NSAtMTAuNXQxNDEuNSAtMjd0MTA4LjUgLTM2LjV0ODEuNSAtNDB0NTMuNSAtMzd0MzEgLTI3bDkgLTEwdi0yMDBxMCAtMjEgLTE0LjUgLTMzdC0zNC41IC05bC0yMDIgMzRxLTIwIDMgLTM0LjUgMjB0LTE0LjUgMzh2MTQ2cS0xNDEgMjQgLTMwMCAyNHQtMzAwIC0yNHYtMTQ2cTAgLTIxIC0xNC41IC0zOHQtMzQuNSAtMjBsLTIwMiAtMzRxLTIwIC0zIC0zNC41IDl0LTE0LjUgMzN2MjAwcTMgNCA5LjUgMTAuNSB0MzEgMjZ0NTQgMzcuNXQ4MC41IDM5LjV0MTA5IDM3LjV0MTQxIDI2LjV0MTc1IDEwLjV6TTYwMCA3OTVxNTYgMCA5NyAtOS41dDYwIC0yMy41dDMwIC0yOHQxMiAtMjRsMSAtMTB2LTUwbDM2NSAtMzAzcTE0IC0xNSAyNC41IC00MHQxMC41IC00NXYtMjEycTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0xMTAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYyMTJxMCAyMCAxMC41IDQ1dDI0LjUgNDBsMzY1IDMwM3Y1MCBxMCA0IDEgMTAuNXQxMiAyM3QzMCAyOXQ2MCAyMi41dDk3IDEweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxODQ7IiBkPSJNMTEwMCA3MDBsLTIwMCAtMjAwaC02MDBsLTIwMCAyMDB2NTAwaDIwMHYtMjAwaDIwMHYyMDBoMjAwdi0yMDBoMjAwdjIwMGgyMDB2LTUwMHpNMjUwIDQwMGg3MDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV0LTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTEybDEzNyAtMTAwaC05NTBsMTM3IDEwMGgtMTJxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41dDE0LjUgMzUuNXQzNS41IDE0LjV6TTUwIDEwMGgxMTAwcTIxIDAgMzUuNSAtMTQuNSB0MTQuNSAtMzUuNXYtNTBoLTEyMDB2NTBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxODU7IiBkPSJNNzAwIDExMDBoLTEwMHEtNDEgMCAtNzAuNSAtMjkuNXQtMjkuNSAtNzAuNXYtMTAwMGgzMDB2MTAwMHEwIDQxIC0yOS41IDcwLjV0LTcwLjUgMjkuNXpNMTEwMCA4MDBoLTEwMHEtNDEgMCAtNzAuNSAtMjkuNXQtMjkuNSAtNzAuNXYtNzAwaDMwMHY3MDBxMCA0MSAtMjkuNSA3MC41dC03MC41IDI5LjV6TTQwMCAwaC0zMDB2NDAwcTAgNDEgMjkuNSA3MC41dDcwLjUgMjkuNWgxMDBxNDEgMCA3MC41IC0yOS41dDI5LjUgLTcwLjV2LTQwMHogIiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTE4NjsiIGQ9Ik0yMDAgMTEwMGg3MDBxMTI0IDAgMjEyIC04OHQ4OCAtMjEydi01MDBxMCAtMTI0IC04OCAtMjEydC0yMTIgLTg4aC03MDBxLTEyNCAwIC0yMTIgODh0LTg4IDIxMnY1MDBxMCAxMjQgODggMjEydDIxMiA4OHpNMTAwIDkwMHYtNzAwaDkwMHY3MDBoLTkwMHpNNTAwIDcwMGgtMjAwdi0xMDBoMjAwdi0zMDBoLTMwMHYxMDBoMjAwdjEwMGgtMjAwdjMwMGgzMDB2LTEwMHpNOTAwIDcwMHYtMzAwbC0xMDAgLTEwMGgtMjAwdjUwMGgyMDB6IE03MDAgNzAwdi0zMDBoMTAwdjMwMGgtMTAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxODc7IiBkPSJNMjAwIDExMDBoNzAwcTEyNCAwIDIxMiAtODh0ODggLTIxMnYtNTAwcTAgLTEyNCAtODggLTIxMnQtMjEyIC04OGgtNzAwcS0xMjQgMCAtMjEyIDg4dC04OCAyMTJ2NTAwcTAgMTI0IDg4IDIxMnQyMTIgODh6TTEwMCA5MDB2LTcwMGg5MDB2NzAwaC05MDB6TTUwMCAzMDBoLTEwMHYyMDBoLTEwMHYtMjAwaC0xMDB2NTAwaDEwMHYtMjAwaDEwMHYyMDBoMTAwdi01MDB6TTkwMCA3MDB2LTMwMGwtMTAwIC0xMDBoLTIwMHY1MDBoMjAweiBNNzAwIDcwMHYtMzAwaDEwMHYzMDBoLTEwMHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTg4OyIgZD0iTTIwMCAxMTAwaDcwMHExMjQgMCAyMTIgLTg4dDg4IC0yMTJ2LTUwMHEwIC0xMjQgLTg4IC0yMTJ0LTIxMiAtODhoLTcwMHEtMTI0IDAgLTIxMiA4OHQtODggMjEydjUwMHEwIDEyNCA4OCAyMTJ0MjEyIDg4ek0xMDAgOTAwdi03MDBoOTAwdjcwMGgtOTAwek01MDAgNzAwaC0yMDB2LTMwMGgyMDB2LTEwMGgtMzAwdjUwMGgzMDB2LTEwMHpNOTAwIDcwMGgtMjAwdi0zMDBoMjAwdi0xMDBoLTMwMHY1MDBoMzAwdi0xMDB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTE4OTsiIGQ9Ik0yMDAgMTEwMGg3MDBxMTI0IDAgMjEyIC04OHQ4OCAtMjEydi01MDBxMCAtMTI0IC04OCAtMjEydC0yMTIgLTg4aC03MDBxLTEyNCAwIC0yMTIgODh0LTg4IDIxMnY1MDBxMCAxMjQgODggMjEydDIxMiA4OHpNMTAwIDkwMHYtNzAwaDkwMHY3MDBoLTkwMHpNNTAwIDQwMGwtMzAwIDE1MGwzMDAgMTUwdi0zMDB6TTkwMCA1NTBsLTMwMCAtMTUwdjMwMHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTkwOyIgZD0iTTIwMCAxMTAwaDcwMHExMjQgMCAyMTIgLTg4dDg4IC0yMTJ2LTUwMHEwIC0xMjQgLTg4IC0yMTJ0LTIxMiAtODhoLTcwMHEtMTI0IDAgLTIxMiA4OHQtODggMjEydjUwMHEwIDEyNCA4OCAyMTJ0MjEyIDg4ek0xMDAgOTAwdi03MDBoOTAwdjcwMGgtOTAwek05MDAgMzAwaC03MDB2NTAwaDcwMHYtNTAwek04MDAgNzAwaC0xMzBxLTM4IDAgLTY2LjUgLTQzdC0yOC41IC0xMDh0MjcgLTEwN3Q2OCAtNDJoMTMwdjMwMHpNMzAwIDcwMHYtMzAwIGgxMzBxNDEgMCA2OCA0MnQyNyAxMDd0LTI4LjUgMTA4dC02Ni41IDQzaC0xMzB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTE5MTsiIGQ9Ik0yMDAgMTEwMGg3MDBxMTI0IDAgMjEyIC04OHQ4OCAtMjEydi01MDBxMCAtMTI0IC04OCAtMjEydC0yMTIgLTg4aC03MDBxLTEyNCAwIC0yMTIgODh0LTg4IDIxMnY1MDBxMCAxMjQgODggMjEydDIxMiA4OHpNMTAwIDkwMHYtNzAwaDkwMHY3MDBoLTkwMHpNNTAwIDcwMGgtMjAwdi0xMDBoMjAwdi0zMDBoLTMwMHYxMDBoMjAwdjEwMGgtMjAwdjMwMGgzMDB2LTEwMHpNOTAwIDMwMGgtMTAwdjQwMGgtMTAwdjEwMGgyMDB2LTUwMHogTTcwMCAzMDBoLTEwMHYxMDBoMTAwdi0xMDB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTE5MjsiIGQ9Ik0yMDAgMTEwMGg3MDBxMTI0IDAgMjEyIC04OHQ4OCAtMjEydi01MDBxMCAtMTI0IC04OCAtMjEydC0yMTIgLTg4aC03MDBxLTEyNCAwIC0yMTIgODh0LTg4IDIxMnY1MDBxMCAxMjQgODggMjEydDIxMiA4OHpNMTAwIDkwMHYtNzAwaDkwMHY3MDBoLTkwMHpNMzAwIDcwMGgyMDB2LTQwMGgtMzAwdjUwMGgxMDB2LTEwMHpNOTAwIDMwMGgtMTAwdjQwMGgtMTAwdjEwMGgyMDB2LTUwMHpNMzAwIDYwMHYtMjAwaDEwMHYyMDBoLTEwMHogTTcwMCAzMDBoLTEwMHYxMDBoMTAwdi0xMDB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTE5MzsiIGQ9Ik0yMDAgMTEwMGg3MDBxMTI0IDAgMjEyIC04OHQ4OCAtMjEydi01MDBxMCAtMTI0IC04OCAtMjEydC0yMTIgLTg4aC03MDBxLTEyNCAwIC0yMTIgODh0LTg4IDIxMnY1MDBxMCAxMjQgODggMjEydDIxMiA4OHpNMTAwIDkwMHYtNzAwaDkwMHY3MDBoLTkwMHpNNTAwIDUwMGwtMTk5IC0yMDBoLTEwMHY1MGwxOTkgMjAwdjE1MGgtMjAwdjEwMGgzMDB2LTMwMHpNOTAwIDMwMGgtMTAwdjQwMGgtMTAwdjEwMGgyMDB2LTUwMHpNNzAxIDMwMGgtMTAwIHYxMDBoMTAwdi0xMDB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTE5NDsiIGQ9Ik02MDAgMTE5MXExMjAgMCAyMjkuNSAtNDd0MTg4LjUgLTEyNnQxMjYgLTE4OC41dDQ3IC0yMjkuNXQtNDcgLTIyOS41dC0xMjYgLTE4OC41dC0xODguNSAtMTI2dC0yMjkuNSAtNDd0LTIyOS41IDQ3dC0xODguNSAxMjZ0LTEyNiAxODguNXQtNDcgMjI5LjV0NDcgMjI5LjV0MTI2IDE4OC41dDE4OC41IDEyNnQyMjkuNSA0N3pNNjAwIDEwMjFxLTExNCAwIC0yMTEgLTU2LjV0LTE1My41IC0xNTMuNXQtNTYuNSAtMjExdDU2LjUgLTIxMSB0MTUzLjUgLTE1My41dDIxMSAtNTYuNXQyMTEgNTYuNXQxNTMuNSAxNTMuNXQ1Ni41IDIxMXQtNTYuNSAyMTF0LTE1My41IDE1My41dC0yMTEgNTYuNXpNODAwIDcwMGgtMzAwdi0yMDBoMzAwdi0xMDBoLTMwMGwtMTAwIDEwMHYyMDBsMTAwIDEwMGgzMDB2LTEwMHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTk1OyIgZD0iTTYwMCAxMTkxcTEyMCAwIDIyOS41IC00N3QxODguNSAtMTI2dDEyNiAtMTg4LjV0NDcgLTIyOS41dC00NyAtMjI5LjV0LTEyNiAtMTg4LjV0LTE4OC41IC0xMjZ0LTIyOS41IC00N3QtMjI5LjUgNDd0LTE4OC41IDEyNnQtMTI2IDE4OC41dC00NyAyMjkuNXQ0NyAyMjkuNXQxMjYgMTg4LjV0MTg4LjUgMTI2dDIyOS41IDQ3ek02MDAgMTAyMXEtMTE0IDAgLTIxMSAtNTYuNXQtMTUzLjUgLTE1My41dC01Ni41IC0yMTF0NTYuNSAtMjExIHQxNTMuNSAtMTUzLjV0MjExIC01Ni41dDIxMSA1Ni41dDE1My41IDE1My41dDU2LjUgMjExdC01Ni41IDIxMXQtMTUzLjUgMTUzLjV0LTIxMSA1Ni41ek04MDAgNzAwdi0xMDBsLTUwIC01MGwxMDAgLTEwMHYtNTBoLTEwMGwtMTAwIDEwMGgtMTUwdi0xMDBoLTEwMHY0MDBoMzAwek01MDAgNzAwdi0xMDBoMjAwdjEwMGgtMjAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxOTc7IiBkPSJNNTAzIDEwODlxMTEwIDAgMjAwLjUgLTU5LjV0MTM0LjUgLTE1Ni41cTQ0IDE0IDkwIDE0cTEyMCAwIDIwNSAtODYuNXQ4NSAtMjA3dC04NSAtMjA3dC0yMDUgLTg2LjVoLTEyOHYyNTBxMCAyMSAtMTQuNSAzNS41dC0zNS41IDE0LjVoLTMwMHEtMjEgMCAtMzUuNSAtMTQuNXQtMTQuNSAtMzUuNXYtMjUwaC0yMjJxLTgwIDAgLTEzNiA1Ny41dC01NiAxMzYuNXEwIDY5IDQzIDEyMi41dDEwOCA2Ny41cS0yIDE5IC0yIDM3cTAgMTAwIDQ5IDE4NSB0MTM0IDEzNHQxODUgNDl6TTUyNSA1MDBoMTUwcTEwIDAgMTcuNSAtNy41dDcuNSAtMTcuNXYtMjc1aDEzN3EyMSAwIDI2IC0xMS41dC04IC0yNy41bC0yMjMgLTI0NHEtMTMgLTE2IC0zMiAtMTZ0LTMyIDE2bC0yMjMgMjQ0cS0xMyAxNiAtOCAyNy41dDI2IDExLjVoMTM3djI3NXEwIDEwIDcuNSAxNy41dDE3LjUgNy41eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUxOTg7IiBkPSJNNTAyIDEwODlxMTEwIDAgMjAxIC01OS41dDEzNSAtMTU2LjVxNDMgMTUgODkgMTVxMTIxIDAgMjA2IC04Ni41dDg2IC0yMDYuNXEwIC05OSAtNjAgLTE4MXQtMTUwIC0xMTBsLTM3OCAzNjBxLTEzIDE2IC0zMS41IDE2dC0zMS41IC0xNmwtMzgxIC0zNjVoLTlxLTc5IDAgLTEzNS41IDU3LjV0LTU2LjUgMTM2LjVxMCA2OSA0MyAxMjIuNXQxMDggNjcuNXEtMiAxOSAtMiAzOHEwIDEwMCA0OSAxODQuNXQxMzMuNSAxMzR0MTg0LjUgNDkuNXogTTYzMiA0NjdsMjIzIC0yMjhxMTMgLTE2IDggLTI3LjV0LTI2IC0xMS41aC0xMzd2LTI3NXEwIC0xMCAtNy41IC0xNy41dC0xNy41IC03LjVoLTE1MHEtMTAgMCAtMTcuNSA3LjV0LTcuNSAxNy41djI3NWgtMTM3cS0yMSAwIC0yNiAxMS41dDggMjcuNXExOTkgMjA0IDIyMyAyMjhxMTkgMTkgMzEuNSAxOXQzMi41IC0xOXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMTk5OyIgZD0iTTcwMCAxMDB2MTAwaDQwMGwtMjcwIDMwMGgxNzBsLTI3MCAzMDBoMTcwbC0zMDAgMzMzbC0zMDAgLTMzM2gxNzBsLTI3MCAtMzAwaDE3MGwtMjcwIC0zMDBoNDAwdi0xMDBoLTUwcS0yMSAwIC0zNS41IC0xNC41dC0xNC41IC0zNS41di01MGg0MDB2NTBxMCAyMSAtMTQuNSAzNS41dC0zNS41IDE0LjVoLTUweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUyMDA7IiBkPSJNNjAwIDExNzlxOTQgMCAxNjcuNSAtNTYuNXQ5OS41IC0xNDUuNXE4OSAtNiAxNTAuNSAtNzEuNXQ2MS41IC0xNTUuNXEwIC02MSAtMjkuNSAtMTEyLjV0LTc5LjUgLTgyLjVxOSAtMjkgOSAtNTVxMCAtNzQgLTUyLjUgLTEyNi41dC0xMjYuNSAtNTIuNXEtNTUgMCAtMTAwIDMwdi0yNTFxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTUwaC0zMDB2NTBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41djI1MXEtNDUgLTMwIC0xMDAgLTMwIHEtNzQgMCAtMTI2LjUgNTIuNXQtNTIuNSAxMjYuNXEwIDE4IDQgMzhxLTQ3IDIxIC03NS41IDY1dC0yOC41IDk3cTAgNzQgNTIuNSAxMjYuNXQxMjYuNSA1Mi41cTUgMCAyMyAtMnEwIDIgLTEgMTB0LTEgMTNxMCAxMTYgODEuNSAxOTcuNXQxOTcuNSA4MS41eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUyMDE7IiBkPSJNMTAxMCAxMDEwcTExMSAtMTExIDE1MC41IC0yNjAuNXQwIC0yOTl0LTE1MC41IC0yNjAuNXEtODMgLTgzIC0xOTEuNSAtMTI2LjV0LTIxOC41IC00My41dC0yMTguNSA0My41dC0xOTEuNSAxMjYuNXEtMTExIDExMSAtMTUwLjUgMjYwLjV0MCAyOTl0MTUwLjUgMjYwLjVxODMgODMgMTkxLjUgMTI2LjV0MjE4LjUgNDMuNXQyMTguNSAtNDMuNXQxOTEuNSAtMTI2LjV6TTQ3NiAxMDY1cS00IDAgLTggLTFxLTEyMSAtMzQgLTIwOS41IC0xMjIuNSB0LTEyMi41IC0yMDkuNXEtNCAtMTIgMi41IC0yM3QxOC41IC0xNGwzNiAtOXEzIC0xIDcgLTFxMjMgMCAyOSAyMnEyNyA5NiA5OCAxNjZxNzAgNzEgMTY2IDk4cTExIDMgMTcuNSAxMy41dDMuNSAyMi41bC05IDM1cS0zIDEzIC0xNCAxOXEtNyA0IC0xNSA0ek01MTIgOTIwcS00IDAgLTkgLTJxLTgwIC0yNCAtMTM4LjUgLTgyLjV0LTgyLjUgLTEzOC41cS00IC0xMyAyIC0yNHQxOSAtMTRsMzQgLTlxNCAtMSA4IC0xcTIyIDAgMjggMjEgcTE4IDU4IDU4LjUgOTguNXQ5Ny41IDU4LjVxMTIgMyAxOCAxMy41dDMgMjEuNWwtOSAzNXEtMyAxMiAtMTQgMTlxLTcgNCAtMTUgNHpNNzE5LjUgNzE5LjVxLTQ5LjUgNDkuNSAtMTE5LjUgNDkuNXQtMTE5LjUgLTQ5LjV0LTQ5LjUgLTExOS41dDQ5LjUgLTExOS41dDExOS41IC00OS41dDExOS41IDQ5LjV0NDkuNSAxMTkuNXQtNDkuNSAxMTkuNXpNODU1IDU1MXEtMjIgMCAtMjggLTIxcS0xOCAtNTggLTU4LjUgLTk4LjV0LTk4LjUgLTU3LjUgcS0xMSAtNCAtMTcgLTE0LjV0LTMgLTIxLjVsOSAtMzVxMyAtMTIgMTQgLTE5cTcgLTQgMTUgLTRxNCAwIDkgMnE4MCAyNCAxMzguNSA4Mi41dDgyLjUgMTM4LjVxNCAxMyAtMi41IDI0dC0xOC41IDE0bC0zNCA5cS00IDEgLTggMXpNMTAwMCA1MTVxLTIzIDAgLTI5IC0yMnEtMjcgLTk2IC05OCAtMTY2cS03MCAtNzEgLTE2NiAtOThxLTExIC0zIC0xNy41IC0xMy41dC0zLjUgLTIyLjVsOSAtMzVxMyAtMTMgMTQgLTE5cTcgLTQgMTUgLTQgcTQgMCA4IDFxMTIxIDM0IDIwOS41IDEyMi41dDEyMi41IDIwOS41cTQgMTIgLTIuNSAyM3QtMTguNSAxNGwtMzYgOXEtMyAxIC03IDF6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTIwMjsiIGQ9Ik03MDAgODAwaDMwMHYtMzgwaC0xODB2MjAwaC0zNDB2LTIwMGgtMzgwdjc1NXEwIDEwIDcuNSAxNy41dDE3LjUgNy41aDU3NXYtNDAwek0xMDAwIDkwMGgtMjAwdjIwMHpNNzAwIDMwMGgxNjJsLTIxMiAtMjEybC0yMTIgMjEyaDE2MnYyMDBoMTAwdi0yMDB6TTUyMCAwaC0zOTVxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXYzOTV6TTEwMDAgMjIwdi0xOTVxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC0xOTV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTIwMzsiIGQ9Ik03MDAgODAwaDMwMHYtNTIwbC0zNTAgMzUwbC01NTAgLTU1MHYxMDk1cTAgMTAgNy41IDE3LjV0MTcuNSA3LjVoNTc1di00MDB6TTEwMDAgOTAwaC0yMDB2MjAwek04NjIgMjAwaC0xNjJ2LTIwMGgtMTAwdjIwMGgtMTYybDIxMiAyMTJ6TTQ4MCAwaC0zNTVxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXY1NWgzODB2LTgwek0xMDAwIDgwdi01NXEwIC0xMCAtNy41IC0xNy41dC0xNy41IC03LjVoLTE1NXY4MGgxODB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTIwNDsiIGQ9Ik0xMTYyIDgwMGgtMTYydi0yMDBoMTAwbDEwMCAtMTAwaC0zMDB2MzAwaC0xNjJsMjEyIDIxMnpNMjAwIDgwMGgyMDBxMjcgMCA0MCAtMnQyOS41IC0xMC41dDIzLjUgLTMwdDcgLTU3LjVoMzAwdi0xMDBoLTYwMGwtMjAwIC0zNTB2NDUwaDEwMHEwIDM2IDcgNTcuNXQyMy41IDMwdDI5LjUgMTAuNXQ0MCAyek04MDAgNDAwaDI0MGwtMjQwIC00MDBoLTgwMGwzMDAgNTAwaDUwMHYtMTAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUyMDU7IiBkPSJNNjUwIDExMDBoMTAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di01MGg1MHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtMTAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0zMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djEwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjVoNTB2NTBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek0xMDAwIDg1MHYxNTBxNDEgMCA3MC41IC0yOS41dDI5LjUgLTcwLjV2LTgwMCBxMCAtNDEgLTI5LjUgLTcwLjV0LTcwLjUgLTI5LjVoLTYwMHEtMSAwIC0yMCA0bDI0NiAyNDZsLTMyNiAzMjZ2MzI0cTAgNDEgMjkuNSA3MC41dDcwLjUgMjkuNXYtMTUwcTAgLTYyIDQ0IC0xMDZ0MTA2IC00NGgzMDBxNjIgMCAxMDYgNDR0NDQgMTA2ek00MTIgMjUwbC0yMTIgLTIxMnYxNjJoLTIwMHYxMDBoMjAwdjE2MnoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjA2OyIgZD0iTTQ1MCAxMTAwaDEwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtNTBoNTBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTEwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtMzAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYxMDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41aDUwdjUwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNODAwIDg1MHYxNTBxNDEgMCA3MC41IC0yOS41dDI5LjUgLTcwLjV2LTUwMCBoLTIwMHYtMzAwaDIwMHEwIC0zNiAtNyAtNTcuNXQtMjMuNSAtMzB0LTI5LjUgLTEwLjV0LTQwIC0yaC02MDBxLTQxIDAgLTcwLjUgMjkuNXQtMjkuNSA3MC41djgwMHEwIDQxIDI5LjUgNzAuNXQ3MC41IDI5LjV2LTE1MHEwIC02MiA0NCAtMTA2dDEwNiAtNDRoMzAwcTYyIDAgMTA2IDQ0dDQ0IDEwNnpNMTIxMiAyNTBsLTIxMiAtMjEydjE2MmgtMjAwdjEwMGgyMDB2MTYyeiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUyMDk7IiBkPSJNNjU4IDExOTdsNjM3IC0xMTA0cTIzIC0zOCA3IC02NS41dC02MCAtMjcuNWgtMTI3NnEtNDQgMCAtNjAgMjcuNXQ3IDY1LjVsNjM3IDExMDRxMjIgMzkgNTQgMzl0NTQgLTM5ek03MDQgODAwaC0yMDhxLTIwIDAgLTMyIC0xNC41dC04IC0zNC41bDU4IC0zMDJxNCAtMjAgMjEuNSAtMzQuNXQzNy41IC0xNC41aDU0cTIwIDAgMzcuNSAxNC41dDIxLjUgMzQuNWw1OCAzMDJxNCAyMCAtOCAzNC41dC0zMiAxNC41ek01MDAgMzAwdi0xMDBoMjAwIHYxMDBoLTIwMHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjEwOyIgZD0iTTQyNSAxMTAwaDI1MHExMCAwIDE3LjUgLTcuNXQ3LjUgLTE3LjV2LTE1MHEwIC0xMCAtNy41IC0xNy41dC0xNy41IC03LjVoLTI1MHEtMTAgMCAtMTcuNSA3LjV0LTcuNSAxNy41djE1MHEwIDEwIDcuNSAxNy41dDE3LjUgNy41ek00MjUgODAwaDI1MHExMCAwIDE3LjUgLTcuNXQ3LjUgLTE3LjV2LTE1MHEwIC0xMCAtNy41IC0xNy41dC0xNy41IC03LjVoLTI1MHEtMTAgMCAtMTcuNSA3LjV0LTcuNSAxNy41djE1MHEwIDEwIDcuNSAxNy41IHQxNy41IDcuNXpNODI1IDgwMGgyNTBxMTAgMCAxNy41IC03LjV0Ny41IC0xNy41di0xNTBxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC0yNTBxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXYxNTBxMCAxMCA3LjUgMTcuNXQxNy41IDcuNXpNMjUgNTAwaDI1MHExMCAwIDE3LjUgLTcuNXQ3LjUgLTE3LjV2LTE1MHEwIC0xMCAtNy41IC0xNy41dC0xNy41IC03LjVoLTI1MHEtMTAgMCAtMTcuNSA3LjV0LTcuNSAxNy41djE1MCBxMCAxMCA3LjUgMTcuNXQxNy41IDcuNXpNNDI1IDUwMGgyNTBxMTAgMCAxNy41IC03LjV0Ny41IC0xNy41di0xNTBxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC0yNTBxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXYxNTBxMCAxMCA3LjUgMTcuNXQxNy41IDcuNXpNODI1IDUwMGgyNTBxMTAgMCAxNy41IC03LjV0Ny41IC0xNy41di0xNTBxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC0yNTBxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNSB2MTUwcTAgMTAgNy41IDE3LjV0MTcuNSA3LjV6TTI1IDIwMGgyNTBxMTAgMCAxNy41IC03LjV0Ny41IC0xNy41di0xNTBxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC0yNTBxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXYxNTBxMCAxMCA3LjUgMTcuNXQxNy41IDcuNXpNNDI1IDIwMGgyNTBxMTAgMCAxNy41IC03LjV0Ny41IC0xNy41di0xNTBxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC0yNTBxLTEwIDAgLTE3LjUgNy41IHQtNy41IDE3LjV2MTUwcTAgMTAgNy41IDE3LjV0MTcuNSA3LjV6TTgyNSAyMDBoMjUwcTEwIDAgMTcuNSAtNy41dDcuNSAtMTcuNXYtMTUwcTAgLTEwIC03LjUgLTE3LjV0LTE3LjUgLTcuNWgtMjUwcS0xMCAwIC0xNy41IDcuNXQtNy41IDE3LjV2MTUwcTAgMTAgNy41IDE3LjV0MTcuNSA3LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTIxMTsiIGQ9Ik03MDAgMTIwMGgxMDB2LTIwMGgtMTAwdi0xMDBoMzUwcTYyIDAgODYuNSAtMzkuNXQtMy41IC05NC41bC02NiAtMTMycS00MSAtODMgLTgxIC0xMzRoLTc3MnEtNDAgNTEgLTgxIDEzNGwtNjYgMTMycS0yOCA1NSAtMy41IDk0LjV0ODYuNSAzOS41aDM1MHYxMDBoLTEwMHYyMDBoMTAwdjEwMGgyMDB2LTEwMHpNMjUwIDQwMGg3MDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV0LTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTEybDEzNyAtMTAwIGgtOTUwbDEzOCAxMDBoLTEzcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXQxNC41IDM1LjV0MzUuNSAxNC41ek01MCAxMDBoMTEwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtNTBoLTEyMDB2NTBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUyMTI7IiBkPSJNNjAwIDEzMDBxNDAgMCA2OC41IC0yOS41dDI4LjUgLTcwLjVoLTE5NHEwIDQxIDI4LjUgNzAuNXQ2OC41IDI5LjV6TTQ0MyAxMTAwaDMxNHExOCAtMzcgMTggLTc1cTAgLTggLTMgLTI1aDMyOHE0MSAwIDQ0LjUgLTE2LjV0LTMwLjUgLTM4LjVsLTE3NSAtMTQ1aC02NzhsLTE3OCAxNDVxLTM0IDIyIC0yOSAzOC41dDQ2IDE2LjVoMzI4cS0zIDE3IC0zIDI1cTAgMzggMTggNzV6TTI1MCA3MDBoNzAwcTIxIDAgMzUuNSAtMTQuNSB0MTQuNSAtMzUuNXQtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtMTUwdi0yMDBsMjc1IC0yMDBoLTk1MGwyNzUgMjAwdjIwMGgtMTUwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXQxNC41IDM1LjV0MzUuNSAxNC41ek01MCAxMDBoMTEwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtNTBoLTEyMDB2NTBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUyMTM7IiBkPSJNNjAwIDExODFxNzUgMCAxMjggLTUzdDUzIC0xMjh0LTUzIC0xMjh0LTEyOCAtNTN0LTEyOCA1M3QtNTMgMTI4dDUzIDEyOHQxMjggNTN6TTYwMiA3OThoNDZxMzQgMCA1NS41IC0yOC41dDIxLjUgLTg2LjVxMCAtNzYgMzkgLTE4M2gtMzI0cTM5IDEwNyAzOSAxODNxMCA1OCAyMS41IDg2LjV0NTYuNSAyOC41aDQ1ek0yNTAgNDAwaDcwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXQtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtMTMgbDEzOCAtMTAwaC05NTBsMTM3IDEwMGgtMTJxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41dDE0LjUgMzUuNXQzNS41IDE0LjV6TTUwIDEwMGgxMTAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di01MGgtMTIwMHY1MHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTIxNDsiIGQ9Ik02MDAgMTMwMHE0NyAwIDkyLjUgLTUzLjV0NzEgLTEyM3QyNS41IC0xMjMuNXEwIC03OCAtNTUuNSAtMTMzLjV0LTEzMy41IC01NS41dC0xMzMuNSA1NS41dC01NS41IDEzMy41cTAgNjIgMzQgMTQzbDE0NCAtMTQzbDExMSAxMTFsLTE2MyAxNjNxMzQgMjYgNjMgMjZ6TTYwMiA3OThoNDZxMzQgMCA1NS41IC0yOC41dDIxLjUgLTg2LjVxMCAtNzYgMzkgLTE4M2gtMzI0cTM5IDEwNyAzOSAxODNxMCA1OCAyMS41IDg2LjV0NTYuNSAyOC41aDQ1IHpNMjUwIDQwMGg3MDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV0LTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTEzbDEzOCAtMTAwaC05NTBsMTM3IDEwMGgtMTJxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41dDE0LjUgMzUuNXQzNS41IDE0LjV6TTUwIDEwMGgxMTAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di01MGgtMTIwMHY1MHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTIxNTsiIGQ9Ik02MDAgMTIwMGwzMDAgLTE2MXYtMTM5aC0zMDBxMCAtNTcgMTguNSAtMTA4dDUwIC05MS41dDYzIC03MnQ3MCAtNjcuNXQ1Ny41IC02MWgtNTMwcS02MCA4MyAtOTAuNSAxNzcuNXQtMzAuNSAxNzguNXQzMyAxNjQuNXQ4Ny41IDEzOS41dDEyNiA5Ni41dDE0NS41IDQxLjV2LTk4ek0yNTAgNDAwaDcwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXQtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtMTNsMTM4IC0xMDBoLTk1MGwxMzcgMTAwIGgtMTJxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41dDE0LjUgMzUuNXQzNS41IDE0LjV6TTUwIDEwMGgxMTAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di01MGgtMTIwMHY1MHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTIxNjsiIGQ9Ik02MDAgMTMwMHE0MSAwIDcwLjUgLTI5LjV0MjkuNSAtNzAuNXYtNzhxNDYgLTI2IDczIC03MnQyNyAtMTAwdi01MGgtNDAwdjUwcTAgNTQgMjcgMTAwdDczIDcydjc4cTAgNDEgMjkuNSA3MC41dDcwLjUgMjkuNXpNNDAwIDgwMGg0MDBxNTQgMCAxMDAgLTI3dDcyIC03M2gtMTcydi0xMDBoMjAwdi0xMDBoLTIwMHYtMTAwaDIwMHYtMTAwaC0yMDB2LTEwMGgyMDBxMCAtODMgLTU4LjUgLTE0MS41dC0xNDEuNSAtNTguNWgtNDAwIHEtODMgMCAtMTQxLjUgNTguNXQtNTguNSAxNDEuNXY0MDBxMCA4MyA1OC41IDE0MS41dDE0MS41IDU4LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTIxODsiIGQ9Ik0xNTAgMTEwMGg5MDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTUwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtOTAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXY1MDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek0xMjUgNDAwaDk1MHExMCAwIDE3LjUgLTcuNXQ3LjUgLTE3LjV2LTUwcTAgLTEwIC03LjUgLTE3LjV0LTE3LjUgLTcuNWgtMjgzbDIyNCAtMjI0cTEzIC0xMyAxMyAtMzEuNXQtMTMgLTMyIHQtMzEuNSAtMTMuNXQtMzEuNSAxM2wtODggODhoLTUyNGwtODcgLTg4cS0xMyAtMTMgLTMyIC0xM3QtMzIgMTMuNXQtMTMgMzJ0MTMgMzEuNWwyMjQgMjI0aC0yODlxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXY1MHEwIDEwIDcuNSAxNy41dDE3LjUgNy41ek01NDEgMzAwbC0xMDAgLTEwMGgzMjRsLTEwMCAxMDBoLTEyNHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjE5OyIgZD0iTTIwMCAxMTAwaDgwMHE4MyAwIDE0MS41IC01OC41dDU4LjUgLTE0MS41di0yMDBoLTEwMHEwIDQxIC0yOS41IDcwLjV0LTcwLjUgMjkuNWgtMjUwcS00MSAwIC03MC41IC0yOS41dC0yOS41IC03MC41aC0xMDBxMCA0MSAtMjkuNSA3MC41dC03MC41IDI5LjVoLTI1MHEtNDEgMCAtNzAuNSAtMjkuNXQtMjkuNSAtNzAuNWgtMTAwdjIwMHEwIDgzIDU4LjUgMTQxLjV0MTQxLjUgNTguNXpNMTAwIDYwMGgxMDAwcTQxIDAgNzAuNSAtMjkuNSB0MjkuNSAtNzAuNXYtMzAwaC0xMjAwdjMwMHEwIDQxIDI5LjUgNzAuNXQ3MC41IDI5LjV6TTMwMCAxMDB2LTUwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0xMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djUwaDIwMHpNMTEwMCAxMDB2LTUwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0xMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djUwaDIwMHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjIxOyIgZD0iTTQ4MCAxMTY1bDY4MiAtNjgzcTMxIC0zMSAzMSAtNzUuNXQtMzEgLTc1LjVsLTEzMSAtMTMxaC00ODFsLTUxNyA1MThxLTMyIDMxIC0zMiA3NS41dDMyIDc1LjVsMjk1IDI5NnEzMSAzMSA3NS41IDMxdDc2LjUgLTMxek0xMDggNzk0bDM0MiAtMzQybDMwMyAzMDRsLTM0MSAzNDF6TTI1MCAxMDBoODAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di01MGgtOTAwdjUwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjIzOyIgZD0iTTEwNTcgNjQ3bC0xODkgNTA2cS04IDE5IC0yNy41IDMzdC00MC41IDE0aC00MDBxLTIxIDAgLTQwLjUgLTE0dC0yNy41IC0zM2wtMTg5IC01MDZxLTggLTE5IDEuNSAtMzN0MzAuNSAtMTRoNjI1di0xNTBxMCAtMjEgMTQuNSAtMzUuNXQzNS41IC0xNC41dDM1LjUgMTQuNXQxNC41IDM1LjV2MTUwaDEyNXEyMSAwIDMwLjUgMTR0MS41IDMzek04OTcgMGgtNTk1djUwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNWg1MHY1MCBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41aDQ4djMwMGgyMDB2LTMwMGg0N3EyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtNTBoNTBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTUweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUyMjQ7IiBkPSJNOTAwIDgwMGgzMDB2LTU3NXEwIC0xMCAtNy41IC0xNy41dC0xNy41IC03LjVoLTM3NXY1OTFsLTMwMCAzMDB2ODRxMCAxMCA3LjUgMTcuNXQxNy41IDcuNWgzNzV2LTQwMHpNMTIwMCA5MDBoLTIwMHYyMDB6TTQwMCA2MDBoMzAwdi01NzVxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC02NTBxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXY5NTBxMCAxMCA3LjUgMTcuNXQxNy41IDcuNWgzNzV2LTQwMHpNNzAwIDcwMGgtMjAwdjIwMHogIiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTIyNTsiIGQ9Ik00ODQgMTA5NWgxOTVxNzUgMCAxNDYgLTMyLjV0MTI0IC04NnQ4OS41IC0xMjIuNXQ0OC41IC0xNDJxMTggLTE0IDM1IC0yMHEzMSAtMTAgNjQuNSA2LjV0NDMuNSA0OC41cTEwIDM0IC0xNSA3MXEtMTkgMjcgLTkgNDNxNSA4IDEyLjUgMTF0MTkgLTF0MjMuNSAtMTZxNDEgLTQ0IDM5IC0xMDVxLTMgLTYzIC00NiAtMTA2LjV0LTEwNCAtNDMuNWgtNjJxLTcgLTU1IC0zNSAtMTE3dC01NiAtMTAwbC0zOSAtMjM0cS0zIC0yMCAtMjAgLTM0LjUgdC0zOCAtMTQuNWgtMTAwcS0yMSAwIC0zMyAxNC41dC05IDM0LjVsMTIgNzBxLTQ5IC0xNCAtOTEgLTE0aC0xOTVxLTI0IDAgLTY1IDhsLTExIC02NHEtMyAtMjAgLTIwIC0zNC41dC0zOCAtMTQuNWgtMTAwcS0yMSAwIC0zMyAxNC41dC05IDM0LjVsMjYgMTU3cS04NCA3NCAtMTI4IDE3NWwtMTU5IDUzcS0xOSA3IC0zMyAyNnQtMTQgNDB2NTBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41aDEyNHExMSA4NyA1NiAxNjZsLTExMSA5NSBxLTE2IDE0IC0xMi41IDIzLjV0MjQuNSA5LjVoMjAzcTExNiAxMDEgMjUwIDEwMXpNNjc1IDEwMDBoLTI1MHEtMTAgMCAtMTcuNSAtNy41dC03LjUgLTE3LjV2LTUwcTAgLTEwIDcuNSAtMTcuNXQxNy41IC03LjVoMjUwcTEwIDAgMTcuNSA3LjV0Ny41IDE3LjV2NTBxMCAxMCAtNy41IDE3LjV0LTE3LjUgNy41eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUyMjY7IiBkPSJNNjQxIDkwMGw0MjMgMjQ3cTE5IDggNDIgMi41dDM3IC0yMS41bDMyIC0zOHExNCAtMTUgMTIuNSAtMzZ0LTE3LjUgLTM0bC0xMzkgLTEyMGgtMzkwek01MCAxMTAwaDEwNnE2NyAwIDEwMyAtMTd0NjYgLTcxbDEwMiAtMjEyaDgyM3EyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtNTBxMCAtMjEgLTE0IC00MHQtMzMgLTI2bC03MzcgLTEzMnEtMjMgLTQgLTQwIDZ0LTI2IDI1cS00MiA2NyAtMTAwIDY3aC0zMDBxLTYyIDAgLTEwNiA0NCB0LTQ0IDEwNnYyMDBxMCA2MiA0NCAxMDZ0MTA2IDQ0ek0xNzMgOTI4aC04MHEtMTkgMCAtMjggLTE0dC05IC0zNXYtNTZxMCAtNTEgNDIgLTUxaDEzNHExNiAwIDIxLjUgOHQ1LjUgMjRxMCAxMSAtMTYgNDV0LTI3IDUxcS0xOCAyOCAtNDMgMjh6TTU1MCA3MjdxLTMyIDAgLTU0LjUgLTIyLjV0LTIyLjUgLTU0LjV0MjIuNSAtNTQuNXQ1NC41IC0yMi41dDU0LjUgMjIuNXQyMi41IDU0LjV0LTIyLjUgNTQuNXQtNTQuNSAyMi41ek0xMzAgMzg5IGwxNTIgMTMwcTE4IDE5IDM0IDI0dDMxIC0zLjV0MjQuNSAtMTcuNXQyNS41IC0yOHEyOCAtMzUgNTAuNSAtNTF0NDguNSAtMTNsNjMgNWw0OCAtMTc5cTEzIC02MSAtMy41IC05Ny41dC02Ny41IC03OS41bC04MCAtNjlxLTQ3IC00MCAtMTA5IC0zNS41dC0xMDMgNTEuNWwtMTMwIDE1MXEtNDAgNDcgLTM1LjUgMTA5LjV0NTEuNSAxMDIuNXpNMzgwIDM3N2wtMTAyIC04OHEtMzEgLTI3IDIgLTY1bDM3IC00M3ExMyAtMTUgMjcuNSAtMTkuNSB0MzEuNSA2LjVsNjEgNTNxMTkgMTYgMTQgNDlxLTIgMjAgLTEyIDU2dC0xNyA0NXEtMTEgMTIgLTE5IDE0dC0yMyAtOHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjI3OyIgZD0iTTYyNSAxMjAwaDE1MHExMCAwIDE3LjUgLTcuNXQ3LjUgLTE3LjV2LTEwOXE3OSAtMzMgMTMxIC04Ny41dDUzIC0xMjguNXExIC00NiAtMTUgLTg0LjV0LTM5IC02MXQtNDYgLTM4dC0zOSAtMjEuNWwtMTcgLTZxNiAwIDE1IC0xLjV0MzUgLTl0NTAgLTE3LjV0NTMgLTMwdDUwIC00NXQzNS41IC02NHQxNC41IC04NHEwIC01OSAtMTEuNSAtMTA1LjV0LTI4LjUgLTc2LjV0LTQ0IC01MXQtNDkuNSAtMzEuNXQtNTQuNSAtMTZ0LTQ5LjUgLTYuNSB0LTQzLjUgLTF2LTc1cTAgLTEwIC03LjUgLTE3LjV0LTE3LjUgLTcuNWgtMTUwcS0xMCAwIC0xNy41IDcuNXQtNy41IDE3LjV2NzVoLTEwMHYtNzVxMCAtMTAgLTcuNSAtMTcuNXQtMTcuNSAtNy41aC0xNTBxLTEwIDAgLTE3LjUgNy41dC03LjUgMTcuNXY3NWgtMTc1cS0xMCAwIC0xNy41IDcuNXQtNy41IDE3LjV2MTUwcTAgMTAgNy41IDE3LjV0MTcuNSA3LjVoNzV2NjAwaC03NXEtMTAgMCAtMTcuNSA3LjV0LTcuNSAxNy41djE1MCBxMCAxMCA3LjUgMTcuNXQxNy41IDcuNWgxNzV2NzVxMCAxMCA3LjUgMTcuNXQxNy41IDcuNWgxNTBxMTAgMCAxNy41IC03LjV0Ny41IC0xNy41di03NWgxMDB2NzVxMCAxMCA3LjUgMTcuNXQxNy41IDcuNXpNNDAwIDkwMHYtMjAwaDI2M3EyOCAwIDQ4LjUgMTAuNXQzMCAyNXQxNSAyOXQ1LjUgMjUuNWwxIDEwcTAgNCAtMC41IDExdC02IDI0dC0xNSAzMHQtMzAgMjR0LTQ4LjUgMTFoLTI2M3pNNDAwIDUwMHYtMjAwaDM2M3EyOCAwIDQ4LjUgMTAuNSB0MzAgMjV0MTUgMjl0NS41IDI1LjVsMSAxMHEwIDQgLTAuNSAxMXQtNiAyNHQtMTUgMzB0LTMwIDI0dC00OC41IDExaC0zNjN6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTIzMDsiIGQ9Ik0yMTIgMTE5OGg3ODBxODYgMCAxNDcgLTYxdDYxIC0xNDd2LTQxNnEwIC01MSAtMTggLTE0Mi41dC0zNiAtMTU3LjVsLTE4IC02NnEtMjkgLTg3IC05My41IC0xNDYuNXQtMTQ2LjUgLTU5LjVoLTU3MnEtODIgMCAtMTQ3IDU5dC05MyAxNDdxLTggMjggLTIwIDczdC0zMiAxNDMuNXQtMjAgMTQ5LjV2NDE2cTAgODYgNjEgMTQ3dDE0NyA2MXpNNjAwIDEwNDVxLTcwIDAgLTEzMi41IC0xMS41dC0xMDUuNSAtMzAuNXQtNzguNSAtNDEuNSB0LTU3IC00NXQtMzYgLTQxdC0yMC41IC0zMC41bC02IC0xMmwxNTYgLTI0M2g1NjBsMTU2IDI0M3EtMiA1IC02IDEyLjV0LTIwIDI5LjV0LTM2LjUgNDJ0LTU3IDQ0LjV0LTc5IDQydC0xMDUgMjkuNXQtMTMyLjUgMTJ6TTc2MiA3MDNoLTE1N2wxOTUgMjYxeiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUyMzE7IiBkPSJNNDc1IDEzMDBoMTUwcTEwMyAwIDE4OSAtODZ0ODYgLTE4OXYtNTAwcTAgLTQxIC00MiAtODN0LTgzIC00MmgtNDUwcS00MSAwIC04MyA0MnQtNDIgODN2NTAwcTAgMTAzIDg2IDE4OXQxODkgODZ6TTcwMCAzMDB2LTIyNXEwIC0yMSAtMjcgLTQ4dC00OCAtMjdoLTE1MHEtMjEgMCAtNDggMjd0LTI3IDQ4djIyNWgzMDB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTIzMjsiIGQ9Ik00NzUgMTMwMGg5NnEwIC0xNTAgODkuNSAtMjM5LjV0MjM5LjUgLTg5LjV2LTQ0NnEwIC00MSAtNDIgLTgzdC04MyAtNDJoLTQ1MHEtNDEgMCAtODMgNDJ0LTQyIDgzdjUwMHEwIDEwMyA4NiAxODl0MTg5IDg2ek03MDAgMzAwdi0yMjVxMCAtMjEgLTI3IC00OHQtNDggLTI3aC0xNTBxLTIxIDAgLTQ4IDI3dC0yNyA0OHYyMjVoMzAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUyMzM7IiBkPSJNMTI5NCA3NjdsLTYzOCAtMjgzbC0zNzggMTcwbC03OCAtNjB2LTIyNGwxMDAgLTE1MHYtMTk5bC0xNTAgMTQ4bC0xNTAgLTE0OXYyMDBsMTAwIDE1MHYyNTBxMCA0IC0wLjUgMTAuNXQwIDkuNXQxIDh0MyA4dDYuNSA2bDQ3IDQwbC0xNDcgNjVsNjQyIDI4M3pNMTAwMCAzODBsLTM1MCAtMTY2bC0zNTAgMTY2djE0N2wzNTAgLTE2NWwzNTAgMTY1di0xNDd6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTIzNDsiIGQ9Ik0yNTAgODAwcTYyIDAgMTA2IC00NHQ0NCAtMTA2dC00NCAtMTA2dC0xMDYgLTQ0dC0xMDYgNDR0LTQ0IDEwNnQ0NCAxMDZ0MTA2IDQ0ek02NTAgODAwcTYyIDAgMTA2IC00NHQ0NCAtMTA2dC00NCAtMTA2dC0xMDYgLTQ0dC0xMDYgNDR0LTQ0IDEwNnQ0NCAxMDZ0MTA2IDQ0ek0xMDUwIDgwMHE2MiAwIDEwNiAtNDR0NDQgLTEwNnQtNDQgLTEwNnQtMTA2IC00NHQtMTA2IDQ0dC00NCAxMDZ0NDQgMTA2dDEwNiA0NHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjM1OyIgZD0iTTU1MCAxMTAwcTYyIDAgMTA2IC00NHQ0NCAtMTA2dC00NCAtMTA2dC0xMDYgLTQ0dC0xMDYgNDR0LTQ0IDEwNnQ0NCAxMDZ0MTA2IDQ0ek01NTAgNzAwcTYyIDAgMTA2IC00NHQ0NCAtMTA2dC00NCAtMTA2dC0xMDYgLTQ0dC0xMDYgNDR0LTQ0IDEwNnQ0NCAxMDZ0MTA2IDQ0ek01NTAgMzAwcTYyIDAgMTA2IC00NHQ0NCAtMTA2dC00NCAtMTA2dC0xMDYgLTQ0dC0xMDYgNDR0LTQ0IDEwNnQ0NCAxMDZ0MTA2IDQ0eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUyMzY7IiBkPSJNMTI1IDExMDBoOTUwcTEwIDAgMTcuNSAtNy41dDcuNSAtMTcuNXYtMTUwcTAgLTEwIC03LjUgLTE3LjV0LTE3LjUgLTcuNWgtOTUwcS0xMCAwIC0xNy41IDcuNXQtNy41IDE3LjV2MTUwcTAgMTAgNy41IDE3LjV0MTcuNSA3LjV6TTEyNSA3MDBoOTUwcTEwIDAgMTcuNSAtNy41dDcuNSAtMTcuNXYtMTUwcTAgLTEwIC03LjUgLTE3LjV0LTE3LjUgLTcuNWgtOTUwcS0xMCAwIC0xNy41IDcuNXQtNy41IDE3LjV2MTUwcTAgMTAgNy41IDE3LjUgdDE3LjUgNy41ek0xMjUgMzAwaDk1MHExMCAwIDE3LjUgLTcuNXQ3LjUgLTE3LjV2LTE1MHEwIC0xMCAtNy41IC0xNy41dC0xNy41IC03LjVoLTk1MHEtMTAgMCAtMTcuNSA3LjV0LTcuNSAxNy41djE1MHEwIDEwIDcuNSAxNy41dDE3LjUgNy41eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUyMzc7IiBkPSJNMzUwIDEyMDBoNTAwcTE2MiAwIDI1NiAtOTMuNXQ5NCAtMjU2LjV2LTUwMHEwIC0xNjUgLTkzLjUgLTI1Ny41dC0yNTYuNSAtOTIuNWgtNTAwcS0xNjUgMCAtMjU3LjUgOTIuNXQtOTIuNSAyNTcuNXY1MDBxMCAxNjUgOTIuNSAyNTcuNXQyNTcuNSA5Mi41ek05MDAgMTAwMGgtNjAwcS00MSAwIC03MC41IC0yOS41dC0yOS41IC03MC41di02MDBxMCAtNDEgMjkuNSAtNzAuNXQ3MC41IC0yOS41aDYwMHE0MSAwIDcwLjUgMjkuNSB0MjkuNSA3MC41djYwMHEwIDQxIC0yOS41IDcwLjV0LTcwLjUgMjkuNXpNMzUwIDkwMGg1MDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTMwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtNTAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYzMDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek00MDAgODAwdi0yMDBoNDAwdjIwMGgtNDAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUyMzg7IiBkPSJNMTUwIDExMDBoMTAwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXQtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtNTB2LTIwMGg1MHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXQtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtNTB2LTIwMGg1MHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXQtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtNTB2LTIwMGg1MHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXQtMTQuNSAtMzUuNSB0LTM1LjUgLTE0LjVoLTEwMDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41dDE0LjUgMzUuNXQzNS41IDE0LjVoNTB2MjAwaC01MHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV0MTQuNSAzNS41dDM1LjUgMTQuNWg1MHYyMDBoLTUwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXQxNC41IDM1LjV0MzUuNSAxNC41aDUwdjIwMGgtNTBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41dDE0LjUgMzUuNXQzNS41IDE0LjV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTIzOTsiIGQ9Ik02NTAgMTE4N3E4NyAtNjcgMTE4LjUgLTE1NnQwIC0xNzh0LTExOC41IC0xNTVxLTg3IDY2IC0xMTguNSAxNTV0MCAxNzh0MTE4LjUgMTU2ek0zMDAgODAwcTEyNCAwIDIxMiAtODh0ODggLTIxMnEtMTI0IDAgLTIxMiA4OHQtODggMjEyek0xMDAwIDgwMHEwIC0xMjQgLTg4IC0yMTJ0LTIxMiAtODhxMCAxMjQgODggMjEydDIxMiA4OHpNMzAwIDUwMHExMjQgMCAyMTIgLTg4dDg4IC0yMTJxLTEyNCAwIC0yMTIgODh0LTg4IDIxMnogTTEwMDAgNTAwcTAgLTEyNCAtODggLTIxMnQtMjEyIC04OHEwIDEyNCA4OCAyMTJ0MjEyIDg4ek03MDAgMTk5di0xNDRxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjV0LTM1LjUgMTQuNXQtMTQuNSAzNS41djE0MnE0MCAtNCA0MyAtNHExNyAwIDU3IDZ6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTI0MDsiIGQ9Ik03NDUgODc4bDY5IDE5cTI1IDYgNDUgLTEybDI5OCAtMjk1cTExIC0xMSAxNSAtMjYuNXQtMiAtMzAuNXEtNSAtMTQgLTE4IC0yMy41dC0yOCAtOS41aC04cTEgMCAxIC0xM3EwIC0yOSAtMiAtNTZ0LTguNSAtNjJ0LTIwIC02M3QtMzMgLTUzdC01MSAtMzl0LTcyLjUgLTE0aC0xNDZxLTE4NCAwIC0xODQgMjg4cTAgMjQgMTAgNDdxLTIwIDQgLTYyIDR0LTYzIC00cTExIC0yNCAxMSAtNDdxMCAtMjg4IC0xODQgLTI4OGgtMTQyIHEtNDggMCAtODQuNSAyMXQtNTYgNTF0LTMyIDcxLjV0LTE2IDc1dC0zLjUgNjguNXEwIDEzIDIgMTNoLTdxLTE1IDAgLTI3LjUgOS41dC0xOC41IDIzLjVxLTYgMTUgLTIgMzAuNXQxNSAyNS41bDI5OCAyOTZxMjAgMTggNDYgMTFsNzYgLTE5cTIwIC01IDMwLjUgLTIyLjV0NS41IC0zNy41dC0yMi41IC0zMXQtMzcuNSAtNWwtNTEgMTJsLTE4MiAtMTkzaDg5MWwtMTgyIDE5M2wtNDQgLTEycS0yMCAtNSAtMzcuNSA2dC0yMi41IDMxdDYgMzcuNSB0MzEgMjIuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjQxOyIgZD0iTTEyMDAgOTAwaC01MHEwIDIxIC00IDM3dC05LjUgMjYuNXQtMTggMTcuNXQtMjIgMTF0LTI4LjUgNS41dC0zMSAydC0zNyAwLjVoLTIwMHYtODUwcTAgLTIyIDI1IC0zNC41dDUwIC0xMy41bDI1IC0ydi0xMDBoLTQwMHYxMDBxNCAwIDExIDAuNXQyNCAzdDMwIDd0MjQgMTV0MTEgMjQuNXY4NTBoLTIwMHEtMjUgMCAtMzcgLTAuNXQtMzEgLTJ0LTI4LjUgLTUuNXQtMjIgLTExdC0xOCAtMTcuNXQtOS41IC0yNi41dC00IC0zN2gtNTB2MzAwIGgxMDAwdi0zMDB6TTUwMCA0NTBoLTI1cTAgMTUgLTQgMjQuNXQtOSAxNC41dC0xNyA3LjV0LTIwIDN0LTI1IDAuNWgtMTAwdi00MjVxMCAtMTEgMTIuNSAtMTcuNXQyNS41IC03LjVoMTJ2LTUwaC0yMDB2NTBxNTAgMCA1MCAyNXY0MjVoLTEwMHEtMTcgMCAtMjUgLTAuNXQtMjAgLTN0LTE3IC03LjV0LTkgLTE0LjV0LTQgLTI0LjVoLTI1djE1MGg1MDB2LTE1MHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjQyOyIgZD0iTTEwMDAgMzAwdjUwcS0yNSAwIC01NSAzMnEtMTQgMTQgLTI1IDMxdC0xNiAyN2wtNCAxMWwtMjg5IDc0N2gtNjlsLTMwMCAtNzU0cS0xOCAtMzUgLTM5IC01NnEtOSAtOSAtMjQuNSAtMTguNXQtMjYuNSAtMTQuNWwtMTEgLTV2LTUwaDI3M3Y1MHEtNDkgMCAtNzguNSAyMS41dC0xMS41IDY3LjVsNjkgMTc2aDI5M2w2MSAtMTY2cTEzIC0zNCAtMy41IC02Ni41dC01NS41IC0zMi41di01MGgzMTJ6TTQxMiA2OTFsMTM0IDM0MmwxMjEgLTM0MiBoLTI1NXpNMTEwMCAxNTB2LTEwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtMTAwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2MTAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNWgxMDAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUyNDM7IiBkPSJNNTAgMTIwMGgxMTAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0xMTAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0xMTAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXYxMTAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNNjExIDExMThoLTcwcS0xMyAwIC0xOCAtMTJsLTI5OSAtNzUzcS0xNyAtMzIgLTM1IC01MXEtMTggLTE4IC01NiAtMzRxLTEyIC01IC0xMiAtMTh2LTUwcTAgLTggNS41IC0xNHQxNC41IC02IGgyNzNxOCAwIDE0IDZ0NiAxNHY1MHEwIDggLTYgMTR0LTE0IDZxLTU1IDAgLTcxIDIzcS0xMCAxNCAwIDM5bDYzIDE2M2gyNjZsNTcgLTE1M3ExMSAtMzEgLTYgLTU1cS0xMiAtMTcgLTM2IC0xN3EtOCAwIC0xNCAtNnQtNiAtMTR2LTUwcTAgLTggNiAtMTR0MTQgLTZoMzEzcTggMCAxNCA2dDYgMTR2NTBxMCA3IC01LjUgMTN0LTEzLjUgN3EtMTcgMCAtNDIgMjVxLTI1IDI3IC00MCA2M2gtMWwtMjg4IDc0OHEtNSAxMiAtMTkgMTJ6TTYzOSA2MTEgaC0xOTdsMTAzIDI2NHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjQ0OyIgZD0iTTEyMDAgMTEwMGgtMTIwMHYxMDBoMTIwMHYtMTAwek01MCAxMDAwaDQwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtOTAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC00MDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djkwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTY1MCAxMDAwaDQwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtNDAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC00MDAgcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXY0MDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek03MDAgOTAwdi0zMDBoMzAwdjMwMGgtMzAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUyNDU7IiBkPSJNNTAgMTIwMGg0MDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTkwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtNDAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXY5MDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek02NTAgNzAwaDQwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtNDAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC00MDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djQwMCBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek03MDAgNjAwdi0zMDBoMzAwdjMwMGgtMzAwek0xMjAwIDBoLTEyMDB2MTAwaDEyMDB2LTEwMHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjQ2OyIgZD0iTTUwIDEwMDBoNDAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0zNTBoMTAwdjE1MHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjVoNDAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di0xNTBoMTAwdi0xMDBoLTEwMHYtMTUwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC00MDBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djE1MGgtMTAwdi0zNTBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTQwMCBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djgwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTcwMCA3MDB2LTMwMGgzMDB2MzAwaC0zMDB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTI0NzsiIGQ9Ik0xMDAgMGgtMTAwdjEyMDBoMTAwdi0xMjAwek0yNTAgMTEwMGg0MDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTQwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtNDAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXY0MDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41ek0zMDAgMTAwMHYtMzAwaDMwMHYzMDBoLTMwMHpNMjUwIDUwMGg5MDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTQwMCBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTkwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2NDAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjQ4OyIgZD0iTTYwMCAxMTAwaDE1MHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtNDAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0xNTB2LTEwMGg0NTBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTQwMHEwIC0yMSAtMTQuNSAtMzUuNXQtMzUuNSAtMTQuNWgtOTAwcS0yMSAwIC0zNS41IDE0LjV0LTE0LjUgMzUuNXY0MDBxMCAyMSAxNC41IDM1LjV0MzUuNSAxNC41aDM1MHYxMDBoLTE1MHEtMjEgMCAtMzUuNSAxNC41IHQtMTQuNSAzNS41djQwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjVoMTUwdjEwMGgxMDB2LTEwMHpNNDAwIDEwMDB2LTMwMGgzMDB2MzAwaC0zMDB6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTI0OTsiIGQ9Ik0xMjAwIDBoLTEwMHYxMjAwaDEwMHYtMTIwMHpNNTUwIDExMDBoNDAwcTIxIDAgMzUuNSAtMTQuNXQxNC41IC0zNS41di00MDBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTQwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2NDAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXpNNjAwIDEwMDB2LTMwMGgzMDB2MzAwaC0zMDB6TTUwIDUwMGg5MDBxMjEgMCAzNS41IC0xNC41dDE0LjUgLTM1LjV2LTQwMCBxMCAtMjEgLTE0LjUgLTM1LjV0LTM1LjUgLTE0LjVoLTkwMHEtMjEgMCAtMzUuNSAxNC41dC0xNC41IDM1LjV2NDAwcTAgMjEgMTQuNSAzNS41dDM1LjUgMTQuNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjUwOyIgZD0iTTg2NSA1NjVsLTQ5NCAtNDk0cS0yMyAtMjMgLTQxIC0yM3EtMTQgMCAtMjIgMTMuNXQtOCAzOC41djEwMDBxMCAyNSA4IDM4LjV0MjIgMTMuNXExOCAwIDQxIC0yM2w0OTQgLTQ5NHExNCAtMTQgMTQgLTM1dC0xNCAtMzV6IiAvPgo8Z2x5cGggdW5pY29kZT0iJiN4ZTI1MTsiIGQ9Ik0zMzUgNjM1bDQ5NCA0OTRxMjkgMjkgNTAgMjAuNXQyMSAtNDkuNXYtMTAwMHEwIC00MSAtMjEgLTQ5LjV0LTUwIDIwLjVsLTQ5NCA0OTRxLTE0IDE0IC0xNCAzNXQxNCAzNXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjUyOyIgZD0iTTEwMCA5MDBoMTAwMHE0MSAwIDQ5LjUgLTIxdC0yMC41IC01MGwtNDk0IC00OTRxLTE0IC0xNCAtMzUgLTE0dC0zNSAxNGwtNDk0IDQ5NHEtMjkgMjkgLTIwLjUgNTB0NDkuNSAyMXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjUzOyIgZD0iTTYzNSA4NjVsNDk0IC00OTRxMjkgLTI5IDIwLjUgLTUwdC00OS41IC0yMWgtMTAwMHEtNDEgMCAtNDkuNSAyMXQyMC41IDUwbDQ5NCA0OTRxMTQgMTQgMzUgMTR0MzUgLTE0eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUyNTQ7IiBkPSJNNzAwIDc0MXYtMTgybC02OTIgLTMyM3YyMjFsNDEzIDE5M2wtNDEzIDE5M3YyMjF6TTEyMDAgMGgtODAwdjIwMGg4MDB2LTIwMHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjU1OyIgZD0iTTEyMDAgOTAwaC0yMDB2LTEwMGgyMDB2LTEwMGgtMzAwdjMwMGgyMDB2MTAwaC0yMDB2MTAwaDMwMHYtMzAwek0wIDcwMGg1MHEwIDIxIDQgMzd0OS41IDI2LjV0MTggMTcuNXQyMiAxMXQyOC41IDUuNXQzMSAydDM3IDAuNWgxMDB2LTU1MHEwIC0yMiAtMjUgLTM0LjV0LTUwIC0xMy41bC0yNSAtMnYtMTAwaDQwMHYxMDBxLTQgMCAtMTEgMC41dC0yNCAzdC0zMCA3dC0yNCAxNXQtMTEgMjQuNXY1NTBoMTAwcTI1IDAgMzcgLTAuNXQzMSAtMiB0MjguNSAtNS41dDIyIC0xMXQxOCAtMTcuNXQ5LjUgLTI2LjV0NCAtMzdoNTB2MzAwaC04MDB2LTMwMHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjU2OyIgZD0iTTgwMCA3MDBoLTUwcTAgMjEgLTQgMzd0LTkuNSAyNi41dC0xOCAxNy41dC0yMiAxMXQtMjguNSA1LjV0LTMxIDJ0LTM3IDAuNWgtMTAwdi01NTBxMCAtMjIgMjUgLTM0LjV0NTAgLTE0LjVsMjUgLTF2LTEwMGgtNDAwdjEwMHE0IDAgMTEgMC41dDI0IDN0MzAgN3QyNCAxNXQxMSAyNC41djU1MGgtMTAwcS0yNSAwIC0zNyAtMC41dC0zMSAtMnQtMjguNSAtNS41dC0yMiAtMTF0LTE4IC0xNy41dC05LjUgLTI2LjV0LTQgLTM3aC01MHYzMDAgaDgwMHYtMzAwek0xMTAwIDIwMGgtMjAwdi0xMDBoMjAwdi0xMDBoLTMwMHYzMDBoMjAwdjEwMGgtMjAwdjEwMGgzMDB2LTMwMHoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjU3OyIgZD0iTTcwMSAxMDk4aDE2MHExNiAwIDIxIC0xMXQtNyAtMjNsLTQ2NCAtNDY0bDQ2NCAtNDY0cTEyIC0xMiA3IC0yM3QtMjEgLTExaC0xNjBxLTEzIDAgLTIzIDlsLTQ3MSA0NzFxLTcgOCAtNyAxOHQ3IDE4bDQ3MSA0NzFxMTAgOSAyMyA5eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGUyNTg7IiBkPSJNMzM5IDEwOThoMTYwcTEzIDAgMjMgLTlsNDcxIC00NzFxNyAtOCA3IC0xOHQtNyAtMThsLTQ3MSAtNDcxcS0xMCAtOSAtMjMgLTloLTE2MHEtMTYgMCAtMjEgMTF0NyAyM2w0NjQgNDY0bC00NjQgNDY0cS0xMiAxMiAtNyAyM3QyMSAxMXoiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjU5OyIgZD0iTTEwODcgODgycTExIC01IDExIC0yMXYtMTYwcTAgLTEzIC05IC0yM2wtNDcxIC00NzFxLTggLTcgLTE4IC03dC0xOCA3bC00NzEgNDcxcS05IDEwIC05IDIzdjE2MHEwIDE2IDExIDIxdDIzIC03bDQ2NCAtNDY0bDQ2NCA0NjRxMTIgMTIgMjMgN3oiIC8+CjxnbHlwaCB1bmljb2RlPSImI3hlMjYwOyIgZD0iTTYxOCA5OTNsNDcxIC00NzFxOSAtMTAgOSAtMjN2LTE2MHEwIC0xNiAtMTEgLTIxdC0yMyA3bC00NjQgNDY0bC00NjQgLTQ2NHEtMTIgLTEyIC0yMyAtN3QtMTEgMjF2MTYwcTAgMTMgOSAyM2w0NzEgNDcxcTggNyAxOCA3dDE4IC03eiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeGY4ZmY7IiBkPSJNMTAwMCAxMjAwcTAgLTEyNCAtODggLTIxMnQtMjEyIC04OHEwIDEyNCA4OCAyMTJ0MjEyIDg4ek00NTAgMTAwMGgxMDBxMjEgMCA0MCAtMTR0MjYgLTMzbDc5IC0xOTRxNSAxIDE2IDNxMzQgNiA1NCA5LjV0NjAgN3Q2NS41IDF0NjEgLTEwdDU2LjUgLTIzdDQyLjUgLTQydDI5IC02NHQ1IC05MnQtMTkuNSAtMTIxLjVxLTEgLTcgLTMgLTE5LjV0LTExIC01MHQtMjAuNSAtNzN0LTMyLjUgLTgxLjV0LTQ2LjUgLTgzdC02NCAtNzAgdC04Mi41IC01MHEtMTMgLTUgLTQyIC01dC02NS41IDIuNXQtNDcuNSAyLjVxLTE0IDAgLTQ5LjUgLTMuNXQtNjMgLTMuNXQtNDMuNSA3cS01NyAyNSAtMTA0LjUgNzguNXQtNzUgMTExLjV0LTQ2LjUgMTEydC0yNiA5MGwtNyAzNXEtMTUgNjMgLTE4IDExNXQ0LjUgODguNXQyNiA2NHQzOS41IDQzLjV0NTIgMjUuNXQ1OC41IDEzdDYyLjUgMnQ1OS41IC00LjV0NTUuNSAtOGwtMTQ3IDE5MnEtMTIgMTggLTUuNSAzMHQyNy41IDEyeiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeDFmNTExOyIgZD0iTTI1MCAxMjAwaDYwMHEyMSAwIDM1LjUgLTE0LjV0MTQuNSAtMzUuNXYtNDAwcTAgLTIxIC0xNC41IC0zNS41dC0zNS41IC0xNC41aC0xNTB2LTUwMGwtMjU1IC0xNzhxLTE5IC05IC0zMiAtMXQtMTMgMjl2NjUwaC0xNTBxLTIxIDAgLTM1LjUgMTQuNXQtMTQuNSAzNS41djQwMHEwIDIxIDE0LjUgMzUuNXQzNS41IDE0LjV6TTQwMCAxMTAwdi0xMDBoMzAwdjEwMGgtMzAweiIgLz4KPGdseXBoIHVuaWNvZGU9IiYjeDFmNmFhOyIgZD0iTTI1MCAxMjAwaDc1MHEzOSAwIDY5LjUgLTQwLjV0MzAuNSAtODQuNXYtOTMzbC03MDAgLTExN3Y5NTBsNjAwIDEyNWgtNzAwdi0xMDAwaC0xMDB2MTAyNXEwIDIzIDE1LjUgNDl0MzQuNSAyNnpNNTAwIDUyNXYtMTAwbDEwMCAyMHYxMDB6IiAvPgo8L2ZvbnQ+CjwvZGVmcz48L3N2Zz4g) format('svg')}.glyphicon{position:relative;top:1px;display:inline-block;font-family:'Glyphicons Halflings';font-style:normal;font-weight:normal;line-height:1;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}.glyphicon-asterisk:before{content:"\002a"}.glyphicon-plus:before{content:"\002b"}.glyphicon-euro:before,.glyphicon-eur:before{content:"\20ac"}.glyphicon-minus:before{content:"\2212"}.glyphicon-cloud:before{content:"\2601"}.glyphicon-envelope:before{content:"\2709"}.glyphicon-pencil:before{content:"\270f"}.glyphicon-glass:before{content:"\e001"}.glyphicon-music:before{content:"\e002"}.glyphicon-search:before{content:"\e003"}.glyphicon-heart:before{content:"\e005"}.glyphicon-star:before{content:"\e006"}.glyphicon-star-empty:before{content:"\e007"}.glyphicon-user:before{content:"\e008"}.glyphicon-film:before{content:"\e009"}.glyphicon-th-large:before{content:"\e010"}.glyphicon-th:before{content:"\e011"}.glyphicon-th-list:before{content:"\e012"}.glyphicon-ok:before{content:"\e013"}.glyphicon-remove:before{content:"\e014"}.glyphicon-zoom-in:before{content:"\e015"}.glyphicon-zoom-out:before{content:"\e016"}.glyphicon-off:before{content:"\e017"}.glyphicon-signal:before{content:"\e018"}.glyphicon-cog:before{content:"\e019"}.glyphicon-trash:before{content:"\e020"}.glyphicon-home:before{content:"\e021"}.glyphicon-file:before{content:"\e022"}.glyphicon-time:before{content:"\e023"}.glyphicon-road:before{content:"\e024"}.glyphicon-download-alt:before{content:"\e025"}.glyphicon-download:before{content:"\e026"}.glyphicon-upload:before{content:"\e027"}.glyphicon-inbox:before{content:"\e028"}.glyphicon-play-circle:before{content:"\e029"}.glyphicon-repeat:before{content:"\e030"}.glyphicon-refresh:before{content:"\e031"}.glyphicon-list-alt:before{content:"\e032"}.glyphicon-lock:before{content:"\e033"}.glyphicon-flag:before{content:"\e034"}.glyphicon-headphones:before{content:"\e035"}.glyphicon-volume-off:before{content:"\e036"}.glyphicon-volume-down:before{content:"\e037"}.glyphicon-volume-up:before{content:"\e038"}.glyphicon-qrcode:before{content:"\e039"}.glyphicon-barcode:before{content:"\e040"}.glyphicon-tag:before{content:"\e041"}.glyphicon-tags:before{content:"\e042"}.glyphicon-book:before{content:"\e043"}.glyphicon-bookmark:before{content:"\e044"}.glyphicon-print:before{content:"\e045"}.glyphicon-camera:before{content:"\e046"}.glyphicon-font:before{content:"\e047"}.glyphicon-bold:before{content:"\e048"}.glyphicon-italic:before{content:"\e049"}.glyphicon-text-height:before{content:"\e050"}.glyphicon-text-width:before{content:"\e051"}.glyphicon-align-left:before{content:"\e052"}.glyphicon-align-center:before{content:"\e053"}.glyphicon-align-right:before{content:"\e054"}.glyphicon-align-justify:before{content:"\e055"}.glyphicon-list:before{content:"\e056"}.glyphicon-indent-left:before{content:"\e057"}.glyphicon-indent-right:before{content:"\e058"}.glyphicon-facetime-video:before{content:"\e059"}.glyphicon-picture:before{content:"\e060"}.glyphicon-map-marker:before{content:"\e062"}.glyphicon-adjust:before{content:"\e063"}.glyphicon-tint:before{content:"\e064"}.glyphicon-edit:before{content:"\e065"}.glyphicon-share:before{content:"\e066"}.glyphicon-check:before{content:"\e067"}.glyphicon-move:before{content:"\e068"}.glyphicon-step-backward:before{content:"\e069"}.glyphicon-fast-backward:before{content:"\e070"}.glyphicon-backward:before{content:"\e071"}.glyphicon-play:before{content:"\e072"}.glyphicon-pause:before{content:"\e073"}.glyphicon-stop:before{content:"\e074"}.glyphicon-forward:before{content:"\e075"}.glyphicon-fast-forward:before{content:"\e076"}.glyphicon-step-forward:before{content:"\e077"}.glyphicon-eject:before{content:"\e078"}.glyphicon-chevron-left:before{content:"\e079"}.glyphicon-chevron-right:before{content:"\e080"}.glyphicon-plus-sign:before{content:"\e081"}.glyphicon-minus-sign:before{content:"\e082"}.glyphicon-remove-sign:before{content:"\e083"}.glyphicon-ok-sign:before{content:"\e084"}.glyphicon-question-sign:before{content:"\e085"}.glyphicon-info-sign:before{content:"\e086"}.glyphicon-screenshot:before{content:"\e087"}.glyphicon-remove-circle:before{content:"\e088"}.glyphicon-ok-circle:before{content:"\e089"}.glyphicon-ban-circle:before{content:"\e090"}.glyphicon-arrow-left:before{content:"\e091"}.glyphicon-arrow-right:before{content:"\e092"}.glyphicon-arrow-up:before{content:"\e093"}.glyphicon-arrow-down:before{content:"\e094"}.glyphicon-share-alt:before{content:"\e095"}.glyphicon-resize-full:before{content:"\e096"}.glyphicon-resize-small:before{content:"\e097"}.glyphicon-exclamation-sign:before{content:"\e101"}.glyphicon-gift:before{content:"\e102"}.glyphicon-leaf:before{content:"\e103"}.glyphicon-fire:before{content:"\e104"}.glyphicon-eye-open:before{content:"\e105"}.glyphicon-eye-close:before{content:"\e106"}.glyphicon-warning-sign:before{content:"\e107"}.glyphicon-plane:before{content:"\e108"}.glyphicon-calendar:before{content:"\e109"}.glyphicon-random:before{content:"\e110"}.glyphicon-comment:before{content:"\e111"}.glyphicon-magnet:before{content:"\e112"}.glyphicon-chevron-up:before{content:"\e113"}.glyphicon-chevron-down:before{content:"\e114"}.glyphicon-retweet:before{content:"\e115"}.glyphicon-shopping-cart:before{content:"\e116"}.glyphicon-folder-close:before{content:"\e117"}.glyphicon-folder-open:before{content:"\e118"}.glyphicon-resize-vertical:before{content:"\e119"}.glyphicon-resize-horizontal:before{content:"\e120"}.glyphicon-hdd:before{content:"\e121"}.glyphicon-bullhorn:before{content:"\e122"}.glyphicon-bell:before{content:"\e123"}.glyphicon-certificate:before{content:"\e124"}.glyphicon-thumbs-up:before{content:"\e125"}.glyphicon-thumbs-down:before{content:"\e126"}.glyphicon-hand-right:before{content:"\e127"}.glyphicon-hand-left:before{content:"\e128"}.glyphicon-hand-up:before{content:"\e129"}.glyphicon-hand-down:before{content:"\e130"}.glyphicon-circle-arrow-right:before{content:"\e131"}.glyphicon-circle-arrow-left:before{content:"\e132"}.glyphicon-circle-arrow-up:before{content:"\e133"}.glyphicon-circle-arrow-down:before{content:"\e134"}.glyphicon-globe:before{content:"\e135"}.glyphicon-wrench:before{content:"\e136"}.glyphicon-tasks:before{content:"\e137"}.glyphicon-filter:before{content:"\e138"}.glyphicon-briefcase:before{content:"\e139"}.glyphicon-fullscreen:before{content:"\e140"}.glyphicon-dashboard:before{content:"\e141"}.glyphicon-paperclip:before{content:"\e142"}.glyphicon-heart-empty:before{content:"\e143"}.glyphicon-link:before{content:"\e144"}.glyphicon-phone:before{content:"\e145"}.glyphicon-pushpin:before{content:"\e146"}.glyphicon-usd:before{content:"\e148"}.glyphicon-gbp:before{content:"\e149"}.glyphicon-sort:before{content:"\e150"}.glyphicon-sort-by-alphabet:before{content:"\e151"}.glyphicon-sort-by-alphabet-alt:before{content:"\e152"}.glyphicon-sort-by-order:before{content:"\e153"}.glyphicon-sort-by-order-alt:before{content:"\e154"}.glyphicon-sort-by-attributes:before{content:"\e155"}.glyphicon-sort-by-attributes-alt:before{content:"\e156"}.glyphicon-unchecked:before{content:"\e157"}.glyphicon-expand:before{content:"\e158"}.glyphicon-collapse-down:before{content:"\e159"}.glyphicon-collapse-up:before{content:"\e160"}.glyphicon-log-in:before{content:"\e161"}.glyphicon-flash:before{content:"\e162"}.glyphicon-log-out:before{content:"\e163"}.glyphicon-new-window:before{content:"\e164"}.glyphicon-record:before{content:"\e165"}.glyphicon-save:before{content:"\e166"}.glyphicon-open:before{content:"\e167"}.glyphicon-saved:before{content:"\e168"}.glyphicon-import:before{content:"\e169"}.glyphicon-export:before{content:"\e170"}.glyphicon-send:before{content:"\e171"}.glyphicon-floppy-disk:before{content:"\e172"}.glyphicon-floppy-saved:before{content:"\e173"}.glyphicon-floppy-remove:before{content:"\e174"}.glyphicon-floppy-save:before{content:"\e175"}.glyphicon-floppy-open:before{content:"\e176"}.glyphicon-credit-card:before{content:"\e177"}.glyphicon-transfer:before{content:"\e178"}.glyphicon-cutlery:before{content:"\e179"}.glyphicon-header:before{content:"\e180"}.glyphicon-compressed:before{content:"\e181"}.glyphicon-earphone:before{content:"\e182"}.glyphicon-phone-alt:before{content:"\e183"}.glyphicon-tower:before{content:"\e184"}.glyphicon-stats:before{content:"\e185"}.glyphicon-sd-video:before{content:"\e186"}.glyphicon-hd-video:before{content:"\e187"}.glyphicon-subtitles:before{content:"\e188"}.glyphicon-sound-stereo:before{content:"\e189"}.glyphicon-sound-dolby:before{content:"\e190"}.glyphicon-sound-5-1:before{content:"\e191"}.glyphicon-sound-6-1:before{content:"\e192"}.glyphicon-sound-7-1:before{content:"\e193"}.glyphicon-copyright-mark:before{content:"\e194"}.glyphicon-registration-mark:before{content:"\e195"}.glyphicon-cloud-download:before{content:"\e197"}.glyphicon-cloud-upload:before{content:"\e198"}.glyphicon-tree-conifer:before{content:"\e199"}.glyphicon-tree-deciduous:before{content:"\e200"}.glyphicon-cd:before{content:"\e201"}.glyphicon-save-file:before{content:"\e202"}.glyphicon-open-file:before{content:"\e203"}.glyphicon-level-up:before{content:"\e204"}.glyphicon-copy:before{content:"\e205"}.glyphicon-paste:before{content:"\e206"}.glyphicon-alert:before{content:"\e209"}.glyphicon-equalizer:before{content:"\e210"}.glyphicon-king:before{content:"\e211"}.glyphicon-queen:before{content:"\e212"}.glyphicon-pawn:before{content:"\e213"}.glyphicon-bishop:before{content:"\e214"}.glyphicon-knight:before{content:"\e215"}.glyphicon-baby-formula:before{content:"\e216"}.glyphicon-tent:before{content:"\26fa"}.glyphicon-blackboard:before{content:"\e218"}.glyphicon-bed:before{content:"\e219"}.glyphicon-apple:before{content:"\f8ff"}.glyphicon-erase:before{content:"\e221"}.glyphicon-hourglass:before{content:"\231b"}.glyphicon-lamp:before{content:"\e223"}.glyphicon-duplicate:before{content:"\e224"}.glyphicon-piggy-bank:before{content:"\e225"}.glyphicon-scissors:before{content:"\e226"}.glyphicon-bitcoin:before{content:"\e227"}.glyphicon-btc:before{content:"\e227"}.glyphicon-xbt:before{content:"\e227"}.glyphicon-yen:before{content:"\00a5"}.glyphicon-jpy:before{content:"\00a5"}.glyphicon-ruble:before{content:"\20bd"}.glyphicon-rub:before{content:"\20bd"}.glyphicon-scale:before{content:"\e230"}.glyphicon-ice-lolly:before{content:"\e231"}.glyphicon-ice-lolly-tasted:before{content:"\e232"}.glyphicon-education:before{content:"\e233"}.glyphicon-option-horizontal:before{content:"\e234"}.glyphicon-option-vertical:before{content:"\e235"}.glyphicon-menu-hamburger:before{content:"\e236"}.glyphicon-modal-window:before{content:"\e237"}.glyphicon-oil:before{content:"\e238"}.glyphicon-grain:before{content:"\e239"}.glyphicon-sunglasses:before{content:"\e240"}.glyphicon-text-size:before{content:"\e241"}.glyphicon-text-color:before{content:"\e242"}.glyphicon-text-background:before{content:"\e243"}.glyphicon-object-align-top:before{content:"\e244"}.glyphicon-object-align-bottom:before{content:"\e245"}.glyphicon-object-align-horizontal:before{content:"\e246"}.glyphicon-object-align-left:before{content:"\e247"}.glyphicon-object-align-vertical:before{content:"\e248"}.glyphicon-object-align-right:before{content:"\e249"}.glyphicon-triangle-right:before{content:"\e250"}.glyphicon-triangle-left:before{content:"\e251"}.glyphicon-triangle-bottom:before{content:"\e252"}.glyphicon-triangle-top:before{content:"\e253"}.glyphicon-console:before{content:"\e254"}.glyphicon-superscript:before{content:"\e255"}.glyphicon-subscript:before{content:"\e256"}.glyphicon-menu-left:before{content:"\e257"}.glyphicon-menu-right:before{content:"\e258"}.glyphicon-menu-down:before{content:"\e259"}.glyphicon-menu-up:before{content:"\e260"}*{-webkit-box-sizing:border-box;-moz-box-sizing:border-box;box-sizing:border-box}*:before,*:after{-webkit-box-sizing:border-box;-moz-box-sizing:border-box;box-sizing:border-box}html{font-size:10px;-webkit-tap-highlight-color:rgba(0,0,0,0)}body{font-family:Georgia,"Times New Roman",Times,serif;font-size:16px;line-height:1.42857143;color:#333333;background-color:#ffffff}input,button,select,textarea{font-family:inherit;font-size:inherit;line-height:inherit}a{color:#4582ec;text-decoration:none}a:hover,a:focus{color:#134fb8;text-decoration:underline}a:focus{outline:thin dotted;outline:5px auto -webkit-focus-ring-color;outline-offset:-2px}figure{margin:0}img{vertical-align:middle}.img-responsive,.thumbnail>img,.thumbnail a>img,.carousel-inner>.item>img,.carousel-inner>.item>a>img{display:block;max-width:100%;height:auto}.img-rounded{border-radius:6px}.img-thumbnail{padding:4px;line-height:1.42857143;background-color:#ffffff;border:1px solid #dddddd;border-radius:4px;-webkit-transition:all .2s ease-in-out;-o-transition:all .2s ease-in-out;transition:all .2s ease-in-out;display:inline-block;max-width:100%;height:auto}.img-circle{border-radius:50%}hr{margin-top:22px;margin-bottom:22px;border:0;border-top:1px solid #eeeeee}.sr-only{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0, 0, 0, 0);border:0}.sr-only-focusable:active,.sr-only-focusable:focus{position:static;width:auto;height:auto;margin:0;overflow:visible;clip:auto}[role="button"]{cursor:pointer}h1,h2,h3,h4,h5,h6,.h1,.h2,.h3,.h4,.h5,.h6{font-family:"Georgia";font-weight:bold;line-height:1.1;color:inherit}h1 small,h2 small,h3 small,h4 small,h5 small,h6 small,.h1 small,.h2 small,.h3 small,.h4 small,.h5 small,.h6 small,h1 .small,h2 .small,h3 .small,h4 .small,h5 .small,h6 .small,.h1 .small,.h2 .small,.h3 .small,.h4 .small,.h5 .small,.h6 .small{font-weight:normal;line-height:1;color:#b3b3b3}h1,.h1,h2,.h2,h3,.h3{margin-top:22px;margin-bottom:11px}h1 small,.h1 small,h2 small,.h2 small,h3 small,.h3 small,h1 .small,.h1 .small,h2 .small,.h2 .small,h3 .small,.h3 .small{font-size:65%}h4,.h4,h5,.h5,h6,.h6{margin-top:11px;margin-bottom:11px}h4 small,.h4 small,h5 small,.h5 small,h6 small,.h6 small,h4 .small,.h4 .small,h5 .small,.h5 .small,h6 .small,.h6 .small{font-size:75%}h1,.h1{font-size:41px}h2,.h2{font-size:34px}h3,.h3{font-size:28px}h4,.h4{font-size:20px}h5,.h5{font-size:16px}h6,.h6{font-size:14px}p{margin:0 0 11px}.lead{margin-bottom:22px;font-size:18px;font-weight:300;line-height:1.4}@media (min-width:768px){.lead{font-size:24px}}small,.small{font-size:87%}mark,.mark{background-color:#fcf8e3;padding:.2em}.text-left{text-align:left}.text-right{text-align:right}.text-center{text-align:center}.text-justify{text-align:justify}.text-nowrap{white-space:nowrap}.text-lowercase{text-transform:lowercase}.text-uppercase{text-transform:uppercase}.text-capitalize{text-transform:capitalize}.text-muted{color:#b3b3b3}.text-primary{color:#4582ec}a.text-primary:hover,a.text-primary:focus{color:#1863e6}.text-success{color:#3fad46}a.text-success:hover,a.text-success:focus{color:#318837}.text-info{color:#5bc0de}a.text-info:hover,a.text-info:focus{color:#31b0d5}.text-warning{color:#f0ad4e}a.text-warning:hover,a.text-warning:focus{color:#ec971f}.text-danger{color:#d9534f}a.text-danger:hover,a.text-danger:focus{color:#c9302c}.bg-primary{color:#fff;background-color:#4582ec}a.bg-primary:hover,a.bg-primary:focus{background-color:#1863e6}.bg-success{background-color:#dff0d8}a.bg-success:hover,a.bg-success:focus{background-color:#c1e2b3}.bg-info{background-color:#d9edf7}a.bg-info:hover,a.bg-info:focus{background-color:#afd9ee}.bg-warning{background-color:#fcf8e3}a.bg-warning:hover,a.bg-warning:focus{background-color:#f7ecb5}.bg-danger{background-color:#f2dede}a.bg-danger:hover,a.bg-danger:focus{background-color:#e4b9b9}.page-header{padding-bottom:10px;margin:44px 0 22px;border-bottom:1px solid #dddddd}ul,ol{margin-top:0;margin-bottom:11px}ul ul,ol ul,ul ol,ol ol{margin-bottom:0}.list-unstyled{padding-left:0;list-style:none}.list-inline{padding-left:0;list-style:none;margin-left:-5px}.list-inline>li{display:inline-block;padding-left:5px;padding-right:5px}dl{margin-top:0;margin-bottom:22px}dt,dd{line-height:1.42857143}dt{font-weight:bold}dd{margin-left:0}@media (min-width:768px){.dl-horizontal dt{float:left;width:160px;clear:left;text-align:right;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.dl-horizontal dd{margin-left:180px}}abbr[title],abbr[data-original-title]{cursor:help;border-bottom:1px dotted #b3b3b3}.initialism{font-size:90%;text-transform:uppercase}blockquote{padding:11px 22px;margin:0 0 22px;font-size:20px;border-left:5px solid #4582ec}blockquote p:last-child,blockquote ul:last-child,blockquote ol:last-child{margin-bottom:0}blockquote footer,blockquote small,blockquote .small{display:block;font-size:80%;line-height:1.42857143;color:#333333}blockquote footer:before,blockquote small:before,blockquote .small:before{content:'\2014 \00A0'}.blockquote-reverse,blockquote.pull-right{padding-right:15px;padding-left:0;border-right:5px solid #4582ec;border-left:0;text-align:right}.blockquote-reverse footer:before,blockquote.pull-right footer:before,.blockquote-reverse small:before,blockquote.pull-right small:before,.blockquote-reverse .small:before,blockquote.pull-right .small:before{content:''}.blockquote-reverse footer:after,blockquote.pull-right footer:after,.blockquote-reverse small:after,blockquote.pull-right small:after,.blockquote-reverse .small:after,blockquote.pull-right .small:after{content:'\00A0 \2014'}address{margin-bottom:22px;font-style:normal;line-height:1.42857143}code,kbd,pre,samp{font-family:monospace}code{padding:2px 4px;font-size:90%;color:#c7254e;background-color:#f9f2f4;border-radius:4px}kbd{padding:2px 4px;font-size:90%;color:#ffffff;background-color:#333333;border-radius:3px;-webkit-box-shadow:inset 0 -1px 0 rgba(0,0,0,0.25);box-shadow:inset 0 -1px 0 rgba(0,0,0,0.25)}kbd kbd{padding:0;font-size:100%;font-weight:bold;-webkit-box-shadow:none;box-shadow:none}pre{display:block;padding:10.5px;margin:0 0 11px;font-size:15px;line-height:1.42857143;word-break:break-all;word-wrap:break-word;color:#333333;background-color:#f5f5f5;border:1px solid #cccccc;border-radius:4px}pre code{padding:0;font-size:inherit;color:inherit;white-space:pre-wrap;background-color:transparent;border-radius:0}.pre-scrollable{max-height:340px;overflow-y:scroll}.container{margin-right:auto;margin-left:auto;padding-left:15px;padding-right:15px}@media (min-width:768px){.container{width:750px}}@media (min-width:992px){.container{width:970px}}@media (min-width:1200px){.container{width:1170px}}.container-fluid{margin-right:auto;margin-left:auto;padding-left:15px;padding-right:15px}.row{margin-left:-15px;margin-right:-15px}.col-xs-1,.col-sm-1,.col-md-1,.col-lg-1,.col-xs-2,.col-sm-2,.col-md-2,.col-lg-2,.col-xs-3,.col-sm-3,.col-md-3,.col-lg-3,.col-xs-4,.col-sm-4,.col-md-4,.col-lg-4,.col-xs-5,.col-sm-5,.col-md-5,.col-lg-5,.col-xs-6,.col-sm-6,.col-md-6,.col-lg-6,.col-xs-7,.col-sm-7,.col-md-7,.col-lg-7,.col-xs-8,.col-sm-8,.col-md-8,.col-lg-8,.col-xs-9,.col-sm-9,.col-md-9,.col-lg-9,.col-xs-10,.col-sm-10,.col-md-10,.col-lg-10,.col-xs-11,.col-sm-11,.col-md-11,.col-lg-11,.col-xs-12,.col-sm-12,.col-md-12,.col-lg-12{position:relative;min-height:1px;padding-left:15px;padding-right:15px}.col-xs-1,.col-xs-2,.col-xs-3,.col-xs-4,.col-xs-5,.col-xs-6,.col-xs-7,.col-xs-8,.col-xs-9,.col-xs-10,.col-xs-11,.col-xs-12{float:left}.col-xs-12{width:100%}.col-xs-11{width:91.66666667%}.col-xs-10{width:83.33333333%}.col-xs-9{width:75%}.col-xs-8{width:66.66666667%}.col-xs-7{width:58.33333333%}.col-xs-6{width:50%}.col-xs-5{width:41.66666667%}.col-xs-4{width:33.33333333%}.col-xs-3{width:25%}.col-xs-2{width:16.66666667%}.col-xs-1{width:8.33333333%}.col-xs-pull-12{right:100%}.col-xs-pull-11{right:91.66666667%}.col-xs-pull-10{right:83.33333333%}.col-xs-pull-9{right:75%}.col-xs-pull-8{right:66.66666667%}.col-xs-pull-7{right:58.33333333%}.col-xs-pull-6{right:50%}.col-xs-pull-5{right:41.66666667%}.col-xs-pull-4{right:33.33333333%}.col-xs-pull-3{right:25%}.col-xs-pull-2{right:16.66666667%}.col-xs-pull-1{right:8.33333333%}.col-xs-pull-0{right:auto}.col-xs-push-12{left:100%}.col-xs-push-11{left:91.66666667%}.col-xs-push-10{left:83.33333333%}.col-xs-push-9{left:75%}.col-xs-push-8{left:66.66666667%}.col-xs-push-7{left:58.33333333%}.col-xs-push-6{left:50%}.col-xs-push-5{left:41.66666667%}.col-xs-push-4{left:33.33333333%}.col-xs-push-3{left:25%}.col-xs-push-2{left:16.66666667%}.col-xs-push-1{left:8.33333333%}.col-xs-push-0{left:auto}.col-xs-offset-12{margin-left:100%}.col-xs-offset-11{margin-left:91.66666667%}.col-xs-offset-10{margin-left:83.33333333%}.col-xs-offset-9{margin-left:75%}.col-xs-offset-8{margin-left:66.66666667%}.col-xs-offset-7{margin-left:58.33333333%}.col-xs-offset-6{margin-left:50%}.col-xs-offset-5{margin-left:41.66666667%}.col-xs-offset-4{margin-left:33.33333333%}.col-xs-offset-3{margin-left:25%}.col-xs-offset-2{margin-left:16.66666667%}.col-xs-offset-1{margin-left:8.33333333%}.col-xs-offset-0{margin-left:0%}@media (min-width:768px){.col-sm-1,.col-sm-2,.col-sm-3,.col-sm-4,.col-sm-5,.col-sm-6,.col-sm-7,.col-sm-8,.col-sm-9,.col-sm-10,.col-sm-11,.col-sm-12{float:left}.col-sm-12{width:100%}.col-sm-11{width:91.66666667%}.col-sm-10{width:83.33333333%}.col-sm-9{width:75%}.col-sm-8{width:66.66666667%}.col-sm-7{width:58.33333333%}.col-sm-6{width:50%}.col-sm-5{width:41.66666667%}.col-sm-4{width:33.33333333%}.col-sm-3{width:25%}.col-sm-2{width:16.66666667%}.col-sm-1{width:8.33333333%}.col-sm-pull-12{right:100%}.col-sm-pull-11{right:91.66666667%}.col-sm-pull-10{right:83.33333333%}.col-sm-pull-9{right:75%}.col-sm-pull-8{right:66.66666667%}.col-sm-pull-7{right:58.33333333%}.col-sm-pull-6{right:50%}.col-sm-pull-5{right:41.66666667%}.col-sm-pull-4{right:33.33333333%}.col-sm-pull-3{right:25%}.col-sm-pull-2{right:16.66666667%}.col-sm-pull-1{right:8.33333333%}.col-sm-pull-0{right:auto}.col-sm-push-12{left:100%}.col-sm-push-11{left:91.66666667%}.col-sm-push-10{left:83.33333333%}.col-sm-push-9{left:75%}.col-sm-push-8{left:66.66666667%}.col-sm-push-7{left:58.33333333%}.col-sm-push-6{left:50%}.col-sm-push-5{left:41.66666667%}.col-sm-push-4{left:33.33333333%}.col-sm-push-3{left:25%}.col-sm-push-2{left:16.66666667%}.col-sm-push-1{left:8.33333333%}.col-sm-push-0{left:auto}.col-sm-offset-12{margin-left:100%}.col-sm-offset-11{margin-left:91.66666667%}.col-sm-offset-10{margin-left:83.33333333%}.col-sm-offset-9{margin-left:75%}.col-sm-offset-8{margin-left:66.66666667%}.col-sm-offset-7{margin-left:58.33333333%}.col-sm-offset-6{margin-left:50%}.col-sm-offset-5{margin-left:41.66666667%}.col-sm-offset-4{margin-left:33.33333333%}.col-sm-offset-3{margin-left:25%}.col-sm-offset-2{margin-left:16.66666667%}.col-sm-offset-1{margin-left:8.33333333%}.col-sm-offset-0{margin-left:0%}}@media (min-width:992px){.col-md-1,.col-md-2,.col-md-3,.col-md-4,.col-md-5,.col-md-6,.col-md-7,.col-md-8,.col-md-9,.col-md-10,.col-md-11,.col-md-12{float:left}.col-md-12{width:100%}.col-md-11{width:91.66666667%}.col-md-10{width:83.33333333%}.col-md-9{width:75%}.col-md-8{width:66.66666667%}.col-md-7{width:58.33333333%}.col-md-6{width:50%}.col-md-5{width:41.66666667%}.col-md-4{width:33.33333333%}.col-md-3{width:25%}.col-md-2{width:16.66666667%}.col-md-1{width:8.33333333%}.col-md-pull-12{right:100%}.col-md-pull-11{right:91.66666667%}.col-md-pull-10{right:83.33333333%}.col-md-pull-9{right:75%}.col-md-pull-8{right:66.66666667%}.col-md-pull-7{right:58.33333333%}.col-md-pull-6{right:50%}.col-md-pull-5{right:41.66666667%}.col-md-pull-4{right:33.33333333%}.col-md-pull-3{right:25%}.col-md-pull-2{right:16.66666667%}.col-md-pull-1{right:8.33333333%}.col-md-pull-0{right:auto}.col-md-push-12{left:100%}.col-md-push-11{left:91.66666667%}.col-md-push-10{left:83.33333333%}.col-md-push-9{left:75%}.col-md-push-8{left:66.66666667%}.col-md-push-7{left:58.33333333%}.col-md-push-6{left:50%}.col-md-push-5{left:41.66666667%}.col-md-push-4{left:33.33333333%}.col-md-push-3{left:25%}.col-md-push-2{left:16.66666667%}.col-md-push-1{left:8.33333333%}.col-md-push-0{left:auto}.col-md-offset-12{margin-left:100%}.col-md-offset-11{margin-left:91.66666667%}.col-md-offset-10{margin-left:83.33333333%}.col-md-offset-9{margin-left:75%}.col-md-offset-8{margin-left:66.66666667%}.col-md-offset-7{margin-left:58.33333333%}.col-md-offset-6{margin-left:50%}.col-md-offset-5{margin-left:41.66666667%}.col-md-offset-4{margin-left:33.33333333%}.col-md-offset-3{margin-left:25%}.col-md-offset-2{margin-left:16.66666667%}.col-md-offset-1{margin-left:8.33333333%}.col-md-offset-0{margin-left:0%}}@media (min-width:1200px){.col-lg-1,.col-lg-2,.col-lg-3,.col-lg-4,.col-lg-5,.col-lg-6,.col-lg-7,.col-lg-8,.col-lg-9,.col-lg-10,.col-lg-11,.col-lg-12{float:left}.col-lg-12{width:100%}.col-lg-11{width:91.66666667%}.col-lg-10{width:83.33333333%}.col-lg-9{width:75%}.col-lg-8{width:66.66666667%}.col-lg-7{width:58.33333333%}.col-lg-6{width:50%}.col-lg-5{width:41.66666667%}.col-lg-4{width:33.33333333%}.col-lg-3{width:25%}.col-lg-2{width:16.66666667%}.col-lg-1{width:8.33333333%}.col-lg-pull-12{right:100%}.col-lg-pull-11{right:91.66666667%}.col-lg-pull-10{right:83.33333333%}.col-lg-pull-9{right:75%}.col-lg-pull-8{right:66.66666667%}.col-lg-pull-7{right:58.33333333%}.col-lg-pull-6{right:50%}.col-lg-pull-5{right:41.66666667%}.col-lg-pull-4{right:33.33333333%}.col-lg-pull-3{right:25%}.col-lg-pull-2{right:16.66666667%}.col-lg-pull-1{right:8.33333333%}.col-lg-pull-0{right:auto}.col-lg-push-12{left:100%}.col-lg-push-11{left:91.66666667%}.col-lg-push-10{left:83.33333333%}.col-lg-push-9{left:75%}.col-lg-push-8{left:66.66666667%}.col-lg-push-7{left:58.33333333%}.col-lg-push-6{left:50%}.col-lg-push-5{left:41.66666667%}.col-lg-push-4{left:33.33333333%}.col-lg-push-3{left:25%}.col-lg-push-2{left:16.66666667%}.col-lg-push-1{left:8.33333333%}.col-lg-push-0{left:auto}.col-lg-offset-12{margin-left:100%}.col-lg-offset-11{margin-left:91.66666667%}.col-lg-offset-10{margin-left:83.33333333%}.col-lg-offset-9{margin-left:75%}.col-lg-offset-8{margin-left:66.66666667%}.col-lg-offset-7{margin-left:58.33333333%}.col-lg-offset-6{margin-left:50%}.col-lg-offset-5{margin-left:41.66666667%}.col-lg-offset-4{margin-left:33.33333333%}.col-lg-offset-3{margin-left:25%}.col-lg-offset-2{margin-left:16.66666667%}.col-lg-offset-1{margin-left:8.33333333%}.col-lg-offset-0{margin-left:0%}}table{background-color:transparent}caption{padding-top:8px;padding-bottom:8px;color:#b3b3b3;text-align:left}th{}.table{width:100%;max-width:100%;margin-bottom:22px}.table>thead>tr>th,.table>tbody>tr>th,.table>tfoot>tr>th,.table>thead>tr>td,.table>tbody>tr>td,.table>tfoot>tr>td{padding:8px;line-height:1.42857143;vertical-align:top;border-top:1px solid #dddddd}.table>thead>tr>th{vertical-align:bottom;border-bottom:2px solid #dddddd}.table>caption+thead>tr:first-child>th,.table>colgroup+thead>tr:first-child>th,.table>thead:first-child>tr:first-child>th,.table>caption+thead>tr:first-child>td,.table>colgroup+thead>tr:first-child>td,.table>thead:first-child>tr:first-child>td{border-top:0}.table>tbody+tbody{border-top:2px solid #dddddd}.table .table{background-color:#ffffff}.table-condensed>thead>tr>th,.table-condensed>tbody>tr>th,.table-condensed>tfoot>tr>th,.table-condensed>thead>tr>td,.table-condensed>tbody>tr>td,.table-condensed>tfoot>tr>td{padding:5px}.table-bordered{border:1px solid #dddddd}.table-bordered>thead>tr>th,.table-bordered>tbody>tr>th,.table-bordered>tfoot>tr>th,.table-bordered>thead>tr>td,.table-bordered>tbody>tr>td,.table-bordered>tfoot>tr>td{border:1px solid #dddddd}.table-bordered>thead>tr>th,.table-bordered>thead>tr>td{border-bottom-width:2px}.table-striped>tbody>tr:nth-of-type(odd){background-color:#f9f9f9}.table-hover>tbody>tr:hover{background-color:#f5f5f5}table col[class*="col-"]{position:static;float:none;display:table-column}table td[class*="col-"],table th[class*="col-"]{position:static;float:none;display:table-cell}.table>thead>tr>td.active,.table>tbody>tr>td.active,.table>tfoot>tr>td.active,.table>thead>tr>th.active,.table>tbody>tr>th.active,.table>tfoot>tr>th.active,.table>thead>tr.active>td,.table>tbody>tr.active>td,.table>tfoot>tr.active>td,.table>thead>tr.active>th,.table>tbody>tr.active>th,.table>tfoot>tr.active>th{background-color:#f5f5f5}.table-hover>tbody>tr>td.active:hover,.table-hover>tbody>tr>th.active:hover,.table-hover>tbody>tr.active:hover>td,.table-hover>tbody>tr:hover>.active,.table-hover>tbody>tr.active:hover>th{background-color:#e8e8e8}.table>thead>tr>td.success,.table>tbody>tr>td.success,.table>tfoot>tr>td.success,.table>thead>tr>th.success,.table>tbody>tr>th.success,.table>tfoot>tr>th.success,.table>thead>tr.success>td,.table>tbody>tr.success>td,.table>tfoot>tr.success>td,.table>thead>tr.success>th,.table>tbody>tr.success>th,.table>tfoot>tr.success>th{background-color:#dff0d8}.table-hover>tbody>tr>td.success:hover,.table-hover>tbody>tr>th.success:hover,.table-hover>tbody>tr.success:hover>td,.table-hover>tbody>tr:hover>.success,.table-hover>tbody>tr.success:hover>th{background-color:#d0e9c6}.table>thead>tr>td.info,.table>tbody>tr>td.info,.table>tfoot>tr>td.info,.table>thead>tr>th.info,.table>tbody>tr>th.info,.table>tfoot>tr>th.info,.table>thead>tr.info>td,.table>tbody>tr.info>td,.table>tfoot>tr.info>td,.table>thead>tr.info>th,.table>tbody>tr.info>th,.table>tfoot>tr.info>th{background-color:#d9edf7}.table-hover>tbody>tr>td.info:hover,.table-hover>tbody>tr>th.info:hover,.table-hover>tbody>tr.info:hover>td,.table-hover>tbody>tr:hover>.info,.table-hover>tbody>tr.info:hover>th{background-color:#c4e3f3}.table>thead>tr>td.warning,.table>tbody>tr>td.warning,.table>tfoot>tr>td.warning,.table>thead>tr>th.warning,.table>tbody>tr>th.warning,.table>tfoot>tr>th.warning,.table>thead>tr.warning>td,.table>tbody>tr.warning>td,.table>tfoot>tr.warning>td,.table>thead>tr.warning>th,.table>tbody>tr.warning>th,.table>tfoot>tr.warning>th{background-color:#fcf8e3}.table-hover>tbody>tr>td.warning:hover,.table-hover>tbody>tr>th.warning:hover,.table-hover>tbody>tr.warning:hover>td,.table-hover>tbody>tr:hover>.warning,.table-hover>tbody>tr.warning:hover>th{background-color:#faf2cc}.table>thead>tr>td.danger,.table>tbody>tr>td.danger,.table>tfoot>tr>td.danger,.table>thead>tr>th.danger,.table>tbody>tr>th.danger,.table>tfoot>tr>th.danger,.table>thead>tr.danger>td,.table>tbody>tr.danger>td,.table>tfoot>tr.danger>td,.table>thead>tr.danger>th,.table>tbody>tr.danger>th,.table>tfoot>tr.danger>th{background-color:#f2dede}.table-hover>tbody>tr>td.danger:hover,.table-hover>tbody>tr>th.danger:hover,.table-hover>tbody>tr.danger:hover>td,.table-hover>tbody>tr:hover>.danger,.table-hover>tbody>tr.danger:hover>th{background-color:#ebcccc}.table-responsive{overflow-x:auto;min-height:0.01%}@media screen and (max-width:767px){.table-responsive{width:100%;margin-bottom:16.5px;overflow-y:hidden;-ms-overflow-style:-ms-autohiding-scrollbar;border:1px solid #dddddd}.table-responsive>.table{margin-bottom:0}.table-responsive>.table>thead>tr>th,.table-responsive>.table>tbody>tr>th,.table-responsive>.table>tfoot>tr>th,.table-responsive>.table>thead>tr>td,.table-responsive>.table>tbody>tr>td,.table-responsive>.table>tfoot>tr>td{white-space:nowrap}.table-responsive>.table-bordered{border:0}.table-responsive>.table-bordered>thead>tr>th:first-child,.table-responsive>.table-bordered>tbody>tr>th:first-child,.table-responsive>.table-bordered>tfoot>tr>th:first-child,.table-responsive>.table-bordered>thead>tr>td:first-child,.table-responsive>.table-bordered>tbody>tr>td:first-child,.table-responsive>.table-bordered>tfoot>tr>td:first-child{border-left:0}.table-responsive>.table-bordered>thead>tr>th:last-child,.table-responsive>.table-bordered>tbody>tr>th:last-child,.table-responsive>.table-bordered>tfoot>tr>th:last-child,.table-responsive>.table-bordered>thead>tr>td:last-child,.table-responsive>.table-bordered>tbody>tr>td:last-child,.table-responsive>.table-bordered>tfoot>tr>td:last-child{border-right:0}.table-responsive>.table-bordered>tbody>tr:last-child>th,.table-responsive>.table-bordered>tfoot>tr:last-child>th,.table-responsive>.table-bordered>tbody>tr:last-child>td,.table-responsive>.table-bordered>tfoot>tr:last-child>td{border-bottom:0}}fieldset{padding:0;margin:0;border:0;min-width:0}legend{display:block;width:100%;padding:0;margin-bottom:22px;font-size:24px;line-height:inherit;color:#333333;border:0;border-bottom:1px solid #e5e5e5}label{display:inline-block;max-width:100%;margin-bottom:5px;font-weight:bold}input[type="search"]{-webkit-box-sizing:border-box;-moz-box-sizing:border-box;box-sizing:border-box}input[type="radio"],input[type="checkbox"]{margin:4px 0 0;margin-top:1px \9;line-height:normal}input[type="file"]{display:block}input[type="range"]{display:block;width:100%}select[multiple],select[size]{height:auto}input[type="file"]:focus,input[type="radio"]:focus,input[type="checkbox"]:focus{outline:thin dotted;outline:5px auto -webkit-focus-ring-color;outline-offset:-2px}output{display:block;padding-top:9px;font-size:16px;line-height:1.42857143;color:#333333}.form-control{display:block;width:100%;height:40px;padding:8px 12px;font-size:16px;line-height:1.42857143;color:#333333;background-color:#ffffff;background-image:none;border:1px solid #dddddd;border-radius:4px;-webkit-box-shadow:inset 0 1px 1px rgba(0,0,0,0.075);box-shadow:inset 0 1px 1px rgba(0,0,0,0.075);-webkit-transition:border-color ease-in-out .15s,-webkit-box-shadow ease-in-out .15s;-o-transition:border-color ease-in-out .15s,box-shadow ease-in-out .15s;transition:border-color ease-in-out .15s,box-shadow ease-in-out .15s}.form-control:focus{border-color:#66afe9;outline:0;-webkit-box-shadow:inset 0 1px 1px rgba(0,0,0,0.075),0 0 8px rgba(102,175,233,0.6);box-shadow:inset 0 1px 1px rgba(0,0,0,0.075),0 0 8px rgba(102,175,233,0.6)}.form-control::-moz-placeholder{color:#b3b3b3;opacity:1}.form-control:-ms-input-placeholder{color:#b3b3b3}.form-control::-webkit-input-placeholder{color:#b3b3b3}.form-control::-ms-expand{border:0;background-color:transparent}.form-control[disabled],.form-control[readonly],fieldset[disabled] .form-control{background-color:#eeeeee;opacity:1}.form-control[disabled],fieldset[disabled] .form-control{cursor:not-allowed}textarea.form-control{height:auto}input[type="search"]{-webkit-appearance:none}@media screen and (-webkit-min-device-pixel-ratio:0){input[type="date"].form-control,input[type="time"].form-control,input[type="datetime-local"].form-control,input[type="month"].form-control{line-height:40px}input[type="date"].input-sm,input[type="time"].input-sm,input[type="datetime-local"].input-sm,input[type="month"].input-sm,.input-group-sm input[type="date"],.input-group-sm input[type="time"],.input-group-sm input[type="datetime-local"],.input-group-sm input[type="month"]{line-height:33px}input[type="date"].input-lg,input[type="time"].input-lg,input[type="datetime-local"].input-lg,input[type="month"].input-lg,.input-group-lg input[type="date"],.input-group-lg input[type="time"],.input-group-lg input[type="datetime-local"],.input-group-lg input[type="month"]{line-height:57px}}.form-group{margin-bottom:15px}.radio,.checkbox{position:relative;display:block;margin-top:10px;margin-bottom:10px}.radio label,.checkbox label{min-height:22px;padding-left:20px;margin-bottom:0;font-weight:normal;cursor:pointer}.radio input[type="radio"],.radio-inline input[type="radio"],.checkbox input[type="checkbox"],.checkbox-inline input[type="checkbox"]{position:absolute;margin-left:-20px;margin-top:4px \9}.radio+.radio,.checkbox+.checkbox{margin-top:-5px}.radio-inline,.checkbox-inline{position:relative;display:inline-block;padding-left:20px;margin-bottom:0;vertical-align:middle;font-weight:normal;cursor:pointer}.radio-inline+.radio-inline,.checkbox-inline+.checkbox-inline{margin-top:0;margin-left:10px}input[type="radio"][disabled],input[type="checkbox"][disabled],input[type="radio"].disabled,input[type="checkbox"].disabled,fieldset[disabled] input[type="radio"],fieldset[disabled] input[type="checkbox"]{cursor:not-allowed}.radio-inline.disabled,.checkbox-inline.disabled,fieldset[disabled] .radio-inline,fieldset[disabled] .checkbox-inline{cursor:not-allowed}.radio.disabled label,.checkbox.disabled label,fieldset[disabled] .radio label,fieldset[disabled] .checkbox label{cursor:not-allowed}.form-control-static{padding-top:9px;padding-bottom:9px;margin-bottom:0;min-height:38px}.form-control-static.input-lg,.form-control-static.input-sm{padding-left:0;padding-right:0}.input-sm{height:33px;padding:5px 10px;font-size:14px;line-height:1.5;border-radius:3px}select.input-sm{height:33px;line-height:33px}textarea.input-sm,select[multiple].input-sm{height:auto}.form-group-sm .form-control{height:33px;padding:5px 10px;font-size:14px;line-height:1.5;border-radius:3px}.form-group-sm select.form-control{height:33px;line-height:33px}.form-group-sm textarea.form-control,.form-group-sm select[multiple].form-control{height:auto}.form-group-sm .form-control-static{height:33px;min-height:36px;padding:6px 10px;font-size:14px;line-height:1.5}.input-lg{height:57px;padding:14px 16px;font-size:20px;line-height:1.3333333;border-radius:6px}select.input-lg{height:57px;line-height:57px}textarea.input-lg,select[multiple].input-lg{height:auto}.form-group-lg .form-control{height:57px;padding:14px 16px;font-size:20px;line-height:1.3333333;border-radius:6px}.form-group-lg select.form-control{height:57px;line-height:57px}.form-group-lg textarea.form-control,.form-group-lg select[multiple].form-control{height:auto}.form-group-lg .form-control-static{height:57px;min-height:42px;padding:15px 16px;font-size:20px;line-height:1.3333333}.has-feedback{position:relative}.has-feedback .form-control{padding-right:50px}.form-control-feedback{position:absolute;top:0;right:0;z-index:2;display:block;width:40px;height:40px;line-height:40px;text-align:center;pointer-events:none}.input-lg+.form-control-feedback,.input-group-lg+.form-control-feedback,.form-group-lg .form-control+.form-control-feedback{width:57px;height:57px;line-height:57px}.input-sm+.form-control-feedback,.input-group-sm+.form-control-feedback,.form-group-sm .form-control+.form-control-feedback{width:33px;height:33px;line-height:33px}.has-success .help-block,.has-success .control-label,.has-success .radio,.has-success .checkbox,.has-success .radio-inline,.has-success .checkbox-inline,.has-success.radio label,.has-success.checkbox label,.has-success.radio-inline label,.has-success.checkbox-inline label{color:#3fad46}.has-success .form-control{border-color:#3fad46;-webkit-box-shadow:inset 0 1px 1px rgba(0,0,0,0.075);box-shadow:inset 0 1px 1px rgba(0,0,0,0.075)}.has-success .form-control:focus{border-color:#318837;-webkit-box-shadow:inset 0 1px 1px rgba(0,0,0,0.075),0 0 6px #81d186;box-shadow:inset 0 1px 1px rgba(0,0,0,0.075),0 0 6px #81d186}.has-success .input-group-addon{color:#3fad46;border-color:#3fad46;background-color:#dff0d8}.has-success .form-control-feedback{color:#3fad46}.has-warning .help-block,.has-warning .control-label,.has-warning .radio,.has-warning .checkbox,.has-warning .radio-inline,.has-warning .checkbox-inline,.has-warning.radio label,.has-warning.checkbox label,.has-warning.radio-inline label,.has-warning.checkbox-inline label{color:#f0ad4e}.has-warning .form-control{border-color:#f0ad4e;-webkit-box-shadow:inset 0 1px 1px rgba(0,0,0,0.075);box-shadow:inset 0 1px 1px rgba(0,0,0,0.075)}.has-warning .form-control:focus{border-color:#ec971f;-webkit-box-shadow:inset 0 1px 1px rgba(0,0,0,0.075),0 0 6px #f8d9ac;box-shadow:inset 0 1px 1px rgba(0,0,0,0.075),0 0 6px #f8d9ac}.has-warning .input-group-addon{color:#f0ad4e;border-color:#f0ad4e;background-color:#fcf8e3}.has-warning .form-control-feedback{color:#f0ad4e}.has-error .help-block,.has-error .control-label,.has-error .radio,.has-error .checkbox,.has-error .radio-inline,.has-error .checkbox-inline,.has-error.radio label,.has-error.checkbox label,.has-error.radio-inline label,.has-error.checkbox-inline label{color:#d9534f}.has-error .form-control{border-color:#d9534f;-webkit-box-shadow:inset 0 1px 1px rgba(0,0,0,0.075);box-shadow:inset 0 1px 1px rgba(0,0,0,0.075)}.has-error .form-control:focus{border-color:#c9302c;-webkit-box-shadow:inset 0 1px 1px rgba(0,0,0,0.075),0 0 6px #eba5a3;box-shadow:inset 0 1px 1px rgba(0,0,0,0.075),0 0 6px #eba5a3}.has-error .input-group-addon{color:#d9534f;border-color:#d9534f;background-color:#f2dede}.has-error .form-control-feedback{color:#d9534f}.has-feedback label~.form-control-feedback{top:27px}.has-feedback label.sr-only~.form-control-feedback{top:0}.help-block{display:block;margin-top:5px;margin-bottom:10px;color:#737373}@media (min-width:768px){.form-inline .form-group{display:inline-block;margin-bottom:0;vertical-align:middle}.form-inline .form-control{display:inline-block;width:auto;vertical-align:middle}.form-inline .form-control-static{display:inline-block}.form-inline .input-group{display:inline-table;vertical-align:middle}.form-inline .input-group .input-group-addon,.form-inline .input-group .input-group-btn,.form-inline .input-group .form-control{width:auto}.form-inline .input-group>.form-control{width:100%}.form-inline .control-label{margin-bottom:0;vertical-align:middle}.form-inline .radio,.form-inline .checkbox{display:inline-block;margin-top:0;margin-bottom:0;vertical-align:middle}.form-inline .radio label,.form-inline .checkbox label{padding-left:0}.form-inline .radio input[type="radio"],.form-inline .checkbox input[type="checkbox"]{position:relative;margin-left:0}.form-inline .has-feedback .form-control-feedback{top:0}}.form-horizontal .radio,.form-horizontal .checkbox,.form-horizontal .radio-inline,.form-horizontal .checkbox-inline{margin-top:0;margin-bottom:0;padding-top:9px}.form-horizontal .radio,.form-horizontal .checkbox{min-height:31px}.form-horizontal .form-group{margin-left:-15px;margin-right:-15px}@media (min-width:768px){.form-horizontal .control-label{text-align:right;margin-bottom:0;padding-top:9px}}.form-horizontal .has-feedback .form-control-feedback{right:15px}@media (min-width:768px){.form-horizontal .form-group-lg .control-label{padding-top:15px;font-size:20px}}@media (min-width:768px){.form-horizontal .form-group-sm .control-label{padding-top:6px;font-size:14px}}.btn{display:inline-block;margin-bottom:0;font-weight:normal;text-align:center;vertical-align:middle;-ms-touch-action:manipulation;touch-action:manipulation;cursor:pointer;background-image:none;border:1px solid transparent;white-space:nowrap;padding:8px 12px;font-size:16px;line-height:1.42857143;border-radius:4px;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none}.btn:focus,.btn:active:focus,.btn.active:focus,.btn.focus,.btn:active.focus,.btn.active.focus{outline:thin dotted;outline:5px auto -webkit-focus-ring-color;outline-offset:-2px}.btn:hover,.btn:focus,.btn.focus{color:#333333;text-decoration:none}.btn:active,.btn.active{outline:0;background-image:none;-webkit-box-shadow:inset 0 3px 5px rgba(0,0,0,0.125);box-shadow:inset 0 3px 5px rgba(0,0,0,0.125)}.btn.disabled,.btn[disabled],fieldset[disabled] .btn{cursor:not-allowed;opacity:0.65;filter:alpha(opacity=65);-webkit-box-shadow:none;box-shadow:none}a.btn.disabled,fieldset[disabled] a.btn{pointer-events:none}.btn-default{color:#333333;background-color:#ffffff;border-color:#dddddd}.btn-default:focus,.btn-default.focus{color:#333333;background-color:#e6e6e6;border-color:#9d9d9d}.btn-default:hover{color:#333333;background-color:#e6e6e6;border-color:#bebebe}.btn-default:active,.btn-default.active,.open>.dropdown-toggle.btn-default{color:#333333;background-color:#e6e6e6;border-color:#bebebe}.btn-default:active:hover,.btn-default.active:hover,.open>.dropdown-toggle.btn-default:hover,.btn-default:active:focus,.btn-default.active:focus,.open>.dropdown-toggle.btn-default:focus,.btn-default:active.focus,.btn-default.active.focus,.open>.dropdown-toggle.btn-default.focus{color:#333333;background-color:#d4d4d4;border-color:#9d9d9d}.btn-default:active,.btn-default.active,.open>.dropdown-toggle.btn-default{background-image:none}.btn-default.disabled:hover,.btn-default[disabled]:hover,fieldset[disabled] .btn-default:hover,.btn-default.disabled:focus,.btn-default[disabled]:focus,fieldset[disabled] .btn-default:focus,.btn-default.disabled.focus,.btn-default[disabled].focus,fieldset[disabled] .btn-default.focus{background-color:#ffffff;border-color:#dddddd}.btn-default .badge{color:#ffffff;background-color:#333333}.btn-primary{color:#ffffff;background-color:#4582ec;border-color:#4582ec}.btn-primary:focus,.btn-primary.focus{color:#ffffff;background-color:#1863e6;border-color:#1045a1}.btn-primary:hover{color:#ffffff;background-color:#1863e6;border-color:#175fdd}.btn-primary:active,.btn-primary.active,.open>.dropdown-toggle.btn-primary{color:#ffffff;background-color:#1863e6;border-color:#175fdd}.btn-primary:active:hover,.btn-primary.active:hover,.open>.dropdown-toggle.btn-primary:hover,.btn-primary:active:focus,.btn-primary.active:focus,.open>.dropdown-toggle.btn-primary:focus,.btn-primary:active.focus,.btn-primary.active.focus,.open>.dropdown-toggle.btn-primary.focus{color:#ffffff;background-color:#1455c6;border-color:#1045a1}.btn-primary:active,.btn-primary.active,.open>.dropdown-toggle.btn-primary{background-image:none}.btn-primary.disabled:hover,.btn-primary[disabled]:hover,fieldset[disabled] .btn-primary:hover,.btn-primary.disabled:focus,.btn-primary[disabled]:focus,fieldset[disabled] .btn-primary:focus,.btn-primary.disabled.focus,.btn-primary[disabled].focus,fieldset[disabled] .btn-primary.focus{background-color:#4582ec;border-color:#4582ec}.btn-primary .badge{color:#4582ec;background-color:#ffffff}.btn-success{color:#ffffff;background-color:#3fad46;border-color:#3fad46}.btn-success:focus,.btn-success.focus{color:#ffffff;background-color:#318837;border-color:#1d5020}.btn-success:hover{color:#ffffff;background-color:#318837;border-color:#2f8034}.btn-success:active,.btn-success.active,.open>.dropdown-toggle.btn-success{color:#ffffff;background-color:#318837;border-color:#2f8034}.btn-success:active:hover,.btn-success.active:hover,.open>.dropdown-toggle.btn-success:hover,.btn-success:active:focus,.btn-success.active:focus,.open>.dropdown-toggle.btn-success:focus,.btn-success:active.focus,.btn-success.active.focus,.open>.dropdown-toggle.btn-success.focus{color:#ffffff;background-color:#286d2c;border-color:#1d5020}.btn-success:active,.btn-success.active,.open>.dropdown-toggle.btn-success{background-image:none}.btn-success.disabled:hover,.btn-success[disabled]:hover,fieldset[disabled] .btn-success:hover,.btn-success.disabled:focus,.btn-success[disabled]:focus,fieldset[disabled] .btn-success:focus,.btn-success.disabled.focus,.btn-success[disabled].focus,fieldset[disabled] .btn-success.focus{background-color:#3fad46;border-color:#3fad46}.btn-success .badge{color:#3fad46;background-color:#ffffff}.btn-info{color:#ffffff;background-color:#5bc0de;border-color:#5bc0de}.btn-info:focus,.btn-info.focus{color:#ffffff;background-color:#31b0d5;border-color:#1f7e9a}.btn-info:hover{color:#ffffff;background-color:#31b0d5;border-color:#2aabd2}.btn-info:active,.btn-info.active,.open>.dropdown-toggle.btn-info{color:#ffffff;background-color:#31b0d5;border-color:#2aabd2}.btn-info:active:hover,.btn-info.active:hover,.open>.dropdown-toggle.btn-info:hover,.btn-info:active:focus,.btn-info.active:focus,.open>.dropdown-toggle.btn-info:focus,.btn-info:active.focus,.btn-info.active.focus,.open>.dropdown-toggle.btn-info.focus{color:#ffffff;background-color:#269abc;border-color:#1f7e9a}.btn-info:active,.btn-info.active,.open>.dropdown-toggle.btn-info{background-image:none}.btn-info.disabled:hover,.btn-info[disabled]:hover,fieldset[disabled] .btn-info:hover,.btn-info.disabled:focus,.btn-info[disabled]:focus,fieldset[disabled] .btn-info:focus,.btn-info.disabled.focus,.btn-info[disabled].focus,fieldset[disabled] .btn-info.focus{background-color:#5bc0de;border-color:#5bc0de}.btn-info .badge{color:#5bc0de;background-color:#ffffff}.btn-warning{color:#ffffff;background-color:#f0ad4e;border-color:#f0ad4e}.btn-warning:focus,.btn-warning.focus{color:#ffffff;background-color:#ec971f;border-color:#b06d0f}.btn-warning:hover{color:#ffffff;background-color:#ec971f;border-color:#eb9316}.btn-warning:active,.btn-warning.active,.open>.dropdown-toggle.btn-warning{color:#ffffff;background-color:#ec971f;border-color:#eb9316}.btn-warning:active:hover,.btn-warning.active:hover,.open>.dropdown-toggle.btn-warning:hover,.btn-warning:active:focus,.btn-warning.active:focus,.open>.dropdown-toggle.btn-warning:focus,.btn-warning:active.focus,.btn-warning.active.focus,.open>.dropdown-toggle.btn-warning.focus{color:#ffffff;background-color:#d58512;border-color:#b06d0f}.btn-warning:active,.btn-warning.active,.open>.dropdown-toggle.btn-warning{background-image:none}.btn-warning.disabled:hover,.btn-warning[disabled]:hover,fieldset[disabled] .btn-warning:hover,.btn-warning.disabled:focus,.btn-warning[disabled]:focus,fieldset[disabled] .btn-warning:focus,.btn-warning.disabled.focus,.btn-warning[disabled].focus,fieldset[disabled] .btn-warning.focus{background-color:#f0ad4e;border-color:#f0ad4e}.btn-warning .badge{color:#f0ad4e;background-color:#ffffff}.btn-danger{color:#ffffff;background-color:#d9534f;border-color:#d9534f}.btn-danger:focus,.btn-danger.focus{color:#ffffff;background-color:#c9302c;border-color:#8b211e}.btn-danger:hover{color:#ffffff;background-color:#c9302c;border-color:#c12e2a}.btn-danger:active,.btn-danger.active,.open>.dropdown-toggle.btn-danger{color:#ffffff;background-color:#c9302c;border-color:#c12e2a}.btn-danger:active:hover,.btn-danger.active:hover,.open>.dropdown-toggle.btn-danger:hover,.btn-danger:active:focus,.btn-danger.active:focus,.open>.dropdown-toggle.btn-danger:focus,.btn-danger:active.focus,.btn-danger.active.focus,.open>.dropdown-toggle.btn-danger.focus{color:#ffffff;background-color:#ac2925;border-color:#8b211e}.btn-danger:active,.btn-danger.active,.open>.dropdown-toggle.btn-danger{background-image:none}.btn-danger.disabled:hover,.btn-danger[disabled]:hover,fieldset[disabled] .btn-danger:hover,.btn-danger.disabled:focus,.btn-danger[disabled]:focus,fieldset[disabled] .btn-danger:focus,.btn-danger.disabled.focus,.btn-danger[disabled].focus,fieldset[disabled] .btn-danger.focus{background-color:#d9534f;border-color:#d9534f}.btn-danger .badge{color:#d9534f;background-color:#ffffff}.btn-link{color:#4582ec;font-weight:normal;border-radius:0}.btn-link,.btn-link:active,.btn-link.active,.btn-link[disabled],fieldset[disabled] .btn-link{background-color:transparent;-webkit-box-shadow:none;box-shadow:none}.btn-link,.btn-link:hover,.btn-link:focus,.btn-link:active{border-color:transparent}.btn-link:hover,.btn-link:focus{color:#134fb8;text-decoration:underline;background-color:transparent}.btn-link[disabled]:hover,fieldset[disabled] .btn-link:hover,.btn-link[disabled]:focus,fieldset[disabled] .btn-link:focus{color:#b3b3b3;text-decoration:none}.btn-lg,.btn-group-lg>.btn{padding:14px 16px;font-size:20px;line-height:1.3333333;border-radius:6px}.btn-sm,.btn-group-sm>.btn{padding:5px 10px;font-size:14px;line-height:1.5;border-radius:3px}.btn-xs,.btn-group-xs>.btn{padding:1px 5px;font-size:14px;line-height:1.5;border-radius:3px}.btn-block{display:block;width:100%}.btn-block+.btn-block{margin-top:5px}input[type="submit"].btn-block,input[type="reset"].btn-block,input[type="button"].btn-block{width:100%}.fade{opacity:0;-webkit-transition:opacity 0.15s linear;-o-transition:opacity 0.15s linear;transition:opacity 0.15s linear}.fade.in{opacity:1}.collapse{display:none}.collapse.in{display:block}tr.collapse.in{display:table-row}tbody.collapse.in{display:table-row-group}.collapsing{position:relative;height:0;overflow:hidden;-webkit-transition-property:height, visibility;-o-transition-property:height, visibility;transition-property:height, visibility;-webkit-transition-duration:0.35s;-o-transition-duration:0.35s;transition-duration:0.35s;-webkit-transition-timing-function:ease;-o-transition-timing-function:ease;transition-timing-function:ease}.caret{display:inline-block;width:0;height:0;margin-left:2px;vertical-align:middle;border-top:4px dashed;border-top:4px solid \9;border-right:4px solid transparent;border-left:4px solid transparent}.dropup,.dropdown{position:relative}.dropdown-toggle:focus{outline:0}.dropdown-menu{position:absolute;top:100%;left:0;z-index:1000;display:none;float:left;min-width:160px;padding:5px 0;margin:2px 0 0;list-style:none;font-size:16px;text-align:left;background-color:#ffffff;border:1px solid #cccccc;border:1px solid rgba(0,0,0,0.15);border-radius:4px;-webkit-box-shadow:0 6px 12px rgba(0,0,0,0.175);box-shadow:0 6px 12px rgba(0,0,0,0.175);-webkit-background-clip:padding-box;background-clip:padding-box}.dropdown-menu.pull-right{right:0;left:auto}.dropdown-menu .divider{height:1px;margin:10px 0;overflow:hidden;background-color:#e5e5e5}.dropdown-menu>li>a{display:block;padding:3px 20px;clear:both;font-weight:normal;line-height:1.42857143;color:#333333;white-space:nowrap}.dropdown-menu>li>a:hover,.dropdown-menu>li>a:focus{text-decoration:none;color:#ffffff;background-color:#4582ec}.dropdown-menu>.active>a,.dropdown-menu>.active>a:hover,.dropdown-menu>.active>a:focus{color:#ffffff;text-decoration:none;outline:0;background-color:#4582ec}.dropdown-menu>.disabled>a,.dropdown-menu>.disabled>a:hover,.dropdown-menu>.disabled>a:focus{color:#b3b3b3}.dropdown-menu>.disabled>a:hover,.dropdown-menu>.disabled>a:focus{text-decoration:none;background-color:transparent;background-image:none;filter:progid:DXImageTransform.Microsoft.gradient(enabled=false);cursor:not-allowed}.open>.dropdown-menu{display:block}.open>a{outline:0}.dropdown-menu-right{left:auto;right:0}.dropdown-menu-left{left:0;right:auto}.dropdown-header{display:block;padding:3px 20px;font-size:14px;line-height:1.42857143;color:#b3b3b3;white-space:nowrap}.dropdown-backdrop{position:fixed;left:0;right:0;bottom:0;top:0;z-index:990}.pull-right>.dropdown-menu{right:0;left:auto}.dropup .caret,.navbar-fixed-bottom .dropdown .caret{border-top:0;border-bottom:4px dashed;border-bottom:4px solid \9;content:""}.dropup .dropdown-menu,.navbar-fixed-bottom .dropdown .dropdown-menu{top:auto;bottom:100%;margin-bottom:2px}@media (min-width:768px){.navbar-right .dropdown-menu{left:auto;right:0}.navbar-right .dropdown-menu-left{left:0;right:auto}}.btn-group,.btn-group-vertical{position:relative;display:inline-block;vertical-align:middle}.btn-group>.btn,.btn-group-vertical>.btn{position:relative;float:left}.btn-group>.btn:hover,.btn-group-vertical>.btn:hover,.btn-group>.btn:focus,.btn-group-vertical>.btn:focus,.btn-group>.btn:active,.btn-group-vertical>.btn:active,.btn-group>.btn.active,.btn-group-vertical>.btn.active{z-index:2}.btn-group .btn+.btn,.btn-group .btn+.btn-group,.btn-group .btn-group+.btn,.btn-group .btn-group+.btn-group{margin-left:-1px}.btn-toolbar{margin-left:-5px}.btn-toolbar .btn,.btn-toolbar .btn-group,.btn-toolbar .input-group{float:left}.btn-toolbar>.btn,.btn-toolbar>.btn-group,.btn-toolbar>.input-group{margin-left:5px}.btn-group>.btn:not(:first-child):not(:last-child):not(.dropdown-toggle){border-radius:0}.btn-group>.btn:first-child{margin-left:0}.btn-group>.btn:first-child:not(:last-child):not(.dropdown-toggle){border-bottom-right-radius:0;border-top-right-radius:0}.btn-group>.btn:last-child:not(:first-child),.btn-group>.dropdown-toggle:not(:first-child){border-bottom-left-radius:0;border-top-left-radius:0}.btn-group>.btn-group{float:left}.btn-group>.btn-group:not(:first-child):not(:last-child)>.btn{border-radius:0}.btn-group>.btn-group:first-child:not(:last-child)>.btn:last-child,.btn-group>.btn-group:first-child:not(:last-child)>.dropdown-toggle{border-bottom-right-radius:0;border-top-right-radius:0}.btn-group>.btn-group:last-child:not(:first-child)>.btn:first-child{border-bottom-left-radius:0;border-top-left-radius:0}.btn-group .dropdown-toggle:active,.btn-group.open .dropdown-toggle{outline:0}.btn-group>.btn+.dropdown-toggle{padding-left:8px;padding-right:8px}.btn-group>.btn-lg+.dropdown-toggle{padding-left:12px;padding-right:12px}.btn-group.open .dropdown-toggle{-webkit-box-shadow:inset 0 3px 5px rgba(0,0,0,0.125);box-shadow:inset 0 3px 5px rgba(0,0,0,0.125)}.btn-group.open .dropdown-toggle.btn-link{-webkit-box-shadow:none;box-shadow:none}.btn .caret{margin-left:0}.btn-lg .caret{border-width:5px 5px 0;border-bottom-width:0}.dropup .btn-lg .caret{border-width:0 5px 5px}.btn-group-vertical>.btn,.btn-group-vertical>.btn-group,.btn-group-vertical>.btn-group>.btn{display:block;float:none;width:100%;max-width:100%}.btn-group-vertical>.btn-group>.btn{float:none}.btn-group-vertical>.btn+.btn,.btn-group-vertical>.btn+.btn-group,.btn-group-vertical>.btn-group+.btn,.btn-group-vertical>.btn-group+.btn-group{margin-top:-1px;margin-left:0}.btn-group-vertical>.btn:not(:first-child):not(:last-child){border-radius:0}.btn-group-vertical>.btn:first-child:not(:last-child){border-top-right-radius:4px;border-top-left-radius:4px;border-bottom-right-radius:0;border-bottom-left-radius:0}.btn-group-vertical>.btn:last-child:not(:first-child){border-top-right-radius:0;border-top-left-radius:0;border-bottom-right-radius:4px;border-bottom-left-radius:4px}.btn-group-vertical>.btn-group:not(:first-child):not(:last-child)>.btn{border-radius:0}.btn-group-vertical>.btn-group:first-child:not(:last-child)>.btn:last-child,.btn-group-vertical>.btn-group:first-child:not(:last-child)>.dropdown-toggle{border-bottom-right-radius:0;border-bottom-left-radius:0}.btn-group-vertical>.btn-group:last-child:not(:first-child)>.btn:first-child{border-top-right-radius:0;border-top-left-radius:0}.btn-group-justified{display:table;width:100%;table-layout:fixed;border-collapse:separate}.btn-group-justified>.btn,.btn-group-justified>.btn-group{float:none;display:table-cell;width:1%}.btn-group-justified>.btn-group .btn{width:100%}.btn-group-justified>.btn-group .dropdown-menu{left:auto}[data-toggle="buttons"]>.btn input[type="radio"],[data-toggle="buttons"]>.btn-group>.btn input[type="radio"],[data-toggle="buttons"]>.btn input[type="checkbox"],[data-toggle="buttons"]>.btn-group>.btn input[type="checkbox"]{position:absolute;clip:rect(0, 0, 0, 0);pointer-events:none}.input-group{position:relative;display:table;border-collapse:separate}.input-group[class*="col-"]{float:none;padding-left:0;padding-right:0}.input-group .form-control{position:relative;z-index:2;float:left;width:100%;margin-bottom:0}.input-group .form-control:focus{z-index:3}.input-group-lg>.form-control,.input-group-lg>.input-group-addon,.input-group-lg>.input-group-btn>.btn{height:57px;padding:14px 16px;font-size:20px;line-height:1.3333333;border-radius:6px}select.input-group-lg>.form-control,select.input-group-lg>.input-group-addon,select.input-group-lg>.input-group-btn>.btn{height:57px;line-height:57px}textarea.input-group-lg>.form-control,textarea.input-group-lg>.input-group-addon,textarea.input-group-lg>.input-group-btn>.btn,select[multiple].input-group-lg>.form-control,select[multiple].input-group-lg>.input-group-addon,select[multiple].input-group-lg>.input-group-btn>.btn{height:auto}.input-group-sm>.form-control,.input-group-sm>.input-group-addon,.input-group-sm>.input-group-btn>.btn{height:33px;padding:5px 10px;font-size:14px;line-height:1.5;border-radius:3px}select.input-group-sm>.form-control,select.input-group-sm>.input-group-addon,select.input-group-sm>.input-group-btn>.btn{height:33px;line-height:33px}textarea.input-group-sm>.form-control,textarea.input-group-sm>.input-group-addon,textarea.input-group-sm>.input-group-btn>.btn,select[multiple].input-group-sm>.form-control,select[multiple].input-group-sm>.input-group-addon,select[multiple].input-group-sm>.input-group-btn>.btn{height:auto}.input-group-addon,.input-group-btn,.input-group .form-control{display:table-cell}.input-group-addon:not(:first-child):not(:last-child),.input-group-btn:not(:first-child):not(:last-child),.input-group .form-control:not(:first-child):not(:last-child){border-radius:0}.input-group-addon,.input-group-btn{width:1%;white-space:nowrap;vertical-align:middle}.input-group-addon{padding:8px 12px;font-size:16px;font-weight:normal;line-height:1;color:#333333;text-align:center;background-color:#eeeeee;border:1px solid #dddddd;border-radius:4px}.input-group-addon.input-sm{padding:5px 10px;font-size:14px;border-radius:3px}.input-group-addon.input-lg{padding:14px 16px;font-size:20px;border-radius:6px}.input-group-addon input[type="radio"],.input-group-addon input[type="checkbox"]{margin-top:0}.input-group .form-control:first-child,.input-group-addon:first-child,.input-group-btn:first-child>.btn,.input-group-btn:first-child>.btn-group>.btn,.input-group-btn:first-child>.dropdown-toggle,.input-group-btn:last-child>.btn:not(:last-child):not(.dropdown-toggle),.input-group-btn:last-child>.btn-group:not(:last-child)>.btn{border-bottom-right-radius:0;border-top-right-radius:0}.input-group-addon:first-child{border-right:0}.input-group .form-control:last-child,.input-group-addon:last-child,.input-group-btn:last-child>.btn,.input-group-btn:last-child>.btn-group>.btn,.input-group-btn:last-child>.dropdown-toggle,.input-group-btn:first-child>.btn:not(:first-child),.input-group-btn:first-child>.btn-group:not(:first-child)>.btn{border-bottom-left-radius:0;border-top-left-radius:0}.input-group-addon:last-child{border-left:0}.input-group-btn{position:relative;font-size:0;white-space:nowrap}.input-group-btn>.btn{position:relative}.input-group-btn>.btn+.btn{margin-left:-1px}.input-group-btn>.btn:hover,.input-group-btn>.btn:focus,.input-group-btn>.btn:active{z-index:2}.input-group-btn:first-child>.btn,.input-group-btn:first-child>.btn-group{margin-right:-1px}.input-group-btn:last-child>.btn,.input-group-btn:last-child>.btn-group{z-index:2;margin-left:-1px}.nav{margin-bottom:0;padding-left:0;list-style:none}.nav>li{position:relative;display:block}.nav>li>a{position:relative;display:block;padding:10px 15px}.nav>li>a:hover,.nav>li>a:focus{text-decoration:none;background-color:#eeeeee}.nav>li.disabled>a{color:#b3b3b3}.nav>li.disabled>a:hover,.nav>li.disabled>a:focus{color:#b3b3b3;text-decoration:none;background-color:transparent;cursor:not-allowed}.nav .open>a,.nav .open>a:hover,.nav .open>a:focus{background-color:#eeeeee;border-color:#4582ec}.nav .nav-divider{height:1px;margin:10px 0;overflow:hidden;background-color:#e5e5e5}.nav>li>a>img{max-width:none}.nav-tabs{border-bottom:1px solid #dddddd}.nav-tabs>li{float:left;margin-bottom:-1px}.nav-tabs>li>a{margin-right:2px;line-height:1.42857143;border:1px solid transparent;border-radius:4px 4px 0 0}.nav-tabs>li>a:hover{border-color:#eeeeee #eeeeee #dddddd}.nav-tabs>li.active>a,.nav-tabs>li.active>a:hover,.nav-tabs>li.active>a:focus{color:#555555;background-color:#ffffff;border:1px solid #dddddd;border-bottom-color:transparent;cursor:default}.nav-tabs.nav-justified{width:100%;border-bottom:0}.nav-tabs.nav-justified>li{float:none}.nav-tabs.nav-justified>li>a{text-align:center;margin-bottom:5px}.nav-tabs.nav-justified>.dropdown .dropdown-menu{top:auto;left:auto}@media (min-width:768px){.nav-tabs.nav-justified>li{display:table-cell;width:1%}.nav-tabs.nav-justified>li>a{margin-bottom:0}}.nav-tabs.nav-justified>li>a{margin-right:0;border-radius:4px}.nav-tabs.nav-justified>.active>a,.nav-tabs.nav-justified>.active>a:hover,.nav-tabs.nav-justified>.active>a:focus{border:1px solid #dddddd}@media (min-width:768px){.nav-tabs.nav-justified>li>a{border-bottom:1px solid #dddddd;border-radius:4px 4px 0 0}.nav-tabs.nav-justified>.active>a,.nav-tabs.nav-justified>.active>a:hover,.nav-tabs.nav-justified>.active>a:focus{border-bottom-color:#ffffff}}.nav-pills>li{float:left}.nav-pills>li>a{border-radius:4px}.nav-pills>li+li{margin-left:2px}.nav-pills>li.active>a,.nav-pills>li.active>a:hover,.nav-pills>li.active>a:focus{color:#ffffff;background-color:#4582ec}.nav-stacked>li{float:none}.nav-stacked>li+li{margin-top:2px;margin-left:0}.nav-justified{width:100%}.nav-justified>li{float:none}.nav-justified>li>a{text-align:center;margin-bottom:5px}.nav-justified>.dropdown .dropdown-menu{top:auto;left:auto}@media (min-width:768px){.nav-justified>li{display:table-cell;width:1%}.nav-justified>li>a{margin-bottom:0}}.nav-tabs-justified{border-bottom:0}.nav-tabs-justified>li>a{margin-right:0;border-radius:4px}.nav-tabs-justified>.active>a,.nav-tabs-justified>.active>a:hover,.nav-tabs-justified>.active>a:focus{border:1px solid #dddddd}@media (min-width:768px){.nav-tabs-justified>li>a{border-bottom:1px solid #dddddd;border-radius:4px 4px 0 0}.nav-tabs-justified>.active>a,.nav-tabs-justified>.active>a:hover,.nav-tabs-justified>.active>a:focus{border-bottom-color:#ffffff}}.tab-content>.tab-pane{display:none}.tab-content>.active{display:block}.nav-tabs .dropdown-menu{margin-top:-1px;border-top-right-radius:0;border-top-left-radius:0}.navbar{position:relative;min-height:65px;margin-bottom:22px;border:1px solid transparent}@media (min-width:768px){.navbar{border-radius:4px}}@media (min-width:768px){.navbar-header{float:left}}.navbar-collapse{overflow-x:visible;padding-right:15px;padding-left:15px;border-top:1px solid transparent;-webkit-box-shadow:inset 0 1px 0 rgba(255,255,255,0.1);box-shadow:inset 0 1px 0 rgba(255,255,255,0.1);-webkit-overflow-scrolling:touch}.navbar-collapse.in{overflow-y:auto}@media (min-width:768px){.navbar-collapse{width:auto;border-top:0;-webkit-box-shadow:none;box-shadow:none}.navbar-collapse.collapse{display:block !important;height:auto !important;padding-bottom:0;overflow:visible !important}.navbar-collapse.in{overflow-y:visible}.navbar-fixed-top .navbar-collapse,.navbar-static-top .navbar-collapse,.navbar-fixed-bottom .navbar-collapse{padding-left:0;padding-right:0}}.navbar-fixed-top .navbar-collapse,.navbar-fixed-bottom .navbar-collapse{max-height:340px}@media (max-device-width:480px) and (orientation:landscape){.navbar-fixed-top .navbar-collapse,.navbar-fixed-bottom .navbar-collapse{max-height:200px}}.container>.navbar-header,.container-fluid>.navbar-header,.container>.navbar-collapse,.container-fluid>.navbar-collapse{margin-right:-15px;margin-left:-15px}@media (min-width:768px){.container>.navbar-header,.container-fluid>.navbar-header,.container>.navbar-collapse,.container-fluid>.navbar-collapse{margin-right:0;margin-left:0}}.navbar-static-top{z-index:1000;border-width:0 0 1px}@media (min-width:768px){.navbar-static-top{border-radius:0}}.navbar-fixed-top,.navbar-fixed-bottom{position:fixed;right:0;left:0;z-index:1030}@media (min-width:768px){.navbar-fixed-top,.navbar-fixed-bottom{border-radius:0}}.navbar-fixed-top{top:0;border-width:0 0 1px}.navbar-fixed-bottom{bottom:0;margin-bottom:0;border-width:1px 0 0}.navbar-brand{float:left;padding:21.5px 15px;font-size:20px;line-height:22px;height:65px}.navbar-brand:hover,.navbar-brand:focus{text-decoration:none}.navbar-brand>img{display:block}@media (min-width:768px){.navbar>.container .navbar-brand,.navbar>.container-fluid .navbar-brand{margin-left:-15px}}.navbar-toggle{position:relative;float:right;margin-right:15px;padding:9px 10px;margin-top:15.5px;margin-bottom:15.5px;background-color:transparent;background-image:none;border:1px solid transparent;border-radius:4px}.navbar-toggle:focus{outline:0}.navbar-toggle .icon-bar{display:block;width:22px;height:2px;border-radius:1px}.navbar-toggle .icon-bar+.icon-bar{margin-top:4px}@media (min-width:768px){.navbar-toggle{display:none}}.navbar-nav{margin:10.75px -15px}.navbar-nav>li>a{padding-top:10px;padding-bottom:10px;line-height:22px}@media (max-width:767px){.navbar-nav .open .dropdown-menu{position:static;float:none;width:auto;margin-top:0;background-color:transparent;border:0;-webkit-box-shadow:none;box-shadow:none}.navbar-nav .open .dropdown-menu>li>a,.navbar-nav .open .dropdown-menu .dropdown-header{padding:5px 15px 5px 25px}.navbar-nav .open .dropdown-menu>li>a{line-height:22px}.navbar-nav .open .dropdown-menu>li>a:hover,.navbar-nav .open .dropdown-menu>li>a:focus{background-image:none}}@media (min-width:768px){.navbar-nav{float:left;margin:0}.navbar-nav>li{float:left}.navbar-nav>li>a{padding-top:21.5px;padding-bottom:21.5px}}.navbar-form{margin-left:-15px;margin-right:-15px;padding:10px 15px;border-top:1px solid transparent;border-bottom:1px solid transparent;-webkit-box-shadow:inset 0 1px 0 rgba(255,255,255,0.1),0 1px 0 rgba(255,255,255,0.1);box-shadow:inset 0 1px 0 rgba(255,255,255,0.1),0 1px 0 rgba(255,255,255,0.1);margin-top:12.5px;margin-bottom:12.5px}@media (min-width:768px){.navbar-form .form-group{display:inline-block;margin-bottom:0;vertical-align:middle}.navbar-form .form-control{display:inline-block;width:auto;vertical-align:middle}.navbar-form .form-control-static{display:inline-block}.navbar-form .input-group{display:inline-table;vertical-align:middle}.navbar-form .input-group .input-group-addon,.navbar-form .input-group .input-group-btn,.navbar-form .input-group .form-control{width:auto}.navbar-form .input-group>.form-control{width:100%}.navbar-form .control-label{margin-bottom:0;vertical-align:middle}.navbar-form .radio,.navbar-form .checkbox{display:inline-block;margin-top:0;margin-bottom:0;vertical-align:middle}.navbar-form .radio label,.navbar-form .checkbox label{padding-left:0}.navbar-form .radio input[type="radio"],.navbar-form .checkbox input[type="checkbox"]{position:relative;margin-left:0}.navbar-form .has-feedback .form-control-feedback{top:0}}@media (max-width:767px){.navbar-form .form-group{margin-bottom:5px}.navbar-form .form-group:last-child{margin-bottom:0}}@media (min-width:768px){.navbar-form{width:auto;border:0;margin-left:0;margin-right:0;padding-top:0;padding-bottom:0;-webkit-box-shadow:none;box-shadow:none}}.navbar-nav>li>.dropdown-menu{margin-top:0;border-top-right-radius:0;border-top-left-radius:0}.navbar-fixed-bottom .navbar-nav>li>.dropdown-menu{margin-bottom:0;border-top-right-radius:4px;border-top-left-radius:4px;border-bottom-right-radius:0;border-bottom-left-radius:0}.navbar-btn{margin-top:12.5px;margin-bottom:12.5px}.navbar-btn.btn-sm{margin-top:16px;margin-bottom:16px}.navbar-btn.btn-xs{margin-top:21.5px;margin-bottom:21.5px}.navbar-text{margin-top:21.5px;margin-bottom:21.5px}@media (min-width:768px){.navbar-text{float:left;margin-left:15px;margin-right:15px}}@media (min-width:768px){.navbar-left{float:left !important}.navbar-right{float:right !important;margin-right:-15px}.navbar-right~.navbar-right{margin-right:0}}.navbar-default{background-color:#ffffff;border-color:#dddddd}.navbar-default .navbar-brand{color:#4582ec}.navbar-default .navbar-brand:hover,.navbar-default .navbar-brand:focus{color:#4582ec;background-color:transparent}.navbar-default .navbar-text{color:#333333}.navbar-default .navbar-nav>li>a{color:#4582ec}.navbar-default .navbar-nav>li>a:hover,.navbar-default .navbar-nav>li>a:focus{color:#4582ec;background-color:transparent}.navbar-default .navbar-nav>.active>a,.navbar-default .navbar-nav>.active>a:hover,.navbar-default .navbar-nav>.active>a:focus{color:#4582ec;background-color:transparent}.navbar-default .navbar-nav>.disabled>a,.navbar-default .navbar-nav>.disabled>a:hover,.navbar-default .navbar-nav>.disabled>a:focus{color:#333333;background-color:transparent}.navbar-default .navbar-toggle{border-color:#dddddd}.navbar-default .navbar-toggle:hover,.navbar-default .navbar-toggle:focus{background-color:#dddddd}.navbar-default .navbar-toggle .icon-bar{background-color:#cccccc}.navbar-default .navbar-collapse,.navbar-default .navbar-form{border-color:#dddddd}.navbar-default .navbar-nav>.open>a,.navbar-default .navbar-nav>.open>a:hover,.navbar-default .navbar-nav>.open>a:focus{background-color:transparent;color:#4582ec}@media (max-width:767px){.navbar-default .navbar-nav .open .dropdown-menu>li>a{color:#4582ec}.navbar-default .navbar-nav .open .dropdown-menu>li>a:hover,.navbar-default .navbar-nav .open .dropdown-menu>li>a:focus{color:#4582ec;background-color:transparent}.navbar-default .navbar-nav .open .dropdown-menu>.active>a,.navbar-default .navbar-nav .open .dropdown-menu>.active>a:hover,.navbar-default .navbar-nav .open .dropdown-menu>.active>a:focus{color:#4582ec;background-color:transparent}.navbar-default .navbar-nav .open .dropdown-menu>.disabled>a,.navbar-default .navbar-nav .open .dropdown-menu>.disabled>a:hover,.navbar-default .navbar-nav .open .dropdown-menu>.disabled>a:focus{color:#333333;background-color:transparent}}.navbar-default .navbar-link{color:#4582ec}.navbar-default .navbar-link:hover{color:#4582ec}.navbar-default .btn-link{color:#4582ec}.navbar-default .btn-link:hover,.navbar-default .btn-link:focus{color:#4582ec}.navbar-default .btn-link[disabled]:hover,fieldset[disabled] .navbar-default .btn-link:hover,.navbar-default .btn-link[disabled]:focus,fieldset[disabled] .navbar-default .btn-link:focus{color:#333333}.navbar-inverse{background-color:#ffffff;border-color:#dddddd}.navbar-inverse .navbar-brand{color:#333333}.navbar-inverse .navbar-brand:hover,.navbar-inverse .navbar-brand:focus{color:#333333;background-color:transparent}.navbar-inverse .navbar-text{color:#333333}.navbar-inverse .navbar-nav>li>a{color:#333333}.navbar-inverse .navbar-nav>li>a:hover,.navbar-inverse .navbar-nav>li>a:focus{color:#333333;background-color:transparent}.navbar-inverse .navbar-nav>.active>a,.navbar-inverse .navbar-nav>.active>a:hover,.navbar-inverse .navbar-nav>.active>a:focus{color:#333333;background-color:transparent}.navbar-inverse .navbar-nav>.disabled>a,.navbar-inverse .navbar-nav>.disabled>a:hover,.navbar-inverse .navbar-nav>.disabled>a:focus{color:#cccccc;background-color:transparent}.navbar-inverse .navbar-toggle{border-color:#dddddd}.navbar-inverse .navbar-toggle:hover,.navbar-inverse .navbar-toggle:focus{background-color:#dddddd}.navbar-inverse .navbar-toggle .icon-bar{background-color:#cccccc}.navbar-inverse .navbar-collapse,.navbar-inverse .navbar-form{border-color:#ededed}.navbar-inverse .navbar-nav>.open>a,.navbar-inverse .navbar-nav>.open>a:hover,.navbar-inverse .navbar-nav>.open>a:focus{background-color:transparent;color:#333333}@media (max-width:767px){.navbar-inverse .navbar-nav .open .dropdown-menu>.dropdown-header{border-color:#dddddd}.navbar-inverse .navbar-nav .open .dropdown-menu .divider{background-color:#dddddd}.navbar-inverse .navbar-nav .open .dropdown-menu>li>a{color:#333333}.navbar-inverse .navbar-nav .open .dropdown-menu>li>a:hover,.navbar-inverse .navbar-nav .open .dropdown-menu>li>a:focus{color:#333333;background-color:transparent}.navbar-inverse .navbar-nav .open .dropdown-menu>.active>a,.navbar-inverse .navbar-nav .open .dropdown-menu>.active>a:hover,.navbar-inverse .navbar-nav .open .dropdown-menu>.active>a:focus{color:#333333;background-color:transparent}.navbar-inverse .navbar-nav .open .dropdown-menu>.disabled>a,.navbar-inverse .navbar-nav .open .dropdown-menu>.disabled>a:hover,.navbar-inverse .navbar-nav .open .dropdown-menu>.disabled>a:focus{color:#cccccc;background-color:transparent}}.navbar-inverse .navbar-link{color:#333333}.navbar-inverse .navbar-link:hover{color:#333333}.navbar-inverse .btn-link{color:#333333}.navbar-inverse .btn-link:hover,.navbar-inverse .btn-link:focus{color:#333333}.navbar-inverse .btn-link[disabled]:hover,fieldset[disabled] .navbar-inverse .btn-link:hover,.navbar-inverse .btn-link[disabled]:focus,fieldset[disabled] .navbar-inverse .btn-link:focus{color:#cccccc}.breadcrumb{padding:8px 15px;margin-bottom:22px;list-style:none;background-color:#f5f5f5;border-radius:4px}.breadcrumb>li{display:inline-block}.breadcrumb>li+li:before{content:"/\00a0";padding:0 5px;color:#cccccc}.breadcrumb>.active{color:#b3b3b3}.pagination{display:inline-block;padding-left:0;margin:22px 0;border-radius:4px}.pagination>li{display:inline}.pagination>li>a,.pagination>li>span{position:relative;float:left;padding:8px 12px;line-height:1.42857143;text-decoration:none;color:#333333;background-color:#ffffff;border:1px solid #dddddd;margin-left:-1px}.pagination>li:first-child>a,.pagination>li:first-child>span{margin-left:0;border-bottom-left-radius:4px;border-top-left-radius:4px}.pagination>li:last-child>a,.pagination>li:last-child>span{border-bottom-right-radius:4px;border-top-right-radius:4px}.pagination>li>a:hover,.pagination>li>span:hover,.pagination>li>a:focus,.pagination>li>span:focus{z-index:2;color:#ffffff;background-color:#4582ec;border-color:#4582ec}.pagination>.active>a,.pagination>.active>span,.pagination>.active>a:hover,.pagination>.active>span:hover,.pagination>.active>a:focus,.pagination>.active>span:focus{z-index:3;color:#ffffff;background-color:#4582ec;border-color:#4582ec;cursor:default}.pagination>.disabled>span,.pagination>.disabled>span:hover,.pagination>.disabled>span:focus,.pagination>.disabled>a,.pagination>.disabled>a:hover,.pagination>.disabled>a:focus{color:#b3b3b3;background-color:#ffffff;border-color:#dddddd;cursor:not-allowed}.pagination-lg>li>a,.pagination-lg>li>span{padding:14px 16px;font-size:20px;line-height:1.3333333}.pagination-lg>li:first-child>a,.pagination-lg>li:first-child>span{border-bottom-left-radius:6px;border-top-left-radius:6px}.pagination-lg>li:last-child>a,.pagination-lg>li:last-child>span{border-bottom-right-radius:6px;border-top-right-radius:6px}.pagination-sm>li>a,.pagination-sm>li>span{padding:5px 10px;font-size:14px;line-height:1.5}.pagination-sm>li:first-child>a,.pagination-sm>li:first-child>span{border-bottom-left-radius:3px;border-top-left-radius:3px}.pagination-sm>li:last-child>a,.pagination-sm>li:last-child>span{border-bottom-right-radius:3px;border-top-right-radius:3px}.pager{padding-left:0;margin:22px 0;list-style:none;text-align:center}.pager li{display:inline}.pager li>a,.pager li>span{display:inline-block;padding:5px 14px;background-color:#ffffff;border:1px solid #dddddd;border-radius:15px}.pager li>a:hover,.pager li>a:focus{text-decoration:none;background-color:#4582ec}.pager .next>a,.pager .next>span{float:right}.pager .previous>a,.pager .previous>span{float:left}.pager .disabled>a,.pager .disabled>a:hover,.pager .disabled>a:focus,.pager .disabled>span{color:#b3b3b3;background-color:#ffffff;cursor:not-allowed}.label{display:inline;padding:.2em .6em .3em;font-size:75%;font-weight:bold;line-height:1;color:#ffffff;text-align:center;white-space:nowrap;vertical-align:baseline;border-radius:.25em}a.label:hover,a.label:focus{color:#ffffff;text-decoration:none;cursor:pointer}.label:empty{display:none}.btn .label{position:relative;top:-1px}.label-default{background-color:#ffffff}.label-default[href]:hover,.label-default[href]:focus{background-color:#e6e6e6}.label-primary{background-color:#4582ec}.label-primary[href]:hover,.label-primary[href]:focus{background-color:#1863e6}.label-success{background-color:#3fad46}.label-success[href]:hover,.label-success[href]:focus{background-color:#318837}.label-info{background-color:#5bc0de}.label-info[href]:hover,.label-info[href]:focus{background-color:#31b0d5}.label-warning{background-color:#f0ad4e}.label-warning[href]:hover,.label-warning[href]:focus{background-color:#ec971f}.label-danger{background-color:#d9534f}.label-danger[href]:hover,.label-danger[href]:focus{background-color:#c9302c}.badge{display:inline-block;min-width:10px;padding:3px 7px;font-size:14px;font-weight:bold;color:#ffffff;line-height:1;vertical-align:middle;white-space:nowrap;text-align:center;background-color:#4582ec;border-radius:10px}.badge:empty{display:none}.btn .badge{position:relative;top:-1px}.btn-xs .badge,.btn-group-xs>.btn .badge{top:0;padding:1px 5px}a.badge:hover,a.badge:focus{color:#ffffff;text-decoration:none;cursor:pointer}.list-group-item.active>.badge,.nav-pills>.active>a>.badge{color:#4582ec;background-color:#ffffff}.list-group-item>.badge{float:right}.list-group-item>.badge+.badge{margin-right:5px}.nav-pills>li>a>.badge{margin-left:3px}.jumbotron{padding-top:30px;padding-bottom:30px;margin-bottom:30px;color:inherit;background-color:#f7f7f7}.jumbotron h1,.jumbotron .h1{color:inherit}.jumbotron p{margin-bottom:15px;font-size:24px;font-weight:200}.jumbotron>hr{border-top-color:#dedede}.container .jumbotron,.container-fluid .jumbotron{border-radius:6px;padding-left:15px;padding-right:15px}.jumbotron .container{max-width:100%}@media screen and (min-width:768px){.jumbotron{padding-top:48px;padding-bottom:48px}.container .jumbotron,.container-fluid .jumbotron{padding-left:60px;padding-right:60px}.jumbotron h1,.jumbotron .h1{font-size:72px}}.thumbnail{display:block;padding:4px;margin-bottom:22px;line-height:1.42857143;background-color:#ffffff;border:1px solid #dddddd;border-radius:4px;-webkit-transition:border .2s ease-in-out;-o-transition:border .2s ease-in-out;transition:border .2s ease-in-out}.thumbnail>img,.thumbnail a>img{margin-left:auto;margin-right:auto}a.thumbnail:hover,a.thumbnail:focus,a.thumbnail.active{border-color:#4582ec}.thumbnail .caption{padding:9px;color:#333333}.alert{padding:15px;margin-bottom:22px;border:1px solid transparent;border-radius:4px}.alert h4{margin-top:0;color:inherit}.alert .alert-link{font-weight:bold}.alert>p,.alert>ul{margin-bottom:0}.alert>p+p{margin-top:5px}.alert-dismissable,.alert-dismissible{padding-right:35px}.alert-dismissable .close,.alert-dismissible .close{position:relative;top:-2px;right:-21px;color:inherit}.alert-success{background-color:#3fad46;border-color:#3fad46;color:#ffffff}.alert-success hr{border-top-color:#389a3e}.alert-success .alert-link{color:#e6e6e6}.alert-info{background-color:#5bc0de;border-color:#5bc0de;color:#ffffff}.alert-info hr{border-top-color:#46b8da}.alert-info .alert-link{color:#e6e6e6}.alert-warning{background-color:#f0ad4e;border-color:#f0ad4e;color:#ffffff}.alert-warning hr{border-top-color:#eea236}.alert-warning .alert-link{color:#e6e6e6}.alert-danger{background-color:#d9534f;border-color:#d9534f;color:#ffffff}.alert-danger hr{border-top-color:#d43f3a}.alert-danger .alert-link{color:#e6e6e6}@-webkit-keyframes progress-bar-stripes{from{background-position:40px 0}to{background-position:0 0}}@-o-keyframes progress-bar-stripes{from{background-position:40px 0}to{background-position:0 0}}@keyframes progress-bar-stripes{from{background-position:40px 0}to{background-position:0 0}}.progress{overflow:hidden;height:22px;margin-bottom:22px;background-color:#f5f5f5;border-radius:4px;-webkit-box-shadow:inset 0 1px 2px rgba(0,0,0,0.1);box-shadow:inset 0 1px 2px rgba(0,0,0,0.1)}.progress-bar{float:left;width:0%;height:100%;font-size:14px;line-height:22px;color:#ffffff;text-align:center;background-color:#4582ec;-webkit-box-shadow:inset 0 -1px 0 rgba(0,0,0,0.15);box-shadow:inset 0 -1px 0 rgba(0,0,0,0.15);-webkit-transition:width 0.6s ease;-o-transition:width 0.6s ease;transition:width 0.6s ease}.progress-striped .progress-bar,.progress-bar-striped{background-image:-webkit-linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);background-image:-o-linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);background-image:linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);-webkit-background-size:40px 40px;background-size:40px 40px}.progress.active .progress-bar,.progress-bar.active{-webkit-animation:progress-bar-stripes 2s linear infinite;-o-animation:progress-bar-stripes 2s linear infinite;animation:progress-bar-stripes 2s linear infinite}.progress-bar-success{background-color:#3fad46}.progress-striped .progress-bar-success{background-image:-webkit-linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);background-image:-o-linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);background-image:linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent)}.progress-bar-info{background-color:#5bc0de}.progress-striped .progress-bar-info{background-image:-webkit-linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);background-image:-o-linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);background-image:linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent)}.progress-bar-warning{background-color:#f0ad4e}.progress-striped .progress-bar-warning{background-image:-webkit-linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);background-image:-o-linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);background-image:linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent)}.progress-bar-danger{background-color:#d9534f}.progress-striped .progress-bar-danger{background-image:-webkit-linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);background-image:-o-linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent);background-image:linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent)}.media{margin-top:15px}.media:first-child{margin-top:0}.media,.media-body{zoom:1;overflow:hidden}.media-body{width:10000px}.media-object{display:block}.media-object.img-thumbnail{max-width:none}.media-right,.media>.pull-right{padding-left:10px}.media-left,.media>.pull-left{padding-right:10px}.media-left,.media-right,.media-body{display:table-cell;vertical-align:top}.media-middle{vertical-align:middle}.media-bottom{vertical-align:bottom}.media-heading{margin-top:0;margin-bottom:5px}.media-list{padding-left:0;list-style:none}.list-group{margin-bottom:20px;padding-left:0}.list-group-item{position:relative;display:block;padding:10px 15px;margin-bottom:-1px;background-color:#ffffff;border:1px solid #dddddd}.list-group-item:first-child{border-top-right-radius:4px;border-top-left-radius:4px}.list-group-item:last-child{margin-bottom:0;border-bottom-right-radius:4px;border-bottom-left-radius:4px}a.list-group-item,button.list-group-item{color:#555555}a.list-group-item .list-group-item-heading,button.list-group-item .list-group-item-heading{color:#333333}a.list-group-item:hover,button.list-group-item:hover,a.list-group-item:focus,button.list-group-item:focus{text-decoration:none;color:#555555;background-color:#f5f5f5}button.list-group-item{width:100%;text-align:left}.list-group-item.disabled,.list-group-item.disabled:hover,.list-group-item.disabled:focus{background-color:#eeeeee;color:#b3b3b3;cursor:not-allowed}.list-group-item.disabled .list-group-item-heading,.list-group-item.disabled:hover .list-group-item-heading,.list-group-item.disabled:focus .list-group-item-heading{color:inherit}.list-group-item.disabled .list-group-item-text,.list-group-item.disabled:hover .list-group-item-text,.list-group-item.disabled:focus .list-group-item-text{color:#b3b3b3}.list-group-item.active,.list-group-item.active:hover,.list-group-item.active:focus{z-index:2;color:#ffffff;background-color:#4582ec;border-color:#4582ec}.list-group-item.active .list-group-item-heading,.list-group-item.active:hover .list-group-item-heading,.list-group-item.active:focus .list-group-item-heading,.list-group-item.active .list-group-item-heading>small,.list-group-item.active:hover .list-group-item-heading>small,.list-group-item.active:focus .list-group-item-heading>small,.list-group-item.active .list-group-item-heading>.small,.list-group-item.active:hover .list-group-item-heading>.small,.list-group-item.active:focus .list-group-item-heading>.small{color:inherit}.list-group-item.active .list-group-item-text,.list-group-item.active:hover .list-group-item-text,.list-group-item.active:focus .list-group-item-text{color:#fefeff}.list-group-item-success{color:#3fad46;background-color:#dff0d8}a.list-group-item-success,button.list-group-item-success{color:#3fad46}a.list-group-item-success .list-group-item-heading,button.list-group-item-success .list-group-item-heading{color:inherit}a.list-group-item-success:hover,button.list-group-item-success:hover,a.list-group-item-success:focus,button.list-group-item-success:focus{color:#3fad46;background-color:#d0e9c6}a.list-group-item-success.active,button.list-group-item-success.active,a.list-group-item-success.active:hover,button.list-group-item-success.active:hover,a.list-group-item-success.active:focus,button.list-group-item-success.active:focus{color:#fff;background-color:#3fad46;border-color:#3fad46}.list-group-item-info{color:#5bc0de;background-color:#d9edf7}a.list-group-item-info,button.list-group-item-info{color:#5bc0de}a.list-group-item-info .list-group-item-heading,button.list-group-item-info .list-group-item-heading{color:inherit}a.list-group-item-info:hover,button.list-group-item-info:hover,a.list-group-item-info:focus,button.list-group-item-info:focus{color:#5bc0de;background-color:#c4e3f3}a.list-group-item-info.active,button.list-group-item-info.active,a.list-group-item-info.active:hover,button.list-group-item-info.active:hover,a.list-group-item-info.active:focus,button.list-group-item-info.active:focus{color:#fff;background-color:#5bc0de;border-color:#5bc0de}.list-group-item-warning{color:#f0ad4e;background-color:#fcf8e3}a.list-group-item-warning,button.list-group-item-warning{color:#f0ad4e}a.list-group-item-warning .list-group-item-heading,button.list-group-item-warning .list-group-item-heading{color:inherit}a.list-group-item-warning:hover,button.list-group-item-warning:hover,a.list-group-item-warning:focus,button.list-group-item-warning:focus{color:#f0ad4e;background-color:#faf2cc}a.list-group-item-warning.active,button.list-group-item-warning.active,a.list-group-item-warning.active:hover,button.list-group-item-warning.active:hover,a.list-group-item-warning.active:focus,button.list-group-item-warning.active:focus{color:#fff;background-color:#f0ad4e;border-color:#f0ad4e}.list-group-item-danger{color:#d9534f;background-color:#f2dede}a.list-group-item-danger,button.list-group-item-danger{color:#d9534f}a.list-group-item-danger .list-group-item-heading,button.list-group-item-danger .list-group-item-heading{color:inherit}a.list-group-item-danger:hover,button.list-group-item-danger:hover,a.list-group-item-danger:focus,button.list-group-item-danger:focus{color:#d9534f;background-color:#ebcccc}a.list-group-item-danger.active,button.list-group-item-danger.active,a.list-group-item-danger.active:hover,button.list-group-item-danger.active:hover,a.list-group-item-danger.active:focus,button.list-group-item-danger.active:focus{color:#fff;background-color:#d9534f;border-color:#d9534f}.list-group-item-heading{margin-top:0;margin-bottom:5px}.list-group-item-text{margin-bottom:0;line-height:1.3}.panel{margin-bottom:22px;background-color:#ffffff;border:1px solid transparent;border-radius:4px;-webkit-box-shadow:0 1px 1px rgba(0,0,0,0.05);box-shadow:0 1px 1px rgba(0,0,0,0.05)}.panel-body{padding:15px}.panel-heading{padding:10px 15px;border-bottom:1px solid transparent;border-top-right-radius:3px;border-top-left-radius:3px}.panel-heading>.dropdown .dropdown-toggle{color:inherit}.panel-title{margin-top:0;margin-bottom:0;font-size:18px;color:inherit}.panel-title>a,.panel-title>small,.panel-title>.small,.panel-title>small>a,.panel-title>.small>a{color:inherit}.panel-footer{padding:10px 15px;background-color:#ffffff;border-top:1px solid #dddddd;border-bottom-right-radius:3px;border-bottom-left-radius:3px}.panel>.list-group,.panel>.panel-collapse>.list-group{margin-bottom:0}.panel>.list-group .list-group-item,.panel>.panel-collapse>.list-group .list-group-item{border-width:1px 0;border-radius:0}.panel>.list-group:first-child .list-group-item:first-child,.panel>.panel-collapse>.list-group:first-child .list-group-item:first-child{border-top:0;border-top-right-radius:3px;border-top-left-radius:3px}.panel>.list-group:last-child .list-group-item:last-child,.panel>.panel-collapse>.list-group:last-child .list-group-item:last-child{border-bottom:0;border-bottom-right-radius:3px;border-bottom-left-radius:3px}.panel>.panel-heading+.panel-collapse>.list-group .list-group-item:first-child{border-top-right-radius:0;border-top-left-radius:0}.panel-heading+.list-group .list-group-item:first-child{border-top-width:0}.list-group+.panel-footer{border-top-width:0}.panel>.table,.panel>.table-responsive>.table,.panel>.panel-collapse>.table{margin-bottom:0}.panel>.table caption,.panel>.table-responsive>.table caption,.panel>.panel-collapse>.table caption{padding-left:15px;padding-right:15px}.panel>.table:first-child,.panel>.table-responsive:first-child>.table:first-child{border-top-right-radius:3px;border-top-left-radius:3px}.panel>.table:first-child>thead:first-child>tr:first-child,.panel>.table-responsive:first-child>.table:first-child>thead:first-child>tr:first-child,.panel>.table:first-child>tbody:first-child>tr:first-child,.panel>.table-responsive:first-child>.table:first-child>tbody:first-child>tr:first-child{border-top-left-radius:3px;border-top-right-radius:3px}.panel>.table:first-child>thead:first-child>tr:first-child td:first-child,.panel>.table-responsive:first-child>.table:first-child>thead:first-child>tr:first-child td:first-child,.panel>.table:first-child>tbody:first-child>tr:first-child td:first-child,.panel>.table-responsive:first-child>.table:first-child>tbody:first-child>tr:first-child td:first-child,.panel>.table:first-child>thead:first-child>tr:first-child th:first-child,.panel>.table-responsive:first-child>.table:first-child>thead:first-child>tr:first-child th:first-child,.panel>.table:first-child>tbody:first-child>tr:first-child th:first-child,.panel>.table-responsive:first-child>.table:first-child>tbody:first-child>tr:first-child th:first-child{border-top-left-radius:3px}.panel>.table:first-child>thead:first-child>tr:first-child td:last-child,.panel>.table-responsive:first-child>.table:first-child>thead:first-child>tr:first-child td:last-child,.panel>.table:first-child>tbody:first-child>tr:first-child td:last-child,.panel>.table-responsive:first-child>.table:first-child>tbody:first-child>tr:first-child td:last-child,.panel>.table:first-child>thead:first-child>tr:first-child th:last-child,.panel>.table-responsive:first-child>.table:first-child>thead:first-child>tr:first-child th:last-child,.panel>.table:first-child>tbody:first-child>tr:first-child th:last-child,.panel>.table-responsive:first-child>.table:first-child>tbody:first-child>tr:first-child th:last-child{border-top-right-radius:3px}.panel>.table:last-child,.panel>.table-responsive:last-child>.table:last-child{border-bottom-right-radius:3px;border-bottom-left-radius:3px}.panel>.table:last-child>tbody:last-child>tr:last-child,.panel>.table-responsive:last-child>.table:last-child>tbody:last-child>tr:last-child,.panel>.table:last-child>tfoot:last-child>tr:last-child,.panel>.table-responsive:last-child>.table:last-child>tfoot:last-child>tr:last-child{border-bottom-left-radius:3px;border-bottom-right-radius:3px}.panel>.table:last-child>tbody:last-child>tr:last-child td:first-child,.panel>.table-responsive:last-child>.table:last-child>tbody:last-child>tr:last-child td:first-child,.panel>.table:last-child>tfoot:last-child>tr:last-child td:first-child,.panel>.table-responsive:last-child>.table:last-child>tfoot:last-child>tr:last-child td:first-child,.panel>.table:last-child>tbody:last-child>tr:last-child th:first-child,.panel>.table-responsive:last-child>.table:last-child>tbody:last-child>tr:last-child th:first-child,.panel>.table:last-child>tfoot:last-child>tr:last-child th:first-child,.panel>.table-responsive:last-child>.table:last-child>tfoot:last-child>tr:last-child th:first-child{border-bottom-left-radius:3px}.panel>.table:last-child>tbody:last-child>tr:last-child td:last-child,.panel>.table-responsive:last-child>.table:last-child>tbody:last-child>tr:last-child td:last-child,.panel>.table:last-child>tfoot:last-child>tr:last-child td:last-child,.panel>.table-responsive:last-child>.table:last-child>tfoot:last-child>tr:last-child td:last-child,.panel>.table:last-child>tbody:last-child>tr:last-child th:last-child,.panel>.table-responsive:last-child>.table:last-child>tbody:last-child>tr:last-child th:last-child,.panel>.table:last-child>tfoot:last-child>tr:last-child th:last-child,.panel>.table-responsive:last-child>.table:last-child>tfoot:last-child>tr:last-child th:last-child{border-bottom-right-radius:3px}.panel>.panel-body+.table,.panel>.panel-body+.table-responsive,.panel>.table+.panel-body,.panel>.table-responsive+.panel-body{border-top:1px solid #dddddd}.panel>.table>tbody:first-child>tr:first-child th,.panel>.table>tbody:first-child>tr:first-child td{border-top:0}.panel>.table-bordered,.panel>.table-responsive>.table-bordered{border:0}.panel>.table-bordered>thead>tr>th:first-child,.panel>.table-responsive>.table-bordered>thead>tr>th:first-child,.panel>.table-bordered>tbody>tr>th:first-child,.panel>.table-responsive>.table-bordered>tbody>tr>th:first-child,.panel>.table-bordered>tfoot>tr>th:first-child,.panel>.table-responsive>.table-bordered>tfoot>tr>th:first-child,.panel>.table-bordered>thead>tr>td:first-child,.panel>.table-responsive>.table-bordered>thead>tr>td:first-child,.panel>.table-bordered>tbody>tr>td:first-child,.panel>.table-responsive>.table-bordered>tbody>tr>td:first-child,.panel>.table-bordered>tfoot>tr>td:first-child,.panel>.table-responsive>.table-bordered>tfoot>tr>td:first-child{border-left:0}.panel>.table-bordered>thead>tr>th:last-child,.panel>.table-responsive>.table-bordered>thead>tr>th:last-child,.panel>.table-bordered>tbody>tr>th:last-child,.panel>.table-responsive>.table-bordered>tbody>tr>th:last-child,.panel>.table-bordered>tfoot>tr>th:last-child,.panel>.table-responsive>.table-bordered>tfoot>tr>th:last-child,.panel>.table-bordered>thead>tr>td:last-child,.panel>.table-responsive>.table-bordered>thead>tr>td:last-child,.panel>.table-bordered>tbody>tr>td:last-child,.panel>.table-responsive>.table-bordered>tbody>tr>td:last-child,.panel>.table-bordered>tfoot>tr>td:last-child,.panel>.table-responsive>.table-bordered>tfoot>tr>td:last-child{border-right:0}.panel>.table-bordered>thead>tr:first-child>td,.panel>.table-responsive>.table-bordered>thead>tr:first-child>td,.panel>.table-bordered>tbody>tr:first-child>td,.panel>.table-responsive>.table-bordered>tbody>tr:first-child>td,.panel>.table-bordered>thead>tr:first-child>th,.panel>.table-responsive>.table-bordered>thead>tr:first-child>th,.panel>.table-bordered>tbody>tr:first-child>th,.panel>.table-responsive>.table-bordered>tbody>tr:first-child>th{border-bottom:0}.panel>.table-bordered>tbody>tr:last-child>td,.panel>.table-responsive>.table-bordered>tbody>tr:last-child>td,.panel>.table-bordered>tfoot>tr:last-child>td,.panel>.table-responsive>.table-bordered>tfoot>tr:last-child>td,.panel>.table-bordered>tbody>tr:last-child>th,.panel>.table-responsive>.table-bordered>tbody>tr:last-child>th,.panel>.table-bordered>tfoot>tr:last-child>th,.panel>.table-responsive>.table-bordered>tfoot>tr:last-child>th{border-bottom:0}.panel>.table-responsive{border:0;margin-bottom:0}.panel-group{margin-bottom:22px}.panel-group .panel{margin-bottom:0;border-radius:4px}.panel-group .panel+.panel{margin-top:5px}.panel-group .panel-heading{border-bottom:0}.panel-group .panel-heading+.panel-collapse>.panel-body,.panel-group .panel-heading+.panel-collapse>.list-group{border-top:1px solid #dddddd}.panel-group .panel-footer{border-top:0}.panel-group .panel-footer+.panel-collapse .panel-body{border-bottom:1px solid #dddddd}.panel-default{border-color:#dddddd}.panel-default>.panel-heading{color:#333333;background-color:#f5f5f5;border-color:#dddddd}.panel-default>.panel-heading+.panel-collapse>.panel-body{border-top-color:#dddddd}.panel-default>.panel-heading .badge{color:#f5f5f5;background-color:#333333}.panel-default>.panel-footer+.panel-collapse>.panel-body{border-bottom-color:#dddddd}.panel-primary{border-color:#4582ec}.panel-primary>.panel-heading{color:#ffffff;background-color:#4582ec;border-color:#4582ec}.panel-primary>.panel-heading+.panel-collapse>.panel-body{border-top-color:#4582ec}.panel-primary>.panel-heading .badge{color:#4582ec;background-color:#ffffff}.panel-primary>.panel-footer+.panel-collapse>.panel-body{border-bottom-color:#4582ec}.panel-success{border-color:#3fad46}.panel-success>.panel-heading{color:#ffffff;background-color:#3fad46;border-color:#3fad46}.panel-success>.panel-heading+.panel-collapse>.panel-body{border-top-color:#3fad46}.panel-success>.panel-heading .badge{color:#3fad46;background-color:#ffffff}.panel-success>.panel-footer+.panel-collapse>.panel-body{border-bottom-color:#3fad46}.panel-info{border-color:#5bc0de}.panel-info>.panel-heading{color:#ffffff;background-color:#5bc0de;border-color:#5bc0de}.panel-info>.panel-heading+.panel-collapse>.panel-body{border-top-color:#5bc0de}.panel-info>.panel-heading .badge{color:#5bc0de;background-color:#ffffff}.panel-info>.panel-footer+.panel-collapse>.panel-body{border-bottom-color:#5bc0de}.panel-warning{border-color:#f0ad4e}.panel-warning>.panel-heading{color:#ffffff;background-color:#f0ad4e;border-color:#f0ad4e}.panel-warning>.panel-heading+.panel-collapse>.panel-body{border-top-color:#f0ad4e}.panel-warning>.panel-heading .badge{color:#f0ad4e;background-color:#ffffff}.panel-warning>.panel-footer+.panel-collapse>.panel-body{border-bottom-color:#f0ad4e}.panel-danger{border-color:#d9534f}.panel-danger>.panel-heading{color:#ffffff;background-color:#d9534f;border-color:#d9534f}.panel-danger>.panel-heading+.panel-collapse>.panel-body{border-top-color:#d9534f}.panel-danger>.panel-heading .badge{color:#d9534f;background-color:#ffffff}.panel-danger>.panel-footer+.panel-collapse>.panel-body{border-bottom-color:#d9534f}.embed-responsive{position:relative;display:block;height:0;padding:0;overflow:hidden}.embed-responsive .embed-responsive-item,.embed-responsive iframe,.embed-responsive embed,.embed-responsive object,.embed-responsive video{position:absolute;top:0;left:0;bottom:0;height:100%;width:100%;border:0}.embed-responsive-16by9{padding-bottom:56.25%}.embed-responsive-4by3{padding-bottom:75%}.well{min-height:20px;padding:19px;margin-bottom:20px;background-color:#f7f7f7;border:1px solid #e5e5e5;border-radius:4px;-webkit-box-shadow:inset 0 1px 1px rgba(0,0,0,0.05);box-shadow:inset 0 1px 1px rgba(0,0,0,0.05)}.well blockquote{border-color:#ddd;border-color:rgba(0,0,0,0.15)}.well-lg{padding:24px;border-radius:6px}.well-sm{padding:9px;border-radius:3px}.close{float:right;font-size:24px;font-weight:bold;line-height:1;color:#ffffff;text-shadow:0 1px 0 #ffffff;opacity:0.2;filter:alpha(opacity=20)}.close:hover,.close:focus{color:#ffffff;text-decoration:none;cursor:pointer;opacity:0.5;filter:alpha(opacity=50)}button.close{padding:0;cursor:pointer;background:transparent;border:0;-webkit-appearance:none}.modal-open{overflow:hidden}.modal{display:none;overflow:hidden;position:fixed;top:0;right:0;bottom:0;left:0;z-index:1050;-webkit-overflow-scrolling:touch;outline:0}.modal.fade .modal-dialog{-webkit-transform:translate(0, -25%);-ms-transform:translate(0, -25%);-o-transform:translate(0, -25%);transform:translate(0, -25%);-webkit-transition:-webkit-transform .3s ease-out;-o-transition:-o-transform .3s ease-out;transition:transform .3s ease-out}.modal.in .modal-dialog{-webkit-transform:translate(0, 0);-ms-transform:translate(0, 0);-o-transform:translate(0, 0);transform:translate(0, 0)}.modal-open .modal{overflow-x:hidden;overflow-y:auto}.modal-dialog{position:relative;width:auto;margin:10px}.modal-content{position:relative;background-color:#ffffff;border:1px solid #999999;border:1px solid rgba(0,0,0,0.2);border-radius:6px;-webkit-box-shadow:0 3px 9px rgba(0,0,0,0.5);box-shadow:0 3px 9px rgba(0,0,0,0.5);-webkit-background-clip:padding-box;background-clip:padding-box;outline:0}.modal-backdrop{position:fixed;top:0;right:0;bottom:0;left:0;z-index:1040;background-color:#000000}.modal-backdrop.fade{opacity:0;filter:alpha(opacity=0)}.modal-backdrop.in{opacity:0.5;filter:alpha(opacity=50)}.modal-header{padding:15px;border-bottom:1px solid #e5e5e5}.modal-header .close{margin-top:-2px}.modal-title{margin:0;line-height:1.42857143}.modal-body{position:relative;padding:20px}.modal-footer{padding:20px;text-align:right;border-top:1px solid #e5e5e5}.modal-footer .btn+.btn{margin-left:5px;margin-bottom:0}.modal-footer .btn-group .btn+.btn{margin-left:-1px}.modal-footer .btn-block+.btn-block{margin-left:0}.modal-scrollbar-measure{position:absolute;top:-9999px;width:50px;height:50px;overflow:scroll}@media (min-width:768px){.modal-dialog{width:600px;margin:30px auto}.modal-content{-webkit-box-shadow:0 5px 15px rgba(0,0,0,0.5);box-shadow:0 5px 15px rgba(0,0,0,0.5)}.modal-sm{width:300px}}@media (min-width:992px){.modal-lg{width:900px}}.tooltip{position:absolute;z-index:1070;display:block;font-family:Georgia,"Times New Roman",Times,serif;font-style:normal;font-weight:normal;letter-spacing:normal;line-break:auto;line-height:1.42857143;text-align:left;text-align:start;text-decoration:none;text-shadow:none;text-transform:none;white-space:normal;word-break:normal;word-spacing:normal;word-wrap:normal;font-size:14px;opacity:0;filter:alpha(opacity=0)}.tooltip.in{opacity:0.9;filter:alpha(opacity=90)}.tooltip.top{margin-top:-3px;padding:5px 0}.tooltip.right{margin-left:3px;padding:0 5px}.tooltip.bottom{margin-top:3px;padding:5px 0}.tooltip.left{margin-left:-3px;padding:0 5px}.tooltip-inner{max-width:200px;padding:3px 8px;color:#ffffff;text-align:center;background-color:#000000;border-radius:4px}.tooltip-arrow{position:absolute;width:0;height:0;border-color:transparent;border-style:solid}.tooltip.top .tooltip-arrow{bottom:0;left:50%;margin-left:-5px;border-width:5px 5px 0;border-top-color:#000000}.tooltip.top-left .tooltip-arrow{bottom:0;right:5px;margin-bottom:-5px;border-width:5px 5px 0;border-top-color:#000000}.tooltip.top-right .tooltip-arrow{bottom:0;left:5px;margin-bottom:-5px;border-width:5px 5px 0;border-top-color:#000000}.tooltip.right .tooltip-arrow{top:50%;left:0;margin-top:-5px;border-width:5px 5px 5px 0;border-right-color:#000000}.tooltip.left .tooltip-arrow{top:50%;right:0;margin-top:-5px;border-width:5px 0 5px 5px;border-left-color:#000000}.tooltip.bottom .tooltip-arrow{top:0;left:50%;margin-left:-5px;border-width:0 5px 5px;border-bottom-color:#000000}.tooltip.bottom-left .tooltip-arrow{top:0;right:5px;margin-top:-5px;border-width:0 5px 5px;border-bottom-color:#000000}.tooltip.bottom-right .tooltip-arrow{top:0;left:5px;margin-top:-5px;border-width:0 5px 5px;border-bottom-color:#000000}.popover{position:absolute;top:0;left:0;z-index:1060;display:none;max-width:276px;padding:1px;font-family:Georgia,"Times New Roman",Times,serif;font-style:normal;font-weight:normal;letter-spacing:normal;line-break:auto;line-height:1.42857143;text-align:left;text-align:start;text-decoration:none;text-shadow:none;text-transform:none;white-space:normal;word-break:normal;word-spacing:normal;word-wrap:normal;font-size:16px;background-color:#ffffff;-webkit-background-clip:padding-box;background-clip:padding-box;border:1px solid #cccccc;border:1px solid rgba(0,0,0,0.2);border-radius:6px;-webkit-box-shadow:0 5px 10px rgba(0,0,0,0.2);box-shadow:0 5px 10px rgba(0,0,0,0.2)}.popover.top{margin-top:-10px}.popover.right{margin-left:10px}.popover.bottom{margin-top:10px}.popover.left{margin-left:-10px}.popover-title{margin:0;padding:8px 14px;font-size:16px;background-color:#f7f7f7;border-bottom:1px solid #ebebeb;border-radius:5px 5px 0 0}.popover-content{padding:9px 14px}.popover>.arrow,.popover>.arrow:after{position:absolute;display:block;width:0;height:0;border-color:transparent;border-style:solid}.popover>.arrow{border-width:11px}.popover>.arrow:after{border-width:10px;content:""}.popover.top>.arrow{left:50%;margin-left:-11px;border-bottom-width:0;border-top-color:#999999;border-top-color:rgba(0,0,0,0.25);bottom:-11px}.popover.top>.arrow:after{content:" ";bottom:1px;margin-left:-10px;border-bottom-width:0;border-top-color:#ffffff}.popover.right>.arrow{top:50%;left:-11px;margin-top:-11px;border-left-width:0;border-right-color:#999999;border-right-color:rgba(0,0,0,0.25)}.popover.right>.arrow:after{content:" ";left:1px;bottom:-10px;border-left-width:0;border-right-color:#ffffff}.popover.bottom>.arrow{left:50%;margin-left:-11px;border-top-width:0;border-bottom-color:#999999;border-bottom-color:rgba(0,0,0,0.25);top:-11px}.popover.bottom>.arrow:after{content:" ";top:1px;margin-left:-10px;border-top-width:0;border-bottom-color:#ffffff}.popover.left>.arrow{top:50%;right:-11px;margin-top:-11px;border-right-width:0;border-left-color:#999999;border-left-color:rgba(0,0,0,0.25)}.popover.left>.arrow:after{content:" ";right:1px;border-right-width:0;border-left-color:#ffffff;bottom:-10px}.carousel{position:relative}.carousel-inner{position:relative;overflow:hidden;width:100%}.carousel-inner>.item{display:none;position:relative;-webkit-transition:.6s ease-in-out left;-o-transition:.6s ease-in-out left;transition:.6s ease-in-out left}.carousel-inner>.item>img,.carousel-inner>.item>a>img{line-height:1}@media all and (transform-3d),(-webkit-transform-3d){.carousel-inner>.item{-webkit-transition:-webkit-transform .6s ease-in-out;-o-transition:-o-transform .6s ease-in-out;transition:transform .6s ease-in-out;-webkit-backface-visibility:hidden;backface-visibility:hidden;-webkit-perspective:1000px;perspective:1000px}.carousel-inner>.item.next,.carousel-inner>.item.active.right{-webkit-transform:translate3d(100%, 0, 0);transform:translate3d(100%, 0, 0);left:0}.carousel-inner>.item.prev,.carousel-inner>.item.active.left{-webkit-transform:translate3d(-100%, 0, 0);transform:translate3d(-100%, 0, 0);left:0}.carousel-inner>.item.next.left,.carousel-inner>.item.prev.right,.carousel-inner>.item.active{-webkit-transform:translate3d(0, 0, 0);transform:translate3d(0, 0, 0);left:0}}.carousel-inner>.active,.carousel-inner>.next,.carousel-inner>.prev{display:block}.carousel-inner>.active{left:0}.carousel-inner>.next,.carousel-inner>.prev{position:absolute;top:0;width:100%}.carousel-inner>.next{left:100%}.carousel-inner>.prev{left:-100%}.carousel-inner>.next.left,.carousel-inner>.prev.right{left:0}.carousel-inner>.active.left{left:-100%}.carousel-inner>.active.right{left:100%}.carousel-control{position:absolute;top:0;left:0;bottom:0;width:15%;opacity:0.5;filter:alpha(opacity=50);font-size:20px;color:#ffffff;text-align:center;text-shadow:0 1px 2px rgba(0,0,0,0.6);background-color:rgba(0,0,0,0)}.carousel-control.left{background-image:-webkit-linear-gradient(left, rgba(0,0,0,0.5) 0, rgba(0,0,0,0.0001) 100%);background-image:-o-linear-gradient(left, rgba(0,0,0,0.5) 0, rgba(0,0,0,0.0001) 100%);background-image:-webkit-gradient(linear, left top, right top, from(rgba(0,0,0,0.5)), to(rgba(0,0,0,0.0001)));background-image:linear-gradient(to right, rgba(0,0,0,0.5) 0, rgba(0,0,0,0.0001) 100%);background-repeat:repeat-x;filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#80000000', endColorstr='#00000000', GradientType=1)}.carousel-control.right{left:auto;right:0;background-image:-webkit-linear-gradient(left, rgba(0,0,0,0.0001) 0, rgba(0,0,0,0.5) 100%);background-image:-o-linear-gradient(left, rgba(0,0,0,0.0001) 0, rgba(0,0,0,0.5) 100%);background-image:-webkit-gradient(linear, left top, right top, from(rgba(0,0,0,0.0001)), to(rgba(0,0,0,0.5)));background-image:linear-gradient(to right, rgba(0,0,0,0.0001) 0, rgba(0,0,0,0.5) 100%);background-repeat:repeat-x;filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#00000000', endColorstr='#80000000', GradientType=1)}.carousel-control:hover,.carousel-control:focus{outline:0;color:#ffffff;text-decoration:none;opacity:0.9;filter:alpha(opacity=90)}.carousel-control .icon-prev,.carousel-control .icon-next,.carousel-control .glyphicon-chevron-left,.carousel-control .glyphicon-chevron-right{position:absolute;top:50%;margin-top:-10px;z-index:5;display:inline-block}.carousel-control .icon-prev,.carousel-control .glyphicon-chevron-left{left:50%;margin-left:-10px}.carousel-control .icon-next,.carousel-control .glyphicon-chevron-right{right:50%;margin-right:-10px}.carousel-control .icon-prev,.carousel-control .icon-next{width:20px;height:20px;line-height:1;font-family:serif}.carousel-control .icon-prev:before{content:'\2039'}.carousel-control .icon-next:before{content:'\203a'}.carousel-indicators{position:absolute;bottom:10px;left:50%;z-index:15;width:60%;margin-left:-30%;padding-left:0;list-style:none;text-align:center}.carousel-indicators li{display:inline-block;width:10px;height:10px;margin:1px;text-indent:-999px;border:1px solid #ffffff;border-radius:10px;cursor:pointer;background-color:#000 \9;background-color:rgba(0,0,0,0)}.carousel-indicators .active{margin:0;width:12px;height:12px;background-color:#ffffff}.carousel-caption{position:absolute;left:15%;right:15%;bottom:20px;z-index:10;padding-top:20px;padding-bottom:20px;color:#ffffff;text-align:center;text-shadow:0 1px 2px rgba(0,0,0,0.6)}.carousel-caption .btn{text-shadow:none}@media screen and (min-width:768px){.carousel-control .glyphicon-chevron-left,.carousel-control .glyphicon-chevron-right,.carousel-control .icon-prev,.carousel-control .icon-next{width:30px;height:30px;margin-top:-10px;font-size:30px}.carousel-control .glyphicon-chevron-left,.carousel-control .icon-prev{margin-left:-10px}.carousel-control .glyphicon-chevron-right,.carousel-control .icon-next{margin-right:-10px}.carousel-caption{left:20%;right:20%;padding-bottom:30px}.carousel-indicators{bottom:20px}}.clearfix:before,.clearfix:after,.dl-horizontal dd:before,.dl-horizontal dd:after,.container:before,.container:after,.container-fluid:before,.container-fluid:after,.row:before,.row:after,.form-horizontal .form-group:before,.form-horizontal .form-group:after,.btn-toolbar:before,.btn-toolbar:after,.btn-group-vertical>.btn-group:before,.btn-group-vertical>.btn-group:after,.nav:before,.nav:after,.navbar:before,.navbar:after,.navbar-header:before,.navbar-header:after,.navbar-collapse:before,.navbar-collapse:after,.pager:before,.pager:after,.panel-body:before,.panel-body:after,.modal-header:before,.modal-header:after,.modal-footer:before,.modal-footer:after{content:" ";display:table}.clearfix:after,.dl-horizontal dd:after,.container:after,.container-fluid:after,.row:after,.form-horizontal .form-group:after,.btn-toolbar:after,.btn-group-vertical>.btn-group:after,.nav:after,.navbar:after,.navbar-header:after,.navbar-collapse:after,.pager:after,.panel-body:after,.modal-header:after,.modal-footer:after{clear:both}.center-block{display:block;margin-left:auto;margin-right:auto}.pull-right{float:right !important}.pull-left{float:left !important}.hide{display:none !important}.show{display:block !important}.invisible{visibility:hidden}.text-hide{font:0/0 a;color:transparent;text-shadow:none;background-color:transparent;border:0}.hidden{display:none !important}.affix{position:fixed}@-ms-viewport{width:device-width}.visible-xs,.visible-sm,.visible-md,.visible-lg{display:none !important}.visible-xs-block,.visible-xs-inline,.visible-xs-inline-block,.visible-sm-block,.visible-sm-inline,.visible-sm-inline-block,.visible-md-block,.visible-md-inline,.visible-md-inline-block,.visible-lg-block,.visible-lg-inline,.visible-lg-inline-block{display:none !important}@media (max-width:767px){.visible-xs{display:block !important}table.visible-xs{display:table !important}tr.visible-xs{display:table-row !important}th.visible-xs,td.visible-xs{display:table-cell !important}}@media (max-width:767px){.visible-xs-block{display:block !important}}@media (max-width:767px){.visible-xs-inline{display:inline !important}}@media (max-width:767px){.visible-xs-inline-block{display:inline-block !important}}@media (min-width:768px) and (max-width:991px){.visible-sm{display:block !important}table.visible-sm{display:table !important}tr.visible-sm{display:table-row !important}th.visible-sm,td.visible-sm{display:table-cell !important}}@media (min-width:768px) and (max-width:991px){.visible-sm-block{display:block !important}}@media (min-width:768px) and (max-width:991px){.visible-sm-inline{display:inline !important}}@media (min-width:768px) and (max-width:991px){.visible-sm-inline-block{display:inline-block !important}}@media (min-width:992px) and (max-width:1199px){.visible-md{display:block !important}table.visible-md{display:table !important}tr.visible-md{display:table-row !important}th.visible-md,td.visible-md{display:table-cell !important}}@media (min-width:992px) and (max-width:1199px){.visible-md-block{display:block !important}}@media (min-width:992px) and (max-width:1199px){.visible-md-inline{display:inline !important}}@media (min-width:992px) and (max-width:1199px){.visible-md-inline-block{display:inline-block !important}}@media (min-width:1200px){.visible-lg{display:block !important}table.visible-lg{display:table !important}tr.visible-lg{display:table-row !important}th.visible-lg,td.visible-lg{display:table-cell !important}}@media (min-width:1200px){.visible-lg-block{display:block !important}}@media (min-width:1200px){.visible-lg-inline{display:inline !important}}@media (min-width:1200px){.visible-lg-inline-block{display:inline-block !important}}@media (max-width:767px){.hidden-xs{display:none !important}}@media (min-width:768px) and (max-width:991px){.hidden-sm{display:none !important}}@media (min-width:992px) and (max-width:1199px){.hidden-md{display:none !important}}@media (min-width:1200px){.hidden-lg{display:none !important}}.visible-print{display:none !important}@media print{.visible-print{display:block !important}table.visible-print{display:table !important}tr.visible-print{display:table-row !important}th.visible-print,td.visible-print{display:table-cell !important}}.visible-print-block{display:none !important}@media print{.visible-print-block{display:block !important}}.visible-print-inline{display:none !important}@media print{.visible-print-inline{display:inline !important}}.visible-print-inline-block{display:none !important}@media print{.visible-print-inline-block{display:inline-block !important}}@media print{.hidden-print{display:none !important}}.navbar{font-family:"Georgia","Helvetica Neue",Helvetica,Arial,sans-serif}.navbar-nav,.navbar-form{margin-left:0;margin-right:0}.navbar-nav>li>a{margin:12.5px 6px;padding:8px 12px;border:1px solid transparent;border-radius:4px}.navbar-nav>li>a:hover{border:1px solid #ddd}.navbar-nav>.active>a,.navbar-nav>.active>a:hover{border:1px solid #ddd}.navbar-default .navbar-nav>.active>a:hover{color:#4582ec}.navbar-inverse .navbar-nav>.active>a:hover{color:#333333}.navbar-brand{padding-top:12.5px;padding-bottom:12.5px;line-height:1.9}@media (min-width:768px){.navbar .navbar-nav>li>a{padding:8px 12px}}@media (max-width:767px){.navbar .navbar-nav>li>a{margin:0}}.btn{font-family:"Georgia","Helvetica Neue",Helvetica,Arial,sans-serif}legend{font-family:"Georgia","Helvetica Neue",Helvetica,Arial,sans-serif}.input-group-addon{font-family:"Georgia","Helvetica Neue",Helvetica,Arial,sans-serif}.nav .open>a,.nav .open>a:hover,.nav .open>a:focus{border:1px solid #ddd}.pagination{font-family:"Georgia","Helvetica Neue",Helvetica,Arial,sans-serif}.pagination-lg>li>a,.pagination-lg>li>span{padding:14px 24px}.pager{font-family:"Georgia","Helvetica Neue",Helvetica,Arial,sans-serif}.pager a{color:#333333}.pager a:hover{border-color:transparent;color:#fff}.pager .disabled a{border-color:#dddddd}.close{color:#fff;text-decoration:none;text-shadow:none;opacity:0.4}.close:hover,.close:focus{color:#fff;opacity:1}.alert .alert-link{color:#ffffff;text-decoration:underline}.label{font-family:Georgia;font-weight:normal}.label-default{border:1px solid #ddd;color:#333333}.badge{padding:1px 7px 5px;vertical-align:2px;font-family:Georgia;font-weight:normal}.panel{-webkit-box-shadow:none;box-shadow:none}.panel-default .close{color:#333333}.modal .close{color:#333333}
</style>
<style>h1 {font-size: 34px;}
h1.title {font-size: 40px;}
h1 {font-size: 30px;}
h2 {font-size: 30px;}
h3 {font-size: 24px;}
h4 {font-size: 18px;}
h5 {font-size: 16px;}
h6 {font-size: 12px;}
code {color: inherit; background-color: rgba(0, 0, 0, 0.04);}
pre:not([class]) { background-color: white }</style>

<header id="header" class="header-glossario">
	<nav class="menu-topo-glossario">
		<!-- MENU MOBILE -->
		<div class="menu-mobile">
			<div class="logo_museu logo-mpeg-mob" aria-label="logo MPEG">

			</div>
		</div>
		<!-- FIM MENU MOBILE -->


		<!-- MENU DESKTOP -->
		<div class="glossario-menu">
			<div class="logo_museu logo-mpeg">

			</div>
			<div class="menu-middle">

			</div>

			<div class="pesquisar-box">
				<div id="barrabusca">
					<input type="text" id="searchbar" onkeyup="valida_busca()"></input>
					<button class="botoes-busca" id="searchbtn" onclick='busca_entrada("Buscando...",true)' disabled>Buscar</button>
			</div>
			</div>
		</div>
		<div class="search-mobile">
			<div class="search-icon"></div>
		</div>
		<!-- FIM MENU DESKTOP -->
	</nav>
</header>

<style type="text/css">
code{white-space: pre-wrap;}
span.smallcaps{font-variant: small-caps;}
span.underline{text-decoration: underline;}
div.column{display: inline-block; vertical-align: top; width: 50%;}
div.hanging-indent{margin-left: 1.5em; text-indent: -1.5em;}
ul.task-list{list-style: none;}
</style>



<style type="text/css">
.main-container {
max-width: 900px;
margin-left: auto;
margin-right: auto;
}
img {
max-width:50%;
}
.tabbed-pane {
padding-top: 12px;
}
.html-widget {
margin-bottom: 20px;
}
button.code-folding-btn:focus {
outline: none;
}
summary {
display: list-item;
}
details > summary > p:only-child {
display: inline;
}
pre code {
padding: 0;
}
</style>

 <style type="text/css">
		:root {
			--imagem-fundo: url("data:image/png;base64,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");
			--cor-border: #4D4637;
			--cor-fundo-h1: #82bfa0;
			--cor-gradient-body: #fdf2c5;
			--cor-scrollbar-bg: #D0D4CE;
			--cor-scrollbar-thumb: #71806B;
			--cor-hover: #1D8563;
			--cor-menu-bg: #82bfa0;
			--cor-menu-hover: #555;
			--cor-menu-ativo: #1b1c1c;
			--cor-texto: #444;
			--cor-branco: #fff;
			--imagem-mouse-audio: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAAsTAAALEwEAmpwYAAABHUlEQVR4nO2VPU4CQRzFfxbSyAmEEk2wg0K5AoHeAmMPpYV0xhOQiAUcAQpCAjfRhh4OoJ18mDGbPJLJZnf2w9UGXrLJvJmX97L/+c8MHJEhnmNorn9jbiI0T8A30ExrbiJ0j9J8AoU05iZEcw/kNJ5IN0xivnUEPGj+VbwEbPQV45rfOgIqwBewA640N5K2YwsbwMpXjr05AQFd4FLjvtZ64i3xuaVn6TD3B+wNxuI34u/iF+ILQgyCYKz1osbeH3vIW93j4czHMwv4COGpSzQSr4m/uUpUjwgxAZvsGaEWtTf5TnyWRZtWgbXatKy5sbRtV0DSg/ZilSfWQUt6VZwCJ8BUukEc86AQF7pW95zzh9d1I6n5vzw4HC5+AAT2iNccEnX8AAAAAElFTkSuQmCC');
			--imagem-play-audio: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAcklEQVR4nO3UsQnDQBAF0YcS40QGt+EqXI47UR3uRVUIrBYUK9AawwUKnP7sBiYeuNtdOh3cmjFWbHhhSATq5IxHMlDYMeGSClRzwTMZKBx4454KVPM3CNdk4JMKHMknWlKfvCfHdE4s2po+FWOz0/GXLzgCStJo0g+2AAAAAElFTkSuQmCC');
			--imagem-stop-audio: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAKElEQVR4nGNgGAUjFvwnExMNRi0gCEaDiCAYDSKCYDSIBj6IRsEwAgDM+MM9I/6OSwAAAABJRU5ErkJggg==');
			--imagem-logo-museu: url("data:image/jpeg;base64,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");
			--audio-simbolo: url("data:image/png;base64,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");
			--video-simbolo: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAMAAAAM7l6QAAAAIGNIUk0AAHomAACAhAAA+gAAAIDoAAB1MAAA6mAAADqYAAAXcJy6UTwAAAJbUExURfzxxf7zxfXrv97UrdDHos7Goc/Goc7FoNjPqO7juf7yxv3yxf/1yNnQqZCLcWllUl9aSWNeTX55YsG4lvjtwfLnvJCKcBkYEwAAAAoJB2BcS9rRqsvCnldURAsKCB4cFx8eGR8dGB8eGCAfGRIRDi0qI6qjhbOri0M/NDMxKKCZfaihhKafgqegg6aega6niFlVRSEfGY+Ib0A9MkhFOOPasfDlu+3jue7kuuziuPjuwn14YYqEa6+niExKPPPpvv/2yP7zxv/0xv//z4aAaImEa0tJO/HmvPvxxPzxxP/1x/rvw//8zYV/Z0xJO//zxuLZsPvww//9zv/4ysG5ln54Yruyke7kufvwxP/6y7GpijUzKXt1X9TLpSQjHB4dGF1ZSKCZfCgnHwQEAwEBAS4sJH96Y8C3levgtycmHgMCAgICAQwMCkNANJqTeNbNp+/lugICAgkJByMiG2ZiUMO6mAYGBUxIO7uzkiclHm9qVrOsjCgmHwMDAxgXE0dEN4yGbdrRqSYlHQ0MCi4rI3BrV8vDnrCoiS0sIx0cFlZSQ+PZsfbswP/5y7evjmFcS5eRdvPovcrBnevht/HnvP/0x//2yUxJPP7yxYWAaEpHOvnuwfbrv/fswPXqvv/3yYJ8ZYqEbLCpiUI/Mz06L7+3lcnCnce/nMjAnMa+m9HJo2plUyEfGsC4lUVCNUlGOEhFN0dFN0tIOiQiHJ2WeuTbsnlzXggHBklGOcnAncG5l1dTQywqIiYlHiclHycmH5yVefXqv/ftweLYsMS8mbGqirKqiry0k////30Q1AAAAAABYktHRMgdulfKAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAAB3RJTUUH6AIUEy4zOc/V9AAAAaxJREFUKM9jYGBkYmZhZWNFB2zsHJxc3Aw8vHz8AliBoJCwCIOomLgEDiApJc0gIyshJ6+gqIQOFJVVJFTVGNQ1JDS1tHV00YGevoGEoRGDvrGEiamZuQU6sLSyllC2YbA1lrCzd3B0cnJydASRMMDt7CKh7ArS7ebu6OHp6enoxe2JAN4+vlBpP1EnT25uf7MAUW5HbhgIDEKR9gwOCQ0L9w70xC4dERkVHR0Ty+3oiUPaNk4iPiExwJ/bE7t0UrJESmpaeoaXP1bpzCyJ7OSc3Lz8Ak+s0oWgkC4qLikNxCWdkiVRVl7hjcPwFAmJyqpqU6yG19RKSNTVNzQ6eGF1WlN2c0trm4h3BAM26faOzi7b7h7soebR29c/gWWioyN2aQav7kmTHWFBiiI9BRRjDFOnOXrCZbmhEQpMDtNFpwL5M7gRckAQETQTqnuW5ew5c9HBvPkLJJQXMixaLLFk6bLlK9DBylWrJdY0MKwtl6hbt36DCTrYuKlGYvMWhq3btuPKBhI7djLM37V7z959ezHB/r2LDxxk4D50+Ij60WNH0cGxo8c5JnoCAE8J6tjn3YH7AAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDI0LTAyLTIwVDE5OjQ2OjMxKzAwOjAwfxCHyAAAACV0RVh0ZGF0ZTptb2RpZnkAMjAyNC0wMi0yMFQxOTo0NjozMSswMDowMA5NP3QAAAAodEVYdGRhdGU6dGltZXN0YW1wADIwMjQtMDItMjBUMTk6NDY6NTErMDA6MDCfNxcsAAAAAElFTkSuQmCC");
			--imagem-simbolo: url("data:image/png;base64,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");
		}



								table, th, td {
								border: 1px solid black;
								border-collapse: collapse;
								padding: 8px;
						}
						th {
								background-color: \#f2f2f2;}



		.overlay {
			display: none;
			position: fixed;
			top: 0;
			left: 0;
			width: 100%;
			height: 100%;
			background-color: rgba(0, 0, 0, 0.7);
			justify-content: center;
			align-items: center;
			z-index: 99;
		}





		.referencia {
			position: relative; /* Adiciona posição relativa para que o botão de fechar seja posicionado em relação a este elemento */
			background-color: var(--cor-gradient-body);
			padding: 20px;
			border-radius: 5px;
			max-width: 90%;
			text-align: center;
			overflow-x: auto;
		}

		#fecharReferencia {
			position: absolute; /* Adiciona posição absoluta para posicionar o botão */
			top: 0; /* Alinha o botão no topo da div de referência */
			right:10px; /* Alinha o botão à direita da div de referência */
			margin-top: 5px;
			background-color: transparent;
			cursor: pointer;
			line-height: 1.46;
			border:none;
		}


	.referencia p {
			font-size: 16px;
			padding-top: 20px;
			text-align: left;
		}
		#botao-citacao {
			display:flex;
			position: relative;
			padding-top: 20px;
		}

		#div-significados {
		column-count: 3; /* Número de colunas desejado */
		column-gap: 20px; /* Espaçamento entre as colunas */
	}


	@media (max-width: 700px){

		#div-significados {
		column-count: 2; /* Número de colunas desejado */
		column-gap: 10px; /* Espaçamento entre as colunas */
	}

	#botao-citacao {
		flex-direction: column;
	}

		}
	#botaoCitar {
		font-size: 13px;
		white-space: nowrap;
		color: var(--cor-texto);
		background-color: var(--cor-fundo-h1);
		cursor: pointer;
		line-height: 1.46;
		border:none;
		border-radius: 10px;
		padding: 5px;
		right: 0px;
		bottom: 5px;
		position: absolute;
	}

	#botaoCitar:hover{background-color: var(--cor-hover);}

		.div_carregamento {
			height: 25px;
			background-color: var(--cor-hover);
			position: relative;
			width: 20vw;
			height: 2vh;
		}




	.frase {margin: 0 0 11px;}
	audio::-webkit-media-controls-enclosure {
			background-color: #82bfa0;
	}



	.significado-az {
		display: block;
		text-decoration: none;
		color: #333;
	}

	h5 {
		margin: 0; /* Remover a margem padrão dos elementos h5 */
	}



	.abre_fecha_btn {
		display: none;
		position: absolute;
		bottom: 0px; /* Adicionando "px" para especificar as unidades de medida */
		left: 0px;   /* Adicionando "px" para especificar as unidades de medida */
		width: 100%;
		z-index: 2;
		border: none;
		cursor: pointer;
		font-size: 8px;
		border-radius: 10px;
		background: linear-gradient(transparent, rgba(130, 191, 160,0.19));
	}



		.div_carregamento {
			height: 25px;
			background-color: var(--cor-hover);
			position: relative;
			width: 20vw;
			height: 2vh;
		}
		.div_carregamento .progress-bar{
		 position: absolute;
		 height: 100%;
		 background-color: var(--cor-branco);
		 animation: progress-animation 1s infinite;
		}
		@keyframes progress-animation{
			0% { width: 0%; }
			100% { width: 100%}
		}



		.significado-az {
			display: block;
			text-decoration: none;
			color: #333;
		}

		h5 {
			margin: 0; /* Remover a margem padrão dos elementos h5 */
		}

	.imagem-ico {
		background-image: var(--imagem-simbolo);
	}
	.imagem-ico:hover::after {
		content: "Essa entrada possui arquivo de imagem";
	}
	.video-ico {
		background-image: var(--video-simbolo);
	}
	.video-ico:hover::after{
		content: "Essa entrada possui arquivo vídeo";
	}

	.audio-ico {
		background-image: var(--audio-simbolo);
	}

	.audio-ico:hover::after{
		content: "Essa entrada possui arquivo áudio";
	}


/* Estilo para o modal */
.modal {
	display: none; /* Inicialmente escondido */
	position: fixed;
	z-index: 1000;
	left: 0;
	top: 0;
	width: 100%;
	height: 100%;
	background-color: rgba(0, 0, 0, 0.9); /* Fundo escuro com transparência */
	justify-content: center;
	align-items: center;
}

/* Ajuste para centralizar o conteúdo */
#imageModal-div {
	display: flex;
	justify-content: center;
	align-items: center;
	width: 100%;
	height: 100%;
}

/* Estilo para a imagem, permitindo que ela seja ampliada */
.modal-content {
	display: block;
	width: 100%; /* A imagem ocupará 100% da largura disponível */
	max-width: 1200px; /* Limite máximo para a largura da imagem */
	max-height: 90vh; /* Limite de altura para a imagem (90% da altura da viewport) */
	object-fit: contain; /* Mantém a proporção da imagem */
}

/* Estilo para o botão de fechar */
.close {
	position: absolute;
	top: 40px;
	right: 20px;
	color: var(--cor-fundo-h1) !important;
	font-size: 30px;
	font-weight: bold;
	background-color: rgba(0, 0, 0, 0.6) !important;
	border: none;
	cursor: pointer;
	z-index: 1001;
	padding: 3px;
}

.close:hover,
.close:focus {
	color: #bbb;
	text-decoration: none;
	cursor: pointer;
}

/* Animação de zoom para exibir a imagem */
.modal-content {
	animation-name: zoom;
	animation-duration: 0.6s;
}

@keyframes zoom {
	from {transform: scale(0)}
	to {transform: scale(1)}
}

/* Responsividade */
@media only screen and (max-width: 700px) {
	.modal-content {
		max-width: 100%;
		max-height: 100%;
	}
}


	



	.imagem-ico:hover::after, .video-ico:hover::after,.audio-ico:hover::after  {
		width: 150px;
		color: var(--cor-branco);
		position:absolute;
		background-color: rgba(128, 128, 128, 0.8);
		border-radius: 10px;
		font-size: 9px;
		padding: 2px;
		border-radius: 5px;
		margin-top: -20px;
		font-size:14px;
		padding-left: 15px;
		transition: opacity 0.01s ease-in-out;
	}
	.ico_media {
		background-size: contain;
		background-position: center;
		background-repeat: no-repeat;
		width: 17px;
		height: 17px;
		margin-right: 2px;
	}


	.indicador_midia {
		position: absolute;
		right: 10px;
		top: 3px;
	}

	.entrada_lexical {
		position: relative;
		border-top: 1px solid var(--cor-fundo-h1);
		border-bottom: 1px solid var(--cor-fundo-h1);
		border-radius: 10px;
		padding: 10px;
		margin: 5px;
	}


	#loading {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background: var(--cor-fundo-h1);
		text-align: center;
		font-size: 20px;
		z-index: 1000;
	}

	/* Estilo para a imagem de fundo */
	.logo_museu {
		background-image: var(--imagem-logo-museu);
		background-size: contain;
		background-position: center;
		background-repeat: no-repeat;
	}

	.tela_carregamento {

		width: 20vw;
		height: 30vh;

	}

	p {text-align:justify;}

	hr {
		border-color: var(--cor-border);}
	div h1{
		text-align: center;border-radius: 10px;background-color: var(--cor-fundo-h1);
	}
	body{
		background: var(--cor-gradient-body);}
	/* Texto com audio */
	.texto_audio {
	max-height: 1000px; /* Altura máxima desejada em pixels */
	overflow-y: auto; /* Adiciona barra de rolagem vertical quando necessário */}
	.texto_audio::-webkit-scrollbar-track{
	border-radius:0;
	background-color: var(--cor-scrollbar-bg);}
	.texto_audio::-webkit-scrollbar{
	width: 2px;
	background-color: var(--cor-scrollbar-bg);}
	.texto_audio::-webkit-scrollbar-thumb{
	border-radius:0;
	-webkit-box-shadow: inset 0 0 6px rgba(0,0,0,.3);
	background-color: var(--cor-scrollbar-thumb);}
	/* esconde a barra de rolagem */
	.texto_audio::-webkit-scrollbar {
	width: 0;}
	/* Ao passar o mouse sobre a div, mostre a barra de rolagem */
	.texto_audio:hover::-webkit-scrollbar {
	width: 2px;
	background-color: var(--cor-scrollbar-bg);}
	.entrada_div {
	display: flex;
	justify-content: space-between;}
	.texto-frase {
		font-style: italic;}
	.destaque {font-weight:bold}
	.texto_audio {
	padding-left: 60px; }
	.texto_audio, .info_entrada {
		flex: 1;
		flex-basis: 50%;}
	.texto-frase {
	cursor: var(--imagem-mouse-audio), pointer;}

	.texto {display: flex; flex-direction: column; align-items: flex-start;}

	@media (max-width: 700px){
		.entrada_div {
	display: block;
	justify-content: space-between;
	.texto_audio {
		padding-left: 10px; }
	}
	.texto_audio, .info_entrada {
		width: 100%;}}
	.destaque {
		font-weight:bold}
	.significado-az {
	color: black;
	cursor: pointer;}

	.link-entrada {
		display: block;
		margin-top: -2cm; /* Ajuste a distância conforme necessário */
		visibility: hidden;
		position: absolute;}
	header.header-glossario {
	position: fixed;}
	header.header-glossario {
	transition: top 0.3s ease-in-out;}
	.header-glossario {
	height: 60px; /* Altura reduzida para dispositivos móveis */
	position: fixed;
	z-index: 5;
	top: 0;
	width: 100%;
	display: flex;
	background-image: var(--imagem-fundo);
	align-items: center;
	padding: 0;
	border-bottom: 1px solid #dadada;
	box-sizing: border-box;}
	.menu-topo-glossario {
	width: 100%;}
	.menu-glossario {
	display: flex;
	align-items: center;
	justify-content: space-between;}
	.menu-mobile {
	display: flex;
	align-items: center;}
	.glossario-menu {
	display: flex;
	align-items: center;}
	.pesquisar-box {
	display: flex;
	flex: 0 0 auto;
	align-items: center;
	justify-content: flex-end;}
	#barrabusca {
	display: flex;
	justify-content: flex-start;
	align-items: center; /* Adicionado para alinhar verticalmente os elementos */}
	#searchbar {
	padding: 4px 16px;
	border-radius: 10px;
	font-size: 14px;}
	.botoes-busca {
	display: inline-block;
	padding: 4px;
	margin: 8px;
	font-size: 16px;
	text-align: center;
	background-color: #f2f2f2;
	color: var(--cor-texto);
	border: none;
	border-radius: 5px;
	cursor: pointer;
	transition: background-color 0.3s ease;}
	.botoes-busca:hover {
		background-color: var(--cor-hover);}
	.logo-glossario {
	flex: 0 0 auto;
	padding-right: 20px;
	display: flex;
	align-items: center;
	margin-left: 1px;}
	.menu-middle {
	flex-grow: 1;
	text-align: center;}
	.titulo {
	margin: 0;}
	#cabecalho #header {
		width: 99%;}
	.logo-mpeg {
	width: 80px;
	height: 40px;}
	.logo-mobile {
	display: none;}
	a.logo-mobile img {
	width: 100px;}
	.variantes{
	display: flex;
	flex-direction: row;
	flex-wrap: wrap;
	margin: 5px;}
	audio {
		z-index: -1;}
	#btn-voltar {
	position: fixed;
	bottom: 20px;
	right: 20px;
	z-index: 4;
	background-color: var(--cor-menu-bg);
	color: var(--cor-menu-ativo);
	text-decoration: none;
	padding: 1em;
	border-radius: 3em;
	opacity: 0;
	visibility: hidden;
	transition: opacity 0.3s, visibility 0.3s;
	z-index: 2;}

	#btn-inicio {
	position: fixed;
	bottom: 80px;
	right: 25px;
	font-size: 17px;
	z-index: 4;
	background-color: var(--cor-menu-bg);
	color: var(--cor-menu-ativo);
	text-decoration: none;
	padding: 1em;
	border-radius: 3em;
	opacity: 0;
	visibility: hidden;
	transition: opacity 0.3s, visibility 0.3s;
	z-index: 2;}

	#menu {
	display: none;
	background-color:  var(--cor-menu-bg);
	box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
	padding: 20px;
	opacity: 0;
	transform: translateY(-10px);
	transition: opacity 0.3s, transform 0.3s;
	position: fixed;
	bottom: 20px;
	right: 20px;
	padding: 1em;
	border-radius: 2em;
	max-height:80%;
	overflow: auto;
	z-index: 3;}
	#menu.menu-ativo {
	display: flex;
	flex-direction: column;
	opacity: 1;
	transform: translateY(0);}
	#menu.menu-ativo + #btn-voltar {
	opacity: 0;
	visibility: hidden;}
	#menu.menu-ativo + #btn-inicio {
	opacity: 0;
	visibility: hidden;}
	#menu a {
	display: inline-block;
	margin-right: 10px;
	color: var(--cor-menu-ativo);
	text-decoration: none;}
	#menu p{
	display: flex;
	flex-direction: column;}
	#barra {
	text-align: center;}
	.btn-barra {
	display: inline-block;
	font-weight: bold;
	line-height: 1.1;
	padding: 10px;
	margin: 1px;
	width: 250px;
	font-size: 16px;
	text-align: center;
	background-color: var(--cor-menu-bg);
	color: var(--cor-texto);
	border: none;
	border-radius: 10px;
	cursor: pointer;
	transition: background-color 0.3s ease;}
	.btn-barra:hover {
	background-color: var(--cor-hover);}
	#espaco-intro{
	height: 500px;
	width: 500px;
	line-height:10%;}
	.sub-c{
	width: 100%;
	text-align:center;
	margin:auto;
	display:table;
	font-size: 25px;
	font-weight: bold;
	font-family: "Georgia";
	text-align: center;
	border-radius: 10px;
	background-color: var(--cor-fundo-h1);
	}
	.entradalex{
	font-weight: normal; font-size: 16px;}
	#categorias {
	position: relative;}
	#cabecalho {
	align-items: center;
	margin-top: 100px; }
	.date, .author {
	text-align: center;}
	#barrabusca {
	display: flex;
	justify-content: flex-end;}
	#introdução {
	overflow-x: auto;
	text-align: justify;}
	.menu a {
	display: block;
	color: var(--cor-menu-ativo);
	padding: 9px;
	text-decoration: none;}
	.menu a.active {
	background-color: var(--cor-menu-ativo);
	color: var(--cor-menu-bg);
	padding-top: 20px;}
	.menu a:hover:not(.active) {
	background-color: var(--cor-menu-hover);
	color: var(--cor-menu-bg);}
	div.content {
	margin-left: 60px;
	z-index: -10;}
	@media (max-width: 700px){
	#cabecalho {
	padding: 100px 0px 0px;;
	}
	.titulo {
	margin: 0;
	font-size: 4vw; /* Tamanho da fonte em relação à largura da viewport */
	}
	#cabecalho {margin: 0px; }
	#searchbar {
	padding: 6px 12px;
	border-radius: 14px;
	font-size: 10px;}
	.botoes-busca {
	padding: 4px 8px;
	border-radius: 8px;
	font-size: 14px;
	background-color:var(--cor-branco);
	margin-left: 2px;}
	.logo-mobile {
	margin-right: 70px;}}


	.legenda-imagem {
	display: block;
	text-align: center;
	margin-top: 10px; /* Ajuste conforme necessário */
	font-size:13px;
}


	.accordion {
	background-color: var(--cor-fundo-h1);
	cursor: pointer;
	padding: 10px;
	width: 100%;
	text-align: center;
	border: none;
	border-radius: 10px;
	margin-bottom: 10px;
	outline: none;
	transition: 0.4s;
	font-family: "Georgia", sans-serif; /* Define uma nova família de fontes */
	font-size: 30px; /* Define um novo tamanho de fonte */
	font-weight: bold;
	line-height: 0.6; /* Ajusta a altura da linha */
	}

	.versao{
	font-family: Arial, sans-serif;
	}

	.active, .accordion:hover {
	background-color: var(--cor-hover);
	}

	.panel {
	padding: 0 18px;
	background-color: transparent;
	display: none;
	overflow: hidden;
	}

	.accordion:after {
	content: '\02795'; /* Unicode character for "plus" sign (+) */
	font-size: 13px;
	color: #777;
	float: right;
	margin-left: 5px;
	}

	.active:after {
	content: "\2796"; /* Unicode character for "minus" sign (-) */
	}

	.toca-texto {
	background-image: var(--imagem-play-audio);
	width: 60px; /* Defina o tamanho do botão conforme necessário */
	height: 40px; /* Defina o tamanho do botão conforme necessário */
	background-repeat: no-repeat; /* Evita que a imagem se repita */
	border: none; /* Remove a borda do botão */
	border-radius: 10px;
	background-position: center;
	margin: 0 auto 10px !important;
	display: inline-block;
	}
	.botao-stop {
	background-image: var(--imagem-stop-audio);
	width: 60px; /* Defina o tamanho do botão conforme necessário */
	height: 40px; /* Defina o tamanho do botão conforme necessário */
	background-repeat: no-repeat; /* Evita que a imagem se repita */
	border: none; /* Remove a borda do botão */
	border-radius: 10px;
	background-position: center;
	margin: 0 auto 10px !important;
	display: inline-block;
	}



.audio_play_botao {
		background-image: var(--imagem-play-audio);
		width: 30px;
		height: 20px; /* Proporção circular */
		background-repeat: no-repeat;
		background-color: var(--cor-fundo-h1);
		border: none;
		border-radius: 30%;
		background-position: center;
		display: inline-block;
		transition: transform 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease;

		/* Efeito 3D padrão */
		box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2), /* Sombra externa */
								inset 0px 4px 8px rgba(255, 255, 255, 0.6); /* Sombra interna */
}

.audio_play_botao:hover {
	 transform: translateY(-3px) scale(1.2); /* Eleva o botão ao passar o mouse */
	 box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.4), inset 0px 4px 8px rgba(255, 255, 255, 0.5); /* Aumenta a sombra */
}

.audio_play_botao:active {
	 transform: translateY(1px) scale(1.1); /* Simula o botão sendo pressionado */
	 box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.4), inset 0px 2px 4px rgba(255, 255, 255, 0.5); /* Sombra mais suave */
}

/* Destaque enquanto o áudio está tocando (afundado) */
.audio_play_botao.ativo {
	 transform: translateY(2px) scale(1.1); /* Simula o afundamento */
	 box-shadow: inset 0px 6px 12px rgba(0, 0, 0, 0.6), /* Sombra interna mais forte */
							 0px 2px 4px rgba(255, 255, 255, 0.3); /* Sombra externa reduzida */
}



	.toca-texto:hover{
	background-color: var(--cor-menu-hover);
	}



	/* Slideshow container */
	.slideshow-container {
			max-width: 50%;
			position: relative;
			margin: auto;
	}

	/* Make the images invisible by default */
	.containers {
			display: none;
	}

	.containers img {
	max-width: 100%;
	height: auto;
}

	/* Forward & Back buttons */
	.back,
	.forward {
			cursor: pointer;
			position: absolute;
			top: 50%;
			width: auto;
			margin-top: -23px;
			padding: 17px;
			color: grey;
			font-weight: bold;
			font-size: 19px;
			transition: 0.4s ease;
			border-radius: 0 5px 5px 0;
			user-select: none;
	}

	/* Place the "forward button" to the right */
	.forward {
			right: 0;
			border-radius: 5px 0 0 5px;
	}

	/* When the user hovers, add a black background with some opacity */
	.back:hover,
	.forward:hover {
			background-color: rgba(0, 0, 0, 0.8);
	}

	/* Caption Info */
	.info {
			color: #f2f2f3;
			background-color: rgba(128, 128, 128, 0.5);
			border-radius: 10px;
			font-size: 14px;
			padding: 10px 14px;
			position: absolute;
			bottom: 30px;
			left: 10px;
			text-align: left;
	}

	/* The circles or bullets indicators */
	.dots {
			cursor: pointer;
			height: 5px;
			width: 16px;
			margin: 0 3px;
			background: linear-gradient(92.18deg, #82bfa0 -25.78%, #fdf2c5 123.02%);
			opacity: 0.3;
			display: inline-block;
			transition: background-color 0.5s ease;
	}

	.enable,
	.dots:hover {
			background: linear-gradient(92.18deg, #1d8563 -25.78%, #34b48a 123.02%);
			opacity: 1;
	}




	.image-container {
		text-align: center; /* Centraliza todos os elementos internos */
	}

	.image-container img {
		display: inline-block; /* Permite a centralização */
		margin: 0 auto; /* Define margens automáticas (auto) à esquerda e à direita, centralizando a imagem */
	}


	label {padding-right: 5px;}

	.toggle-switch {
			position:relative;
			display: inline-block;
			width: 40px;
			height: 20px;
			margin: 10px;
	}


	.toggle-switch .toggle-input {
			display: none;
	}


	.toggle-switch .toggle-label {
			position: absolute;
			top: 0;
			left: 0;
			width: 36px;
			height: 20px;
			background-color: #2196F3;
			border-radius: 34px;
			cursor: pointer;
			transition: background-color 0.3s;
			padding-right: 5px;

	}

	.toggle-switch .toggle-label::before {
			content: "";
			position: absolute;
			width: 16px;
			height: 16px;
			border-radius: 50%;
			top: 2px;
			left: 2px;
			background-color: #fff;
			box-shadow: 0px 2px 5px 0px rgba(0, 0, 0, 0.3);
			transition: transform 0.3s;
	}

	/* Texto à esquerda e à direita */
	.botao-toggle {
			display: flex;
			align-items: center;
			margin-right: 20px;

		}



	/* Anahtarın etkin hale gelmesindeki stil değişiklikleri */
	.toggle-switch .toggle-input:checked + .toggle-label {
			background-color: #4CAF50;
	}

	.toggle-switch .toggle-input:checked + .toggle-label::before {
			transform: translateX(16px);
	}

	/* Light tema */
	.toggle-switch.light .toggle-label {
			background-color: #BEBEBE;
	}

	.toggle-switch.light .toggle-input:checked + .toggle-label {
			background-color: #9B9B9B;
	}

	.toggle-switch.light .toggle-input:checked + .toggle-label::before {
			transform: translateX(6px);
	}

	/* Dark tema */
	.toggle-switch.dark .toggle-label {
			background-color: #4B4B4B;
	}

	.toggle-switch.dark .toggle-input:checked + .toggle-label {
			background-color: #717171;
	}

	.toggle-switch.dark .toggle-input:checked + .toggle-label::before {
			transform: translateX(16px);
	}


	.palavra_entrada {

	font-family: "Georgia";
	font-weight: bold;
	line-height: 1.1;
	color: inherit;
	font-size: 30px;
	margin-top: 22px;
	margin-bottom: 11px;

	}

	hr {
		margin-top: 15px;
		margin-bottom: 15px;
	}

	.entrada_lexical .significado-lista::before {
		content: attr(data-count);
	}

	</style>

<!-- meus scripts 1-->
<script>

function esconderDivs() {
		toggleVisibility(document.getElementsByClassName('entrada_div'));
		toggleVisibility(document.getElementsByClassName('significado-lista'));
}

function toggleVisibility(elements) {
		for (var i = 0; i < elements.length; i++) {
				if (!elements[i].hasAttribute('data-estilo-original')) {
						elements[i].setAttribute('data-estilo-original', elements[i].style.cssText);
				}

				var estiloOriginal = elements[i].getAttribute('data-estilo-original');
				var estiloAtual = window.getComputedStyle(elements[i]).display;

				if (estiloAtual !== 'none' && estiloOriginal !== 'none') {
						elements[i].style.display = 'none';
				} else {
						elements[i].style.cssText = estiloOriginal;
				}
		}
}




	function navegarParaAncora(entradaId) {


		var divs = document.querySelectorAll('#dicionario, .ordem-alfabetica');

		for (var i = 0; i < divs.length; i++) {
				var div = divs[i];
				var displayDiv = window.getComputedStyle(div).getPropertyValue('display');
				if (displayDiv !== 'none') {
						// Encontrar a entrada dentro da div ativa
						var entradaNaDiv = div.querySelector('.link-entrada[name="' + entradaId + '"]');

						if (entradaNaDiv) {
								// Navegar para a entrada
								entradaNaDiv.scrollIntoView();
								return;
						}
				}
		}

		console.error('Entrada não encontrada!');
}






var slidePosition = 1;

function plusSlides(n, elemento) {
		showSlides(slidePosition += n, elemento);
}

function currentSlide(n, elemento) {
		var slideshowContainer = elemento.closest('.slideshow-container');
		if (!slideshowContainer) {
				console.error('Não foi possível encontrar o contêiner do slideshow.');
				return;
		}

		var slides = slideshowContainer.getElementsByClassName("containers");
		var dots = slideshowContainer.getElementsByClassName("dots");

		for (var i = 0; i < dots.length; i++) {
				dots[i].classList.remove("enable");
				slides[i].style.display = "none";
		}

		dots[n - 1].classList.add("enable");
		slides[n - 1].style.display = "block";
}

function showSlides(n, elemento) {
		var slideshowContainer = elemento.closest('.slideshow-container');
		if (!slideshowContainer) {
				console.error('Não foi possível encontrar o contêiner do slideshow.');
				return;
		}

		var i;
		var slides = slideshowContainer.getElementsByClassName("containers");
		var dots = slideshowContainer.getElementsByClassName("dots");

		if (n > slides.length) {
				slidePosition = 1;
		}
		if (n < 1) {
				slidePosition = slides.length;
		}
		for (i = 0; i < slides.length; i++) {
				slides[i].style.display = "none";
		}
		for (i = 0; i < dots.length; i++) {
				dots[i].className = dots[i].className.replace(" enable", "");
		}

		slides[slidePosition - 1].style.display = "block";
		dots[slidePosition - 1].className += " enable";
}

// Initialize slideshows
document.addEventListener("DOMContentLoaded", function () {
		initSlideshows();
});

function initSlideshows() {
		var slideshowContainers = document.getElementsByClassName("slideshow-container");
		for (var i = 0; i < slideshowContainers.length; i++) {
				currentSlide(1, slideshowContainers[i]);
		}
}





let audioElements = []; // Array para armazenar os elementos de áudio
let audioPlaying = false; // Variável para controlar o estado de reprodução
let currentAudioIndex = -1; // Índice do áudio atualmente tocando

function tocaTexto(botao, idTexto) {
		const divTexto = document.getElementById(idTexto);
		const divsFrases = divTexto.querySelectorAll(".frase");

		// Carregar elementos de áudio
		audioElements = Array.from(divTexto.querySelectorAll("audio"));

		function destacaFrase(index) {
				divsFrases.forEach((frase, i) => {
						const textoFrase = frase.querySelector(".texto-frase");
						if (i === index) {
								textoFrase.classList.add("destaque");
						} else {
								textoFrase.classList.remove("destaque");
						}
				});
		}

		
		function playAudio(index) {
				if (index < audioElements.length) {
						const audio = audioElements[index];
						audio.play();
						currentAudioIndex = index;

						audio.addEventListener("ended", function () {
								destacaFrase(-1); // Remove todos os destaques quando o áudio termina
								if (index + 1 < audioElements.length) {
										destacaFrase(index + 1); // Destaca o próximo texto
										playAudio(index + 1); // Toca o próximo áudio
								} else {
										audioPlaying = false;
										currentAudioIndex = -1;
										botao.classList.remove('botao-stop');
										botao.classList.add('toca-texto');
								}
						});
				}
		}

		if (!audioPlaying) {
				audioPlaying = true;
				playAudio(0); // Inicia a reprodução do primeiro áudio
				destacaFrase(0); // Destaca o primeiro texto
				botao.classList.remove('toca-texto');
				botao.classList.add('botao-stop');
		} else {
				if (currentAudioIndex !== -1) {
						audioElements[currentAudioIndex].pause();
						audioElements[currentAudioIndex].currentTime = 0;
						audioElements = [];
						audioPlaying = false;
						currentAudioIndex = -1;
						botao.classList.remove('botao-stop');
						botao.classList.add('toca-texto');
						destacaFrase(-1); // Remove todos os destaques quando a reprodução é interrompida
				}
		}
}

	function playAudio_frase(clickedElement) {
		// Pausar todos os áudios em execução antes de tocar o próximo
		const allAudios = document.querySelectorAll('audio');
		allAudios.forEach(audio => {
				if (!audio.paused) {
						audio.pause();
				}
		});

		const audio = clickedElement.querySelector("audio");
		const frase = clickedElement.querySelector(".texto-frase");

		// Toca o áudio do elemento clicado
		audio.play();

		// Adiciona a classe de destaque apenas para a frase do elemento clicado
		frase.classList.add("destaque");

		// Remove a classe de destaque quando o áudio termina
		audio.addEventListener('ended', function() {
				frase.classList.remove("destaque");
		});
}



function escapeRegExp(string) {
		return string.replace(/[.*+\-?^${}()|[\]\\]/g, '\\$&');
}

function escapeRegExp(string) {
		return string.replace(/[.*+\-?^${}()|[\]\\]/g, '\\$&');
}

function destacar_palavras(entrada, palavras) {
		let innerHTML = entrada;
		palavras.forEach((palavra) => {
		let palavraEscapada = escapeRegExp(palavra);
		let regEx = new RegExp(`(${palavraEscapada}|${palavraEscapada.replace(/[\[\]()]/g, '\\$&').replace(/\s+/g, '|')})`, 'gi');
		innerHTML = innerHTML.replace(regEx, match => {
				let primeiraLetra = match[0];
				let casoOriginal = primeiraLetra.toUpperCase() === primeiraLetra ? palavra.charAt(0).toUpperCase() + palavra.slice(1) : palavra;
				return `<mark style="background-color: yellow; padding: 0;">${casoOriginal}</mark>`;
		});
		});
		return innerHTML;
}


function busca_entrada(buscaText, destacar) {

const entrada_div = document.getElementsByClassName('entrada_div');
const significado_lista = document.getElementsByClassName('significado-lista');
const palavras = document.querySelectorAll('.palavra_entrada');
document.getElementById("checkbox_lista").checked = false;


palavras.forEach(elemento => {
elemento.style.fontSize = '30px';
});
esconderElementos(significado_lista);
mostrarElementos(entrada_div);

	let input = document.getElementById('searchbar').value.toLowerCase();
	let x = document.getElementsByClassName('section level1');
	let x2 = document.getElementsByClassName('level2');
	let searchbar = document.getElementById("searchbar");
	let searchbtn = document.getElementById("searchbtn");
	let clearbtn = document.getElementById("clearbtn");

	let oldInput = input;
	searchbar.value = buscaText;

	setTimeout(() => {
		let hasResults = false;
		for (let i = 0; i < x.length; i++) {
			if (!x[i].innerText.toLowerCase().includes(input) || x[i].hasAttribute('data-ignore-search')) {
				x[i].style.display = "none";
			} else {
				x[i].style.display = "block";
				if (destacar) {
					marca_texto(x[i], input, "yellow");
				}
				hasResults = true;
			}
		}

		for (let i = 0; i < x2.length; i++) {
			if (!x2[i].innerText.toLowerCase().includes(input) || x2[i].hasAttribute('data-ignore-search')) {
				x2[i].style.display = "none";
			} else {
				x2[i].style.display = "block";
				if (destacar) {
					marca_texto(x2[i], input, "yellow");
				}
				hasResults = true;
			}
		}

		searchbar.value = oldInput;
		searchbar.focus();

		if (!hasResults) {
			limpa_busca();
			searchbar.value = oldInput;
			alert("Nenhum resultado encontrado para a busca: " + oldInput);
		}
	}, 1000);
}

function marca_texto(elemento, buscaText, destacar) {
		// Obtém o conteúdo do elemento
		let conteudo = elemento.innerHTML;

		// Verifica se o elemento é uma imagem com src em formato base64
		if (elemento.tagName === 'IMG' && elemento.src && elemento.src.startsWith('data:image')) {
		// Caso seja, não faz nada
		return;
		}

		// Verifica se o elemento é um elemento vazio, como uma tag <br>
		if (conteudo.trim() === '') {
		return;
		}

		// Verifica se o elemento tem o atributo 'data-ignore-search'
		let ignoreSearch = false;
		if (elemento.hasAttribute('data-ignore-search')) {
		ignoreSearch = true;
		}

		// Cria uma lista de nós de texto dentro do elemento
		let nosTexto = [];
		const pegaNosTexto = (no) => {
		if (no.nodeType === Node.TEXT_NODE) {
				nosTexto.push(no);
		} else if (no.nodeType === Node.ELEMENT_NODE) {
				for (const filho of no.childNodes) {
				pegaNosTexto(filho);
				}
		}
		};
		pegaNosTexto(elemento);

		// Realiza a busca em cada nó de texto


		let regEx = new RegExp(`(${buscaText.replace(/[\[\]()]/g, '\\$&')})`, 'gui');



		for (const no of nosTexto) {
		let texto = no.textContent;
		let novoTexto = texto;
		if (!ignoreSearch) {
				novoTexto = texto.replace(regEx, `<span id = "${buscaText}" style="background-color: ${destacar}; padding: 0;">$1</span>`);
		}
		if (novoTexto !== texto) {
				let novoNo = document.createElement('span');
				novoNo.innerHTML = novoTexto;
				no.parentNode.replaceChild(novoNo, no);
		}
		}
}


function w3_open() {
		document.getElementById("mySidebar").style.display = "block";
		document.getElementById("myButton").style.display = "none";
		document.getElementById("mySidebar").style.position = "fixed";
}

function w3_close() {
		document.getElementById("mySidebar").style.display = "none";
		document.getElementById("myButton").style.display = "block";

}

function esconde_intro() {
		var btn = document.getElementById('btn-div');
		var container = document.querySelector('.texto-introducao');

		if((container.style.display === 'block') || (container.style.display == '' )) {
				container.style.display = 'none';
				btn.innerHTML = 'Mostrar Introdução';

		} else {
				container.style.display = 'block';
				btn.innerHTML = 'Ocultar Introdução';
		}
		}

		document.addEventListener("DOMContentLoaded", function() {
		let searchbar = document.getElementById("searchbar");

		searchbar.addEventListener("keydown", function(event) {
		if (event.key === "Enter") {
				event.preventDefault();
				busca_entrada("Buscando...", true);
		}
		});

		searchbar.addEventListener("input", function() {
		if (searchbar.value.trim() === "") {
				limpa_busca();
		}
		});
});

function limpa_busca() {
// limpa a barra de busca e chama a função de busca
document.getElementById("searchbar").value = "";
busca_entrada('Limpando...');

// remove o fundo amarelo de todos os spans
let spans = document.getElementsByTagName("span");
for (let i = 0; i < spans.length; i++) {
spans[i].style.backgroundColor = ""; // Remove o estilo de fundo (background-color)
}
}


function valida_busca() {
		var searchbar = document.getElementById("searchbar");
		var searchbtn = document.getElementById("searchbtn");

		if (searchbar.value.trim() === "") {
				searchbtn.disabled = true;
		} else {
				searchbtn.disabled = false;
		}
}

var posicaoInicial = window.pageYOffset;
var isScrolling = false;

let anchorClicked = false;

document.addEventListener('scroll', function(event) {
	// Verificar se o scroll é causado pelo mouse, não por uma âncora
	if (event.type === 'scroll' && !anchorClicked) {
		var posicaoAtual = window.pageYOffset;
		if (posicaoInicial > posicaoAtual) {
			document.getElementById("header").style.top = "";
			document.getElementById("btn-voltar").style.opacity = "1";
			document.getElementById("btn-voltar").style.visibility = "visible";
			document.getElementById("btn-inicio").style.opacity = "1";
			document.getElementById("btn-inicio").style.visibility = "visible";
		} else {
			document.getElementById("header").style.top = "-74px";
			document.getElementById("btn-voltar").style.opacity = "0";
			document.getElementById("btn-voltar").style.visibility = "hidden";
			document.getElementById("btn-inicio").style.opacity = "0";
			document.getElementById("btn-inicio").style.visibility = "hidden";
		}
		posicaoInicial = posicaoAtual;
	}
});

// Função para verificar se uma âncora foi clicada
function isAnchorLinkClicked() {
	if (window.location.hash !== '') {
		anchorClicked = true;
		return true;
	}
	return false;
}

function toggleMenu() {
var menu = document.querySelector('.menu');
menu.classList.toggle('menu-ativo');

}

function fecharMenu() {
var menu = document.querySelector('.menu');
menu.classList.remove('menu-ativo');
}

document.addEventListener('click', function(event) {
var menu = document.querySelector('.menu');
var targetElement = event.target;

// Verifica se o clique ocorreu fora do menu e dos links que abrem o menu
if (!menu.contains(targetElement) && targetElement.id !== 'btn-voltar') {
menu.classList.remove('menu-ativo');
}
})

</script>
</head>

<div id='loading'><div class="logo_museu tela_carregamento"></div><div id="texto_loading">Carregando...</div><div class="div_carregamento"><div class="progress-bar"></div></div></div>
<body>
	<div class="container-fluid main-container">
		 <a name="ini"></a>

		<div id="cabecalho">
		<div id="header">
		<h1 class="title toc-ignore">''' + titulo + r'''</h1>
		<h4 class="author">''' + autor +r'''</h4>


'''


	if versao != "":
		html_string += f'''<h4 class="author versao">{versao}</h4>\n 		</div>\n</div>\n'''
	else:
		html_string += '''\n 		</div>\n</div>\n'''


	html_string += '''
<p>
<a id="btn-inicio" href="#ini"">⤒</a>
</p>
<p>
<a id="btn-voltar" onclick="toggleMenu()">☰</a>
</p>
<div id="menu" class="menu">
<a href="#ini" onclick="fecharMenu()">Início</a>
'''

	for campo in campos_semanticos:
		html_string += '<a class="link-categoria-menu" href="#' + campo.replace(" ", "") + '" onclick="fecharMenu()">' + campo + '</a>\n'
	html_string += '''<a href="#lista-significados" onclick="fecharMenu()">Português(A-Z)</a>
</div>

'''

	barra = ""
	for campo in campos_semanticos:
		item = '<a class="btn-barra categoria_btn" href="#' + campo.replace(" ", "") + '">' + campo + '</a>'
		barra += item + " "
	barra += '<a class="btn-barra" href="#lista-significados">Português(A-Z)</a>'

	referencia = cria_ref()

	if referencia != "":
		html_string += f'''
<div id="botao-citacao">

	<label>
		<input type="checkbox" id="checkbox_AZ">
			Ordenar A-Z   
	</label>
	<label>
		<input type="checkbox" id="checkbox_lista">
			Formato de lista
	</label>

	<button id="botaoCitar"><b>Como citar?</b></button>
	</div>
	<div class="overlay" id="overlay">
		<div class="referencia">
			<button id="fecharReferencia"><b>X</b></button>

{referencia}


		</div>

	 </div>
'''
	else:
		html_string += f'''
	<button id="botaoCitar" style="display: none;"></button>
	<button id="fecharReferencia" style="display: none;"></button>
	<label>		
		<input type="checkbox" id="checkbox_AZ">
			Ordenar A-Z
	</label>
	<label>
		<input type="checkbox" id="checkbox_lista">
			Formato de lista
	</label>
'''
	html_string += '''<div id = "corpotexto">\n
<button id="botao-introducao" class="accordion active">Introdução</button>
<div class="panel" style="display: block;">
<div id="introdução" class="texto-introducao">
'''
	introducao = cria_intro()
	html_string += introducao 
	html_string += '''\n</div>\n</div>\n\n'''

	html_string += '''<button class="accordion">Categorias</button>
<div class="panel" id="barra">
''' + barra + '''
</div>
'''

	html_string += '<div id="dicionario">'

	html_string += '''
<div id="imageModal" class="modal" onclick="closeModalOnClickOutside(event)">
	<div id="imageModal-div">
		<button onclick="closeModal()" class="close">&times;</button>
		<img class="modal-content" id="modalImage">
	</div>
</div>
'''
	html_string += entradas_html_string

	html_string += r'''
</div>'''



	html_string += """


<audio id="audioPlayer" style="display:none;">
	<source id="audioSource" src="" type="audio/mpeg">
	Seu navegador não suporta o elemento de áudio.
</audio>

"""

	if midias_tag != None:
		html_string += midias_tag

	else:

		html_string += """\n<script>const audioDictionary = {}</script>\n\n"""


	html_string += r'''


	<script>


	
function playAudio2(filePath) {
	const audioPlayer = document.getElementById("audioPlayer");
	const audioSource = document.getElementById("audioSource");
	
	// Define o caminho do arquivo de áudio
	audioSource.src = `audio/${filePath}`;
	audioPlayer.load();  // Carrega o novo áudio
	audioPlayer.play();  // Toca o áudio
}




// Função para abrir o modal e exibir a imagem ampliada
function openModal(src) {
	var modal = document.getElementById("imageModal");
	var modalImg = document.getElementById("modalImage");
	modal.style.display = "flex";
	modalImg.src = src;
}

// Função para fechar o modal
function closeModal() {
	var modal = document.getElementById("imageModal");
	modal.style.display = "none";
}

// Função para fechar o modal ao clicar fora da imagem
function closeModalOnClickOutside(event) {
	var modalImg = document.getElementById("modalImage");
	if (event.target !== modalImg) {
		closeModal();
	}
}



function addAudioPlayEvent(buttonSelector, audioDictionary) {
  // Seleciona todos os botões com o seletor fornecido
  const audioButtons = document.querySelectorAll(buttonSelector);

  // Adiciona um evento de clique em cada botão
  audioButtons.forEach(button => {
	button.addEventListener('click', () => {
	  // Pega o ID do áudio a partir do atributo 'data-audio-id'
	  const audioId = button.getAttribute('data-audio-id');
	  
	  // Busca o source do áudio no dicionário
	  const audioSrc = audioDictionary[audioId];
	  
	  if (audioSrc) {
		// Cria um novo elemento de áudio dinamicamente
		const audioElement = new Audio(audioSrc);

		// Configura o preload
		audioElement.preload = "auto";

		// Adiciona a classe 'ativo' para destacar o botão
		button.classList.add('ativo');

		// Tocar o áudio
		audioElement.play();

		console.log('Tocando o áudio:', audioId);

		// Remove a classe 'ativo' quando o áudio terminar
		audioElement.addEventListener('ended', () => {
		  button.classList.remove('ativo');
		});
	  } 
	});
  });
}


addAudioPlayEvent('.audio_play_botao', audioDictionary);

// JavaScript para mostrar o loading enquanto a página está carregando
var loadingElement = document.getElementById('loading');
var loadStart = new Date().getTime(); // Tempo inicial

window.addEventListener('load', function () {
		var loadEnd = new Date().getTime(); // Tempo final
		var loadTime = loadEnd - loadStart;

		var minimumDisplayTime = 500; // Tempo mínimo de exibição em milissegundos

		// Garante que o tempo mínimo de exibição seja respeitado
		setTimeout(function () {
				loadingElement.style.display = 'none';
		}, Math.max(0, minimumDisplayTime - loadTime));

});
	document.addEventListener('DOMContentLoaded', function () {
		const corpotexto = document.getElementById('corpotexto');

		corpotexto.addEventListener('scroll', function () {
			// Verifica se os elementos estão visíveis no viewport
			document.querySelectorAll('img[data-src]:not([src]), audio[data-src]:not([src])').forEach(function (element) {
				const rect = element.getBoundingClientRect();
				if (rect.top < window.innerHeight && rect.bottom >= 0) {
					// Carrega a imagem ou áudio
					element.src = element.getAttribute('data-src');
				}
			});
		});

		// Dispara o evento de scroll inicialmente para carregar os elementos visíveis
		corpotexto.dispatchEvent(new Event('scroll'));
	});

document.getElementById('checkbox_lista').addEventListener('change', function() {
	if (this.checked) {
		const entrada_div = document.getElementsByClassName('entrada_div');
		const significado_lista = document.getElementsByClassName('significado-lista');
		const palavras = document.querySelectorAll('.palavra_entrada');
		const indicadorMidia = document.getElementsByClassName("indicador_midia");
		const abreFechaBtn = document.querySelectorAll('.abre_fecha_btn');


		palavras.forEach(elemento => {
			elemento.style.fontSize = '25px';
		});

		esconderElementos(entrada_div);
		mostrarElementos(significado_lista);
		mostrarElementos(indicadorMidia,"inline-flex");
		mostrarElementos(abreFechaBtn);
		adicionarNumeracao();
	} else {
		const entrada_div = document.getElementsByClassName('entrada_div');
		const significado_lista = document.getElementsByClassName('significado-lista');
		const palavras = document.querySelectorAll('.palavra_entrada');
		const indicadorMidia = document.getElementsByClassName("indicador_midia");
		const abreFechaBtn = document.querySelectorAll('.abre_fecha_btn');


		palavras.forEach(elemento => {
			elemento.style.fontSize = '30px';
		});
		esconderElementos(significado_lista);
		esconderElementos(indicadorMidia);
		mostrarElementos(entrada_div);
		esconderElementos(abreFechaBtn);
	}
});


document.addEventListener("DOMContentLoaded", function() {
	var accordions = document.querySelectorAll(".main-container .accordion");

	accordions.forEach(function(accordion) {
		accordion.addEventListener("click", function() {
			var isActive = this.classList.contains("active");
			var panel = this.nextElementSibling;

			if (this.classList.contains("active")) {panel.style.display = "none";}else{panel.style.display ='block'}

			// Adiciona ou remove a classe "active" apenas para este acordeão
			this.classList.toggle("active", !isActive);
		});
	});
});


document.addEventListener("DOMContentLoaded", function() {
	var accordions = document.querySelectorAll(".main-container .abre_fecha_btn");

	accordions.forEach(function(accordion) {
		accordion.addEventListener("click", function() {
			var isActive = this.classList.contains("ativado");
			var panel = this.parentNode;
			console.log("panel")

		const palavraEntrada = panel.querySelector('.entrada_div');
		const significadoLista = panel.querySelector('.significado-lista');
		var estiloAtual = window.getComputedStyle(palavraEntrada).display;
		var estiloOriginal = palavraEntrada.getAttribute('data-estilo-original');
		const palavras = panel.querySelectorAll('.palavra_entrada');
		const indicadorMidia = panel.querySelector(".indicador_midia");

		if (estiloAtual === "none") {
			palavraEntrada.style.display = estiloOriginal;
			significadoLista.style.display = "none";
			indicadorMidia.style.display = "none";
			palavras.forEach(elemento => {
				elemento.style.fontSize = '30px';
			});
		} else {
			palavraEntrada.style.display = "none";
			significadoLista.style.display = "inline";
			indicadorMidia.style.display = "inline-flex";
			palavras.forEach(elemento => {
				elemento.style.fontSize = '25px';
			});
		}

			// Adiciona ou remove a classe "active" apenas para este acordeão
			this.classList.toggle("ativado", !isActive);
		});
	});
});



// Função para esconder elementos
function esconderElementos(elementos) {
	for (var i = 0; i < elementos.length; i++) {
		elementos[i].setAttribute('data-estilo-original',  window.getComputedStyle(elementos[i]).display);
		elementos[i].style.display = 'none';
	}
}

// Função para mostrar elementos
function mostrarElementos(elementos,estiloEscolido="inline") {
	for (var i = 0; i < elementos.length; i++) {
		var estiloOriginal = elementos[i].getAttribute('data-estilo-original');
		var estiloAtual = window.getComputedStyle(elementos[i]).display;

		if (estiloOriginal !== null && estiloOriginal !== "none") {
			elementos[i].style.display = estiloOriginal;
		}else if (estiloAtual === 'none') {
			elementos[i].style.display = estiloEscolido;}
	}
}


document.getElementById('checkbox_AZ').addEventListener('change', function() {
	if (this.checked) {
		alternarOrdem();
		abre_fecha_entrada();
		distribuir_observador();
		addAudioPlayEvent('.audio_play_botao', audioDictionary);
	} else {
		restaurarOrdemOriginal();
		abre_fecha_entrada();
		distribuir_observador();
		addAudioPlayEvent('.audio_play_botao', audioDictionary);
	}

});


function alternarOrdem() {
	const ordemAlfabeticaDiv = document.querySelector('.ordem-alfabetica');
	const entradasLexicais = document.querySelectorAll('.entrada_lexical');
	const botoes_menu = document.querySelectorAll('.link-categoria-menu');
	const dicionario = document.querySelector('#dicionario');
	const botoes_barra = document.querySelectorAll('.categoria_btn');

	const entradasOrdenadas = Array.from(entradasLexicais)
		.sort((a, b) => a.getAttribute('ordem-alfabetica') - b.getAttribute('ordem-alfabetica'));

	// Limpa a div de ordem alfabética antes de recriar a lista
	ordemAlfabeticaDiv.innerHTML = '';

	

	const titulo = document.createElement('h1');
	titulo.textContent = "Ordem Alfabética"; // Define o texto do título

	// Adiciona o título antes de entradaClone
	ordemAlfabeticaDiv.appendChild(titulo);




	for (const entrada of entradasOrdenadas) {
		// Clone a entrada
		const entradaClone = entrada.cloneNode(true);

		// Atualize os IDs para garantir que sejam únicos
		const novoID = 'nova-' + entrada.id; // Adicione um prefixo ou outra lógica para garantir unicidade
		entradaClone.id = novoID;

		// Adicione a cópia à div de ordem alfabética
		ordemAlfabeticaDiv.appendChild(entradaClone);
	}

	// Oculta as categorias originais
	dicionario.style.display = 'none';
	for (const botaoMenu of botoes_menu) {
		botaoMenu.style.display = 'none';
	}
	for (const botaoBarra of botoes_barra) {
		botaoBarra.style.display = 'none';
	}
	// Exibe a div de ordem alfabética
	ordemAlfabeticaDiv.style.display = 'block';
}


function restaurarOrdemOriginal() {
	const ordemAlfabeticaDiv = document.querySelector('.ordem-alfabetica');
	const dicionario = document.querySelector('#dicionario');
	const botoes_menu = document.querySelectorAll('.link-categoria-menu');
	const botoes_barra = document.querySelectorAll('.categoria_btn');

	// Limpa a div de ordem alfabética antes de escondê-la
	ordemAlfabeticaDiv.innerHTML = '';

	// Oculta a div de ordem alfabética
	ordemAlfabeticaDiv.style.display = 'none';

	// Exibe as categorias originais
	dicionario.style.display = 'block';
	for (const botaoMenu of botoes_menu) {
			botaoMenu.style.display = "inline-block";
	}
	for (const botaoBarra of botoes_barra) {
		botaoBarra.style.display = "inline-block";
}
}


function adicionarNumeracao() {
	// Obtém todas as divs com a classe .entrada_lexical
	const divsEntradaLexical = document.querySelectorAll('.entrada_lexical');

	// Itera sobre cada div
	divsEntradaLexical.forEach(div => {
		// Obtém a lista de elementos .significado_lista dentro da div
		const significados = div.querySelectorAll('.significado-lista');

		// Itera sobre os elementos e adiciona a numeração dinamicamente
		if (significados.length > 1) {significados.forEach((elemento, index) => {
			// Temporariamente, torna o elemento visível para a numeração
			elemento.setAttribute('data-count', index + 1 + ". ");


		});}

	});
}


function abre_fecha_entrada (){


	var accordions = document.querySelectorAll(".main-container .abre_fecha_btn");

	accordions.forEach(function(accordion) {
		accordion.addEventListener("click", function() {
			var isActive = this.classList.contains("ativado");
			var panel = this.parentNode;

		const palavraEntrada = panel.querySelector('.entrada_div');
		const significadoLista = panel.querySelector('.significado-lista');
		var estiloAtual = window.getComputedStyle(palavraEntrada).display;
		var estiloOriginal = palavraEntrada.getAttribute('data-estilo-original');
		const palavras = panel.querySelectorAll('.palavra_entrada');
		const indicadorMidia = panel.querySelector(".indicador_midia");
		const abreFechaBTN = panel.querySelector(".abre_fecha_btn");



		if (estiloAtual === "none") {
			palavraEntrada.style.display = estiloOriginal;
			significadoLista.style.display = "none";
			indicadorMidia.style.display = "none";
			abreFechaBTN.innerHTML = '&#9650;';
			palavras.forEach(elemento => {
				elemento.style.fontSize = '30px';
			});
		} else {
			palavraEntrada.style.display = "none";
			significadoLista.style.display = "inline";
			indicadorMidia.style.display = "inline-flex";
			abreFechaBTN.innerHTML = '&#9660;';
			palavras.forEach(elemento => {
				elemento.style.fontSize = '25px';
			});
		}
			// Adiciona ou remove a classe "active" apenas para este acordeão
			this.classList.toggle("ativado", !isActive);
		});
	});


	initSlideshows()

}


function autoplayVisibleSlide(entries, observer) {
	entries.forEach(function (entry) {
		if (entry.isIntersecting) {
			let slideshow = entry.target;
			let slideIndex = 0;
			let slideshowTimeout;

			function showSlides2() {
				let slides = slideshow.getElementsByClassName("containers");
				let dots2 = slideshow.getElementsByClassName("dots");

				for (let j = 0; j < slides.length; j++) {
					slides[j].style.display = "none";
					dots2[j].classList.remove("enable");
				}

				slideIndex++;

				if (slideIndex > slides.length) {
					slideIndex = 1;
				}

				slides[slideIndex - 1].style.display = "block";
				dots2[slideIndex - 1].classList.add("enable");

				// Remova a classe "enable" dos pontos anteriores
				for (let j = 0; j < dots2.length; j++) {
					if (j !== slideIndex - 1) {
						dots2[j].classList.remove("enable");
					}
				}

				clearTimeout(slideshowTimeout);
				slideshowTimeout = setTimeout(showSlides2, 3000);
			}

			function pauseSlides2() {
				clearTimeout(slideshowTimeout);
			}

			function resumeSlides2() {
				showSlides2();
			}

			let images = slideshow.querySelectorAll('.containers img');
			images.forEach(function (img) {
				img.addEventListener('click', function () {
					pauseSlides2();
					setTimeout(resumeSlides2, 30000);
				});
			});

			let backButtons = slideshow.querySelectorAll('.forward');
			backButtons.forEach(function (button) {
				button.addEventListener('click', function () {
					pauseSlides2();
					setTimeout(resumeSlides2, 30000);
				});
			});

			let nextButtons = slideshow.querySelectorAll('.back');
			nextButtons.forEach(function (button) {
				button.addEventListener('click', function () {
					pauseSlides2();
					setTimeout(resumeSlides2, 30000);
				});
			});

			showSlides2();

			// Adicione um evento para quando o slide não estiver mais visível
			let options = { threshold: 0 };
			let visibilityObserver = new IntersectionObserver(function (visibilityEntries) {
				visibilityEntries.forEach(function (visibilityEntry) {
					if (visibilityEntry.isIntersecting) {
						// Se o slide estiver visível, retome a animação
						resumeSlides2();
					} else {
						// Se o slide não estiver mais visível, pause a animação
						pauseSlides2();
					}
				});
			}, options);

			// Observe a visibilidade do slide
			visibilityObserver.observe(slideshow);

			// Remova o observer após a primeira interseção
			observer.unobserve(entry.target);
		}
	});
}

function distribuir_observador() {
	var observer = new IntersectionObserver(function(entries, observer) {
		autoplayVisibleSlide(entries, observer);
	}, { threshold: 1 });

	var slides = document.querySelectorAll('.main-container .slideshow-container');

	slides.forEach(function (slide) {
		observer.observe(slide);
	});
}

distribuir_observador();


const botaoCitar = document.getElementById('botaoCitar');
const overlay = document.getElementById('overlay');
const fecharReferencia = document.getElementById('fecharReferencia');

botaoCitar.addEventListener('click', () => {
	overlay.style.display = 'flex';
});

fecharReferencia.addEventListener('click', () => {
	overlay.style.display = 'none';
});





</script>
</body>


</html>'''

	return html_string

# Função para mover arquivos não utilizados para uma subpasta
def mover_nao_utilizados(arquivos_pasta, arquivos_tabela, pasta_origem, tipo):
	# Criar o diretório "nao_utilizados" se não existir
	pasta_nao_utilizados = os.path.join(pasta_origem, "nao_utilizados")
	if not os.path.exists(pasta_nao_utilizados):
		os.makedirs(pasta_nao_utilizados)
	
	# Verificar e mover arquivos não utilizados
	for arquivo in arquivos_pasta:
		caminho_origem = os.path.join(pasta_origem, arquivo)
		
		# Ignorar o próprio diretório "nao_utilizados"
		if arquivo == "nao_utilizados":
			continue

		if arquivo not in arquivos_tabela:
			caminho_destino = os.path.join(pasta_nao_utilizados, arquivo)
			shutil.move(caminho_origem, caminho_destino)

def gera_entrada_html(dicionarios, novas_colunas={},midia_inclusa=True):
	html_entrada = ""
	tem_imagem = False
	tem_audio = False
	tem_video = False
	# Pegar informações comuns do primeiro dicionário
	item = dicionarios[0].get("ITEM_LEXICAL", "").split("|")
	trans_fon = dicionarios[0].get("TRANSCRICAO_FONEMICA", "").split("|")
	trans_fonet = dicionarios[0].get("TRANSCRICAO_FONETICA", "").split("|")
	classe = dicionarios[0].get("CLASSE_GRAMATICAL", "")
	arquivos_som = dicionarios[0].get('ARQUIVO_SONORO', "").split("|")

	arquivos_som_tratados = []
	if arquivos_som != [""]:
		for i in arquivos_som:
			midia_tag = generate_media_tag(f"{i}", media_type="audio",midia_inclusa=midia_inclusa)
			arquivos_som_tratados.append(midia_tag)
		arquivos_som = arquivos_som_tratados



	html_entrada += f'''\n<div class="entrada_lexical section level2" ordem-alfabetica="{dicionarios[0].get("ID", "").replace("ID-","")}">\n'''  
	html_entrada += f'<div class="div-link" style="position: relative;">\n<a class="link-entrada" name="{dicionarios[0].get("ID", "")}"></a>\n</div>\n'


	html_entrada += "\n\n"
	html_entrada += '<span>\n'
	item_tratado = []
	for idx, i in enumerate(item):
		if arquivos_som[idx] == "":
			item_tratado.append("<span class='palavra_entrada'>" + i + "</span>")
		else:
			item_tratado.append(f'''<span class='palavra_entrada'>{i}
{arquivos_som[idx]}
</span>

''')

	item_tratado = " ~ ".join(item_tratado)
	html_entrada += item_tratado
	html_entrada += '<span class="entradalex"> '

	trans_fon_tratada = []
	trans_fonet_tratada = []

	for i in trans_fon:
		if i:
			trans_fon_tratada.append(f"/{i}/")
	for i in trans_fonet:
		if i:
			trans_fonet_tratada.append(f"[{i}]")
	if trans_fon_tratada or trans_fonet_tratada:
		html_entrada += f'''{" ~ ".join(trans_fon_tratada)} {" ~ ".join(trans_fonet_tratada)}'''

	if classe:
		html_entrada += f"<i> {classe} </i>"

	html_entrada += "</span></span> \n"
	html_entrada += '''\n<div class="entrada_div">\n<div class="info_entrada">\n'''


	# Verificar quantos significados existem
	qtd_significados = len(dicionarios)

	# Adicionar cada significado em sequência
	significados_lista = []

	for i, dic in enumerate(dicionarios, 1):
		traducao = testa_final(dic.get("TRADUCAO_SIGNIFICADO", ""),remove_ponto=True)
		descricao = testa_final(dic.get("DESCRICAO", ""),remove_ponto=True)
		exemplos_trans = dic.get("TRANSCRICAO_EXEMPLO", "").split("|")
		exemplos = dic.get("TRADUCAO_EXEMPLO", "").split("|")
		relacionados = dic.get("ITENS_RELACIONADOS", "")
		imagens = dic.get("IMAGEM", "").split("|")
		legenda_imagens = dic.get("LEGENDA_IMAGEM", "").split("|")
		arquivos_som_exemplo = dic.get("ARQUIVO_SONORO_EXEMPLO", "").split("|")
		arquivos_video_exemplo = dic.get("ARQUIVO_VIDEO", "").split("|")
		if arquivos_som != [""] or arquivos_som_exemplo != [""]:
			tem_audio = True
		if imagens != [""]:
			tem_imagem = True
		if arquivos_video_exemplo != [""]:
			tem_video = True

		if qtd_significados > 1:
			contador = f"{i}. "
		else:
			contador = ""
		significados_lista.append(contador +traducao)
		if traducao or descricao:
			# Verifica se traducao não está vazia
			traducao_formatada = traducao if traducao else ''

			# Verifica se descricao não está vazia
			descricao_formatada = descricao[0].upper() + descricao[1:] if descricao else ''

			# Gera o HTML
			html_entrada += f'''<p>{contador}{traducao_formatada}.</p> {descricao_formatada}'''


		if imagens != "":
			if len(imagens) == 1:
				for filename in os.listdir(os.getcwd() + "/foto"):
					if filename == imagens[0]:
						html_entrada += generate_media_tag(filename, "image",midia_inclusa=midia_inclusa)
						if legenda_imagens != "":
							html_entrada += f'''<span class="legenda-imagem">{legenda_imagens[0]}</span>'''
						break
			else:
				arquivos_imagem = []

				for filename in os.listdir(os.getcwd() + "/foto"):
					if filename in imagens:
						arquivos_imagem.append(filename)
				imagens_organizadas = []
				for img in imagens:
					if img in arquivos_imagem:
						imagens_organizadas.append(img)

				arquivos_imagem = imagens_organizadas
				html_entrada += '''
			<div class="slideshow-container" id="slideshow_''' + dic["ID"] + '''">
			'''

				for arquivo_imagem in arquivos_imagem:
					html_entrada += '''
					<div class="containers">
							''' + generate_media_tag(arquivo_imagem,"image",slide=True,midia_inclusa=midia_inclusa) +'''                                
		'''
					if legenda_imagens != [""]:
						legenda_unica = legenda_imagens[arquivos_imagem.index(arquivo_imagem)]
						html_entrada += '''
							<div class="info">''' + legenda_unica +'''</div><!-- div de legenda -->\n                                                                   
		'''
					html_entrada += "</div><!-- div da imagem -->\n"
				html_entrada += '''
					<!-- Prev and Next buttons -->
					<a class="back" onclick="plusSlides(-1, this)">&#10094;</a>
					<a class="forward" onclick="plusSlides(1, this)">&#10095;</a>

					<div style="text-align:center">'''
				for arquivo_imagem in arquivos_imagem:
					html_entrada += '''                             
							<span class="dots" onclick="currentSlide(''' + str(arquivos_imagem.index(arquivo_imagem)+1) +''', this)"></span>

																'''
				html_entrada += '''
					</div><!-- div da imagem -->
			</div><!-- div da imagem -->
			<br>
		'''


		exemplos_trans, exemplos, arquivos_som_exemplo, arquivos_video_exemplo = preencher_listas(exemplos_trans, exemplos, arquivos_som_exemplo, arquivos_video_exemplo)
		for transcricao, traducao_ex, arquivo_som_exemplo, arquivo_video_exemplo in zip(exemplos_trans, exemplos, arquivos_som_exemplo, arquivos_video_exemplo):

			# Verifica se há tradução e transcrição válidas
			if traducao_ex and transcricao:

				# Caso a transcrição exista
				if transcricao:

					# Verifica se não há arquivo de som e vídeo associado
					if not arquivo_som_exemplo and not arquivo_video_exemplo:
						html_entrada += f'''\n<p style="margin-bottom: 0.1px;"><b><i>{testa_final(transcricao)}</i></b></p>'''
					else:
						# Verifica e gera a tag para arquivo de som, se disponível
						if arquivo_som_exemplo:
							midia_tag = generate_media_tag(f"{arquivo_som_exemplo}", media_type="audio", midia_inclusa=midia_inclusa)

						# Verifica e gera a tag para arquivo de vídeo, se disponível
						if arquivo_video_exemplo:
							midia_tag = generate_media_tag(f'{arquivo_video_exemplo}', "video", midia_inclusa=midia_inclusa)

						# Adiciona a transcrição e a mídia associada ao HTML
						html_entrada += f'''\n<p style="margin-bottom: 0.1px;"><b><i>{testa_final(transcricao)}</i></b> {midia_tag}</p>'''

				# Adiciona a tradução ao HTML
				html_entrada += f'''<p>{testa_final(traducao_ex)}</p>\n'''

		if relacionados != "":
			html_entrada += f"<p><b>Itens relacionados:</b> {relacionados}.</p>"


		for chave in novas_colunas.keys():
			html_entrada += f"<p>{dic[chave]}</p>"
	html_entrada += '\n</div>\n</div>'


	if significados_lista != []:
		html_entrada += f'''<span class="significado-lista" style="display:none;">{" ".join(significados_lista)}</span>\n'''

	if tem_imagem or tem_audio or tem_video:
		html_entrada += '''\n<div class="indicador_midia" style='display:none;'>'''
		if tem_audio:
			html_entrada += '<div class="audio-ico ico_media "></div>'
		if tem_imagem:
			html_entrada += '<div class="imagem-ico ico_media"></div>'      
		if tem_video:
			html_entrada += '<div class="video-ico ico_media "></div>' 
		html_entrada += '</div>\n'

	html_entrada += '''\n<button class="abre_fecha_btn">▼</button>\n</div>\n '''


	return html_entrada

def verificar_barras(dic, campos, ignorar = ['ARQUIVO_SONORO_EXEMPLO','TRANSCRICAO_FONEMICA','TRANSCRICAO_FONETICA','ARQUIVO_VIDEO']):
	contagens = {}

	for campo in campos:
		# Ignorar ARQUIVO_SONORO_EXEMPLO ou TRANSCRICAO_FONEMICA/FONETICA se estiverem vazios
		if dic[campo] == "" and campo in ignorar:
			continue  # Ignora os campos se estiverem vazios
		
		# Se o campo contém "|", conta quantas barras tem
		if "|" in dic[campo]:
			contagens[campo] = dic[campo].count('|')
		else:
			contagens[campo] = 0

	# Se não houver barras, retorna sucesso
	if not contagens:
		return [True,contagens]
	
	# Verifica se todas as contagens de barras são iguais
	valores_distintos = set(contagens.values())
	if len(valores_distintos) == 1:
		return [True,contagens]
	

	return [False,contagens]

def gerar_cabecalho():
	agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
	cabecalho = (
		f"+{'-' * 90}+\n"
		f'''|{'RELATÓRIO DE PENDÊNCIAS, arquivo: "dicionario.csv"'.center(90)}|\n'''
		f"|{('Gerado em: ' + agora).center(90)}|\n"
		#f"+{'-' * 40}+\n\n"
		f"{'=' * 90}\n"
	)
	return cabecalho

def verifica_tabela():
	campos_obrigatorios = ["ITEM_LEXICAL",'TRADUCAO_SIGNIFICADO','CAMPO_SEMANTICO']
	

	arquivos_audio_tabela = set()
	arquivos_video_tabela = set()
	arquivos_imagem_tabela = set()





	dados = abrearquivo()
	contador = 2
	for dic in dados:
		dic["LINHA"] = contador
		contador += 1
		if dic["ARQUIVO_SONORO"] != "":
			for arquivo in dic["ARQUIVO_SONORO"].split("|"):
				arquivos_audio_tabela.add(arquivo)
		if dic['ARQUIVO_SONORO_EXEMPLO'] != "":
			for arquivo in dic['ARQUIVO_SONORO_EXEMPLO'].split("|"):
				arquivos_audio_tabela.add(arquivo)
		if dic["ARQUIVO_VIDEO"] != "":
			for arquivo in dic["ARQUIVO_VIDEO"].split("|"):
				arquivos_video_tabela.add(arquivo)
		if dic["IMAGEM"] != "":
			for arquivo in dic["IMAGEM"].split("|"):
				arquivos_imagem_tabela.add(arquivo)

	quantidade_entradas = len(agrupar_dicionarios(dados))
	quantidade_imagens = len(arquivos_imagem_tabela)
	quantidade_videos =  len(arquivos_video_tabela)
	quantidade_audios = len(arquivos_audio_tabela)
	arquivos_audio_pasta = os.listdir(os.path.join(os.getcwd(), "audio"))
	arquivos_foto_pasta = os.listdir(os.path.join(os.getcwd(), "foto"))
	arquivos_video_pasta = os.listdir(os.path.join(os.getcwd(), "video"))
	erros = {}


	# Loop principal
	for dic in dados:
		erros[dic["LINHA"]] = []
		campos_nao_preenchidos = []
		
		# Verifica campos obrigatórios
		for campo_obrigatorio in campos_obrigatorios:
			if dic[campo_obrigatorio] == "":
				campos_nao_preenchidos.append(campo_obrigatorio)
		
		# Se houver campos não preenchidos, adiciona à lista de erros
		if campos_nao_preenchidos != []:
			erros[dic["LINHA"]].append(f"Campos não preenchidos: {', '.join(campos_nao_preenchidos)}")
		
		# Conjunto 1: Verifica ITEM_LEXICAL, ARQUIVO_SONORO, TRANSCRICAO_FONEMICA, TRANSCRICAO_FONETICA
		resultado_conjunto_1 = verificar_barras(dic, ['ITEM_LEXICAL', 'ARQUIVO_SONORO', 'TRANSCRICAO_FONEMICA', 'TRANSCRICAO_FONETICA'])
		
		if not resultado_conjunto_1[0]:
			erros[dic["LINHA"]].append(f"Erro no uso de barras nas células referentes ao item lexical: {resultado_conjunto_1[1]}")
		
		# Conjunto 2: Verifica ARQUIVO_SONORO_EXEMPLO, TRANSCRICAO_EXEMPLO, TRADUCAO_EXEMPLO, ARQUIVO_VIDEO
		resultado_conjunto_2 = verificar_barras(dic, ['ARQUIVO_SONORO_EXEMPLO','TRANSCRICAO_EXEMPLO', 'TRADUCAO_EXEMPLO', 'ARQUIVO_VIDEO'])
		if not resultado_conjunto_2[0]:
			erros[dic["LINHA"]].append(f"Erro no uso de barras nos campos referentes a exemplos:{resultado_conjunto_2[1]}")
		
		audio_nao_utilizado = []
		if dic["ARQUIVO_SONORO"] != "":
			for arquivo in dic["ARQUIVO_SONORO"].split("|"):
				if arquivo != "":
					if arquivo not in arquivos_audio_pasta:
						audio_nao_utilizado.append(arquivo)
		if dic["ARQUIVO_SONORO_EXEMPLO"] != "":
			for arquivo in dic["ARQUIVO_SONORO_EXEMPLO"].split("|"):
				if arquivo != "":
					if arquivo not in arquivos_audio_pasta:
						audio_nao_utilizado.append(arquivo)
		if audio_nao_utilizado != []:
			erros[dic["LINHA"]].append(f'''Arquivos de áudio não encontrados: {", ".join(audio_nao_utilizado)}''')

		imagem_nao_utilizado = []
		if dic['IMAGEM'] != "":
			for arquivo in dic['IMAGEM'].split("|"):
				if arquivo != "":
					if arquivo not in arquivos_foto_pasta:
						imagem_nao_utilizado.append(arquivo)
		if imagem_nao_utilizado != []:
			erros[dic["LINHA"]].append(f'''Arquivos de imagem não encontrados: {", ".join(imagem_nao_utilizado)}''')
		
		video_nao_utilizado = []
		if dic['ARQUIVO_VIDEO'] != "":
			for arquivo in dic['ARQUIVO_VIDEO'].split("|"):
				if arquivo != "":
					if arquivo not in arquivos_video_pasta:
						video_nao_utilizado.append(arquivo)
		if video_nao_utilizado != []:
			erros[dic["LINHA"]].append(f'''Arquivos de vídeo não encontrados: {", ".join(video_nao_utilizado)}''')

	# Diretórios das pastas
	pasta_audio = os.path.join(os.getcwd(), "audio")
	pasta_foto = os.path.join(os.getcwd(), "foto")
	pasta_video = os.path.join(os.getcwd(), "video")		

	mover_nao_utilizados(arquivos_audio_pasta, arquivos_audio_tabela, pasta_audio, "audio")
	mover_nao_utilizados(arquivos_foto_pasta, arquivos_imagem_tabela, pasta_foto, "imagem")
	mover_nao_utilizados(arquivos_video_pasta, arquivos_video_tabela, pasta_video, "video")

	entradas_sem_audio = 0
	entradas_sem_video = 0
	entradas_sem_foto = 0
	for dic in dados:
		if dic["ARQUIVO_SONORO"] == "" and dic["ARQUIVO_SONORO_EXEMPLO"] == "":
			entradas_sem_audio += 1
		if dic["IMAGEM"] == "":
			entradas_sem_foto += 1
		if dic["ARQUIVO_VIDEO"] == "":
			entradas_sem_video += 1


	# Escrevendo o relatório
	with open("PENDENCIAS_TABELA.txt", "w", encoding="utf-8") as arquivo_erro:
		arquivo_erro.write(gerar_cabecalho())
		arquivo_erro.write(f" QUANTIDADE DE ENTRADAS: {quantidade_entradas}\n")
		arquivo_erro.write(f" QUANTIDADE DE AUDIOS: {quantidade_audios}\n")
		arquivo_erro.write(f" QUANTIDADE DE IMAGENS: {quantidade_imagens}\n")
		arquivo_erro.write(f" QUANTIDADE DE VIDEOS: {quantidade_videos}\n")
		arquivo_erro.write(f"{'-' * 90}\n\n")
		arquivo_erro.write(f" QUANTIDADE DE ENTRADAS SEM AUDIO: {entradas_sem_audio}\n")
		arquivo_erro.write(f" QUANTIDADE DE ENTRADAS SEM IMAGENS: {entradas_sem_foto}\n")
		arquivo_erro.write(f" QUANTIDADE DE ENTRADAS SEM VIDEOS: {entradas_sem_video}\n\n")

		sem_pendencias = True
		for linha in erros:
			if erros[linha] != []:
				sem_pendencias = False
				break

		if sem_pendencias:
			arquivo_erro.write(f"{'=' * 90}\n\n")
			arquivo_erro.write(f"SEM PENDÊNCIAS DE CAMPOS OU ARQUIVOS\n".center(90))
		else:
			arquivo_erro.write(f"{'=' * 90}\n")
			arquivo_erro.write("LISTA DE ERROS:\n".center(90))
			for linha, lista_erros in erros.items():
				if lista_erros:
					arquivo_erro.write(f"\nLINHA {linha}:\n")
	
					# Dentro do seu loop, onde você escreve os erros:
					for erro in erros[linha]:
						# Quebrando o erro em várias linhas com no máximo 60 caracteres
						erro_quebrado = textwrap.wrap(erro, width=900)
						
						# Escreve a primeira linha com a barra e as demais sem a barra
						arquivo_erro.write(f"--> {erro_quebrado[0]}\n")
						
						# Para as linhas subsequentes, não usar a barra
						for linha_quebrada in erro_quebrado[1:]:
							arquivo_erro.write(f"    {linha_quebrada}\n")

		arquivo_erro.write(f"\n{'=' * 90}\n")

def criar_tabela():
	# Verifica se o arquivo dicionario.csv já existe
	if not os.path.exists('dicionario.csv'):
		# Cria o DataFrame com as colunas especificadas
		df = pd.DataFrame(columns=[
			'ID',
			'ITEM_LEXICAL',
			'IMAGEM',
			'ARQUIVO_SONORO',
			'TRANSCRICAO_FONEMICA',
			'TRANSCRICAO_FONETICA',
			'CLASSE_GRAMATICAL',
			'TRADUCAO_SIGNIFICADO',
			'DESCRICAO',
			'ARQUIVO_SONORO_EXEMPLO',
			'TRANSCRICAO_EXEMPLO',
			'TRADUCAO_EXEMPLO',
			'ARQUIVO_VIDEO',
			'CAMPO_SEMANTICO',
			'SUB_CAMPO_SEMANTICO',
			'ITENS_RELACIONADOS'
		]).fillna('')
		
		# Salva o DataFrame em um arquivo CSV
		df.to_csv('dicionario.csv', index=False, encoding='utf-8')
	else:
		input("O arquivo dicionario.csv já existe, arquivo não criado!")

def selecionar_campos_semanticos(
	titulo, 
	campos_semanticos,  
	tamanho=77):
	"""
	Função que recebe uma lista de campos semânticos e usa o inquirer para
	permitir que o usuário selecione os campos que NÃO deseja utilizar.
	
	Args:
		titulo (str): Título do menu.
		campos_semanticos (list): Lista de campos semânticos.
		texto_explicativo (str, opcional): Texto explicativo para o menu.
		tamanho (int, opcional): Largura do menu, padrão é 77 caracteres.
	
	Returns:
		list: Lista de campos que o usuário deseja manter, em ordem alfabética.
	"""
	
	
	chave_parametro = "Manter a ordem alfabética"
	valor_parametro = verificar_e_executar(chave_parametro)
	if valor_parametro:
		opcao = valor_parametro
	else:
		opcao = imprimir_menu("Manter a ordem alfabética automática em todo documento?",["Sim","Não"])
		salvar_parametros({chave_parametro: opcao}) 
		if opcao == "1":
			return campos_semanticos

	
	chave_parametro = "Usar ordem alfabética"
	valor_parametro = verificar_e_executar(chave_parametro)
	print(valor_parametro)
	if valor_parametro:
		return valor_parametro.split(",")
	else:	
		
		
		texto_explicativo = '''Instruções para seleção dos elementos: 1 -> Use as setas ↑ e ↓ para navegar pelas opções. 2 -> Pressione a tecla [Espaço] para selecionar ou desmarcar uma opção. 3 -> Depois de selecionar os campos que deseja EXCLUIR, pressione [Enter] para confirmar.'''


		# Exibir o título e bordas do menu
		print("+" + "-" * tamanho + "+")
		print("\u2502" + titulo.ljust(tamanho) + "\u2502")
		print("+" + "-" * tamanho + "+")
		
		# Se houver texto explicativo, exibi-lo
		if texto_explicativo is not None:
			linhas = dividir_texto(texto_explicativo, tamanho)
			for linha in linhas:
				print("\u2502" + linha.ljust(tamanho) + "\u2502")
			print("+" + "-" * tamanho + "+")
		
		

		
		pergunta = [
			inquirer.Checkbox('excluir',
							message="Selecione os campos que você em que deseja usar ordenação alfabética",
							choices=campos_semanticos)
		]
		
		
		resposta = inquirer.prompt(pergunta)
		campos_selecionados = set(resposta['excluir'])  
		
		
		
		# Exibir borda final e retornar lista de campos restantes ordenada
		print("+" + "-" * tamanho + "+")
		salvar_parametros({chave_parametro: ",".join(list(campos_selecionados))})
		return list(campos_selecionados)

def gerar_script_tags_audio():
	dados = abrearquivo()
	arquivos_audio_tabela = set()

	for dic in dados:
		if dic["ARQUIVO_SONORO"] != "":
			for arquivo in dic["ARQUIVO_SONORO"].split("|"):
				arquivos_audio_tabela.add(arquivo)
		if dic['ARQUIVO_SONORO_EXEMPLO'] != "":
			for arquivo in dic['ARQUIVO_SONORO_EXEMPLO'].split("|"):
				arquivos_audio_tabela.add(arquivo)


	midia_tag = """\n<script>\nconst audioDictionary = {\n\n"""

	for audio in list(arquivos_audio_tabela):
		
		if audio != "":
			midia_tag += f'''"{audio}":"data:audio/mp3;base64,{file_to_base64(os.path.join(os.getcwd(),r"audio/",audio))}",\n'''
	midia_tag += """};\n</script>\n"""
	
	return midia_tag

def cria_arquivos_configuracao():
	with open('intro_html.txt', "a+", encoding="UTF-8") as arquivo:
		arquivo.write(r'''
Utilize este arquivo para adicionar uma introdução ao seu dicionário. Apague todo o conteúdo existente neste arquivo e insira sua introdução aqui. Você pode usar elementos de Markdown para formatar o texto. Markdown é uma linguagem de marcação simples que permite a formatação de texto de maneira prática e sem a complexidade do HTML.

### 1. Títulos

Você pode criar títulos usando o símbolo de cerquilha (`#`). O número de cerquilhas indica o nível do título. Por exemplo:

```markdown
# Título de Nível 1
## Título de Nível 2
### Título de Nível 3
```

### 2. Ênfase

Para enfatizar texto, você pode usar asteriscos ou sublinhados:

- **Texto em negrito:** `**este texto**` ou `__este texto__`
- *Texto em itálico:* `*este texto*` ou `_este texto_`

### 3. Listas

Você pode criar listas não ordenadas e ordenadas:
```
- Lista não ordenada:
  - Item 1
  - Item 2
	- Subitem 2.1
- Lista ordenada:
  1. Primeiro item
  2. Segundo item
	 2.1. Subitem 2.1
```
### 4. Links

Para adicionar links, use a seguinte sintaxe:

```markdown
[Visite nosso site](https://dicionarios.museu-goeldi.br)
```

Exemplo: [Visite nosso site](https://dicionarios.museu-goeldi.br)

### 5. Imagens

Para adicionar imagens, use a sintaxe semelhante à dos links, mas comece com um ponto de exclamação:

```markdown
![Texto Alternativo](https://www.exemplo.com/imagem.jpg)
```

### 6. Citações

Você pode criar citações usando o símbolo de maior (`>`):

```markdown
> "Esta é uma citação."
```

### 7. Código

Para destacar código, use crases simples para trechos de código em linha:

```markdown
`código em linha`
```

Para blocos de código, use três crases:

````markdown
```
print("Olá, mundo!")
```
````


### 8. Tabelas

Para criar tabelas no Markdown, você pode usar colunas separadas por barras verticais (`|`) e linhas de cabeçalho separadas por hífens (`-`). A quantidade de hífens indica onde a linha de cabeçalho termina e o conteúdo da tabela começa. Você pode alinhar o texto das colunas usando os dois-pontos (`:`) na linha de cabeçalho.

**Exemplo básico de tabela:**

```markdown
| Coluna 1       | Coluna 2      | Coluna 3      |
|----------------|---------------|---------------|
| Conteúdo 1     | Conteúdo 2    | Conteúdo 3    |
| Mais conteúdo  | Mais conteúdo | Mais conteúdo |
```

**Exemplo de tabela com alinhamento:**

```markdown
| Alinhado à Esquerda | Centralizado      | Alinhado à Direita |
|:--------------------|:-----------------:|--------------------:|
| Texto à esquerda    | Texto centralizado| Texto à direita     |
| Mais texto          | Mais texto        | Mais texto          |
```

Esse exemplo será renderizado como:

| Alinhado à Esquerda | Centralizado      | Alinhado à Direita |
|:--------------------|:-----------------:|--------------------:|
| Texto à esquerda    | Texto centralizado| Texto à direita     |
| Mais texto          | Mais texto        | Mais texto          |

''')
	
	with open('intro_pdf.txt', "a+", encoding="UTF-8") as arquivo:	
		arquivo.write(r'''

Você deve utilizar este arquivo para adicionar uma introdução ao seu dicionário. Apague todo o conteúdo existente neste arquivo e insira sua introdução aqui. São permitidos elementos do **LaTeX** para formatar seu texto. **LaTeX** é uma linguagem de marcação usada para a criação de documentos, especialmente na área acadêmica, e oferece um controle avançado sobre a formatação.

\section{1. Títulos}

Você pode criar títulos utilizando os comandos \texttt{\textbackslash section}, \texttt{\textbackslash subsection}, \texttt{\textbackslash subsubsection}, e outros. A estrutura de títulos no LaTeX segue uma hierarquia definida por esses comandos. Por exemplo:

\begin{verbatim}
\section{Título de Nível 1}
\subsection{Título de Nível 2}
\subsubsection{Título de Nível 3}
\end{verbatim}

\section{2. Ênfase}

Para enfatizar o texto, você pode usar os seguintes comandos:

\begin{itemize}
  \item \textbf{Texto em negrito}: \verb|\textbf{este texto}|
  \item \textit{Texto em itálico}: \verb|\textit{este texto}|
\end{itemize}

Exemplo:

\begin{verbatim}
\textbf{Texto em negrito} e \textit{Texto em itálico}
\end{verbatim}

\section{3. Listas}

Você pode criar listas não ordenadas e ordenadas:

\subsection{Lista não ordenada}

\begin{verbatim}
\begin{itemize}
    \item Item 1
    \item Item 2
    \item Subitem 2.1
\end{itemize}
\end{verbatim}

\subsection{Lista ordenada}

\begin{verbatim}
\begin{enumerate}
    \item Primeiro item
    \item Segundo item
    \begin{enumerate}
        \item Subitem 2.1
    \end{enumerate}
\end{enumerate}
\end{verbatim}

\section{4. Links}

Para adicionar links em LaTeX, você pode usar o pacote \texttt{hyperref}. Exemplo:

\begin{verbatim}
\href{https://dicionarios.museu-goeldi.br}{Visite nosso site}
\end{verbatim}

Exemplo: \href{https://dicionarios.museu-goeldi.br}{Visite nosso site}

\section{5. Imagens}

Para adicionar imagens, use o seguinte comando:

\begin{verbatim}
\begin{figure}[h]
    \centering
    \includegraphics[width=0.5\textwidth]{imagem.jpg}
    \caption{Texto Alternativo}
\end{figure}
\end{verbatim}

\section{6. Citações}

Você pode criar citações utilizando o comando \texttt{quote}:

\begin{verbatim}
\begin{quote}
    "Esta é uma citação."
\end{quote}
\end{verbatim}

\section{7. Código}

Para destacar código em LaTeX, você pode usar o ambiente \texttt{verbatim} para blocos de código:

\begin{verbatim}
print("Olá, mundo!")
\end{verbatim}

Ou para trechos de código em linha, use o comando \verb|\texttt{}|:

\begin{verbatim}
\texttt{código em linha}
\end{verbatim}

\section{8. Tabelas}

Para criar tabelas em LaTeX, você pode usar o ambiente \texttt{tabular}. Aqui está um exemplo básico de uma tabela:

\begin{verbatim}
\begin{tabular}{|c|c|c|}
    \hline
    Coluna 1 & Coluna 2 & Coluna 3 \\
    \hline
    Conteúdo 1 & Conteúdo 2 & Conteúdo 3 \\
    Mais conteúdo & Mais conteúdo & Mais conteúdo \\
    \hline
\end{tabular}
\end{verbatim}

Você também pode alinhar o texto das colunas usando as opções de alinhamento: \texttt{l} (esquerda), \texttt{c} (centro) e \texttt{r} (direita):

\begin{verbatim}
\begin{tabular}{|l|c|r|}
    \hline
    Alinhado à Esquerda & Centralizado & Alinhado à Direita \\
    \hline
    Texto à esquerda & Texto centralizado & Texto à direita \\
    Mais texto & Mais texto & Mais texto \\
    \hline
\end{tabular}
\end{verbatim}

Esse exemplo será renderizado como:

\begin{tabular}{|l|c|r|}
    \hline
    Alinhado à Esquerda & Centralizado & Alinhado à Direita \\
    \hline
    Texto à esquerda & Texto centralizado & Texto à direita \\
    Mais texto & Mais texto & Mais texto \\
    \hline
\end{tabular}


''')	
	
	with open("referencia.txt", "a+", encoding="UTF-8") as arquivo:
		arquivo.write('''AUTOR(ES)=SOBRENOME, Nome
ANO=2023
TITULO=Dicionário de Teste
VERSAO= Versão 2.0
LOCAL=Belém
EDITOR=Editora Exemplo
LINK=https://dicionarios.museu-goeldi.br
''')

def cria_ref(formato="html"):
	# Lê o arquivo txt e converte as linhas em um dicionário chave-valor
	
	try:
		elementos = {}	
		with open("referencia.txt", 'r', encoding='utf-8') as f:
			for line in f:
				key, value = line.strip().split('=', 1)
				elementos[key.upper()] = value.strip()

		# Função para adicionar uma parte da citação se o elemento existir
		def add_if_present(key, before='', after=''):
			return f"{before}{elementos[key]}{after}" if key in elementos else ''

		# Formatar a citação em HTML
		if formato == "html":
			citacao = f"""<p>{add_if_present('AUTOR(ES)',after=". ")}{add_if_present('ANO',after=". ")}<strong>{add_if_present('TITULO')}</strong>{add_if_present('VERSAO', '. ', '')}{add_if_present('LOCAL', '. ')}{add_if_present('EDITOR', ': ')}{add_if_present('LINK', '. Disponível em: <a href="', '">')}{add_if_present('LINK', after='</a>')}</p>"""

		# Formatar a citação em LaTeX
		elif formato == "latex":
			citacao = (
				f"{add_if_present('AUTOR(ES)',after=". ")}{add_if_present('ANO', after=". ")}"
				+ "\\textbf{" + add_if_present('TITULO') + "}"
				+ add_if_present('VERSAO', '. ', '')
				+ add_if_present('LOCAL', '. ') + add_if_present('EDITOR', ': ')
			+ add_if_present('LINK', '. Disponível em: \\url{', '}')
		)

		# Limpa espaços extras e retorna a citação
		return citacao.strip()
	except FileNotFoundError:
		referencia_html = ""
		return referencia_html



def init():
	opcao = 0
	while opcao != "5":
		opcao = imprimir_menu("CSV2RMD", ["Validar tabela ('dicionario.csv')","Gerar  PDF",'Gerar HTML','Gerar arquivos de configuração','Sair'])
		if opcao == "1":
			verifica_tabela()
			opcaovalidacao = "0"
			while opcaovalidacao != "1" and opcaovalidacao != "2":
				opcaovalidacao = imprimir_menu("Validar tabela ('dicionario.csv')", ["Voltar ao menu inicial","sair"],"Validação terminada (Encontre os arquivos referentes na mesma pasta: " + str(os.getcwd()))
				if opcaovalidacao == "2":
					opcao = "5"

		if opcao == "2":
			opcaosimples = imprimir_menu("Gerar PDF", ["Gerar PDF com opções padrão ","Gerar PDF costumizado"], "A opção de customização oferece passos adicionais para: ordem alfabética e ordem dos campos semânticos. Para gerar um PDF você precisa ter MiKTeX instalado")
			if opcaosimples == "1":
				cria_pdf()
			if opcaosimples == "2":
				cria_pdf(opcao_simples=False)
			opcaovalidacao = "0"
			while opcaovalidacao != "1" and opcaovalidacao != "2":
				opcaovalidacao = imprimir_menu("Gerar PDF", ["Voltar ao menu inicial","sair"],"Processo encerrado verifique a pasta 'pdf' para acesssar o PDF ou os logs de erro")
				if opcaovalidacao == "2":
					opcao = "5"
		if opcao == "3":
			opcaosimples = imprimir_menu("Gerar HTML", ["Gerar os HTML opções padrão","Customizar HTML"], "A opção de customização oferece passos adicionais para: midias inclusas, ordem alfabética e ordem dos campos semânticos")
			if opcaosimples == "1":
				cria_html()
			if opcaosimples == "2":				
				chave_parametro = "Midias_inclusas"
				valor_parametro = verificar_e_executar(chave_parametro)
				if valor_parametro:
					opcaomidia = valor_parametro
				else:
					opcaomidia = imprimir_menu("Gerar HTML",["Gerar HTML com mídias inclusas", "Gerar HTML com mídias externas"],"Você pode gerar um HTML com mídias inclusas em BASE64, ou criar um HTML com mídias separadas em pastas")
					salvar_parametros({chave_parametro: opcaomidia})
				
				if opcaomidia == "1":
					cria_html(opcao_simples=False)
				if opcaomidia == "2":
					cria_html(opcao_simples=False, midia_inclusa=False)

			opcaovalidacao = "0"
			while opcaovalidacao != "1" and opcaovalidacao != "2":
				opcaovalidacao = imprimir_menu("Gerar HTML único", ["Voltar ao menu inicial","sair"],"Arquivo HTML gerado na pasta 'html'")
				if opcaovalidacao == "2":
					opcao = "5"


		if opcao == "4":
			opcaosimples = imprimir_menu("Gerar arquivos de configuração", ["Gerar tabela vazia","Gerar arquivo para introdução e referência"])
			if opcaosimples == "1":
				criar_tabela()
			if opcaosimples == "2":
				cria_arquivos_configuracao()


			opcaovalidacao = "0"
			while opcaovalidacao != "1" and opcaovalidacao != "2":
				opcaovalidacao = imprimir_menu("Gerar arquivos de configuração", ["Voltar ao menu inicial","sair"],"Arquivos gerados no diretório raiz")
				if opcaovalidacao == "2":
					opcao = "5"



if __name__ == "__main__":
    try:
        init()
    except Exception as e:
        # Captura a exceção e exibe uma mensagem de erro
        print("Ocorreu um erro no programa.")
        traceback.print_exc()  # Mostra a exceção completa com o rastreamento
        input("Pressione Enter para fechar...")  # Mantém a janela aberta até o usuário pressionar Enter





'''lista = abrearquivo()
campos, campos_normalizados, dic_subcampos = listar_campos_semanticos(lista)
novas = listar_novas_colunas(lista)
lista = ordenar_dicionarios(lista,"ITEM_LEXICAL")
lista = agrupar_dicionarios(lista)

with open("teste.html","a",encoding="utf-8") as arquivo:
		arquivo.write(gera_entrada_html(lista[-1],novas_colunas=novas,midia_inclusa=False))
		#print(gera_entrada_html(lista[-1],novas_colunas=novas,midia_inclusa=False))

cria_html()'''
