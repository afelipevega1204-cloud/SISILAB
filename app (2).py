# -*- coding: utf-8 -*-
"""
app.py — Boletín de Contratación (app web, PDF)
--------------------------------------------------------------------
El usuario pega el link de Google Sheets y descarga el PDF del boletín.

NOVEDAD: sección "Logo del boletín"
  - Subir un PNG para cambiar el logo.
  - Ajustar su tamaño.
  - "Guardar logo" lo deja fijo para la próxima vez.
  - "Volver al logo original" restaura el logo SISILab.

CÓMO EJECUTARLA LOCALMENTE
  1) pip install -r requirements.txt
  2) streamlit run app.py
--------------------------------------------------------------------
"""

import io
import os
import re
import json
import base64
import datetime
import urllib.request

import pandas as pd
import streamlit as st
from PIL import Image

import motor_boletin as motor

st.set_page_config(page_title="Boletín de Contratación", page_icon="📄", layout="centered")

BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_LOGO = os.path.join(BASE, "logo_boletin_guardado.png")
RUTA_CONFIG = os.path.join(BASE, "config_boletin.json")


# ----------------------------------------------------------------
# Guardado permanente (servidor + GitHub opcional mediante Secrets)
# ----------------------------------------------------------------
def _github_disponible():
    try:
        return bool(st.secrets.get("GITHUB_TOKEN")) and bool(st.secrets.get("GITHUB_REPO"))
    except Exception:
        return False


def _github(nombre_archivo, contenido=None, mensaje="Actualiza archivo", borrar=False):
    token = st.secrets["GITHUB_TOKEN"]
    repo = st.secrets["GITHUB_REPO"]
    rama = st.secrets.get("GITHUB_BRANCH", "main")
    url = "https://api.github.com/repos/" + repo + "/contents/" + nombre_archivo
    headers = {"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
               "User-Agent": "boletin-pdf-app"}
    sha = None
    try:
        with urllib.request.urlopen(urllib.request.Request(url + "?ref=" + rama, headers=headers),
                                    timeout=20) as r:
            sha = json.loads(r.read())["sha"]
    except Exception:
        pass
    if borrar:
        if not sha:
            return
        cuerpo = {"message": mensaje, "sha": sha, "branch": rama}
        metodo = "DELETE"
    else:
        cuerpo = {"message": mensaje, "content": base64.b64encode(contenido).decode(), "branch": rama}
        if sha:
            cuerpo["sha"] = sha
        metodo = "PUT"
    req = urllib.request.Request(url, data=json.dumps(cuerpo).encode(), headers=headers, method=metodo)
    urllib.request.urlopen(req, timeout=30)


def leer_config():
    cfg = {"escala_logo": 100}
    if os.path.exists(RUTA_CONFIG):
        try:
            with open(RUTA_CONFIG, encoding="utf-8") as f:
                cfg.update(json.load(f))
        except Exception:
            pass
    return cfg


def leer_logo_guardado():
    if os.path.exists(RUTA_LOGO):
        with open(RUTA_LOGO, "rb") as f:
            return f.read()
    return None


def guardar_todo(logo_bytes, escala):
    contenido_cfg = json.dumps({"escala_logo": escala}, indent=2).encode("utf-8")
    with open(RUTA_CONFIG, "wb") as f:
        f.write(contenido_cfg)
    if logo_bytes:
        with open(RUTA_LOGO, "wb") as f:
            f.write(logo_bytes)
    elif os.path.exists(RUTA_LOGO):
        os.remove(RUTA_LOGO)

    if _github_disponible():
        _github("config_boletin.json", contenido_cfg, "Actualiza configuración del boletín PDF")
        if logo_bytes:
            _github("logo_boletin_guardado.png", logo_bytes, "Actualiza logo del boletín PDF")
        else:
            _github("logo_boletin_guardado.png", borrar=True, mensaje="Restaura logo original")
        return "servidor y GitHub"
    return "servidor"


def a_png(img):
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


# ----------------------------------------------------------------
# Estado inicial
# ----------------------------------------------------------------
if "iniciado" not in st.session_state:
    st.session_state["logo_bytes"] = leer_logo_guardado()
    st.session_state["escala_logo"] = int(leer_config().get("escala_logo", 100))
    st.session_state["iniciado"] = True


def volver_logo_original():
    st.session_state["logo_bytes"] = None
    st.session_state.pop("firma_logo", None)


# ----------------------------------------------------------------
# Utilidad: convierte cualquier link de Google Sheets a CSV
# ----------------------------------------------------------------
def normalizar_link(url: str) -> str:
    url = url.strip()
    if not url:
        return url
    m = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
    if not m:
        return url
    file_id = m.group(1)
    gid_match = re.search(r"[?&#]gid=(\d+)", url)
    gid = gid_match.group(1) if gid_match else "0"
    return "https://docs.google.com/spreadsheets/d/" + file_id + "/export?format=csv&gid=" + gid


# ----------------------------------------------------------------
# Interfaz
# ----------------------------------------------------------------
st.title("📄 Boletín de Contratación")
st.write(
    "Pega el enlace de tu Google Sheets (pestaña **BOLETIN_CANVA**) y genera "
    "automáticamente el boletín en PDF, con el mismo diseño de la plantilla original."
)

with st.expander("ℹ️ ¿Cómo obtengo el enlace correcto?", expanded=False):
    st.markdown(
        """
1. Abre tu Google Sheets y asegúrate de que esté compartido como **"Cualquier
   persona con el enlace - Lector"** (botón *Compartir*, arriba a la derecha).
2. Haz clic en la pestaña **`BOLETIN_CANVA`**.
3. Copia la URL completa de la barra de direcciones.
4. Pégala tal cual abajo: **la app la convierte automáticamente**.
        """
    )

# ---------------- LOGO ----------------
with st.expander("🏢 Logo del boletín", expanded=False):
    st.caption("Sube el logo en **PNG con fondo transparente** (ideal). Si trae un fondo de un "
               "solo color, la app lo quita sola. El logo se ajusta a la plantilla sin deformarse.")
    archivo = st.file_uploader("Subir nuevo logo", type=["png", "jpg", "jpeg", "webp"])
    if archivo is not None:
        firma = (archivo.name, archivo.size)
        if st.session_state.get("firma_logo") != firma:
            st.session_state["logo_bytes"] = a_png(Image.open(archivo).convert("RGBA"))
            st.session_state["firma_logo"] = firma

    logo_vista = motor.obtener_logo(st.session_state.get("logo_bytes"))
    muestra = Image.new("RGBA", (logo_vista.width + 60, logo_vista.height + 40), (246, 246, 246, 255))
    muestra.alpha_composite(logo_vista, (30, 20))
    st.image(muestra.convert("RGB"),
             caption=("Logo personalizado" if st.session_state.get("logo_bytes") else "Logo original")
             + " · así se verá en el boletín", width=420)

    st.slider("Tamaño del logo (%)", min_value=40, max_value=160, step=5, key="escala_logo")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Guardar logo", type="primary", use_container_width=True):
            try:
                donde = guardar_todo(st.session_state.get("logo_bytes"), st.session_state["escala_logo"])
                st.success(f"Logo guardado en el {donde}.")
            except Exception as e:
                st.error(f"No se pudo guardar: {e}")
    with c2:
        st.button("↩️ Volver al logo original", use_container_width=True, on_click=volver_logo_original)
    if not _github_disponible():
        st.caption("ℹ️ Para que el logo guardado no se pierda si la app se reinicia, configura los "
                   "*Secrets* GITHUB_TOKEN y GITHUB_REPO en Streamlit.")

# ---------------- GENERAR ----------------
url_input = st.text_input(
    "Enlace de Google Sheets",
    placeholder="https://docs.google.com/spreadsheets/d/XXXXX/edit?gid=0#gid=0",
)

fecha_sel = st.date_input("Fecha de actualización a mostrar en el boletín", value=datetime.date.today(),
                          format="DD/MM/YYYY")
fecha_str = fecha_sel.strftime("%d/%m/%Y")

if st.button("Generar boletín", type="primary", use_container_width=True):
    if not url_input.strip():
        st.warning("Por favor pega primero el enlace de tu Google Sheets.")
    else:
        link_final = normalizar_link(url_input)
        with st.spinner("Generando el boletín..."):
            try:
                pdf_bytes, n_proyectos = motor.generar_pdf_desde_url(
                    link_final, fecha_str,
                    logo_bytes=st.session_state.get("logo_bytes"),
                    escala_logo=st.session_state.get("escala_logo", 100),
                )
            except ValueError as e:
                st.error(f"Hubo un problema con las columnas de tu hoja:\n\n{e}")
            except pd.errors.ParserError:
                st.error(
                    "No se pudo leer la hoja como datos tabulares. Verifica que "
                    "el enlace apunte a la pestaña correcta y que esté compartida "
                    "como 'Cualquier persona con el enlace'."
                )
            except Exception as e:
                st.error(f"Ocurrió un error inesperado: {e}")
            else:
                st.success(f"¡Listo! Se generaron {n_proyectos} proyectos en el boletín.")
                st.download_button(
                    label="⬇️ Descargar PDF",
                    data=pdf_bytes,
                    file_name="Boletin_Contratacion.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

st.divider()
st.caption(
    "SISI Lab · Sistema de Información del Sector de la Infraestructura y "
    "Laboratorio de Gestión · Cámara Colombiana de la Infraestructura, Seccional Norte."
)
