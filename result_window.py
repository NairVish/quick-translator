import html
import tkinter as tk
import webbrowser
from tkinter import *


class ResultWindow(tk.Tk):

    def __init__(self, window_height: int, chars_per_line: int, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.chars_per_line = chars_per_line

        # build initial components of the window
        self.bind('<Escape>', ResultWindow.close)

        S = Scrollbar(self)
        S.pack(side=RIGHT, fill=Y)

        self.T = Text(self, height=window_height, width=chars_per_line, wrap=WORD)

        # configure some common tags and bindings
        self.T.tag_configure('main_header', font=('Times New Roman', 14, 'bold'))
        self.T.tag_configure('footer', font=('Times New Roman', 9))
        self.T.tag_configure('footer_link', foreground="blue", font=('Times New Roman', 9, 'underline'))
        self.T.tag_bind('footer_link', '<Button-1>', self.open_link)
        self.T.tag_configure('header_cont', font=('Times New Roman', 12))

    def build_result_window(self,
                            result_is_dict_lookup: bool,
                            src_lang: str,
                            dest_lang: str,
                            outbound_url: str,
                            selected_text: str,
                            _trans_translated_text: str = "",
                            _dict_resultd: dict = None):
        self.title('Translation Result' if not result_is_dict_lookup else "Lookup Result")
        if not result_is_dict_lookup:
            self._build_trans_window(src_lang, dest_lang, outbound_url, selected_text, self.chars_per_line,
                                     _trans_translated_text)
        else:  # not result_is_dict_lookup
            self._build_dict_window(src_lang, dest_lang, outbound_url, selected_text, _dict_resultd)
        self.T.pack(side=LEFT, fill=Y)

    def _build_trans_window(self, src_lang, dest_lang, this_gt_url, selected_text, chars_per_line, translated_text):
        # SRC_LANG, DEST_LANG, this_gt_url, selected_text, CHARS_PER_LINE, translated_text
        self.T.tag_configure('sect_header', font=('Times New Roman', 12, 'italic'))
        self.T.tag_configure('text', font=('Times New Roman', 12, 'bold'))

        self.T.insert(END, "Text translation results ({} to {})\n".format(src_lang.upper(), dest_lang.upper()),
                      'main_header')
        self.T.insert(END, "Translation by Google Translate. ", 'footer')
        self.T.insert(END, "View online.", ('footer_link', this_gt_url))
        self.T.insert(END, "\n\n")

        self.T.insert(END, "Source ({}):\n\n".format(src_lang), 'sect_header')
        self.T.insert(END, "{}".format(selected_text), 'text')
        self.T.insert(END, "\n\n{}\n\n".format('-' * chars_per_line))
        self.T.insert(END, "Translation ({}):\n\n".format(dest_lang), 'sect_header')
        self.T.insert(END, "{}".format(translated_text), 'text')

    def _build_dict_window(self, src_lang, dest_lang, this_glosbe_url, selected_text, rd):
        # SRC_LANG, DEST_LANG, this_glosbe_url, selected_text, rd
        self.T.tag_configure('phrase_main', font=('Times New Roman', 12, 'italic'))
        self.T.tag_configure('phrase_meaning', font=('Times New Roman', 11))
        self.T.tag_configure('phrase_meaning_source', font=('Times New Roman', 8))
        self.T.tag_configure('phrase_meaning_source_link', foreground="blue",
                             font=('Times New Roman', 8, 'underline'))

        self.T.tag_bind('phrase_meaning_source_link', '<Button-1>', ResultWindow.open_link)

        defs = rd["tuc"]
        sources = rd["authors"]

        self.T.insert(END, "{}\n".format(selected_text), 'main_header')
        self.T.insert(END, "Dictionary lookup results ({} to {})\n".format(src_lang.upper(), dest_lang.upper()),
                      'header_cont')
        self.T.insert(END, "Lookup results from Glosbe. ", 'footer')
        self.T.insert(END, "View detailed results online.", ('footer_link', this_glosbe_url))
        self.T.insert(END, "\n\n")

        for d in defs:
            try:
                phrase = html.unescape(d["phrase"]["text"])  # some Glosbe results have HTML entities so unescape them
            except KeyError:
                phrase = "---"

            self.T.insert(END, "{}\n".format(phrase), 'phrase_main')
            try:
                all_meanings = d["meanings"]
            except KeyError:
                all_meanings = []

            for m in all_meanings:
                self.T.insert(END, "\t* {} [{}]\n".format(ResultWindow.clean_text(html.unescape(m["text"])), m["language"]),
                              'phrase_meaning')

            self.T.insert(END, "\tSource(s): ", 'phrase_meaning_source')
            for a in d["authors"]:
                self.T.insert(END, "{} ".format(sources[str(a)]["N"]),
                              ('phrase_meaning_source_link', sources[str(a)]["url"]))
            self.T.insert(END, "\n\n")

    @staticmethod
    def clean_text(raw_str):
        """
        Cleans all normal HTML and bracket tags.
        :param raw_html: The input string that needs to be cleaned.
        :return: The cleaned string.
        """
        cleaner_regex = re.compile('(<.*?>|\[.*?\])')
        return re.sub(cleaner_regex, '', raw_str)

    @staticmethod
    def open_link(event):
        """
        Opens the link connected to the widget whose event has been called.
        :param event: The click event.
        """
        webbrowser.open(event.widget.tag_names(CURRENT)[1])

    @staticmethod
    def close(event):
        """
        Closes the window.
        :param event: The (unused) click event.
        """
        sys.exit(0)