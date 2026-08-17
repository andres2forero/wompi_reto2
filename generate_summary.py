import argparse
import json
from pathlib import Path
import pandas as pd
import hashlib

def read_transactions(input_file: Path) -> pd.DataFrame:
    """Lee las transacciones desde un archivo en formato JSONL"""

    transactions = []

    # Abre el archivo en modo lectura utilizando codificación UTF-8
    with input_file.open("r", encoding="utf-8") as file:

        # Recorre el archivo línea por línea.
        # enumerate permite conocer el número de cada línea
        for line_number, line in enumerate(file, start=1):

            # Elimina espacios y saltos de línea al inicio y al final
            line = line.strip()

            # Ignora las líneas vacías.
            if not line:
                continue

            try:
                # Convierte la línea de texto JSON en un diccionario de Python
                transaction = json.loads(line)

                # Agrega la transacción a la lista de transacciones
                transactions.append(transaction)

            except json.JSONDecodeError as exc:
                # Si la línea no contiene un JSON válido, genera un error
                # indicando exactamente en qué línea se encontró el problema
                raise ValueError(
                    f"JSON inválido en la línea {line_number}"
                ) from exc

    # Convierte la lista de diccionarios en un DataFrame de Pandas
    return pd.DataFrame(transactions)


def transform_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Extrae y transforma los campos necesarios para la vista resumen."""

    result = pd.DataFrame()

    # Convierte la fecha de creación de texto a un tipo fecha de Pandas
    # Los valores que no puedan convertirse se transforman en NaT
    result["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    # Copia el estado de cada transacción.
    result["status"] = df["status"]

    # Extrae el BIN desde la estructura anidada:
    # payment_method_type -> extra -> bin
    # Si la estructura no existe o no es un diccionario, devuelve None
    result["bin"] = df["payment_method_type"].apply(
        lambda payment_method: (
            payment_method.get("extra", {}).get("bin")
            if isinstance(payment_method, dict)
            else None
        )
    )

    # Convierte el monto a un valor numérico.
    # Los valores que no puedan convertirse se transforman en NaN.
    result["amount_in_cents"] = pd.to_numeric(
        df["amount_in_cents"],
        errors="coerce"
    )

    # Elimina las transacciones que no tengan una fecha,
    # un BIN o un monto válido
    result = result.dropna(
        subset=["created_at", "bin", "amount_in_cents"]
    )

    # El reto requiere contar y sumar únicamente las transacciones aprobadas
    result = result[result["status"] == "APPROVED"].copy()

    # Extrae el día, mes y año a partir de la fecha de la transacción
    result["day"] = result["created_at"].dt.date
    result["month"] = result["created_at"].dt.month
    result["year"] = result["created_at"].dt.year

    return result


def aggregate_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Genera la vista agregada requerida"""

    # Agrupa las transacciones por día, mes, año y BIN
    # Como previamente se filtraron únicamente las transacciones aprobadas,
    # cada grupo representa las transacciones aprobadas de un BIN en un día
    summary = (
        df.groupby(
            ["day", "month", "year", "bin"],
            as_index=False
        )
        .agg(
            # Cuenta la cantidad de transacciones aprobadas de cada grupo
            approved_transactions=("status", "size"),

            # Suma el monto total aprobado de cada grupo
            # El valor original está expresado en centavos
            total_approved_amount_cents=(
                "amount_in_cents",
                "sum"
            ),
        )
    )

    # Convierte el monto total de centavos a unidades monetarias
    # Por ejemplo, 15000 centavos se convierten en 150.00
    summary["total_approved_amount"] = (
        summary["total_approved_amount_cents"] / 100
    )

    # Elimina la columna temporal que contiene el monto en centavos,
    # ya que la vista final utilizará el monto convertido
    summary = summary.drop(
        columns=["total_approved_amount_cents"]
    )

    # Ordena el resultado por día y BIN para garantizar
    # un resultado consistente y determinístico
    summary = summary.sort_values(
        ["day", "bin"]
    ).reset_index(drop=True)

    return summary


def write_parquet(df: pd.DataFrame, output_file: Path) -> None:
    """Guarda el resultado en formato Parquet."""

    # Crea el directorio de salida si todavía no existe
    # parents=True permite crear también los directorios padre necesarios
    # exist_ok=True evita generar un error si el directorio ya existe
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Guarda el DataFrame en formato Parquet utilizando PyArrow como motor
    # Si el archivo ya existe, se sobrescribe para garantizar la idempotencia
    # del proceso
    # index=False evita guardar el índice de Pandas como una columna adicional
    df.to_parquet(
        output_file,
        engine="pyarrow",
        index=False
    )


def calculate_file_hash(file_path: Path) -> str:
    """Calcula el hash SHA-256 de un archivo"""

    # Crea un objeto SHA-256 que se utilizará para calcular
    # la huella digital del archivo
    sha256 = hashlib.sha256()

    # Abre el archivo en modo binario para poder procesar
    # exactamente los bytes que contiene
    with file_path.open("rb") as file:

        # Lee el archivo en bloques de 8192 bytes en lugar de cargarlo
        # completamente en memoria
        # Cada bloque se agrega al cálculo del hash
        for chunk in iter(lambda: file.read(8192), b""):
            sha256.update(chunk)

    # Devuelve el hash completo como una cadena hexadecimal
    # Este valor permite verificar si el archivo es exactamente igual
    # entre diferentes ejecuciones del proceso
    return sha256.hexdigest()


def main() -> None:
    """Ejecuta el flujo principal del procesamiento de transacciones"""

    # Crea el parser que permite recibir argumentos desde la línea de comandos
    parser = argparse.ArgumentParser(
        description="Genera una vista agregada de las transacciones."
    )

    # Define la ruta del archivo JSONL de entrada
    # Este argumento es obligatorio para ejecutar el script.
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Ruta al archivo JSONL de entrada."
    )

    # Define la ruta donde se guardará el archivo Parquet de salida.
    # Este argumento también es obligatorio
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Ruta al archivo Parquet de salida."
    )

    # Lee y procesa los argumentos proporcionados al ejecutar el script
    args = parser.parse_args()

    # Lee las transacciones del archivo JSONL y las convierte
    # en un DataFrame de Pandas
    transactions = read_transactions(args.input)

    # Limpia y transforma las transacciones, extrayendo los campos
    # necesarios y conservando únicamente las transacciones aprobadas
    transformed = transform_transactions(transactions)

    # Agrupa las transacciones por día, mes, año y BIN,
    # calculando la cantidad y el monto total aprobado
    summary = aggregate_transactions(transformed)

    # Guarda la vista agregada en formato Parquet
    write_parquet(summary, args.output)

    # Calcula el hash SHA-256 del archivo Parquet generado
    # Esto permite verificar que el resultado sea idéntico
    # entre diferentes ejecuciones con el mismo archivo de entrada
    file_hash = calculate_file_hash(args.output)

    # Muestra un resumen de la ejecución
    print(f"Transacciones procesadas: {len(transactions)}")
    print(f"Transacciones aprobadas: {len(transformed)}")
    print(f"Filas de la vista agregada: {len(summary)}")
    print(f"Archivo de salida: {args.output}")
    print(f"SHA-256: {file_hash}")


# Este bloque garantiza que la función main() se ejecute
# únicamente cuando este archivo se ejecuta directamente,
# y no cuando es importado como módulo desde otro archivo
if __name__ == "__main__":
    main()