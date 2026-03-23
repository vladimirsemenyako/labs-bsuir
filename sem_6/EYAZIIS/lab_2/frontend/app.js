const api = {
  get: async (path) => {
    const res = await fetch(`/api${path}`);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  post: async (path, body) => {
    const res = await fetch(`/api${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  postForm: async (path, formData) => {
    const res = await fetch(`/api${path}`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  put: async (path, body) => {
    const res = await fetch(`/api${path}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  del: async (path) => {
    const res = await fetch(`/api${path}`, { method: "DELETE" });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  downloadJson: async (path) => {
    const res = await fetch(`/api${path}`);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
};

const el = (id) => document.getElementById(id);

const state = {
  filterDocIds: null,
  selectedDocId: null,
  freqKind: "word",
  docsPage: 1,
  docsPageSize: 20,
  docsTotalPages: 1,
  docsTotal: 0,
  docsCurrentIds: [],
  freqPage: 1,
  freqPageSize: 20,
  freqTotalPages: 1,
  freqTotal: 0,
  concPage: 1,
  concPageSize: 20,
  concTotalPages: 1,
  concTotal: 0,
  lastConcQuery: null,
  lastConcBy: "lemma",
  lastConcContext: 5,
  morphPage: 1,
  morphPageSize: 20,
  morphTotalPages: 1,
  morphTotal: 0,
  lastMorphLemma: null,
  selectedFreqLemma: null,
  lemmaEditId: null,
};

function setStatus(text) {
  el("status").textContent = text;
}

function getActiveTab() {
  const btn = document.querySelector(".tab-btn.active");
  return btn ? btn.dataset.tab : "docs";
}

function updatePaginationBar() {
  const tab = getActiveTab();
  const bar = el("pagination-bar");
  bar.classList.toggle("tab-meta-active", tab === "meta" || tab === "lemmas");

  if (tab === "meta" || tab === "lemmas") return;

  const prevBtn = el("pagination-prev");
  const nextBtn = el("pagination-next");
  const ind = el("pagination-indicator");
  const sizeSelect = el("pagination-page-size");

  if (tab === "docs") {
    ind.textContent = `Страница ${state.docsPage} из ${state.docsTotalPages} (всего: ${state.docsTotal})`;
    prevBtn.disabled = state.docsPage <= 1;
    nextBtn.disabled = state.docsPage >= state.docsTotalPages;
    sizeSelect.value = String(state.docsPageSize);
  } else if (tab === "freq") {
    ind.textContent = `Страница ${state.freqPage} из ${state.freqTotalPages} (всего: ${state.freqTotal})`;
    prevBtn.disabled = state.freqPage <= 1;
    nextBtn.disabled = state.freqPage >= state.freqTotalPages;
    sizeSelect.value = String(state.freqPageSize);
  } else if (tab === "conc") {
    if (state.lastConcQuery == null) {
      ind.textContent = "Выполните поиск";
      prevBtn.disabled = true;
      nextBtn.disabled = true;
    } else {
      ind.textContent = `Страница ${state.concPage} из ${state.concTotalPages} (всего: ${state.concTotal})`;
      prevBtn.disabled = state.concPage <= 1;
      nextBtn.disabled = state.concPage >= state.concTotalPages;
    }
    sizeSelect.value = String(state.concPageSize);
  } else if (tab === "morph") {
    if (state.lastMorphLemma == null) {
      ind.textContent = "Введите лемму и нажмите «Показать морфологию»";
      prevBtn.disabled = true;
      nextBtn.disabled = true;
    } else {
      ind.textContent = `Страница ${state.morphPage} из ${state.morphTotalPages} (всего: ${state.morphTotal})`;
      prevBtn.disabled = state.morphPage <= 1;
      nextBtn.disabled = state.morphPage >= state.morphTotalPages;
    }
    sizeSelect.value = String(state.morphPageSize);
  }
}

function getSelectedSearchBy() {
  return document.querySelector('input[name="search-by"]:checked')?.value || "lemma";
}

function getFilterDocIdsParam() {
  if (!state.filterDocIds || !state.filterDocIds.length) return "";
  return `&doc_ids=${encodeURIComponent(state.filterDocIds.join(","))}`;
}

function renderTable(containerId, headers, rows) {
  const container = el(containerId);
  if (!rows.length) {
    container.innerHTML = "<p>Нет данных.</p>";
    return;
  }
  const thead = `<thead><tr>${headers.map((h) => `<th>${h}</th>`).join("")}</tr></thead>`;
  const tbody = `<tbody>${rows
    .map((row) => `<tr>${row.map((cell) => `<td>${cell ?? ""}</td>`).join("")}</tr>`)
    .join("")}</tbody>`;
  container.innerHTML = `<table>${thead}${tbody}</table>`;
}

function renderDocumentsTable(docs) {
  const tbody = el("docs-table").querySelector("tbody");
  tbody.innerHTML = "";

  const filterSet = state.filterDocIds ? new Set(state.filterDocIds) : null;

  docs.forEach((doc) => {
    const tr = document.createElement("tr");
    tr.dataset.docId = doc.id;
    if (state.selectedDocId === doc.id) tr.classList.add("selected");

    const checked = filterSet ? filterSet.has(doc.id) : false;

    tr.innerHTML = `
      <td>
        <input type="checkbox" class="filter-check" ${checked ? "checked" : ""} />
      </td>
      <td>${doc.title || ""}</td>
      <td>${doc.author || ""}</td>
      <td>${doc.year || ""}</td>
      <td>${doc.tokens_count ?? 0}</td>
    `;

    tr.addEventListener("click", () => {
      state.selectedDocId = doc.id;
      tbody.querySelectorAll("tr").forEach((r) => r.classList.remove("selected"));
      tr.classList.add("selected");
    });

    tr.addEventListener("dblclick", () => {
      previewDocumentText(doc.id).catch((err) => {
        console.error(err);
        alert("Не удалось загрузить текст документа.");
      });
    });

    tbody.appendChild(tr);
  });
}

async function refreshDocuments() {
  const res = await api.get(
    `/documents?page=${encodeURIComponent(state.docsPage)}&page_size=${encodeURIComponent(state.docsPageSize)}`
  );
  state.docsTotalPages = res.total_pages ?? 1;
  state.docsTotal = res.total ?? 0;
  state.docsPage = res.page ?? 1;
  state.docsCurrentIds = (res.items || []).map((d) => d.id);
  const totalTokens = res.total_tokens ?? 0;
  el("docs-total-tokens").textContent = `Всего токенов в корпусе: ${totalTokens}`;

  renderDocumentsTable(res.items || []);

  updatePaginationBar();
  setStatus(
    state.docsTotal
      ? `Корпус загружен. Документов: ${state.docsTotal}. (страница ${state.docsPage})`
      : "Корпус пуст. Добавьте документы или загрузите корпус."
  );
}

async function previewDocumentText(docId) {
  const doc = await api.get(`/documents/${encodeURIComponent(docId)}`);
  el("modal-title").textContent = doc.title || "Документ";
  el("modal-text").value = doc.text || "";
  el("modal").style.display = "flex";
}

function closeModal() {
  el("modal").style.display = "none";
}

async function setFilterFromChecks() {
  const checkedOnPage = Array.from(el("docs-table").querySelectorAll(".filter-check:checked")).map(
    (checkbox) => checkbox.closest("tr")?.dataset.docId
  );
  const checkedSet = new Set(checkedOnPage.filter(Boolean));

  const filterSet = state.filterDocIds ? new Set(state.filterDocIds) : new Set();
  state.docsCurrentIds.forEach((id) => {
    if (checkedSet.has(id)) filterSet.add(id);
    else filterSet.delete(id);
  });

  state.filterDocIds = filterSet.size ? Array.from(filterSet) : null;
  setStatus(
    state.filterDocIds
      ? `Фильтр: ${state.filterDocIds.length} документов. Обновите частоты или выполните поиск.`
      : "Фильтр сброшен — учитываются все документы."
  );
}

function resetFilter() {
  state.filterDocIds = null;
  el("docs-table").querySelectorAll(".filter-check").forEach((c) => (c.checked = false));
  setStatus("Фильтр сброшен — учитываются все документы.");
}

async function deleteSelectedDoc() {
  if (!state.selectedDocId) {
    alert("Выберите документ в списке для удаления.");
    return;
  }
  const ok = confirm("Удалить выбранный документ из корпуса?");
  if (!ok) return;
  await api.del(`/documents/${encodeURIComponent(state.selectedDocId)}`);
  state.selectedDocId = null;
  // После удаления пересчитаем страницу, т.к. total мог уменьшиться.
  state.docsPage = 1;
  refreshDocuments().catch(console.error);
}

async function showConcordance({ query, by, contextSize }, page = 1) {
  const t0 = performance.now();
  const pageSize = state.concPageSize;
  const res = await api.get(
    `/search?query=${encodeURIComponent(query)}&by=${encodeURIComponent(by)}&context_size=${contextSize}&max_lines=5000&page=${page}&page_size=${pageSize}${getFilterDocIdsParam()}`
  );
  const elapsed = performance.now() - t0;

  const rows = res.items != null ? res.items : res;
  state.lastConcQuery = query;
  state.lastConcBy = by;
  state.lastConcContext = contextSize;
  state.concTotal = res.total ?? rows.length;
  state.concTotalPages = res.total_pages ?? 1;
  state.concPage = res.page ?? 1;

  renderTable(
    "concordance-results",
    ["Слева", "Центр", "Справа", "Документ"],
    rows.map((row) => [row.left, row.center, row.right, row.doc_title || row.doc_id])
  );

  updatePaginationBar();
  return { rowsCount: rows.length, total: state.concTotal, elapsed };
}

function renderFreqTable(rows, kind) {
  const container = el("freq-results");
  const isLemma = kind === "lemma";
  el("btn-delete-lemma").style.display = isLemma ? "" : "none";
  if (!rows.length) {
    container.innerHTML = "<p>Нет данных.</p>";
    return;
  }
  const thead = `<thead><tr><th>Элемент</th><th>Частота</th><th>Описание</th></tr></thead>`;
  const tbody = document.createElement("tbody");
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    tr.dataset.item = row.item;
    if (isLemma && state.selectedFreqLemma === row.item) tr.classList.add("selected");
    tr.innerHTML = `<td>${row.item ?? ""}</td><td>${row.freq ?? ""}</td><td>${row.extra ?? ""}</td>`;
    if (isLemma) {
      tr.style.cursor = "pointer";
      tr.addEventListener("click", () => {
        state.selectedFreqLemma = row.item;
        tbody.querySelectorAll("tr").forEach((r) => r.classList.remove("selected"));
        tr.classList.add("selected");
      });
    }
    tbody.appendChild(tr);
  });
  container.innerHTML = "";
  const table = document.createElement("table");
  table.innerHTML = thead;
  table.appendChild(tbody);
  container.appendChild(table);
}

async function refreshFrequencies() {
  const t0 = performance.now();
  const res = await api.get(
    `/frequencies?kind=${encodeURIComponent(state.freqKind)}&page=${state.freqPage}&page_size=${state.freqPageSize}${getFilterDocIdsParam()}`
  );
  const elapsed = performance.now() - t0;

  const rows = res.items != null ? res.items : res;
  state.freqTotal = res.total ?? rows.length;
  state.freqTotalPages = res.total_pages ?? 1;
  state.freqPage = res.page ?? 1;

  renderFreqTable(rows, state.freqKind);

  updatePaginationBar();
  setStatus(`Частоты обновлены за ${elapsed.toFixed(2)} мс.`);
}

async function deleteLemmaFromCorpus() {
  if (state.freqKind !== "lemma") {
    setStatus("Выберите режим «Леммы» и выделите лемму в таблице.");
    return;
  }
  if (!state.selectedFreqLemma) {
    setStatus("Выделите лемму в таблице частот (клик по строке).");
    return;
  }
  if (!confirm(`Удалить лемму «${state.selectedFreqLemma}» из корпуса? Все вхождения будут удалены из документов. Восстановить будет нельзя.`)) return;
  try {
    const res = await api.del(`/corpus/lemmas/${encodeURIComponent(state.selectedFreqLemma)}`);
    setStatus(`Лемма «${state.selectedFreqLemma}» удалена из корпуса. Обновлено документов: ${res.documents_updated ?? 0}.`);
    state.selectedFreqLemma = null;
    await refreshFrequencies();
  } catch (err) {
    console.error(err);
    alert(err.message || "Ошибка.");
  }
}

async function showMorphology(lemma, page = 1) {
  const t0 = performance.now();
  const pageSize = state.morphPageSize;
  const res = await api.get(
    `/morphology/${encodeURIComponent(lemma)}?page=${page}&page_size=${pageSize}${getFilterDocIdsParam()}`
  );
  const elapsed = performance.now() - t0;

  const rows = res.items != null ? res.items : res;
  state.lastMorphLemma = lemma;
  state.morphTotal = res.total ?? rows.length;
  state.morphTotalPages = res.total_pages ?? 1;
  state.morphPage = res.page ?? 1;

  renderTable(
    "morph-results",
    ["Словоформа", "POS", "Описание", "Частота"],
    rows.map((row) => [row.word, row.pos, row.pos_label, row.count])
  );

  updatePaginationBar();
  setStatus(`Морфология показана за ${elapsed.toFixed(2)} мс.`);
}

async function showMetadata() {
  if (!state.selectedDocId) {
    el("meta-text").textContent = "Выберите документ в списке «Документы корпуса».";
    return;
  }
  const doc = await api.get(`/documents/${encodeURIComponent(state.selectedDocId)}`);

  el("meta-text").textContent =
    `Название: ${doc.title || ""}\n` +
    `Автор: ${doc.author || ""}\n` +
    `Год: ${doc.year || ""}\n` +
    `Источник: ${doc.source || ""}\n` +
    `Файл: ${doc.filepath || ""}\n` +
    `Токенов: ${doc.tokens_count ?? 0}\n`;
}

async function refreshCustomLemmas() {
  const list = await api.get("/lemmas");
  const tbody = el("custom-lemmas-table").querySelector("tbody");
  tbody.innerHTML = "";
  el("custom-lemmas-empty").style.display = list.length ? "none" : "block";
  list.forEach((item) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${item.lemma || ""}</td>
      <td>${item.description || ""}</td>
      <td>
        <button class="lemma-btn-edit ghost" data-id="${item.id}">Изменить</button>
        <button class="lemma-btn-delete danger" data-id="${item.id}">Удалить</button>
      </td>
    `;
    tr.querySelector(".lemma-btn-edit").addEventListener("click", () => openLemmaModal(true, item));
    tr.querySelector(".lemma-btn-delete").addEventListener("click", () => deleteCustomLemma(item.id));
    tbody.appendChild(tr);
  });
}

function openLemmaModal(isEdit, item) {
  state.lemmaEditId = isEdit && item ? item.id : null;
  el("lemma-modal-title").textContent = state.lemmaEditId ? "Изменить лемму" : "Добавить лемму";
  el("lemma-form-lemma").value = item ? item.lemma || "" : "";
  el("lemma-form-desc").value = item ? item.description || "" : "";
  el("lemma-modal").style.display = "flex";
}

function closeLemmaModal() {
  el("lemma-modal").style.display = "none";
  state.lemmaEditId = null;
}

async function lemmaFormSubmit() {
  const lemma = el("lemma-form-lemma").value.trim();
  if (!lemma) {
    alert("Введите лемму.");
    return;
  }
  const description = el("lemma-form-desc").value.trim();
  try {
    if (state.lemmaEditId) {
      await api.put(`/lemmas/${state.lemmaEditId}`, { lemma, description });
      setStatus("Лемма обновлена.");
    } else {
      await api.post("/lemmas", { lemma, description });
      setStatus("Лемма добавлена.");
    }
    closeLemmaModal();
    await refreshCustomLemmas();
  } catch (err) {
    console.error(err);
    alert(err.message || "Ошибка сохранения леммы.");
  }
}

async function deleteCustomLemma(id) {
  if (!confirm("Удалить эту лемму из списка?")) return;
  try {
    await api.del(`/lemmas/${encodeURIComponent(id)}`);
    setStatus("Лемма удалена.");
    await refreshCustomLemmas();
  } catch (err) {
    console.error(err);
    alert(err.message || "Ошибка удаления.");
  }
}

async function handleSearch() {
  const query = el("query").value.trim();
  if (!query) {
    setStatus("Введите запрос.");
    return;
  }

  const by = getSelectedSearchBy();
  let contextSize = Number(el("context-size").value || 5);
  if (!Number.isFinite(contextSize) || contextSize < 1) contextSize = 5;

  const { rowsCount, elapsed } = await showConcordance({ query, by, contextSize });

  // Логика из desktop-версии: если запрос фраза — морфологию показываем по первому слову.
  const lemma = query.includes(" ") ? query.split(/\s+/)[0] : query;
  el("lemma-input").value = lemma;
  await showMorphology(lemma);
  setStatus(`Найдено вхождений: ${rowsCount} за ${elapsed.toFixed(2)} мс.`);
}

async function addDocumentsFromFiles(fileList) {
  const files = Array.from(fileList || []);
  if (!files.length) return;

  const form = new FormData();
  files.forEach((f) => form.append("files", f));

  setStatus("Добавление документов...");
  const res = await api.postForm("/documents/upload", form);
  setStatus(
    `Добавлено документов: ${res.inserted.length} из ${files.length}. Пропущено: ${res.skipped.length}.`
  );

  await refreshDocuments();
  // В desktop-версии после добавления обновляются частоты.
  await refreshFrequencies().catch(() => {});
}

function downloadJson(obj, filename) {
  const blob = new Blob([JSON.stringify(obj, null, 2)], { type: "application/json;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

async function saveCorpus() {
  const data = await api.downloadJson("/corpus/export");
  const ts = Date.now();
  downloadJson(data, `corpus_${ts}.json`);
  setStatus("Корпус сохранён.");
}

async function loadCorpusFromFile(file) {
  if (!file) return;
  const txt = await file.text();
  const json = JSON.parse(txt);
  if (!json.documents || !Array.isArray(json.documents)) {
    alert("Неверный формат JSON корпуса.");
    return;
  }

  await api.post("/corpus/import", {
    replace: true,
    name: json.name || "Imported corpus",
    documents: json.documents,
  });

  state.filterDocIds = null;
  state.selectedDocId = null;
  await refreshDocuments();
  await refreshFrequencies().catch(() => {});
  el("meta-text").textContent = "Выберите документ в списке «Документы корпуса».";
  setStatus("Корпус загружен.");
}

function bindUI() {
  el("btn-add-docs").addEventListener("click", () => el("upload-files").click());
  el("upload-files").addEventListener("change", async (e) => {
    await addDocumentsFromFiles(e.target.files);
    el("upload-files").value = "";
  });

  el("btn-save-corpus").addEventListener("click", () => saveCorpus().catch((err) => {
    console.error(err);
    alert("Не удалось сохранить корпус.");
  }));

  el("btn-load-corpus").addEventListener("click", () => el("load-corpus").click());
  el("load-corpus").addEventListener("change", async (e) => {
    const file = e.target.files?.[0];
    await loadCorpusFromFile(file).catch((err) => {
      console.error(err);
      alert("Не удалось загрузить корпус.");
    });
    el("load-corpus").value = "";
  });

  el("btn-help").addEventListener("click", () => {
    const helpText =
      `Справка. Корпусный менеджер — Вариант 21.\n\n` +
      `Словоформа vs лемма: словоформа — слово как в тексте (running, sang); лемма — начальная форма (run, sing). В частотных характеристиках «Словоформы» считают каждое вхождение отдельно, «Леммы» объединяют все формы одного слова.\n\n` +
      `1) Добавить документы — загрузка TXT/RTF/PDF/DOC/DOCX.\n` +
      `2) Сохранить/Загрузить корпус — корпус в JSON.\n` +
      `3) Поиск — запрос + по лемме/по словоформе + размер контекста.\n` +
      `4) Документы — фильтр по чекбоксам, двойной щелчок — текст, внизу сумма токенов.\n` +
      `5) Частотные характеристики — три режима (словоформы/леммы/POS). В режиме «Леммы» можно выделить строку и нажать «Удалить лемму из корпуса» (вхождения удаляются из документов навсегда).\n` +
      `6) Вкладка «Леммы» — добавить свою лемму в словарь (появится в частотах с частотой 0, если нет в текстах).\n` +
      `7) Морфология леммы — словоформы и частоты для введённой леммы.\n`;
    alert(helpText);
  });

  el("refresh-docs").addEventListener("click", () => refreshDocuments());

  el("pagination-prev").addEventListener("click", () => {
    const tab = getActiveTab();
    if (tab === "docs") {
      state.docsPage = Math.max(1, state.docsPage - 1);
      refreshDocuments().catch(console.error);
    } else if (tab === "freq") {
      state.freqPage = Math.max(1, state.freqPage - 1);
      refreshFrequencies().catch(console.error);
    } else if (tab === "conc" && state.lastConcQuery != null) {
      state.concPage = Math.max(1, state.concPage - 1);
      showConcordance(
        { query: state.lastConcQuery, by: state.lastConcBy, contextSize: state.lastConcContext },
        state.concPage
      ).catch(console.error);
    } else if (tab === "morph" && state.lastMorphLemma != null) {
      state.morphPage = Math.max(1, state.morphPage - 1);
      showMorphology(state.lastMorphLemma, state.morphPage).catch(console.error);
    }
  });
  el("pagination-next").addEventListener("click", () => {
    const tab = getActiveTab();
    if (tab === "docs") {
      state.docsPage = Math.min(state.docsTotalPages || 1, state.docsPage + 1);
      refreshDocuments().catch(console.error);
    } else if (tab === "freq") {
      state.freqPage = Math.min(state.freqTotalPages || 1, state.freqPage + 1);
      refreshFrequencies().catch(console.error);
    } else if (tab === "conc" && state.lastConcQuery != null) {
      state.concPage = Math.min(state.concTotalPages || 1, state.concPage + 1);
      showConcordance(
        { query: state.lastConcQuery, by: state.lastConcBy, contextSize: state.lastConcContext },
        state.concPage
      ).catch(console.error);
    } else if (tab === "morph" && state.lastMorphLemma != null) {
      state.morphPage = Math.min(state.morphTotalPages || 1, state.morphPage + 1);
      showMorphology(state.lastMorphLemma, state.morphPage).catch(console.error);
    }
  });
  el("pagination-page-size").addEventListener("change", () => {
    const v = Number(el("pagination-page-size").value);
    if (!Number.isFinite(v) || v <= 0) return;
    const tab = getActiveTab();
    if (tab === "docs") {
      state.docsPageSize = v;
      state.docsPage = 1;
      refreshDocuments().catch(console.error);
    } else if (tab === "freq") {
      state.freqPageSize = v;
      state.freqPage = 1;
      refreshFrequencies().catch(console.error);
    } else if (tab === "conc") {
      state.concPageSize = v;
      state.concPage = 1;
      if (state.lastConcQuery != null) {
        showConcordance(
          { query: state.lastConcQuery, by: state.lastConcBy, contextSize: state.lastConcContext },
          1
        ).catch(console.error);
      } else updatePaginationBar();
    } else if (tab === "morph") {
      state.morphPageSize = v;
      state.morphPage = 1;
      if (state.lastMorphLemma != null) {
        showMorphology(state.lastMorphLemma, 1).catch(console.error);
      } else updatePaginationBar();
    }
  });
  el("btn-use-filter").addEventListener("click", () => setFilterFromChecks());
  el("btn-reset-filter").addEventListener("click", () => resetFilter());
  el("btn-delete-doc").addEventListener("click", () => deleteSelectedDoc().catch(console.error));

  el("search-btn").addEventListener("click", () => handleSearch().catch((err) => {
    console.error(err);
    alert("Не удалось выполнить поиск.");
  }));

  el("morph-btn").addEventListener("click", () => {
    const lemma = el("lemma-input").value.trim();
    if (!lemma) return;
    showMorphology(lemma).catch(console.error);
  });

  el("btn-show-meta").addEventListener("click", () => showMetadata().catch(console.error));

  el("btn-refresh-freq").addEventListener("click", () => refreshFrequencies().catch(console.error));

  document.querySelectorAll(".freq-tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".freq-tab-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      state.freqKind = btn.dataset.kind;
      state.selectedFreqLemma = null;
      el("btn-delete-lemma").style.display = state.freqKind === "lemma" ? "" : "none";
    });
  });

  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      const tabId = btn.dataset.tab;
      document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
      el(`tab-${tabId}`).classList.add("active");
      if (tabId === "lemmas") refreshCustomLemmas().catch(console.error);
      updatePaginationBar();
    });
  });

  el("modal-close").addEventListener("click", () => closeModal());
  el("modal").addEventListener("click", (e) => {
    if (e.target === el("modal")) closeModal();
  });

  el("btn-delete-lemma").addEventListener("click", () => deleteLemmaFromCorpus().catch(console.error));
  el("btn-add-lemma").addEventListener("click", () => openLemmaModal(false));
  el("btn-refresh-lemmas").addEventListener("click", () => refreshCustomLemmas().catch(console.error));
  el("lemma-modal-close").addEventListener("click", () => closeLemmaModal());
  el("lemma-form-submit").addEventListener("click", () => lemmaFormSubmit());
  el("lemma-form-cancel").addEventListener("click", () => closeLemmaModal());
  el("lemma-modal").addEventListener("click", (e) => {
    if (e.target === el("lemma-modal")) closeLemmaModal();
  });

  // Benchmarks (как в desktop-версии, приближённо через доступные API)
  el("bench-search-music").addEventListener("click", async () => {
    const t0 = performance.now();
    const rows = await api.get(`/search?query=music&by=lemma&context_size=5&max_lines=2000${getFilterDocIdsParam()}`);
    const elapsed = performance.now() - t0;
    alert(`Поиск по лемме 'music': ${elapsed.toFixed(2)} мс, строк: ${rows.length}`);
  });
  el("bench-concord-concert").addEventListener("click", async () => {
    const t0 = performance.now();
    const rows = await api.get(`/search?query=concert&by=lemma&context_size=5&max_lines=500${getFilterDocIdsParam()}`);
    const elapsed = performance.now() - t0;
    // Обновим вкладку конкорданса теми же данными
    renderTable(
      "concordance-results",
      ["Слева", "Центр", "Справа", "Документ"],
      rows.map((row) => [row.left, row.center, row.right, row.doc_title || row.doc_id])
    );
    alert(`Конкорданс по 'concert': ${elapsed.toFixed(2)} мс, строк: ${rows.length}`);
  });
  el("bench-freq-update").addEventListener("click", async () => {
    const t0 = performance.now();
    await refreshFrequencies();
    const elapsed = performance.now() - t0;
    alert(`Обновление частот: ${elapsed.toFixed(2)} мс`);
  });
  el("bench-morph-instrument").addEventListener("click", async () => {
    const t0 = performance.now();
    el("lemma-input").value = "instrument";
    await showMorphology("instrument");
    const elapsed = performance.now() - t0;
    alert(`Морфология 'instrument': ${elapsed.toFixed(2)} мс`);
  });
}

bindUI();
updatePaginationBar();
refreshDocuments().catch((err) => {
  console.error(err);
  setStatus("Не удалось загрузить документы. Проверьте backend.");
  el("docs-table").querySelector("tbody").innerHTML = "<tr><td colspan='5'>Ошибка загрузки</td></tr>";
});
