def generate_yarrrml_template(csv_file_name):
    template = f"""
    authors: Catalina Martinez-Costa <cmartinezcosta@um.es>
    prefixes:
      base: http://stratifai-resources/ontologies/stratifai-data#
      stratifai: http://stratifai#
      sct: http://snomed.info/id/
      scdm: http://www.semanticweb.org/catimc/SemanticCommonDataModel#
      btl2: http://purl.org/biotop/btl2.owl#
      fno:  https://w3id.org/function/ontology# 
      fnom: https://w3id.org/function/vocabulary/mapping#
      ex: http://example.org/functions#
      stratifai-function: http://ontology.stratifai.um.es/STRATIF-AI_Functions/
      grel: http://users.ugent.be/bjdmeest/function/grel.ttl#
      rdf: http://www.w3.org/1999/02/22-rdf-syntax-ns#
      xsd: http://www.w3.org/2001/XMLSchema#


    mappings:

        ClinicalCase:
            sources: 
                    - ['{csv_file_name}~csv']
            s: base:Case_$(case_id)
            po:
              - [a, stratifai:ClinicalCase]
              - [stratifai:caseId, $(case_id), xsd:string]
              - [scdm:hasInformationAboutProvider, base:InformationAboutStratifAIProviderOfInformation_$(case_id)~iri]
              - [scdm:hasInformationAboutProvider, base:InformationAboutStratifAISourceOfInformation_$(case_id)~iri]
              - p: scdm:hasPart
                o:
                - function: stratifai-function:generatePart
                  parameters:
                  - parameter: grel:valueParam
                    value: $(pattern_type)
                  - parameter: grel:valueParam1
                    value: $(field_id)
                  - parameter: grel:valueParam2
                    value: $(ontology_mapping)
                  - parameter: grel:valueParam3
                    value: $(case_id)
                  type: iri       
        InformationAboutProvider:
            sources: 
                    - ['{csv_file_name}~csv']
            s: base:InformationAboutStratifAIProviderOfInformation_$(case_id)
            po:
              - [a, stratifai:InformationAboutStratifAIProviderOfInformation]
              - [btl2:represents, base:StratifAIProvider_$(case_id)~iri]

        InformationAboutSource:
            sources: 
                    - ['{csv_file_name}~csv']
            s: base:InformationAboutStratifAISourceOfInformation_$(case_id)
            po:
              - [a, stratifai:InformationAboutStratifAISourceOfInformation]
              - [btl2:represents, base:StratifAISource_$(case_id)~iri]
        
        StratifAIProvider:
            sources: 
                    - ['{csv_file_name}~csv']
            s: base:StratifAIProvider_$(case_id)
            po:
              - [a, stratifai:StratifAIProvider] 

        StratifAISource:
            sources: 
                    - ['{csv_file_name}~csv']
            s: base:StratifAISource_$(case_id)
            po:
              - [a, stratifai:StratifAISource]
              #- [base:sourceId,$(source)]        
        
        StatementTemporalContext:
            sources: 
                - ['{csv_file_name}~csv']
            s:
            - function: stratifai-function:generate_temporal_context
              parameters:
              - parameter: grel:valueParam
                value: $(temporal_context)
              type: iri
            po:
                - [a, $(temporal_context)~iri]
            
        StatementContext:
            sources: 
                - ['{csv_file_name}~csv']
            s:
            - function: stratifai-function:generate_statement_context
              parameters:
              - parameter: grel:valueParam
                value: $(statement_context)
              type: iri
            po:
                - [a, $(statement_context)~iri]

        ProcedureLocation:
            sources: 
                - ['{csv_file_name}~csv']
            s:
            - function: stratifai-function:generate_procedure_location
              parameters:
              - parameter: grel:valueParam
                value: $(procedure_location)
              type: iri
            po:
                - [a, $(procedure_location)~iri]

        ProcedureReason:
            sources: 
                - ['{csv_file_name}~csv']
            s:
            - function: stratifai-function:generate_procedure_reason
              parameters:
              - parameter: grel:valueParam
                value: $(procedure_reason)
              type: iri
            po:
                - [a, $(procedure_reason)~iri]
        
        ProcedureDateTime:        
          sources: 
              - ['{csv_file_name}~csv']
          s: 
          - function: stratifai-function:generate_procedure_dateTime
            parameters: 
            - parameter: grel:valueParam
              value: $(procedure)
            - parameter: grel:valueParam1
              value: $(categorical_ontology_mapping)
            type: iri
          po:
            - [a, $(categorical_ontology_mapping)~iri]  
    """

    return template