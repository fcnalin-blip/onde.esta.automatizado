import requests

url = "http://hightechtvr1.online/get.php?username=97533635&password=57989443&type=m3u_plus&output=ts"

# Cabeçalhos limpos sem caracteres especiais
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive"
}

print("Tentando conectar ao servidor de IPTV com cabeçalhos limpos...")

try:
    response = requests.get(url, headers=headers, timeout=45)
    response.raise_for_status()
    
    nome_arquivo = "teste_lista.m3u"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(response.text)
        
    print(f"Sucesso! Arquivo '{nome_arquivo}' salvo com sucesso.")
    print(f"Tamanho do conteúdo baixado: {len(response.text)} caracteres.")

except Exception as e:
    print(f"Ocorreu um erro: {e}")
