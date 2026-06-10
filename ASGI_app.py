import streamlit as st
import requests
import base64
import time
import random
import zipfile
from io import BytesIO

st.title("Stahování obrázků z prohlížečky ČGS")

# Uživatelské vstupy
username = st.text_input("Uživatelské jméno")
password = st.text_input("Heslo", type="password")
agenda = st.text_input("Agenda ID (např. 45123)")
img_start = st.text_input("ID první stránky (např. MzY1OTc0MA==)")
img_end = st.text_input("ID poslední stránky (např. MzY1OTkyNA==)")

if st.button("📥 Stáhnout obrázky"):

    if not all([username, password, agenda, img_start, img_end]):
        st.error("❗ Vyplň prosím všechna pole")
        st.stop()

    try:
        start_id = int(base64.b64decode(img_start).decode())
        end_id = int(base64.b64decode(img_end).decode())
    except Exception as e:
        st.error(f"Chyba při dekódování ID: {e}")
        st.stop()

    session = requests.Session()
    session.auth = (username, password)

    zip_buffer = BytesIO()

    total = end_id - start_id + 1
    progress = st.progress(0)
    status_text = st.empty()

    downloaded = 0

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:

        for index, i in enumerate(range(start_id, end_id + 1), start=1):

            kod = base64.b64encode(str(i).encode()).decode()

            url = (
                f"https://docview.geology.cz/prohlizecka/"
                f"ovladac.php?img={kod}&f=F&agenda={agenda}"
            )

            try:
                r = session.get(url, timeout=30)
                content_type = r.headers.get("Content-Type", "")

                if r.status_code == 200 and content_type.startswith("image"):

                    filename = f"stranka_{index}.jpg"

                    # PŘÍMO do ZIPu (žádný disk)
                    zipf.writestr(filename, r.content)

                    downloaded += 1
                    status_text.info(f"Staženo {index}/{total}")

                else:
                    status_text.warning(
                        f"Přeskočeno {index} (status={r.status_code}, typ={content_type})"
                    )

            except Exception as e:
                status_text.error(f"Chyba u obrázku {index}: {e}")

            progress.progress(index / total)

            time.sleep(random.uniform(7, 11))

    zip_buffer.seek(0)

    if downloaded == 0:
        st.error("Nepodařilo se stáhnout žádné obrázky.")
        st.stop()

    st.success(f"Hotovo! Staženo {downloaded} obrázků.")

    st.download_button(
        label="📦 Stáhnout ZIP s obrázky",
        data=zip_buffer,
        file_name=f"agenda_{agenda}.zip",
        mime="application/zip"
    )

    st.balloons()
