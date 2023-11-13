
# -*- coding: utf-8 -*-
#quando a tabela for modificada e necessário modificar as chamadas dos campos em: criar pdf (2x pt e lingua) criar html legenda e sem legenda e na revisao de arquivos e campos

import os
import shutil
import re
import unicodedata
import pandas as pd
import locale
colunas_padrao = ['ID','ITEM_LEXICAL','IMAGEM',"LEGENDA_IMAGEM",'ARQUIVO_SONORO','TRANSCRICAO_FONEMICA','TRANSCRICAO_FONETICA','CLASSE_GRAMATICAL','TRADUCAO_SIGNIFICADO','DESCRICAO','ARQUIVO_SONORO_EXEMPLO','TRANSCRICAO_EXEMPLO','TRADUCAO_EXEMPLO','ARQUIVO_VIDEO','CAMPO_SEMANTICO',"SUB_CAMPO_SEMANTICO","ITENS_RELACIONADOS"]
configuracoes = 'configuracao.txt'

# Copiar arquivo de gerar produtos

def copiar_arquivo_para_subpasta(nome_arquivo, subpasta_destino):
    # Obtém o caminho absoluto da pasta "02-SCRIPTS-AUXILIARES" no mesmo diretório
    diretorio_atual = os.getcwd()
    caminho_pasta_auxiliar = os.path.join("..", "02-SCRIPTS-AUXILIARES")
    
    # Caminho completo do arquivo de origem
    
    caminho_origem = os.path.join(caminho_pasta_auxiliar, nome_arquivo)
    
    # Caminho completo para a subpasta de destino
    caminho_destino = os.path.join(diretorio_atual, subpasta_destino)
    try:
        # Verifica se a subpasta de destino existe, se não, a cria
        if not os.path.exists(caminho_destino):
            os.makedirs(caminho_destino)
        
        # Copia o arquivo para a subpasta de destino
        shutil.copy(caminho_origem, caminho_destino)
    except Exception as e:
        pass

#salva as respostas em txt para as proximas execuções
def salvar_parametros(parametros):
    existing_params = carregar_parametros() if os.path.exists(configuracoes) else {}  # Carrega os parâmetros existentes do arquivo se ele existir

    existing_params.update(parametros)  # Atualiza os parâmetros existentes com os novos valores

    with open(configuracoes, 'w', encoding="UTF-8") as arquivo:
        for chave, valor in existing_params.items():
            arquivo.write(f"{chave}={valor}\n")
def carregar_parametros():
    parametros = {}
    try:
        with open(configuracoes, 'r', encoding="UTF-8") as arquivo:
            linhas = arquivo.readlines()
            for linha in linhas:
                chave, valor = linha.strip().split('=')
                parametros[chave] = valor
    except:
        pass
    return parametros
def verificar_e_executar(chave):
    parametros = carregar_parametros()
    if chave in parametros:
        valor = parametros[chave]
        # Faça algo com o valor, atribua-o a uma variável, etc.
        return valor
    else:
        return False

#menu inicial e funções para gerar menus
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
    print("+" + "-" * tamanho + "+")
    print("\u2502" + " " * tamanho + "\u2502")
    print("\u2502" + titulo.center(tamanho) + "\u2502")
    print("\u2502" + " " * tamanho + "\u2502")
    print("+" + "-" * tamanho + "+")

    if texto_explicativo is not None:
        linhas = dividir_texto(texto_explicativo, tamanho)
        for linha in linhas:
            print("\u2502" + linha + "\u2502")
        print("+" + "-" * tamanho + "+")

    for i, opcao in enumerate(opcoes):
        print("\u2502 [" + str(i+1) + "] - " + opcao.ljust(tamanho-7) + "\u2502")
    print("+" + "-" * tamanho + "+")

    escolha = input("Digite o número da opção desejada: ")

    # Loop while para validar a entrada do usuário
    while escolha not in map(str, range(1, len(opcoes)+1)):
        print("Opção inválida. Tente novamente.")
        escolha = input("Digite o número da opção desejada: ")

    return escolha
def menu_simples(titulo, lista_referencia=None, texto_explicativo=None, tamanho=77, resposta_obrigatoria=True):
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
            resposta = input("Digite sua resposta (separe os elementos por vírgula): ")
        else:
            resposta = input("Digite sua resposta: ")

        # Se a lista de referência for None, aceitamos qualquer resposta
        if lista_referencia is None:
            return resposta

        # Converter a lista de referência para um conjunto para facilitar a verificação
        conjunto_referencia = set(map(str, lista_referencia))

        # Dividir a resposta do usuário em elementos individuais por vírgula
        elementos_resposta = set(resposta.split(','))

        # Verificar se todos os elementos da resposta estão no conjunto de referência
        if resposta_obrigatoria and not elementos_resposta.issuperset(conjunto_referencia):
            print("A resposta deve conter todos os elementos da lista de referência.")
        else:
            # Verificar se não há elementos em excesso na sequência
            elementos_excesso = elementos_resposta - conjunto_referencia

            if elementos_excesso:
                print("Elementos em excesso na sequência:", ', '.join(sorted(elementos_excesso)))
            else:
                return resposta
def init(): #inicia o funcionamento do script
    opcao = 0
    while opcao != "5":
        opcao = imprimir_menu("CSV2RMD", ["Validar tabela ('dicionario.csv')","Gerar arquivos RMD para criar PDF",'Gerar arquivos RMD para criar HTML','Gerar arquivo RMD para criar HTML único','Sair'])
        if opcao == "1":
            dicionario = abrearquivo()
            validacao_tabela_campos(dicionario)
            validacao_tabela_arquivos(dicionario)
            opcaovalidacao = "0"
            while opcaovalidacao != "1" and opcaovalidacao != "2":
                opcaovalidacao = imprimir_menu("Validar tabela ('dicionario.csv')", ["Voltar ao menu inicial","sair"],"Validação terminada (Encontre os arquivos referentes na mesma pasta: " + str(os.getcwd()))
                if opcaovalidacao == "2":
                    opcao = "5"
        if opcao == "2":   
            dicionario = abrearquivo()
            opcaosimples = imprimir_menu("Gerar arquivos RMD para criar PDF", ["Gerar os RMDS com opções padrão","Customizar os RMD's"], "A opção de customização oferece passos adicionais para: legendas em áudios, ordem alfabética e ordem dos campos semânticos")
            if opcaosimples == "2":       
                cria_pdf(dicionario,opcao_simples=False)
                opcaohtml = "0"
                while opcaohtml != "1" and opcaohtml != "2":
                    opcaohtml = imprimir_menu("Gerar arquivos RMD para criar PDF", ["Voltar ao menu inicial","sair"],"Arquivos RMD criados na pasta pdf")
                    if opcaohtml == "2":
                        opcao = "5"
            elif opcaosimples == "1":
                cria_pdf(dicionario)
                opcaohtml = "0"
                while opcaohtml != "1" and opcaohtml != "2":
                    opcaohtml = imprimir_menu("Gerar arquivos RMD para criar PDF", ["Voltar ao menu inicial","sair"],"Arquivos RMD criados na pasta pdf")
                    if opcaohtml == "2":
                        opcao = "5"
        if opcao == "3":
            dicionario = abrearquivo()
            opcaosimples = imprimir_menu("Gerar arquivos RMD para criar HTML", ["Gerar os RMDS com opções padrão","Customizar os RMD's"], "A opção de customização oferece passos adicionais para: legendas em áudios, ordem alfabética e ordem dos campos semânticos")

            if opcaosimples == "2":  

                chave_parametro = "Opção de legenda automática para áudio"
                valor_parametro = verificar_e_executar(chave_parametro)
                if valor_parametro:
                    opcaolegenda = valor_parametro
                else:
                    opcaolegenda = imprimir_menu("Opção de legenda para áudio e vídeo",['Não usar legendas automáticas','Usar legendas automáticas'],'''Para adicionar informação de autor e data aos arquivos de áudio e vídeo, e necessário 
        adicionar junto ao 'dicionario.csv' um arquivo 'atores.csv' com uma coluna para sigla 
        do falante (código) e outra para o nome como deve aparecer no html. Para essa opção 
        os arquivos devem ter sido nomeados de acordo com o padrão de nomenclatura do Museu 
        Goeldi''')
                    salvar_parametros({chave_parametro: opcaolegenda})     
                




                if opcaolegenda == "2":
                    cria_html(dicionario,True,False)
                    opcaohtml = "0"
                    while opcaohtml != "1" and opcaohtml != "2":
                        opcaohtml = imprimir_menu("Gerar arquivos RMD para criar HTML", ["Voltar ao menu inicial","sair"],"Arquivos RMD criados na pasta html")
                        if opcaohtml == "2":
                            opcao = "5"


                if opcaolegenda == "1":
                    cria_html(dicionario,opcao_simples=False)
                    opcaohtml = "0"
                    while opcaohtml != "1" and opcaohtml != "2":
                        opcaohtml = imprimir_menu("Gerar arquivos RMD para criar HTML", ["Voltar ao menu inicial","sair"],"Arquivos RMD criados na pasta html")
                        if opcaohtml == "2":
                            opcao = "5"
            elif opcaosimples == "1":
                cria_html(dicionario,False,True)
                opcaohtml = "0"
                while opcaohtml != "1" and opcaohtml != "2":
                    opcaohtml = imprimir_menu("Gerar arquivos RMD para criar HTML", ["Voltar ao menu inicial","sair"],"Arquivos RMD criados na pasta html")
                    if opcaohtml == "2":
                        opcao = "5"
        if opcao == "4":
            dicionario = abrearquivo()
            opcaosimples = imprimir_menu("Gerar arquivos RMD para criar HTML único", ["Gerar os RMDS com opções padrão","Customizar os RMD's"], "A opção de customização oferece passos adicionais para: legendas em áudios, ordem alfabética e ordem dos campos semânticos")

            if opcaosimples == "2":       
                chave_parametro = "Opção de legenda automática para áudio"
                valor_parametro = verificar_e_executar(chave_parametro)
                if valor_parametro:
                    opcaolegenda = valor_parametro
                else:
                    opcaolegenda = imprimir_menu("Opção de legenda para áudio e vídeo",['Não usar legendas automáticas','Usar legendas automáticas'],'''Para adicionar informação de autor e data aos arquivos de áudio e vídeo, e necessário 
        adicionar junto ao 'dicionario.csv' um arquivo 'atores.csv' com uma coluna para sigla 
        do falante (código) e outra para o nome como deve aparecer no html. Para essa opção 
        os arquivos devem ter sido nomeados de acordo com o padrão de nomenclatura do Museu 
        Goeldi''')
                    salvar_parametros({chave_parametro: opcaolegenda})

                if opcaolegenda == "2":
                    cria_html_unico(dicionario,True,False)
                    opcaohtml = "0"
                    while opcaohtml != "1" and opcaohtml != "2":
                        opcaohtml = imprimir_menu("Gerar arquivos RMD para criar HTML único", ["Voltar ao menu inicial","sair"],"Arquivos RMD criados na pasta html único")
                        if opcaohtml == "2":
                            opcao = "5"


                if opcaolegenda == "1":
                    cria_html_unico(dicionario,opcao_simples=False)
                    opcaohtml = "0"
                    while opcaohtml != "1" and opcaohtml != "2":
                        opcaohtml = imprimir_menu("Gerar arquivos RMD para criar HTML único", ["Voltar ao menu inicial","sair"],"Arquivos RMD criados na pasta html único")
                        if opcaohtml == "2":
                            opcao = "5"
            elif opcaosimples == "1":
                cria_html_unico(dicionario,False,True)
                opcaohtml = "0"
                while opcaohtml != "1" and opcaohtml != "2":
                    opcaohtml = imprimir_menu("Gerar arquivos RMD para criar HTML", ["Voltar ao menu inicial","sair"],"Arquivos RMD criados na pasta html único")
                    if opcaohtml == "2":
                        opcao = "5"

#Abrir o arquivo csv
def abrearquivo():
    arquivo = os.path.join(os.getcwd(), "dicionario.csv")
    try:
        df_temp = pd.read_csv(arquivo)
        df_temp = df_temp.fillna('')
        df_temp.columns = df_temp.columns.str.upper()
        colunas_df = list(df_temp.columns)  

        # Filtrar colunas que não começam com '#'
        colunas_df = [coluna for coluna in df_temp.columns if not coluna.startswith('#')]

        if colunas_padrao == colunas_df:
            return df_temp
        else:
            df = pd.DataFrame(columns=colunas_padrao)
             
            for coluna in colunas_padrao:
                if coluna in colunas_df:
                    df[coluna] = df_temp[coluna].values
                    colunas_df.remove(coluna)
            
            for coluna in colunas_df:
                df[coluna] = df_temp[coluna].values
            df = df.fillna('')
            return df
    except (FileNotFoundError, IOError):
        resposta = '99999999244885'
        while resposta != '1':
            resposta = imprimir_menu("Erro de arquivo", ["sair"],"arquivo não encontrado - Caminho não encontrado: " + arquivo)
        exit()

# Listar colunas adicionais, os campos semanticos utilizados e reunir os campos com mesmo significado
def listar_novas_colunas(dataframe):
    '''Retorna uma lista de novas colunas adicionadas no planilha original'''
    colunas_df = list(dataframe.columns)
    novas_colunas = []
    if colunas_padrao != colunas_df:    # pegar possiveis colunas extras
        for i in colunas_df:
            if i not in colunas_padrao:
                novas_colunas.append(i)
    return novas_colunas
def titulo_autor():
    chave_parametro = "Título"
    valor_parametro = verificar_e_executar(chave_parametro)
    if valor_parametro:
        titulo = valor_parametro
    else:
        titulo = menu_simples("Digite o título do documento")
        salvar_parametros({chave_parametro: titulo})

    chave_parametro = "Autor(es)"
    valor_parametro = verificar_e_executar(chave_parametro)
    if valor_parametro:
        autor = valor_parametro
    else:
        autor = menu_simples("Digite o nome do(s) autor(es) documento")
        salvar_parametros({chave_parametro: autor})

    return titulo,autor
def listar_campos_semanticos(dataframe,opcao_ordem=False):
    '''Cria duas listas de campos semanticos:
    primeira: lista padrão com os campos semânticos do jeito que estão no csv
    segunda: lista de campos semanticos normalizada e sem acento para criar os arquivos "RMD" com nomenclatura correta.
    '''
    campos = []
    campos_semanticos = []
    campos_semanticos_normalizado = []
    sub = []
    sub_campos = []
    sub_campos_normalizado = []



    contador_linha = 1  # Inicializamos o contador de linha

    campos = []
    sub = []

    for i in range(len(dataframe)):  # usar len(dataframe) para iterar sobre as linhas
        campo_semantico = dataframe['CAMPO_SEMANTICO'][i]
        sub_campo = dataframe["SUB_CAMPO_SEMANTICO"][i]

        contador_linha += 1  # Incrementar o contador de linha após cada iteração

        if campo_semantico == '':
            imprimir_menu('Erro no preenchimento dos campos semânticos',['Sair'], 'Preencha o campo semântico do item na linha '+ str(contador_linha)+ ' do arquivo "dicionario.csv".')
            exit()

        if campo_semantico.capitalize() not in campos:
            campos.append(campo_semantico.capitalize())

        if sub_campo.capitalize() not in campos and sub_campo.strip() != "":
            sub.append(sub_campo.capitalize())



    campos = sorted(campos)
    if opcao_ordem == True:
        
        campospadrao = ""
        numeros_campos = []
        for campo in campos:
            campospadrao += str(campos.index(campo)) + " - " + campo + ", "
            numeros_campos.append(campos.index(campo))
        campospadrao = campospadrao[:-1]

        chave_parametro = "Alterar ordem dos campos"
        valor_parametro = verificar_e_executar(chave_parametro)
        if valor_parametro:
            opcao = valor_parametro
        else:
            opcao = imprimir_menu("Ordem atual dos campos",["Não alterar ordem", "Sim, alterar a ordem"]," A ordem atual dos campos é: " + campospadrao)
            salvar_parametros({chave_parametro: opcao})       
        
        if opcao == "2":
            chave_parametro = "Ordem dos campos"
            valor_parametro = verificar_e_executar(chave_parametro)

            if valor_parametro:
                novaordem = valor_parametro
            else:
                novaordem = menu_simples("Digite uma sequência numérica reordenando os números referentes a cada campo", numeros_campos, "Ordem atual: " + campospadrao + " Digite uma sequência numérica reordenando os números referentes a cada campo. Por exemplo: 5,4,2,3,1,0")
                salvar_parametros({chave_parametro: novaordem})
            camposnovaordem = []
            for i in novaordem.split(","):
                camposnovaordem.append(campos[int(i)])
            campos = camposnovaordem
    for campo in campos:
        campos_semanticos.append(campo.capitalize())
        campos_semanticos_normalizado.append(
                strip_accents(campo.replace(' ', '-').capitalize()))
    sub_campos = []
    for campo_semantico in campos_semanticos:
        subcampos = dataframe[dataframe['CAMPO_SEMANTICO'] == campo_semantico]['SUB_CAMPO_SEMANTICO'].unique()
        if list(subcampos) != [""]:
            subcampos = [subcampo.strip() for subcampo in subcampos]  # Aplica strip() em cada subcampo
            subcampos = list(set(subcampos))
            sub_campos.append([campo_semantico] + subcampos) 
    return campos_semanticos, campos_semanticos_normalizado, sub_campos
def reune_significados(lista):
    lista_agrupada = []
    identificadores = []

    for palavra in lista:
        item_lexical = palavra[1]
        campo = palavra[14]
        subcampo = palavra[15]
        classe = palavra[7]
        if [item_lexical,classe,campo,subcampo] not in identificadores:
            identificadores.append([item_lexical,classe,campo,subcampo])
            lista_agrupada.append([palavra])
        else:
            lista_agrupada[identificadores.index([item_lexical,classe,campo,subcampo])].append(palavra)

        
    for item in lista_agrupada:

        if len(item) == 1:
            item[0][1] = item[0][1].replace("%","")
        else:
            cont = 1
            for palavra in item:
                if "%" in palavra[1]:
                    palavra[1] = palavra[1].replace("%","")
                    palavra[1] = palavra[1] + ("~" + str(cont) + "~")
                    cont += 1
            
            
    lista_final = []
    for item in lista_agrupada:
        if len(item) == 1:
            lista_final.append(item)  
        else:
            if "~" == item[0][1][-1]:
                for palavra in item:
                    lista_final.append([palavra])
            else:
                if len(item) != 1:
                    cont = 1
                    for palavra in item:
                        palavra[8] = str(cont) + "\\. " +palavra[8] 
                        cont += 1
                item.insert(0, ["MULT-SIGN"])
                lista_final.append(item)


    return lista_final

# transforma o dataframe em uma lista e organiza a ordem alfabética
def mapear_caractere(caractere, ordem):
    acentos = [['a','á', 'à', 'â', 'ã', 'ä', 'å', 'æ'], ["c",'ç'],["e",'é', 'è', 'ê', 'ë',"ẽ"],["i",'í', 'ì', 'î', 'ï'],["n",'ñ'],["o",'ó', 'ò', 'ô', 'õ', 'ö', 'ø'],["s",'ś','ş'],["u",'ú', 'ù', 'û', 'ü'],["y",'ý', 'ỳ', 'ŷ', 'ÿ'],["z",'ż']]

    for letra in acentos:
        if caractere in letra:
            caractere = letra[0]
            break
    return ordem.get(caractere, float('inf'))
def dividir_palavra(palavra, alfabeto):
    alfabeto = sorted(alfabeto, key=len, reverse=True)
    grupos = []
    palavra = (strip_accents(palavra.split("|")[0]).replace(".","").replace("’","'").replace("‘","'").replace("%","")).lower()
    for i in palavra:
        if i not in alfabeto:
            resposta = "999"
            while resposta != '1':
                resposta = imprimir_menu("Erro: letra '" + str(i) +"'", ["sair"], "Letra não encontrada no arquivo 'ordem-alfabeto.txt'")
            exit()
    
    while palavra:
        grupo_atual = ""
        for letra in alfabeto:
            if palavra.startswith(grupo_atual + letra):
                grupo_atual += letra
                break
        grupos.append(grupo_atual)
        palavra = palavra[len(grupo_atual):]



    return grupos
def cria_lista_dicionario(dataframe,ordenar_categorias=False,para_validacao=False): 
    '''Retorna uma lista chamada dicionario com todos os itens do csv, cada item lexical 
    passa a ser um item no dicionario como uma lista individual'''
    dicionario = dataframe.values.tolist()
    cont = 0
    for i in dicionario:
        dicionario[cont][0] = "ID-" + str(cont)
        cont += 1
    if para_validacao == False:
        
        try:
            with open("ordem-alfabeto.txt", "r",encoding="UTF-8") as alfabeto:
                alfabeto_string = alfabeto.read()
                alfabeto_separado = [letra.strip() for letra in alfabeto_string.split(",")]
                ordem = {}
                cont_ordem = 0
            for i in alfabeto_separado:
                ordem[i.strip()] = cont_ordem
                cont_ordem += 1
            alfabeto_separado.append(" ")
            #ordem_padrao = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9, 'j': 10,'k': 11, 'l': 12, 'm': 13, 'n': 14, 'o': 15, 'p': 16, 'q': 17, 'r': 18, 's': 19,'t': 20, 'u': 21, 'v': 22, 'w': 23, 'x': 24, 'y': 25, 'z': 26, "'":27}
            dicionario_ordenado_lingua = sorted(dicionario, key=lambda x: [mapear_caractere(c,ordem) for c in dividir_palavra(x[1],alfabeto_separado)])
            locale.setlocale(locale.LC_ALL, '')
            dicionario_ordenado_pt = sorted(dicionario, key = lambda x: locale.strxfrm(strip_accents(x[8].lower().strip()).split("|")[0]))
        except FileNotFoundError:
            locale.setlocale(locale.LC_ALL, '')
            dicionario_ordenado_lingua = sorted(dicionario, key=lambda x: locale.strxfrm(x[1].split("|")[0].replace("%","")))
            dicionario_ordenado_pt = sorted(dicionario, key = lambda x: locale.strxfrm(strip_accents(x[8].lower().strip()).split("|")[0])) 
    else:
        dicionario_ordenado_lingua = dicionario
        locale.setlocale(locale.LC_ALL, '')
        dicionario_ordenado_pt = sorted(dicionario, key = lambda x: locale.strxfrm(strip_accents(x[8].lower().strip()).split("|")[0]))            
    if ordenar_categorias == True:

        chave_parametro = "Manter a ordem alfabética"
        valor_parametro = verificar_e_executar(chave_parametro)
        if valor_parametro:
            opcao = valor_parametro
        else:
            opcao = imprimir_menu("Manter a ordem alfabética automática?",["Sim","Não"])
            salvar_parametros({chave_parametro: opcao}) 

        if opcao == "2":
            
            chave_parametro = "Alterar ordem Alfabética em todo arquivo"
            valor_parametro = verificar_e_executar(chave_parametro)
            if valor_parametro:
                opcao = valor_parametro
            else:
                opcao = imprimir_menu("Ordem Alfabética",["Manter a ordem original de todo o arquivo 'dicionario.csv'","Manter a ordem original em categoria(s) específica(s)"])
                salvar_parametros({chave_parametro: opcao}) 
            if opcao == "1":
                return dicionario_ordenado_pt, dicionario
            if opcao == "2":
                categorias, campos_norm, sub_campos = listar_campos_semanticos(dataframe)

                for i in dicionario:
                    if i[14] not in categorias:
                        categorias.append(i[14]) 
                dicionario_por_categoria= []
                for i in categorias:
                    cat = []
                    for x in dicionario:
                        if x[14] == i:
                            cat.append(x)
                    dicionario_por_categoria.append(cat)

                categorias_string = ""
                for i in categorias:
                    categorias_string += i + ","
                categorias_string = categorias_string[:-1]


                chave_parametro = "Não usar ordem alfabética"
                valor_parametro = verificar_e_executar(chave_parametro)
                if valor_parametro:
                    nao_ordenar = valor_parametro
                else:
                    nao_ordenar = menu_simples("Ordem Alfabética",categorias, "Digite em quais categorias você deseja manter a ordem da tabela (separar por vírgula): " + categorias_string,resposta_obrigatoria=False)
                    salvar_parametros({chave_parametro: nao_ordenar})
                nao_ordenar = nao_ordenar.split(",")



                for categoria in dicionario_por_categoria:
                    if categoria[0][14] not in nao_ordenar:

                        try:
                            with open("ordem-alfabeto.txt", "r",encoding="UTF-8") as alfabeto:
                                alfabeto_separado = alfabeto.read().split(",")
                                ordem = {}
                                cont_ordem = 0
                            for i in alfabeto_separado:
                                ordem[i.strip()] = cont_ordem
                                cont_ordem += 1
                                dicionario_ordenado_lingua = sorted(categoria, key=lambda x: [mapear_caractere(c,ordem) for c in dividir_palavra(x[1],alfabeto_separado)])
                                locale.setlocale(locale.LC_ALL, '')
                                dicionario_ordenado_pt = sorted(dicionario, key = lambda x: locale.strxfrm(strip_accents(x[8].lower()).split("|")[0])) 

                        except FileNotFoundError:
                            locale.setlocale(locale.LC_ALL, '')
                            indice = dicionario_por_categoria.index(categoria)
                            dicionario_por_categoria[indice] = sorted(categoria, key=lambda x: locale.strxfrm(str(str(x[1]).split("|")[0].replace("%",""))))

                dicionario_ordenado_lingua = []
                for item in dicionario_por_categoria:
                    for i in item:
                        dicionario_ordenado_lingua.append(i)
    return dicionario_ordenado_pt, dicionario_ordenado_lingua

#validação de arquivos e de campos obrigatórios
def validacao_tabela_campos(dataframe):
    '''Recebe o dataframe e devolve arquivos 
    de texto contendo os campos vazios 
    da tabela e arquivos ausentes nas pastas'''
    #verificacão dos campos essenciais
    if not os.path.exists(os.getcwd() + '/audio/'): 
        os.makedirs(os.getcwd() + '/audio/')
    if not os.path.exists(os.getcwd() + '/video/'): 
        os.makedirs(os.getcwd() + '/video/')
    if not os.path.exists(os.getcwd() + '/foto/'): 
        os.makedirs(os.getcwd() + '/foto/')
    dicionariopt, dicionario = cria_lista_dicionario(dataframe,para_validacao=True)
    linha = 2
    preencher = []
    cont_erro_barra = 0
    cont_itemlexical = 0
    cont_transcricaofonetica = 0
    cont_classegramatical = 0
    cont_significadopt  = 0
    cont_camposemantico = 0
    for item in dicionario:
        itemlexical = item[1]
        arquivosom = item[4]
        transcricaofonemica = item[5]
        transcricaofonetica = item[6]
        classegramatical = item[7]
        significadopt = item[8]
        camposemantico = item[14]
        arquivosomexemplo = item[10].strip()
        transcricaoexemplo = testa_final(str(item[11]).replace("'", "\\'")).replace("ʼ", "\\'").strip()
        traducaoexemplo = testa_final(item[12]).strip()
        arquivovideo = item[13].strip()
        if itemlexical == "":
            preencher.append([linha, "ITEM_LEXICAL"])
            cont_itemlexical += 1
        if classegramatical == "":
            preencher.append([linha, "CLASSE_GRAMATICAL"])
            cont_classegramatical += 1
        if significadopt == "":
            preencher.append([linha, "TRADUCAO_SIGNIFICADO"])
            cont_significadopt += 1
        if camposemantico == "":
            preencher.append([linha, "CAMPO_SEMANTICO"])
            cont_camposemantico += 1
        numero_transcricao_ex = len(transcricaoexemplo.split("|"))
        numero_traducao_ex = len(traducaoexemplo.split("|"))
        numero_arquivo_ex = len(arquivosomexemplo.split("|"))
        numero_arquivo_video = len(arquivovideo.split("|"))
        if arquivovideo != "":
            numeros_ex = [numero_transcricao_ex, numero_traducao_ex,numero_arquivo_ex,numero_arquivo_video]
        else:
            numeros_ex = [numero_transcricao_ex, numero_traducao_ex,numero_arquivo_ex]
        if len(set(numeros_ex)) != 1:
            preencher.append([linha, "ERRO_USO_BARRAS_EXEMPLO"])
            cont_erro_barra += 1
        if "|" in itemlexical or "|" in transcricaofonemica or "|" in transcricaofonemica or "|" in arquivosom:
            if transcricaofonemica != "":
                numeros_variante = [len(itemlexical.split("|")),len(transcricaofonemica.split("|")),len(transcricaofonetica.split("|")),len(arquivosom.split("|")),]
            else:
                numeros_variante = [len(itemlexical.split("|")),len(transcricaofonetica.split("|")),len(arquivosom.split("|")),]
            if len(set(numeros_variante)) != 1:
                preencher.append([linha, "ERRO_USO_BARRAS_VARIANTES"])
                cont_erro_barra += 1        
        linha += 1  
    pendencias_linha = []
    pendencias = []
    linhas = []
    for pendencia in preencher:
        if pendencia[0]  not in linhas:
            linhas.append(pendencia[0])
    for linha in linhas:
        for pendencia in preencher:
            if pendencia[0] == linha:
                pendencias_linha.append(pendencia[1])
        pendencias.append([linha] + pendencias_linha)
        pendencias_linha = []
    if pendencias != []:
        with open('pendencias-campos.txt', 'a+', encoding="UTF-8") as arquivo:
            arquivo.write("arquivo: dicionario.csv\n") 
            arquivo.write("Itens Lexicais a preencher: " + str(cont_itemlexical) + "\n")
            arquivo.write("Transcrições fonéticas a preencher: " + str(cont_transcricaofonetica) + "\n")
            arquivo.write("Classes gramaticais a preencher: " + str(cont_classegramatical) + "\n")
            arquivo.write("Significados ou traduções a preencher: " + str(cont_significadopt) + "\n")
            arquivo.write("Campos semânticos a preencher: " + str(cont_camposemantico) + "\n") 
            arquivo.write("Erro do preenchimento de barras para multiplos exemplos: " + str(cont_erro_barra) + "\n")  
            arquivo.write("Pendências por linha:\n\n")   
            for pendencia in pendencias:
                linha = pendencia[0]
                texto = "Linha" + str(linha) + ": "
                elemento = 1
                for i in range(len(pendencia)-1):
                    texto = texto + pendencia[elemento] + " | "
                    elemento += 1
                arquivo.write(texto + "\n")
def validacao_tabela_arquivos(dataframe):    
    '''Recebe o dataframe e verifica se os arquivos das pastas audio/video/foto especificados na planilha 
    estão na pasta, ou se arquivos da pasta não estão na lista'''            
    dicionario = dataframe.values.tolist() 
    listaarquivossom = []
    arquivosexemplo = []
    arquivosvideo = []
    arquivosimagem = []
    semimagem = 0
    semsom = 0
    semexemplo = 0
    semvideo = 0
    for item in dicionario:
        arquivosom = item[4]
        arquivoexemplo = item[10]
        arquivovideo = item[13]
        imagem = item[2]
        if arquivosom.strip() != "" and "|" not in arquivosom:
            listaarquivossom.append(arquivosom.strip())
        elif arquivosom.strip() != "" and "|" in arquivosom:
            for i in arquivosom.split("|"):
               listaarquivossom.append(i.strip()) 

        else:
            semsom += 1
        if arquivoexemplo.strip() != "":
            if "|" in arquivoexemplo:
                separado = arquivoexemplo.split("|")
                for i in separado:
                    arquivosexemplo.append(i)
            else:    
                arquivosexemplo.append(arquivoexemplo.strip())
        else:
            semexemplo += 1
        if imagem.strip() != "":
            arquivosimagem.append(imagem.strip())
        else:
            semimagem += 1
        if arquivovideo.strip() != "" and arquivosvideo.strip() != "|":
            arquivosvideo.append(arquivovideo.strip())
        else:
            semvideo += 1
    with open('pendencias-arquivos.txt', 'a+', encoding="UTF-8") as arquivotexto:
        arquivotexto.write("-> Quantidade de arquivos listados na tabela:\n\n")
        arquivotexto.write("Quantidade de entradas: "+ str(len(dicionario))+"\n")
        arquivotexto.write("Arquivos de som: "+ str(len(listaarquivossom))+"\n")
        arquivotexto.write("Arquivos de som de exemplo: "+ str(len(arquivosexemplo))+"\n")
        arquivotexto.write("Arquivos de video: "+ str(len(arquivovideo))+"\n")
        arquivotexto.write("Arquivos de imagem: "+ str(len(arquivosimagem))+"\n\n")
        arquivotexto.write("-> Pendências em arquivos:\n\n")
        arquivotexto.write("Entradas sem imagem: " + str(semimagem) + "\n")
        arquivotexto.write("Entradas sem arquivo de som: " + str(semsom) + "\n")
        arquivotexto.write("Entradas sem arquivo de som de exemplo: " + str(semexemplo) + "\n")
        arquivotexto.write("Entradas sem arquivo de video: " + str(semvideo) + "\n")
        arquivotexto.write("Se houver pendências em relação aos arquivos contidos na tabela ou na pasta, estas estarão abaixo:\n\n")
        

        for roots, dirs, files in os.walk(os.path.join(os.getcwd(), "audio")):    
            arquivosnapasta = files
            if "Desktop.ini" in arquivosnapasta:
                arquivosnapasta.remove("Desktop.ini")
        if listaarquivossom != []:
            for arquivo in listaarquivossom:
                if arquivo not in arquivosnapasta:         
                        arquivotexto.write("Arquivo de som não encontrado: " +  arquivo + "\n")

        if arquivosexemplo != []:
            for arquivo in arquivosexemplo:
                if arquivo not in arquivosnapasta:         
                        arquivotexto.write("Arquivo de som de exemplo não encontrado: " +  arquivo + "\n")
        
        arquivosdeaudio = listaarquivossom + arquivosexemplo
        
        for file in arquivosnapasta:
            if file not in arquivosdeaudio:
                arquivotexto.write("Arquivo na pasta de áudio e ausente na tabela: " +  file + "\n")


        for roots, dirs, files in os.walk(os.path.join(os.getcwd(), "video")):    
            arquivosnapasta = files    
            if "Desktop.ini" in arquivosnapasta:
                arquivosnapasta.remove("Desktop.ini")
        if arquivosvideo != []:
            for arquivo in arquivosvideo:
                if arquivo not in arquivosnapasta:         
                        arquivotexto.write("Arquivo de video não encontrado: " +  arquivo + "\n")

        for file in arquivosnapasta:
            if file not in arquivosvideo:
                arquivotexto.write("Arquivo na pasta de video e ausente na tabela: " +  file + "\n")



        for roots, dirs, files in os.walk(os.path.join(os.getcwd(), "foto")):    
            arquivosnapasta = files  
            if "Desktop.ini" in arquivosnapasta:
                arquivosnapasta.remove("Desktop.ini")
        if arquivosimagem  != []:
            for arquivo in arquivosimagem :
                if arquivo not in arquivosnapasta:         
                        arquivotexto.write("Arquivo de imagem não encontrado: " +  arquivo + "\n")

        for file in arquivosnapasta:
            if file not in arquivosimagem:
                arquivotexto.write("Arquivo na pasta 'fotos' e ausente na tabela: " +  file + "\n")

# preparação dos itens, verificação do fim de strings e retirada de acentos e numeros
def prepara_itens(lista):
    id_entrada = str(lista[0])
    itemlexical = str(lista[1].strip()).replace("'", "\\'").replace("ʼ", "\\'")
    if itemlexical[-1] == ".":
        itemlexical = itemlexical[:-1]
    imagem = lista[2].strip()
    legenda_imagem = lista[3].strip()
    arquivosom = lista[4].strip()
    transcricaofonemica = str(lista[5]).replace("'", "\\'").replace("ʼ", "\\'").strip()
    transcricaofonetica = str(lista[6]).replace("'", "\\'").replace("ʼ", "\\'").strip()
    classegramatical = lista[7].strip()
    significadopt = lista[8].strip()
    if significadopt[-1] == ".":
        significadopt = significadopt[:-1]
    descricao = testa_final(lista[9]).strip()
    if descricao != "" == "." and descricao[-1]:
        descricao = descricao[:-1]
    arquivosomexemplo = lista[10].strip()
    transcricaoexemplo = testa_final(str(lista[11]).replace("'", "\\'")).replace("ʼ", "\\'").strip()
    traducaoexemplo = testa_final(lista[12]).strip()
    arquivovideo = lista[13].strip()
    camposemantico = lista[14].strip()
    sub_campo = lista[15].strip()
    itensrelacionados = testa_final(lista[16]).strip()
    return id_entrada,itemlexical,imagem,legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt, descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo, arquivovideo,camposemantico,sub_campo,itensrelacionados
def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')
def testa_final(string):
    string = string.strip()
    if string == "" or string == " ":
        return ""
    elif string[-1] == ".":     
        return string
    else:
        string += "."
        return string
def remover_numeros_inicio_string(texto): #remover a marcação da frente dos significados
    padrao = r'^\d+\\\.\s'
    resultado = re.sub(padrao, '', texto)
    return resultado

# cria a introdução a partir do arquivo "intro.txt"
def cria_intro():
    try:
        with open("intro.txt", "r",encoding="UTF-8") as introducao:
            introducao_string = introducao.read()
            return introducao_string
    except FileNotFoundError:
        introducao_string = "SUA INTRODUÇÃO VAI AQUI"         
        return introducao_string

# Cria LEgendas para arquivos de audio
def cria_legenda(filename):
    filename = str(filename)
    arquivoatores = os.path.join(os.getcwd(), "atores.csv")
    atoresrecuperado = []
    cont = 5
    while atoresrecuperado == [] and cont != 0:
        siglas = r'[-_][A-Za-z][A-Za-z][A-Za-z]*' * cont
        atoresrecuperado = re.findall(r'\d\d\d\d\d\d\d\d' + siglas,filename)
        cont -= 1
    if atoresrecuperado != []:
        atoresrecuperado = re.sub(r'\d\d\d\d\d\d\d\d',"",atoresrecuperado[0])
        atoresrecuperado = re.sub(r'[_-]'," ",atoresrecuperado)
        atoresrecuperado = atoresrecuperado.strip()
        atoresrecuperado = atoresrecuperado.split(" ")
    data = re.findall(r'\d\d\d\d',filename)
    if data == [] or data < 1860:
        data = ["data não encontrada"]
    if atoresrecuperado == []:
        legenda = '<font size="1">'+ "(Falante não informado, " + data[0]+ ")" + '</font><br />'
        return str(legenda)
    try:
        dfatores = pd.read_csv(arquivoatores)
        dfatores = dfatores.fillna('')
        listaatores = dfatores.values.tolist()
    except (FileNotFoundError, IOError):
        legenda = '<font size="1">'+ "(Falante não informado, " + data[0]+ ")" +'</font><br />'
        return str(legenda)
    texto = ""
    for ator in atoresrecuperado:
        for dadosator in listaatores:
            if ator == dadosator[0]:
                texto = texto + dadosator[1] + ", "
    if texto == "":
        return '<font size="1">'+ "(Falante não informado, " + data[0]+ ")" + '</font><br />'
    return str('<font size="1">'+ "("+ texto + data[0] + ")" +'</font><br />')

# escreve as entradas para o html unico e para o html comum
def escreve_entrada_html(id_entrada,itemlexical,imagem, legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt,descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo,arquivovideo,camposemantico,sub_campo,itensrelacionados, novas_colunas, arquivo,item,entrada_lingua_secundaria=False,opcao_legenda=False,caminho_relativo=False, somente_significado=False):
    if caminho_relativo == False:
        caminho = ""
    else:
        caminho = "../"
    if somente_significado == False:           
            if entrada_lingua_secundaria == False:
                arquivo.write("\n\n\n\n## " +'<span style="display: none;">' + itemlexical.split("|")[0] + "</span>" + "\n<hr>" +"\n")
                arquivo.write('<h2>')
                for i in itemlexical.split("|"):
                    arquivo.write(i)
                    if i != itemlexical.split("|")[-1] and i != "" and i != itemlexical[0] and len(itemlexical.split("|")) > 1:
                        arquivo.write(" ~ ")
                arquivo.write('<span id="entradalex"> ')   
            if transcricaofonemica != "" and transcricaofonetica == "":
                for i in transcricaofonemica.split("|"):
                    arquivo.write("/"+i+ "/")
                    if len(transcricaofonemica.split("|")) > 1:
                        if i != transcricaofonemica.split("|")[-1] and i != "":
                            arquivo.write(" ~ ")
                if classegramatical != "":
                    arquivo.write(" *")
            elif transcricaofonemica == "" and transcricaofonetica != "":
                for i in transcricaofonetica.split("|"):                
                    arquivo.write(" ["+i + "]")
                    if len(transcricaofonetica.split("|")) > 1:
                        if i != transcricaofonetica.split("|")[-1] and i != "": 
                            arquivo.write(" ~ ")
                if classegramatical != "":
                    arquivo.write(" *")
            elif transcricaofonemica == "" and transcricaofonetica == "":
                if classegramatical != "":
                    arquivo.write(" *")
            else:
                for i in transcricaofonemica.split("|"):
                    arquivo.write("/"+i+ "/")
                    if len(transcricaofonemica.split("|")) > 1:
                        if i != transcricaofonemica.split("|")[-1] and i != "": 
                            arquivo.write("~")
                arquivo.write(" ")
                for i in transcricaofonetica.split("|"):                
                    arquivo.write("["+i + "]")
                    if len(transcricaofonetica.split("|")) > 1:
                        if i != transcricaofonetica.split("|")[-1] and i != "":  
                            arquivo.write(" ~ ")
                if classegramatical != "":
                    arquivo.write(" *") 
            if classegramatical != "":
                arquivo.write(classegramatical + "* </span></h2> \n")
            else:
                arquivo.write(" </span>")
                arquivo.write('</h2>\n')                
            if arquivosom != "":
                if len(arquivosom.split("|")) > 1:
                    arquivo.write('<div class="variantes">')
                for i in arquivosom.split("|"):    
                    for filename in os.listdir(os.getcwd() + "/audio"):
                        if filename == i:
                            if len(arquivosom.split("|")) > 1:
                                indice = arquivosom.split("|").index(i)
                                arquivo.write('<div class="div-variante">')
                                arquivo.write(itemlexical.split("|")[indice]+"\n\n")
                            arquivo.write('\n<audio width="320" height="240" preload="none" controls>\n  <source src="' + caminho + "audio/" + filename +'" type="audio/wav">\n</audio>')
                            if opcao_legenda == True:
                                arquivo.write("\n" + cria_legenda(arquivosom))
                            if len(arquivosom.split("|")) > 1:
                                arquivo.write('</div>')
                            break
                if len(arquivosom.split("|")) > 1:
                    arquivo.write('</div>')
    if significadopt != "":
        arquivo.write('<p></p>' +significadopt )
    if descricao != "":
        arquivo.write(". " + descricao + "\n")
    if imagem != "":
        for filename in os.listdir(os.getcwd() + "/foto"):
            if filename == imagem:
                arquivo.write('\n\n\n\n<div id="image-container">\n![](' + caminho +"foto/" + filename + "){loading='lazy'}\n</div>\n\n")
                if legenda_imagem != "":
                    arquivo.write('<span class="legenda-imagem">' + legenda_imagem + "<span>")
                break

    if transcricaoexemplo != "":
        transcricaoexemplo = transcricaoexemplo.split("|")
        traducaoexemplo = traducaoexemplo.split("|")
        arquivosomexemplo = arquivosomexemplo.split("|")
        arquivovideo = arquivovideo.split("|")

        if len(transcricaoexemplo)  > 1:
            for i in range(len(transcricaoexemplo)):
                if transcricaoexemplo != ['']:
                    if transcricaoexemplo[i] != "":
                        arquivo.write("\n<br>*" + testa_final(transcricaoexemplo[i]).strip() + "*\n")
                if traducaoexemplo != ['']:
                    if traducaoexemplo[i] != "":
                        arquivo.write("\n" + testa_final(traducaoexemplo[i]).strip() + "\n")
                if arquivovideo != ['']:
                    if arquivovideo[i] != "":
                        for filename in os.listdir(os.getcwd() + "/video"):
                            if filename == arquivovideo[i].strip():
                                arquivo.write('\n<video width="320" height="240" controls preload="none">\n  <source src="' + caminho + "video/" + arquivovideo[1] + '" type="video/mp4"></video><br>')
                                if opcao_legenda == True:
                                    arquivo.write("\n" + cria_legenda(arquivovideo))                                        
                                break                        
                if arquivosomexemplo != ['']:
                    if arquivosomexemplo[i] != "":
                        for filename in os.listdir(os.getcwd() + "/audio"):
                            if filename == arquivosomexemplo[i].strip():
                                arquivo.write('\n<audio width="320" height="240" controls preload="none">\n  <source src="'+ caminho + "audio/" +arquivosomexemplo[i]+'" type="audio/wav">\n</audio>')
                                if opcao_legenda == True:
                                    arquivo.write("\n" + cria_legenda(arquivosomexemplo)) 
                                break
        elif len(transcricaoexemplo)  == 1:
            for i in range(len(transcricaoexemplo)):
                if transcricaoexemplo != ['']:    
                    if transcricaoexemplo[i] != "":
                        arquivo.write("\n<br>*" + testa_final(transcricaoexemplo[i]).strip() + "*\n")
                if traducaoexemplo != ['']:
                    if traducaoexemplo[i] != "":
                        arquivo.write("\n" + testa_final(traducaoexemplo[i]).strip() + "\n")
                if arquivovideo != ['']:
                    if arquivovideo[i] != "":
                        for filename in os.listdir(os.getcwd() + "/video"):
                            if filename == arquivovideo[i].strip("|"):
                                arquivo.write('\n<video width="320" height="240" controls preload="none">\n  <source src="' + caminho + "video/" + arquivovideo[1] + '" type="video/mp4"></video><br>')
                                if opcao_legenda == True:
                                    arquivo.write("\n" + cria_legenda(arquivovideo))                                         
                                break                       
                if arquivosomexemplo != ['']:
                    if arquivosomexemplo[i] != "":
                        for filename in os.listdir(os.getcwd() + "/audio"):
                            if filename == arquivosomexemplo[i].strip():
                                arquivo.write('\n<audio width="320" height="240" controls preload="none">\n  <source src="' + caminho + "audio/" +arquivosomexemplo[i]+'" type="audio/wav">\n</audio>')
                                if opcao_legenda == True:
                                    arquivo.write("\n" + cria_legenda(arquivosomexemplo))     
                                break


                if itensrelacionados != "":
                    arquivo.write("\n" + "Itens relacionados: "+ itensrelacionados)
    cont = 17
    if len(item) == 1:
        item = item[0]
    for nova_coluna in novas_colunas:
        if item[cont] != "":
            arquivo.write(testa_final(str(item[cont])))
        cont += 1

#arquivos para html unico
def cria_html_unico(dataframe,opcao_legenda=False,opcao_simples=True,entrada_lingua_secundaria=False):
    '''recebe um dataframe e cria os arquivos necessarios para produzir um html unico com midias embutidas'''    
    titulo_documento, autor = titulo_autor()
    if opcao_simples == True:
        lista_portugues, lista_lingua = cria_lista_dicionario(dataframe)
        campos_semanticos, campos_semanticos_normalizado, sub_campos = listar_campos_semanticos(dataframe)
    else:
        lista_portugues, lista_lingua = cria_lista_dicionario(dataframe,True)
        campos_semanticos, campos_semanticos_normalizado, sub_campos = listar_campos_semanticos(dataframe,True)
    novas_colunas = listar_novas_colunas(dataframe)
    if not os.path.exists(os.getcwd() + '/html_unico/'): 
         os.makedirs(os.getcwd() + '/html_unico/')
    #Escrever arquivo com entrada lingua
    id = 0
    arquivo = open(os.getcwd() + "/html_unico/dicionario.Rmd", mode="w+", encoding="utf-8")
    arquivo.write("---\n")
    arquivo.write('title: "' + titulo_documento +'"\n')
    arquivo.write('author: "' + autor + '"\n')
    arquivo.write('''date: "`r Sys.Date()`"
output:
  html_document:
    section_divs: yes
    self_contained: true
    theme: readable
    highlight: tango
    css: "styles.css"
    includes:
       before_body: before-body.html
       in_header: in-header.html

---
</div>
<p>
<a id="btn-voltar" onclick="toggleMenu()">☰</a>
</p>
<div id="menu" class="menu">
<a href="#ini" onclick="fecharMenu()">Início</a>
''')
    for campo in campos_semanticos:
        arquivo.write('<a href="#' + campo.replace(" ", "") + '" onclick="fecharMenu()">' + campo + '</a>\n')
    arquivo.write('''<a href="#lista-significados" onclick="fecharMenu()">Significados A-Z</a>
</div>
<a name="ini"></a>

''')
    barra = ""
    for campo in campos_semanticos:
        item = '<a class="btn-barra" href="#' + campo.replace(" ", "") + '">'+ campo +'</a>'
        barra += item + " "
    barra += '<a class="btn-barra" href="#lista-significados">Significados A-Z</a>'
    arquivo.write('''<div id="categorias" class="section level1">
<h1>Categorias</h1>
<div id="barra" class="section level1">
<h2>''' + barra + '''</h2>
</div>
</div>
''')
    arquivo.write('''<div id = "corpotexto">\n
<div id="intro">
<p><button onmouseout="this.style.opacity = '0.5'" onmouseover="this.style.opacity = '1'" style="border-radius: 4px;transition: opacity 0.2s;padding: 8px 16px;border-radius: 4px;position:static;border:solid 1px;font-size: 15px;opacity : 0.5;" id='btn-div' onclick="esconde_intro()">Ocultar Introdução</button>
<div class="texto-introducao">
# Introdução
''')
    introducao = cria_intro()
    arquivo.write(introducao) 
    arquivo.write('''
</div>
</div>

''')
    lista_lingua = reune_significados(lista_lingua)
    for i in campos_semanticos_normalizado: 
        arquivo.write("<br/>")
        arquivo.write('\n\n<div class="div-link">\n')
        arquivo.write('<p><a class="link-entrada" name="' + campos_semanticos[id].replace(" ", "") + '"></a></p>')
        arquivo.write('</div>\n')
        arquivo.write("\n\n# " + campos_semanticos[id] + "\n\n")
        arquivo.write('<p><a href="#ini">Voltar para o começo</a></p>')
        
        subcampos = []
        for sub_campo in sub_campos:
            if sub_campo[0] == campos_semanticos[id]:
                subcampos = sub_campo[1:]
                break
        subcampos = sorted(subcampos)
        outros= []
        for sub in subcampos:
            if sub.startswith("Outros") or sub.startswith("Outras"):
                outros.append(sub)
        for outro in outros:
            subcampos.remove(outro)
        
        subcampos = subcampos + outros
        if subcampos == []:
            subcampos = [""]
        for subcampo in subcampos:
            if subcampo != "":
                arquivo.write('''
  <div class="level2">
  <hr>
  <span id="sub-c" class="level2"> '''+ subcampo.capitalize() +''' </span>
  </div>
  ''')
            for item in lista_lingua:
                if item[0] != ['MULT-SIGN']:               
                    id_entrada,itemlexical,imagem,legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt,descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo,arquivovideo,camposemantico,sub_campo,itensrelacionados = prepara_itens(item[0])
                    if camposemantico.capitalize() == campos_semanticos[id] and subcampo.capitalize() == sub_campo.capitalize():
                        arquivo.write('<div class="div-link">\n')
                        arquivo.write('<a class="link-entrada" name="' + id_entrada +'"></a>\n')
                        arquivo.write('</div>\n')
                        escreve_entrada_html(id_entrada,itemlexical,imagem,legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt,descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo,arquivovideo,camposemantico,sub_campo,itensrelacionados, novas_colunas, arquivo,item,entrada_lingua_secundaria,opcao_legenda,caminho_relativo=True)
                else:
                    for i in item[1:]:
                        arquivo.write('<div class="div-link" style="position: relative;">\n<a class="link-entrada" name="' + i[0] +'"></a>\n</div>\n')
                    id_entrada,itemlexical,imagem,legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt,descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo,arquivovideo,camposemantico,sub_campo,itensrelacionados = prepara_itens(item[1])   
                    if camposemantico.capitalize() == campos_semanticos[id] and subcampo.capitalize() == sub_campo.capitalize():
                        escreve_entrada_html(id_entrada,itemlexical,imagem,legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt,descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo,arquivovideo,camposemantico,sub_campo,itensrelacionados, novas_colunas, arquivo,item[1],entrada_lingua_secundaria,opcao_legenda,caminho_relativo=True)       
                        for significado in item[2:]:
                            id_entrada,itemlexical,imagem,legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt,descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo,arquivovideo,camposemantico,sub_campo,itensrelacionados = prepara_itens(significado)   
                            if camposemantico.capitalize() == campos_semanticos[id] and subcampo.capitalize() == sub_campo.capitalize():
                                escreve_entrada_html(id_entrada,itemlexical,imagem,legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt,descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo,arquivovideo,camposemantico,sub_campo,itensrelacionados, novas_colunas, arquivo,significado,entrada_lingua_secundaria,opcao_legenda,caminho_relativo=True,somente_significado=True) 

        id += 1
    arquivo.write('''\n</div>\n\n\n\n<hr>
''')
    arquivo.write('<div class="div-link">\n')
    arquivo.write('<a class="link-entrada" name="lista-significados"></a>\n')
    arquivo.write('</div>\n')

    arquivo.write("# Entradas ordenadas por significado\n\n\n\n")
    arquivo.write("<hr>")
    arquivo.write('<div id="div-significados">')
    for i in lista_portugues:
        arquivo.write('<p><a class="significado-az" href="#'+ str(i[0]) +'"><h5>'+ i[8] + " (" + i[1] +')</h5></a></p>\n')
    arquivo.write('</div>')

    arquivo.close()
    cria_header_htmlunico()
    cria_css_html_unico()
    cria_cabecalho()
    copiar_arquivo_para_subpasta("GERAR-PRODUTOS.exe", "html_unico")
def cria_cabecalho():
    arquivo = open(os.getcwd() + "/html_unico/" + "in-header.html", mode="w+", encoding="utf-8")
    arquivo.write(r'''<header id="header" class="header-glossario">
  <nav class="menu-topo-glossario">
    <!-- MENU MOBILE -->
    <div class="menu-mobile">
      <a class="logo-mobile" aria-label="logo MPEG">
        <img class="logo-mpeg-mob" src="data:image/jpeg;base64,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" alt="MUSEU GOELDI" />
      </a>
    </div>
    <!-- FIM MENU MOBILE -->

    <!-- MENU DESKTOP -->
    <div class="glossario-menu">
      <a class="logo-glossario">
        <img class="logo-mpeg" src="data:image/jpeg;base64,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" alt="MUSEU GOELDI" />
      </a>
      <div class="menu-middle">

      </div>
      <div class="pesquisar-box">
        <div id="barrabusca">
          <input type="text" id="searchbar" onkeyup="valida_busca()"/>
          <button class="botoes-busca" id="searchbtn" onclick="busca_entrada('Buscando...',true)" disabled>Buscar</button>
      </div>
      </div>
    </div>
    <div class="search-mobile">
      <div class="search-icon"></div>
    </div>
    <!-- FIM MENU DESKTOP -->
  </nav>
</header>
''')
    arquivo.close()
def cria_header_htmlunico():
    arquivo = open(os.getcwd() + "/html_unico/" + "before-body.html", mode="w+", encoding="utf-8")
    arquivo.write(r'''
                  
<script>

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
let input = document.getElementById('searchbar').value.toLowerCase();
let x = document.getElementsByClassName('section level1');
let x2 = document.getElementsByClassName('section level2');
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
window.onscroll = function() {
var posicaoAtual = window.pageYOffset;
if (posicaoInicial > posicaoAtual) {
    document.getElementById("header").style.top = "";
    document.getElementById("btn-voltar").style.opacity = "1";
    document.getElementById("btn-voltar").style.visibility = "visible";
} else {
    document.getElementById("header").style.top = "-74px";
    document.getElementById("btn-voltar").style.opacity = "0";
    document.getElementById("btn-voltar").style.visibility = "hidden";
}
posicaoInicial = posicaoAtual;
};

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

<div id="cabecalho">
''')
    arquivo.close()
def cria_css_html_unico():
    arquivo = open(os.getcwd() + "/html_unico/" + "styles.css", mode="w+", encoding="utf-8")
    arquivo.write('''

/* CONFIG TOPO DA PÁGINA */

.significado-az {
color: black;
cursor: pointer;
}
                  
.div-link p {
position: relative;
}
.link-entrada {
    position: absolute;
    top: -60px;}                  

header.header-glossario {
position: fixed;
}
header.header-glossario {
transition: top 0.3s ease-in-out;
}
.header-glossario {
height: 60px; /* Altura reduzida para dispositivos móveis */
position: fixed;
z-index: 5;
top: 0;
background-color: #fff;
width: 100%;
display: flex;
align-items: center;
padding: 0;
border-bottom: 1px solid #dadada;
box-sizing: border-box;
}
.menu-topo-glossario {
width: 100%;
}
.menu-glossario {
display: flex;
align-items: center;
justify-content: space-between;
}
.menu-mobile {
display: flex;
align-items: center;
}
.glossario-menu {
display: flex;
align-items: center;
}


.logo-mpeg {
    width: 80px;
}
.pesquisar-box {
display: flex;
flex: 0 0 auto;
align-items: center;
justify-content: flex-end;
}



#barrabusca {
  display: flex;
  justify-content: flex-start;
  align-items: center; /* Adicionado para alinhar verticalmente os elementos */
}

#searchbar {
  padding: 4px 16px;
  border-radius: 10px;
  font-size: 14px;
}

.botoes-busca {
display: inline-block;
padding: 4px;
margin: 8px;
font-size: 16px;
text-align: center;
background-color: #f2f2f2;
color: #444;
border: none;
border-radius: 5px;
cursor: pointer;
transition: background-color 0.3s ease;
}

.botoes-busca:hover {
  background-color: #ddd;
}
.logo-glossario {
flex: 0 0 auto;
padding-right: 20px;
display: flex;
align-items: center;
margin-left: 1px;
}
.menu-middle {
flex-grow: 1;
text-align: center;
}

.titulo {
margin: 0;
}

#cabecalho #header {width: 100%;}

.logo-mpeg {
width: 80px;
}
.logo-mobile {
display: none;
}
a.logo-mobile img {
width: 100px;
}
/* FIM CONFIG TOPO DA PÁGINA */
.variantes{
display: flex;
flex-direction: row;
flex-wrap: wrap;
margin: 5px;
}

audio {z-index: -1;}

#btn-voltar {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 4;
  background-color: #f2f2f2;
  color: black;
  text-decoration: none;
  padding: 1em;
  border-radius: 3em;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s, visibility 0.3s;
  z-index: 2;
}

#menu {
  display: none;
  background-color:  #f2f2f2;
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
  z-index: 3;
}

#menu.menu-ativo {
  display: flex;
  flex-direction: column;
  opacity: 1;
  transform: translateY(0);
}

#menu.menu-ativo + #btn-voltar {
  opacity: 0;
  visibility: hidden;
}

#menu a {
  display: inline-block;
  margin-right: 10px;
  color: black;
  text-decoration: none;
}

#menu p{
display: flex;
flex-direction: column;}
#barra h2 {
text-align: center;
}

.btn-barra {
display: inline-block;
padding: 10px;
margin: 1px;
font-size: 16px;
text-align: center;
background-color: #f2f2f2;
color: #444;
border: none;
border-radius: 5px;
cursor: pointer;
transition: background-color 0.3s ease;
}
.btn-barra:hover {
background-color: #ddd;
}
#espaco-intro{
height: 500px;
width: 500px;
line-height:10%;
} 
#sub-c{
text-align:center;
margin:auto;
display:table;
font-size: 33px;
font-weight:bold;
font-family: "Raleway","Helvetica Neue",Helvetica,Arial,sans-serif;}   
#entradalex{font-weight: normal; font-size: 16px;}

#categorias {
background-color: white;
position: relative;

}

div h1{background-color: #e0e0e0;text-align: center;}
#cabecalho {
align-items: center;
margin-top: 100px; 
}
.date, .author {
text-align: center;               
}



#barrabusca {
display: flex;
justify-content: flex-end;
}
#introdução {
text-align: justify;
}
img {
border: 1px solid black;
}

.menu a {
display: block;
color: black;
padding: 9px;
text-decoration: none;
}
.menu a.active {
background-color: #1b1c1c;
color: white;
padding-top: 20px;
}
.menu a:hover:not(.active) {
background-color: #555;
color: white;
}

div.content {
margin-left: 60px;
z-index: -10;
}

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
font-size: 10px;
}

.botoes-busca {
padding: 4px 8px;
border-radius: 8px;
font-size: 14px;
background-color: #e0e0e0;
margin-left: 2px;
}

.logo-mobile {
margin-right: 70px;
}



}

''')
    arquivo.close()

#arquivos para o html
def cria_html(dataframe,opcao_legenda=False,opcao_simples=True,entrada_lingua_secundaria=False):
    '''recebe um dataframe e cria os arquivos necessarios para produzir o html'''    
    titulo_documento, autor = titulo_autor()
    if opcao_simples == True:
        lista_portugues, lista_lingua = cria_lista_dicionario(dataframe)
        campos_semanticos, campos_semanticos_normalizado, sub_campos = listar_campos_semanticos(dataframe)
    else:
        lista_portugues, lista_lingua = cria_lista_dicionario(dataframe,True)
        campos_semanticos, campos_semanticos_normalizado, sub_campos = listar_campos_semanticos(dataframe,True)
    novas_colunas = listar_novas_colunas(dataframe)
    if not os.path.exists(os.getcwd() + '/html/'): 
         os.makedirs(os.getcwd() + '/html/')
    #Escrever arquivo com entrada lingua
    id = 0
    lista_lingua = reune_significados(lista_lingua)
    for i in campos_semanticos_normalizado:  # cria os arquivos RMD com o titulo
        arquivo = open(os.getcwd() + "/html/"+ i + ".Rmd", mode="w+", encoding="utf-8")
        arquivo.write("---\n")
        arquivo.write('title: "' + titulo_documento +'"\n')
        arquivo.write('author: "' + autor + '"\n')
        arquivo.write("---\n\n")
        arquivo.write('''<div id="barrabusca">
<input type="text" id="searchbar" onkeyup="valida_busca()"/>
<button class="botoes-busca" id="searchbtn" onclick="busca_entrada('Buscando...',true)">Buscar</button>
</div>

<style type="text/css">

mark {
padding: 0;
}

#barrabusca {
display: flex;
justify-content: flex-end;
flex-wrap: wrap;
}

#searchbar {
border: 1px solid #ccc;
font-size: 16px;
padding:03px;
border-radius: 10px;
width: 40%; z-index: 999;
margin-top: 30px;
}

.botoes-busca {
font-size: 16px;
background-color: #f2f2f2;
color: #444;
border: none;
border-radius: 5px;
}

#barra h2 {
display: flex;
flex-wrap: wrap;
}

#sub-c{
text-align:center;
margin:auto;
display:table;
font-size: 33px;
font-weight:bold;
font-family: "Raleway","Helvetica Neue",Helvetica,Arial,sans-serif;
}    
#entradalex{font-weight: normal; font-size: 16px;white-space: nowrap;}
li #entradalex{display: none;}
#cabecalho{
display: flex;
flex-flow: column wrap;
}


#introdução {
text-align: justify;
}
img {
border: 1px solid black;
}


div.content {
margin-left: 60px;
z-index: -10;
}
@media only screen and (max-width: 700px){



#corpotexto {
margin-left: 60px;
position: static;
z-index: 1;
}


}
@media only screen and (max-width: 850px){


#corpotexto {
margin-left: 60px;
position: static;
z-index: 1;
}

}

</style>
<script>
    
  function escapeRegExp(string) {
    return string.replace(/[.*+\-?^${}()|[\]\\\\]/g, '\\\\$&');
  }
  
  
  
  function destacar_palavras(entrada, palavras) {
    let innerHTML = entrada;
    palavras.forEach((palavra) => {
      let palavraEscapada = escapeRegExp(palavra);
      let regEx = new RegExp(`(${palavraEscapada}|${palavraEscapada.replace(/[\[\]()]/g, '\\\\$&').replace(/\s+/g, '|')})`, 'gi');
      innerHTML = innerHTML.replace(regEx, match => {
        let primeiraLetra = match[0];
        let casoOriginal = primeiraLetra.toUpperCase() === primeiraLetra ? palavra.charAt(0).toUpperCase() + palavra.slice(1) : palavra;
        return `<mark style="background-color: yellow; padding: 0;">${casoOriginal}</mark>`;
      });
    });
    return innerHTML;
  }
  
  
  function busca_entrada(buscaText, destacar) {
let input = document.getElementById('searchbar').value.toLowerCase();
let x = document.getElementsByClassName('level1');
let x2 = document.getElementsByClassName('level2');
let searchbar = document.getElementById("searchbar");
let searchbtn = document.getElementById("searchbtn");
let clearbtn = document.getElementById("clearbtn");

let oldInput = input;
searchbar.value = buscaText;

setTimeout(() => {
  let hasResults = false;
  for (let i = 0; i < x.length; i++) {
    if (!x[i].innerText.toLowerCase().includes(input)) {
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
    if (!x2[i].innerText.toLowerCase().includes(input)) {
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
  
  </script>\n''')
        subcampos = []
        for sub_campo in sub_campos:
            if sub_campo[0] == campos_semanticos[id]:
                subcampos = sub_campo[1:]
                break
        subcampos = sorted(subcampos)
        outros= []
        for sub in subcampos:
            if sub.startswith("Outros") or sub.startswith("Outras"):
                outros.append(sub)
        for outro in outros:
            subcampos.remove(outro)
        
        subcampos = subcampos + outros
        if subcampos == []:
            subcampos = [""]
        for subcampo in subcampos:

            if subcampo != "":
                arquivo.write('''
  <div class="level2">
  <hr>
  <span id="sub-c" class="level2"> '''+ subcampo.capitalize() +''' </span>
  </div>
  ''')
            for item in lista_lingua:
                if item[0] != ['MULT-SIGN']:
                    
                    id_entrada,itemlexical,imagem,legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt,descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo,arquivovideo,camposemantico,sub_campo,itensrelacionados = prepara_itens(item[0])
                    if camposemantico.capitalize() == campos_semanticos[id] and subcampo.capitalize() == sub_campo.capitalize():
                        escreve_entrada_html(id_entrada,itemlexical,imagem,legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt,descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo,arquivovideo,camposemantico,sub_campo,itensrelacionados, novas_colunas, arquivo,item,entrada_lingua_secundaria,opcao_legenda,caminho_relativo=False)
                else:
                    id_entrada,itemlexical,imagem,legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt,descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo,arquivovideo,camposemantico,sub_campo,itensrelacionados = prepara_itens(item[1])   
                    if camposemantico.capitalize() == campos_semanticos[id] and subcampo.capitalize() == sub_campo.capitalize():
                        escreve_entrada_html(id_entrada,itemlexical,imagem,legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt,descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo,arquivovideo,camposemantico,sub_campo,itensrelacionados, novas_colunas, arquivo,item[1],entrada_lingua_secundaria,opcao_legenda,caminho_relativo=False)       
                        
                        for significado in item[2:]:

                            id_entrada,itemlexical,imagem,legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt,descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo,arquivovideo,camposemantico,sub_campo,itensrelacionados = prepara_itens(significado)   
                            if camposemantico.capitalize() == campos_semanticos[id] and subcampo.capitalize() == sub_campo.capitalize():
                                escreve_entrada_html(id_entrada,itemlexical,imagem,legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt,descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo,arquivovideo,camposemantico,sub_campo,itensrelacionados, novas_colunas, arquivo,significado,entrada_lingua_secundaria,opcao_legenda,caminho_relativo=False,somente_significado=True) 
        id += 1
        arquivo.close()
    cria_index()
    cria_site_yml(dataframe, titulo_documento)
    cria_proj_site()
    cria_output_yml()
    copiar_arquivo_para_subpasta("GERAR-PRODUTOS.exe", "html")
def cria_index():
    arquivo = open(os.getcwd() + "/html/" + "index.Rmd", mode="w+", encoding="utf-8")
    arquivo.write('''---
title: "Introdução"
output: html_document
---
<style type = "text/css">
.col-xs-12 {
    width: 100%;
}
#TOC {display: none;}
</style>
        
        ''')
    introducao = cria_intro()
    arquivo.write(introducao)
    arquivo.close
def cria_site_yml(dataframe, lingua):
    arquivo = open(os.getcwd() + "/html/" + "_site.yml", mode="w+", encoding="utf-8")
    arquivo.write('''    
name: my-website
output_dir: _site
navbar:\n''')
    arquivo.write('  title: "Dicionário ' + lingua + '"\n')  
    arquivo.write('''  left:
    - text: "Introdução"
      href: index.html\n''')
    campos, campos_norm, sub_campos = listar_campos_semanticos(dataframe)
    campos = sorted(campos)
    campos_norm = sorted(campos_norm)
    id = 0
    for campo in campos:
        arquivo.write('    - text: "'+ campo + '"\n')
        arquivo.write('      href: ' + campos_norm[id] + ".html\n")
        id += 1
    arquivo.close
def cria_output_yml():
    arquivo = open(os.getcwd() + "/html/" + "_output.yml", mode="w+", encoding="utf-8")
    arquivo.write('''html_document:
    theme: simplex
    highlight: tango
    toc: true
    toc_float: true''')
    arquivo.close
def cria_proj_site():
    arquivo = open(os.getcwd() + "/html/" + "site.Rproj", mode="w+", encoding="utf-8")
    arquivo.write('''Version: 1.0

RestoreWorkspace: Default
SaveWorkspace: Default
AlwaysSaveHistory: Default

EnableCodeIndexing: Yes
UseSpacesForTab: Yes
NumSpacesForTab: 2
Encoding: UTF-8

RnwWeave: Sweave
LaTeX: pdfLaTeX

BuildType: Website''')
    arquivo.close

#arquivos para o pdf
def cria_pdf(dataframe,opcao_simples=True): 
    titulo_documento, autor = titulo_autor() 
    if opcao_simples == True:
        lista_portugues, lista_lingua = cria_lista_dicionario(dataframe)
        campos_semanticos, campos_semanticos_normalizado, sub_campos = listar_campos_semanticos(dataframe)
    else:
        lista_portugues, lista_lingua = cria_lista_dicionario(dataframe,True)
        campos_semanticos, campos_semanticos_normalizado, sub_campos = listar_campos_semanticos(dataframe,True)

    novas_colunas = listar_novas_colunas(dataframe)
    if not os.path.exists(os.getcwd() + '/pdf/'): 
         os.makedirs(os.getcwd() + '/pdf/')

    #Escrever arquivo com entrada lingua
    id = 0
    contador = 0
    arquivo = open(os.getcwd() + "/pdf/" +  strip_accents("00_dicionario".replace(" ","_")) +  ".Rmd", mode="a+", encoding="utf-8")    
    lista_lingua = reune_significados(lista_lingua)
    for i in campos_semanticos_normalizado: #cria os rmds com entrada em portugues
        arquivo.write("\n\n# " + campos_semanticos[id])

        subcampos = []
        for sub_campo in sub_campos:
            if sub_campo[0] == campos_semanticos[id]:
                subcampos = sub_campo[1:]
                break
        subcampos = sorted(subcampos)
        outros= []
        for sub in subcampos:
            if sub.startswith("Outros") or sub.startswith("Outras"):
                outros.append(sub)
        for outro in outros:
            subcampos.remove(outro)
        
        subcampos = subcampos + outros
        if subcampos == []:
            subcampos = [""]
        for subcampo in subcampos:

            if subcampo != "":
                arquivo.write('\n\n## '+ subcampo.capitalize() + "\n")

            for item in lista_lingua:
                if item[0] != ['MULT-SIGN']:
                    
                    id_entrada,itemlexical,imagem,legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt,descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo,arquivovideo,camposemantico,sub_campo,itensrelacionados = prepara_itens(item[0])
                    if camposemantico.capitalize() == campos_semanticos[id] and subcampo.capitalize() == sub_campo.capitalize():
                        escreve_entrada_pdf(id_entrada,itemlexical,imagem,legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt,descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo,arquivovideo,camposemantico,sub_campo,itensrelacionados, novas_colunas, arquivo,item,contador) 
                        contador += 1
                else:
                    id_entrada,itemlexical,imagem,legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt,descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo,arquivovideo,camposemantico,sub_campo,itensrelacionados = prepara_itens(item[1])   
                    if camposemantico.capitalize() == campos_semanticos[id] and subcampo.capitalize() == sub_campo.capitalize():
                        escreve_entrada_pdf(id_entrada,itemlexical,imagem,legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt,descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo,arquivovideo,camposemantico,sub_campo,itensrelacionados, novas_colunas, arquivo,item[1],contador)        
                        contador += 1
                        for significado in item[2:]:

                            id_entrada,itemlexical,imagem,legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt,descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo,arquivovideo,camposemantico,sub_campo,itensrelacionados = prepara_itens(significado)   
                            if camposemantico.capitalize() == campos_semanticos[id] and subcampo.capitalize() == sub_campo.capitalize():
                                escreve_entrada_pdf(id_entrada,itemlexical,imagem,legenda_imagem,arquivosom,transcricaofonemica,transcricaofonetica,classegramatical,significadopt,descricao,arquivosomexemplo,transcricaoexemplo,traducaoexemplo,arquivovideo,camposemantico,sub_campo,itensrelacionados, novas_colunas, arquivo,significado,contador,somente_significado=True) 
                                contador += 1            
        id += 1
    arquivo.write("\n\\onecolumn\n\printindex")
    arquivo.close()
    cria_pdf_yml()
    cria_output_yml_pdf()
    cria_preamble_tex()
    cria_css()
    cria_proj_book()
    cria_index_pdf(autor, titulo_documento)
    copiar_arquivo_para_subpasta("GERAR-PRODUTOS.exe", "pdf")
def escreve_entrada_pdf(id_entrada,itemlexical, imagem, legenda_imagem ,arquivosom, transcricaofonemica, transcricaofonetica, classegramatical, significadopt, descricao, arquivosomexemplo, transcricaoexemplo, traducaoexemplo, arquivovideo, camposemantico, sub_campo, itensrelacionados, novas_colunas, arquivo, item, contador, entrada_lingua_secundaria=False, somente_significado=False):

    itemlexical = itemlexical

    primeiro_til_index = itemlexical.find("~")
    if primeiro_til_index != -1:
        # Substitua o primeiro til
        itemlexical = itemlexical[:primeiro_til_index] + " $_" + itemlexical[primeiro_til_index+1:]

        # Encontre o índice do segundo til
        segundo_til_index = itemlexical.find("~", primeiro_til_index)
        if segundo_til_index != -1:
            # Substitua o segundo til
            itemlexical = itemlexical[:segundo_til_index] + "$" + itemlexical[segundo_til_index+1:]

    chamada_topo = (itemlexical.split("|")[0]).split(" ")
    chamada_topo_separada = chamada_topo[0]
    if len(chamada_topo_separada) == 2:
        chamada_topo_separada += " "
    elif len(chamada_topo_separada) < 2:
        chamada_topo_separada += "  "
    chamada_topo2 = remover_numeros_inicio_string(significadopt).split(" ")
    chamada_topo_separada2 = chamada_topo2[0]
    if len(chamada_topo_separada2) == 2:
        chamada_topo_separada2 += " "
    elif len(chamada_topo_separada2) < 2:
        chamada_topo_separada2 += "  "

    if somente_significado == False: 

        arquivo.write("\n\n\\markboth{" + chamada_topo_separada.replace("\\'","\\textquotesingle ") + "}{" + chamada_topo_separada.replace("\\'","\\textquotesingle ") + "}\\index{" + "\\markboth{" + chamada_topo_separada2  + "}{" + chamada_topo_separada2  + "}" + remover_numeros_inicio_string(significadopt) + " (" + itemlexical.split("|")[0] + ")}")
        
        
        for i in itemlexical.split("|"):
            arquivo.write("\\negritoetamanhogrande{" + i.replace("\\'","\\textquotesingle ") + "}")
            if i != itemlexical.split("|")[-1] and i != "" and i != itemlexical[0] and len(itemlexical.split("|")) > 1:
                arquivo.write(" ~ ")            
        if transcricaofonemica != "" and transcricaofonetica == "":
            for i in transcricaofonemica.split("|"):
                arquivo.write("/"+i.replace("\\'","\\textquotesingle ")+ "/")
                if len(transcricaofonemica.split("|")) > 1:
                    if i != transcricaofonemica.split("|")[-1] and i != "":
                        arquivo.write(" ~ ")          
        elif transcricaofonemica == "" and transcricaofonetica != "":
            for i in transcricaofonetica.split("|"):                
                arquivo.write(" ["+i.replace("\\'","\\textquotesingle ") + "]")
                if len(transcricaofonetica.split("|")) > 1:
                    if i != transcricaofonetica.split("|")[-1] and i != "": 
                        arquivo.write(" ~ ")
        elif transcricaofonemica == "" and transcricaofonetica == "":
            pass
        else:
            for i in transcricaofonemica.split("|"):
                arquivo.write("/"+i.replace("\\'","\\textquotesingle ")+ "/")
                if len(transcricaofonemica.split("|")) > 1:
                    if i != transcricaofonemica.split("|")[-1] and i != "":
                        arquivo.write(" ~ ") 
            for i in transcricaofonetica.split("|"):                
                arquivo.write(" ["+i.replace("\\'","\\textquotesingle ") + "]")
                if len(transcricaofonetica.split("|")) > 1:
                    if i != transcricaofonetica.split("|")[-1] and i != "": 
                        arquivo.write(" ~ ")
        if classegramatical != "":
            arquivo.write( "\\textit{ " +classegramatical + " }")
        else:
            arquivo.write(". ")
    
    else:
        arquivo.write("\n\\index{" + "\\markboth{" + chamada_topo_separada2  + "}{" + chamada_topo_separada2  + "}" + remover_numeros_inicio_string(significadopt) + " (" + (itemlexical.split("|")[0]) + ")}")
    if significadopt != "":
        arquivo.write(" " + significadopt + ". ") 

        
    
    if descricao != "":
        arquivo.write(descricao + " ")
    else:
        arquivo.write(" ")

    if transcricaoexemplo != "":
        transcricaoexemplo = transcricaoexemplo.split("|")
        traducaoexemplo = traducaoexemplo.split("|")

        
        if len(transcricaoexemplo)  > 1:
            cont = 1
            for i in range(len(transcricaoexemplo)):
                if transcricaoexemplo != ['']:    
                    arquivo.write(" \\textit{\\textbf{"  + testa_final(transcricaoexemplo[i]).replace("\\'","\\textquotesingle ")  + "}} ")
                if traducaoexemplo != ['']:
                    if traducaoexemplo[i] != "":
                        arquivo.write( testa_final(traducaoexemplo[i])+ " ")
                    cont += 1


        elif len(transcricaoexemplo)  == 1:
            for i in range(len(transcricaoexemplo)):
                if transcricaoexemplo != ['']:
                    arquivo.write(" \\textbf{\\textit{" +  testa_final(transcricaoexemplo[i]).replace("\\'","\\textquotesingle ")  + "}} ")
                if traducaoexemplo != ['']:
                    if traducaoexemplo[i] != "":
                        arquivo.write(" " + testa_final(traducaoexemplo[i]) + " ")

    if itensrelacionados != "":
        arquivo.write(". " + "Itens relacionados: "+ itensrelacionados + "")
    cont = 17
    if len(item) == 1:
        item = item[0]
    for nova_coluna in novas_colunas:
        if item[cont] != "":
            arquivo.write(testa_final(str(item[cont])))
        cont += 1
    
    if imagem != "":
        for filename in os.listdir(os.getcwd() + "/foto"):
            if filename == imagem:
                arquivo.write('''\n```{r echo=FALSE, IMAGEM_''' + str(contador) + ''', fig.align="center", out.height="65%", out.width = "65%"}
  knitr::include_graphics("../foto/''' + filename + '''") 
```\n''')
                break
def cria_pdf_yml():
    arquivo = open(os.getcwd() + "/pdf/" + "_output.yml", mode="w+", encoding="utf-8")
    arquivo.write('''bookdown::pdf_document2:
  latex_engine: lualatex
  includes:
    in_header: preamble.tex''')
    arquivo.close
def cria_css():
    arquivo = open(os.getcwd() + "/pdf/" + "style.css", mode="w+", encoding="utf-8")
    arquivo.write('''p.caption {
  color: #777;
  margin-top: 10px;
}
p code {
  white-space: inherit;
}
pre {
  word-break: normal;
  word-wrap: normal;
}
pre code {
  white-space: inherit;
}    
    ''')
    arquivo.close
def cria_pdf_yml():
    arquivo = open(os.getcwd() + "/pdf/" + "_bookdown.yml", mode="w+", encoding="utf-8")
    arquivo.write('''delete_merged_file: true
language:
  label:
    chapter_name: "Capítulo"\n''')
    arquivo.close
def cria_output_yml_pdf():
    arquivo = open(os.getcwd() + "/pdf/" + "_output.yml", mode="w+", encoding="utf-8")
    arquivo.write('''bookdown::pdf_document2:
  latex_engine: lualatex
  keep_tex: yes
  includes:
    in_header: preamble.tex''')
    arquivo.close
def cria_preamble_tex():
    arquivo = open(os.getcwd() + "/pdf/" + "preamble.tex", mode="w+", encoding="utf-8")
    arquivo.write(r'''% preamble.tex
\usepackage{booktabs}
\usepackage[Brazil]{babel}
\usepackage[twoside,top=3.5cm,bottom=3.5cm,left=2cm,right=2cm,columnsep=50pt]{geometry} 
\usepackage{textcomp} 
\usepackage{fancyhdr}
\usepackage{parskip}
\usepackage{marvosym}
\usepackage{ragged2e}
\usepackage[T1]{fontenc}
\usepackage{titlesec}
\usepackage{emptypage}
\usepackage{lastpage} % Obter o número total de páginas
\usepackage{fontspec}

% Pacote para criar o índice
\usepackage{imakeidx}
\makeindex[columns=3, title=Índice Alfabético, intoc]

% Configuração dos títulos dos capítulos
\titleformat{\chapter}[display]
  {\normalfont\huge\bfseries}{\chaptertitlename\ \thechapter}{20pt}{\Huge}
\titlespacing*{\chapter}{0pt}{50pt}{40pt}

% Configuração das seções (section)
\titleformat{\section}
  {\normalfont\Large\bfseries}{\thesection}{1em}{}
\titlespacing*{\section}{0pt}{20pt}{10pt}

% Configuração das subseções (subsection)
\titleformat{\subsection}
  {\normalfont\large\bfseries}{\thesubsection}{1em}{}
\titlespacing*{\subsection}{0pt}{15pt}{5pt}

% Configuração de cabeçalho e rodapé
\fancyhf{} % Limpa todos os campos de cabeçalho e rodapé
\fancyhead[L]{\textsf{\rightmark}} % Cabeçalho esquerdo (capítulo)
\fancyhead[R]{\textsf{\leftmark}} % Cabeçalho direito (seção)
\fancyfoot[C]{\textbf{\textsf{\thepage}}} % Rodapé central (número da página)
\renewcommand{\headrulewidth}{1.1pt} % Linha horizontal no cabeçalho
\renewcommand{\footrulewidth}{1.1pt} % Linha horizontal no rodapé
\pagestyle{fancy} % Define o estilo de página como "fancy"
\setlength{\headheight}{12.28003pt}
% Fonte principal do documento (Arial)
\setmainfont[% OK7
UprightFont = * ,
BoldFont = *bd ,
ItalicFont = *i ,
BoldItalicFont = *bi,
]{Arial}

% Comando personalizado
\newcommand{\negritoetamanhogrande}[1]{\textbf{\large #1}}
''')
    arquivo.close
def cria_proj_book():
    arquivo = open(os.getcwd() + "/pdf/" + "book.Rproj", mode="w+", encoding="utf-8")
    arquivo.write('''Version: 1.0

RestoreWorkspace: Default
SaveWorkspace: Default
AlwaysSaveHistory: Default

EnableCodeIndexing: Yes
UseSpacesForTab: Yes
NumSpacesForTab: 2
Encoding: UTF-8

RnwWeave: Sweave
LaTeX: pdfLaTeX

BuildType: Website
''')
    arquivo.close   
def cria_index_pdf(autor, lingua):
    arquivo = open(os.getcwd() + "/pdf/" + "index.Rmd", mode="w+", encoding="utf-8")
    arquivo.write("---\n")
    arquivo.write('title: "' + lingua + '"\n')
    arquivo.write('author: "' + autor + '"\n')
    arquivo.write('''date: "`r Sys.Date()`"
documentclass: book
papersize: a4
linestretch: 1
fontsize: 10pt
site: bookdown::bookdown_site
biblio-style: apalike
---
# Introdução
''')
    introducao = cria_intro()
    arquivo.write(introducao) 
    arquivo.write('''
\\twocolumn''')
    arquivo.close

init()

