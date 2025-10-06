import os
import requests
from bs4 import BeautifulSoup

# URL da página
url = "https://www.juareztavora.pb.gov.br/vice-prefeito"

# Pasta de saída
output_dir = "prefeitura_viceprefeito"
os.makedirs(output_dir, exist_ok=True)

# Requisição HTTP
response = requests.get(url)
response.raise_for_status()

# Parser HTML
soup = BeautifulSoup(response.text, "html.parser")

# ---- Coletar textos ----
texto_div = soup.find("div", class_="col-lg-6")
if texto_div:
    textos = texto_div.get_text(separator="\n", strip=True)
    
    # Salvar textos em arquivo
    with open(os.path.join(output_dir, "prefeito_texto.txt"), "w", encoding="utf-8") as f:
        f.write(textos)
    print("✅ Texto salvo em prefeito_texto.txt")
else:
    print("⚠️ Não foi possível encontrar o bloco de texto.")

# ---- Coletar imagem ----
img_div = soup.find("div", class_="about-img")
if img_div and img_div.img:
    img_url = img_div.img["src"]

    # Caso o link seja relativo, corrige
    if not img_url.startswith("http"):
        img_url = "https://www.juareztavora.pb.gov.br" + img_url

    img_response = requests.get(img_url)
    img_response.raise_for_status()

    # Nome do arquivo da imagem
    img_path = os.path.join(output_dir, "prefeito.jpg")
    with open(img_path, "wb") as f:
        f.write(img_response.content)

    print(f"✅ Imagem salva em {img_path}")
else:
    print("⚠️ Não foi possível encontrar a imagem do prefeito.")
