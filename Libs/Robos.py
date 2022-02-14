from re import A, X
from time import sleep
from turtle import right
from selenium import *
from re import search
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from Libs.Logs import Logs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from Libs.AppConfig import appConfig
from Libs.Classes import *
from datetime import date
import datetime as dt
import clipboard as c
import pyautogui
#from workday import workday as wd

log = Logs.RetornaLog("--C6--")
json = appConfig()
data_atual = date.today()
data_em_texto = f'{data_atual.day}/{data_atual.month}/{data_atual.year}'
url_portal = json.retorna_c6_url()
retorno = Retorno_Inatividade()


class C6():
    def __init__(self, proxy = False) -> None:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument('--verbose')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        

        self.driver = webdriver.Chrome('./chromedriver', chrome_options=chrome_options)        
    def login_portal(self)-> Retorno_Inatividade:
        
        login_usuario = json.retorna_c6_login()
        senha_usuario = json.retorna_c6_senha()
        
        log.info('Iniciando o método de login no portal')
        self.driver.maximize_window()
        self.driver.get(url_portal)
        self.driver.implicitly_wait(5)

        log.info(f'Navegando para: {url_portal}')
        
        login = check_exists_by_id(self.driver, 'login', ativo=True)
        if login:
            log.info('Preenchendo login')
            login.send_keys(login_usuario)
        else:
            retorno.processo = False
            return retorno
        
        senha = check_exists_by_id(self.driver, 'passw', ativo=True)
        if senha:
            log.info('Preenchendo a senha')
            senha.send_keys(senha_usuario)
        else:
            retorno.processo = False
            return retorno
        
        btn_entrar = check_exists_by_id(self.driver, 'btEntrar', ativo=True)
        if btn_entrar:
            log.info('Acessando o portal')
            btn_entrar.click()
            
            #INICIANDO VERIFICAÇÃO DO MFA
            campo_mfa = check_exists_by_id(self.driver, 'mfaPassCode', ativo=True)
            if campo_mfa:
                log.info('Abrindo aplicativo OKTA para pegar o código')     
                pyautogui.press("win")
                sleep(0.5)
                pyautogui.write("Okta")
                sleep(0.5)
                pyautogui.press("backspace")
                sleep(0.5)
                pyautogui.press('enter')
                sleep(16)
                #Dando duplo clique para copiar o código
                pyautogui.doubleClick(x=97, y=135)
                sleep(0.5)
                #Clicando no X para fechar
                pyautogui.click(x=193, y=17)
                sleep(0.5)
                #Clicando em confirmar fechamento
                pyautogui.click(x=276, y=239)
                sleep(0.5)
                #CLIANDO NO CAMPO DE DIGITAR O CÓDIGO 
                log.info('Clicando no campo de digitar o código')
                campo_mfa.click()
                sleep(0.5)
                # Dando Ctrl + v para colar o código copiado
                pyautogui.hotkey('ctrl', 'v')
                sleep(0.5)
                
            else:
                retorno.processo = False
                return retorno
            
            btn_entrar = check_exists_by_id(self.driver, 'btEntrar', ativo=True)
            if btn_entrar:
                log.info('Acessando o portal')
                btn_entrar.click()
            else:
                retorno.processo = False
                return retorno 
            
            #VERIFIANCO SE O PORTAL CONSEGUIU LOGAR CORRETAMENTE, CASO CONTRARIO SUBIR O LAÇO
            sem_conexao = check_exists_by_id(self.driver, 'reload-button', ativo=True)    
            login = check_exists_by_id(self.driver, 'login', ativo=True)  
            errologin = check_exists_by_class(self.driver, 'message.messageLogin.error', ativo=True)
            if errologin:
                log.info(f'Erro de login encontrado: {errologin.text}')
                if errologin.text.startswith("Usuário logado na estação"):
                    log.info('Tentando executar o login novamente...')
                    log.info('Aguardando 10 segundos para tentar novamente...')
                    sleep(10)
                    retorno.processo = False
                    return retorno
                else:
                    sleep(3)
                    log.info(f'Não encontrado erro de login')
                    self.driver.get('https://gracco.corp.c6bank.com/gestao-processos')
                    
                    log.info('Acessando o link: https://gracco.corp.c6bank.com/gestao-processos')
                    #Criado esse bloco para testar o carregamento da página. Enquanto estiver carregando ele não sai do laço   
                    verifica_carregamento(self.driver)
                    #aqui vai o return true. 
                    retorno.processo = True
                    return retorno
            #Verificando o ID de página não carregada, caso seja verdadeiro, aguardar e reiniciar laço    
            elif sem_conexao:
                #sleep(5)
                self.driver.implicitly_wait(5)
                log.info('Pagina sem conexão com a internet')
                retorno.processo = False
                return retorno
                
            #Verificando se a página de login está carregada para recomeçar laço        
            elif login:
                log.info('Pagina de login encontrada, voltando laço para preencher login')
                retorno.processo = False
                return retorno 
                
                
            else: 
                log.info(f'Não encontrado erro de login')
                self.driver.get('https://gracco.corp.c6bank.com/gestao-processos')
                log.info('Acessando o link: https://gracco.corp.c6bank.com/gestao-processos')
                #Criado esse bloco para testar o carregamento da página. Enquanto estiver carregando ele não sai do laço   
                verifica_carregamento(self.driver)
                retorno.processo = True
                return retorno       
        else:
            retorno.processo = False
            return retorno 
    def consulta_processo_aceite(self, Processo:Aceite)-> Retorno_Inatividade:
        try:
            aceite_encontrado = False
            a = Aceite()
            a.NumeroProcesso = Processo.NumeroProcesso
            a.Status = Processo.Status

            log.info(f'Capturando o processo: {a.NumeroProcesso}')

            combo_processo = check_exists_by_id(
                self.driver, 'campoChavePesqHeader')
            if combo_processo:
                log.info('Acessando a combo da pesquisa')
                combo = Select(self.driver.find_element_by_id('campoChavePesqHeader'))
                combo.select_by_value('PROCESSO_NUMERO')

            else:
                retorno.processo = False
                return retorno

            pesquisa_processo = check_exists_by_id(self.driver, 'palavraChavePesqHeader')
            if pesquisa_processo:
                log.info('Preenchendo campo pesquisa')
                pesquisa_processo.send_keys(Keys.LEFT_CONTROL + 'A')
                pesquisa_processo.send_keys(a.NumeroProcesso)
            else:
                retorno.processo = False
                return retorno

            btn_pesquisa = check_exists_by_id(self.driver, 'btPesquisarPesqHeader')
            if btn_pesquisa:
                log.info('Acessando botão de pesquisa')
                verifica_carregamento(self.driver)
                btn_pesquisa.click()
                sleep(6)
            else:
                retorno.processo = False
                return retorno

            clique_processo = check_exists_by_xpath(self.driver, '/html/body/div[2]/div[2]/div[3]/div/div/div[2]/div[3]/div[3]/div/table/tbody/tr/td[2]')
            if clique_processo:
                log.info('Clique no processo na grid')
                clique_processo.click()

                clique_tutela = check_exists_by_id(self.driver, 'btnProcessoTutela')
                sleep(3)
                if clique_tutela:
                    log.info('Clique no botão tutelar')
                    clique_tutela.click()
                    
                    clique_tarefas_concluidas = check_exists_by_id(self.driver, 'divTarefasConcluidas')
                    clique_tarefas_vencendo = check_exists_by_id(self.driver, 'divTarefasVencendoHoje')
                    clique_tarefas_andamento = check_exists_by_id(self.driver, 'divTarefasEmAndamento')
                    
                    if clique_tarefas_concluidas and clique_tarefas_vencendo and clique_tarefas_andamento:
                        clique_tarefas_concluidas.click()
                        sleep(1)
                        clique_tarefas_vencendo.click()
                        sleep(1)
                        clique_tarefas_andamento.click()
                        sleep(1)
                        log.info('Verificando se existe aceite.')
                        div_tarefas = check_elements_exists_by_id(self.driver,'divtarefas')
                        if div_tarefas:
                            log.info('Listando as tarefas do contrato')
                            linhas_div_tarefas = check_elements_exists_by_class(self.driver,'solicLinha')
                            cont_linha = 0
                            if linhas_div_tarefas:
                                for linha in linhas_div_tarefas:
                                    cont_linha +=1
                                    log.info(linha.text)
                                    if search('ACEITAR CONTRATAÇÃO' ,linha.text):
                                        log.info('Aceite Encontrado')
                                        
                                        if not search('Concluído', linha.text):
                                            log.info('Aceite não realizado.')
                                            if cont_linha == 1:
                                                clique_concluir = check_exists_by_xpath(self.driver, '/html/body/div[2]/div[2]/div[3]/div[3]/div/div[2]/div[3]/form/div[3]/div[2]/div[1]/div[4]/div[1]/div[2]/div[2]/div')
                                                sleep(1)
                                            else:
                                                clique_concluir = check_exists_by_xpath(self.driver, f'/html/body/div[2]/div[2]/div[3]/div[3]/div/div[2]/div[3]/form/div[3]/div[2]/div[1]/div[4]/div[{cont_linha}]/div[2]/div[2]/div')
                                                sleep(1)
                                            
                                            if clique_concluir:
                                                clique_concluir.click()
                                                aceite_encontrado = True
                                                break 
                                        else:
                                            #!Aceite já realizado
                                            log.info('Aceite já realizado anteriormente para esse contrato')
                                            limpeza_campos(self.driver)
                                            retorno.processo = True
                                            return retorno       
                            
                        if not aceite_encontrado:
                                log.info('Tentando escrever na barra de pesquisas')
                                barra_pesquisa = check_exists_by_id(self.driver, 'palavraChaveAcoes')
                                if barra_pesquisa:
                                    barra_pesquisa.send_keys('ACEITAR CONTRATAÇÃO')
                                    log.info('Campo de pesquisa preenchido')
                                    botao_barra_pesquisa = check_exists_by_id(self.driver, 'btnPesquisarAcoes')
                                    if botao_barra_pesquisa:
                                        log.info('Pesquisando...')
                                        botao_barra_pesquisa.click()
                                        clique_aceitar_contratacao = check_exists_by_xpath(self.driver, '/html/body/div[2]/div[2]/div[3]/div[4]/div/div[2]/div[3]/form/div[4]/div/div[2]/div[2]/a[1]')
                                        if clique_aceitar_contratacao:
                                            aceite_encontrado = True
                                            clique_aceitar_contratacao.click()            
                        
                        if aceite_encontrado:
                            clique_seletor = check_exists_by_id(self.driver, 'select2-statusFinalTarefa-container')
                            if clique_seletor:
                                log.info('Selecionando o seletor para dar o Aceite')
                                clique_seletor.click()
                                sleep(2)
                                clique_caixa_seletor = check_exists_by_xpath(self.driver, '/html/body/span/span/span[1]/input')
                                if clique_caixa_seletor:
                                    clique_caixa_seletor.send_keys('Aceite')
                                    clique_caixa_seletor.send_keys(Keys.ENTER)

                                    btn_salvar_aceite = check_exists_by_xpath(self.driver, '/html/body/div[2]/div[2]/div[3]/div[3]/div/div[1]/div/form/div[2]/div[1]/div/div')
                                    sleep(1)
                                    if btn_salvar_aceite:
                                        btn_salvar_aceite.click()
                                        log.info('Aceite salvo com sucesso!')
                                        limpeza_campos(self.driver)
                                        retorno.processo = True
                                        return retorno
                        else:
                            #!Aceite não encontrado
                            log.info('Erro: Aceite não encontrado')
                            limpeza_campos(self.driver)
                            retorno.processo = False
                            return retorno
            
            #!Não encontrou o processo.
            else:
                log.info('Erro: Não encontrou o processo')
                pesquisa_processo = check_exists_by_id(self.driver, 'palavraChavePesqHeader')
                if pesquisa_processo:
                    log.info('Limpando o campo pesquisa')
                    pesquisa_processo.send_keys(Keys.LEFT_CONTROL + 'A')
                    pesquisa_processo.send_keys(Keys.BACK_SPACE)
                    retorno.processo = False
                    return retorno
                else:
                    log.info(f'Erro detectado no campo de pesquisa de processo')
                    retorno.processo = False
                    return retorno         
        except:
            retorno.processo = False
            log.info('Inconsistência no sistema...')
            return retorno 
    def lancamento_processo_subsidio(self, Processo:Subsidio)-> bool:
        try: 
            a = Subsidio()
            a.NumeroProcesso = Processo.NumeroProcesso
            a.Status = Processo.Status

            log.info(f'Capturando o processo: {a.NumeroProcesso}')

            combo_processo = check_exists_by_id(self.driver, 'campoChavePesqHeader')
            if combo_processo:
                log.info('Acessando a combo da pesquisa')
                combo = Select(self.driver.find_element_by_id('campoChavePesqHeader'))
                combo.select_by_value('PROCESSO_NUMERO')

            else:
                retorno.processo = False
                return retorno

            pesquisa_processo = check_exists_by_id(
                self.driver, 'palavraChavePesqHeader')
            if pesquisa_processo:
                log.info('Preenchendo campo pesquisa')
                pesquisa_processo.send_keys(Keys.LEFT_CONTROL + 'A')
                pesquisa_processo.send_keys(a.NumeroProcesso)
            else:
                retorno.processo = False
                return retorno

            btn_pesquisa = check_exists_by_id(self.driver, 'btPesquisarPesqHeader')
            if btn_pesquisa:
                log.info('Acessando botão de pesquisa')
                verifica_carregamento(self.driver)
                btn_pesquisa.click()
                sleep(6)
            else:
                retorno.processo = False
                return retorno

            clique_processo = check_exists_by_xpath(self.driver, '/html/body/div[2]/div[2]/div[3]/div/div/div[2]/div[3]/div[3]/div/table/tbody/tr/td[2]')
            if clique_processo:
                log.info('Clique no processo na grid')
                clique_processo.click()

                clique_tutela = check_exists_by_id(self.driver, 'btnProcessoTutela')
                if clique_tutela:
                    log.info('Clique no botão tutelar')
                    sleep(2)
                    clique_tutela.click()

                    #inserir o código para a verificação se o processo já tem subssídios. 
                    lancou_subssidio = verifica_tarefas_subsidio(self.driver)
                    log.info(lancou_subssidio)
                    if lancou_subssidio == False:
                        log.info('Tentando escrever na barra de pesquisas')
                        barra_pesquisa = check_exists_by_id(self.driver, 'palavraChaveAcoes')
                        if barra_pesquisa:
                            barra_pesquisa.send_keys('BUSCAR SUBSÍDIOS')
                            log.info('Campo de pesquisa preenchido')
                            botao_barra_pesquisa = check_exists_by_id(self.driver, 'btnPesquisarAcoes')
                            if botao_barra_pesquisa:
                                log.info('Pesquisando...')
                                botao_barra_pesquisa.click()
                                clique_lancar_subsidios = check_exists_by_xpath(self.driver, '/html/body/div[2]/div[2]/div[3]/div[3]/div/div[2]/div[3]/form/div[4]/div/div[2]/div[2]/a[1]')
                                if clique_lancar_subsidios:
                                    clique_lancar_subsidios.click()
                                    log.info('Clicado em lançar subsídios')
                                    data_lancamento = atualiza_data_v2()
                                    log.info('Calculando a data para o lançamento')
                                    if data_lancamento:
                                        escreve_data_agendamento = check_exists_by_name(self.driver,'dataAgendamento')
                                        if escreve_data_agendamento:
                                            log.info('Escrevendo a data de Agendamento')
                                            escreve_data_agendamento.send_keys(data_lancamento)
                                            escreve_data_fatal = check_exists_by_name(self.driver,'dataPrazoFatal')
                                            if escreve_data_fatal:
                                                log.info('Escrevendo data prazo fatal')
                                                escreve_data_fatal.send_keys(data_lancamento)
                                                log.info('Clicando em salvar os subsídios')
                                                clique_salvar_subsidio = check_exists_by_xpath(self.driver,'/html/body/div[2]/div[2]/div[3]/div[3]/div/div[1]/div/form/div[2]/div[1]/div/div')
                                                if clique_salvar_subsidio:
                                                    clique_salvar_subsidio.click()
                                                    log.info('Subsídio lançado com sucesso')
                                                    limpeza_campos(self.driver)
                                                    retorno.processo = True
                                                    return retorno
                                                
                    else:
                        #!Subssídio já foi lançado anteriormente.
                        limpeza_campos(self.driver)
                        retorno.processo = False
                        return retorno
            else:
                log.info('Erro: Não encontrou o processo')
                pesquisa_processo = check_exists_by_id(self.driver, 'palavraChavePesqHeader')
                if pesquisa_processo:
                    log.info('Limpando o campo pesquisa')
                    pesquisa_processo.send_keys(Keys.LEFT_CONTROL + 'A')
                    pesquisa_processo.send_keys(Keys.BACK_SPACE)
                else:
                    log.info(f'Erro detectado no campo de pesquisa de processo')
                    retorno.processo = False
                    return retorno
                
                retorno.processo = False
                return retorno
                #Não encontrou o processo.
        except:
            retorno.processo = False
            log.info('Inconsistência no sistema...')
            return retorno
    def lancamento_copias(self, Processo:Upload)-> bool:
        
            #criando o objeto upload e passando os valores que vieram da fila para esse objeto.
            up = Upload()
            up.NumeroProcesso = Processo.NumeroProcesso
            up.CaminhoArquivo = Processo.CaminhoArquivo
            up.NomeArquivo = Processo.NomeArquivo
            up.Status = Processo.Status
            
            log.info(f'Capturando o processo: {up.NumeroProcesso}')

            combo_processo = check_exists_by_id(self.driver, 'campoChavePesqHeader')
            if combo_processo:
                log.info('Acessando a combo da pesquisa')
                combo = Select(self.driver.find_element_by_id('campoChavePesqHeader'))
                combo.select_by_value('PROCESSO_NUMERO')

            else:
                retorno.processo = False
                return retorno

            pesquisa_processo = check_exists_by_id(self.driver, 'palavraChavePesqHeader')
            if pesquisa_processo:
                log.info('Preenchendo campo pesquisa')
                pesquisa_processo.send_keys(Keys.LEFT_CONTROL + 'A')
                pesquisa_processo.send_keys(up.NumeroProcesso)
            else:
                retorno.processo = False
                return retorno

            btn_pesquisa = check_exists_by_class(self.driver, 'btnPesquisar')
            if btn_pesquisa:
                log.info('Acessando botão de pesquisa')
                verifica_carregamento(self.driver)
                btn_pesquisa.click()
                sleep(6)
            else:
                retorno.processo = False
                return retorno
            #except:
            #og.info("erro")
            # CLICANDO NO NÚMERO DO PROCESSOR
            clique_number_processo = check_exists_by_class(self.driver, 'sorting_1')
            if clique_number_processo:
                log.info('Clicando no número do processo')
                clique_number_processo.click()
                sleep(1)
            # CLICANDO EM ARQUIVOS
                clique_arquivos = check_exists_by_id(self.driver, 'profile')
                if clique_arquivos:
                    log.info('Clicando em arquivos')
                    clique_arquivos.click()
                    sleep(0.8)
                #CLICANDO NO MAIS DO DOCUMENTO
                    clique_mais = check_exists_by_xpath(self.driver, '/html/body/div[2]/div[2]/div[3]/div[2]/div/div[2]/div/div[2]/div[9]/div[2]/form/div[1]/div/div[2]/div[1]/div[2]/ul/li[3]/div[1]/span[2]')
                    if clique_mais:
                        log.info('Clicando no mais para upload do documento')
                        clique_mais.click()
                        sleep(0.5)
                        #CLICANDO EM "CLIQUE AQUI PARA SUBIR SEUS ARQUIVOS"
                        clique_inserir = check_exists_by_xpath(self.driver, '/html/body/div[2]/div[2]/div[3]/div[2]/div/div[1]/div/form/div[3]')
                        if clique_inserir:
                            log.info('Clicando em inserir arquivos')
                            clique_inserir.click()
                            sleep(2)
                            # Clicando no campo de inserir nome do arquivo
                            pyautogui.press('enter')
                            sleep(1)
                            #Levando o indicador do mouse até o campo correto para digitar o caminho
                            pyautogui.press(['tab', 'tab', 'tab', 'tab', 'tab'])
                            sleep(3)
                            #Confirmando se o ponteiro do mouse está no lugar certo
                            pyautogui.press('enter')
                            sleep(1)
                            #Escrevendo o caminho do arquivo no campo selecionado
                            pyautogui.write(up.CaminhoArquivo)
                            sleep(1)
                            #Clicando em Enter para pesquisar o caminho
                            pyautogui.press('enter')
                            sleep(1)
                            #Clicando em TAB para pular para o campo de inserir o nome do arquivo
                            pyautogui.press('tab')
                            sleep(1)
                            #ESCREVENDO O NOME DO ARQUIVO
                            pyautogui.write(up.NumeroProcesso)
                            sleep(1)
                            #Clicando em Enter para pesquisar o nome do arquivo
                            pyautogui.press('enter')
                            sleep(1)
                            #Pressionando Tab para selecionar o arquivo encontrado
                            pyautogui.press('tab', presses=2)
                            sleep(1)
                            #Clicando na tecla para direita para selecionar realmente o arquivo
                            pyautogui.press('right')
                            sleep(1)
                            #Clicando em Enter para finalizar a abertura do arquivo
                            pyautogui.press('enter')
                            sleep(1)
                            pyautogui.press('enter')
                            sleep(1)
                #Verificando se existe a palavra sentença no nome do arquivo, caso contenha, clicando em sentença            
                if "SENTENÇA" in up.NomeArquivo:
                    combo_sentenca = check_exists_by_class(self.driver, '#previews > div.dz-preview.dz-file-preview > select')
                    if combo_sentenca:
                      log.info('Acessando o combo da sentença')
                      combo2 = Select(self.driver.find_element_by_class_name('#previews > div.dz-preview.dz-file-preview > select'))
                      combo2.select_by_value('2')
                      sleep(2)
                 #Se o documento não conter o nome Sentença executar o comando de baixo     
                #else: 
                    #log.info('Acessando o combo padrão')
                    #combo1 = Select(self.driver.find_element_by_class_name('#previews > div.dz-preview.dz-file-preview > select'))
                    #combo1.select_by_value('1')
                    #sleep(2)
                         
            #Clicando no botão de salvar 
                btn_salvar = check_exists_by_xpath(self.driver, '//*[@id="profileSalvar"]')
                if btn_salvar: 
                    log.info('Acessando botão de salvar')
                    pyautogui.press('pageup')
                    sleep(1)
                    pyautogui.press('pageup')
                    sleep(0.5)
                    btn_salvar.click()
                    sleep(1)
                    
            #FECHANDO A ABA APÓS CONSULTA DE PROCESSO
                btn_fechar = check_exists_by_class(self.driver, 'abaFechar')
                if btn_fechar:
                    log.info('Clicando em botão fechar')
                    # FUNÇÃO CARREGAR ELEMENTO
                    verifica_carregamento2(self.driver)
                    btn_fechar.click()
                    sleep(2)
                    

                
                    
                    
  
  
  
                              
def verifica_carregamento(driver, debug=False):
    try:
        cont =0
        display = driver.find_element_by_id('_viewRoot:status.start').value_of_css_property('display') 
        while display == 'inline':
            cont +=1
            sleep(1)
            log.error(f'Carregamento de tela encontrado: Aguardando {cont}')
            display = driver.find_element_by_id('_viewRoot:status.start').value_of_css_property('display')
        log.info('Carregamento de tela concluído')
        
    except NoSuchElementException as erro:
        log.info(f'Carregamento de tela não localizado...')
    return False
   
                             
def atualiza_data_v2():
    #*Aqui temos que fazer o calculo da data a ser lancada
    data = dt.date(data_atual.year, data_atual.month, data_atual.day)
    data_lancamento = str(wd.workdays(data, 8))
    data_lancamento_final = f'{data_lancamento[8:8+2]}/{data_lancamento[5:5+2]}/{data_lancamento[0:0+4]}'
    return data_lancamento_final

def check_exists_by_id(driver, id, debug = False, ativo = False):
    if not ativo:
        ativo = verifica_inatividade(driver)
    
    if ativo:
        try:
            elemento = driver.find_element_by_id(id)
            sleep(1)
            if elemento:
                elemento = WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.ID, id)))
        except NoSuchElementException as erro:
            if debug:
                log.info(f'Erro detectado: {erro.msg}')
            return False
        return elemento
    else:
        return False
def check_exists_by_name(driver, name, debug=False ,ativo = False):
    if not ativo:
        ativo = verifica_inatividade(driver)
    
    if ativo:
        try:
            elemento = driver.find_element_by_name(name)
            sleep(1)
            if elemento:
                elemento = WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.NAME, name)))
        except NoSuchElementException as erro:
            if debug:
                log.info(f'Erro detectado: {erro.msg}')
            return False
        return elemento
    else:
        return False
def check_exists_by_class(driver, classe, debug=False,ativo = False):
    if not ativo:
        ativo = verifica_inatividade(driver)
    if ativo:
        try:
            elemento = driver.find_element_by_class_name(classe)
            sleep(1)
            if elemento:
                elemento = WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.CLASS_NAME, classe)))
        except NoSuchElementException as erro:
            if debug:
                log.info(f'Erro detectado: {erro.msg}')
            return False
        return elemento
    else:
        return False
def check_exists_by_xpath(driver, xpath, debug=False,ativo = False):
    if not ativo:
        ativo = verifica_inatividade(driver)
    if ativo:
        try:
            elemento = driver.find_element_by_xpath(xpath)
            sleep(1)
            if elemento:
                elemento = WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except NoSuchElementException as erro:
            if debug:
                log.info(f'Erro detectado: {erro.msg}')
            return False
        return elemento
    else:
        return False


def check_elements_exists_by_id(driver, id, debug=False,ativo = False):
    if not ativo:
        ativo = verifica_inatividade(driver)
    if ativo:
        try:
            elemento = driver.find_elements_by_id(id)
            sleep(1)
            if elemento:
                elemento = WebDriverWait(driver, 180).until(EC.presence_of_all_elements_located((By.ID, id)))
        except NoSuchElementException as erro:
            if debug:
                log.info(f'Erro detectado: {erro.msg}')
            return False
        return elemento
    else:
        return False
def check_elements_exists_by_class(driver, classe, debug=False,ativo = False):
    if not ativo:
        ativo = verifica_inatividade(driver)
    if ativo:
        try:
            elemento = driver.find_elements_by_class_name(classe)
            sleep(1)
            if elemento:
                elemento = WebDriverWait(driver, 180).until(EC.presence_of_all_elements_located((By.CLASS_NAME, classe)))
        except NoSuchElementException as erro:
            if debug:
                log.info(f'Erro detectado: {erro.msg}')
            return False
        return elemento
    else:
        return False
def check_elements_exists_by_xpath(driver, xpath, debug=False,ativo = False):
    if not ativo:
        ativo = verifica_inatividade(driver)
    if ativo:
        try:
            elemento = driver.find_elements_by_xpath(xpath)
            sleep(1)
            if elemento:
                elemento = WebDriverWait(driver, 180).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        except NoSuchElementException as erro:
            if debug:
                log.info(f'Erro detectado: {erro.msg}')
            return False
        return elemento
    else:
        return False

def verifica_carregamento(driver, debug=False):
    try:
        spinner = driver.find_element_by_class_name('spinnerLoading')
        if spinner:
            spinner = WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.CLASS_NAME, 'spinnerLoading'))) 
            if spinner:
                cont = 1
                log.info('Carregamento de tela encontrado, Aguardando loading...')
                while spinner:
                    sleep(1)
                    log.info(f'Tempo aguardando ... {cont}')
                    cont = cont + 1
                    spinner = driver.find_element_by_class_name('spinnerLoading')
                    sleep(0.3)
                    if spinner:
                        spinner = WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.CLASS_NAME, 'spinnerLoading')))

    except NoSuchElementException as erro:
        log.info(f'Carregamento de tela não localizado...')
        return False
    
#ATUALIZAÇÃO PIETRO   
def verifica_carregamento2(driver, debug=False):
    try:
        spinner2 = driver.find_element_by_class_name('spinnerLoadingText')
        if spinner2:
            spinner2 = WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.CLASS_NAME, 'spinnerLoadingText'))) 
            if spinner2:
                cont = 1
                log.info('Aguardando o salvamento do arquivo')
                while spinner2:
                    sleep(1)
                    log.info(f'Tempo aguardando ... {cont}')
                    cont = cont + 1
                    spinner2 = driver.find_element_by_class_name('spinnerLoadingText')
                    sleep(0.3)
                    if spinner2:
                        spinner2 = WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.CLASS_NAME, 'spinnerLoadingText')))

    except NoSuchElementException as erro:
        log.info(f'Carregamento de tela não localizado...')
        return False
#FIM ATUALIZAÇÃO PIETRO 

def limpeza_campos(driver):
    log.info('Chamando a rotina de limpeza dos campos')
    for x in range(2):
    #Limpa os campos
        limpar = check_exists_by_xpath(driver, f'/html/body/div[2]/div[2]/div[2]/div/ul/li[2]/div[2]/i')
        if limpar:
            sleep(1)
            limpar.click()
        
        
    pesquisa_processo = check_exists_by_id(driver, 'palavraChavePesqHeader')
    if pesquisa_processo:
        log.info('Limpando o campo pesquisa')
        pesquisa_processo.send_keys(Keys.LEFT_CONTROL + 'A')
        pesquisa_processo.send_keys(Keys.DELETE)

def verifica_tarefas_subsidio(driver)-> bool:
    clique_tarefas_concluidas = check_exists_by_id(driver, 'divTarefasConcluidas')
    if clique_tarefas_concluidas:
        clique_tarefas_concluidas.click()
        log.info('Verificando se existe lançamento de subssídios.')
        div_tarefas = check_elements_exists_by_id(driver,'divtarefas')
        if div_tarefas:
            log.info('Listando as tarefas do contrato')
            linhas_div_tarefas = check_elements_exists_by_class(driver,'solicLinha')
            if linhas_div_tarefas:
                for linha in linhas_div_tarefas:
                    log.info(linha.text)
                    if ('BUSCAR SUBSÍDIOS' in linha.text.upper()):
                        log.info('Subssídio lançado')
                        return True                                  
                    else:
                        log.info('Subssídio não encontrado na tarefa')
                        return False
            else:
                log.info('Não conseguiu encontrar as linhas da div_tarefas')
                return False
        else: 
            log.info('Não conseguiu encontrar a div_tarefas')
            return False
    else:
        log.info('Não conseguiu encontrar o clique de tarefas concluidas')
        return False       
def verifica_tarefas_aceite(driver):
    try:
        clique_tarefas_concluidas = check_exists_by_id(driver, 'divTarefasConcluidas')
        if clique_tarefas_concluidas:
            clique_tarefas_concluidas.click()
            log.info('Verificando se existe aceite.')
            div_tarefas = driver.find_elements_by_id('divtarefas')
            if div_tarefas:
                log.info('Listando as tarefas do contrato')
                linhas_div_tarefas = driver.find_elements_by_class_name('solicLinha')
                cont_linha = 0
                if linhas_div_tarefas:
                    for linha in linhas_div_tarefas:
                        cont_linha +=1
                        log.info(linha.text)
                        if ('ACEITAR CONTRATAÇÃO' in linha.text):
                            log.info('Aceite Encontrado')
                            
                            return True, cont_linha                               
                        else:
                            log.info('Aceite não Encontrado')
                            return False
                else:
                    log.info('Não conseguiu encontrar as linhas da div_tarefas')
                    return False
            else: 
                log.info('Não conseguiu encontrar a div_tarefas')
                return False
        else:
            log.info('Não conseguiu encontrar o clique de tarefas concluidas')
            return False       
    except:
        return False        
def verifica_inatividade(driver):
    url_corrente = 'https://gracco.corp.c6bank.com/gestao-processos'
    if not driver.current_url.strip().startswith(url_corrente):
        retorno.ativo = False
        log.info('Encontrado uma inconsistência no sistema...')
        log.info('Tentativa de reestabelecimento de rotinas...')
        return False
    else: 
        retorno.ativo = True
        return True






