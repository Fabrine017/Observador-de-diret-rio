#Bibliotecas
import os
import time
from pathlib import Path
import threading
import logging
from logging.handlers import RotatingFileHandler
#Configuração de log 
logger = logging.getLogger()
logger.setLevel(logging.INFO)
arquivo_logger = RotatingFileHandler(
    filename ='logs',
    maxBytes = 5_248_00,
    backupCount = 5,
    encoding = 'utf-8'
)
logger.addHandler(arquivo_logger)
formataçao = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%d/%m/%Y | %H:%M:%S')
arquivo_logger.setFormatter(formataçao)
#Exceções personalizadas
class DiretorioInexistente(Exception):
    pass
#Funções
#A função encerrar() determina o fim da execução.
def encerrar():
    while True:
        comando = input('Digite "stop" para encerrar: ').lower()
        if comando !='stop':
            continue
        else:
            evento_encerrar.set()
            break
#A função monitorar() compara o estado inicial e atual do diretório e gera dados e logs dos eventos
#ocorridos.
def monitorar():
    while True:
        arquivos_iniciais = os.listdir(diretorio)
        for arquivo_inicial in arquivos_iniciais:
            caminho_inicial = os.path.join(diretorio,arquivo_inicial)
            id_iniciais[arquivo_inicial] = os.stat(caminho_inicial).st_ino
        time.sleep(5)   
        arquivos_atuais = os.listdir(diretorio)
#Comparando as listas de arquivos. Primeiro registramos os arquivos adicionados.
        if arquivos_iniciais != arquivos_atuais:
            if len(arquivos_atuais) > len(arquivos_iniciais):
                adicionado = str(set(arquivos_atuais) - set(arquivos_iniciais))
                arquivos_adicionados.append(adicionado)
                logging.info(f'Arquivo adicionado: {adicionado.replace('{','').replace('}','')}')
#Depois registramos os arquivos removidos.
            if len(arquivos_iniciais) > len(arquivos_atuais):
                removido = str(set(arquivos_iniciais) - set(arquivos_atuais))
                arquivos_removidos.append(removido)
                logging.info(f'Arquivo removido: {removido.replace('{','').replace('}','')}')
#E depois verificamos os arquivos renomeados. Para isso, compararamos os nomes dos arquivos que possuem 
#o mesmo ID em diferentes momentos. Se o nome for diferente, o programa registra uma mudança no nome do 
#arquivo. Primeiro, ele identifica o ID de cada um dos arquivos atuais.
        for arquivo_atual in arquivos_atuais:
            caminho_atual = os.path.join(diretorio, arquivo_atual)
            id_atual = os.stat(caminho_atual).st_ino
#Depois verifica se esse ID é igual a algum ID do dicionário de IDs iniciais. Caso afirmativo, ele confere
#se esse arquivo ainda possui o mesmo nome, verificando se o arquivo atual está no dicionário como uma 
#chave. Se não estiver, isso quer dizer que seu nome foi modificado.
            for arquivo_inicial, id_arquivo in id_iniciais.items():
                if id_arquivo == id_atual:
                    if arquivo_atual not in id_iniciais.keys():
                        logging.info(f'Arquivo renomeado: {arquivo_inicial.replace('{','').replace('}','')} -> {arquivo_atual.replace('{','').replace('}','')}')
                        arquivos_renomeados.append(arquivo_inicial)
        if evento_encerrar.is_set():
            break
#Início de operação
inicio = time.time()
evento_encerrar = threading.Event()
arquivos_adicionados = []
arquivos_removidos = []
arquivos_renomeados = []
id_iniciais = {}
try:
    diretorio = input('Caminho do diretório: ')
    if os.path.exists(diretorio):
        diretorio = Path(diretorio)
#Estabelecendo as funções encerrar() e monitoramento() como threads.
        exec_encerrar = threading.Thread(target=encerrar)
        exec_monitorar = threading.Thread(target=monitorar)
#Executando as threads "exec_encerrar" e "exec_monitorar".
        exec_encerrar.start()
        exec_monitorar.start()
#Esperando a finalização das duas threads.
        exec_encerrar.join()
        exec_monitorar.join()
#Gerando métricas.
        adicionados_num = len(arquivos_adicionados)
        removidos_num = len(arquivos_removidos)
        renomeados_num = len(arquivos_renomeados)
#Contando o tempo de monitoramento
        fim = time.time()
        tempo = round(fim - inicio)
        horas = tempo//3600
        minutos = tempo//60
        segundos = tempo
        if tempo > 59:
            segundos = (tempo%60)
#Obtendo informações para o dashboard.
        nome_diretorio = os.path.basename(diretorio)
        monitorados_num = len(os.listdir(diretorio)) + len(arquivos_removidos)
        with open('logs','r',encoding = 'utf-8') as arquivo_logs:
            tamanho_arquivo = os.path.getsize('logs')
            if tamanho_arquivo == 0:
                ultimo_evento = 'Nenhum evento registrado.'
            else:
                for evento in arquivo_logs:
                    continue
                else:
                    ultimo_evento = evento 
#Printando as informações no terminal.
        print('===================================\n')
        print('RELATÓRIO DE MONITORAMENTO\n')
        print('===================================\n')
        print(f'| Diretório monitorado: {nome_diretorio}\n')
        print(f'| Total de arquivos monitorados: {monitorados_num}\n')
        print(f'| Arquivos adicionados: {adicionados_num}\n')
        print(f'| Arquivos removidos: {removidos_num}\n')
        print(f'| Arquivos renomeados: {renomeados_num}\n')
        print(f'| Tempo em monitoramento: {horas:02d}:{minutos:02d}:{segundos:02d}\n')
        print(f'| Último evento: {ultimo_evento.replace('{','').replace('}','')}\n')
    else:
        raise DiretorioInexistente
except DiretorioInexistente:
    print('Esse diretório não existe.')