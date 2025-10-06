import requests
from bs4 import BeautifulSoup
import os
import json
from urllib.parse import urljoin

# URL base
base_url = 'https://www.juareztavora.pb.gov.br'

# Percorrer as páginas de 97 até 1
for page_number in range(97, 0, -1):  # 97, 96, 95, ..., 1
    print(f"\nAcessando página {page_number}...")

    url = f'{base_url}/noticias?page={page_number}'

    # Criar pasta da página
    pagina_dir = f'pagina{page_number}'
    os.makedirs(pagina_dir, exist_ok=True)

    # Acessar a página de listagem
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Erro ao acessar a página {page_number}: {response.status_code}")
        continue  # Ir para a próxima página

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article', class_='d-flex flex-column')

    if not articles:
        print(f"Nenhuma notícia encontrada na página {page_number}.")
        continue

    for idx, article in enumerate(articles, start=1):
        # Extrair link da notícia
        title_elem = article.find('h2', class_='title').find('a')
        if not title_elem:
            continue
        noticia_url = title_elem.get('href')
        if noticia_url.startswith('/'):
            noticia_url = urljoin(base_url, noticia_url)

        # Criar pasta da notícia
        noticia_dir = os.path.join(pagina_dir, f'noticia{idx}')
        os.makedirs(noticia_dir, exist_ok=True)

        # Acessar a página da notícia
        noticia_response = requests.get(noticia_url)
        if noticia_response.status_code != 200:
            print(f"Erro ao acessar notícia: {noticia_url}")
            continue

        noticia_soup = BeautifulSoup(noticia_response.text, 'html.parser')

        # Extrair dados
        title = ''
        date = ''
        text = ''
        author = ''
        category = ''
        img_filename = ''

        # Título
        title_tag = noticia_soup.find('h2', class_='title')
        if title_tag:
            title = title_tag.get_text(strip=True)

        # Data
        time_tag = noticia_soup.find('time')
        if time_tag:
            date = time_tag.get_text(strip=True)

        # Texto (ajustado para capturar de ambas as formas)
        content_div = noticia_soup.find('div', class_='content')
        if content_div:
            text_elem = content_div.find('a')
            if text_elem:
                text = text_elem.get_text(strip=True)
            else:
                text = content_div.get_text(strip=True)

        # Autor
        cats_ul = noticia_soup.find('ul', class_='cats')
        if cats_ul:
            cat_li = cats_ul.find('li')
            if cat_li:
                author = cat_li.get_text(strip=True)

        # Categoria
        tags_ul = noticia_soup.find('ul', class_='tags')
        if tags_ul:
            tag_li = tags_ul.find('li')
            if tag_li:
                category = tag_li.get_text(strip=True)

        # Imagem
        img_tag = noticia_soup.find('div', class_='post-img')
        if img_tag:
            img_tag = img_tag.find('img')
            if img_tag:
                img_url = img_tag.get('src')
                if img_url:
                    img_url = img_url.strip()
                    if img_url.startswith('/'):
                        img_url = urljoin(base_url, img_url)
                    img_response = requests.get(img_url)
                    if img_response.status_code == 200:
                        img_filename = os.path.basename(img_url).strip()
                        img_path = os.path.join(noticia_dir, img_filename)
                        with open(img_path, 'wb') as f:
                            f.write(img_response.content)

        # Salvar JSON
        data = {
            "Titulo": title,
            "Data": date,
            "Texto": text,
            "Imagens": img_filename,
            "Categoria": category,
            "Autor": author,
            "Link": noticia_url
        }

        json_path = os.path.join(noticia_dir, 'dados.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Notícia {idx} salva em: {noticia_dir}")

print("\nProcesso concluído para todas as páginas.")

'''
import requests
from bs4 import BeautifulSoup
import os
import json
from urllib.parse import urljoin

# URL base
base_url = 'https://www.juareztavora.pb.gov.br'
page_number = 97
url = f'{base_url}/noticias?page={page_number}'

# Criar pasta da página
pagina_dir = f'pagina{page_number}'
os.makedirs(pagina_dir, exist_ok=True)

# Acessar a página de listagem
response = requests.get(url)
if response.status_code != 200:
    print(f"Erro ao acessar a página: {response.status_code}")
    exit()

soup = BeautifulSoup(response.text, 'html.parser')
articles = soup.find_all('article', class_='d-flex flex-column')

for idx, article in enumerate(articles, start=1):
    # Extrair link da notícia
    title_elem = article.find('h2', class_='title').find('a')
    if not title_elem:
        continue
    noticia_url = title_elem.get('href')
    if noticia_url.startswith('/'):
        noticia_url = urljoin(base_url, noticia_url)

    # Criar pasta da notícia
    noticia_dir = os.path.join(pagina_dir, f'noticia{idx}')
    os.makedirs(noticia_dir, exist_ok=True)

    # Acessar a página da notícia
    noticia_response = requests.get(noticia_url)
    if noticia_response.status_code != 200:
        print(f"Erro ao acessar notícia: {noticia_url}")
        continue

    noticia_soup = BeautifulSoup(noticia_response.text, 'html.parser')

    # Extrair dados
    title = ''
    date = ''
    text = ''
    author = ''
    category = ''
    img_filename = ''

    # Título
    title_tag = noticia_soup.find('h2', class_='title')
    if title_tag:
        title = title_tag.get_text(strip=True)

    # Data
    time_tag = noticia_soup.find('time')
    if time_tag:
        date = time_tag.get_text(strip=True)

    # Texto (ajustado para capturar de ambas as formas)
    content_div = noticia_soup.find('div', class_='content')
    if content_div:
        text_elem = content_div.find('a')
        if text_elem:
            text = text_elem.get_text(strip=True)
        else:
            text = content_div.get_text(strip=True)

    # Autor
    cats_ul = noticia_soup.find('ul', class_='cats')
    if cats_ul:
        cat_li = cats_ul.find('li')
        if cat_li:
            author = cat_li.get_text(strip=True)

    # Categoria
    tags_ul = noticia_soup.find('ul', class_='tags')
    if tags_ul:
        tag_li = tags_ul.find('li')
        if tag_li:
            category = tag_li.get_text(strip=True)

    # Imagem
    img_tag = noticia_soup.find('div', class_='post-img')
    if img_tag:
        img_tag = img_tag.find('img')
        if img_tag:
            img_url = img_tag.get('src')
            if img_url:
                img_url = img_url.strip()
                if img_url.startswith('/'):
                    img_url = urljoin(base_url, img_url)
                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    img_filename = os.path.basename(img_url).strip()
                    img_path = os.path.join(noticia_dir, img_filename)
                    with open(img_path, 'wb') as f:
                        f.write(img_response.content)

    # Salvar JSON
    data = {
        "Titulo": title,
        "Data": date,
        "Texto": text,
        "Imagens": img_filename,
        "Categoria": category,
        "Autor": author,
        "Link": noticia_url
    }

    json_path = os.path.join(noticia_dir, 'dados.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Notícia {idx} salva em: {noticia_dir}")

print("Processo concluído.")
'''

"""
import requests
from bs4 import BeautifulSoup

# URL da página que você quer acessar
url = 'https://www.juareztavora.pb.gov.br/noticias?page=97'

# Fazendo a requisição HTTP
response = requests.get(url)

# Verificando se a requisição foi bem-sucedida
if response.status_code == 200:
    # Parseando o conteúdo HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Procurando todos os artigos com a classe específica
    articles = soup.find_all('article', class_='d-flex flex-column')

    # Iterando sobre os artigos e extraindo os links
    for article in articles:
        # Procurando o link dentro do título (h2 > a)
        title_link = article.find('h2', class_='title').find('a')
        if title_link:
            link = title_link.get('href')
            print(link)
else:
    print(f"Erro ao acessar a página: {response.status_code}")
"""