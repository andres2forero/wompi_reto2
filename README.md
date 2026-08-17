# Wompi Reto 2

Pipeline en Python para procesar transacciones con tarjeta desde un archivo JSONL, filtrar las transacciones aprobadas y generar una vista agregada por día y BIN en formato Parquet.

## Estructura del proyecto

```text
wompi_reto2/
├── generate_summary.py
├── input/
│   └── transactions_50k.jsonl
├── output/
│   └── transactions_summary.parquet
├── requirements.txt
├── README.md
└── .gitignore
```

## Requisitos

- Python 3.13
- Pandas
- PyArrow

## Instalación

### 1. Install Python

Descargar e instalar [Python 3.13](https://www.python.org/downloads/).

Verificar la versión:

```powershell
python --version
```

Actualizar PIP:

```powershell
python -m pip install --upgrade pip
```

### 2. Configurar el Virtual Environment

Desde la carpeta del proyecto:

```powershell
cd .\wompi_reto2\
```

Instalar `virtualenv`:

```powershell
pip3 install virtualenv
```

Crear el entorno virtual:

```powershell
python -m virtualenv venv
```

Activar el entorno virtual:

```powershell
.\venv\Scripts\activate
```

Instalar las dependencias:

```powershell
pip3 install -r requirements.txt
```

## Datos fuente

El archivo `transactions_50k.jsonl` contiene las transacciones utilizadas por el proceso.

Por motivos de privacidad, este archivo **no está incluido en el repositorio**, ya que contiene información personal.

Para ejecutar el proyecto, se debe suministrar el archivo y colocarlo en:

```text
input/transactions_50k.jsonl
```

El archivo utiliza el formato JSONL, donde cada línea representa una transacción independiente.

## Ejecución

Con el entorno virtual activo y el archivo de entrada ubicado en `input/`, ejecutar:

```powershell
python .\generate_summary.py --input .\input\transactions_50k.jsonl --output .\output\transactions_summary.parquet
```

El script:

1. Lee las transacciones del archivo JSONL.
2. Extrae y transforma los campos necesarios.
3. Filtra únicamente las transacciones con estado `APPROVED`.
4. Extrae el BIN de la tarjeta.
5. Agrupa las transacciones por día, mes, año y BIN.
6. Calcula la cantidad de transacciones aprobadas.
7. Calcula el monto total aprobado.
8. Genera el archivo Parquet.
9. Muestra la vista agregada en consola.
10. Genera un hash SHA-256 del archivo de salida.

## Datos de salida

El resultado principal se genera en:

```text
output/transactions_summary.parquet
```

La vista agregada contiene las siguientes columnas:

```text
day
month
year
bin
approved_transactions
total_approved_amount
```

La granularidad de la vista es:

```text
Día + BIN
```

Esto significa que todas las transacciones aprobadas del mismo BIN realizadas durante el mismo día se agrupan en una única fila.

## Idempotencia

El proceso es idempotente. Ejecutar el script varias veces utilizando el mismo archivo de entrada produce el mismo resultado.

El archivo Parquet se sobrescribe en cada ejecución y no se utilizan resultados de ejecuciones anteriores.

Al finalizar el proceso se genera un hash SHA-256 del archivo Parquet, permitiendo verificar que el resultado sea consistente entre diferentes ejecuciones.

## Supuestos

- `created_at` se utiliza como fecha de la transacción.
- `updated_at` no se utiliza porque corresponde a la fecha de actualización del registro.
- Solo se consideran transacciones con `status = APPROVED`.
- El BIN se obtiene de `payment_method_type.extra.bin`.
- `amount_in_cents` está expresado en centavos.
- El monto total aprobado se convierte a unidades monetarias dividiendo entre 100.
- Los registros con fecha, BIN o monto inválidos son excluidos.
- Cada línea del archivo JSONL representa una transacción independiente.
- La agregación se realiza por día y BIN.
- El archivo Parquet se sobrescribe en cada ejecución para garantizar la idempotencia.

## Desactivar Virtual Environment

Una vez finalizado el procesamiento:

```powershell
deactivate
```

## Aviso de privacidad

El archivo `transactions_50k.jsonl` **no se incluye en este repositorio** debido a que contiene información personal asociada a las transacciones.

El archivo debe ser suministrado de forma independiente y colocado en:

```text
input/transactions_50k.jsonl
```

No se deben publicar en el repositorio archivos que contengan información personal o datos sensibles.