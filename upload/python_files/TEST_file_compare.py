#!/usr/bin/env python3
import argparse
import filecmp
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Compara dos archivos CSV y dice si son exactamente iguales."
    )
    parser.add_argument("csv1", help="Ruta al primer archivo CSV")
    parser.add_argument("csv2", help="Ruta al segundo archivo CSV")
    args = parser.parse_args()

    # Compara contenido byte a byte (shallow=False fuerza comparación de contenido)
    iguales = filecmp.cmp(args.csv1, args.csv2, shallow=False)

    if iguales:
        print("Los archivos son exactamente iguales.")
        sys.exit(0)
    else:
        print("Los archivos son diferentes.")
        sys.exit(1)

if __name__ == "__main__":
    main()
