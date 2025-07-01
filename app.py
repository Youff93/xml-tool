import streamlit as st
import csv
import re
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

menu = st.sidebar.radio("Navigation", ["📌 Extraction", "🔄 Remplacement"])

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
        
        remplacements = {}
        csv_reader = csv.DictReader(StringIO(csv_content), delimiter=";")
        for row in csv_reader:
            ancien = row['ancien'].strip()
            nouveau = row['nouveau'].strip()
            remplacements[ancien] = nouveau
        
        def remplacer_name(match):
            original = match.group(1).strip()
            remplacant = remplacements.get(original, original)
            return f"<Name>{remplacant}</Name>"
        
        new_content = re.sub(r"<Name>\s*(.*?)\s*</Name>", remplacer_name, xml_content)
        
        st.success("✅ Remplacements effectués.")
        
        st.download_button(
            "⬇️ Télécharger le XML transformé",
            data=new_content,
            file_name="xml_modifie.xml",
            mime="application/xml"
        )

st.markdown("---")
st.caption("🛠️ Développé avec Python & Streamlit — adapté à vos besoins. 🚀")
