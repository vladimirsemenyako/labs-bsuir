import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
from pathlib import Path
import json
import time
import logging

from text_processor import (
    extract_text_from_file,
    build_lemma_collocation_dict,
    extract_collocations_from_text,
    load_dictionary,
    save_dictionary,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("DictionaryApp")
try:
    fh = logging.FileHandler(Path(__file__).parent / "app.log", encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(fh)
except Exception:
    pass


class DictionaryApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Словарь лексем (вариант 21) — сочетаемость слов, английский, DOC/DOCX")
        self.root.geometry("1400x1000")
        self.root.minsize(800, 500)

        self.current_file = None
        self.dictionary = {}
        self.full_collocations = []
        self._search_exact = None
        self._build_ui()
        self._create_help_window_content()

    def _build_ui(self):
        top = ttk.Frame(self.root, padding=5)
        top.pack(fill=tk.X)

        ttk.Button(top, text="Открыть документ (DOC/DOCX)", command=self.open_document).pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="Построить словарь из документа", command=self.build_from_document).pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="Сохранить словарь", command=self.save_dict).pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="Загрузить словарь", command=self.load_dict).pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="Экспорт в TXT", command=self.export_txt).pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="Справка", command=self.show_help).pack(side=tk.RIGHT, padx=2)

        self.file_label = ttk.Label(top, text="Файл не выбран", foreground="gray")
        self.file_label.pack(side=tk.LEFT, padx=10)

        search_frame = ttk.Frame(self.root, padding=5)
        search_frame.pack(fill=tk.X)
        ttk.Label(search_frame, text="Поиск (точная лемма):").pack(side=tk.LEFT, padx=2)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side=tk.LEFT, padx=2)
        search_entry.bind("<Return>", lambda e: self.apply_search())
        ttk.Button(search_frame, text="Найти", command=self.apply_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="Показать все", command=self.show_all_lemmas).pack(side=tk.LEFT, padx=2)
        ttk.Label(search_frame, text="  Мин. частота сочетания:").pack(side=tk.LEFT, padx=(10, 2))
        self.min_freq_var = tk.StringVar(value="1")
        ttk.Entry(search_frame, textvariable=self.min_freq_var, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="Применить фильтр", command=self.apply_filter).pack(side=tk.LEFT, padx=2)

        self.notebook = ttk.Notebook(self.root, padding=5)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        dict_frame = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(dict_frame, text="Словарь лексем (по алфавиту)")
        self.dict_tree = ttk.Treeview(dict_frame, columns=("lemma", "partners", "total"), show="headings", height=20)
        self.dict_tree.heading("lemma", text="Лемма")
        self.dict_tree.heading("partners", text="Сочетается с (← до по алфавиту, → после)")
        self.dict_tree.heading("total", text="Число связей")
        self.dict_tree.column("lemma", width=150)
        self.dict_tree.column("partners", width=450)
        self.dict_tree.column("total", width=80)
        scroll_dict = ttk.Scrollbar(dict_frame, orient=tk.VERTICAL, command=self.dict_tree.yview)
        self.dict_tree.configure(yscrollcommand=scroll_dict.set)
        self.dict_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_dict.pack(side=tk.RIGHT, fill=tk.Y)
        self.dict_tree.bind("<Double-1>", self.on_lemma_double_click)

        coll_frame = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(coll_frame, text="Типовые словосочетания")
        self.coll_tree = ttk.Treeview(coll_frame, columns=("w1", "w2", "freq"), show="headings", height=20)
        self.coll_tree.heading("w1", text="Слово 1")
        self.coll_tree.heading("w2", text="Слово 2")
        self.coll_tree.heading("freq", text="Частота")
        self.coll_tree.column("w1", width=200)
        self.coll_tree.column("w2", width=200)
        self.coll_tree.column("freq", width=80)
        scroll_coll = ttk.Scrollbar(coll_frame, orient=tk.VERTICAL, command=self.coll_tree.yview)
        self.coll_tree.configure(yscrollcommand=scroll_coll.set)
        self.coll_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_coll.pack(side=tk.RIGHT, fill=tk.Y)

        bottom = ttk.Frame(self.root, padding=5)
        bottom.pack(fill=tk.X)
        self.status_var = tk.StringVar(value="Готово. Выберите документ и постройте словарь.")
        ttk.Label(bottom, textvariable=self.status_var).pack(anchor=tk.W)

        edit_frame = ttk.LabelFrame(self.root, text="Редактирование записи леммы (доп. информация)", padding=5)
        edit_frame.pack(fill=tk.X, padx=5, pady=2)
        self.lemma_edit_var = tk.StringVar()
        ttk.Label(edit_frame, text="Лемма:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(edit_frame, textvariable=self.lemma_edit_var, width=20).pack(side=tk.LEFT, padx=2)
        ttk.Label(edit_frame, text="Примечание (произвольный текст):").pack(side=tk.LEFT, padx=(10, 2))
        self.note_var = tk.StringVar()
        note_entry = ttk.Entry(edit_frame, textvariable=self.note_var, width=60)
        note_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(edit_frame, text="Сохранить примечание", command=self.save_lemma_note).pack(side=tk.LEFT, padx=2)

        crud_frame = ttk.LabelFrame(self.root, text="CRUD: запись словаря", padding=5)
        crud_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(crud_frame, text="Добавить лемму", command=self.lemma_create).pack(side=tk.LEFT, padx=2)
        ttk.Button(crud_frame, text="Удалить лемму", command=self.lemma_delete).pack(side=tk.LEFT, padx=2)
        ttk.Button(crud_frame, text="Добавить партнёра", command=self.partner_add).pack(side=tk.LEFT, padx=2)
        ttk.Button(crud_frame, text="Удалить партнёра", command=self.partner_remove).pack(side=tk.LEFT, padx=2)

        self.lemma_notes = {}

    def _create_help_window_content(self):
        self.help_text = """
Справка. Вариант 21: Словарь лексем с сочетаемостью (английский, DOC/DOCX).

1) Открыть документ — выбрать файл DOC или DOCX. Текст будет использован для построения словаря.

2) Построить словарь — из текущего документа извлекаются леммы (словарные формы слов) и типичные словосочетания (биграммы). Словарь упорядочен по алфавиту; для каждой леммы хранятся слова, с которыми она сочетается, и частоты.

3) Сохранить / Загрузить словарь — словарь сохраняется в JSON для последующего просмотра и редактирования.

4) Экспорт в TXT — выгрузка словаря или его части в текстовый файл для отчёта.

5) Поиск — введите точную лемму и нажмите «Найти»: отобразится только эта лемма (точное совпадение). «Показать все» сбрасывает поиск. «Применить фильтр» — по минимальной частоте сочетания.

6) Редактирование — выберите лемму в таблице (двойной щелчок) и при необходимости добавьте примечание. В колонке «Сочетается с» стрелка ← значит партнёр идёт до леммы по алфавиту, → — после.

Поддерживаются только форматы DOC и DOCX (английский текст).
        """

    def open_document(self):
        path = filedialog.askopenfilename(
            title="Выберите документ",
            filetypes=[
                ("Word (DOCX)", "*.docx"),
                ("Word (DOC)", "*.doc"),
                ("Все", "*.*"),
            ],
        )
        if not path:
            return
        self.current_file = path
        self.file_label.config(text=Path(path).name, foreground="black")
        text = extract_text_from_file(path)
        if not text or len(text.strip()) < 10:
            messagebox.showwarning("Внимание", "Не удалось извлечь достаточно текста из файла. Проверьте формат и кодировку.")
        else:
            self.status_var.set(f"Загружен файл: {Path(path).name}, символов: {len(text)}")

    def build_from_document(self):
        if not self.current_file:
            messagebox.showinfo("Подсказка", "Сначала выберите документ (Открыть документ).")
            return
        text = extract_text_from_file(self.current_file)
        if not text or len(text.strip()) < 10:
            messagebox.showwarning("Внимание", "Текст не извлечён. Укажите файл DOC или DOCX с английским текстом.")
            return
        self.status_var.set("Построение словаря...")
        self.root.update()
        t0 = time.perf_counter()
        self.dictionary = build_lemma_collocation_dict(text, top_collocations_per_lemma=100)
        self.full_collocations = extract_collocations_from_text(text, top_n=500, min_freq=2)
        elapsed = time.perf_counter() - t0
        logger.info("Построение словаря: %.3f с, лемм: %d, словосочетаний: %d", elapsed, len(self.dictionary), len(self.full_collocations))
        self._refresh_dict_tab()
        self._refresh_coll_tab()
        self.status_var.set(f"Словарь построен за {elapsed:.2f} с. Лемм: {len(self.dictionary)}, словосочетаний: {len(self.full_collocations)}")

    def _refresh_dict_tab(self):
        for i in self.dict_tree.get_children(""):
            self.dict_tree.delete(i)
        query = (self.search_var.get() or "").strip().lower() if self._search_exact is not None else ""
        try:
            min_f = int(self.min_freq_var.get())
        except (ValueError, TypeError):
            min_f = 1
        sorted_lemmas = sorted(self.dictionary.keys())
        if query:
            sorted_lemmas = [l for l in sorted_lemmas if l.lower() == query]
        visible = []
        for lemma in sorted_lemmas:
            partners = self.dictionary[lemma]
            total = sum(p["freq"] for p in partners)
            if total < min_f:
                continue
            visible.append(lemma)
        for idx, lemma in enumerate(visible, 1):
            partners = self.dictionary[lemma]
            parts = []
            for p in partners[:8]:
                w, f = p["word"], p["freq"]
                if w < lemma:
                    parts.append(f"{w}({f}) ←")
                elif w > lemma:
                    parts.append(f"{w}({f}) →")
                else:
                    parts.append(f"{w}({f})")
            partners_str = ", ".join(parts) if parts else "—"
            total = sum(p["freq"] for p in partners)
            self.dict_tree.insert("", tk.END, values=(lemma, partners_str, total), tags=(lemma,))

    def _refresh_coll_tab(self):
        for i in self.coll_tree.get_children(""):
            self.coll_tree.delete(i)
        for (w1, w2), freq in self.full_collocations:
            self.coll_tree.insert("", tk.END, values=(w1, w2, freq))

    def apply_filter(self):
        if self.dictionary:
            self._search_exact = None
            self._refresh_dict_tab()

    def apply_search(self):
        if not self.dictionary:
            return
        self._search_exact = (self.search_var.get() or "").strip()
        self._refresh_dict_tab()
        if self._search_exact and not self.dict_tree.get_children(""):
            self.status_var.set(f"Лемма «{self._search_exact}» не найдена (точное совпадение).")
        elif self._search_exact:
            self.status_var.set(f"Найдена лемма «{self._search_exact}».")

    def show_all_lemmas(self):
        self.search_var.set("")
        self._search_exact = None
        if self.dictionary:
            self._refresh_dict_tab()
        self.status_var.set("Показаны все леммы.")

    def on_lemma_double_click(self, event):
        sel = self.dict_tree.selection()
        if not sel:
            return
        item = self.dict_tree.item(sel[0])
        vals = item["values"]
        if vals:
            lemma = vals[0]
            self.lemma_edit_var.set(lemma)
            self.note_var.set(self.lemma_notes.get(lemma, ""))

    def save_lemma_note(self):
        lemma = (self.lemma_edit_var.get() or "").strip()
        if not lemma:
            messagebox.showinfo("Подсказка", "Выберите лемму (двойной щелчок по строке) или введите её.")
            return
        self.lemma_notes[lemma] = self.note_var.get()
        self.status_var.set(f"Примечание для «{lemma}» сохранено.")

    def lemma_create(self):
        win = tk.Toplevel(self.root)
        win.title("Добавить лемму")
        win.geometry("400x120")
        win.transient(self.root)
        ttk.Label(win, text="Лемма:").pack(anchor=tk.W, padx=5, pady=2)
        lemma_entry = ttk.Entry(win, width=40)
        lemma_entry.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(win, text="Партнёры (слово:частота через запятую, например: word:5, run:3):").pack(anchor=tk.W, padx=5, pady=2)
        partners_entry = ttk.Entry(win, width=50)
        partners_entry.pack(fill=tk.X, padx=5, pady=2)

        def on_ok():
            lemma = (lemma_entry.get() or "").strip().lower()
            if not lemma:
                messagebox.showwarning("Внимание", "Введите лемму.", parent=win)
                return
            if lemma in self.dictionary:
                messagebox.showwarning("Внимание", f"Лемма «{lemma}» уже есть в словаре.", parent=win)
                return
            partners_str = (partners_entry.get() or "").strip()
            partners = []
            if partners_str:
                for part in partners_str.split(","):
                    part = part.strip()
                    if ":" in part:
                        w, _, f = part.partition(":")
                        w, f = w.strip().lower(), f.strip()
                        try:
                            partners.append({"word": w, "freq": int(f)})
                        except ValueError:
                            pass
            self.dictionary[lemma] = partners
            self._refresh_dict_tab()
            self.status_var.set(f"Добавлена лемма «{lemma}».")
            win.destroy()

        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="OK", command=on_ok).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Отмена", command=win.destroy).pack(side=tk.LEFT, padx=2)

    def lemma_delete(self):
        lemma = (self.lemma_edit_var.get() or "").strip()
        if not lemma:
            messagebox.showinfo("Подсказка", "Выберите лемму в таблице (двойной щелчок) или введите в поле «Лемма».")
            return
        if lemma not in self.dictionary:
            messagebox.showwarning("Внимание", f"Леммы «{lemma}» нет в словаре.")
            return
        if not messagebox.askyesno("Подтверждение", f"Удалить лемму «{lemma}» и все её записи?", parent=self.root):
            return
        del self.dictionary[lemma]
        if lemma in self.lemma_notes:
            del self.lemma_notes[lemma]
        self.lemma_edit_var.set("")
        self.note_var.set("")
        self._refresh_dict_tab()
        self.status_var.set(f"Лемма «{lemma}» удалена.")

    def partner_add(self):
        lemma = (self.lemma_edit_var.get() or "").strip().lower()
        if not lemma:
            messagebox.showinfo("Подсказка", "Выберите или введите лемму, к которой добавить партнёра.")
            return
        word = (simpledialog.askstring("Добавить партнёра", "Слово (партнёр):", parent=self.root) or "").strip().lower()
        if not word:
            return
        try:
            freq = int(simpledialog.askstring("Частота", "Частота (целое число):", initialvalue="1", parent=self.root) or "1")
        except (ValueError, TypeError):
            freq = 1
        if lemma not in self.dictionary:
            self.dictionary[lemma] = []
        for p in self.dictionary[lemma]:
            if p["word"] == word:
                p["freq"] += freq
                self._refresh_dict_tab()
                self.status_var.set(f"Обновлена частота для «{lemma}» + «{word}».")
                return
        self.dictionary[lemma].append({"word": word, "freq": freq})
        self.dictionary[lemma].sort(key=lambda x: -x["freq"])
        self._refresh_dict_tab()
        self.status_var.set(f"Добавлен партнёр «{word}» к лемме «{lemma}».")

    def partner_remove(self):
        lemma = (self.lemma_edit_var.get() or "").strip().lower()
        if not lemma or lemma not in self.dictionary:
            messagebox.showinfo("Подсказка", "Выберите лемму в таблице, у которой удалить партнёра.")
            return
        partners = self.dictionary[lemma]
        if not partners:
            messagebox.showinfo("Подсказка", f"У леммы «{lemma}» нет партнёров.")
            return
        word = (simpledialog.askstring("Удалить партнёра", "Введите слово партнёра для удаления:", parent=self.root) or "").strip().lower()
        if not word:
            return
        self.dictionary[lemma] = [p for p in partners if p["word"] != word]
        if not self.dictionary[lemma]:
            del self.dictionary[lemma]
            if lemma in self.lemma_notes:
                del self.lemma_notes[lemma]
            self.lemma_edit_var.set("")
            self.note_var.set("")
        self._refresh_dict_tab()
        self.status_var.set(f"Партнёр «{word}» удалён у леммы «{lemma}».")

    def save_dict(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Все", "*.*")],
        )
        if not path:
            return
        data = {
            "lemmas": self.dictionary,
            "notes": self.lemma_notes,
            "collocations": [{"w1": w1, "w2": w2, "freq": f} for (w1, w2), f in self.full_collocations],
        }
        save_dictionary(data, path)
        self.status_var.set(f"Словарь сохранён: {path}")

    def load_dict(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json"), ("Все", "*.*")],
        )
        if not path:
            return
        data = load_dictionary(path)
        self.dictionary = data.get("lemmas", {})
        self.lemma_notes = data.get("notes", {})
        coll = data.get("collocations", [])
        self.full_collocations = [((c["w1"], c["w2"]), c["freq"]) for c in coll]
        self._refresh_dict_tab()
        self._refresh_coll_tab()
        self.status_var.set(f"Словарь загружен: {path}")

    def export_txt(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текст", "*.txt"), ("Все", "*.*")],
        )
        if not path:
            return
        lines = []
        for lemma in sorted(self.dictionary.keys()):
            note = self.lemma_notes.get(lemma, "")
            lines.append(f"\n{lemma}" + (f"  [{note}]" if note else ""))
            for p in self.dictionary[lemma]:
                lines.append(f"    — {p['word']}: {p['freq']}")
        Path(path).write_text("\n".join(lines), encoding="utf-8")
        self.status_var.set(f"Экспорт в TXT: {path}")

    def show_help(self):
        win = tk.Toplevel(self.root)
        win.title("Справка")
        win.geometry("600x400")
        st = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("TkDefaultFont", 10))
        st.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        st.insert(tk.END, self.help_text)
        st.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()


def main():
    app = DictionaryApp()
    app.run()


if __name__ == "__main__":
    main()
