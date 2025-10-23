import json
import datetime
from xml.etree.ElementTree import Element, SubElement, tostring

# 1️⃣ Lire les notes depuis JSON
with open("notes.json", "r", encoding="utf-8") as f:
    notes = json.load(f)

# 2️⃣ Créer la structure RSS
rss = Element('rss', version='2.0')
channel = SubElement(rss, 'channel')
SubElement(channel, 'title').text = "🛠️ Le Fil de Nicolas – Équipe Tech"
SubElement(channel, 'link').text = "https://intranet.exemple.com"
SubElement(channel, 'description').text = "Un petit fil sympa pour partager astuces, updates et infos utiles avec toute l'équipe."
SubElement(channel, 'lastBuildDate').text = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

# 3️⃣ Ajouter les notes au flux
for note in notes:
    item = SubElement(channel, 'item')
    for key, value in note.items():
        SubElement(item, key).text = value

# 4️⃣ Écrire le RSS dans un fichier XML
with open("feed.xml", "wb") as f:
    f.write(tostring(rss, encoding="utf-8"))
