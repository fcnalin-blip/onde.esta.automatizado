import json
import re
import urllib.request
import subprocess
import os

URL_M3U = "http://hightechtvr1.online/get.php?username=97533635&password=57989443&type=m3u_plus&output=ts"

print("========================================")
print("   IPTV SYNC, COMPARISON & GIT AUTO     ")
print("========================================")

# 1. Carregar catálogo antigo (se existir) para comparar depois
catalogo_antigo_nomes = set()
if os.path.exists("data.js"):
    try:
        with open("data.js", "r", encoding="utf-8") as f:
            conteudo_atual = f.read()
            match = re.search(r'const CATALOG_DATA = (\[.*?\]);', conteudo_atual, re.DOTALL)
            if match:
                dados_antigos = json.loads(match.group(1))
                for item in dados_antigos:
                    catalogo_antigo_nomes.add(f"{item['t']} ({item['cat']})")
    except Exception as e:
        print(f"[AVISO] Não foi possível ler o data.js anterior para comparação: {e}")

# 2. Baixar a lista M3U nova
print("\n[1/4] Baixando a lista M3U atualizada...")
try:
    req = urllib.request.Request(URL_M3U, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resposta:
        conteudo_arquivo = resposta.read().decode('utf-8')
except Exception as e:
    print(f"[ERRO] Erro ao baixar a lista: {e}")
    exit(1)

# 3. Processar e limpar o novo catálogo
print("[2/4] Processando e limpando o catálogo...")
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

# Salva o novo resultado no data.js
conteudo_js = f"const CATALOG_DATA = {json.dumps(catalogo, ensure_ascii=False, indent=2)};"
with open('data.js', 'w', encoding='utf-8') as arquivo_saida:
    arquivo_saida.write(conteudo_js)

print(f"      [OK] Sucesso! {len(catalogo)} itens processados.")

# 4. Relatório de Alterações (Completo, sem cortes)
print("\n[3/4] Analisando alteracoes na grade...")
print("========================================")
print("           RELATORIO DE MUDANCAS        ")
print("========================================")

adicionados = sorted(list(catalogo_novo_nomes - catalogo_antigo_nomes))
removidos = sorted(list(catalogo_antigo_nomes - catalogo_novo_nomes))

print(f" [+] ADICIONADOS RECENTEMENTE ({len(adicionados)} novos):")
if adicionados:
    for item in adicionados:
        print(f"    + {item}")
else:
    print("    Nenhum item novo.")

print(f"\n [-] REMOVIDOS DA LISTA ({len(removidos)} sairam):")
if removidos:
    for item in removidos:
        print(f"    - {item}")
else:
    print("    Nenhum item removido.")
print("========================================")

# 5. Envio automático para o GitHub
print("\n[4/4] Enviando atualizacao para o GitHub...")
try:
    subprocess.run(["git", "add", "data.js"], check=True)
    subprocess.run(["git", "commit", "-m", f"Atualizacao automatica: +{len(adicionados)} / -{len(removidos)}"], capture_output=True, text=True)
    subprocess.run(["git", "push"], check=True)
    print("      [OK] Upload concluido com sucesso no GitHub!")
except subprocess.CalledProcessError as e:
    print(f"      [AVISO/ERRO NO GIT]: O arquivo foi gerado localmente, mas o envio teve um detalhe: {e}")

print("\n========================================")
print("   PROCESSO CONCLUIDO COM SUCESSO!      ")
print("========================================")