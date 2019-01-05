import subprocess

from googletrans import Translator

selected_text = subprocess.check_output(["xsel", "-o"]).decode().strip()

translator = Translator()
t = translator.translate(selected_text, src="fr", dest='en').text

subprocess.call(['notify-send', "-i", "system-search", selected_text, t])

