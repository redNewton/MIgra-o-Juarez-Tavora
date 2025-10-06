import requests
from bs4 import BeautifulSoup
import os
import json
from urllib.parse import urljoin

# URL base
base_url = 'https://www.juareztavora.pb.gov.br'

# Criar pasta principal "Licitações"
pasta_principal = 'Licitações'
os.makedirs(pasta_principal, exist_ok=True)

# Percorrer as páginas de 63 até 1 (começando pela mais recente)
for page_number in range(63, 0, -1):  # 63, 62, 61, ..., 1
    print(f"\nAcessando página {page_number}...")

    url = f'{base_url}/licitacoes?page={page_number}'

    # Criar pasta da página DENTRO da pasta principal
    pagina_dir = os.path.join(pasta_principal, f'Pagina{page_number}')
    os.makedirs(pagina_dir, exist_ok=True)

    # Acessar a página de listagem
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Erro ao acessar a página {page_number}: {response.status_code}")
        continue  # Ir para a próxima página

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Encontrar todos os botões "Detalhes" que levam às licitações
    detail_buttons = soup.find_all('a', class_='tm-execute btn btn-licitacao d-block w-100 d-sm-inline-block')

    if not detail_buttons:
        print(f"Nenhuma licitação encontrada na página {page_number}.")
        continue

    for idx, button in enumerate(detail_buttons, start=1):
        # Extrair link da licitação
        licitacao_url = button.get('href')
        if not licitacao_url:
            continue
            
        if licitacao_url.startswith('/'):
            licitacao_url = urljoin(base_url, licitacao_url)

        # Criar pasta da licitação DENTRO da pasta da página
        licitacao_dir = os.path.join(pagina_dir, f'licitacao{idx}')
        os.makedirs(licitacao_dir, exist_ok=True)

        # Acessar a página da licitação
        licitacao_response = requests.get(licitacao_url)
        if licitacao_response.status_code != 200:
            print(f"Erro ao acessar licitação: {licitacao_url}")
            continue

        licitacao_soup = BeautifulSoup(licitacao_response.text, 'html.parser')

        # Extrair dados da licitação
        modalidade = ''
        situacao = ''
        numero_licitacao = ''
        publicacao = ''
        unidade_gestora = ''
        realizacao = ''
        codigo_unidade_gestora = ''
        objetivo = ''

        # Modalidade
        modalidade_elem = licitacao_soup.find('p', itemprop='bidModality')
        if modalidade_elem:
            modalidade = modalidade_elem.get_text(strip=True)

        # Situação
        situacao_div = licitacao_soup.find('div', class_='informacoes').find_next_sibling('div')
        if situacao_div:
            situacao_p = situacao_div.find('p', class_='text-muted')
            if situacao_p:
                situacao = situacao_p.get_text(strip=True)

        # Número da Licitação
        numero_elem = licitacao_soup.find('p', itemprop='bidID')
        if numero_elem:
            numero_licitacao = numero_elem.get_text(strip=True)

        # Publicação
        publicacao_elem = licitacao_soup.find('p', itemprop='publicationDate')
        if publicacao_elem:
            publicacao = publicacao_elem.get_text(strip=True)

        # Unidade Gestora
        unidade_gestora_elem = licitacao_soup.find('p', itemprop='managementUnitName')
        if unidade_gestora_elem:
            unidade_gestora = unidade_gestora_elem.get_text(strip=True)

        # Realização
        realizacao_elem = licitacao_soup.find('p', itemprop='realizationDate')
        if realizacao_elem:
            realizacao = realizacao_elem.get_text(strip=True)

        # Código da Unidade Gestora
        codigo_unidade_elem = licitacao_soup.find('p', itemprop='managementUnitID')
        if codigo_unidade_elem:
            codigo_unidade_gestora = codigo_unidade_elem.get_text(strip=True)

        # Objetivo
        objetivo_elem = licitacao_soup.find('p', itemprop='object')
        if objetivo_elem:
            objetivo = objetivo_elem.get_text(strip=True)

        # Extrair documentos da licitação
        documentos = []
        documentos_table = licitacao_soup.find('h5', string='Documentos da Licitação:')
        if documentos_table:
            documentos_table = documentos_table.find_next('table')
            if documentos_table:
                rows = documentos_table.find_all('tr')[1:]  # Pular o cabeçalho
                for row_idx, row in enumerate(rows, start=1):
                    cells = row.find_all(['th', 'td'])
                    if len(cells) >= 3:
                        # Tipo do documento
                        tipo_elem = cells[0]
                        tipo = tipo_elem.get_text(strip=True) if tipo_elem else ''
                        
                        # Nome do documento
                        nome_elem = cells[1].find('h5')
                        nome = nome_elem.get_text(strip=True) if nome_elem else ''
                        
                        # Link de download
                        link_elem = cells[2].find('a', download=True)
                        link = link_elem.get('href') if link_elem else ''
                        
                        # Nome do arquivo
                        arquivo = os.path.basename(link) if link else ''
                        
                        if tipo and link:
                            # Baixar o arquivo PDF
                            try:
                                pdf_response = requests.get(link)
                                if pdf_response.status_code == 200:
                                    # Criar nome seguro para o arquivo
                                    nome_arquivo_seguro = f"documento{row_idx}_{arquivo}"
                                    caminho_arquivo = os.path.join(licitacao_dir, nome_arquivo_seguro)
                                    
                                    with open(caminho_arquivo, 'wb') as f:
                                        f.write(pdf_response.content)
                                    
                                    print(f"    📄 Baixado: {nome_arquivo_seguro}")
                                else:
                                    print(f"    ⚠️ Erro ao baixar: {arquivo}")
                                    nome_arquivo_seguro = ""
                            except Exception as e:
                                print(f"    ❌ Erro no download: {e}")
                                nome_arquivo_seguro = ""

                            documento = {
                                "Tipo": tipo,
                                "Nome": nome,
                                "Link": link,
                                "Arquivo": arquivo,
                                "ArquivoSalvo": nome_arquivo_seguro
                            }
                            documentos.append(documento)

        # Salvar JSON
        data = {
            "Modalidade": modalidade,
            "Situação": situacao,
            "Número da Licitação": numero_licitacao,
            "Publicação": publicacao,
            "Unidade Gestora": unidade_gestora,
            "Realização": realizacao,
            "Código da Unidade Gestora": codigo_unidade_gestora,
            "Objetivo": objetivo,
            "Link": licitacao_url,
            "Documentos": documentos
        }

        json_path = os.path.join(licitacao_dir, 'dados.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Licitação {idx} salva em: {licitacao_dir}")
        print(f"  Número: {numero_licitacao}")
        print(f"  Modalidade: {modalidade}")
        print(f"  Situação: {situacao}")
        print(f"  Documentos baixados: {len([d for d in documentos if d['ArquivoSalvo']])}/{len(documentos)}")

print(f"\nProcesso concluído! Todas as licitações foram salvas na pasta '{pasta_principal}'")


'''
import requests
from bs4 import BeautifulSoup
import os
import json
from urllib.parse import urljoin

# URL base
base_url = 'https://www.juareztavora.pb.gov.br'

# Criar pasta principal "Licitações"
pasta_principal = 'Licitações'
os.makedirs(pasta_principal, exist_ok=True)

# Percorrer as páginas de 63 até 1 (começando pela mais recente)
for page_number in range(63, 0, -1):  # 63, 62, 61, ..., 1
    print(f"\nAcessando página {page_number}...")

    url = f'{base_url}/licitacoes?page={page_number}'

    # Criar pasta da página DENTRO da pasta principal
    pagina_dir = os.path.join(pasta_principal, f'Pagina{page_number}')
    os.makedirs(pagina_dir, exist_ok=True)

    # Acessar a página de listagem
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Erro ao acessar a página {page_number}: {response.status_code}")
        continue  # Ir para a próxima página

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Encontrar todos os botões "Detalhes" que levam às licitações
    detail_buttons = soup.find_all('a', class_='tm-execute btn btn-licitacao d-block w-100 d-sm-inline-block')

    if not detail_buttons:
        print(f"Nenhuma licitação encontrada na página {page_number}.")
        continue

    for idx, button in enumerate(detail_buttons, start=1):
        # Extrair link da licitação
        licitacao_url = button.get('href')
        if not licitacao_url:
            continue
            
        if licitacao_url.startswith('/'):
            licitacao_url = urljoin(base_url, licitacao_url)

        # Criar pasta da licitação DENTRO da pasta da página
        licitacao_dir = os.path.join(pagina_dir, f'licitacao{idx}')
        os.makedirs(licitacao_dir, exist_ok=True)

        # Acessar a página da licitação
        licitacao_response = requests.get(licitacao_url)
        if licitacao_response.status_code != 200:
            print(f"Erro ao acessar licitação: {licitacao_url}")
            continue

        licitacao_soup = BeautifulSoup(licitacao_response.text, 'html.parser')

        # Extrair dados da licitação
        modalidade = ''
        situacao = ''
        numero_licitacao = ''
        publicacao = ''
        unidade_gestora = ''
        realizacao = ''
        codigo_unidade_gestora = ''
        objetivo = ''

        # Modalidade
        modalidade_elem = licitacao_soup.find('p', itemprop='bidModality')
        if modalidade_elem:
            modalidade = modalidade_elem.get_text(strip=True)

        # Situação
        situacao_div = licitacao_soup.find('div', class_='informacoes').find_next_sibling('div')
        if situacao_div:
            situacao_p = situacao_div.find('p', class_='text-muted')
            if situacao_p:
                situacao = situacao_p.get_text(strip=True)

        # Número da Licitação
        numero_elem = licitacao_soup.find('p', itemprop='bidID')
        if numero_elem:
            numero_licitacao = numero_elem.get_text(strip=True)

        # Publicação
        publicacao_elem = licitacao_soup.find('p', itemprop='publicationDate')
        if publicacao_elem:
            publicacao = publicacao_elem.get_text(strip=True)

        # Unidade Gestora
        unidade_gestora_elem = licitacao_soup.find('p', itemprop='managementUnitName')
        if unidade_gestora_elem:
            unidade_gestora = unidade_gestora_elem.get_text(strip=True)

        # Realização
        realizacao_elem = licitacao_soup.find('p', itemprop='realizationDate')
        if realizacao_elem:
            realizacao = realizacao_elem.get_text(strip=True)

        # Código da Unidade Gestora
        codigo_unidade_elem = licitacao_soup.find('p', itemprop='managementUnitID')
        if codigo_unidade_elem:
            codigo_unidade_gestora = codigo_unidade_elem.get_text(strip=True)

        # Objetivo
        objetivo_elem = licitacao_soup.find('p', itemprop='object')
        if objetivo_elem:
            objetivo = objetivo_elem.get_text(strip=True)

        # Extrair documentos da licitação
        documentos = []
        documentos_table = licitacao_soup.find('h5', string='Documentos da Licitação:')
        if documentos_table:
            documentos_table = documentos_table.find_next('table')
            if documentos_table:
                rows = documentos_table.find_all('tr')[1:]  # Pular o cabeçalho
                for row in rows:
                    cells = row.find_all(['th', 'td'])
                    if len(cells) >= 3:
                        # Tipo do documento
                        tipo_elem = cells[0]
                        tipo = tipo_elem.get_text(strip=True) if tipo_elem else ''
                        
                        # Nome do documento
                        nome_elem = cells[1].find('h5')
                        nome = nome_elem.get_text(strip=True) if nome_elem else ''
                        
                        # Link de download
                        link_elem = cells[2].find('a', download=True)
                        link = link_elem.get('href') if link_elem else ''
                        
                        # Nome do arquivo
                        arquivo = os.path.basename(link) if link else ''
                        
                        if tipo and link:
                            documento = {
                                "Tipo": tipo,
                                "Nome": nome,
                                "Link": link,
                                "Arquivo": arquivo
                            }
                            documentos.append(documento)

        # Salvar JSON
        data = {
            "Modalidade": modalidade,
            "Situação": situacao,
            "Número da Licitação": numero_licitacao,
            "Publicação": publicacao,
            "Unidade Gestora": unidade_gestora,
            "Realização": realizacao,
            "Código da Unidade Gestora": codigo_unidade_gestora,
            "Objetivo": objetivo,
            "Link": licitacao_url,
            "Documentos": documentos
        }

        json_path = os.path.join(licitacao_dir, 'dados.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Licitação {idx} salva em: {licitacao_dir}")
        print(f"  Número: {numero_licitacao}")
        print(f"  Modalidade: {modalidade}")
        print(f"  Situação: {situacao}")
        print(f"  Documentos encontrados: {len(documentos)}")

print(f"\nProcesso concluído! Todas as licitações foram salvas na pasta '{pasta_principal}'")
'''




'''
import requests
from bs4 import BeautifulSoup
import os
import json
from urllib.parse import urljoin

# URL base
base_url = 'https://www.juareztavora.pb.gov.br'

# Criar pasta principal "Licitações"
pasta_principal = 'Licitações'
os.makedirs(pasta_principal, exist_ok=True)

# Percorrer as páginas de 63 até 1 (começando pela mais recente)
for page_number in range(63, 0, -1):  # 63, 62, 61, ..., 1
    print(f"\nAcessando página {page_number}...")

    url = f'{base_url}/licitacoes?page={page_number}'

    # Criar pasta da página DENTRO da pasta principal
    pagina_dir = os.path.join(pasta_principal, f'Pagina{page_number}')
    os.makedirs(pagina_dir, exist_ok=True)

    # Acessar a página de listagem
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Erro ao acessar a página {page_number}: {response.status_code}")
        continue  # Ir para a próxima página

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Encontrar todos os botões "Detalhes" que levam às licitações
    detail_buttons = soup.find_all('a', class_='tm-execute btn btn-licitacao d-block w-100 d-sm-inline-block')

    if not detail_buttons:
        print(f"Nenhuma licitação encontrada na página {page_number}.")
        continue

    for idx, button in enumerate(detail_buttons, start=1):
        # Extrair link da licitação
        licitacao_url = button.get('href')
        if not licitacao_url:
            continue
            
        if licitacao_url.startswith('/'):
            licitacao_url = urljoin(base_url, licitacao_url)

        # Criar pasta da licitação DENTRO da pasta da página
        licitacao_dir = os.path.join(pagina_dir, f'licitacao{idx}')
        os.makedirs(licitacao_dir, exist_ok=True)

        # Acessar a página da licitação
        licitacao_response = requests.get(licitacao_url)
        if licitacao_response.status_code != 200:
            print(f"Erro ao acessar licitação: {licitacao_url}")
            continue

        licitacao_soup = BeautifulSoup(licitacao_response.text, 'html.parser')

        # Extrair dados da licitação
        modalidade = ''
        situacao = ''
        numero_licitacao = ''
        publicacao = ''
        unidade_gestora = ''
        realizacao = ''
        codigo_unidade_gestora = ''
        objetivo = ''

        # Modalidade
        modalidade_elem = licitacao_soup.find('p', itemprop='bidModality')
        if modalidade_elem:
            modalidade = modalidade_elem.get_text(strip=True)

        # Situação
        situacao_div = licitacao_soup.find('div', class_='informacoes').find_next_sibling('div')
        if situacao_div:
            situacao_p = situacao_div.find('p', class_='text-muted')
            if situacao_p:
                situacao = situacao_p.get_text(strip=True)

        # Número da Licitação
        numero_elem = licitacao_soup.find('p', itemprop='bidID')
        if numero_elem:
            numero_licitacao = numero_elem.get_text(strip=True)

        # Publicação
        publicacao_elem = licitacao_soup.find('p', itemprop='publicationDate')
        if publicacao_elem:
            publicacao = publicacao_elem.get_text(strip=True)

        # Unidade Gestora
        unidade_gestora_elem = licitacao_soup.find('p', itemprop='managementUnitName')
        if unidade_gestora_elem:
            unidade_gestora = unidade_gestora_elem.get_text(strip=True)

        # Realização
        realizacao_elem = licitacao_soup.find('p', itemprop='realizationDate')
        if realizacao_elem:
            realizacao = realizacao_elem.get_text(strip=True)

        # Código da Unidade Gestora
        codigo_unidade_elem = licitacao_soup.find('p', itemprop='managementUnitID')
        if codigo_unidade_elem:
            codigo_unidade_gestora = codigo_unidade_elem.get_text(strip=True)

        # Objetivo
        objetivo_elem = licitacao_soup.find('p', itemprop='object')
        if objetivo_elem:
            objetivo = objetivo_elem.get_text(strip=True)

        # Salvar JSON
        data = {
            "Modalidade": modalidade,
            "Situação": situacao,
            "Número da Licitação": numero_licitacao,
            "Publicação": publicacao,
            "Unidade Gestora": unidade_gestora,
            "Realização": realizacao,
            "Código da Unidade Gestora": codigo_unidade_gestora,
            "Objetivo": objetivo,
            "Link": licitacao_url
        }

        json_path = os.path.join(licitacao_dir, 'dados.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Licitação {idx} salva em: {licitacao_dir}")
        print(f"  Número: {numero_licitacao}")
        print(f"  Modalidade: {modalidade}")
        print(f"  Situação: {situacao}")

print(f"\nProcesso concluído! Todas as licitações foram salvas na pasta '{pasta_principal}'")
'''