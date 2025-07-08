import streamlit as st
import csv
import re
import os
import zipfile
import tempfile
from io import StringIO


st.set_page_config(page_title="XML Tools", page_icon="🔧", layout="wide")

st.title("🔧 XML Tools : Extraction & Remplacement de balises <Name>")

st.markdown(
    """
    Cet outil vous permet de :
    1. Extraire les balises `<Name>` d’un XML et générer un CSV à éditer
    2. Réinjecter ce CSV modifié pour générer un XML final
    """
)

menu = st.sidebar.radio(
    "Navigation",
    ["📌 Extraction", "🔄 Remplacement", "📁 Extraction multiple", "🔁 Remplacement multiple"]
)



if menu == "📌 Extraction":
    st.header("Étape 1 : Extraction des balises <Name> vers un CSV")
    xml_file = st.file_uploader("Sélectionnez votre fichier XML", type="xml")
    
    if xml_file:
        xml_content = xml_file.read().decode("utf-8")
        valeurs = re.findall(r"<Name>\s*(.*?)\s*</Name>", xml_content)
        valeurs_uniques = sorted(set(v.strip() for v in valeurs))
        
        st.success(f"{len(valeurs_uniques)} balises <Name> détectées.")
        
        output = StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["ancien", "nouveau"])
        for v in valeurs_uniques:
            writer.writerow([v, ""])
        
        st.download_button(
            "⬇️ Télécharger le CSV à remplir",
            data=output.getvalue(),
            file_name="extraction.csv",
            mime="text/csv"
        )

if menu == "🔄 Remplacement":
    st.header("Étape 2 : Remplacement dans le XML avec un CSV")

    xml_file = st.file_uploader("Sélectionnez le XML d'origine", type="xml")
    csv_file = st.file_uploader("Sélectionnez le CSV de correspondances", type="csv")

    if xml_file and csv_file:
        xml_content = xml_file.read().decode("utf-8")
        csv_content = csv_file.read().decode("utf-8")

        # récupérer les balises <Name> existantes
        noms_existants = re.findall(r"<Name>\s*(.*?)\s*</Name>", xml_content)
        noms_final_utilisés = {}

        remplacements = {}
        csv_reader = csv.DictReader(StringIO(csv_content), delimiter=";")
        for row in csv_reader:
            ancien = row['ancien'].strip()
            nouveau = row['nouveau'].strip()
            # si vide, on garde l'ancien nom
            if nouveau == "":
                remplacements[ancien] = ancien
            else:
                remplacements[ancien] = nouveau

        st.info(f"{len(remplacements)} correspondances chargées.")
        with st.expander("🔍 Table des remplacements"):
            for k, v in remplacements.items():
                st.write(f"**{k}** → {v}")

        # compteur global pour suffixes
        suffixes_utilisés = {}

        def nom_unique(nom):
            base = nom
            compteur = 0
            while nom in noms_final_utilisés:
                compteur += 1
                nom = f"{base} ({compteur})"
            noms_final_utilisés[nom] = True
            return nom

        def remplacer_name(match):
            original = match.group(1).strip()
            nouveau_nom = remplacements.get(original, original).strip()
            nom_final = nom_unique(nouveau_nom)

            if original != nom_final:
                st.write(f"Remplacement : '{original}' → '{nom_final}'")

            return f"<Name>{nom_final}</Name>"

        new_content = re.sub(r"<Name>\s*(.*?)\s*</Name>", remplacer_name, xml_content)

        st.success("✅ Remplacements appliqués avec gestion des doublons.")
        st.download_button(
            "⬇️ Télécharger le XML transformé",
            data=new_content,
            file_name="xml_modifie.xml",
            mime="application/xml"
        )


import os
import zipfile
import tempfile

if menu == "📁 Extraction multiple":
    st.header("📁 Extraction groupée de plusieurs fichiers XML")

    uploaded_files = st.file_uploader(
        "Déposez plusieurs fichiers XML ici",
        type="xml",
        accept_multiple_files=True
    )

    if uploaded_files:
        all_names = set()
        for file in uploaded_files:
            try:
                xml_content = file.read().decode("utf-8")
                noms = re.findall(r"<Name>\s*(.*?)\s*</Name>", xml_content)
                all_names.update(n.strip() for n in noms)
            except Exception as e:
                st.error(f"Erreur avec le fichier {file.name} : {e}")

        if all_names:
            valeurs_uniques = sorted(all_names)

            output = StringIO()
            writer = csv.writer(output, delimiter=";")
            writer.writerow(["ancien", "nouveau"])
            for name in valeurs_uniques:
                writer.writerow([name, ""])

            st.success(f"{len(valeurs_uniques)} balises uniques extraites de {len(uploaded_files)} fichiers.")
            st.download_button(
                "⬇️ Télécharger le CSV global à éditer",
                data=output.getvalue(),
                file_name="extraction_globale.csv",
                mime="text/csv"
            )
        else:
            st.warning("Aucune balise <Name> détectée dans les fichiers fournis.")


elif menu == "🔁 Remplacement multiple":

    st.header("🔁 Remplacement groupé sur plusieurs XML")

    uploaded_xmls = st.file_uploader(
        "Sélectionnez plusieurs fichiers XML",
        type="xml",
        accept_multiple_files=True
    )

    csv_file = st.file_uploader("Sélectionnez le CSV de correspondances", type="csv")

    if uploaded_xmls and csv_file:
        csv_content = csv_file.read().decode("utf-8")

        remplacements = {}
        csv_reader = csv.DictReader(StringIO(csv_content), delimiter=";")
        for row in csv_reader:
            ancien = row['ancien'].strip()
            nouveau = row['nouveau'].strip()
            remplacements[ancien] = nouveau if nouveau else ancien

        st.info(f"{len(remplacements)} correspondances chargées pour tous les fichiers.")

        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "modifiés.zip")

            with zipfile.ZipFile(zip_path, "w") as zipf:
                for xml_file in uploaded_xmls:
                    xml_content = xml_file.read().decode("utf-8")
                    noms_final_utilisés = {}

                    def nom_unique(nom):
                        base = nom
                        compteur = 0
                        while nom in noms_final_utilisés:
                            compteur += 1
                            nom = f"{base} ({compteur})"
                        noms_final_utilisés[nom] = True
                        return nom

                    def remplacer_name(match):
                        original = match.group(1).strip()
                        nouveau_nom = remplacements.get(original, original).strip()
                        nom_final = nom_unique(nouveau_nom)
                        return f"<Name>{nom_final}</Name>"

                    contenu_modifie = re.sub(r"<Name>\s*(.*?)\s*</Name>", remplacer_name, xml_content)

                    nom_modifie = f"{os.path.splitext(xml_file.name)[0]}_modifie.xml"
                    chemin_modifie = os.path.join(temp_dir, nom_modifie)
                    with open(chemin_modifie, "w", encoding="utf-8") as f:
                        f.write(contenu_modifie)

                    zipf.write(chemin_modifie, arcname=nom_modifie)

            with open(zip_path, "rb") as f:
                st.download_button(
                    "⬇️ Télécharger tous les XML modifiés (ZIP)",
                    data=f.read(),
                    file_name="xml_modifies.zip",
                    mime="application/zip"
                )



st.markdown("---")
st.caption("🛠️ Développé avec Python & Streamlit — adapté à vos besoins. 🚀")
