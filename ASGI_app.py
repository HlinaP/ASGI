import streamlit as st
import requests
import base64
import time
import random
import os

st.title("Stahování obrázků z prohlížečky ČGS")

# Uživatelské vstupy
username = st.text_input("Uživatelské jméno", )
password = st.text_input("Heslo", type="password")
agenda = st.text_input("Agenda ID (např. 45123)")
img_start = st.text_input("ID první stránky (např. MzY1OTc0MA==)")
img_end = st.text_input("ID poslední stránky (např. MzY1OTkyNA==)")
output_folder = st.text_input("Cesta k adresáři pro uložení", value=r"T:\OGGP_KNIHOVNA\ASGI")

if st.button("📥 Stáhnout obrázky"):
    if not all([username, password, agenda, img_start, img_end, output_folder]):
        st.error(" ❗ Vyplň prosím všechna pole")
    else:
        try:
            start_id = int(base64.b64decode(img_start).decode())
            end_id = int(base64.b64decode(img_end).decode())
        except Exception as e:
            st.error(f"Chyba při dekódování ID: {e}")
            st.stop()

        os.makedirs(output_folder, exist_ok=True)
        st.write("Aktuální pracovní adresář:", os.getcwd())
        st.write("Výstupní adresář:", os.path.abspath(output_folder))
        st.write("Adresář existuje:", os.path.exists(output_folder))

        session = requests.Session()
        session.auth = (username, password)

        with st.spinner("Stahuji obrázky..."):
            status_text = st.empty()
            for i in range(start_id, end_id + 1):
                kod = base64.b64encode(str(i).encode()).decode()
                url = f"https://docview.geology.cz/prohlizecka/ovladac.php?img={kod}&f=F&agenda={agenda}"

                try:
                    r = session.get(url)
                    content_type = r.headers.get("Content-Type", "")

                    if r.status_code == 200 and content_type.startswith("image"):
                        filename = os.path.join(output_folder, f"stranka_{i - start_id + 1}.jpg")
                        with open(filename, "wb") as f:
                            f.write(r.content)
                        status_text.success(f"Staženo: {filename}")
                        
                    else:
                        st.warning(f"Přeskočeno (neobrázkový obsah): {url}")
                except Exception as e:
                    st.error(f"Chyba u obrázku {i}: {e}")

                delay = random.uniform(7, 11)  # Kratší delay, ať to netrvá moc dlouho při testu
                time.sleep(delay)

        st.balloons()
        st.success("Hotovo!")
