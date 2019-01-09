import subprocess
import requests
import webbrowser

from math import ceil

import pycountry

from googletrans import Translator
from tkinter import *


def open_link(event):
    webbrowser.open(event.widget.tag_names(CURRENT)[1])


SRC_LANG = "auto"  # can use auto for auto-detect
DEST_LANG = "en" # keep as default lang

CHARS_PER_LINE = 75
RESULT_IS_DICT_LOOKUP = False
GTRANS_REAL_URL = "https://translate.google.com/#view=home&op=translate&sl={}&tl={}&text={}"
GLOSBE_API_URL = "https://glosbe.com/gapi/translate?from={}&dest={}&phrase={}&format=json&pretty=false"
GLOSBE_REAL_URL = "https://glosbe.com/{}/{}/{}"

selected_text = subprocess.check_output(["xsel", "-o"]).decode().strip()

translator = Translator()
if SRC_LANG == "auto":
    SRC_LANG = translator.detect(selected_text).lang[:2]

try:
    ISO6393_src_lang = pycountry.languages.get(alpha_2=SRC_LANG).alpha_3
    ISO6393_dest_lang = pycountry.languages.get(alpha_2=DEST_LANG).alpha_3
except AttributeError:
    subprocess.call(['notify-send', "-i", "system-search", "Invalid source or destination language?",
                     "The desired source or destination language is invalid! [S: {}; D: {}]".format(SRC_LANG, DEST_LANG)])

if SRC_LANG == DEST_LANG:
    subprocess.call(['notify-send', "-i", "system-search", "Nothing to translate!", "The source and destination languages are the same! [{}]".format(SRC_LANG)])
    sys.exit(0)

this_glosbe_api_url = GLOSBE_API_URL.format(ISO6393_src_lang, ISO6393_dest_lang, selected_text)
this_glosbe_url = GLOSBE_REAL_URL.format(SRC_LANG, DEST_LANG, selected_text)
this_gt_url = GTRANS_REAL_URL.format(SRC_LANG, DEST_LANG, selected_text)

if len(selected_text.split(" ")) < 5:
    rd = requests.get(this_glosbe_api_url).json()
    try:
        if len(rd["tuc"]) != 0:
            RESULT_IS_DICT_LOOKUP = True
    except KeyError:
        pass  # keep RESULT_IS_DICT_LOOKUP as False

if RESULT_IS_DICT_LOOKUP:
    rd = requests.get(this_glosbe_api_url).json()
    W_HEIGHT = 30
else:
    translated_text = translator.translate(selected_text, src=SRC_LANG, dest=DEST_LANG).text
    W_HEIGHT = ceil(len(selected_text) / CHARS_PER_LINE) + ceil(len(translated_text) / CHARS_PER_LINE) + 12

root = Tk()
root.title('Translation Result' if not RESULT_IS_DICT_LOOKUP else "Lookup Result")
S = Scrollbar(root)
S.pack(side=RIGHT, fill=Y)
T = Text(root, height=W_HEIGHT, width=CHARS_PER_LINE, wrap=WORD)

T.tag_configure('main_header', font=('Times New Roman', 14, 'bold'))
T.tag_configure('footer', font=('Times New Roman', 9))
T.tag_configure('footer_link', foreground="blue", font=('Times New Roman', 9, 'underline'))
T.tag_bind('footer_link', '<Button-1>', open_link)
T.tag_configure('header_cont', font=('Times New Roman', 12))

if not RESULT_IS_DICT_LOOKUP:
    T.tag_configure('sect_header', font=('Times New Roman', 12, 'italic'))
    T.tag_configure('text', font=('Times New Roman', 12, 'bold'))

    T.insert(END, "Text translation results ({} to {})\n".format(SRC_LANG.upper(), DEST_LANG.upper()), 'main_header')
    T.insert(END, "Translation by Google Translate. ", 'footer')
    T.insert(END, "View online.", ('footer_link', this_gt_url))
    T.insert(END, "\n\n")

    T.insert(END, "Source ({}):\n\n".format(SRC_LANG), 'sect_header')
    T.insert(END, "{}".format(selected_text), 'text')
    T.insert(END, "\n\n{}\n\n".format('-'*CHARS_PER_LINE))
    T.insert(END, "Translation ({}):\n\n".format(DEST_LANG), 'sect_header')
    T.insert(END, "{}".format(translated_text), 'text')

else:
    T.tag_configure('phrase_main', font=('Times New Roman', 12, 'italic'))
    T.tag_configure('phrase_meaning', font=('Times New Roman', 11))
    T.tag_configure('phrase_meaning_source', font=('Times New Roman', 8))
    T.tag_configure('phrase_meaning_source_link', foreground="blue", font=('Times New Roman', 8, 'underline'))

    T.tag_bind('phrase_meaning_source_link', '<Button-1>', open_link)

    defs = rd["tuc"]
    sources = rd["authors"]

    T.insert(END, "{}\n".format(selected_text), 'main_header')
    T.insert(END, "Dictionary lookup results ({} to {})\n".format(SRC_LANG.upper(), DEST_LANG.upper()), 'header_cont')
    T.insert(END, "Lookup results from Glosbe. ", 'footer')
    T.insert(END, "View detailed results online.", ('footer_link', this_glosbe_url))
    T.insert(END, "\n\n")

    for d in defs:
        try:
            phrase = d["phrase"]["text"]
        except KeyError:
            phrase = "---"

        T.insert(END, "{}\n".format(phrase), 'phrase_main')
        try:
            all_meanings = d["meanings"]
        except KeyError:
            all_meanings = []

        for m in all_meanings:
            T.insert(END, "\t* {} [{}]\n".format(m["text"], m["language"]), 'phrase_meaning')

        T.insert(END, "\tSource(s): ", 'phrase_meaning_source')
        for a in d["authors"]:
            T.insert(END, "{} ".format(sources[str(a)]["N"]), ('phrase_meaning_source_link', sources[str(a)]["url"]))
        T.insert(END, "\n\n")

T.pack(side=LEFT, fill=Y)
mainloop()