import sqlite3
from pathlib import Path
import streamlit as st

DB_PATH = Path(__file__).resolve().parents[1] / "db" / "park.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def section_company():
    st.header("Компания")
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM company WHERE id=1").fetchone()
        name = st.text_input("Название", value=row["name"] if row else "")
        addr = st.text_input("Юридический адрес", value=row["legal_address"] if row else "")
        if st.button("Сохранить", type="primary"):
            conn.execute(
                """
                INSERT INTO company(id, name, legal_address)
                VALUES(1, ?, ?)
                ON CONFLICT(id) DO UPDATE SET name=excluded.name, legal_address=excluded.legal_address
                """,
                (name, addr),
            )
            conn.commit()
            st.success("Сохранено")


def list_species(conn):
    return conn.execute("SELECT * FROM species ORDER BY common_name NULLS LAST, latin_name").fetchall()


def section_species():
    st.header("Виды растений")
    with get_conn() as conn:
        with st.form("add_species"):
            latin = st.text_input("Латинское название")
            common = st.text_input("Русское название")
            submitted = st.form_submit_button("Добавить")
            if submitted and latin:
                conn.execute("INSERT INTO species(latin_name, common_name) VALUES(?, ?)", (latin, common))
                conn.commit()
                st.success("Добавлено")
        rows = list_species(conn)
        st.subheader("Список")
        for r in rows:
            with st.expander(f"{r['common_name'] or ''} ({r['latin_name']}) [id={r['id']}]"):
                nl = st.text_input("Латинское", value=r["latin_name"], key=f"sl{r['id']}")
                nc = st.text_input("Русское", value=r["common_name"] or "", key=f"sc{r['id']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Обновить", key=f"su{r['id']}"):
                        conn.execute("UPDATE species SET latin_name=?, common_name=? WHERE id=?", (nl, nc, r["id"]))
                        conn.commit()
                        st.success("Обновлено")
                with col2:
                    if st.button("Удалить", key=f"sd{r['id']}"):
                        conn.execute("DELETE FROM species WHERE id=?", (r["id"],))
                        conn.commit()
                        st.warning("Удалено")


def parks_options(conn):
    return conn.execute("SELECT id, name FROM park ORDER BY name").fetchall()


def zones_for_park(conn, park_id):
    return conn.execute("SELECT id, name FROM zone WHERE park_id=? ORDER BY name", (park_id,)).fetchall()


def section_parks_zones():
    st.header("Парки и зоны")
    with get_conn() as conn:
        st.subheader("Добавить парк")
        with st.form("add_park"):
            name = st.text_input("Название парка")
            addr = st.text_input("Адрес")
            if st.form_submit_button("Добавить парк") and name:
                conn.execute("INSERT INTO park(name, address) VALUES(?, ?)", (name, addr))
                conn.commit()
                st.success("Парк добавлен")

        st.subheader("Добавить зону")
        parks = parks_options(conn)
        park_map = {p["name"]: p["id"] for p in parks}
        park_name = st.selectbox("Парк", list(park_map.keys()), key="zone_park_select") if parks else None
        zone_name = st.text_input("Название зоны")
        if st.button("Добавить зону") and park_name and zone_name:
            conn.execute("INSERT INTO zone(park_id, name) VALUES(?, ?)", (park_map[park_name], zone_name))
            conn.commit()
            st.success("Зона добавлена")

        st.subheader("Список парков и зон")
        for p in parks:
            st.markdown(f"**{p['name']}**")
            zones = zones_for_park(conn, p["id"])
            if not zones:
                st.caption("Нет зон")
            else:
                st.write(
                    [{"id": z["id"], "name": z["name"]} for z in zones]
                )


def section_plants():
    st.header("Растения")
    with get_conn() as conn:
        parks = parks_options(conn)
        park_map = {p["name"]: p["id"] for p in parks}
        sp_rows = list_species(conn)
        sp_map = {f"{s['common_name'] or ''} ({s['latin_name']})": s["id"] for s in sp_rows}

        st.subheader("Добавить растение")
        if parks and sp_rows:
            park_name = st.selectbox("Парк", list(park_map.keys()), key="plant_park")
            zones = zones_for_park(conn, park_map[park_name])
            zone_map = {z["name"]: z["id"] for z in zones}
            zone_name = st.selectbox("Зона", list(zone_map.keys()), key="plant_zone") if zones else None
            sp_name = st.selectbox("Вид", list(sp_map.keys()), key="plant_species")
            number = st.number_input("Номер в зоне", min_value=1, step=1, key="plant_number")
            pdate = st.date_input("Дата высадки", key="plant_date")
            age = st.number_input("Возраст при высадке (лет)", min_value=0, step=1, key="plant_age")
            if st.button("Добавить растение") and zone_name:
                conn.execute(
                    "INSERT INTO plant(zone_id, species_id, plant_number, planting_date, age_years_at_planting) VALUES(?, ?, ?, ?, ?)",
                    (zone_map[zone_name], sp_map[sp_name], int(number), str(pdate), int(age)),
                )
                conn.commit()
                st.success("Добавлено")

        st.subheader("Список растений")
        rows = conn.execute(
            """
            SELECT pl.id, pk.name AS park, z.name AS zone, s.common_name, s.latin_name, pl.plant_number, pl.planting_date, pl.age_years_at_planting
            FROM plant pl JOIN zone z ON z.id=pl.zone_id JOIN park pk ON pk.id=z.park_id JOIN species s ON s.id=pl.species_id
            ORDER BY pk.name, z.name, pl.plant_number
            """
        ).fetchall()
        st.dataframe(rows)


def section_staff():
    st.header("Сотрудники и закрепления")
    with get_conn() as conn:
        st.subheader("Служители")
        with st.form("add_att"):
            name = st.text_input("ФИО")
            b = st.date_input("Дата рождения")
            phone = st.text_input("Телефон")
            addr = st.text_input("Адрес")
            if st.form_submit_button("Добавить служителя") and name:
                conn.execute("INSERT INTO attendant(full_name, birth_date, phone, address) VALUES(?, ?, ?, ?)", (name, str(b), phone, addr))
                conn.commit()
                st.success("Добавлено")

        st.subheader("Декораторы")
        with st.form("add_dec"):
            name = st.text_input("ФИО", key="dname")
            b = st.date_input("Дата рождения", key="dbirth")
            phone = st.text_input("Телефон", key="dphone")
            addr = st.text_input("Адрес", key="daddr")
            edu = st.text_input("Образование")
            inst = st.text_input("Учреждение")
            cat = st.text_input("Категория")
            if st.form_submit_button("Добавить декоратора") and name:
                conn.execute(
                    "INSERT INTO decorator(full_name, birth_date, phone, address, education, institution, category) VALUES(?, ?, ?, ?, ?, ?, ?)",
                    (name, str(b), phone, addr, edu, inst, cat),
                )
                conn.commit()
                st.success("Добавлено")

        st.subheader("Закрепления служителей за растениями")
        plants = conn.execute(
            "SELECT id, plant_number FROM plant ORDER BY id"
        ).fetchall()
        atts = conn.execute(
            "SELECT id, full_name FROM attendant ORDER BY full_name"
        ).fetchall()
        if plants and atts:
            plant_opt = st.selectbox("Растение", [f"id={p['id']} №{p['plant_number']}" for p in plants], key="assign_plant")
            att_opt = st.selectbox("Служитель", [f"id={a['id']} {a['full_name']}" for a in atts], key="assign_attendant")
            adate = st.date_input("Дата")
            if st.button("Закрепить"):
                pid = int(plant_opt.split()[0].split('=')[1])
                aid = int(att_opt.split()[0].split('=')[1])
                conn.execute("INSERT INTO attendant_assignment(plant_id, assignment_date, attendant_id) VALUES(?, ?, ?)", (pid, str(adate), aid))
                conn.commit()
                st.success("Закреплено")


def section_regimes_waterings():
    st.header("Режимы полива и поливы")
    with get_conn() as conn:
        st.subheader("Режимы полива")
        species = list_species(conn)
        if species:
            sp_map = {f"{s['common_name'] or ''} ({s['latin_name']})": s["id"] for s in species}
            sp_name = st.selectbox("Вид", list(sp_map.keys()), key="regime_species")
            min_age = st.number_input("Мин. возраст (годы)", min_value=0, step=1, key="regime_min_age")
            max_age = st.number_input("Макс. возраст (годы)", min_value=0, step=1, key="regime_max_age")
            pattern = st.text_input("Шаблон дня (напр., daily)", key="regime_pattern")
            time = st.text_input("Время (HH:MM)", key="regime_time")
            liters = st.number_input("Литры", min_value=0.0, step=1.0, key="regime_liters")
            if st.button("Добавить режим"):
                conn.execute(
                    "INSERT INTO watering_regime(species_id, min_age_years, max_age_years, day_pattern, time_of_day, water_liters) VALUES(?, ?, ?, ?, ?, ?)",
                    (sp_map[sp_name], int(min_age), int(max_age), pattern, time, float(liters)),
                )
                conn.commit()
                st.success("Добавлено")

        st.subheader("Поливы")
        plants = conn.execute("SELECT id, plant_number FROM plant ORDER BY id").fetchall()
        if plants:
            plant_label = st.selectbox("Растение", [f"id={p['id']} №{p['plant_number']}" for p in plants], key="watering_plant")
            wdate = st.date_input("Дата полива", key="watering_date")
            wtime = st.text_input("Время (HH:MM)", value="08:00", key="watering_time")
            wl = st.number_input("Литры", min_value=0.0, step=1.0, key="watering_liters")
            if st.button("Записать полив"):
                pid = int(plant_label.split()[0].split('=')[1])
                conn.execute("INSERT INTO watering(plant_id, watering_date, time_of_day, liters) VALUES(?, ?, ?, ?)", (pid, str(wdate), wtime, float(wl)))
                conn.commit()
                st.success("Записано")


def section_reports():
    st.header("Отчёты")
    with get_conn() as conn:
        st.subheader("Насаждения заданного вида")
        q = st.text_input("Вид (русское или латинское)")
        if st.button("Показать насаждения") and q:
            rows = conn.execute(
                """
                SELECT p.id AS plant_id, sp.common_name, sp.latin_name, pk.name AS park, z.name AS zone,
                       p.plant_number, p.planting_date, p.age_years_at_planting
                FROM plant p
                JOIN species sp ON sp.id = p.species_id
                JOIN zone z ON z.id = p.zone_id
                JOIN park pk ON pk.id = z.park_id
                WHERE sp.common_name = ? OR sp.latin_name = ?
                ORDER BY pk.name, z.name, p.plant_number
                """,
                (q, q),
            ).fetchall()
            st.dataframe(rows)

        st.subheader("Сотрудники, работающие на дату")
        d = st.date_input("Дата отчёта")
        if st.button("Показать сотрудников"):
            rows = conn.execute(
                """
                SELECT a.full_name AS name, a.birth_date, a.phone, 'attendant' AS role
                FROM attendant a WHERE a.id IN (
                  SELECT DISTINCT attendant_id FROM attendant_assignment WHERE assignment_date = ?
                )
                UNION ALL
                SELECT d.full_name, d.birth_date, d.phone, 'decorator' AS role FROM decorator d
                """,
                (str(d),),
            ).fetchall()
            st.dataframe(rows)

        st.subheader("Растения вида и режимы их полива (на сегодня)")
        q2 = st.text_input("Вид для режимов (русское или латинское)")
        if st.button("Показать режимы") and q2:
            rows = conn.execute(
                """
                WITH plant_age_today AS (
                  SELECT p.id, p.species_id,
                         CAST((julianday(date('now')) - julianday(p.planting_date)) / 365.25 + p.age_years_at_planting AS INTEGER) AS age_years
                  FROM plant p JOIN species s ON s.id = p.species_id
                  WHERE s.common_name = ? OR s.latin_name = ?
                )
                SELECT p.id AS plant_id, z.name AS zone, pk.name AS park,
                       s.common_name, s.latin_name, a.age_years,
                       wr.day_pattern, wr.time_of_day, wr.water_liters
                FROM plant_age_today a
                JOIN plant p ON p.id = a.id
                JOIN zone z ON z.id = p.zone_id
                JOIN park pk ON pk.id = z.park_id
                JOIN species s ON s.id = p.species_id
                LEFT JOIN watering_regime wr
                  ON wr.species_id = s.id AND a.age_years BETWEEN wr.min_age_years AND wr.max_age_years
                ORDER BY pk.name, z.name, p.plant_number
                """,
                (q2, q2),
            ).fetchall()
            st.dataframe(rows)


def main():
    st.set_page_config(page_title="Парки — Банк данных", layout="wide")
    st.title("Банк данных насаждений парков")
    tabs = st.tabs([
        "Компания",
        "Виды",
        "Парки/Зоны",
        "Растения",
        "Сотрудники",
        "Режимы/Поливы",
        "Отчёты",
    ])
    with tabs[0]:
        section_company()
    with tabs[1]:
        section_species()
    with tabs[2]:
        section_parks_zones()
    with tabs[3]:
        section_plants()
    with tabs[4]:
        section_staff()
    with tabs[5]:
        section_regimes_waterings()
    with tabs[6]:
        section_reports()


if __name__ == "__main__":
    main()


