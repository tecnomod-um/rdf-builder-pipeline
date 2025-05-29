import morph_kgc
import os
import rdflib
import argparse
import pandas as pd
import subprocess
import numpy as np

def combine_ttl_files(output_folder, combined_output_file):
    combined_graph = rdflib.Graph()

    for file_name in os.listdir(output_folder):
        if file_name.endswith('.ttl'):
            file_path = os.path.join(output_folder, file_name)
            combined_graph.parse(file_path, format='turtle')

    combined_graph.serialize(destination=combined_output_file, format='turtle')


def main():

    parser = argparse.ArgumentParser(description='Procesar datos CSV')
    parser.add_argument('main_folder', type=str, help='Ruta carpeta principal')
    args = parser.parse_args()

    csv_file_path = os.path.join(args.main_folder, 'preprocessed_data/preprocessed_data.csv')
    df = pd.read_csv(csv_file_path,keep_default_na=False)
    grouped = df.groupby('field_id')

    for name, group in grouped:
        if not np.any(group['pattern_type'].values == ''):
            csv_file_path = os.path.join(args.main_folder,'csv')
            group_csv_filename = os.path.join(csv_file_path, f"{name}.csv")
            group.to_csv(group_csv_filename, index=False)

            rules_directory = os.path.join(args.main_folder, 'rules')
            python_directory = os.path.join(args.main_folder, 'python_files')
            udf_path = os.path.join(python_directory, 'udf.py')
            mapping_path = os.path.join(rules_directory, f"{name}_reglasgenericas.yarrrml")        
            subprocess.run(['python', 'generateRules.py', '--input', group_csv_filename, '--output', mapping_path], check=True)


            config = f'[CONFIGURATION]\noutput_format=N-QUADS\nudfs={udf_path}\n[DataSource]\nmappings={mapping_path}'
            output_file_path = os.path.join(args.main_folder,'instances')
            output_file_path_name = os.path.join(output_file_path,f"{name}_salida.ttl")
            g_morph = morph_kgc.materialize(config)
            g_morph.serialize(destination=output_file_path_name, format='turtle')

    combined_output_file = os.path.join(args.main_folder, 'output_experimento3_uncaso.ttl')
    combine_ttl_files(output_file_path, combined_output_file)


if __name__ == '__main__':
    main()

