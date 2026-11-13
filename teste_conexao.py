import requests

# URL da sua lista M3U
url = "http://hightechtvr1.online/get.php?username=97533635&password=57989443&type=m3u_plus&output=ts"

# Cabeçalhos simulando um navegador moderno para evitar bloqueios por User-Agent
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("Tentando conectar ao servidor de IPTV...")

try:
    # Realiza a requisição com timeout de 30 segundos
    response = requests.get(url, headers=headers, timeout=30)
    
    # Verifica se o status HTTP foi bem-sucedido (200 OK)
    response.raise_for_status()
    
    # Salva o conteúdo em um arquivo de teste
    nome_arquivo = "teste_lista.m3u"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(response.text)
        
    print(f"Sucesso! Conexão estabelecida e arquivo '{nome_arquivo}' salvo.")
    print(f"Tamanho do conteúdo baixado: {len(response.text)} caracteres.")
    
    # Mostra as primeiras 3 linhas do arquivo para verificar se é um M3U válido
    linhas = response.text.strip().split("\n")
    print("\nPrimeiras linhas do arquivo baixado:")
    for i in range(min(3, len(linhas))):
        print(f"  {linhas[i]}")

except requests.exceptions.HTTPError as err:
    print(f"Erro HTTP ao tentar acessar a lista: {err}")
except requests.exceptions.ConnectionError:
    print("Erro de conexão: Verifique sua internet ou se o endereço do servidor está correto.")
except requests.exceptions.Timeout:
    print("O servidor demorou muito para responder (Timeout).")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
