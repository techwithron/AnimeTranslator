from flask import Flask, request, send_file, render_template_string
from deep_translator import GoogleTranslator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

app = Flask(__name__)

HTML_PAGE = """
<h2>Naruto Subtitle Translator</h2>
<form method="post" enctype="multipart/form-data">
<input type="file" name="file">
<button type="submit">Translate</button>
</form>
"""

def clean_roman(text):
    replacements = {
        ".n":"n",
        "~":"n",
        "nahim":"nahi",
        "haim":"hai",
        "kaha.n":"kahan",
        "yaha.n":"yahan",
        "pahu.ncha":"pahuncha",
        "tuma":"tum",
        "hama":"hum",
        "apa":"aap"
    }

    for k,v in replacements.items():
        text = text.replace(k,v)

    return text

@app.route("/", methods=["GET","POST"])
def index():

    if request.method == "POST":

        file = request.files["file"]
        input_file = "input.vtt"
        output_file = "output.vtt"

        file.save(input_file)

        with open(input_file,"r",encoding="utf-8") as f:
            lines = f.readlines()

        text_lines = []
        indexes = []

        for i,line in enumerate(lines):
            if line.strip() and "-->" not in line and not line.startswith("WEBVTT"):
                text_lines.append(line.strip())
                indexes.append(i)

        translated = []

        for text in text_lines:

            hindi = GoogleTranslator(source="en", target="hi").translate(text)

            roman = transliterate(hindi, sanscript.DEVANAGARI, sanscript.ITRANS)

            roman = clean_roman(roman.lower())

            translated.append(roman)

        for idx,new_text in zip(indexes,translated):
            lines[idx] = new_text + "\n"

        with open(output_file,"w",encoding="utf-8") as f:
            f.writelines(lines)

        return send_file(output_file, as_attachment=True)

    return render_template_string(HTML_PAGE)

app.run(host="0.0.0.0", port=10000)