import pandas as pd
from pathlib import Path

# Caminho da pasta com os CSVs
input_dir = Path("data")

# Garante que a pasta existe
if not input_dir.exists() or not input_dir.is_dir():
    raise FileNotFoundError(f"Pasta '{input_dir}' não encontrada.")

# Encontra todos os arquivos CSV
csv_files = list(input_dir.glob("*.csv"))

if not csv_files:
    print("Nenhum arquivo CSV encontrado na pasta 'data'.")
else:
    for csv_file in csv_files:
        try:
            print(f"Convertendo {csv_file.name}...")
            df = pd.read_csv(csv_file)
            parquet_file = csv_file.with_suffix(".parquet")
            df.to_parquet(parquet_file, engine="pyarrow", index=False)
            print(f"✔️  Criado: {parquet_file.name}")
        except Exception as e:
            print(f"❌ Erro ao processar {csv_file.name}: {e}")
