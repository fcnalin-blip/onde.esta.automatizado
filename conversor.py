import json
import re
import os
import time
import hashlib
import urllib.request
import urllib.parse
from datetime import datetime

# ---------------- CONFIGURAÇÃO ----------------
BASE = os.environ.get("IPTV_BASE", "http://hightechtvr1.online")
USER = "97533635"
PASS = "57989443"
# ----------------------------------------------

URL_M3U = f"{BASE}/get.php?username={USER}&password={PASS}&type=m3u_plus&output=ts"
HEADERS = {'User-Agent': 'Mozilla/5.0'}
padrao_ep = re.compile(r'\s*(?:-\s*)?S\d+(?:E\d+)?.*$', re.IGNORECASE)

print("========================================")
print("      IPTV SYNC & COMPARISON (API)      ")
print("========================================")


# 1. Carregar catálogo antigo (se existir) para comparar depois
catalogo_antigo_nomes = set()
contagem_antiga = {}   # títulos únicos por tipo (FILMES, SÉRIES, CANAIS)
if os.path.exists("data.js"):
    try:
        with open("data.js", "r", encoding="utf-8") as f:
            conteudo_atual = f.read()
        texto_json = conteudo_atual.split("const CATALOG_DATA =", 1)[1].strip().rstrip(";")
        for item in json.loads(texto_json):
            catalogo_antigo_nomes.add(f"{item['t']} ({item['cat']})")
        for nome in catalogo_antigo_nomes:
            tipo = nome.rsplit("(", 1)[1].rstrip(")")
            contagem_antiga[tipo] = contagem_antiga.get(tipo, 0) + 1
    except Exception as e:
        print(f"[AVISO] Não foi possível ler o data.js anterior: {e}")


# 2. Obter os registros: (nome bruto, categoria maior, grupo)
def pedir_api(action, tentativas=3):
    params = {"username": USER, "password": PASS, "action": action}
    url = f"{BASE}/player_api.php?" + urllib.parse.urlencode(params)
    ultimo_erro = None
    for n in range(1, tentativas + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=300) as resp:
                dados = json.loads(resp.read().decode("utf-8"))
            if not isinstance(dados, list):
                raise ValueError("resposta não é uma lista (login recusado?)")
            return dados
        except Exception as e:
            ultimo_erro = e
            print(f"      [tentativa {n}/{tentativas}] {action}: {e}")
            time.sleep(5)
    raise RuntimeError(f"{action} falhou: {ultimo_erro}")


def registros_da_api():
    fontes = [
        ("FILMES", "get_vod_categories", "get_vod_streams"),
        ("SÉRIES", "get_series_categories", "get_series"),
        ("CANAIS", "get_live_categories", "get_live_streams"),
    ]
    registros = []
    for cat_maior, acao_cat, acao_itens in fontes:
        print(f"      - {cat_maior}...")
        cats = {str(c.get("category_id")): (c.get("category_name") or "Geral")
                for c in pedir_api(acao_cat)}
        itens = pedir_api(acao_itens)
        print(f"        {len(cats)} categorias, {len(itens)} itens")
        for it in itens:
            nome = (it.get("name") or "").strip()
            if not nome:
                continue
            ids = it.get("category_ids")
            if not (isinstance(ids, list) and ids):
                ids = [it.get("category_id")]
            for cid in ids:
                registros.append((nome, cat_maior, cats.get(str(cid), "Geral")))
    return registros


def registros_do_m3u():
    req = urllib.request.Request(URL_M3U, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=300) as resp:
        conteudo = resp.read().decode("utf-8")
    linhas = conteudo.splitlines()
    registros = []
    for i in range(len(linhas)):
        linha = linhas[i].strip()
        if not linha.startswith('#EXTINF:'):
            continue
        categoria = "Geral"
        if 'group-title="' in linha:
            categoria = linha.split('group-title="')[1].split('"')[0]
        titulo_bruto = linha.rsplit(',', 1)[1].strip()
        link = linhas[i + 1].strip() if (i + 1) < len(linhas) else ""
        if "/movie/" in link:
            cat_maior = "FILMES"
        elif "/series/" in link:
            cat_maior = "SÉRIES"
        else:
            cat_maior = "CANAIS"
        registros.append((titulo_bruto, cat_maior, categoria))
    return registros


print("\n[1/3] Baixando o catálogo...")
fonte = "API"
try:
    registros = registros_da_api()
except Exception as e_api:
    print(f"[AVISO] A API falhou ({e_api}). Tentando o M3U como plano B...")
    fonte = "M3U"
    try:
        registros = registros_do_m3u()
    except Exception as e_m3u:
        print(f"[ERRO] O M3U também falhou: {e_m3u}")
        exit(1)
print(f"      [OK] Fonte usada: {fonte} ({len(registros)} registros)")


# 3. Limpar e remover duplicatas
print("[2/3] Processando e limpando o catálogo...")
catalogo = []
vistos = set()
catalogo_novo_nomes = set()

for titulo_bruto, cat_maior, categoria in registros:
    titulo_limpo = padrao_ep.sub('', titulo_bruto).strip()
    chave_unica = f"{titulo_limpo}|{categoria}|{cat_maior}"
    if chave_unica in vistos:
        continue
    vistos.add(chave_unica)
    catalogo.append({"t": titulo_limpo, "cat": cat_maior, "tp": categoria})
    catalogo_novo_nomes.add(f"{titulo_limpo} ({cat_maior})")

# Segurança: não sobrescreve se vier vazio ou muito menor que o anterior
if len(catalogo) == 0:
    print("[ERRO] Nenhum item encontrado. O data.js não foi alterado.")
    exit(1)
contagem_nova = {}
for nome in catalogo_novo_nomes:
    tipo = nome.rsplit("(", 1)[1].rstrip(")")
    contagem_nova[tipo] = contagem_nova.get(tipo, 0) + 1
for tipo, antiga in contagem_antiga.items():
    nova = contagem_nova.get(tipo, 0)
    if nova < 0.5 * antiga:
        print(f"[ERRO] {tipo}: o catálogo novo tem {nova} títulos e o anterior tinha {antiga}. "
              f"Parece resposta incompleta. O data.js não foi alterado.")
        exit(1)

# 4. Gravar o data.js (com a data na primeira linha)
data_hoje = datetime.now().strftime("%d/%m/%Y")
conteudo_js = (
    f'const CATALOG_UPDATED = "{data_hoje}";\n'
    f"const CATALOG_DATA = {json.dumps(catalogo, ensure_ascii=False, indent=2)};"
)
with open('data.js', 'w', encoding='utf-8', newline='\n') as arquivo_saida:
    arquivo_saida.write(conteudo_js)
print(f"      [OK] {len(catalogo)} itens processados. Atualizado em {data_hoje}.")

# 5. Atualizar a versão do data.js dentro do index.html (evita cache antigo)
if os.path.exists("index.html"):
    versao = hashlib.md5(conteudo_js.encode("utf-8")).hexdigest()[:8]
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
    novo_html = re.sub(r'data\.js(\?v=\w+)?"', f'data.js?v={versao}"', html, count=1)
    if novo_html != html:
        with open("index.html", "w", encoding="utf-8", newline='\n') as f:
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
print(f"   CONCLUÍDO! (fonte: {fonte})")
print("========================================")
