"""Корпусный менеджер — Лабораторная работа №2, вариант 21 (английский язык, предметная область: Музыка)."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import time
import logging
import sys

_eyaziis = Path(__file__).resolve().parent.parent
lab2 = Path(__file__).resolve().parent
if str(_eyaziis) not in sys.path:
    sys.path.insert(0, str(_eyaziis))
if str(lab2) not in sys.path:
    sys.path.insert(0, str(lab2))

try:
    from lab_2.text_extractor import extract_text_from_file
    from lab_2.corpus import Corpus, POS_LABELS
except ImportError:
    from text_extractor import extract_text_from_file
    from corpus import Corpus, POS_LABELS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("CorpusManager")
try:
    fh = logging.FileHandler(Path(__file__).parent / "corpus_app.log", encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(fh)
except Exception:
    pass


class CorpusManagerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Корпусный менеджер — Вариант 21 (English, Music)")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)

        self.corpus = Corpus("Music Corpus (Variant 21)")
        self.selected_doc_indices = None  # None = все документы
        self._build_ui()
        self._create_help_content()

    def _build_ui(self):
        top = ttk.Frame(self.root, padding=5)
        top.pack(fill=tk.X)

        ttk.Button(top, text="Добавить документы", command=self.add_documents).pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="Сохранить корпус", command=self.save_corpus).pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="Загрузить корпус", command=self.load_corpus).pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="Справка", command=self.show_help).pack(side=tk.RIGHT, padx=2)

        # Поиск
        search_frame = ttk.LabelFrame(self.root, text="Поиск в корпусе", padding=5)
        search_frame.pack(fill=tk.X, padx=5, pady=2)
        row1 = ttk.Frame(search_frame)
        row1.pack(fill=tk.X)
        ttk.Label(row1, text="Запрос (слово или фраза):").pack(side=tk.LEFT, padx=2)
        self.query_var = tk.StringVar()
        self.query_entry = ttk.Entry(row1, textvariable=self.query_var, width=35)
        self.query_entry.pack(side=tk.LEFT, padx=2)
        self.query_entry.bind("<Return>", lambda e: self.do_search())
        ttk.Button(row1, text="Найти", command=self.do_search).pack(side=tk.LEFT, padx=2)
        self.search_by = tk.StringVar(value="lemma")
        ttk.Radiobutton(row1, text="По лемме", variable=self.search_by, value="lemma").pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(row1, text="По словоформе", variable=self.search_by, value="word").pack(side=tk.LEFT, padx=2)
        ttk.Label(row1, text="Контекст (слов):").pack(side=tk.LEFT, padx=(10, 2))
        self.context_var = tk.StringVar(value="5")
        ttk.Spinbox(row1, from_=1, to=20, textvariable=self.context_var, width=4).pack(side=tk.LEFT, padx=2)

        self.notebook = ttk.Notebook(self.root, padding=5)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка: Документы корпуса
        doc_frame = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(doc_frame, text="Документы корпуса")
        cols = ("title", "author", "year", "tokens")
        self.doc_tree = ttk.Treeview(doc_frame, columns=cols, show="headings", height=12, selectmode="extended")
        self.doc_tree.heading("title", text="Название")
        self.doc_tree.heading("author", text="Автор")
        self.doc_tree.heading("year", text="Год")
        self.doc_tree.heading("tokens", text="Токенов")
        for c in cols:
            self.doc_tree.column(c, width=200)
        scroll_doc = ttk.Scrollbar(doc_frame, orient=tk.VERTICAL, command=self.doc_tree.yview)
        self.doc_tree.configure(yscrollcommand=scroll_doc.set)
        self.doc_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_doc.pack(side=tk.RIGHT, fill=tk.Y)
        self.doc_tree.bind("<Double-1>", self.on_doc_double_click)
        ttk.Button(doc_frame, text="Обновить список", command=self._refresh_docs_tab).pack(anchor=tk.W, pady=2)
        ttk.Button(doc_frame, text="Использовать выбранные для фильтра", command=self.set_filter_docs).pack(anchor=tk.W, padx=2)
        ttk.Button(doc_frame, text="Сбросить фильтр (все документы)", command=self.reset_filter).pack(anchor=tk.W, padx=2)
        ttk.Button(doc_frame, text="Удалить выбранный документ", command=self.remove_document).pack(anchor=tk.W, padx=2)

        # Вкладка: Частоты
        freq_frame = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(freq_frame, text="Частотные характеристики")
        self.freq_sub = ttk.Notebook(freq_frame)
        self.freq_sub.pack(fill=tk.BOTH, expand=True)
        for name, col in [("Словоформы", "word"), ("Леммы", "lemma"), ("Части речи (POS)", "pos")]:
            f = ttk.Frame(self.freq_sub)
            self.freq_sub.add(f, text=name)
            tv = ttk.Treeview(f, columns=("item", "freq", "extra"), show="headings", height=15)
            tv.heading("item", text="Форма / Лемма / POS")
            tv.heading("freq", text="Частота")
            tv.heading("extra", text="Описание (для POS)")
            tv.column("item", width=250)
            tv.column("freq", width=100)
            tv.column("extra", width=200)
            scroll = ttk.Scrollbar(f, orient=tk.VERTICAL, command=tv.yview)
            tv.configure(yscrollcommand=scroll.set)
            tv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scroll.pack(side=tk.RIGHT, fill=tk.Y)
            setattr(self, f"freq_tree_{col}", tv)
        ttk.Button(freq_frame, text="Обновить частоты", command=self._refresh_frequencies).pack(anchor=tk.W, pady=2)

        # Вкладка: Конкорданс
        conc_frame = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(conc_frame, text="Конкорданс")
        self.conc_tree = ttk.Treeview(conc_frame, columns=("left", "center", "right", "doc"), show="headings", height=18)
        self.conc_tree.heading("left", text="Слева")
        self.conc_tree.heading("center", text="Слово")
        self.conc_tree.heading("right", text="Справа")
        self.conc_tree.heading("doc", text="Документ")
        self.conc_tree.column("left", width=280)
        self.conc_tree.column("center", width=120)
        self.conc_tree.column("right", width=280)
        self.conc_tree.column("doc", width=150)
        scroll_conc = ttk.Scrollbar(conc_frame, orient=tk.VERTICAL, command=self.conc_tree.yview)
        self.conc_tree.configure(yscrollcommand=scroll_conc.set)
        self.conc_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_conc.pack(side=tk.RIGHT, fill=tk.Y)

        # Вкладка: Морфология леммы
        morph_frame = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(morph_frame, text="Морфология леммы")
        ttk.Label(morph_frame, text="Введите лемму и нажмите «Показать» (или используйте результат поиска):").pack(anchor=tk.W)
        row_m = ttk.Frame(morph_frame)
        row_m.pack(fill=tk.X)
        self.lemma_var = tk.StringVar()
        ttk.Entry(row_m, textvariable=self.lemma_var, width=25).pack(side=tk.LEFT, padx=2)
        ttk.Button(row_m, text="Показать морфологию", command=self.show_morphology).pack(side=tk.LEFT, padx=2)
        self.morph_tree = ttk.Treeview(morph_frame, columns=("word", "pos", "pos_label", "count"), show="headings", height=12)
        self.morph_tree.heading("word", text="Словоформа")
        self.morph_tree.heading("pos", text="POS")
        self.morph_tree.heading("pos_label", text="Описание")
        self.morph_tree.heading("count", text="Частота")
        for c in ("word", "pos", "pos_label", "count"):
            self.morph_tree.column(c, width=120)
        scroll_m = ttk.Scrollbar(morph_frame, orient=tk.VERTICAL, command=self.morph_tree.yview)
        self.morph_tree.configure(yscrollcommand=scroll_m.set)
        self.morph_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_m.pack(side=tk.RIGHT, fill=tk.Y)

        # Метаданные документа
        meta_frame = ttk.LabelFrame(self.notebook, text="Метаданные документа", padding=5)
        self.notebook.add(meta_frame, text="Метаданные")
        self.meta_text = scrolledtext.ScrolledText(meta_frame, wrap=tk.WORD, height=10, font=("TkDefaultFont", 10))
        self.meta_text.pack(fill=tk.BOTH, expand=True)
        ttk.Label(meta_frame, text="Выберите документ в списке «Документы корпуса» и перейдите сюда — метаданные подтянутся при поиске или здесь:").pack(anchor=tk.W)
        ttk.Button(meta_frame, text="Показать метаданные выбранного документа", command=self.show_metadata).pack(anchor=tk.W, pady=2)

        # Блок для удобного замера времени операций, используемых в отчёте
        bench_frame = ttk.LabelFrame(self.root, text="Замер времени (операции для отчёта)", padding=5)
        bench_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(
            bench_frame,
            text="Поиск по лемме 'music'",
            command=self.bench_search_music,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            bench_frame,
            text="Конкорданс по 'concert'",
            command=self.bench_concord_concert,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            bench_frame,
            text="Обновить частоты (benchmark)",
            command=self.bench_freq_update,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            bench_frame,
            text="Морфология леммы 'instrument'",
            command=self.bench_morph_instrument,
        ).pack(side=tk.LEFT, padx=2)

        self.status_var = tk.StringVar(value="Готово. Добавьте документы (TXT, RTF, PDF, DOC, DOCX) или загрузите корпус.")
        ttk.Label(self.root, textvariable=self.status_var).pack(anchor=tk.W, padx=5, pady=2)

    def _create_help_content(self):
        self.help_text = """
Справка. Корпусный менеджер — Лабораторная работа №2, вариант 21.
Язык: английский. Предметная область: Музыка.

1) Добавить документы — выбор одного или нескольких файлов форматов TXT, RTF, PDF, DOC, DOCX. Текст извлекается, размечается (лемматизация и части речи) и добавляется в корпус.

2) Сохранить / Загрузить корпус — корпус сохраняется в JSON (все документы, токены, метаданные) для последующей работы без повторной загрузки файлов.

3) Поиск — введите слово или фразу в поле «Запрос». «По лемме» — поиск по словарной форме, «По словоформе» — по точному вхождению. После нажатия «Найти» обновляются вкладки «Конкорданс» и «Частотные характеристики» (при необходимости нажмите «Обновить частоты»).

4) Документы корпуса — список всех документов. Двойной щелчок открывает просмотр текста. «Использовать выбранные для фильтра» — последующий поиск и частоты только по выбранным документам. «Сбросить фильтр» — снова учитываются все документы.

5) Частотные характеристики — частоты словоформ, лемм и частей речи (POS) по корпусу (или по отфильтрованному подмножеству). Обновить: кнопка «Обновить частоты».

6) Конкорданс — контексты вхождений запроса (слева — центр — справа). Размер контекста задаётся в поле «Контекст (слов)».

7) Морфология леммы — для введённой леммы показываются все словоформы, части речи и частоты (используются результаты лабораторной работы №1).

8) Метаданные — библиографические и типологические данные выбранного документа (название, автор, год, источник, путь к файлу, число токенов).

Поддерживаемые форматы: TXT, RTF, PDF, DOC, DOCX.
        """

    def add_documents(self):
        paths = filedialog.askopenfilenames(
            title="Выберите документы",
            filetypes=[
                ("Текст", "*.txt"),
                ("RTF", "*.rtf"),
                ("PDF", "*.pdf"),
                ("Word DOCX", "*.docx"),
                ("Word DOC", "*.doc"),
                ("Все", "*.*"),
            ],
        )
        if not paths:
            return
        added = 0
        t0 = time.perf_counter()
        for path in paths:
            text = extract_text_from_file(path)
            if self.corpus.add_document(path, text, lang="english"):
                added += 1
            else:
                logger.warning("Не удалось добавить: %s", path)
        elapsed = time.perf_counter() - t0
        self._refresh_docs_tab()
        self._refresh_frequencies()
        self.status_var.set(f"Добавлено документов: {added} из {len(paths)} за {elapsed:.2f} с. Всего в корпусе: {len(self.corpus.documents)}")

    def save_corpus(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Все", "*.*")],
        )
        if not path:
            return
        t0 = time.perf_counter()
        self.corpus.save(path)
        elapsed = time.perf_counter() - t0
        self.status_var.set(f"Корпус сохранён: {path} за {elapsed:.2f} с")

    def load_corpus(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json"), ("Все", "*.*")],
        )
        if not path:
            return
        t0 = time.perf_counter()
        if self.corpus.load(path):
            self.selected_doc_indices = None
            self._refresh_docs_tab()
            self._refresh_frequencies()
            elapsed = time.perf_counter() - t0
            self.status_var.set(f"Корпус загружен: {path}, документов: {len(self.corpus.documents)} за {elapsed:.2f} с")
        else:
            messagebox.showerror("Ошибка", "Не удалось загрузить файл.")

    def _refresh_docs_tab(self):
        for i in self.doc_tree.get_children(""):
            self.doc_tree.delete(i)
        for idx, doc in enumerate(self.corpus.documents):
            n = len(doc.get("tokens", []))
            self.doc_tree.insert("", tk.END, values=(
                doc.get("title", "")[:50],
                doc.get("author", "")[:30],
                doc.get("year", ""),
                n,
            ), iid=str(idx), tags=(str(idx),))

    def set_filter_docs(self):
        sel = self.doc_tree.selection()
        if not sel:
            messagebox.showinfo("Подсказка", "Выберите один или несколько документов в списке.")
            return
        self.selected_doc_indices = [int(i) for i in sel]
        self.status_var.set(f"Фильтр: {len(self.selected_doc_indices)} документов. Обновите частоты или выполните поиск.")

    def reset_filter(self):
        self.selected_doc_indices = None
        self.status_var.set("Фильтр сброшен — учитываются все документы.")

    def remove_document(self):
        sel = self.doc_tree.selection()
        if not sel:
            messagebox.showinfo("Подсказка", "Выберите документ для удаления.")
            return
        idx = int(sel[0])
        if messagebox.askyesno("Подтверждение", "Удалить выбранный документ из корпуса?"):
            self.corpus.remove_document(idx)
            self._refresh_docs_tab()
            self._refresh_frequencies()
            self.status_var.set("Документ удалён.")

    def on_doc_double_click(self, event):
        sel = self.doc_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        if idx < 0 or idx >= len(self.corpus.documents):
            return
        doc = self.corpus.documents[idx]
        win = tk.Toplevel(self.root)
        win.title(doc.get("title", "Документ"))
        win.geometry("700x500")
        st = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("TkDefaultFont", 10))
        st.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        st.insert(tk.END, doc.get("text", ""))
        st.config(state=tk.DISABLED)

    def do_search(self):
        if not self.corpus.documents:
            messagebox.showinfo("Подсказка", "Корпус пуст. Добавьте документы.")
            return
        query = (self.query_var.get() or "").strip()
        if not query:
            self.status_var.set("Введите запрос.")
            return
        by = self.search_by.get() or "lemma"
        try:
            ctx = int(self.context_var.get())
        except (ValueError, TypeError):
            ctx = 5
        t0 = time.perf_counter()
        concordance = self.corpus.get_concordance(
            query, by=by, context_size=ctx,
            doc_indices=self.selected_doc_indices, max_lines=500,
        )
        elapsed = time.perf_counter() - t0
        for i in self.conc_tree.get_children(""):
            self.conc_tree.delete(i)
        for line in concordance:
            self.conc_tree.insert("", tk.END, values=(
                line["left"][-120:] if len(line["left"]) > 120 else line["left"],
                line["center"],
                line["right"][:120] if len(line["right"]) > 120 else line["right"],
                line["doc_title"][:30] if line.get("doc_title") else "",
            ))
        self.lemma_var.set(query.split()[0] if " " in query else query)
        self.show_morphology()
        self.status_var.set(f"Найдено вхождений: {len(concordance)} за {elapsed:.2f} с")

    def _refresh_frequencies(self):
        doc_indices = self.selected_doc_indices
        # Словоформы
        wf = self.corpus.get_word_form_frequencies(doc_indices)
        for i in self.freq_tree_word.get_children(""):
            self.freq_tree_word.delete(i)
        for word, freq in list(wf.items())[:500]:
            self.freq_tree_word.insert("", tk.END, values=(word, freq, ""))

        # Леммы
        lf = self.corpus.get_lemma_frequencies(doc_indices)
        for i in self.freq_tree_lemma.get_children(""):
            self.freq_tree_lemma.delete(i)
        for lemma, freq in list(lf.items())[:500]:
            self.freq_tree_lemma.insert("", tk.END, values=(lemma, freq, ""))

        # POS
        pf = self.corpus.get_pos_frequencies(doc_indices)
        for i in self.freq_tree_pos.get_children(""):
            self.freq_tree_pos.delete(i)
        for pos, freq in list(pf.items())[:100]:
            self.freq_tree_pos.insert("", tk.END, values=(pos, freq, POS_LABELS.get(pos, "")))

    def show_morphology(self):
        lemma = (self.lemma_var.get() or "").strip().lower()
        if not lemma:
            return
        for i in self.morph_tree.get_children(""):
            self.morph_tree.delete(i)
        rows = self.corpus.get_morphology_for_lemma(lemma, doc_indices=self.selected_doc_indices)
        for r in rows:
            self.morph_tree.insert("", tk.END, values=(r["word"], r["pos"], r["pos_label"], r["count"]))

    def show_metadata(self):
        sel = self.doc_tree.selection()
        self.meta_text.delete("1.0", tk.END)
        if not sel:
            self.meta_text.insert(tk.END, "Выберите документ в списке «Документы корпуса».")
            return
        idx = int(sel[0])
        meta = self.corpus.get_document_metadata(idx)
        if meta:
            self.meta_text.insert(tk.END, f"Название: {meta.get('title', '')}\n")
            self.meta_text.insert(tk.END, f"Автор: {meta.get('author', '')}\n")
            self.meta_text.insert(tk.END, f"Год: {meta.get('year', '')}\n")
            self.meta_text.insert(tk.END, f"Источник: {meta.get('source', '')}\n")
            self.meta_text.insert(tk.END, f"Файл: {meta.get('filepath', '')}\n")
            self.meta_text.insert(tk.END, f"Токенов: {meta.get('tokens_count', 0)}\n")
        else:
            self.meta_text.insert(tk.END, "Метаданные недоступны.")

    # --- Методы для замера времени операций (benchmarks для отчёта) ---

    def bench_search_music(self):
        """Замер времени поиска по лемме 'music'."""
        if not self.corpus.documents:
            messagebox.showinfo("Подсказка", "Корпус пуст. Добавьте документы.")
            return
        t0 = time.perf_counter()
        hits = self.corpus.search("music", by="lemma", doc_indices=self.selected_doc_indices)
        elapsed = time.perf_counter() - t0
        logger.info("Benchmark: search lemma 'music': %.5f c, hits=%d", elapsed, len(hits))
        messagebox.showinfo("Замер времени", f"Поиск по лемме 'music': {elapsed:.5f} c, вхождений: {len(hits)}")

    def bench_concord_concert(self):
        """Замер времени построения конкорданса по лемме 'concert'."""
        if not self.corpus.documents:
            messagebox.showinfo("Подсказка", "Корпус пуст. Добавьте документы.")
            return
        t0 = time.perf_counter()
        concordance = self.corpus.get_concordance(
            "concert",
            by="lemma",
            context_size=5,
            doc_indices=self.selected_doc_indices,
            max_lines=500,
        )
        elapsed = time.perf_counter() - t0
        # Обновим вкладку конкорданса теми же данными
        for i in self.conc_tree.get_children(""):
            self.conc_tree.delete(i)
        for line in concordance:
            self.conc_tree.insert(
                "",
                tk.END,
                values=(
                    line["left"][-120:] if len(line["left"]) > 120 else line["left"],
                    line["center"],
                    line["right"][:120] if len(line["right"]) > 120 else line["right"],
                    line["doc_title"][:30] if line.get("doc_title") else "",
                ),
            )
        logger.info("Benchmark: concordance lemma 'concert': %.5f c, lines=%d", elapsed, len(concordance))
        messagebox.showinfo("Замер времени", f"Конкорданс по 'concert': {elapsed:.5f} c, строк: {len(concordance)}")

    def bench_freq_update(self):
        """Замер времени пересчёта частот (word/lemma/POS) и обновления таблиц."""
        if not self.corpus.documents:
            messagebox.showinfo("Подсказка", "Корпус пуст. Добавьте документы.")
            return
        t0 = time.perf_counter()
        doc_indices = self.selected_doc_indices
        wf = self.corpus.get_word_form_frequencies(doc_indices)
        lf = self.corpus.get_lemma_frequencies(doc_indices)
        pf = self.corpus.get_pos_frequencies(doc_indices)
        # Обновляем таблицы так же, как в _refresh_frequencies
        for i in self.freq_tree_word.get_children(""):
            self.freq_tree_word.delete(i)
        for word, freq in list(wf.items())[:500]:
            self.freq_tree_word.insert("", tk.END, values=(word, freq, ""))
        for i in self.freq_tree_lemma.get_children(""):
            self.freq_tree_lemma.delete(i)
        for lemma, freq in list(lf.items())[:500]:
            self.freq_tree_lemma.insert("", tk.END, values=(lemma, freq, ""))
        for i in self.freq_tree_pos.get_children(""):
            self.freq_tree_pos.delete(i)
        for pos, freq in list(pf.items())[:100]:
            self.freq_tree_pos.insert("", tk.END, values=(pos, freq, POS_LABELS.get(pos, "")))
        elapsed = time.perf_counter() - t0
        logger.info(
            "Benchmark: freq update (word/lemma/POS): %.5f c, uniq_word=%d, uniq_lemma=%d, uniq_pos=%d",
            elapsed,
            len(wf),
            len(lf),
            len(pf),
        )
        messagebox.showinfo("Замер времени", f"Обновление частот: {elapsed:.5f} c")

    def bench_morph_instrument(self):
        """Замер времени получения морфологии леммы 'instrument'."""
        if not self.corpus.documents:
            messagebox.showinfo("Подсказка", "Корпус пуст. Добавьте документы.")
            return
        t0 = time.perf_counter()
        rows = self.corpus.get_morphology_for_lemma("instrument", doc_indices=self.selected_doc_indices)
        elapsed = time.perf_counter() - t0
        # Обновляем вкладку морфологии
        self.lemma_var.set("instrument")
        for i in self.morph_tree.get_children(""):
            self.morph_tree.delete(i)
        for r in rows:
            self.morph_tree.insert("", tk.END, values=(r["word"], r["pos"], r["pos_label"], r["count"]))
        logger.info("Benchmark: morphology for lemma 'instrument': %.5f c, rows=%d", elapsed, len(rows))
        messagebox.showinfo("Замер времени", f"Морфология 'instrument': {elapsed:.5f} c, записей: {len(rows)}")

    def show_help(self):
        win = tk.Toplevel(self.root)
        win.title("Справка")
        win.geometry("620x480")
        st = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("TkDefaultFont", 10))
        st.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        st.insert(tk.END, self.help_text)
        st.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()


def main():
    app = CorpusManagerApp()
    app.run()


if __name__ == "__main__":
    main()
