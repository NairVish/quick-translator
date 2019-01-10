import re
import os
import html
import subprocess
import requests
import webbrowser
import configparser

from math import ceil

import pycountry

from googletrans import Translator
from tkinter import *


def clean_text(raw_str):
    """
    Cleans all normal HTML and bracket tags.
    :param raw_html: The input string that needs to be cleaned.
    :return: The cleaned string.
    """
    cleaner_regex = re.compile('(<.*?>|\[.*?\])')
    return re.sub(cleaner_regex, '', raw_str)


def open_link(event):
    """
    Opens the link connected to the widget whose event has been called.
    :param event: The click event.
    """
    webbrowser.open(event.widget.tag_names(CURRENT)[1])


def close(event):
    """
    Closes the window.
    :param event: The (unused) click event.
    """
    sys.exit(0)


def get_currently_selected_or_copied_text():
    from sys import platform
    if platform.startswith("linux") or platform.startswith('freebsd'):
        # linux
        return subprocess.check_output(["xsel", "-o"]).decode().strip()
    elif platform == "darwin":
        # OS X
        raise NotImplementedError("This program has not yet been implemented for MacOS.")
    elif platform == "win32":
        # Windows...
        raise NotImplementedError("This program has not yet been implemented for Windows.")


def post_notification(title, body):
    from sys import platform
    if platform.startswith("linux") or platform.startswith('freebsd'):
        # linux
        subprocess.call(['notify-send', "-i", "system-search", title, body])
    elif platform == "darwin":
        # OS X
        raise NotImplementedError("This program has not yet been implemented for MacOS.")
    elif platform == "win32":
        # Windows...
        raise NotImplementedError("This program has not yet been implemented for Windows.")


# some needed variables
CHARS_PER_LINE = 75
GTRANS_REAL_URL = "https://translate.google.com/#view=home&op=translate&sl={}&tl={}&text={}"
GLOSBE_API_URL = "https://glosbe.com/gapi/translate?from={}&dest={}&phrase={}&format=json&pretty=false"
GLOSBE_REAL_URL = "https://glosbe.com/{}/{}/{}"
CONFIG_FILE_PATH = os.path.expanduser("~/.quick-translator.ini")

if __name__ == "__main__":

    RESULT_IS_DICT_LOOKUP = False
    CONFIG_REWRITE_NEEDED = False

    # get config
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    try:
        config['TRANSLATION_OPTIONS']
    except KeyError:
        config['TRANSLATION_OPTIONS'] = {}
        CONFIG_REWRITE_NEEDED = True
    opts = config['TRANSLATION_OPTIONS']

    if 'source_lang' not in opts:
        config['TRANSLATION_OPTIONS']['source_lang'] = "auto"
        CONFIG_REWRITE_NEEDED = True
    if 'destination_lang' not in opts:
        config['TRANSLATION_OPTIONS']['destination_lang'] = "en"
        CONFIG_REWRITE_NEEDED = True

    # define source and destination languages using the config file
    SRC_LANG = opts.get('source_lang', 'auto')
    DEST_LANG = opts.get('destination_lang', 'en')

    # save the config file if needed
    if CONFIG_REWRITE_NEEDED:
        with open(CONFIG_FILE_PATH, 'w+') as configfile:
            configfile.truncate(0)
            configfile.seek(0)
            config.write(configfile)

    # get the last selected text via xsel
    selected_text = get_currently_selected_or_copied_text()

    # initialize the translator and try to determine the source language for a dictionary lookup
    translator = Translator()
    if SRC_LANG == "auto":
        SRC_LANG = translator.detect(selected_text).lang[:2]

    # convert the new source and defined destination languages into ISO-639-3 form
    try:
        ISO6393_src_lang = pycountry.languages.get(alpha_2=SRC_LANG).alpha_3
        ISO6393_dest_lang = pycountry.languages.get(alpha_2=DEST_LANG).alpha_3
    except AttributeError:
        post_notification("Invalid source or destination language in config file?",
                          "The defined source or destination language is invalid! [S: {}; D: {}, Config file: {}]"
                          .format(SRC_LANG, DEST_LANG, CONFIG_FILE_PATH))
        sys.exit(0)

    # build the needed urls
    this_glosbe_api_url = GLOSBE_API_URL.format(ISO6393_src_lang, ISO6393_dest_lang, selected_text)
    this_glosbe_url = GLOSBE_REAL_URL.format(SRC_LANG, DEST_LANG, selected_text)
    this_gt_url = GTRANS_REAL_URL.format(SRC_LANG, DEST_LANG, selected_text)

    # determine if a dictionary result is in order
    # only do this for source text that is sufficiently short
    if len(selected_text.split(" ")) < 5:
        rd = requests.get(this_glosbe_api_url).json()
        try:
            if len(rd["tuc"]) != 0: # if we do have results...
                RESULT_IS_DICT_LOOKUP = True
        except KeyError:
            pass  # keep RESULT_IS_DICT_LOOKUP as False

    # even if source lang == dest lang, Glosbe can still return a dictionary result, but a full translation makes no sense in this case
    # so if source lang == dest lang, but Glosbe did not return any results for this term, terminate here
    if SRC_LANG == DEST_LANG and not RESULT_IS_DICT_LOOKUP:
        post_notification("No dictionary lookup results and nothing to translate!",
                          "The source and destination languages are the same. [{}]".format(SRC_LANG))
        sys.exit(0)

    # determine the resulting window height and (if needed) full translation
    if RESULT_IS_DICT_LOOKUP:
        # rd = requests.get(this_glosbe_api_url).json()
        W_HEIGHT = 30
    else:
        translated_text = translator.translate(selected_text, src=SRC_LANG, dest=DEST_LANG).text
        W_HEIGHT = ceil(len(selected_text) / CHARS_PER_LINE) + ceil(len(translated_text) / CHARS_PER_LINE) + 12

    # build the window
    root = Tk()
    root.title('Translation Result' if not RESULT_IS_DICT_LOOKUP else "Lookup Result")
    root.bind('<Escape>', close)

    S = Scrollbar(root)
    S.pack(side=RIGHT, fill=Y)

    T = Text(root, height=W_HEIGHT, width=CHARS_PER_LINE, wrap=WORD)

    # configure some common tags and bindings
    T.tag_configure('main_header', font=('Times New Roman', 14, 'bold'))
    T.tag_configure('footer', font=('Times New Roman', 9))
    T.tag_configure('footer_link', foreground="blue", font=('Times New Roman', 9, 'underline'))
    T.tag_bind('footer_link', '<Button-1>', open_link)
    T.tag_configure('header_cont', font=('Times New Roman', 12))

    if not RESULT_IS_DICT_LOOKUP:   # if this is a full translation result...
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

    else:   # if this is a dictionary lookup result...
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
                phrase = html.unescape(d["phrase"]["text"]) # some Glosbe results have HTML entities so unescape them
            except KeyError:
                phrase = "---"

            T.insert(END, "{}\n".format(phrase), 'phrase_main')
            try:
                all_meanings = d["meanings"]
            except KeyError:
                all_meanings = []

            for m in all_meanings:
                T.insert(END, "\t* {} [{}]\n".format(clean_text(html.unescape(m["text"])), m["language"]), 'phrase_meaning')

            T.insert(END, "\tSource(s): ", 'phrase_meaning_source')
            for a in d["authors"]:
                T.insert(END, "{} ".format(sources[str(a)]["N"]), ('phrase_meaning_source_link', sources[str(a)]["url"]))
            T.insert(END, "\n\n")

    T.pack(side=LEFT, fill=Y)
    mainloop()