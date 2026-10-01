import hashlib
import json
import os 
import sys

BASELINE_FILE = "baseline.json"
MONITOR_DIR = r"CAMINHO\PASTA_MONITORADA"

def calcular_hash(caminho_arquivo):
  sha256 = hashlib.sha256()
  try:
    with open(caminho_arquivo, "rb") as f:
      while chunk := f.read(4096):
        sha256.update(chunk)
    return sha256.hexdigest()
  except FileNotFoundError:
    return None

def gerar_baseline():
  if not os.path.exists(MONITOR_DIR):
    os.makedirs(MONITOR_DIR)
    print(
        f"Diretório '{MONITOR_DIR}' criado. Adicione arquivos nele e inicie a baseline novamente."
    )
    return

  baseline = {}
  for raiz, _, arquivos in os.walk(MONITOR_DIR):
    for arquivo in arquivos:
      caminho_completo = os.path.join(raiz, arquivo)
      h = calcular_hash(caminho_completo)
      if h:
        baseline[caminho_completo] = h

  with open(BASELINE_FILE, "w") as f:
    json.dump(baseline, f, indent=4)
  print(
      f"Baseline gerada com sucesso! {len(baseline)} arquivos catalogados em"
      f" '{BASELINE_FILE}'."
  )

def verificar_integridade():
  if not os.path.exists(BASELINE_FILE):
    print("Baseline não encontrada. Execute 'python codigo.py init' primeiro ou reveja seu caminho.")
    return

  with open(BASELINE_FILE, "r") as f:
    baseline = json.load(f)

  arquivos_atuais = {}
  if os.path.exists(MONITOR_DIR):
    for raiz, _, arquivos in os.walk(MONITOR_DIR):
      for arquivo in arquivos:
        caminho_completo = os.path.join(raiz, arquivo)
        h = calcular_hash(caminho_completo)
        if h:
          arquivos_atuais[caminho_completo] = h

  alertas = 0

  for caminho, h_atual in arquivos_atuais.items():
    if caminho not in baseline:
      print(f"[ALERTA] Novo arquivo criado: {caminho}")
      alertas += 1
    elif baseline[caminho] != h_atual:
      print(f"[ALERTA] Arquivo modificado: {caminho}")
      alertas += 1

  for caminho in baseline:
    if caminho not in arquivos_atuais:
      print(f"[ALERTA] Arquivo apagado: {caminho}")
      alertas += 1

  if alertas == 0:
    print("Nenhuma alteração detectada. Todos os arquivos estão íntegros.")
  else:
    print(f"Verificação concluída. Total de alertas: {alertas}")

if __name__ == "__main__":
  if len(sys.argv) > 1 and sys.argv[1] == "init":
    gerar_baseline()
  else:
    verificar_integridade()