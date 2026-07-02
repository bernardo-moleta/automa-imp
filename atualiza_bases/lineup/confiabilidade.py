import pandas as pd

def comparar_escalacao_siacesp(caminho_lineup, caminho_siacesp):
    # 1. Preparação dos dados: Carregamento das bases
    try:
        df_lineup = pd.read_excel(caminho_lineup)
        df_siacesp = pd.read_excel(caminho_siacesp)
    except FileNotFoundError as e:
        return f"Erro ao carregar arquivos: {e}"

    # Sanitização básica de colunas para garantir referências exatas
    df_lineup.columns = df_lineup.columns.str.strip()
    df_siacesp.columns = df_siacesp.columns.str.strip()

    # Conversão de colunas de data do Line Up para datetime
    df_lineup['DATA POSIÇÃO'] = pd.to_datetime(df_lineup['DATA POSIÇÃO'], errors='coerce')
    df_lineup['ETB'] = pd.to_datetime(df_lineup['ETB'], errors='coerce')

    # 2. Filtragem: Selecionar linhas onde a data da posição é 11 de junho de 2026
    data_alvo = pd.to_datetime('2026-06-11').date()
    df_lineup_filtrado = df_lineup[df_lineup['DATA POSIÇÃO'].dt.date == data_alvo]

    # 3. Agregação (Lista de Produtos): Isolar mês de maio pela coluna ETB
    df_lineup_maio = df_lineup_filtrado[df_lineup_filtrado['ETB'].dt.month == 5]
    
    # Agrupar dados por Produto ('Y_PRODUTO PARA') e somar as quantidades ('Qtty')
    lineup_agg = df_lineup_maio.groupby('Y_PRODUTO PARA', as_index=False)['Qtty'].sum()
    lineup_agg.rename(columns={'Qtty': 'Volume_LineUp'}, inplace=True)

    # 4. Agregação (SIACESP): Agrupar por produto e somar o Volume
    siacesp_agg = df_siacesp.groupby('Y_PRODUTO PARA', as_index=False)['VOLUME'].sum()
    siacesp_agg.rename(columns={'VOLUME': 'Volume_SIACESP'}, inplace=True)

    # 5. Comparação: Unir os dois dataframes agregados e substituir valores faltantes por 0
    df_comparacao = pd.merge(lineup_agg, siacesp_agg, on='Y_PRODUTO PARA', how='outer').fillna(0)

    # Calcular as discrepâncias entre as bases
    df_comparacao['Discrepancia'] = df_comparacao['Volume_LineUp'] - df_comparacao['Volume_SIACESP']

    # Organizar o resultado pelas maiores diferenças (em valores absolutos) para facilitar a análise
    df_resultado = df_comparacao.sort_values(by='Discrepancia', key=abs, ascending=False).reset_index(drop=True)

    return df_resultado

# Execução da função
if __name__ == "__main__":
    resultado_final = comparar_escalacao_siacesp('BI_Line Up_ORION.xlsx', 'siacesp.xlsx')
    print(resultado_final.to_string())