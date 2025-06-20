import csv
import argparse
import template_manager

### GENERATION FUNCTIONS ###

def generate_observation_result_statement(row,csv_file_name):
    rule_name = row['ontology_mapping'].strip() + '_' + row['field_id'].strip()
    ontology_mapping = row['ontology_mapping'].strip()
    field_id = row['field_id'].strip()
    observable = row['observable'].strip()
    source_procedure = extract_last_part(row['source_procedure'].strip())
    value_type = row['value_type'].strip()
    
    regla = f"""
        {rule_name}_ObservationResultStatement:
            sources:
                - ['{csv_file_name}~csv']
            s: base:ObservationResultSt_{ontology_mapping}_{field_id}_$(case_id)
            po:
                - [a, stratifai:{ontology_mapping}~iri]
                - [scdm:hasObservable, {observable}~iri] # observable entity
                - [scdm:isResultOf, base:Procedure_{source_procedure}_$(case_id)~iri]
                - p: scdm:temporalContext
                  o:
                  - function: stratifai-function:add_temporal_context
                    parameters: 
                    - parameter: grel:valueParam
                      value: $(temporal_context)
                    type: iri
                - p: scdm:situationContext
                  o:
                  - function: stratifai-function:add_observable_statement_context
                    parameters:
                    - parameter: grel:valueParam
                      value: $(value_type)
                    - parameter: grel:valueParam1
                      value: $(field_value)
                    type: iri
        """
    
    # Handling value types other than Boolean
    if value_type != 'Boolean':
        regla += f"        - [scdm:hasObservableValue, base:PrimitiveValue_{field_id}_$(case_id)~iri]\n"

    return regla

def generate_procedure(row,csv_file_name):
    rule_name = row['ontology_mapping'].strip()
    source_procedure = row['source_procedure'].strip()

    # If the source procedure is empty, return empty to avoid generating invalid rules
    if not source_procedure:
        return ''

    # Extract the last part of the source procedure which is typically used as an identifier
    if '#' in source_procedure:
        source_procedure, source_procedure_iri = source_procedure.split('#')[-1], source_procedure
    else:
        source_procedure, source_procedure_iri = source_procedure.split('/')[-1], source_procedure

    # Base rule setup
    regla = f"""
        {rule_name}_ResultOfProcedure:
            sources: 
                - ['{csv_file_name}~csv']
            s: base:Procedure_{source_procedure}_$(case_id)
            po:
                - [a, {source_procedure_iri}~iri]
    """

    return regla


def generate_observation_result(row,csv_file_name):
    rule_name = row['ontology_mapping'].strip() + '_' + row['field_id'].strip()
    field_id = row['field_id'].strip()
    value_type = row['value_type'].strip().lower()

    # Mapping value types to XSD types
    xsd_types = {
        'integer': 'xsd:integer',
        'float': 'xsd:double',
        'datetime': 'xsd:dateTime',
        'string': 'xsd:string',  
        'boolean': 'xsd:boolean'
    }

    # Default to xsd:string if datatype is not recognized
    datatype_value = xsd_types.get(value_type, 'xsd:string')

    regla = f"""
        {rule_name}_PrimitiveValue:
            sources: 
                - ['{csv_file_name}~csv']
            s: base:PrimitiveValue_{field_id}_$(case_id)
            po:
                - [a, scdm:QuantitativeResultValue~iri]
                - [btl2:hasValue, $(field_value), {datatype_value}]  
        """
    return regla

def generate_clinical_situation_statement(row,csv_file_name):
    ontology_mapping = row['ontology_mapping'].strip()
    source_procedure = extract_last_part(row['source_procedure'].strip())
    categorical_ontology_mapping = row['categorical_ontology_mapping'].strip()
    value_type = row['value_type'].strip()

    regla = f"""
        {ontology_mapping}_ClinicalSituationStatement:
            sources: 
                - ['{csv_file_name}~csv']
            s: base:ClinicalSituationSt_$(ontology_mapping)_$(field_id)_$(case_id)
            po:
                - [a, stratifai:{ontology_mapping}~iri]
                - [scdm:isResultOf, base:Procedure_{source_procedure}_$(case_id)~iri]
                - p: scdm:temporalContext
                  o:
                  - function: stratifai-function:add_temporal_context
                    parameters:
                    - parameter: grel:valueParam
                      value: $(temporal_context)
                    type: iri
                - p: scdm:situationContext
                  o:
                  - function: stratifai-function:add_situation_context
                    parameters: 
                    - parameter: grel:valueParam
                      value: $(value_type)
                    - parameter: grel:valueParam1
                      value: $(field_value)
                    - parameter: grel:valueParam2
                      value: $(statement_context)
                    type: iri
    """

    if value_type == 'Categorical' and categorical_ontology_mapping != '':
        regla += f"            - [scdm:representsSituation, $(categorical_ontology_mapping)~iri]\n"
    else:
        regla += f"            - [scdm:representsSituation, $(finding)~iri]\n"


    procedure_result = row['procedure_result'].strip()
    if procedure_result:
        # Tratar de forma especial esto en preprocesamiento
        procedure = procedure_result
        procedure_result = procedure_result.split('#')[-1] if '#' in procedure_result else procedure_result.split('/')[-1]
        regla += f"""                - p: scdm:isResultOf 
                  o: 
                  - function: stratifai-function:extract_last_part 
                    parameters: 
                    - parameter: grel:valueParam 
                      value: $(procedure_result)
                    - parameter: grel:valueParam1
                      value: $(case_id)
                    type: iri
            """
    return regla


def generate_clinical_procedure_statement(row,csv_file_name):
    ontology_mapping = row['ontology_mapping'].strip()
    categorical_ontology_mapping = row['categorical_ontology_mapping'].strip()
    field_id = row['field_id'].strip()
    procedure = row['procedure'].strip()
    source_procedure = extract_last_part(row['source_procedure'].strip())
    rule_name = f"{ontology_mapping}_{field_id}_ClinicalProcedureStatement"
    value_type = row['value_type'].strip()
    field_value = row['field_value'].strip()

    regla = f"""
        {rule_name}:
            sources:
                - ['{csv_file_name}~csv']
            s: base:ClinicalProcedureSt_{ontology_mapping}_{field_id}_$(case_id)
            po:
                - [a, stratifai:{ontology_mapping}~iri]
                - [scdm:isResultOf, base:Procedure_{source_procedure}_$(case_id)~iri]
                - p: scdm:procedureContext
                  o:
                  - function: stratifai-function:add_procedure_statement_context
                    parameters: 
                    - parameter: grel:valueParam
                      value: $(value_type)
                    - parameter: grel:valueParam2
                      value: $(field_value)
                    - parameter: grel:valueParam3
                      value: $(categorical_ontology_mapping)
                    type: iri
                - p: scdm:procedureReason
                  o:
                  - function: stratifai-function:add_procedure_reason
                    parameters:
                    - parameter: grel:valueParam
                      value: $(procedure)
                    - parameter: grel:valueParam1
                      value: $(procedure_reason)
                    type: iri
                - p: scdm:procedureLocation
                  o:
                  - function: stratifai-function:add_procedure_location
                    parameters:
                    - parameter: grel:valueParam
                      value: $(procedure)
                    - parameter: grel:valueParam1
                      value: $(procedure_location)
                    type: iri
                - p: scdm:hasInformationAboutProvider
                  o:
                  - function: stratifai-function:add_procedure_performer
                    parameters:
                    - parameter: grel:valueParam
                      value: $(procedure)
                    type: iri
                - p: scdm:temporalContext
                  o:
                  - function: stratifai-function:add_procedure_dateTime
                    parameters: 
                    - parameter: grel:valueParam
                      value: $(procedure)
                    - parameter: grel:valueParam1
                      value: $(categorical_ontology_mapping)
                    type: iri          
    """     
    if value_type == 'Boolean':
        regla += f"""            - p: scdm:representsProcedure 
                  o: 
                  - function: stratifai-function:extract_last_part 
                    parameters: 
                    - parameter: grel:valueParam 
                      value: $(procedure)
                    - parameter: grel:valueParam1
                      value: $(case_id)
                    type: iri
            """
    #Categorical
    else:
        if field_value.capitalize() in ['Yes','No']:
            regla += f"""            - p: scdm:representsProcedure 
                  o: 
                  - function: stratifai-function:extract_last_part 
                    parameters: 
                    - parameter: grel:valueParam 
                      value: $(procedure)
                    - parameter: grel:valueParam1
                      value: $(case_id)
                    type: iri
            """
        elif categorical_ontology_mapping != '' and procedure not in ['dateTime', 'procedureReason','procedureLocation', 'performer']:
            regla += f"""            - p: scdm:representsProcedure 
                  o: 
                  - function: stratifai-function:extract_last_part 
                    parameters: 
                    - parameter: grel:valueParam 
                      value: $(categorical_ontology_mapping)
                    - parameter: grel:valueParam1
                      value: $(case_id)
                    type: iri
            """
    return regla


def generate_represented_procedure(row,csv_file_name):
    categorical_ontology_mapping = row['categorical_ontology_mapping'].strip()
    procedure = row['procedure'].strip()
    if categorical_ontology_mapping == '' and "http" not in procedure:
        return 
    ontology_mapping = row['ontology_mapping'].strip()
    rule_name = f"{ontology_mapping}_RepresentedProcedure"
    regla = f"""
        {rule_name}:
            sources:
                - ['{csv_file_name}~csv']
            s:
            - function: stratifai-function:generateDynamicSubject
              parameters:
              - parameter: grel:valueParam
                value: $(value_type)
              - parameter: grel:valueParam1
                value: $(procedure)
              - parameter: grel:valueParam2
                value: $(field_value)
              - parameter: grel:valueParam3
                value: $(categorical_ontology_mapping)
              - parameter: grel:valueParam4
                value: $(case_id)
              type: iri
            po:
              - p: rdf:type
                o:
                - function: stratifai-function:generateDynamicObject
                  parameters:
                  - parameter: grel:valueParam
                    value: $(value_type)
                  - parameter: grel:valueParam1
                    value: $(procedure)
                  - parameter: grel:valueParam2
                    value: $(field_value)
                  - parameter: grel:valueParam3
                    value: $(categorical_ontology_mapping)
                  type: iri

        """     
    return regla


def extract_last_part(uri):
    """Extracts the last significant part of a URI, handling both '#' and '/' separators."""
    return uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]


def generate_rule(row, pattern_handlers,csv_file_name):

    pattern_type = row['pattern_type'].strip()
    rules = []
    if pattern_type in pattern_handlers:
        for handler in pattern_handlers[pattern_type]:
            rule = handler(row,csv_file_name)
            if rule:
                rules.append(rule)
        return "\n".join(rules)
    else:
        print(f"Unknown or unhandled pattern type: {pattern_type}")  
        return ''  
    

### MAIN FUNCTIONS ###

def parse_arguments():
    """
    Parses command line arguments for input and output file paths.
    Returns:
        argparse.Namespace: Contains the input and output file paths.
    """

    parser = argparse.ArgumentParser(
        description="Generates YARRRML files from a CSV"
    )
    parser.add_argument(
        '--input', type=str, required=True,
        help='Path to the input CSV file'
    )
    parser.add_argument(
        '--output', type=str, required=True,
        help='Path to the output YARRRML file'
    )
    return parser.parse_args()


def load_template(csv_file_name):
    """
    Reads the YARRRML template from the template manager.
    Raises:
        FileNotFoundError: If the template file does not exist.
    Returns:
        str: The content of the YARRRML template file.
    """
    return template_manager.generate_yarrrml_template(csv_file_name)


def load_pattern_handlers():
    """
    Returns a dictionary mapping pattern types to their respective handler functions.
    """
    return {
        'ObservationResultStatement': [
            generate_observation_result_statement,
            generate_procedure,
            generate_observation_result
        ],
        'ClinicalSituationStatement': [
            generate_clinical_situation_statement,
            generate_procedure
        ],
        'ClinicalProcedureStatement': [
            generate_clinical_procedure_statement,
            generate_represented_procedure,
            generate_procedure
        ]
    }


def generate_rules(csv_file_name, pattern_handlers):
    """
    Reads a CSV file and generates YARRRML rules based on the patterns defined in pattern_handlers.
    Args:
        csv_file_name (str): Path to the input CSV file.
        pattern_handlers (dict): Dictionary mapping pattern types to handler functions.
    Returns:
        list: List of generated YARRRML rules.
    """

    rules = []
    field_ids_seen = set()

    # Leer CSV y acumular reglas, saltando duplicados
    with open(csv_file_name, mode='r', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            field_id = row['field_id'].strip()
            if field_id in field_ids_seen:
                continue   # Saltar duplicados, no romper el bucle
            field_ids_seen.add(field_id)

            print(f"field:{field_id}")
            rule = generate_rule(row, pattern_handlers, csv_file_name)
            if rule:
                rules.append(rule)

    return rules
    

def write_output(template, rules, output_file_path):
    """
    Writes the YARRRML output to a file, combining the template and generated rules.
    Args:
        template (str): The YARRRML template.
        rules (list): List of generated rules.
        output_file_path (str): Path to the output file.
    """
    yarrml_output = template + '\n'.join(rules)
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(yarrml_output)
        print(f"Generated YARRRML saved at: {output_file_path}")

def main():
    args = parse_arguments()

    csv_file_name = args.input
    output_file_path = args.output

    pattern_handlers = load_pattern_handlers()
    yarrml_template = load_template(csv_file_name)

    rules = generate_rules(csv_file_name, pattern_handlers)
    write_output(yarrml_template, rules, output_file_path)

    

if __name__ == "__main__":
    main()