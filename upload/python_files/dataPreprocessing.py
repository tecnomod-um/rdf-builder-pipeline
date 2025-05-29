import pandas as pd
import argparse

def main(csvdata, csvmapping, output_path):
    # Cargar los datos del CSV y el archivo de mapping usando pandas
    data_df = pd.read_csv(csvdata, encoding='utf-8-sig')
    mapping_df = pd.read_csv(csvmapping, encoding='utf-8-sig')

    # Limpiar espacios en blanco alrededor de los IDs de campo y otros campos necesarios
    mapping_df['field_id'] = mapping_df['field_id'].str.strip()
    mapping_df['categorical_value'] = mapping_df['categorical_value'].str.strip()  
    mapping_df['procedure_result'] = mapping_df['procedure_result'].str.strip()

    # Crear un DataFrame vacío para almacenar los resultados
    results = []

    # Procesar cada fila en el DataFrame de datos
    for _, data_row in data_df.iterrows():
        case_id = data_row['case_id']
        
        # Procesar cada fila en el DataFrame de mapeo
        for _, map_row in mapping_df.iterrows():
            field_id = map_row['field_id']
            #el campo en mapping file está en los datos
            if field_id in data_df.columns:
                # Verificar si el valor en data_df coincide con el valor en mapping_df y en caso de tener valor categórico, si coincide
                if not pd.notna(map_row['categorical_value']) or data_row[field_id] == map_row['categorical_value']:
                    #print(f"field_id={field_id} data={data_row[field_id]} mapping={map_row['categorical_value']}")
                    result_row = map_row.to_dict()
                    if map_row['value_type'] == 'Boolean' and not pd.notna(data_row[field_id]):
                        continue
                    if map_row['value_type'] == 'Integer' and pd.notna(data_row[field_id]):
                        #print(f"field = {field_id}")
                        value = int(data_row[field_id])
                    elif map_row['value_type'] == 'Integer':
                        continue
                    else:
                        value = data_row[field_id]
                    result_row.update({
                        'case_id': case_id,
                        'field_value': value
                    })
                    
                    # Verificar si `procedure_result` tiene un valor
                    if pd.notna(map_row['procedure_result']) and map_row['procedure_result'] in data_df.columns:
                        proc_result_field = map_row['procedure_result']
                        proc_result_value = data_row[proc_result_field]
                        
                        # Buscar en mapping_df el mapeo correspondiente al valor encontrado en proc_result_value
                        mapping_match = mapping_df[(mapping_df['field_id'] == proc_result_field) & (mapping_df['categorical_value'] == proc_result_value)]
                        if not mapping_match.empty:
                            result_row['procedure_result'] = mapping_match['categorical_ontology_mapping'].values[0]
                        else:
                            result_row['procedure_result'] = None
                    else:
                        result_row['procedure_result'] = None

                    results.append(result_row)

    # Convertir la lista de resultados en un DataFrame
    result_df = pd.DataFrame(results)

    # Guardar el DataFrame resultante en un archivo CSV
    result_data_file = f'{output_path}/preprocessed_data.csv'
    result_df.to_csv(result_data_file, index=False, encoding='utf-8-sig')
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process CSV data and mapping files using pandas.")
    parser.add_argument('csvdata', type=str, help='Path to the CSV data file')
    parser.add_argument('csvmapping', type=str, help='Path to the CSV mapping file')
    parser.add_argument('output_path', type=str, help='Output path for the processed CSV file')
    args = parser.parse_args()
    main(args.csvdata, args.csvmapping, args.output_path)
