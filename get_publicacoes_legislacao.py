import os
import re
import json
import requests
from bs4 import BeautifulSoup
from time import sleep

BASE_URL = "https://www.juareztavora.pb.gov.br"
BASE_DIR = "publicacoes/legislacoes"
os.makedirs(BASE_DIR, exist_ok=True)

def sanitize_folder_name(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]', '_', name.strip())

def process_page(page_number: int):
    url = f"{BASE_URL}/legislacoes?page={page_number}"
    print(f"\n=== Página {page_number} ===")
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except Exception as e:
        print(f"[!] Erro ao acessar {url}: {e}")
        return

    soup = BeautifulSoup(resp.text, "html.parser")

    # Pega todos os títulos
    titulos = soup.find_all("h5", class_="text-md-left text-uppercase")

    if not titulos:
        print(f"[!] Nenhuma lei encontrada na página {page_number}")
        return

    for titulo_tag in titulos:
        titulo = titulo_tag.get_text(strip=True)
        print(f"Processando: {titulo}")

        # Pasta da lei
        folder_name = sanitize_folder_name(titulo)
        folder_path = os.path.join(BASE_DIR, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # Data
        li_data = titulo_tag.find_next("li", class_="mr-md-4 p-1")
        data_text = li_data.get_text(strip=True) if li_data else ""

        # Link de detalhes
        detalhes_div = titulo_tag.find_parent().find_next("div", class_="job-right my-4 flex-shrink-0")
        detalhes_url = detalhes_div.find("a")["href"] if detalhes_div else None

        descricao = ""
        pdf_filename = ""

        if detalhes_url:
            try:
                resp_det = requests.get(detalhes_url)
                resp_det.raise_for_status()
                soup_det = BeautifulSoup(resp_det.text, "html.parser")

                # Descrição
                desc_tag = soup_det.find("div", class_="mt-4")
                if desc_tag and desc_tag.find("p"):
                    descricao = desc_tag.find("p").get_text(strip=True)

                # PDF
                alert_div = soup_det.find("div", class_="alert alert-warning")
                if alert_div and alert_div.find("a"):
                    pdf_url = alert_div.find("a")["href"]
                    pdf_filename = os.path.basename(pdf_url)
                    pdf_path = os.path.join(folder_path, pdf_filename)

                    pdf_resp = requests.get(pdf_url)
                    if pdf_resp.status_code == 200:
                        with open(pdf_path, "wb") as f:
                            f.write(pdf_resp.content)
                        print(f"  [+] PDF salvo: {pdf_path}")
            except Exception as e:
                print(f"[!] Erro ao processar detalhes da lei {titulo}: {e}")

        # JSON
        data_json = {
            "titulo": titulo,
            "data": data_text,
            "descricao": descricao,
            "arquivo": pdf_filename
        }
        json_path = os.path.join(folder_path, "dados.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data_json, f, ensure_ascii=False, indent=4)

        print(f"  [+] JSON salvo: {json_path}")

    # Pausa curta para não sobrecarregar o servidor
    sleep(1)

# Loop da página 47 até a 1
for page in range(47, 0, -1):
    process_page(page)




'''
import os
import re
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.juareztavora.pb.gov.br"
LIST_URL = f"{BASE_URL}/legislacoes?page=47"

BASE_DIR = "publicacoes/legislacoes"
os.makedirs(BASE_DIR, exist_ok=True)

def sanitize_folder_name(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]', '_', name.strip())

# Baixa a página de listagem
resp = requests.get(LIST_URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# Pega todos os títulos
titulos = soup.find_all("h5", class_="text-md-left text-uppercase")

for titulo_tag in titulos:
    titulo = titulo_tag.get_text(strip=True)
    print(f"Processando: {titulo}")

    # Pasta da lei
    folder_name = sanitize_folder_name(titulo)
    folder_path = os.path.join(BASE_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Pegar a data (li logo depois do h5)
    li_data = titulo_tag.find_next("li", class_="mr-md-4 p-1")
    data_text = li_data.get_text(strip=True) if li_data else ""

    # Pegar o link de detalhes (div.job-right mais próxima)
    detalhes_div = titulo_tag.find_parent().find_next("div", class_="job-right my-4 flex-shrink-0")
    detalhes_url = detalhes_div.find("a")["href"] if detalhes_div else None

    descricao = ""
    pdf_filename = ""

    if detalhes_url:
        resp_det = requests.get(detalhes_url)
        resp_det.raise_for_status()
        soup_det = BeautifulSoup(resp_det.text, "html.parser")

        # Descrição
        desc_tag = soup_det.find("div", class_="mt-4")
        if desc_tag and desc_tag.find("p"):
            descricao = desc_tag.find("p").get_text(strip=True)

        # PDF
        alert_div = soup_det.find("div", class_="alert alert-warning")
        if alert_div and alert_div.find("a"):
            pdf_url = alert_div.find("a")["href"]
            pdf_filename = os.path.basename(pdf_url)
            pdf_path = os.path.join(folder_path, pdf_filename)

            pdf_resp = requests.get(pdf_url)
            if pdf_resp.status_code == 200:
                with open(pdf_path, "wb") as f:
                    f.write(pdf_resp.content)
                print(f"  [+] PDF salvo: {pdf_path}")

    # Salva JSON
    data_json = {
        "titulo": titulo,
        "data": data_text,
        "descricao": descricao,
        "arquivo": pdf_filename
    }
    json_path = os.path.join(folder_path, "dados.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data_json, f, ensure_ascii=False, indent=4)

    print(f"  [+] JSON salvo: {json_path}")
'''