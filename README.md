# Quick Translator

A simple application that that translates the currently selected text and pops the results up in a simple window.
Small phrases or simple words are first looked up in a multilingual dictionary ([Glosbe](https://glosbe.com/) via their [API](https://glosbe.com/a-api)).
If the word/phrase doesn't exist or if the selected text is relatively long, it is then translated (Google Translate via [googletrans](https://github.com/ssut/py-googletrans)).
As a consequence of how Glosbe's API works, same-language lookups usually work too.

## Screenshots

_Regular dictionary lookup_

![Regular dictionary lookup screenshot](https://vnair.me/images/hotlink-ok/qtrans/reg-dict.png)

_Regular translation_

![Regular translation screenshot](https://vnair.me/images/hotlink-ok/qtrans/reg-trans.png)

_Same-language lookup_

![Same language lookup screenshot](https://vnair.me/images/hotlink-ok/qtrans/same-lang-dict.png)

## Language Configuration

On the first run, a configuration file is created at `~/.quick-translator.ini`, which looks like this:

```
[TRANSLATION_OPTIONS]
source_lang = auto
destination_lang = en
```

The `auto` option uses Google Translate's language detection and works most of the time, but there may be many instances
where it does not work correctly. To force the program to use a pre-defined source language, change `source_lang`
to any [valid, 2-letter ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) language code. The same goes
if you want to use a destination language other than English.

Any language that Google Translate supports can be used here.
Though note that Glosbe may not necessarily support all of these languages, and thus you will only get translation results for these languages.

## Usage/Installation

To use this, you would need to install the requirements listed in `requirements.txt`, including tkinter (which would vary by distribution).
You could use [Pyinstaller](http://www.pyinstaller.org/) to generate an executable file that bundles all of the files, including dependencies together into one executable. (Remember to use the `--onefile` option!)
Then, using built-in system utility or a third-party utility, this executable can then be bound to a keyboard shortcut.

Once that's done, just select the text you want to translate and hit the shortcut you defined. You can hit the Escape button to quickly exit the window.

## TODOs

This is still very much a work-in-progress.

- [ ] (Possibly) rewrite in another language/framework for better/easier cross-platform installation and usage.
- [ ] Monitor in the background for a pre-defined shortcut.
- [ ] Expand to other platforms.
