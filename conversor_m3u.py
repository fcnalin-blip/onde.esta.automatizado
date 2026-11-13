import json
import re
import urllib.request
import os
import hashlib
from datetime import datetime

URL_M3U = "http://hightechtvr1.online/get.php?username=97533635&password=57989443&type=m3u_plus&output=ts"

print("========================================")
print("      IPTV SYNC & COMPARISON            ")
print("========================================")

# 1. Carregar catálogo antigo (se existir) para comparar depois
catalogo_antigo_nomes = set()
if os.path.exists("data.js"):
    try:
        with open("data.js", "r", encoding="utf-8") as f:
            conteudo_atual = f.read()
        texto_json = conteudo_atual.split("const CATALOG_DATA =", 1)[1].strip().rstrip(";")
        for item in json.loads(texto_json):
            catalogo_antigo_nomes.add(f"{item['t']} ({item['cat']})")
    except Exception as e:
        print(f"[AVISO] Não foi possível ler o data.js anterior: {e}")

# 2. Baixar a lista M3U nova
print("\n[1/3] Baixando a lista M3U atualizada...")
try:
    req = urllib.request.Request(URL_M3U, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=300) as resposta:
        conteudo_arquivo = resposta.read().decode('utf-8')
except Exception as e:
    print(f"[ERRO] Erro ao baixar a lista: {e}")
    exit(1)

# 3. Processar e limpar o novo catálogo
print("[2/3] Processando e limpando o catálogo...")
catalogo = []
vistos = set()
catalogo_novo_nomes = set()
padrao_ep = re.compile(r'\s*(?:-\s*)?S\d+(?:E\d+)?.*$', re.IGNORECASE)

linhas = conteudo_arquivo.splitlines()

for i in range(len(linhas)):
    linha = linhas[i].strip()

    if linha.startswith('#EXTINF:'):
        categoria = "Geral"
        if 'group-title="' in linha:
            categoria = linha.split('group-title="')[1].split('"')[0]

        titulo_bruto = linha.rsplit(',', 1)[1].strip()
        titulo_limpo = padrao_ep.sub('', titulo_bruto).strip()

        link = linhas[i+1].strip() if (i+1) < len(linhas) else ""

        if "/movie/" in link:
            cat_maior = "FILMES"
        elif "/series/" in link:
            cat_maior = "SÉRIES"
        else:
            cat_maior = "CANAIS"

        chave_unica = f"{titulo_limpo}|{categoria}"

        if chave_unica not in vistos:
            vistos.add(chave_unica)
            catalogo.append({
                "t": titulo_limpo,
                "cat": cat_maior,
                "tp": categoria
            })
            catalogo_novo_nomes.add(f"{titulo_limpo} ({cat_maior})")

# Segurança: se a lista veio vazia, não sobrescreve o data.js
if len(catalogo) == 0:
    print("[ERRO] Nenhum item encontrado. O data.js não foi alterado.")
    exit(1)

# 4. Gravar o data.js (com a data de atualização na primeira linha)
data_hoje = datetime.now().strftime("%d/%m/%Y")
conteudo_js = (
    f'const CATALOG_UPDATED = "{data_hoje}";\n'
    f"const CATALOG_DATA = {json.dumps(catalogo, ensure_ascii=False, indent=2)};"
)
with open('data.js', 'w', encoding='utf-8') as arquivo_saida:
    arquivo_saida.write(conteudo_js)

print(f"      [OK] {len(catalogo)} itens processados. Atualizado em {data_hoje}.")

# 5. Atualizar a versão do data.js dentro do index.html (evita cache antigo)
if os.path.exists("index.html"):
    versao = hashlib.md5(conteudo_js.encode("utf-8")).hexdigest()[:8]
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
    novo_html = re.sub(r'data\.js(\?v=\w+)?"', f'data.js?v={versao}"', html, count=1)
    if novo_html != html:
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(novo_html)
    print(f"      [OK] Versão do data.js no index.html: {versao}")
else:
    print("      [AVISO] index.html não encontrado nesta pasta.")

# 6. Relatório de alterações
print("\n[3/3] Relatório de mudanças")
print("========================================")

adicionados = sorted(catalogo_novo_nomes - catalogo_antigo_nomes)
removidos = sorted(catalogo_antigo_nomes - catalogo_novo_nomes)

print(f" [+] ADICIONADOS ({len(adicionados)}):")
for item in adicionados:
    print(f"    + {item}")

print(f"\n [-] REMOVIDOS ({len(removidos)}):")
for item in removidos:
    print(f"    - {item}")

print("========================================")
print("   CONCLUÍDO!")
print("========================================")
