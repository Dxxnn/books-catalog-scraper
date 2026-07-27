# Uso responsable

Este proyecto fue diseñado para demostrar web scraping de bajo impacto sobre
una fuente que invita explícitamente a practicar automatización.

## Principios aplicados

1. Se usa únicamente información pública y ficticia.
2. Se consulta `robots.txt` antes de iniciar y antes de solicitar cada página.
3. La ausencia de `robots.txt` no elimina los límites internos del programa.
4. Se aplica una pausa mínima de 0,5 segundos y un máximo de 50 páginas.
5. Los reintentos son moderados y respetan `Retry-After`.
6. No se usan credenciales, proxies, CAPTCHA solvers ni técnicas de evasión.
7. No se extraen datos personales ni se intenta identificar personas.
8. Los resultados se destinan a aprendizaje, pruebas y portafolio.

Antes de reutilizar el código con otra fuente, se deben revisar sus términos,
`robots.txt`, límites, licencia, jurisdicción y alternativas oficiales como
APIs o descargas de datos abiertos. Si existe duda sobre la autorización, no se
debe ejecutar el scraper.
