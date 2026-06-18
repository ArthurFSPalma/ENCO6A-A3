"""
main.py — Orquestrador (Refatorado para Sprint 4).

Fluxo simplificado: 
    1. O usuário escolhe o arquivo CSV.
    2. O usuário informa uma data (DD-MM-YYYY).
    3. O usuário seleciona se o relatório é para Pesquisador ou Reporter.
    4. O sistema converte, filtra e gera a saída diretamente em um arquivo .txt.
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from pipeline import PipelinePesquisador, PipelineJornalista

# Garante saída em UTF-8 no terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def main() -> None:
    print("=" * 62)
    print("  ANALISADOR DE QUALIDADE DO AR — IQAr (CONAMA 491/2018)")
    print("=" * 62)

    try:
        # Passo 1: Caminho do Arquivo com loop de validação
        while True:
            caminho = input("Caminho do arquivo CSV (ex: PR2020.csv): ").strip()
            if not caminho:
                print("[ERRO] Caminho não pode ser vazio. Tente novamente.\n")
                continue
            
            caminho_bruto = Path(caminho)
            if not caminho_bruto.exists():
                # Tenta buscar na pasta 'dados'
                pasta_dados = Path(__file__).resolve().parent.parent / "dados"
                caminho_alternativo = pasta_dados / caminho
                if caminho_alternativo.exists():
                    caminho_bruto = caminho_alternativo
                    break
                else:
                    print(f"[ERRO] Arquivo '{caminho}' não encontrado. Tente novamente.\n")
                    continue
            break

        # Tenta extrair o ano do nome do arquivo (ex: PR2020.csv -> 2020) para validação
        ano_esperado = None
        match = re.search(r"(\d{4})", caminho_bruto.name)
        if match:
            ano_esperado = int(match.group(1))

        # Passo 2: Data Específica com loop de validação
        while True:
            data_entrada = input("Digite a data para análise (formato DD-MM-YYYY): ").strip()
            if not data_entrada:
                print("[ERRO] Data não pode ser vazia. Tente novamente.\n")
                continue
            
            try:
                # Valida se a data está no formato correto e existe no calendário
                data_obj = datetime.strptime(data_entrada, "%d-%m-%Y")
                
                # Garante que a data informada seja do mesmo ano do arquivo
                if ano_esperado and data_obj.year != ano_esperado:
                    print(f"[ERRO] O arquivo '{caminho_bruto.name}' contém dados de {ano_esperado}. O ano informado ({data_obj.year}) é inválido. Tente novamente.\n")
                    continue

                # Converte para o padrão interno (ISO YYYY-MM-DD) do sistema
                data = data_obj.strftime("%Y-%m-%d")
                break
            except ValueError:
                print("[ERRO] Data inválida ou fora do formato esperado (DD-MM-YYYY). Tente novamente.\n")

        # Passo 3: Escolha do Público com loop de validação
        while True:
            print("\nPara quem é este relatório?")
            print("  [1] Pesquisador")
            print("  [2] Reporter")
            opcao = input("Opção (1/2): ").strip()

            if opcao == "1":
                pipeline = PipelinePesquisador()
                nome_saida = f"relatorio_pesquisador_{data_entrada}.txt"
                break
            elif opcao == "2":
                pipeline = PipelineJornalista()
                nome_saida = f"relatorio_reporter_{data_entrada}.txt"
                break
            else:
                print("[ERRO] Opção inválida. Digite 1 ou 2.\n")

        # Caminho onde o txt será salvo (na pasta 'relatorios')
        pasta_relatorios = Path(__file__).resolve().parent.parent / "relatorios"
        pasta_relatorios.mkdir(exist_ok=True)
        caminho_saida = pasta_relatorios / nome_saida
        
        print("\nProcessando...")
        
        # Executa o Template Method do fluxo principal
        pipeline.executar(caminho_bruto=caminho_bruto, data=data, caminho_saida=caminho_saida)

    except KeyboardInterrupt:
        print("\n[AVISO] Operação cancelada pelo usuário.")
        sys.exit(0)
    except ValueError as erro:
        print(f"[ERRO] {erro}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERRO INESPERADO] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
