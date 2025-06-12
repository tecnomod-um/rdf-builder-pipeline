#!/bin/bash

# Verificar si se proporcionó un parámetro
if [ $# -ne 3 ]; then
    echo "Usage: $0 <path_to_input> <path_to_mappings> <output_filename>"    
    exit 1
fi

INPUT_FILE=$1
MAPPINGS_FILE=$2
OUTPUT_FILE=$3

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null
then
    echo "Error: Python not installed or not in PATH."
    exit 1
fi

# Ejecutar el preprocesamiento de datos
python3 dataPreprocessing.py "$INPUT_FILE" "$MAPPINGS_FILE" "../preprocessed_data"

# Verificar si el comando anterior fue exitoso
if [ $? -ne 0 ]; then
    echo "Error al ejecutar dataPreprocessing.py"
    exit 1
fi

# Iniciar el proceso
python3 initiate.py ../

# Verificar si el comando anterior fue exitoso
if [ $? -ne 0 ]; then
    echo "Error al ejecutar initiate.py"
    exit 1
fi

# Mover el archivo de salida a la carpeta ../outputs con el nuevo nombre
OUTPUT="../outputs/${OUTPUT_FILE}"
mv ../initiate_output.ttl "$OUTPUT"

# Verificar si el comando anterior fue exitoso
if [ $? -ne 0 ]; then
    echo "Error al mover initiate_output.ttl a $OUTPUT"
    exit 1
fi

# Borrar el contenido de los directorios ../csv, ../rules y ../instances
rm -rf ../csv/* ../rules/* ../instances/* ../preprocessed_data/*

# Verificar si el comando anterior fue exitoso
if [ $? -ne 0 ]; then
    echo "Error al borrar contenido de los directorios ../csv, ../rules ../instances o ../preprocessed_data"
    exit 1
fi

echo "Ejecución completada con éxito."
