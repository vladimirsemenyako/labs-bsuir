"""Приложение для синтаксического анализа текста — Лабораторная работа №3.

Требования:
- входные данные: текст естественного языка (TXT, RTF, PDF, HTML, DOC, DOCX)
- выходные данные: структуры синтаксического анализа (деревья зависимостей)
- GUI, справка, сохранение/просмотр/редактирование результатов
"""

import json
import logging
import sys
import time
import webbrowser
from pathlib import Path

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

_eyaziis = Path(__file__).resolve().parent.parent
lab3 = Path(__file__).resolve().parent
if str(_eyaziis) not in sys.path:
    sys.path.insert(0, str(_eyaziis))
if str(lab3) not in sys.path:
    sys.path.insert(0, str(lab3))

try:
    from lab_3.text_extractor import extract_text_from_file
    from lab_3.syntactic_analyzer import SyntacticAnalyzer
except ImportError:
    from text_extractor import extract_text_from_file
    from syntactic_analyzer import SyntacticAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("SyntacticAnalysis")
try:
    fh = logging.FileHandler(lab3 / "syntax_app.log", encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(fh)
except Exception:
    pass


class SyntacticAnalysisApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Синтаксический анализ текста — Лабораторная работа №3")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)

        self.analyzer = SyntacticAnalyzer(lang="en")
        self.current_text = ""
        self.current_filepath = ""
        self.parsed_data = []
        self._build_ui()
        self._create_help_content()

    def _build_ui(self):
        top = ttk.Frame(self.root, padding=5)
        top.pack(fill=tk.X)

        ttk.Button(top, text="Открыть файл", command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="Анализировать", command=self.run_analysis).pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="Визуализировать дерево", command=self.visualize_tree).pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="Сохранить результат", command=self.save_result).pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="Справка", command=self.show_help).pack(side=tk.RIGHT, padx=2)

        main = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        # Левая панель — входной текст
        left = ttk.Frame(main)
        main.add(left, weight=1)
        ttk.Label(left, text="Исходный текст:").pack(anchor=tk.W)
        self.input_text = scrolledtext.ScrolledText(left, wrap=tk.WORD, height=25, font=("Consolas", 10))
        self.input_text.pack(fill=tk.BOTH, expand=True)
        ttk.Button(left, text="Очистить", command=lambda: self.input_text.delete("1.0", tk.END)).pack(anchor=tk.W, pady=2)

        # Правая панель — результат анализа
        right = ttk.Frame(main)
        main.add(right, weight=1)
        ttk.Label(right, text="Результат синтаксического анализа (зависимости):").pack(anchor=tk.W)
        cols = ("sentence", "idx", "token", "lemma", "pos", "head", "dep")
        self.result_tree = ttk.Treeview(right, columns=cols, show="headings", height=20, selectmode="extended")
        self.result_tree.heading("sentence", text="Предложение")
        self.result_tree.heading("idx", text="#")
        self.result_tree.heading("token", text="Токен")
        self.result_tree.heading("lemma", text="Лемма")
        self.result_tree.heading("pos", text="POS")
        self.result_tree.heading("head", text="Глава")
        self.result_tree.heading("dep", text="Связь")
        for c in cols:
            self.result_tree.column(c, width=80)
        self.result_tree.column("sentence", width=200)
        scroll_r = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scroll_r.set)
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_r.pack(side=tk.RIGHT, fill=tk.Y)

        # Редактируемая область для просмотра/редактирования выбранного предложения
        edit_frame = ttk.LabelFrame(self.root, text="Просмотр/редактирование предложения", padding=5)
        edit_frame.pack(fill=tk.X, padx=5, pady=2)
        self.edit_var = tk.StringVar()
        self.edit_entry = ttk.Entry(edit_frame, textvariable=self.edit_var, width=80)
        self.edit_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(edit_frame, text="Повторить анализ", command=self.reanalyze_selection).pack(side=tk.LEFT, padx=2)
        self.result_tree.bind("<<TreeviewSelect>>", self.on_result_select)

        # Benchmark
        bench_frame = ttk.LabelFrame(self.root, text="Замер времени (для отчёта)", padding=5)
        bench_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(bench_frame, text="Бенчмарк: анализ 10 предложений", command=self.benchmark_analysis).pack(side=tk.LEFT, padx=2)

        self.status_var = tk.StringVar(value="Готово. Откройте файл (TXT, RTF, PDF, HTML, DOC, DOCX) или введите текст и нажмите «Анализировать».")
        ttk.Label(self.root, textvariable=self.status_var).pack(anchor=tk.W, padx=5, pady=2)

    def _create_help_content(self):
        self.help_text = """
Справка. Синтаксический анализ текста — Лабораторная работа №3.

1) Открыть файл — выбор файла форматов TXT, RTF, PDF, HTML, DOC, DOCX. Текст извлекается и отображается в левой панели. Поддерживаются русский и английский языки.

2) Анализировать — выполняется автоматический синтаксический разбор предложений: построение дерева зависимостей (dependency parsing) с помощью spaCy. Результат отображается в таблице: предложение, номер токена, токен, лемма, часть речи (POS), головное слово, тип зависимости.

3) Визуализировать дерево — по выделенному в таблице предложению (или первому предложению из текста) строится HTML-визуализация дерева и открывается в браузере.

4) Сохранить результат — экспорт результата анализа в JSON-файл для последующего просмотра и документирования.

5) Просмотр/редактирование — при выборе строки в таблице предложение отображается в поле внизу. Можно отредактировать текст и нажать «Повторить анализ» для переразбора.

Обозначения типов зависимостей (Universal Dependencies):
- ROOT — корень предложения
- nsubj — подлежащее
- obj — прямое дополнение
- amod — определение (прилагательное)
- advmod — обстоятельство
- и др. (см. документацию Universal Dependencies)

Поддерживаемые форматы: TXT, RTF, PDF, HTML, DOC, DOCX.
        """

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=[
                ("Текст", "*.txt"),
                ("RTF", "*.rtf"),
                ("PDF", "*.pdf"),
                ("HTML", "*.html *.htm"),
                ("Word DOCX", "*.docx"),
                ("Word DOC", "*.doc"),
                ("Все", "*.*"),
            ],
        )
        if not path:
            return
        text = extract_text_from_file(path)
        if not text:
            messagebox.showwarning("Внимание", "Не удалось извлечь текст из файла.")
            return
        self.current_text = text
        self.current_filepath = path
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert(tk.END, text)
        self.status_var.set(f"Загружен: {Path(path).name}")

    def run_analysis(self):
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Подсказка", "Введите текст или откройте файл.")
            return
        self.current_text = text
        t0 = time.perf_counter()
        try:
            self.parsed_data = self.analyzer.parse_sentences(text)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            logger.exception("Analysis failed")
            return
        elapsed = time.perf_counter() - t0
        self._fill_result_tree()
        n_sent = len(self.parsed_data)
        n_tok = sum(len(s["tokens"]) for s in self.parsed_data)
        self.status_var.set(f"Проанализировано: {n_sent} предложений, {n_tok} токенов за {elapsed:.3f} с")

    def _fill_result_tree(self):
        for i in self.result_tree.get_children(""):
            self.result_tree.delete(i)
        rows = self.analyzer.get_dependency_table(self.parsed_data)
        for r in rows:
            self.result_tree.insert("", tk.END, values=r)

    def on_result_select(self, event):
        sel = self.result_tree.selection()
        if not sel:
            return
        item = self.result_tree.item(sel[0])
        vals = item["values"]
        if vals:
            self.edit_var.set(vals[0] if isinstance(vals[0], str) and len(vals[0]) > 5 else "")

    def reanalyze_selection(self):
        text = self.edit_var.get().strip()
        if not text:
            messagebox.showinfo("Подсказка", "Введите текст в поле редактирования.")
            return
        t0 = time.perf_counter()
        try:
            parsed = self.analyzer.parse_sentences(text)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return
        elapsed = time.perf_counter() - t0
        for i in self.result_tree.get_children(""):
            self.result_tree.delete(i)
        for sent in parsed:
            for t in sent["tokens"]:
                dep_label = self.analyzer.dep_label(t["dep"])
                self.result_tree.insert("", tk.END, values=(
                    sent["text"][:60] + "..." if len(sent["text"]) > 60 else sent["text"],
                    t["idx"], t["text"], t["lemma"], t["pos"], t["head_text"], dep_label,
                ))
        self.parsed_data = parsed
        self.status_var.set(f"Повторный анализ: {len(parsed)} предложений за {elapsed:.3f} с")

    def visualize_tree(self):
        text = ""
        sel = self.result_tree.selection()
        if sel:
            item = self.result_tree.item(sel[0])
            vals = item.get("values", ())
            if vals:
                sent = vals[0]
                if len(sent) > 5 and not sent.endswith("..."):
                    text = sent
                else:
                    for p in self.parsed_data:
                        if p["text"][:60] == sent[:60] or p["text"] == sent:
                            text = p["text"]
                            break
        if not text:
            text = self.input_text.get("1.0", tk.END).strip().split("\n")[0][:500] if self.parsed_data else ""
        if not text:
            messagebox.showinfo("Подсказка", "Сначала выполните анализ и выберите предложение.")
            return
        try:
            path = self.analyzer.render_tree_html(text)
            webbrowser.open(Path(path).resolve().as_uri())
            self.status_var.set("Визуализация открыта в браузере.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def save_result(self):
        if not self.parsed_data:
            messagebox.showinfo("Подсказка", "Сначала выполните анализ.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Все", "*.*")],
        )
        if not path:
            return
        data = {
            "source": self.current_filepath or "(введён вручную)",
            "text_preview": self.current_text[:500] + "..." if len(self.current_text) > 500 else self.current_text,
            "analysis": self.analyzer.to_export_format(self.parsed_data),
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.status_var.set(f"Результат сохранён: {path}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def benchmark_analysis(self):
        sample = "The quick brown fox jumps over the lazy dog. " * 5
        sample += "Natural language processing is a subfield of linguistics and computer science."
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert(tk.END, sample)
        t0 = time.perf_counter()
        try:
            parsed = self.analyzer.parse_sentences(sample)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return
        elapsed = time.perf_counter() - t0
        n_sent = len(parsed)
        n_tok = sum(len(s["tokens"]) for s in parsed)
        logger.info("Benchmark: %d sentences, %d tokens in %.5f s", n_sent, n_tok, elapsed)
        messagebox.showinfo(
            "Замер времени",
            f"Анализ {n_sent} предложений ({n_tok} токенов): {elapsed:.5f} с",
        )
        self.parsed_data = parsed
        self._fill_result_tree()

    def show_help(self):
        win = tk.Toplevel(self.root)
        win.title("Справка")
        win.geometry("580x420")
        st = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("TkDefaultFont", 10))
        st.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        st.insert(tk.END, self.help_text)
        st.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()


def main():
    app = SyntacticAnalysisApp()
    app.run()


if __name__ == "__main__":
    main()
