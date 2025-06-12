import morph_kgc
import os
import rdflib
import argparse
import pandas as pd
import subprocess
import sys
 
from config import (
    PREPROCESSED_FOLDER,
    PREPROCESSED_FILENAME,
    CSV_FOLDER,
    RULES_FOLDER,
    PYTHON_FOLDER,
    UDF_FILENAME,
    INSTANCES_FOLDER,
    FINAL_OUTPUT_FILENAME,
)

# Checks if the necessary directories exist, and creates them if they do not.
def check_or_create_directories(main_folder: str):
    required = [
        os.path.join(main_folder, PREPROCESSED_FOLDER),
        os.path.join(main_folder, CSV_FOLDER),
        os.path.join(main_folder, RULES_FOLDER),
        os.path.join(main_folder, PYTHON_FOLDER),
        os.path.join(main_folder, INSTANCES_FOLDER),
    ]
    for folder in required:
        os.makedirs(folder, exist_ok=True)


# Checks if the preprocessed CSV file exists, and loads it into a DataFrame.
def load_preprocessed_csv(main_folder: str) -> pd.DataFrame:
    csv_path = os.path.join(main_folder, PREPROCESSED_FOLDER, PREPROCESSED_FILENAME)
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Preprocessed data file not found on path: {csv_path}")
    df = pd.read_csv(csv_path, keep_default_na=False)
    return df

# Filters the DataFrame by field_id, and ensures that no rows in each group have an empty pattern_type.
def filter_valid_groups(df: pd.DataFrame):
    grouped = df.groupby('field_id')
    for field_id, group in grouped:
        if not (group['pattern_type'] == '').any():
            yield field_id, group

# Exports a DataFram group to a csv file in the corresponding folder 
def export_group_to_csv(group: pd.DataFrame, csv_folder: str, field_id: str) -> str:
    output_path = os.path.join(csv_folder, f"{field_id}.csv")
    group.to_csv(output_path, index=False)
    return output_path


# For a given field_id, generates the YARRRML file, materializes the RDF and serializes it to TTL.
def generate_yarrrml_and_serialize(field_id: str,
                                  group_csv_path: str,
                                  main_folder: str) -> str:

    rules_dir = os.path.join(main_folder, RULES_FOLDER)
    python_dir = os.path.join(main_folder, PYTHON_FOLDER)
    instances_dir = os.path.join(main_folder, INSTANCES_FOLDER)

    udf_path = os.path.join(python_dir, UDF_FILENAME)
    mapping_path = os.path.join(rules_dir, f"{field_id}_reglasgenericas.yarrrml")
    ttl_output_path = os.path.join(instances_dir, f"{field_id}_output.ttl")

    try:
        subprocess.run(
            [sys.executable, 'generateRules.py',
             '--input', group_csv_path,
             '--output', mapping_path],
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error when executing generateRules.py for '{field_id}': {e}")

    config = "\n".join([
        "[CONFIGURATION]",
        "output_format=N-QUADS",
        f"udfs={udf_path}",
        "[DataSource]",
        f"mappings={mapping_path}"
    ])

    try:
        g_morph = morph_kgc.materialize(config)
    except Exception as e:
        raise RuntimeError(f"Error in materialize() for '{field_id}': {e}")

    try:
        g_morph.serialize(destination=ttl_output_path, format='turtle')
    except Exception as e:
        raise RuntimeError(f"Error when serializing TTL for '{field_id}': {e}")

    return ttl_output_path


# Reads all .ttl files in the specified folder and combines them into a single RDF graph
def combine_ttl_files(instances_folder: str, combined_output_file: str):

    combined_graph = rdflib.Graph()

    for filename in os.listdir(instances_folder):
        if filename.endswith('.ttl'):
            file_path = os.path.join(instances_folder, filename)
            try:
                combined_graph.parse(file_path, format='turtle')
            except Exception:
                pass

    combined_graph.serialize(destination=combined_output_file, format='turtle')

def main():

    parser = argparse.ArgumentParser(description='RDF Generation using preprocessed CSV')
    parser.add_argument('main_folder', type=str, help='Path to the project root directory')
    args = parser.parse_args()
    main_folder = args.main_folder

    # 1. Additional directories verification and creation
    check_or_create_directories(main_folder)

    # 2. Load preprocessed CSV file
    try:
        df = load_preprocessed_csv(main_folder)
    except Exception as e:
        print(f"Error when loading the preprocessed data CSV file: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. Process each group of data
    for field_id, group in filter_valid_groups(df):
        csv_folder = os.path.join(main_folder, CSV_FOLDER)
        group_csv = export_group_to_csv(group, csv_folder, field_id)

        try:
            generate_yarrrml_and_serialize(field_id, group_csv, main_folder)
        except RuntimeError as e:
            print(f"Exiting '{field_id}' due to: {e}", file=sys.stderr)
            continue

    # 4. Combine TTL files into a single output file
    instances_folder = os.path.join(main_folder, INSTANCES_FOLDER)
    combined_output_file = os.path.join(main_folder, FINAL_OUTPUT_FILENAME)
    combine_ttl_files(instances_folder, combined_output_file)


if __name__ == '__main__':
    main()

