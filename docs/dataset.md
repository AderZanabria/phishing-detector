# Dataset

LegitPhish (Mendeley Data, DOI 10.17632/hx4m73v2sf.2, CC BY 4.0) tiene 101.219 URLs: 63.678 phishing y 37.540 legítimas. El archivo publicado es `url_features_extracted1.csv`.

Ficha: https://data.mendeley.com/datasets/hx4m73v2sf/2

```bash
curl -L -o ml/data/raw/legitphish.csv \
  "https://data.mendeley.com/public-files/datasets/hx4m73v2sf/files/0ed51e4d-d160-4047-b650-3f0801eea4aa/file_downloaded"
```

## Columnas

`URL`, 16 features (`url_length`, `has_ip_address`, `dot_count`, `https_flag`, `url_entropy`, `token_count`, `subdomain_count`, `query_param_count`, `tld_length`, `path_length`, `has_hyphen_in_domain`, `number_of_digits`, `tld_popularity`, `suspicious_file_extension`, `domain_name_length`, `percentage_numeric_chars`) y `ClassLabel`.

En el CSV, `ClassLabel` 0 es phishing y 1 es legítima. `load_dataset()` invierte eso.

## Reemplazo

Otro CSV sirve si trae una columna de URL y una etiqueta binaria reconocible (`ClassLabel`, `Label` o `label`). El entrenamiento usa las features del archivo, no las reextraídas. La inferencia sí reextrae con `extract_features_from_url`, así que el esquema tiene que coincidir.

## Ética

Las URLs de phishing son indicadores de amenaza. No las abras. El dataset no incluye contenido de páginas ni credenciales. Cita a los autores y respeta CC BY 4.0.
