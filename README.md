# Wompi Reto 2

Pipeline en Python para procesar transacciones con tarjeta desde un archivo JSONL, filtrar las transacciones aprobadas y generar una vista agregada por día y BIN en formato Parquet.

## Estructura del proyecto

```text
wompi_reto2/
├── generate_summary.py
├── input/
│   └── transactions_50k.jsonl
├── output/
│   ├── transactions_summary.parquet
│   └── transactions_summary_validation.jsonl
├── requirements.txt
├── README.md
└── .gitignore
```

> Los archivos de entrada y salida pueden existir localmente, pero están excluidos del repositorio mediante `.gitignore` debido a que contienen información derivada de las transacciones.

## Requisitos

- Python 3.13
- Pandas
- PyArrow

## Instalación

### 1. Instalar Python

Descargar e instalar [Python 3.13](https://www.python.org/downloads/).

Verificar la versión:

```powershell
python --version
```

Actualizar PIP:

```powershell
python -m pip install --upgrade pip
```

### 2. Configurar el entorno virtual

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

El resultado principal será generado en:

```text
output/transactions_summary.parquet
```

### Generar JSONL de validación

El JSONL de validación es opcional y permite revisar fácilmente el resultado de las transformaciones y la agregación.

Para generarlo:

```powershell
python .\generate_summary.py --input .\input\transactions_50k.jsonl --output .\output\transactions_summary.parquet --json-output .\output\transactions_summary_validation.jsonl
```

El archivo será generado en:

```text
output/transactions_summary_validation.jsonl
```

Este archivo contiene la misma vista agregada generada en Parquet, pero en un formato más sencillo de inspeccionar.

La fecha se representa como `YYYY-MM-DD`. Por ejemplo:

```json
{"day":"2024-04-01","month":4,"year":2024,"bin":"400489","approved_transactions":1,"total_approved_amount":24995.53}
```

## Proceso

El script:

1. Lee las transacciones del archivo JSONL.
2. Extrae y transforma los campos necesarios.
3. Convierte `created_at` a una fecha válida.
4. Extrae el BIN desde `payment_method_type.extra.bin`.
5. Convierte `amount_in_cents` a un valor numérico.
6. Filtra únicamente las transacciones con estado `APPROVED`.
7. Agrupa las transacciones por día, mes, año y BIN.
8. Calcula la cantidad de transacciones aprobadas.
9. Calcula el monto total aprobado.
10. Genera el archivo Parquet.
11. Genera opcionalmente un archivo JSONL para validación.
12. Calcula un hash SHA-256 del archivo Parquet generado.

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
- El archivo JSONL de validación es opcional y no afecta el resultado principal del proceso.

## Archivos ignorados por Git

Por motivos de privacidad, los archivos que contienen información de transacciones o resultados generados no deben ser publicados en el repositorio.

El `.gitignore` excluye:

```text
input/*.jsonl
output/*.parquet
output/*.jsonl
```

También se excluyen archivos propios del entorno de desarrollo de Python, como:

```text
venv/
.venv/
__pycache__/
```

## Desactivar el entorno virtual

Una vez finalizado el procesamiento:

```powershell
deactivate
```

## Aviso de privacidad

El archivo `transactions_50k.jsonl` **no se incluye en este repositorio** debido a que contiene información personal asociada a las transacciones.

Los archivos generados a partir de estas transacciones, incluyendo el Parquet y el JSONL de validación, también están excluidos del repositorio.

El archivo de entrada debe ser suministrado de forma independiente y colocado en:

```text
input/transactions_50k.jsonl
```

No se deben publicar en el repositorio archivos que contengan información personal o datos sensibles.