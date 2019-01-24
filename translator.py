import os
import sys
import subprocess
import configparser
from math import ceil

import googletrans
import pycountry
import requests


class Translator:

    # some needed variables
    CHARS_PER_LINE = 75
    GTRANS_REAL_URL = "https://translate.google.com/#view=home&op=translate&sl={}&tl={}&text={}"
    GLOSBE_API_URL = "https://glosbe.com/gapi/translate?from={}&dest={}&phrase={}&format=json&pretty=false"
    GLOSBE_REAL_URL = "https://glosbe.com/{}/{}/{}"
    CONFIG_FILE_PATH = os.path.expanduser("~/.quick-translator.ini")

    def __init__(self):
        self.RESULT_IS_DICT_LOOKUP = False
        self._process_config()

    def _process_config(self):
        CONFIG_REWRITE_NEEDED = False
        # get config
        config = configparser.ConfigParser()
        config.read(self.CONFIG_FILE_PATH)
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
        self.src_lang = opts.get('source_lang', 'auto')
        self.dest_lang = opts.get('destination_lang', 'en')

        # save the config file if needed
        if CONFIG_REWRITE_NEEDED:
            with open(self.CONFIG_FILE_PATH, 'w+') as configfile:
                configfile.truncate(0)
                configfile.seek(0)
                config.write(configfile)

    def translate(self):
        # get the last selected text via xsel
        self.selected_text = self.get_currently_selected_or_copied_text()

        # initialize the translator and try to determine the source language for a dictionary lookup
        translator = googletrans.Translator()
        if self.src_lang == "auto":
            self.src_lang = translator.detect(self.selected_text).lang[:2]

        # convert the new source and defined destination languages into ISO-639-3 form
        try:
            ISO6393_src_lang = pycountry.languages.get(alpha_2=self.src_lang).alpha_3
            ISO6393_dest_lang = pycountry.languages.get(alpha_2=self.dest_lang).alpha_3
        except AttributeError:
            self.post_notification("Invalid source or destination language in config file?",
                              "The defined source or destination language is invalid! [S: {}; D: {}, Config file: {}]"
                              .format(self.src_lang, self.dest_lang, self.CONFIG_FILE_PATH))
            sys.exit(1)

        # build the needed urls
        this_glosbe_api_url = self.GLOSBE_API_URL.format(ISO6393_src_lang, ISO6393_dest_lang, self.selected_text)
        self.this_glosbe_url = self.GLOSBE_REAL_URL.format(self.src_lang, self.dest_lang, self.selected_text)
        self.this_gt_url = self.GTRANS_REAL_URL.format(self.src_lang, self.dest_lang, self.selected_text)

        # determine if a dictionary result is in order
        # only do this for source text that is sufficiently short
        if len(self.selected_text.split(" ")) < 5:
            self.rd = requests.get(this_glosbe_api_url).json()
            try:
                if len(self.rd["tuc"]) != 0:  # if we do have results...
                    self.RESULT_IS_DICT_LOOKUP = True
            except KeyError:
                pass  # keep RESULT_IS_DICT_LOOKUP as False

        # even if source lang == dest lang, Glosbe can still return a dictionary result, but a full translation makes no sense in this case
        # so if source lang == dest lang, but Glosbe did not return any results for this term, terminate here
        if self.src_lang == self.dest_lang and not self.RESULT_IS_DICT_LOOKUP:
            self.post_notification("No dictionary lookup results and nothing to translate!",
                              "The source and destination languages are the same. [{}]".format(self.src_lang))
            sys.exit(0)

        # determine the resulting window height and (if needed) full translation
        if self.RESULT_IS_DICT_LOOKUP:
            # rd = requests.get(this_glosbe_api_url).json()
            self.W_HEIGHT = 30
        else:
            self.translated_text = translator.translate(self.selected_text, src=self.src_lang, dest=self.dest_lang).text
            self.W_HEIGHT = ceil(len(self.selected_text) / self.CHARS_PER_LINE) + ceil(len(self.translated_text) / self.CHARS_PER_LINE) + 12

    def expand_results_to_dict(self):
        d = {
            'result_is_dict_lookup': self.RESULT_IS_DICT_LOOKUP,
            'src_lang': self.src_lang,
            'dest_lang': self.dest_lang,
            'selected_text': self.selected_text
        }
        if self.RESULT_IS_DICT_LOOKUP:
            d["outbound_url"] = self.this_glosbe_url
            d["_dict_resultd"] = self.rd
        else:
            d["outbound_url"] = self.this_gt_url
            d["_trans_translated_text"] = self.translated_text
        return d

    def expand_size_to_dict(self):
        return {
            "window_height": self.W_HEIGHT,
            "chars_per_line": self.CHARS_PER_LINE
        }

    @staticmethod
    def get_currently_selected_or_copied_text():
        from sys import platform
        if platform.startswith("linux") or platform.startswith('freebsd'):  # Linux/FreeBSD
            return subprocess.check_output(["xsel", "-o"]).decode().strip()
        elif platform == "darwin":  # Darwin/MacOS
            raise NotImplementedError("This program has not yet been implemented for MacOS.")
        elif platform == "win32":   # Windows
            raise NotImplementedError("This program has not yet been implemented for Windows.")

    @staticmethod
    def post_notification(title, body):
        from sys import platform
        if platform.startswith("linux") or platform.startswith("freebsd"):  # Linux/FreeBSD
            subprocess.call(['notify-send', "-i", "system-search", title, body])
        elif platform == "darwin":
            raise NotImplementedError("This program has not yet been implemented for MacOS.")
        elif platform == "win32":
            raise NotImplementedError("This program has not yet been implemented for Windows.")
