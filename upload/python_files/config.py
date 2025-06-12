# dataPreprocessing.py constants
CASE_ID_COLUMN = "case_id"

REQUIRED_MAPPING_COLS = {
    'field_id', 'value_type', 'categorical_value', 
    'categorical_ontology_mapping', 'procedure_result'
}
REQUIRED_DATA_COLS = {'case_id'}

# Initiate.py path constants
PREPROCESSED_FOLDER = 'preprocessed_data'
PREPROCESSED_FILENAME = 'preprocessed_data.csv'
CSV_FOLDER = 'csv'
RULES_FOLDER = 'rules'
PYTHON_FOLDER = 'python_files'
UDF_FILENAME = 'udf.py'
INSTANCES_FOLDER = 'instances'
FINAL_OUTPUT_FILENAME = 'output_RDF_Guttman.ttl'
TEMPLATES_FOLDER = 'templates'

# generateRules.py constants
YARRML_TEMPLATE_FILE = 'yarrrml_template.yml'