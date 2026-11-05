# Boletín de Contratación — App Web

App web en **Streamlit** que genera el Boletín de Contratación en PDF
(con el mismo diseño exacto de la plantilla original de Canva) a partir
de un enlace de Google Sheets. Solo pegas el link y descargas el PDF.

## Archivos del proyecto

```
app.py              -> interfaz web (lo que ve el usuario)
motor_boletin.py    -> motor que genera el PDF (colores, logo, tabla, footer)
requirements.txt    -> librerías necesarias
```

---

## Opción A (recomendada): publicarla gratis en internet con Streamlit Community Cloud

Así obtienes un link público tipo `https://tu-app.streamlit.app` que puedes
abrir desde cualquier computador o celular, sin instalar nada.

### Paso 1. Sube estos 3 archivos a GitHub

1. Crea una cuenta gratis en [github.com](https://github.com) si no tienes.
2. Crea un repositorio nuevo (puede ser privado o público), por ejemplo
   `boletin-contratacion`.
3. Sube los archivos `app.py`, `motor_boletin.py` y `requirements.txt`
   a ese repositorio (botón "Add file" → "Upload files").

### Paso 2. Conecta el repositorio a Streamlit Community Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io) e inicia sesión
   con tu cuenta de GitHub (es gratis).
2. Haz clic en **"New app"**.
3. Selecciona el repositorio `boletin-contratacion`.
4. En "Main file path" escribe: `app.py`.
5. Haz clic en **"Deploy"**.

En un par de minutos tendrás tu app publicada con un link que puedes
compartir con quien necesites (por ejemplo tu equipo de SISI Lab).

### Paso 3. Actualizaciones futuras

Cada vez que quieras cambiar algo del diseño, edita el archivo en GitHub
y la app se actualiza sola en unos segundos.

---

## Opción B: correrla en tu computador (sin publicarla)

Si solo la quieres usar tú, desde tu propio computador:

1. Instala Python si no lo tienes ([python.org](https://www.python.org/downloads/)).
2. Abre una terminal en la carpeta donde están estos 3 archivos.
3. Instala las librerías:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecuta la app:
   ```bash
   streamlit run app.py
   ```
5. Se abrirá automáticamente en tu navegador en `http://localhost:8501`.

---

## Cómo se usa la app (una vez publicada o corriendo)

1. Abre tu Google Sheets y asegúrate de que esté compartido como
   **"Cualquier persona con el enlace — Lector"** (botón *Compartir*).
2. Haz clic en la pestaña **`BOLETIN_CANVA`**.
3. Copia la URL completa de la barra de direcciones (puede ser la de
   edición normal, por ejemplo `.../edit?gid=123456789`).
4. Pégala tal cual en el campo de la app — **la app la convierte
   automáticamente** al formato que necesita, no hace falta editarla.
5. Elige la fecha de actualización que quieres mostrar en el boletín.
6. Haz clic en **"Generar boletín"** y luego en **"Descargar PDF"**.

Listo: cada vez que actualices tu Google Sheets, solo repites estos
pasos y obtienes el PDF actualizado, sin tocar Canva.
