from translator import Translator
from result_window import ResultWindow

if __name__ == "__main__":
    t = Translator()
    t.translate()
    w = ResultWindow(**(t.expand_size_to_dict()))
    w.build_result_window(**(t.expand_results_to_dict()))
    w.mainloop()
