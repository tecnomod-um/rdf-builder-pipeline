import morph_kgc
from rdflib import URIRef


@udf( # type: ignore
    fun_id = "http://ontology.resq.um.es/RES-Q_Functions/add_procedure_dateTime",
    procedure = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam",
    temporal_context = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam1"
)

def add_procedure_dateTime(procedure,temporal_context):
    base = "http://resqplus-resources/ontologies/resqplus-data#"
    if procedure != 'dateTime':
        return
    uri = temporal_context.split('#')[-1] if '#' in temporal_context else temporal_context.split('/')[-1]
    return f"{base}{uri}"

@udf( # type: ignore
    fun_id = "http://ontology.resq.um.es/RES-Q_Functions/generate_procedure_dateTime",
    procedure = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam",
    temporal_context = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam1"
)

def generate_procedure_dateTime(procedure,temporal_context):
    base = "http://resqplus-resources/ontologies/resqplus-data#"
    if procedure != 'dateTime':
        return
    uri = temporal_context.split('#')[-1] if '#' in temporal_context else temporal_context.split('/')[-1]
    return f"{base}{uri}"

@udf( # type: ignore
    fun_id = "http://ontology.resq.um.es/RES-Q_Functions/add_temporal_context",
    temporal_context = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam")

def add_temporal_context(temporal_context):
    base = "http://resqplus-resources/ontologies/resqplus-data#"
    if temporal_context == 'nan':
        return None
    uri = temporal_context.split('#')[-1] if '#' in temporal_context else temporal_context.split('/')[-1]
    return f"{base}{uri}"

@udf( # type: ignore
    fun_id = "http://ontology.resq.um.es/RES-Q_Functions/generate_temporal_context",
    temporal_context = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam")

def generate_temporal_context(temporal_context):
    base = "http://resqplus-resources/ontologies/resqplus-data#"
    if temporal_context == 'nan':
        return None
    uri = temporal_context.split('#')[-1] if '#' in temporal_context else temporal_context.split('/')[-1]
    return f"{base}{uri}"

@udf( # type: ignore
    fun_id = "http://ontology.resq.um.es/RES-Q_Functions/generate_procedure_location",
    location = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam")

def generate_procedure_location(location):
    base = "http://resqplus-resources/ontologies/resqplus-data#"
    if location.strip() == 'nan':
        return None
    uri =location.split('#')[-1] if '#' in location else location.split('/')[-1]
    return f"{base}ProcedureLocation_{uri}"

@udf( # type: ignore
    fun_id = "http://ontology.resq.um.es/RES-Q_Functions/generate_procedure_reason",
    reason = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam")

def generate_procedure_reason(reason):
    base = "http://resqplus-resources/ontologies/resqplus-data#"
    if reason.strip() == 'nan':
        return None
    uri =reason.split('#')[-1] if '#' in reason else reason.split('/')[-1]
    return f"{base}ProcedureReason_{uri}"


@udf( # type: ignore
    fun_id = "http://ontology.resq.um.es/RES-Q_Functions/generate_statement_context",
    statement_context = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam")

def generate_statement_context(statement_context):
    base = "http://resqplus-resources/ontologies/resqplus-data#"
    if statement_context.strip() == 'nan':
        return None
    uri = statement_context.split('#')[-1] if '#' in statement_context else statement_context.split('/')[-1]
    return f"{base}{uri}"
# case ObservationResultStatement and boolean datatype (onset_time_known)
# if field_value is true then known present
# if field_value is false then unknown

@udf(# type:ignore
    fun_id = "http://ontology.resq.um.es/RES-Q_Functions/add_observable_statement_context",
    value = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam1",
    datatype = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam")

def add_observable_statement_context(datatype,value):
    if datatype == 'Boolean':
        if value in ['FALSE','FALSO']:
            return "http://snomed.info/id/261665006" #Unknown
        elif value in ['TRUE','VERDADERO']:
            return "http://snomed.info/id/410515003" #Known present
    return

#case ClinicalSituationStatement datatype Boolean 
#field_value true return
#field_value false known absent

@udf(# type:ignore
    fun_id = "http://ontology.resq.um.es/RES-Q_Functions/add_situation_context",
    field_value = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam1",
    datatype = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam",
    context = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam2"
)
def add_situation_context(datatype,field_value,context):
    base = "http://resqplus-resources/ontologies/resqplus-data#"
    if context.strip() == 'nan':
        return None
    if datatype.strip() == 'Boolean':
        if field_value in ['FALSE','FALSO']:
            return "http://snomed.info/id/410516002" #known absent
    elif datatype.strip() == 'Categorical':
        uri = context.split('#')[-1] if '#' in context else context.split('/')[-1]
        return f"{base}{uri}"
    return

@udf(#type:ignore
     fun_id = "http://ontology.resq.um.es/RES-Q_Functions/add_procedure_statement_context",
     datatype = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam",
     field_value = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam2",
     categorical_mapping = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam3")

def add_procedure_statement_context(datatype,field_value,categorical_mapping):
    if datatype == 'Boolean':
        if field_value in ('FALSE', 'FALSO'):
                return "http://snomed.info/id/385660001"  # not done
        return "http://snomed.info/id/385658003"  # done
    elif datatype == 'Categorical':
        context_map = {
            'not required': f"{categorical_mapping}",
            'recommended only': f"{categorical_mapping}",
            'yes': "http://snomed.info/id/385658003",  # done
            'no': "http://snomed.info/id/385660001",  # not done
            'not applicable': "http://snomed.info/id/385432009",  # not applicable
            'not done': "http://snomed.info/id/385660001~iri",  # not done
        }
        return context_map.get(field_value.strip())
    return

@udf(#type:ignore
    fun_id = "http://ontology.resq.um.es/RES-Q_Functions/add_procedure_reason",
    type = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam",
    reason = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam1"
)
def add_procedure_reason(type,reason):
    base = "http://resqplus-resources/ontologies/resqplus-data#"
    if type == 'procedureReason':
        reason = reason.split('#')[-1] if '#' in reason else reason.split('/')[-1]
        return f"{base}ProcedureReason_{reason}"
    return

@udf(#type:ignore
    fun_id = "http://ontology.resq.um.es/RES-Q_Functions/add_procedure_location",
    type = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam",
    location = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam1",
)
def add_procedure_location(type,location):
    base = "http://resqplus-resources/ontologies/resqplus-data#"
    if type == 'procedureLocation':
        location = location.split('#')[-1] if '#' in location else location.split('/')[-1]
        return f"{base}ProcedureLocation_{location}"
    return

@udf(#type:ignore
    fun_id = "http://ontology.resq.um.es/RES-Q_Functions/add_procedure_performer",
    type = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam"
)
def add_procedure_performer(type):
    if type == 'performer':
        return f"base:Performer_$(field_id)_$(case_id)"
    return


@udf(#type:ignore
    fun_id = "http://ontology.resq.um.es/RES-Q_Functions/generateDynamicSubject",
    type = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam",
    procedure = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam1",
    field_value = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam2",
    categorical_ontology_mapping = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam3",
    case_id = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam4"
)
def generateDynamicSubject(type,procedure,field_value,categorical_ontology_mapping,case_id):
    base = "http://resqplus-resources/ontologies/resqplus-data#"
    if type == 'Boolean':
        uri = procedure.split('#')[-1] if '#' in procedure else procedure.split('/')[-1]
    #Categorical
    else:
        if field_value.capitalize() in ['Yes','No']:
            uri = procedure.split('#')[-1] if '#' in procedure else procedure.split('/')[-1]
        else:
            uri = categorical_ontology_mapping.split('#')[-1] if '#' in categorical_ontology_mapping else categorical_ontology_mapping.split('/')[-1]
    return f"{base}{uri}_{case_id}"


@udf(#type:ignore
    fun_id = "http://ontology.resq.um.es/RES-Q_Functions/generateDynamicObject",
    type = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam",
    procedure = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam1",
    field_value = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam2",
    categorical_ontology_mapping = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam3"
)
def generateDynamicObject(type,procedure,field_value,categorical_ontology_mapping):
    if type == 'Boolean':
        return f"{procedure}"
    #Categorical
    else:
        if field_value.capitalize() in ['Yes','No']:
            return f"{procedure}"
        else:
            #print(f"objeto: {categorical_ontology_mapping}~iri")
            return f"{categorical_ontology_mapping}"
    return



@udf(#type:ignore
    fun_id = "http://ontology.resq.um.es/RES-Q_Functions/extract_last_part",
    uri = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam",
    case_id = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam1"
)
def extract_last_part(uri,case_id):
    base = "http://resqplus-resources/ontologies/resqplus-data#"
    uri = uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]
    #print(f"base:{uri}_{case_id}")
    return f"{base}{uri}_{case_id}"
 

@udf(#type:ignore
    fun_id = "http://ontology.resq.um.es/RES-Q_Functions/generatePart",
    pattern_type = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam",
    field_id = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam1",
    ontology_mapping = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam2",
    case_id = "http://users.ugent.be/bjdmeest/function/grel.ttl#valueParam3"
)
def generatePart(pattern_type,field_id,ontology_mapping,case_id):
    base = "http://resqplus-resources/ontologies/resqplus-data#"
    if pattern_type == 'ObservationResultStatement':
        return f"{base}ObservationResultSt_{ontology_mapping}_{field_id}_{case_id}"
    elif pattern_type == 'ClinicalProcedureStatement':
        return f"{base}ClinicalProcedureSt_{ontology_mapping}_{field_id}_{case_id}"
    elif pattern_type == 'ClinicalSituationStatement':
        return f"{base}ClinicalSituationSt_{ontology_mapping}_{field_id}_{case_id}"
    else:
        return ''
    

    