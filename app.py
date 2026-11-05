# -*- coding: utf-8 -*-
"""
app.py — Boletín de Contratación (app web)
--------------------------------------------------------------------
App web en Streamlit: el usuario pega el link de Google Sheets
(formato CSV) y descarga el PDF del boletín, con el mismo diseño
exacto de la plantilla original de Canva.

CÓMO EJECUTARLA LOCALMENTE
--------------------------------------------------------------------
1) pip install streamlit reportlab pandas
2) streamlit run app.py

CÓMO PUBLICARLA GRATIS EN INTERNET
--------------------------------------------------------------------
Ver instrucciones en el archivo README.md que acompaña este proyecto.
--------------------------------------------------------------------
"""

import datetime
import re
import streamlit as st
import pandas as pd

from motor_boletin import generar_pdf_desde_url

st.set_page_config(
    page_title="Boletín de Contratación",
    page_icon="📄",
    layout="centered",
)

# ----------------------------------------------------------------
# Utilidad: convierte cualquier link de Google Sheets (de edición,
# de vista, etc.) a su versión de exportación CSV automáticamente.
# ----------------------------------------------------------------
def normalizar_link(url: str) -> str:
    url = url.strip()
    if not url:
        return url

    m = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
    if not m:
        return url  # no es un link reconocible de Sheets; se intenta tal cual
    file_id = m.group(1)

    gid_match = re.search(r"[?&#]gid=(\d+)", url)
    gid = gid_match.group(1) if gid_match else "0"

    return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv&gid={gid}"


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
2. Haz clic en la pestaña **`BOLETIN_CANVA`** (abajo, donde están los nombres
   de las hojas).
3. Copia la URL completa que aparece en la barra de direcciones del navegador
   (puede ser la de edición normal, por ejemplo `.../edit?gid=123456789`).
4. Pégala tal cual en el campo de abajo — **esta app la convierte
   automáticamente** al formato que necesita, no hace falta que la edites.
        """
    )

url_input = st.text_input(
    "Enlace de Google Sheets",
    placeholder="https://docs.google.com/spreadsheets/d/XXXXX/edit?gid=0#gid=0",
)

fecha_default = datetime.date.today()
fecha_sel = st.date_input("Fecha de actualización a mostrar en el boletín", value=fecha_default)
fecha_str = fecha_sel.strftime("%d/%m/%Y")

generar_btn = st.button("Generar boletín", type="primary", use_container_width=True)

if generar_btn:
    if not url_input.strip():
        st.warning("Por favor pega primero el enlace de tu Google Sheets.")
    else:
        link_final = normalizar_link(url_input)
        with st.spinner("Generando el boletín..."):
            try:
                pdf_bytes, n_proyectos = generar_pdf_desde_url(link_final, fecha_str)
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
