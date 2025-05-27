import os
import pandas as pd

def is_demographics_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        return "Vecums" in first_line and "Stimuls" not in first_line

def is_test_file(filepath, keyword):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines[:5]:
            if keyword.lower() in line.lower():
                return True
    return False

def read_test_data_safe(filepath, test_type):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    header_index = next((i for i, line in enumerate(lines) if "Stimuls" in line), None)
    if header_index is None:
        return None
    data_header = lines[header_index].split(",")
    data_rows = [line.split(",") for line in lines[header_index + 1:] if len(line.split(",")) == len(data_header)]
    df = pd.DataFrame(data_rows, columns=data_header)
    df['Globāls'] = df['Globāls'].str.lower() == 'true'
    df['Lokāls'] = df['Lokāls'].str.lower() == 'true'
    df['Pareizi'] = df['Pareizi'].str.lower() == 'true'
    df['Reakcijas_laiks_ms'] = pd.to_numeric(df['Reakcijas_laiks_ms'], errors='coerce')

    id_val = lines[1].split(",")[0].zfill(6)

    if test_type == 'figūras':
        try:
            test_order = int(lines[1].split(",")[2])
        except:
            test_order = 1
    else:
        test_order = 2
        for line in lines[:5]:
            parts = line.split(",")
            try:
                maybe = int(parts[1])
                test_order = maybe
                break
            except:
                continue

    summary = {
        'ID': id_val,
        f'Tests_1' if test_type == 'figūras' else 'Tests_2': test_type,
        f'Testa_kārta_1' if test_type == 'figūras' else 'Testa_kārta_2': test_order,
        f'Globāls_Vid_Reakcija_1' if test_type == 'figūras' else 'Globāls_Vid_Reakcija_2': df[df['Globāls']]['Reakcijas_laiks_ms'].mean(),
        f'Globāls_Pareizi_%_1' if test_type == 'figūras' else 'Globāls_Pareizi_%_2': 100 * df[df['Globāls']]['Pareizi'].mean(),
        f'Lokāls_Vid_Reakcija_1' if test_type == 'figūras' else 'Lokāls_Vid_Reakcija_2': df[df['Lokāls']]['Reakcijas_laiks_ms'].mean(),
        f'Lokāls_Pareizi_%_1' if test_type == 'figūras' else 'Lokāls_Pareizi_%_2': 100 * df[df['Lokāls']]['Pareizi'].mean(),
    }
    return summary

def read_demographics_fixed(filepath):
    df = pd.read_csv(filepath)
    df['ID'] = df['ID'].astype(str).str.strip().str.zfill(6)
    df = df.drop_duplicates(subset='ID', keep='first')
    return df.set_index('ID').to_dict(orient='index')

def pilnais_apvienojums_safe(no_foldera):
    all_files = [os.path.join(no_foldera, f) for f in os.listdir(no_foldera) if f.endswith(".csv")]
    demographics_data = {}

    for file in all_files:
        if is_demographics_file(file):
            demographics_data.update(read_demographics_fixed(file))

    results = []

    for fig_file in all_files:
        if not is_test_file(fig_file, "figūras"):
            continue
        fig_data = read_test_data_safe(fig_file, "figūras")
        if not fig_data:
            continue

        user_id = fig_data['ID']
        result_row = fig_data.copy()

        for burti_file in all_files:
            if not is_test_file(burti_file, "burti"):
                continue
            if user_id not in open(burti_file, encoding='utf-8').read():
                continue
            burti_data = read_test_data_safe(burti_file, "burti")
            if burti_data and burti_data['ID'] == user_id:
                result_row.update(burti_data)
                break

        if user_id in demographics_data:
            result_row.update(demographics_data[user_id])

        results.append(result_row)

    final_df = pd.DataFrame(results)
    return final_df

folder_path = r"I:\Macibas\8.semestris\bakis\datu_analize"
final_df = pilnais_apvienojums_safe(folder_path)

# Saglabā CSV
final_df.to_csv("pilnais_apkopojums.csv", index=False, encoding="utf-8-sig")

# Saglabā arī kā Excel
final_df.to_excel("pilnais_apkopojums.xlsx", index=False)

print("✅ Saglabāts kā 'pilnais_apkopojums.csv' un 'pilnais_apkopojums.xlsx'")
