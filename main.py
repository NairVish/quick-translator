import subprocess
import requests

import tkinter as tk
from tkinterhtml import HtmlFrame
from googletrans import Translator

bulk_text_translation_html = """
<p style="font-size: 24px; font-weight: bold;">%s</p>
<hr>
<p style="font-size: 24px; font-style: oblique;">%s</p>
"""

selected_text = subprocess.check_output(["xsel", "-o"]).decode().strip()

translator = Translator()
t = translator.translate(selected_text, src="fr", dest='en').text

# subprocess.call(['notify-send', "-i", "system-search", selected_text, t])

root = tk.Tk()

frame = HtmlFrame(root, vertical_scrollbar="auto")
frame.set_content(bulk_text_translation_html % (selected_text, t))

frame.pack()
root.mainloop()
