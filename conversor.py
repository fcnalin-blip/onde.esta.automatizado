import json
import re
import urllib.request

URL_M3U = "http://hightechtvr1.online/get.php?username=97533635&password=57989443&type=m3u_plus&output=ts"

print("Baixando a lista M3U...")
try:
    req = urllib.request.Request(
        URL_M3U, 
        headers={'User-Agent': 'IPTV Smarters Pro'} # Fingindo ser o app
    )
    with urllib.request.urlopen(req) as resposta:
        conteudo_arquivo = resposta.read().decode('utf-8')
except Exception as e:
    print(f"Erro ao baixar a lista: {e}")
    exit(1)

catalogo = []
vistos = set()
padrao_ep = re.compile(r'\s*(?:-\s*)?S\d+(?:E\d+)?.*$', re.IGNORECASE)

linhas = conteudo_arquivo.splitlines()

# O pulo do gato: processamos o arquivo linha por linha
for i in range(len(linhas)):
    linha = linhas[i].strip()
    
    if linha.startswith('#EXTINF:'):
        # 1. Extrai Categoria (group-title)
        categoria = "Geral"
        if 'group-title="' in linha:
            categoria = linha.split('group-title="')[1].split('"')[0]
        
        # 2. Extrai Título
        titulo_bruto = linha.rsplit(',', 1)[1].strip()
        titulo_limpo = padrao_ep.sub('', titulo_bruto).strip()
        
        # 3. Pega o link na PRÓXIMA linha (i + 1) para classificar a categoria maior
        link = linhas[i+1].strip() if (i+1) < len(linhas) else ""
        
        if "/movie/" in link:
            cat_maior = "FILMES"
        elif "/series/" in link:
            cat_maior = "SÉRIES"
        else:
            cat_maior = "CANAIS"
            
        # 4. Evita duplicatas
        chave_unica = f"{titulo_limpo}|{categoria}"
        
        if chave_unica not in vistos:
            vistos.add(chave_unica)
            catalogo.append({
                "t": titulo_limpo,
                "cat": cat_maior, # Agora com a Categoria Maior
                "tp": categoria
            })

# Salva o resultado
conteudo_js = f"const CATALOG_DATA = {json.dumps(catalogo, ensure_ascii=False, indent=2)};"
with open('data.js', 'w', encoding='utf-8') as arquivo_saida:
    arquivo_saida.write(conteudo_js)

print(f"Sucesso! {len(catalogo)} itens processados.")
