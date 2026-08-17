# Wompi Reto 2
Pipeline en Python para procesar transacciones con tarjeta desde un archivo JSONL, filtrar las transacciones aprobadas y generar una vista agregada por día y BIN en formato Parquet.

## Install Python and update PIP
> PowerShell

* Instalar [Python 3.13](https://www.python.org/downloads/)
* Verificar la versión de Python: `python --version`
* Instalar y actualizar PIP: `python -m pip install --upgrade pip`

## Configure the virtual environment
> PowerShell

* Permitir la ejecución de scripts para activar un entorno virtual: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
* Instalar el paquete para crear entornos virtuales: `pip3 install virtualenv`
* Acceder a la carpeta del repositorio: `cd .\wompi_reto2\`
* Crear un entorno virtual: `python -m virtualenv venv`
* Activar el entorno virtual: `.\venv\Scripts\activate`
* Instalar las librerías requeridas: `pip3 install -r requirements.txt`

## Project Structure

```text
wompi_reto2/
│
├── generate_summary.py
├── transactions_50k.jsonl
├── output/
│   └── transactions_summary.parquet
├── requirements.txt
├── README.md
└── .gitignore