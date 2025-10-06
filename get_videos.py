import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.juareztavora.pb.gov.br/videos?page={}"

def scrape_videos(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    videos = []
    video_divs = soup.find_all("div", class_="col-lg-3 mt-3")

    for div in video_divs:
        iframe = div.find("iframe")
        title_tag = div.find("p", style="color: #2c4964;")

        if iframe and title_tag:
            link = iframe["src"].strip()
            title = title_tag.get_text(strip=True)
            videos.append({
                "titulo": title,
                "link": link
            })

    return videos

def main():
    all_videos = []

    # Loop da página 10 até a 1
    for page in range(10, 0, -1):
        url = BASE_URL.format(page)
        print(f"🔎 Coletando vídeos da página {page}...")
        try:
            videos = scrape_videos(url)
            all_videos.extend(videos)
            print(f"   ✅ Encontrados {len(videos)} vídeos.")
        except Exception as e:
            print(f"   ⚠️ Erro na página {page}: {e}")
        time.sleep(1)  # Pausa leve para não sobrecarregar o servidor

    # Salvar em JSON
    with open("videos.json", "w", encoding="utf-8") as f:
        json.dump(all_videos, f, ensure_ascii=False, indent=4)

    print("\n📂 Coleta concluída!")
    print("Total de vídeos coletados:", len(all_videos))

if __name__ == "__main__":
    main()
