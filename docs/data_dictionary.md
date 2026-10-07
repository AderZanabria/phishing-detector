# Diccionario de datos

## Etiqueta

| Origen LegitPhish | Significado original | `label` en el pipeline |
| --- | --- | --- |
| 0 | phishing | 1 |
| 1 | legítima | 0 |

La inversión es `label = 1 - ClassLabel` y se aplica solo en `load_dataset()`.

## Features (entrenamiento = columnas del CSV)

| Feature | Tipo | Descripción |
| --- | --- | --- |
| url_length | int | Caracteres de la URL |
| has_ip_address | 0/1 | El host es una IP |
| dot_count | int | Número de puntos |
| https_flag | 0/1 | Esquema HTTPS |
| url_entropy | float | Entropía de Shannon |
| token_count | int | Tokens alfanuméricos |
| subdomain_count | int | Subdominios por encima del dominio registrable |
| query_param_count | int | Parámetros de query |
| tld_length | int | Longitud del TLD |
| path_length | int | Longitud del path |
| has_hyphen_in_domain | 0/1 | Guion en el hostname |
| number_of_digits | int | Dígitos en la URL |
| tld_popularity | 0/1 | TLD en la lista de populares |
| suspicious_file_extension | 0/1 | Extensión de fichero sospechosa en el path |
| domain_name_length | int | Longitud del nombre registrable |
| percentage_numeric_chars | float | Porcentaje de dígitos |

`extract_features_from_url()` recalcula este mismo esquema para URLs fuera del CSV.
Si las definiciones del CSV difieren en algún borde (TLD compuesto, lista de extensiones),
la inferencia puede desviarse; en ese caso regenera las features con esta función y reentrena.
