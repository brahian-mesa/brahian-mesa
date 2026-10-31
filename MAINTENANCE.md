# Mantenimiento del perfil

El perfil se orienta a frontend y backend. Formación, ubicación, inglés y participación en proyectos fueron confirmados por Brahian. Las tecnologías y funcionalidades se basan en los archivos revisados de cada repositorio. Se conservan los proyectos aprobados; SmartStock no se incorpora.

## Actualización de commits

- El generador usa la API pública de GitHub. Enumera repositorios públicos propios y excluye forks, archivados y privados.
- Lee las ramas predeterminadas y los commits cuyo autor está asociado a `brahian-mesa`.
- Cuenta SHA únicos en los últimos 28 días según la fecha de autor en UTC.
- No incluye commits de organizaciones ni privados. No representa el calendario completo de contribuciones de GitHub.
- Si alcanza el límite de paginación, el README indica que el recuento puede ser parcial. Si falla la API, el proceso falla y conserva el último resumen publicado.
- Los asuntos de commit se escapan antes de introducirlos en Markdown. No se publica el cuerpo de los commits.
- `assets/activity.json` contiene el estado, `assets/activity.svg` la gráfica y el README los seis últimos cambios.

El workflow se ejecuta diariamente a las 11:23 UTC (06:23 en Colombia), manualmente desde Actions o al cambiar sus fuentes en `main`. GitHub puede retrasar ejecuciones programadas. Solo crea un commit si hay cambios; no fabrica actividad. Usa el token automático del repositorio y no necesita token personal.

## Desarrollo local

Requiere Python 3.12 o posterior, sin paquetes externos.

```sh
python -m unittest discover -s scripts -p 'test_*.py' -v
python scripts/update_activity.py
```

Sin `GITHUB_TOKEN`, se aplican los límites públicos sin autenticación. Nunca guardar credenciales ni imprimir el token.

## Interacción y diseño

El README usa enlaces, imágenes y secciones desplegables `details`; no ejecuta JavaScript. Banner y gráfica se sirven desde el propio repositorio. Los iconos usan skillicons.dev y tienen texto alternativo y una lista textual equivalente.

Referencias: [README de perfil](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme), [API de commits](https://docs.github.com/en/rest/commits/commits), [permisos de Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions).
