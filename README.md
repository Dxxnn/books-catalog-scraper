# Books Catalog Scraper

Proyecto de portafolio en Python para extraer, limpiar y estructurar el catálogo
público de [Books to Scrape](https://books.toscrape.com/), un sitio ficticio
creado expresamente como entorno seguro de práctica para web scraping.

El flujo usa `requests` y `BeautifulSoup` para recorrer páginas del catálogo,
normaliza los registros con `pandas` y genera archivos CSV y JSON listos para
análisis. La implementación incorpora comprobación de `robots.txt`, pausas
entre solicitudes, reintentos moderados, límites de recorrido, logs y pruebas
unitarias sin tráfico de red.

## Qué demuestra

- Extracción de HTML paginado con selectores CSS estables.
- Validación de `robots.txt` antes de solicitar cada URL.
- Sesión HTTP con `User-Agent` identificable, timeout, reintentos y backoff.
- Límite configurable de páginas y pausa mínima de 0,5 segundos.
- Limpieza, tipado, deduplicación y ordenamiento con `pandas`.
- Exportación a `books.csv`, `books.json` y `summary.json`.
- Registro de ejecución y manejo explícito de errores.
- Pruebas unitarias para parsing, política de robots, configuración y exportación.

## Fuente y uso responsable

La fuente es un catálogo ficticio de 1.000 libros publicado por
[ToScrape](https://toscrape.com/) para aprender y validar tecnologías de
scraping. No requiere autenticación ni JavaScript y no contiene datos
personales.

Antes de cada recorrido, el programa solicita `/robots.txt`:

- si existe, aplica sus reglas y cualquier `Crawl-delay`;
- si responde `404`, interpreta que no hay reglas publicadas y mantiene sus
  propios límites conservadores;
- si ocurre otro error al consultar la política, detiene la ejecución.

El proyecto no intenta evadir CAPTCHA, autenticación, controles antibot ni
restricciones técnicas. La configuración predeterminada recorre cinco páginas,
espera un segundo entre solicitudes y nunca permite más de 50 páginas por
ejecución. Consulta también [ETHICS.md](ETHICS.md).

## Estructura

```text
.
├── data/output/                  # Resultados locales (ignorados por Git)
├── src/books_catalog_scraper/
│   ├── cli.py                    # Interfaz de línea de comandos
│   ├── config.py                 # Límites y configuración
│   ├── exporter.py               # CSV, JSON y resumen
│   ├── http_client.py            # Sesión, reintentos y pausas
│   ├── models.py                 # Modelo de registro
│   ├── parser.py                 # Extracción del HTML
│   ├── pipeline.py               # Orquestación del recorrido
│   └── robots.py                 # Política robots.txt
├── tests/                        # Pruebas sin acceso a Internet
├── .github/workflows/tests.yml   # Integración continua
├── ETHICS.md
├── LICENSE
├── pyproject.toml
└── requirements.txt
```

## Instalación

Requiere Python 3.10 o superior.

```bash
cd books-catalog-scraper
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

En Windows PowerShell, activa el entorno con:

```powershell
.venv\Scripts\Activate.ps1
```

## Ejecución

Recorrido responsable de tres páginas:

```bash
books-catalog-scraper --max-pages 3 --delay 1.0
```

También puede ejecutarse como módulo:

```bash
python -m books_catalog_scraper --max-pages 3 --output-dir data/output
```

Opciones principales:

```text
--max-pages     Número de páginas (1-50; predeterminado: 5)
--delay         Pausa mínima entre solicitudes (>= 0,5 s)
--output-dir    Carpeta para CSV y JSON
--log-file      Archivo local de logs
--base-url      URL inicial; se conserva para facilitar pruebas controladas
```

## Resultados

`books.csv` y `books.json` contienen:

| Campo | Descripción |
| --- | --- |
| `title` | Título normalizado |
| `price_gbp` | Precio convertido a número |
| `availability` | Texto de disponibilidad |
| `in_stock` | Indicador booleano |
| `rating` | Calificación de 1 a 5 |
| `product_url` | URL pública normalizada |
| `source_page` | Página de origen |
| `scraped_at_utc` | Marca de tiempo UTC de extracción |

`summary.json` resume cantidad de registros, precios, disponibilidad y
distribución de calificaciones.

## Pruebas

Las pruebas usan HTML sintético local y no hacen solicitudes externas:

```bash
python -m unittest discover -s tests -v
```

## Publicación en GitHub

Si el repositorio todavía no existe en GitHub, una sesión autenticada de
GitHub CLI permite crearlo y publicar el commit local:

```bash
gh auth login
gh auth status
gh repo create Dxxnn/books-catalog-scraper \
  --public \
  --source=. \
  --remote=origin \
  --push \
  --description "Responsible Python scraper for a public practice catalogue"
```

Después de publicarlo, otras personas podrán clonarlo con:

```bash
git clone https://github.com/Dxxnn/books-catalog-scraper.git
```

## Alcance y limitaciones

- La estructura HTML pertenece a un sandbox y puede cambiar.
- Los datos son demostrativos; no representan inventario comercial real.
- El resumen es descriptivo y no busca inferir demanda ni comportamiento.
- Un `robots.txt` permisivo no reemplaza la revisión de términos y contexto.

## Licencia

[MIT](LICENSE).
