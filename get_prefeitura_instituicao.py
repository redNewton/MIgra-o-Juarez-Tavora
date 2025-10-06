import requests
from bs4 import BeautifulSoup
import base64
import os

def coletar_dados_prefeitura():
    url = "https://www.juareztavora.pb.gov.br/instituicao"
    
    try:
        # Fazer requisição à página
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse do HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Encontrar o elemento container principal
        container = soup.find('div', class_='container p-4')
        
        if not container:
            print("Elemento container não encontrado!")
            return None
        
        # Coletar todo o texto do container
        texto_completo = container.get_text(separator='\n', strip=True)
        
        # Encontrar a imagem
        imagem_element = container.find('img')
        imagem_data = None
        formato_imagem = None
        
        if imagem_element and 'src' in imagem_element.attrs:
            src = imagem_element['src']
            
            # Verificar se é uma imagem em base64
            if src.startswith('data:image/'):
                # Extrair dados base64
                header, data = src.split(',', 1)
                formato_imagem = header.split('/')[1].split(';')[0]
                imagem_data = base64.b64decode(data)
        
        # Criar pasta prefeitura_instituicao se não existir
        pasta = "prefeitura_instituicao"
        if not os.path.exists(pasta):
            os.makedirs(pasta)
            print(f"Pasta '{pasta}' criada!")
        
        # Salvar o texto na pasta prefeitura_instituicao
        arquivo_texto = os.path.join(pasta, "texto_completo.txt")
        with open(arquivo_texto, 'w', encoding='utf-8') as f:
            f.write(texto_completo)
        
        # Salvar a imagem na pasta prefeitura_instituicao se existir
        if imagem_data and formato_imagem:
            arquivo_imagem = os.path.join(pasta, f"imagem_historia.{formato_imagem}")
            with open(arquivo_imagem, 'wb') as f:
                f.write(imagem_data)
        
        print(f"✓ Dados salvos na pasta '{pasta}':")
        print(f"  - Texto completo: {arquivo_texto}")
        if imagem_data:
            print(f"  - Imagem: {arquivo_imagem}")
        else:
            print(f"  - Imagem: Não foi possível baixar a imagem")
        
        return {
            'texto': texto_completo,
            'imagem_data': imagem_data,
            'formato_imagem': formato_imagem
        }
        
    except requests.RequestException as e:
        print(f"Erro ao acessar a página: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return None

# Executar o script
if __name__ == "__main__":
    print("Coletando dados da prefeitura...")
    dados = coletar_dados_prefeitura()
    
    if dados:
        print("\n" + "="*60)
        print("COLETA CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print("Todos os arquivos foram salvos na pasta 'prefeitura_instituicao'")
    else:
        print("Falha na coleta dos dados.")