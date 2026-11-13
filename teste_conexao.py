import requests

url = "http://hightechtvr1.online/get.php?username=97533635&password=57989443&type=m3u_plus&output=ts"

# Headers idênticos aos de um player real
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

print("Tentando baixar a lista...")

try:
    # Caso queira testar com um proxy gratuito do Brasil (substitua IP:Porta se necessário)
    # proxies = {"http": "http://SEU_IP_PROXY:PORTA", "https": "http://SEU_IP_PROXY:PORTA"}
    
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    with open("teste_lista.m3u", "w", encoding="utf-8") as f:
        f.write(response.text)
        
    print("Sucesso! Lista salva.")

except Exception as e:
    print(f"Erro na requisição: {e}")
