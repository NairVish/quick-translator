import subprocess
import requests
import webbrowser
from math import ceil
from googletrans import Translator
from tkinter import *


def open_link(event):
   webbrowser.open(event.widget.tag_names(CURRENT)[1])


SRC_LANG = "fr"  # can use auto for auto-detect
DEST_LANG = "en" # keep as default lang
CHARS_PER_LINE = 75

bulk_text_translation_html = """
<p style="font-size: 24px; font-weight: bold;">{}</p>
<hr>
<p style="font-size: 24px; font-style: oblique;">{}</p>
<p>Translation from Google Translate. <a href="{}">View online.</a></p>
"""
GTRANS_REAL_URL = "https://translate.google.com/#view=home&op=translate&sl={}&tl={}&text={}"

selected_text = subprocess.check_output(["xsel", "-o"]).decode().strip()

translator = Translator()
translated_text = translator.translate(selected_text, src=SRC_LANG, dest=DEST_LANG).text
# subprocess.call(['notify-send', "-i", "system-search", selected_text, translated_text])
this_gt_url = GTRANS_REAL_URL.format(SRC_LANG, DEST_LANG, selected_text)
W_HEIGHT = ceil(len(selected_text)/CHARS_PER_LINE) + ceil(len(translated_text)/CHARS_PER_LINE) + 11

root = Tk()
S = Scrollbar(root)
T = Text(root, height=W_HEIGHT, width=CHARS_PER_LINE, wrap=WORD)

T.tag_configure('header', font=('Times New Roman', 12))
T.tag_configure('text', font=('Times New Roman', 12, 'bold'))
T.tag_configure('footer', font=('Times New Roman', 9))
T.tag_configure('footer_link', foreground="blue", font=('Times New Roman', 9, 'underline'))
T.tag_bind('footer_link', '<Button-1>', open_link)

T.insert(END, "Source ({}):\n\n".format(SRC_LANG), 'header')
T.insert(END, "{}".format(selected_text), 'text')
T.insert(END, "\n\n{}\n\n".format('-'*75))
T.insert(END, "Translation ({}):\n\n".format(DEST_LANG), 'header')
T.insert(END, "{}".format(translated_text), 'text')

T.insert(END, "\n\nTranslation by Google Translate. ", 'footer')
T.insert(END, "View online.", ('footer_link', this_gt_url))

S.pack(side=RIGHT, fill=Y)
T.pack(side=LEFT, fill=Y)
mainloop()