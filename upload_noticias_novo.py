import os
import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import NoSuchElementException

#### ---- FUNÇÕES AUXILIARES ---- ####

def configurar_logging(pasta_nome):
    """Configura o logging dinâmico para cada pasta"""
    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler(f'log - {pasta_nome}.txt'),
            logging.StreamHandler()
        ]
    )

def registrar_erro_em_tempo_real(pasta_base, ano, nome_arquivo, arquivo_erros='arquivos-erro.txt'):
    """Registra um erro no arquivo em tempo real, organizado por pasta/ano."""
    cabecalho = f"#### {os.path.basename(pasta_base)} - {ano} ####"
    
    # Verifica se o cabeçalho já foi escrito no arquivo
    cabecalho_existente = False
    if os.path.exists(arquivo_erros):
        with open(arquivo_erros, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            cabecalho_existente = cabecalho in conteudo
    
    # Escreve no arquivo (modo append)
    with open(arquivo_erros, 'a', encoding='utf-8') as f:
        if not cabecalho_existente:
            f.write(f"{cabecalho}\n")
        f.write(f"{nome_arquivo}\n")

def selecionar_categoria(navegador, nome_categoria):
    try:
        logging.info(f"Selecionando categoria: {nome_categoria}")
        categoria_select = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="category_contents_id"]'))
        )
        select = Select(categoria_select)
        try:
            select.select_by_visible_text(nome_categoria)
            logging.info("Categoria selecionada pelo texto")
            return True
        except NoSuchElementException:
            options = [option.text for option in select.options]
            logging.warning(f"Categoria não encontrada! Opções disponíveis: {options}")
            return False
    except Exception as e:
        logging.error(f"Erro ao selecionar categoria: {str(e)}")
        return False

def parsear_data(data_str):
    """Converte datas no formato 'terça-feira, 23 de setembro de 2025' para '23/09/2025'"""
    try:
        if ',' in data_str:
            data_str = data_str.split(',', 1)[1].strip()
        
        partes = data_str.split()
        if len(partes) < 5 or partes[1] != 'de' or partes[3] != 'de':
            logging.error(f"Formato de data inesperado: {data_str}")
            return None
            
        dia = partes[0]
        mes_str = partes[2].lower()
        ano = partes[4]
        
        meses = {
            'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
            'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
            'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
        }
        
        mes = meses.get(mes_str)
        if mes is None:
            logging.error(f"Mês não reconhecido: {mes_str}")
            return None
            
        return f"{dia}/{mes}/{ano}"
    except Exception as e:
        logging.error(f"Erro ao parsear data: {str(e)}")
        return None

#### ---- FUNÇÕES DE CADASTRO MODULARIZADAS ---- ####

def cadastrar_categoria(navegador, nome_da_categoria):
    """Seleciona a categoria na página de cadastro"""
    try:
        logging.info(f'Selecionando categoria: {nome_da_categoria}')
        if not selecionar_categoria(navegador, nome_da_categoria):
            logging.error("Falha ao selecionar categoria")
            return False
        return True
    except Exception as e:
        logging.error(f"Erro em cadastrar_categoria: {str(e)}")
        return False

def cadastrar_titulo(navegador, titulo):
    """Preenche o campo de título"""
    try:
        logging.info(f'Preenchendo título: {titulo}')
        campo_titulo = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="title"]'))
        )
        campo_titulo.clear()
        campo_titulo.send_keys(titulo)
        
        # Verifica se o valor foi inserido corretamente
        WebDriverWait(navegador, 5).until(
            lambda d: campo_titulo.get_attribute('value').strip() == titulo.strip()
        )
        return True
    except Exception as e:
        logging.error(f"Erro em cadastrar_titulo: {str(e)}")
        return False

def cadastrar_autor(navegador, nome_autor):
    """Preenche o campo de autor no formulário"""
    try:
        if not nome_autor:  # Campo opcional
            logging.info('Campo autor vazio, pulando preenchimento')
            return True
            
        logging.info(f'Preenchendo autor: {nome_autor}')
        campo_autor = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="author"]'))
        )
        campo_autor.clear()
        campo_autor.send_keys(nome_autor)
        
        # Verifica se o valor foi inserido corretamente
        WebDriverWait(navegador, 5).until(
            lambda d: campo_autor.get_attribute('value').strip() == nome_autor.strip()
        )
        return True
    except Exception as e:
        logging.error(f"Erro em cadastrar_autor: {str(e)}")
        return False

def cadastrar_data(navegador, data_publicacao):
    """Preenche a data de publicação"""
    try:
        if not data_publicacao:
            logging.info('Campo data vazio, pulando preenchimento')
            return True  # Campo não obrigatório
            
        logging.info(f'Preenchendo data de publicação: {data_publicacao}')
        campo_data = WebDriverWait(navegador, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="publication_date"]'))
        )
        campo_data.clear()
        campo_data.send_keys(data_publicacao)
        return True
    except Exception as e:
        logging.error(f"Erro em cadastrar_data: {str(e)}")
        return False

def cadastrar_texto(navegador, texto):
    """Preenche o campo de texto principal"""
    try:
        # Mostra apenas os primeiros 100 caracteres do texto no log para não poluir
        texto_preview = texto[:100] + "..." if len(texto) > 100 else texto
        logging.info(f'Preenchendo texto principal: {texto_preview}')
        
        campo_texto = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.note-editable'))
        )
        campo_texto.clear()
        campo_texto.send_keys(texto)
        return True
    except Exception as e:
        logging.error(f"Erro em cadastrar_texto: {str(e)}")
        return False

def adicionar_arquivo(nome_arquivo, navegador, caminho_pasta, titulo):
    """Adiciona um arquivo ao formulário"""
    try:
        logging.info(f"Clicando no botão 'Adicionar Arquivo' para: {nome_arquivo}")
        navegador.find_element(By.ID, 'btn-adicionar').click()
        time.sleep(2)
        
        input_arquivo = navegador.find_element(By.CLASS_NAME, 'archives')
        caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
        logging.info(f"Subindo o arquivo: {caminho_arquivo}")
        input_arquivo.send_keys(caminho_arquivo)

        campo_descricao = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.ID, 'description'))
        )
        campo_descricao.send_keys(titulo)

        WebDriverWait(navegador, 10).until(
            lambda d: campo_descricao.get_attribute('value').strip() != ''
        )
        
        time.sleep(5)
        logging.info(f"Arquivo {nome_arquivo} adicionado com sucesso.")
        return True
    except Exception as e:
        logging.error(f"Erro ao adicionar o arquivo {nome_arquivo}: {str(e)}")
        return False

def clicar_no_salvar(navegador):
    """Clica no botão Salvar e verifica se foi bem sucedido"""
    try:
        logging.info("Clicando no botão 'Salvar'")
        navegador.find_element(By.ID, 'btn-submit').click()
        WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.alert.alert-success'))
        )
        logging.info("Publicação salva com sucesso.")
        return True
    except Exception as e:
        logging.error(f"Erro ao clicar no botão 'Salvar': {str(e)}")
        return False

def cadastrar_publicacao_com_upload(dados, caminho_pasta, navegador):
    """Função principal que coordena todo o processo de cadastro para uma notícia"""
    try:
        titulo = dados['Titulo']
        data_publicacao = parsear_data(dados['Data'])
        texto = dados['Texto']
        nome_da_categoria = dados['Categoria']
        autor = dados.get('Autor', '')  # Campo opcional
        imagens_str = dados.get('Imagens', '')
        lista_imagens = [img.strip() for img in imagens_str.split(',')] if imagens_str else []
        
        if not titulo or not data_publicacao or not texto or not nome_da_categoria:
            logging.warning(f"Dados incompletos em {caminho_pasta}")
            return False

        titulo_truncado = titulo[:120] if len(titulo) > 120 else titulo
        if len(titulo) > 120:
            logging.warning(f"Título truncado (mais de 120 caracteres): {titulo}")

        # Acessar página de cadastro
        logging.info('Acessando página de cadastro')
        WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/section[2]/div/div/div/div[1]/div[1]/a'))
        ).click()

        # Executar fluxo de cadastro
        steps = [
            lambda: cadastrar_categoria(navegador, nome_da_categoria),
            lambda: cadastrar_titulo(navegador, titulo_truncado),
            lambda: cadastrar_autor(navegador, autor),
            lambda: cadastrar_data(navegador, data_publicacao),
            lambda: cadastrar_texto(navegador, texto),
        ]
        
        # Adicionar passos para cada imagem
        for img in lista_imagens:
            steps.append(lambda img=img: adicionar_arquivo(img, navegador, caminho_pasta, titulo))
        
        steps.append(lambda: clicar_no_salvar(navegador))
        
        for step in steps:
            if not step():
                logging.error("Interrompendo processo devido a erro em uma das etapas")
                return False
                
        time.sleep(2)
        return True
        
    except Exception as e:
        logging.error(f"Erro ao processar a notícia em {caminho_pasta}: {str(e)}")
        return False

#### ---- FUNÇÕES DE PROCESSAMENTO ---- ####

def processar_pastas(pasta_base, navegador):
    erros_por_pasta = {}
    try:
        # Lista para armazenar todos os caminhos de dados.json
        caminhos_json = []
        
        # Percorre a pasta_base e encontra todos os dados.json
        for root, _, files in os.walk(pasta_base):
            if 'dados.json' in files:
                caminhos_json.append(os.path.join(root, 'dados.json'))
        
        # Ordena as pastas numericamente (pagina1, pagina2, ...)
        caminhos_json.sort(key=lambda path: (
            int(os.path.basename(
                os.path.dirname(
                    os.path.dirname(path)
                )
            ).replace('pagina', ''))
        ))
        
        total = len(caminhos_json)
        logging.info(f"Total de notícias encontradas: {total}")
        
        for i, caminho_json in enumerate(caminhos_json, 1):
            logging.info(f"\n{'='*30}")
            logging.info(f"Processando notícia {i} de {total}")
            logging.info(f"Caminho: {caminho_json}")
            logging.info(f"{'='*30}\n")
            
            try:
                with open(caminho_json, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                # Log dos dados que serão processados
                logging.info(f"Dados da notícia: Título='{dados['Titulo']}', Categoria='{dados['Categoria']}', Autor='{dados.get('Autor', 'N/A')}'")
            except Exception as e:
                logging.error(f"Erro ao ler {caminho_json}: {str(e)}")
                erros_por_pasta.setdefault(os.path.dirname(caminho_json), []).append(caminho_json)
                continue
                
            # A pasta da notícia é o diretório que contém o dados.json
            pasta_noticia = os.path.dirname(caminho_json)
            sucesso = cadastrar_publicacao_com_upload(dados, pasta_noticia, navegador)
            if not sucesso:
                erros_por_pasta.setdefault(pasta_noticia, []).append(caminho_json)
                
    except Exception as e:
        logging.error(f"Erro ao processar pastas: {str(e)}")
        
    return erros_por_pasta

def escrever_arquivo_erros(erros_global):
    """Função opcional para gerar um arquivo consolidado ao final"""
    with open('arquivos-erro-consolidado.txt', 'w', encoding='utf-8') as f:
        for (pasta_base, pasta), arquivos in erros_global.items():
            f.write(f"#### {pasta_base} - {pasta} ####\n")
            for arquivo in arquivos:
                f.write(f"{arquivo}\n")
            f.write("\n")

#### ---- EXECUÇÃO PRINCIPAL ---- ####
if __name__ == "__main__":
    erros_global = {}
    try:
        # Configurações fixas
        url = 'https://juareztavora.maximatecnologia.com.br/cms/'
        email = 'suporte@maxima.inf.br'
        password = 'r<nO$=33rc3M}'
        caminho_base = '/home/newton/juarez_tavora/Noticias'
        menu_do_cms = 'Noticias'  # Fixamos o menu em Publicações
        
        pasta_nome = os.path.basename(caminho_base)
        configurar_logging(pasta_nome)
        
        logging.info(f'\n{"#"*50}')
        logging.info(f'INICIANDO PROCESSAMENTO PARA: {pasta_nome}')
        logging.info(f'Menu CMS: {menu_do_cms}')
        logging.info(f'{"#"*50}\n')
        
        try:
            logging.info('# INICIANDO O NAVEGADOR #')
            servico = Service(GeckoDriverManager().install())
            navegador = webdriver.Firefox(service=servico)

            logging.info('Acessando o CMS')
            navegador.get(url)
            navegador.find_element(By.CSS_SELECTOR, 'input[name="email"]').send_keys(email)
            navegador.find_element(By.CSS_SELECTOR, 'input[name="password"]').send_keys(password)
            navegador.find_element(By.XPATH, '/html/body/div/div/div[2]/form/div[3]/div[2]/button').click()
            
            if menu_do_cms == 'Noticias':
                logging.info('Clicando em Noticias')
                WebDriverWait(navegador, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '.fa-fw.fa-newspaper-o'))
                ).click()

            if menu_do_cms == 'Publicações':
                logging.info('Clicando em Publicações')
                WebDriverWait(navegador, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '.fa-fw.fa-book'))
                ).click()

            erros_pasta = processar_pastas(caminho_base, navegador)
            for pasta, arquivos in erros_pasta.items():
                erros_global[(pasta_nome, pasta)] = arquivos

            navegador.quit()
            logging.info(f"Processo concluído para {pasta_nome}!")

        except Exception as e:
            logging.error(f"Erro fatal no processamento de {pasta_nome}: {str(e)}")
            if 'navegador' in locals():
                navegador.quit()

        # Opcional: Gera um arquivo consolidado ao final
        escrever_arquivo_erros(erros_global)

    except Exception as e:
        logging.error(f"Erro na inicialização: {str(e)}")







'''
import os
import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import NoSuchElementException

#### ---- FUNÇÕES AUXILIARES ---- ####

def configurar_logging(pasta_nome):
    """Configura o logging dinâmico para cada pasta"""
    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler(f'log - {pasta_nome}.txt'),
            logging.StreamHandler()
        ]
    )

def registrar_erro_em_tempo_real(pasta_base, ano, nome_arquivo, arquivo_erros='arquivos-erro.txt'):
    """Registra um erro no arquivo em tempo real, organizado por pasta/ano."""
    cabecalho = f"#### {os.path.basename(pasta_base)} - {ano} ####"
    
    # Verifica se o cabeçalho já foi escrito no arquivo
    cabecalho_existente = False
    if os.path.exists(arquivo_erros):
        with open(arquivo_erros, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            cabecalho_existente = cabecalho in conteudo
    
    # Escreve no arquivo (modo append)
    with open(arquivo_erros, 'a', encoding='utf-8') as f:
        if not cabecalho_existente:
            f.write(f"{cabecalho}\n")
        f.write(f"{nome_arquivo}\n")

def selecionar_categoria(navegador, nome_categoria):
    try:
        logging.info(f"Selecionando categoria: {nome_categoria}")
        categoria_select = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="category_contents_id"]'))
        )
        select = Select(categoria_select)
        try:
            select.select_by_visible_text(nome_categoria)
            logging.info("Categoria selecionada pelo texto")
            return True
        except NoSuchElementException:
            options = [option.text for option in select.options]
            logging.warning(f"Categoria não encontrada! Opções disponíveis: {options}")
            return False
    except Exception as e:
        logging.error(f"Erro ao selecionar categoria: {str(e)}")
        return False

def parsear_data(data_str):
    """Converte datas no formato 'terça-feira, 23 de setembro de 2025' para '23/09/2025'"""
    try:
        if ',' in data_str:
            data_str = data_str.split(',', 1)[1].strip()
        
        partes = data_str.split()
        if len(partes) < 5 or partes[1] != 'de' or partes[3] != 'de':
            logging.error(f"Formato de data inesperado: {data_str}")
            return None
            
        dia = partes[0]
        mes_str = partes[2].lower()
        ano = partes[4]
        
        meses = {
            'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
            'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
            'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
        }
        
        mes = meses.get(mes_str)
        if mes is None:
            logging.error(f"Mês não reconhecido: {mes_str}")
            return None
            
        return f"{dia}/{mes}/{ano}"
    except Exception as e:
        logging.error(f"Erro ao parsear data: {str(e)}")
        return None

#### ---- FUNÇÕES DE CADASTRO MODULARIZADAS ---- ####

def cadastrar_categoria(navegador, nome_da_categoria):
    """Seleciona a categoria na página de cadastro"""
    try:
        logging.info('Selecionando categoria')
        if not selecionar_categoria(navegador, nome_da_categoria):
            logging.error("Falha ao selecionar categoria")
            return False
        return True
    except Exception as e:
        logging.error(f"Erro em cadastrar_categoria: {str(e)}")
        return False

def cadastrar_titulo(navegador, titulo):
    """Preenche o campo de título"""
    try:
        logging.info('Preenchendo título')
        campo_titulo = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="title"]'))
        )
        campo_titulo.clear()
        campo_titulo.send_keys(titulo)
        
        # Verifica se o valor foi inserido corretamente
        WebDriverWait(navegador, 5).until(
            lambda d: campo_titulo.get_attribute('value').strip() == titulo.strip()
        )
        return True
    except Exception as e:
        logging.error(f"Erro em cadastrar_titulo: {str(e)}")
        return False

def cadastrar_autor(navegador, nome_autor):
    """Preenche o campo de autor no formulário"""
    try:
        if not nome_autor:  # Campo opcional
            return True
            
        logging.info('Preenchendo autor')
        campo_autor = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="author"]'))
        )
        campo_autor.clear()
        campo_autor.send_keys(nome_autor)
        
        # Verifica se o valor foi inserido corretamente
        WebDriverWait(navegador, 5).until(
            lambda d: campo_autor.get_attribute('value').strip() == nome_autor.strip()
        )
        return True
    except Exception as e:
        logging.error(f"Erro em cadastrar_autor: {str(e)}")
        return False

def cadastrar_data(navegador, data_publicacao):
    """Preenche a data de publicação"""
    try:
        if not data_publicacao:
            return True  # Campo não obrigatório
            
        logging.info('Preenchendo data de publicação')
        campo_data = WebDriverWait(navegador, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="publication_date"]'))
        )
        campo_data.clear()
        campo_data.send_keys(data_publicacao)
        return True
    except Exception as e:
        logging.error(f"Erro em cadastrar_data: {str(e)}")
        return False

def cadastrar_texto(navegador, texto):
    """Preenche o campo de texto principal"""
    try:
        logging.info('Preenchendo texto principal')
        campo_texto = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.note-editable'))
        )
        campo_texto.clear()
        campo_texto.send_keys(texto)
        return True
    except Exception as e:
        logging.error(f"Erro em cadastrar_texto: {str(e)}")
        return False

def adicionar_arquivo(nome_arquivo, navegador, caminho_pasta, titulo):
    """Adiciona um arquivo ao formulário"""
    try:
        logging.info("Clicando no botão 'Adicionar Arquivo'")
        navegador.find_element(By.ID, 'btn-adicionar').click()
        time.sleep(2)
        
        input_arquivo = navegador.find_element(By.CLASS_NAME, 'archives')
        caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
        logging.info(f"Subindo o arquivo: {caminho_arquivo}")
        input_arquivo.send_keys(caminho_arquivo)

        campo_descricao = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.ID, 'description'))
        )
        campo_descricao.send_keys(titulo)

        WebDriverWait(navegador, 10).until(
            lambda d: campo_descricao.get_attribute('value').strip() != ''
        )
        
        time.sleep(5)
        logging.info(f"Arquivo {nome_arquivo} adicionado com sucesso.")
        return True
    except Exception as e:
        logging.error(f"Erro ao adicionar o arquivo {nome_arquivo}: {str(e)}")
        return False

def clicar_no_salvar(navegador):
    """Clica no botão Salvar e verifica se foi bem sucedido"""
    try:
        logging.info("Clicando no botão 'Salvar'")
        navegador.find_element(By.ID, 'btn-submit').click()
        WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.alert.alert-success'))
        )
        logging.info("Publicação salva com sucesso.")
        return True
    except Exception as e:
        logging.error(f"Erro ao clicar no botão 'Salvar': {str(e)}")
        return False

def cadastrar_publicacao_com_upload(dados, caminho_pasta, navegador):
    """Função principal que coordena todo o processo de cadastro para uma notícia"""
    try:
        titulo = dados['Titulo']
        data_publicacao = parsear_data(dados['Data'])
        texto = dados['Texto']
        nome_da_categoria = dados['Categoria']
        autor = dados.get('Autor', '')  # Campo opcional
        imagens_str = dados.get('Imagens', '')
        lista_imagens = [img.strip() for img in imagens_str.split(',')] if imagens_str else []
        
        if not titulo or not data_publicacao or not texto or not nome_da_categoria:
            logging.warning(f"Dados incompletos em {caminho_pasta}")
            return False

        titulo_truncado = titulo[:120] if len(titulo) > 120 else titulo
        if len(titulo) > 120:
            logging.warning(f"Título truncado (mais de 120 caracteres): {titulo}")

        # Acessar página de cadastro
        logging.info('Acessando página de cadastro')
        WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/section[2]/div/div/div/div[1]/div[1]/a'))
        ).click()

        # Executar fluxo de cadastro
        steps = [
            lambda: cadastrar_categoria(navegador, nome_da_categoria),
            lambda: cadastrar_titulo(navegador, titulo_truncado),
            lambda: cadastrar_autor(navegador, autor),  # NOVO PASSO
            lambda: cadastrar_data(navegador, data_publicacao),
            lambda: cadastrar_texto(navegador, texto),
        ]
        
        # Adicionar passos para cada imagem
        for img in lista_imagens:
            steps.append(lambda img=img: adicionar_arquivo(img, navegador, caminho_pasta, titulo))
        
        steps.append(lambda: clicar_no_salvar(navegador))
        
        for step in steps:
            if not step():
                logging.error("Interrompendo processo devido a erro em uma das etapas")
                return False
                
        time.sleep(2)
        return True
        
    except Exception as e:
        logging.error(f"Erro ao processar a notícia em {caminho_pasta}: {str(e)}")
        return False

#### ---- FUNÇÕES DE PROCESSAMENTO ---- ####

def processar_pastas(pasta_base, navegador):
    erros_por_pasta = {}
    try:
        # Lista para armazenar todos os caminhos de dados.json
        caminhos_json = []
        
        # Percorre a pasta_base e encontra todos os dados.json
        for root, _, files in os.walk(pasta_base):
            if 'dados.json' in files:
                caminhos_json.append(os.path.join(root, 'dados.json'))
        
        # Ordena as pastas numericamente (pagina1, pagina2, ...)
        caminhos_json.sort(key=lambda path: (
            int(os.path.basename(
                os.path.dirname(
                    os.path.dirname(path)
                )
            ).replace('pagina', ''))
        ))
        
        total = len(caminhos_json)
        logging.info(f"Total de notícias encontradas: {total}")
        
        for i, caminho_json in enumerate(caminhos_json, 1):
            logging.info(f"\n{'='*30}")
            logging.info(f"Processando notícia {i} de {total}")
            logging.info(f"Caminho: {caminho_json}")
            logging.info(f"{'='*30}\n")
            
            try:
                with open(caminho_json, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
            except Exception as e:
                logging.error(f"Erro ao ler {caminho_json}: {str(e)}")
                erros_por_pasta.setdefault(os.path.dirname(caminho_json), []).append(caminho_json)
                continue
                
            # A pasta da notícia é o diretório que contém o dados.json
            pasta_noticia = os.path.dirname(caminho_json)
            sucesso = cadastrar_publicacao_com_upload(dados, pasta_noticia, navegador)
            if not sucesso:
                erros_por_pasta.setdefault(pasta_noticia, []).append(caminho_json)
                
    except Exception as e:
        logging.error(f"Erro ao processar pastas: {str(e)}")
        
    return erros_por_pasta

def escrever_arquivo_erros(erros_global):
    """Função opcional para gerar um arquivo consolidado ao final"""
    with open('arquivos-erro-consolidado.txt', 'w', encoding='utf-8') as f:
        for (pasta_base, pasta), arquivos in erros_global.items():
            f.write(f"#### {pasta_base} - {pasta} ####\n")
            for arquivo in arquivos:
                f.write(f"{arquivo}\n")
            f.write("\n")

#### ---- EXECUÇÃO PRINCIPAL ---- ####
if __name__ == "__main__":
    erros_global = {}
    try:
        # Configurações fixas
        url = 'https://juareztavora.maximatecnologia.com.br/cms/'
        email = 'suporte@maxima.inf.br'
        password = 'r<nO$=33rc3M}'
        caminho_base = '/home/newton/juarez_tavora/Noticias'
        menu_do_cms = 'Noticias'  # Fixamos o menu em Publicações
        
        pasta_nome = os.path.basename(caminho_base)
        configurar_logging(pasta_nome)
        
        logging.info(f'\n{"#"*50}')
        logging.info(f'INICIANDO PROCESSAMENTO PARA: {pasta_nome}')
        logging.info(f'Menu CMS: {menu_do_cms}')
        logging.info(f'{"#"*50}\n')
        
        try:
            logging.info('# INICIANDO O NAVEGADOR #')
            servico = Service(GeckoDriverManager().install())
            navegador = webdriver.Firefox(service=servico)

            logging.info('Acessando o CMS')
            navegador.get(url)
            navegador.find_element(By.CSS_SELECTOR, 'input[name="email"]').send_keys(email)
            navegador.find_element(By.CSS_SELECTOR, 'input[name="password"]').send_keys(password)
            navegador.find_element(By.XPATH, '/html/body/div/div/div[2]/form/div[3]/div[2]/button').click()
            
            if menu_do_cms == 'Noticias':
                logging.info('Clicando em Noticias')
                WebDriverWait(navegador, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '.fa-fw.fa-newspaper-o'))
                ).click()

            if menu_do_cms == 'Publicações':
                logging.info('Clicando em Publicações')
                WebDriverWait(navegador, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '.fa-fw.fa-book'))
                ).click()

            erros_pasta = processar_pastas(caminho_base, navegador)
            for pasta, arquivos in erros_pasta.items():
                erros_global[(pasta_nome, pasta)] = arquivos

            navegador.quit()
            logging.info(f"Processo concluído para {pasta_nome}!")

        except Exception as e:
            logging.error(f"Erro fatal no processamento de {pasta_nome}: {str(e)}")
            if 'navegador' in locals():
                navegador.quit()

        # Opcional: Gera um arquivo consolidado ao final
        escrever_arquivo_erros(erros_global)

    except Exception as e:
        logging.error(f"Erro na inicialização: {str(e)}")
'''