import requests

# URL da sua lista M3U
url = "http://hightechtvr1.online/get.php?username=97533635&password=57989443&type=m3u_plus&output=ts"

# Cabeçalhos robustos simulando um navegador real (evita bloqueios de datacenter/bot)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, бr",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

print("Tentando conectar ao servidor de IPTV com cabeçalhos simulados...")

try:
    # Usando session para manter os cookies e simular um fluxo de navegação real
    session = requests.Session()
    response = session.get(url, headers=headers, timeout=45)
    
    # Verifica se a resposta foi bem-sucedida
    response.raise_for_status()
    
    nome_arquivo = "teste_lista.m3u"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(response.text)
        
    print(f"Sucesso! Arquivo '{nome_arquivo}' salvo com sucesso.")
    print(f"Tamanho do conteúdo baixado: {len(response.text)} caracteres.")
    
    # Validação rápida das primeiras linhas
    linhas = response.text.strip().split("\n")
    print("\nPrimeiras linhas da lista:")
    for i in range(min(3, len(linhas))):
        print(f"  {linhas[i]}")

except requests.exceptions.HTTPError as err:
    print(f"Erro HTTP retornado pelo servidor: {err}")
except requests.exceptions.ConnectionError:
    print("Erro de conexão: Verifique a URL ou o acesso à rede.")
except requests.exceptions.Timeout:
    print("O servidor demorou muito para responder (Timeout excedido).")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
