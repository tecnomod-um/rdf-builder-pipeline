import pandas as pd
import argparse
import config
import os
import sys

### Setup functions

# Function to clean whitespace around field IDs and other necessary fields
def clean_data(df):
    if 'field_id' in df.columns:
        df['field_id'] = df['field_id'].str.strip()
    if 'categorical_value' in df.columns:
        df['categorical_value'] = df['categorical_value'].str.strip()
    if 'procedure_result' in df.columns:
        df['procedure_result'] = df['procedure_result'].str.strip()
    return df


# Checks if the necessary columns are present in the data and mapping DataFrames.
def validate_inputs(data_df: pd.DataFrame, mapping_df: pd.DataFrame):
    """
    Lanza un error si faltan columnas necesarias en data_df o mapping_df.
    """
    missing_data = config.REQUIRED_DATA_COLS - set(data_df.columns)
    if missing_data:
        raise KeyError(f"The following columns are missing in the data file: {missing_data}")

    missing_map = config.REQUIRED_MAPPING_COLS - set(mapping_df.columns)
    if missing_map:
        raise KeyError(f"The following columns are missing in the mappings file: {missing_map}")


# Builds default dictionaries that will help with the processing of the data.
def build_mapping_indices(mapping_df):
    """
    Builds two structures by analyzing the mapping DataFrame:
    1. A dictionary that, for each field, contains the row that would result from processing it
    2. A dictionary that, for each field, contains information about the procedure that generates the field data

    This is used to avoid processing the same field multiple times, and to avoid having to
    search for the procedure result in the mapping DataFrame every time we process a row.
    """
    mapping_by_field = {}
    proc_result_index = {}

    for _, row in mapping_df.iterrows():
        # Process the mapping by field
        field = row['field_id']
        row_dict = row.to_dict()
        mapping_by_field.setdefault(field, []).append(row_dict)

        # Process the procedure result index
        categorical_value = row_dict.get('categorical_value')
        ontology_mapping = row_dict.get('categorical_ontology_mapping')
        if pd.notna(categorical_value) and pd.notna(ontology_mapping):
            proc_result_index.setdefault(field, {})[categorical_value] = ontology_mapping
    
    return mapping_by_field, proc_result_index

# Obtains the field value from a data row and checks if it is valid
def get_field_value(data_row, map_row):
    field_id = map_row['field_id']
    dtype = map_row['value_type']
    raw_value = data_row[field_id]

    if dtype == 'Boolean':
        if pd.isna(raw_value):
            return None
        return raw_value
    
    if dtype == 'Integer':
        if pd.notna(raw_value):
            try:
                return int(raw_value)
            except ValueError:
                return None
        return None
    
    return raw_value

# Checks if the procedure result is valid and returns the corresponding value
def get_procedure_result(data_row, map_row, proc_result_index):

    proc_field = map_row.get('procedure_result')

    if pd.isna(proc_field) or proc_field not in data_row.index:
        return None
    
    value = data_row[proc_field]

    if pd.isna(value):
        return None
    
    field_index = proc_result_index.get(proc_field)
    if field_index is None:
        return None
    
    return field_index.get(value)


### Processing functions


def process_data(data_df, mapping_df):
    
    # 1. Validates that the necessary columns are present in the data and mapping DataFrames.
    validate_inputs(data_df, mapping_df)

    # 2. Selects only the fields that are present in the data file
    filtered_mapping_df = mapping_df[mapping_df['field_id'].isin(data_df.columns)]

    # 3. Builds the mapping indexes
    mapping_by_field, proc_result_index = build_mapping_indices(filtered_mapping_df)

    results = []

    # 4. Build the result row using data from the indexes that were built before
    for _, data_row in data_df.iterrows():
        case_id = data_row[config.CASE_ID_COLUMN]

        for field_id, map_rows in mapping_by_field.items():
            raw_value = data_row[field_id]
            
            # Checks the correct mapping row based on the value
            for map_row in map_rows:
                categorical_value = map_row.get('categorical_value')

                # If the row is categorical, we have to find the correct one
                # Otherwise, we can process it directly
                if pd.notna(categorical_value) and raw_value != categorical_value:
                    continue

                value = get_field_value(data_row, map_row)
                # If the value is None it means that the field is not valid or not present, and the row should be skipped
                if value is None:
                    continue
                
                # The procedure result is not an obligatory field, so this can return None
                procedure_result_uri = get_procedure_result(data_row, map_row, proc_result_index)

                result_row = map_row.copy()
                result_row['case_id'] = case_id
                result_row['field_value'] = value
                result_row['procedure_result'] = procedure_result_uri

                results.append(result_row)

    return pd.DataFrame(results)




def main(path_csv_data, path_csv_mapping, output_path):

    # Error handling for file paths
    if not os.path.exists(path_csv_data):
        raise FileNotFoundError(f"The CSV data file does not exist: {path_csv_data}")
    if not os.path.exists(path_csv_mapping):
        raise FileNotFoundError(f"The CSV mapping file does not exist: {path_csv_mapping}")

    # Load CSV data file
    try:
        data_df = pd.read_csv(path_csv_data, encoding='utf-8-sig')
    except pd.errors.EmptyDataError:
        print(f"Error: file '{path_csv_data}' is empty.")
        sys.exit(1)
    except pd.errors.ParserError as e:
        print(f"Error when parsing the data csv '{path_csv_data}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error when reading '{path_csv_data}': {e}")
        sys.exit(1)

    # Load mapping CSV file
    try:
        mapping_df = pd.read_csv(path_csv_mapping, encoding='utf-8-sig')
    except pd.errors.EmptyDataError:
        print(f"Error: mapping file '{path_csv_mapping}' is empty.")
        sys.exit(1)
    except pd.errors.ParserError as e:
        print(f"Error when parsing the mapping CSV file '{path_csv_mapping}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error when reading '{path_csv_mapping}': {e}")
        sys.exit(1)

    # Clean whitespace around field IDs and other necessary fields
    mapping_df = clean_data(mapping_df)

    # Process the data using the mapping
    result_df = process_data(data_df, mapping_df)

    # Guardar el DataFrame resultante en un archivo CSV
    result_data_file = f'{output_path}/preprocessed_data.csv'
    result_df.to_csv(result_data_file, index=False, encoding='utf-8-sig')
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process CSV data and mapping files using pandas.")
    parser.add_argument('csv_data_path', type=str, help='Path to the CSV data file')
    parser.add_argument('csv_mapping_path', type=str, help='Path to the CSV mapping file')
    parser.add_argument('output_path', type=str, help='Output path for the processed CSV file')
    args = parser.parse_args()
    main(args.csv_data_path, args.csv_mapping_path, args.output_path)
