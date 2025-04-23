import os
import subprocess
from datetime import datetime
import shutil
import glob
import unicodedata
import pandas as pd
from pympi.Elan import Eaf
from tqdm import tqdm
from pydub import AudioSegment
from PIL import Image, ExifTags
import sys
import traceback


# Define the standard dimensions for each orientation
largura_padrao_paisagem = 690
altura_padrao_paisagem = 500
largura_padrao_retrato = 450
altura_padrao_retrato = 650
largura_padrao_quadrada = 500
altura_padrao_quadrada = 500
largura_minima = 400
altura_minima = 400
# Lista de extensões suportadas para diminuir bitrate
supported_extensions = [".wav",".mp3"]

# Verifica se o FFmpeg está instalado no sistema
def is_ffmpeg_installed():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

# Define o caminho para o FFmpeg localmente, se necessário
if not is_ffmpeg_installed():
    ffmpeg_folder = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin")
    ffmpeg_executable = os.path.join(ffmpeg_folder, "ffmpeg.exe")
    this_script_dir = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin")
    AudioSegment.converter = this_script_dir + '\\ffmpeg.exe'
else:
    ffmpeg_executable = "ffmpeg"

def verifica_pasta_audio():
    # Verifica se a pasta 'audio' existe
    audio_folder = os.path.join(os.getcwd(), "audio")
    if not os.path.exists(audio_folder):
        while True:
            sair = input("Pasta 'audio' não encontrada! Digite 's' para sair: ")
            if sair == "s":
                exit()
    return audio_folder

# Função para listar pastas e selecionar para backup
def listar_pastas(pastas_lista):
    # Ordena a lista de pastas
    pastas_lista.sort()
    
    # Cria uma lista numerada das pastas
    lista_numerada = [f"{i + 1}. {pasta}" for i, pasta in enumerate(pastas_lista)]
    
    # Usa o menu_simples para solicitar a seleção das pastas
    escolhas = menu_simples('Selecionar pastas', 
                            texto_explicativo="Digite os números das pastas que deseja fazer uma cópia, separados por vírgula:\n" + "\n".join(lista_numerada))
    
    # Converte as escolhas do usuário em índices
    escolhas_indices = [int(x.strip()) - 1 for x in escolhas.split(',') if x.strip().isdigit()]

    # Filtra as pastas selecionadas
    pastas_selecionadas = [pastas_lista[i] for i in escolhas_indices if 0 <= i < len(pastas_lista)]
    return pastas_selecionadas

# Função para realizar o backup das pastas selecionadas
def backup_midias(pastas_lista):
    data_hora = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_folder = os.path.join("brutos", f"{data_hora}-copia")
    os.makedirs(backup_folder, exist_ok=True)

    for pasta in pastas_lista:
        if os.path.exists(pasta):
            shutil.copytree(pasta, os.path.join(backup_folder, os.path.basename(pasta)))
            print(f"Pasta '{pasta}' copiada.")
        else:
            print(f"Pasta '{pasta}' não encontrada, pulando...")

    print(f"Cópia das mídias concluído em: {backup_folder}")

# Funções para gerar menus
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

def init():  # Inicia o funcionamento do script
    pastas_disponiveis = ["audio", "foto", "video"]  # Substitua com suas pastas reais

    # Pergunta ao usuário se deseja fazer backup antes de continuar
    fazer_backup = imprimir_menu("Cópia das pastas de Mídia",["Sim","Não"],"Deseja fazer uma cópia das pastas de mídia antes de iniciar?")
    
    if fazer_backup.lower() == "1":
        pastas_selecionadas = listar_pastas(pastas_disponiveis)
        if pastas_selecionadas:
            backup_midias(pastas_selecionadas)
        else:
            print("Nenhuma pasta foi selecionada para copiar.")
    else:
        print("A cópia não será realizada.")

    opcao = 0
    while opcao != "4":
        opcao = imprimir_menu("OPÇÕES DE MÍDIA", ["Diminuir bitrate", "Cortar áudio", 'Ajustar Imagens', 'Sair'])
        if opcao == "1":
            audio_folder = verifica_pasta_audio()
            diminuir_bitrate(audio_folder)

            opcaosaida = "0"
            while opcaosaida != "1" and opcaosaida != "2":
                opcaosaida = imprimir_menu("Diminuir bitrate", ["Voltar ao menu inicial","sair"],"Arquivos alterados na pasta 'audio', arquivos originais na pasta brutos.")
                if opcaosaida == "2":
                    opcao = "4"

        if opcao == "2":
            recortar_audio() 

            opcaosaida = "0"
            while opcaosaida != "1" and opcaosaida != "2":
                opcaosaida = imprimir_menu("Cortar áudio", ["Voltar ao menu inicial","sair"],"Arquivos recortados na pasta 'audio-novo'.")
                if opcaosaida == "2":
                    opcao = "4"            

        if opcao == "3":
            padronizar_imagens()

            opcaosaida = "0"
            while opcaosaida != "1" and opcaosaida != "2":
                opcaosaida = imprimir_menu("Ajustar Imagens", ["Voltar ao menu inicial","sair"],"Imagens ajustadas na pasta 'foto'.")
                if opcaosaida == "2":
                    opcao = "4" 

        if opcao == "4":
            sys.exit()

def diminuir_bitrate(audio_folder):
    # Pergunta ao usuário o bitrate desejado
    bitratedado = input("Para qual bitrate você deseja converter seus arquivos? (arquivos em formato WAV serão convertidos para MP3) >> ")

    # Cria a pasta 'brutos' com data e hora se não existir
    data_hora = datetime.now().strftime("%Y%m%d%H%M%S")
    brutos_bitrate_folder = os.path.join("brutos", f"{data_hora}-audio-bitrate")
    if not os.path.exists(brutos_bitrate_folder):
        os.makedirs(brutos_bitrate_folder)

    # Converte arquivos
    for filename in os.listdir(audio_folder):
        file_extension = os.path.splitext(filename)[1].lower()
        if file_extension in supported_extensions:
            input_file_path = os.path.join(audio_folder, filename)
            output_file_path = os.path.join(audio_folder, os.path.splitext(filename)[0] + ".mp3")

            # Move o arquivo original para a pasta 'brutos'
            brutos_file_path = os.path.join(brutos_bitrate_folder, filename)
            os.rename(input_file_path, brutos_file_path)

            # Verifica se o arquivo é comprimível e converte
            process = subprocess.run([ffmpeg_executable, "-i", brutos_file_path, "-b:a", f"{int(bitratedado):03d}k", output_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            print(f"Arquivo {filename} convertido!")
        elif filename == "convertidos":
            pass
        else:
            print(f"O arquivo {filename} não pode ser convertido")

    # Informa ao usuário que a tarefa foi concluída
    print(f"Tarefa concluída, arquivos convertidos para {bitratedado}K.")

# funções cortar-audio
def trata_eafs(arquivoeaf):
    arquivoeaf = Eaf(arquivoeaf)

    # obtenha as transcrições
    transcricoes = []
    for tier in arquivoeaf.get_tier_names():
        if '_transcription-' in tier.lower():
            for annotation in arquivoeaf.get_annotation_data_for_tier(tier):
                transcricoes.append(list(annotation))

    # obtenha as traduções
    traducoes = []
    for tier in arquivoeaf.get_tier_names():
        if '_translation-' in tier.lower() and "-pt" in tier.lower():
            for annotation in arquivoeaf.get_annotation_data_for_tier(tier):
                traducoes.append(list(annotation))

    # obtenha as ortografias
    ortografias = []
    for tier in arquivoeaf.get_tier_names():
        if '_orthography-' in tier.lower():
            for annotation in arquivoeaf.get_annotation_data_for_tier(tier):
                ortografias.append(list(annotation))

    #obtenha as anotações csv2rmd
    anotacoes_csv2rmd= []
    for tier in arquivoeaf.get_tier_names():
        if 'csv2rmd' in tier.lower():
            for annotation in arquivoeaf.get_annotation_data_for_tier(tier):
                anotacoes_csv2rmd.append(list(annotation))

    anotacoes = []
    for anotacao in anotacoes_csv2rmd:
        if anotacao[2] != "":
            anotacoes.append([anotacao[0],anotacao[1],strip_accents(anotacao[2]),["trans"],["tradu"],["ortog"]])
    
    for anotacao in anotacoes:
        for i in transcricoes:
            if i[0] == anotacao[0] and i[1] == anotacao[1]:
                    anotacao[3].append(i[2])
        for i in traducoes:
            if i[0] == anotacao[0] and i[1] == anotacao[1]:
                anotacao[4].append(i[2])
        for i in ortografias:
            if i[0] == anotacao[0] and i[1] == anotacao[1]:
                anotacao[5].append(i[2])

    palavras = []
    exemplos = []
    for anotacao in anotacoes:
        # Verifica se é uma entrada principal ou um exemplo
        if "-ex" not in anotacao[2]:
            palavras.append(anotacao)
        else:
            anotacao[3] = anotacao[5]
            exemplos.append(anotacao)

    return palavras,exemplos

def separa_entradas(palavras_arquivos, exemplos_arquivos):
    palavras_com_exemplos = []
    exemplos_utilizados = []
    for palavra in palavras_arquivos:
        palavra_temp = [palavra, []]

        for exemplo in exemplos_arquivos:
            testar = palavra[2] + "-ex"
            if "|" not in exemplo[2]:
                if "-" + testar in exemplo[-1]:
                    palavra_temp[1].append(exemplo)
                    if [testar, exemplo[-1]] not in exemplos_utilizados:
                        exemplos_utilizados.append([testar, exemplo[-1]])
            else:
                lista = exemplo[2].split("|")
                for item in lista:
                    if item == testar:
                        palavra_temp[1].append(exemplo)
                        if [item, exemplo[-1]] not in exemplos_utilizados:
                            exemplos_utilizados.append([item, exemplo[-1]])
        palavras_com_exemplos.append(palavra_temp)
              
    todos_ex = []
    for exemplo in exemplos_arquivos:
        if "|" in exemplo[2]:
            lista = exemplo[2].split("|")
            for i in lista:
                todos_ex.append([i,exemplo[-1]])
        else:
            todos_ex.append([exemplo[2],exemplo[-1]])

    exemplos_n_usados = todos_ex
    for exemplo in exemplos_utilizados:
        if exemplo in exemplos_n_usados:
            exemplos_n_usados.remove(exemplo)

    
    exemplos_soltos = []
    for exemplo in exemplos_n_usados:
        for exemplo_completo in exemplos_arquivos:
            if exemplo[0] in exemplo_completo[2] and exemplo[1] == exemplo_completo[-1]:
                exemplo_temp = exemplo_completo
                exemplo_temp[2] = exemplo[0]

                exemplos_soltos.append(exemplo_temp)
       
    entradas_organizadas = []
    for entrada in palavras_com_exemplos:
        entrada_temp = ["","","","","","","","","","","","","","","",""]
        
        #item lexical / ort
        if len(entrada[0][5]) != 1:
            entrada_temp[1] = entrada[0][5][1]
        # transcricao
        if len(entrada[0][3]) != 1:
            entrada_temp[5] = entrada[0][3][1]
        # traducao
        if len(entrada[0][4]) != 1:
            entrada_temp[7] = entrada[0][4][1]
        #arquivo 
        entrada_temp[3] = entrada[0][6]

        if entrada[1] != []:
            trans_exemplos = ""
            trad_exemplos = ""
            arquivo_ex = ""
            for ex in entrada[1]:
                if len(ex[3]) != 1: 
                    trans_exemplos += ex[3][1] + "|"
                if len(ex[4]) != 1:
                    trad_exemplos += ex[4][1] + "|"
                if ex[6] != "":
                    arquivo_ex += ex[6] + "|"

            entrada_temp[9] = arquivo_ex[:-1]
            entrada_temp[10] = trans_exemplos[:-1]
            entrada_temp[11] = trad_exemplos[:-1]
        else:
            entrada_temp[0] = "SEM-EX"
        entradas_organizadas.append(entrada_temp)

    for ex in exemplos_soltos:
        entrada_temp = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]

        if ex[6] != "":
            entrada_temp[9] = ex[6]
        if len(ex[3]) != 1:
            entrada_temp[10] = ex[3][1]
        if len(ex[4]) != 1:
            entrada_temp[11] = ex[4][1]
        possiveis_entradas = []
        entrada_temp[0] = "EX-ISOLADO"

        for entrada in entradas_organizadas:
            palavra = entrada[1]
            significado = entrada[7]
            
            # Verificar se a palavra está inteira na entrada_temp[10]
            if (" " + palavra + " ") in entrada_temp[10] or entrada_temp[10].startswith(palavra + " ") or entrada_temp[10].endswith(" " + palavra):
                linha = entradas_organizadas.index(entrada) + 2
                possiveis_entradas.append(palavra+"-"+ significado + "(linha:" + str(linha) + ")")

        if len(possiveis_entradas) != 0:
            entrada_temp[0] = "EX-ISOLADO, ver: " + ', '.join(possiveis_entradas)
        
        entrada_temp[1] = ex[2].replace("-ex","")
        entradas_organizadas.append(entrada_temp)
    return entradas_organizadas

def gerar_nomes_arquivos(lista, nome_eaf, extensao):
    arquivos = {}  # dicionário de arquivos gerados anteriormente
    nome_eaf = nome_eaf.replace(".eaf", "")
    for item in lista:
        nome_base = item[2].split('-ex')[0].split('|')[0]    # nome base do arquivo, removendo "-ex" e tudo depois de "|"
        if nome_base not in arquivos:
            nome_arquivo = f"{nome_eaf}-{(nome_base)}{extensao}"  # nome do arquivo sem número de sequência
            arquivos[nome_base] = 1  # adiciona o nome base ao dicionário de arquivos gerados anteriormente
        else:
            contador = arquivos[nome_base]
            nome_arquivo = f"{nome_eaf}-{nome_base}{'{:02d}'.format(contador)}{extensao}"  # nome do arquivo com número de sequência
            arquivos[nome_base] += 1  # incrementa o contador de sequência para o nome base
        if '-ex' in item[2]:  # se o nome do item contém "-ex", mantém essa string no nome do arquivo gerado
            nome_arquivo = nome_arquivo.replace(nome_base, item[2].split('|')[0])
        item.append(os.path.basename(nome_arquivo.replace(" ", "")))  # adiciona o nome do arquivo gerado ao item da lista
    return lista

def exporta_audios(lista, extensao, arquivo, nome_eaf, tamanho_str):
    output_path = os.path.join('audio-novo')
    os.makedirs(output_path, exist_ok=True)  
    nome_eaf = nome_eaf.ljust(tamanho_str)
    
    # Defina o tamanho fixo da barra de progresso (por exemplo, 30 caracteres)
    tamanho_fixo_barra = 30
    
    with tqdm(total=len(lista), desc=nome_eaf, ncols=100, bar_format='{desc} {percentage:3.0f}%|{bar:30}| {n_fmt}/{total_fmt}') as pbar:
        for clip in lista:
            start_time, end_time, filename = clip[0], clip[1], clip[-1]
            filepath = os.path.join(output_path, filename)
            audio_clip = arquivo[start_time:end_time]
            audio_clip.export(filepath, format=extensao.replace(".", ""))
            pbar.set_postfix(file=filename)
            pbar.update(1)

def strip_accents(s):
    s = s.replace("?", "").replace("!", "").replace("/", "").replace("\\", "").replace(" ", "-").replace(",", "").strip().lower()
    s = unicodedata.normalize("NFD", s)
    s = s.encode("ascii", "ignore").decode("utf-8")
   
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')

def recortar_audio():
    opcoesvalidas = ["1","2"]

    opcaoformato = imprimir_menu("Recortar Áudio",["WAV","MP3"],"Você deseja exportar os recortes em qual formato? Digite a opção desejada")

    while opcaoformato not in opcoesvalidas:
        print("Digite 1 para WAV ou 2 para MP3")
        opcaoformato = input("Opção >>  ")

    if opcaoformato == "1":
        extensao = ".wav"
    else: 
        extensao = ".mp3"

    busca1 = os.getcwd() + r"//eaf//*.wav"
    arquivoswav = glob.glob(busca1)
    busca2 = os.getcwd() + r"//eaf//*.eaf"
    arquivoseaf = glob.glob(busca2)
    busca3 = os.getcwd() + r"//eaf//*.mp3"
    arquivosmp3 = glob.glob(busca2)
    dados_por_arquivo = []
    erros = []
    palavras_arquivos = []
    exemplos_arquivos = []
    cont = 0
    tamanhos_str = 0
    for arquivoeaf in arquivoseaf:
        if len(os.path.basename(arquivoeaf)) > tamanhos_str:
            tamanhos_str = len(os.path.basename(arquivoeaf))
    
    for arquivoeaf in arquivoseaf:
        arquivo = open(arquivoeaf, 'r', encoding="utf-8")
        cont += 1

        try:
            audio = AudioSegment.from_wav(arquivoeaf.replace(".eaf",".wav"))
        except:
            try:
                audio = AudioSegment.from_mp3(arquivoeaf.replace(".eaf",".mp3"))
            except:
                print(f"Erro no arquivo, verifique as midias correspondentes: {os.path.basename(arquivoeaf)}")
                erro = arquivoeaf

                with open("erros.txt", "a") as f:
                    f.write(erro + "\n")

                continue  # pula para o próximo arquivo

        palavras, exemplos = trata_eafs(arquivoeaf)
        palavras_arquivos1 = gerar_nomes_arquivos(palavras,arquivoeaf,extensao)
        exemplos_arquivos1 = gerar_nomes_arquivos(exemplos, arquivoeaf,extensao)
        exporta_audios(palavras_arquivos1+exemplos, extensao, audio, os.path.basename(arquivoeaf),tamanhos_str)
        palavras_arquivos += palavras_arquivos1
        exemplos_arquivos += exemplos_arquivos1

    print("quantidade de arquivos:" + str(cont))


    entradas_organizadas = separa_entradas(palavras_arquivos,exemplos_arquivos)


    if not os.path.exists(os.getcwd() + '/audio-novo/'): 
        os.makedirs(os.getcwd() + '/audio-novo/')


    colunas_padrao = 'ID','ITEM_LEXICAL','IMAGEM','ARQUIVO_SONORO','TRANSCRICAO_FONEMICA','TRANSCRICAO_FONETICA','CLASSE_GRAMATICAL','TRADUCAO_SIGNIFICADO','DESCRICAO','ARQUIVO_SONORO_EXEMPLO','TRANSCRICAO_EXEMPLO','TRADUCAO_EXEMPLO','ARQUIVO_VIDEO','CAMPO_SEMANTICO',"SUB_CAMPO_SEMANTICO","ITENS_RELACIONADOS"


    dicionario = pd.DataFrame(columns=colunas_padrao,data=entradas_organizadas)

    # Nome base do arquivo
    data_hora = datetime.now().strftime("%Y%m%d%H%M%S")
    base_filename =  f"dicionario-{data_hora}"
    extension = ".csv"
    new_filename = base_filename + extension


    # Salvando o DataFrame no novo arquivo CSV
    dicionario.to_csv(new_filename, encoding="UTF-8", index=False)

def delete_empty_folder(folder_path):
    """
    Verifica se a pasta está vazia e a apaga se estiver.
    
    :param folder_path: Caminho da pasta a ser verificada.
    """
    if os.path.exists(folder_path) and len(os.listdir(folder_path)) == 0:
        shutil.rmtree(folder_path)  
    else:
      pass 

def resize_and_pad(image_path, output_path):
    """
    Redimensiona e ajusta a imagem para o tamanho desejado sem distorção e sem mudar a orientação.
    
    :param image_path: Caminho da imagem de entrada.
    :param output_path: Caminho da imagem de saída.
    """
    with Image.open(image_path) as image:
        # Corrige a orientação da imagem com base nos metadados EXIF
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = image._getexif()
            if exif is not None:
                exif = dict(exif.items())
                if orientation in exif:
                    if exif[orientation] == 3:
                        image = image.rotate(180, expand=True)
                    elif exif[orientation] == 6:
                        image = image.rotate(270, expand=True)
                    elif exif[orientation] == 8:
                        image = image.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            pass

        original_width, original_height = image.size
        
        # Determinar a orientação da imagem
        if original_width > original_height:
            desired_width = largura_padrao_paisagem
            desired_height = altura_padrao_paisagem
        elif original_width < original_height:
            desired_width = largura_padrao_retrato
            desired_height = altura_padrao_retrato
        else:
            desired_width = largura_padrao_quadrada
            desired_height = altura_padrao_quadrada
        
        # Calcular as proporções
        original_ratio = original_width / float(original_height)
        desired_ratio = desired_width / float(desired_height)
        
        if original_ratio > desired_ratio:
            # A imagem é mais larga em proporção, então ajusta a largura
            new_width = desired_width
            new_height = int(desired_width / original_ratio)
        else:
            # A imagem é mais alta em proporção, então ajusta a altura
            new_height = desired_height
            new_width = int(desired_height * original_ratio)
        
        # Redimensiona a imagem
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        
        # Cria uma nova imagem com o tamanho desejado e fundo branco
        new_image = Image.new("RGB", (desired_width, desired_height), (255, 255, 255))
        
        # Calcula a posição para centralizar a imagem redimensionada
        paste_position = ((desired_width - new_width) // 2, (desired_height - new_height) // 2)
        
        # Cola a imagem redimensionada na nova imagem
        new_image.paste(resized_image, paste_position)
        
        # Salva a nova imagem
        new_image.save(output_path)

def padronizar_imagens():

    data_hora = datetime.now().strftime("%Y%m%d%H%M%S")
    # Define the input and output directories
    imagens_input_dir = os.path.join(os.getcwd(),'foto')
    imagens_output_dir = os.path.join(os.getcwd(),'foto')
    imagens_brutos_dir = os.path.join(os.getcwd(),"brutos", f"{data_hora}-foto")
    imagens_pequenas_dir = os.path.join(os.getcwd(),'foto/imagens_pequenas') 
    # Ensure output directories exist
    os.makedirs(imagens_output_dir, exist_ok=True)
    os.makedirs(imagens_brutos_dir, exist_ok=True)
    os.makedirs(imagens_pequenas_dir, exist_ok=True)

    # Loop through all files in the input directory
    # Loop through all files in the input directory
    for filename in os.listdir(imagens_input_dir):
        # Check if the file is an image
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
            image_path = os.path.join(imagens_input_dir, filename)
            output_path = os.path.join(imagens_output_dir, filename)
            
            with Image.open(image_path) as image:
                original_width, original_height = image.size
                
                if original_width < largura_minima or original_height < altura_minima:
                    # Move the image to the pequenas directory
                    os.rename(image_path, os.path.join(imagens_pequenas_dir, filename))
                    continue
            
            # Move the original image to the brutos directory
            try:
                os.rename(image_path, os.path.join(imagens_brutos_dir, filename))
            except FileNotFoundError:
                print(f"File not found: {image_path}")
            except PermissionError:
                print(f"Permission error: {image_path}")
            
            # Resize and pad the image
            resize_and_pad(os.path.join(imagens_brutos_dir, filename), output_path)

    # Verifica se a pasta 'imagens_pequenas' está vazia e a apaga se estiver
    delete_empty_folder(imagens_pequenas_dir)




if __name__ == "__main__":
    try:
        init()
    except Exception as e:
        # Captura a exceção e exibe uma mensagem de erro
        print("Ocorreu um erro no programa.")
        traceback.print_exc()  # Mostra a exceção completa com o rastreamento
        input("Pressione Enter para fechar...")  # Mantém a janela aberta até o usuário pressionar Enter
