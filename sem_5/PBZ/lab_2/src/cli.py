#!/usr/bin/env python3
import argparse
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "db" / "park.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def print_rows(rows):
    if not rows:
        print("<empty>")
        return
    headers = rows[0].keys()
    print("\t".join(headers))
    for r in rows:
        print("\t".join(str(r[h]) if r[h] is not None else "" for h in headers))


def cmd_company(args):
    with get_conn() as conn:
        if args.action == "get":
            rows = conn.execute("SELECT * FROM company WHERE id = 1").fetchall()
            print_rows(rows)
        elif args.action == "set":
            conn.execute(
                """
                INSERT INTO company(id, name, legal_address)
                VALUES(1, ?, ?)
                ON CONFLICT(id) DO UPDATE SET name=excluded.name, legal_address=excluded.legal_address
                """,
                (args.name, args.address),
            )
            conn.commit()
            print("Company saved")


def cmd_species(args):
    with get_conn() as conn:
        if args.action == "add":
            conn.execute("INSERT INTO species(latin_name, common_name) VALUES(?, ?)", (args.latin, args.common))
            conn.commit()
            print("Species added")
        elif args.action == "list":
            rows = conn.execute("SELECT * FROM species ORDER BY latin_name").fetchall()
            print_rows(rows)
        elif args.action == "update":
            conn.execute("UPDATE species SET latin_name=?, common_name=? WHERE id=?", (args.latin, args.common, args.id))
            conn.commit()
            print("Species updated")
        elif args.action == "delete":
            conn.execute("DELETE FROM species WHERE id=?", (args.id,))
            conn.commit()
            print("Species deleted")


def cmd_park(args):
    with get_conn() as conn:
        if args.action == "add":
            conn.execute("INSERT INTO park(name, address) VALUES(?, ?)", (args.name, args.address))
            conn.commit()
            print("Park added")
        elif args.action == "list":
            rows = conn.execute("SELECT * FROM park ORDER BY name").fetchall()
            print_rows(rows)
        elif args.action == "update":
            conn.execute("UPDATE park SET name=?, address=? WHERE id=?", (args.name, args.address, args.id))
            conn.commit()
            print("Park updated")
        elif args.action == "delete":
            conn.execute("DELETE FROM park WHERE id=?", (args.id,))
            conn.commit()
            print("Park deleted")


def cmd_zone(args):
    with get_conn() as conn:
        if args.action == "add":
            conn.execute("INSERT INTO zone(park_id, name) VALUES(?, ?)", (args.park_id, args.name))
            conn.commit()
            print("Zone added")
        elif args.action == "list":
            rows = conn.execute(
                """
                SELECT z.id, z.name, p.name AS park, z.park_id
                FROM zone z JOIN park p ON p.id = z.park_id
                ORDER BY p.name, z.name
                """
            ).fetchall()
            print_rows(rows)
        elif args.action == "update":
            conn.execute("UPDATE zone SET park_id=?, name=? WHERE id=?", (args.park_id, args.name, args.id))
            conn.commit()
            print("Zone updated")
        elif args.action == "delete":
            conn.execute("DELETE FROM zone WHERE id=?", (args.id,))
            conn.commit()
            print("Zone deleted")


def cmd_plant(args):
    with get_conn() as conn:
        if args.action == "add":
            conn.execute(
                """
                INSERT INTO plant(zone_id, species_id, plant_number, planting_date, age_years_at_planting)
                VALUES(?, ?, ?, ?, ?)
                """,
                (args.zone_id, args.species_id, args.number, args.date, args.age),
            )
            conn.commit()
            print("Plant added")
        elif args.action == "list":
            rows = conn.execute(
                """
                SELECT pl.id, pl.zone_id, z.name AS zone, pl.species_id, s.common_name, s.latin_name,
                       pl.plant_number, pl.planting_date, pl.age_years_at_planting
                FROM plant pl
                JOIN zone z ON z.id = pl.zone_id
                JOIN species s ON s.id = pl.species_id
                ORDER BY z.name, pl.plant_number
                """
            ).fetchall()
            print_rows(rows)
        elif args.action == "update":
            conn.execute(
                "UPDATE plant SET zone_id=?, species_id=?, plant_number=?, planting_date=?, age_years_at_planting=? WHERE id=?",
                (args.zone_id, args.species_id, args.number, args.date, args.age, args.id),
            )
            conn.commit()
            print("Plant updated")
        elif args.action == "delete":
            conn.execute("DELETE FROM plant WHERE id=?", (args.id,))
            conn.commit()
            print("Plant deleted")


def cmd_attendant(args):
    with get_conn() as conn:
        if args.action == "add":
            conn.execute(
                "INSERT INTO attendant(full_name, birth_date, phone, address) VALUES(?, ?, ?, ?)",
                (args.name, args.birth, args.phone, args.address),
            )
            conn.commit()
            print("Attendant added")
        elif args.action == "list":
            rows = conn.execute("SELECT * FROM attendant ORDER BY full_name").fetchall()
            print_rows(rows)
        elif args.action == "update":
            conn.execute(
                "UPDATE attendant SET full_name=?, birth_date=?, phone=?, address=? WHERE id=?",
                (args.name, args.birth, args.phone, args.address, args.id),
            )
            conn.commit()
            print("Attendant updated")
        elif args.action == "delete":
            conn.execute("DELETE FROM attendant WHERE id=?", (args.id,))
            conn.commit()
            print("Attendant deleted")


def cmd_assignment(args):
    with get_conn() as conn:
        if args.action == "assign":
            conn.execute(
                "INSERT INTO attendant_assignment(plant_id, assignment_date, attendant_id) VALUES(?, ?, ?)",
                (args.plant_id, args.date, args.attendant_id),
            )
            conn.commit()
            print("Assigned")
        elif args.action == "list":
            rows = conn.execute(
                """
                SELECT aa.id, aa.assignment_date, a.full_name, pl.id AS plant_id, pl.plant_number, z.name AS zone
                FROM attendant_assignment aa
                JOIN attendant a ON a.id = aa.attendant_id
                JOIN plant pl ON pl.id = aa.plant_id
                JOIN zone z ON z.id = pl.zone_id
                ORDER BY aa.assignment_date DESC
                """
            ).fetchall()
            print_rows(rows)
        elif args.action == "delete":
            conn.execute("DELETE FROM attendant_assignment WHERE id=?", (args.id,))
            conn.commit()
            print("Assignment deleted")


def cmd_decorator(args):
    with get_conn() as conn:
        if args.action == "add":
            conn.execute(
                """
                INSERT INTO decorator(full_name, birth_date, phone, address, education, institution, category)
                VALUES(?, ?, ?, ?, ?, ?, ?)
                """,
                (args.name, args.birth, args.phone, args.address, args.education, args.institution, args.category),
            )
            conn.commit()
            print("Decorator added")
        elif args.action == "list":
            rows = conn.execute("SELECT * FROM decorator ORDER BY full_name").fetchall()
            print_rows(rows)
        elif args.action == "update":
            conn.execute(
                """
                UPDATE decorator SET full_name=?, birth_date=?, phone=?, address=?, education=?, institution=?, category=?
                WHERE id=?
                """,
                (args.name, args.birth, args.phone, args.address, args.education, args.institution, args.category, args.id),
            )
            conn.commit()
            print("Decorator updated")
        elif args.action == "delete":
            conn.execute("DELETE FROM decorator WHERE id=?", (args.id,))
            conn.commit()
            print("Decorator deleted")


def cmd_regime(args):
    with get_conn() as conn:
        if args.action == "add":
            conn.execute(
                """
                INSERT INTO watering_regime(species_id, min_age_years, max_age_years, day_pattern, time_of_day, water_liters)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (args.species_id, args.min_age, args.max_age, args.pattern, args.time, args.liters),
            )
            conn.commit()
            print("Regime added")
        elif args.action == "list":
            rows = conn.execute(
                """
                SELECT wr.id, s.common_name, s.latin_name, wr.min_age_years, wr.max_age_years, wr.day_pattern, wr.time_of_day, wr.water_liters
                FROM watering_regime wr JOIN species s ON s.id = wr.species_id
                ORDER BY s.common_name, wr.min_age_years
                """
            ).fetchall()
            print_rows(rows)
        elif args.action == "delete":
            conn.execute("DELETE FROM watering_regime WHERE id=?", (args.id,))
            conn.commit()
            print("Regime deleted")


def cmd_watering(args):
    with get_conn() as conn:
        if args.action == "add":
            conn.execute(
                "INSERT INTO watering(plant_id, watering_date, time_of_day, liters) VALUES(?, ?, ?, ?)",
                (args.plant_id, args.date, args.time, args.liters),
            )
            conn.commit()
            print("Watering recorded")
        elif args.action == "list":
            rows = conn.execute(
                """
                SELECT w.id, w.watering_date, w.time_of_day, w.liters, pl.id AS plant_id, pl.plant_number, z.name AS zone
                FROM watering w JOIN plant pl ON pl.id = w.plant_id
                JOIN zone z ON z.id = pl.zone_id
                ORDER BY w.watering_date DESC, w.time_of_day DESC
                """
            ).fetchall()
            print_rows(rows)
        elif args.action == "delete":
            conn.execute("DELETE FROM watering WHERE id=?", (args.id,))
            conn.commit()
            print("Watering deleted")


# Reports
def cmd_report_species(args):
    # Full information on plantings of a given species
    with get_conn() as conn:
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
            (args.species, args.species),
        ).fetchall()
        print_rows(rows)


def cmd_report_staff_on_date(args):
    # List staff (attendants and decorators) working on a given date – name, birth_date, phone
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT a.full_name AS name, a.birth_date, a.phone, 'attendant' AS role
            FROM attendant a
            WHERE a.id IN (
                SELECT DISTINCT attendant_id FROM attendant_assignment WHERE assignment_date = ?
            )
            UNION ALL
            SELECT d.full_name, d.birth_date, d.phone, 'decorator' AS role
            FROM decorator d
            -- Decorators assumed working every day unless schedule table added; include all
            """,
            (args.date,),
        ).fetchall()
        print_rows(rows)


def cmd_report_plants_regimes_today(args):
    # List all plants of given species and their watering regimes for today (by age)
    with get_conn() as conn:
        rows = conn.execute(
            """
            WITH plant_age_today AS (
              SELECT p.id, p.species_id,
                     CAST(
                       (julianday(date('now')) - julianday(p.planting_date)) / 365.25
                       + p.age_years_at_planting AS INTEGER
                     ) AS age_years
              FROM plant p
              JOIN species s ON s.id = p.species_id
              WHERE s.common_name = ? OR s.latin_name = ?
            )
            SELECT p.id AS plant_id, z.name AS zone, pk.name AS park,
                   s.common_name, s.latin_name,
                   a.age_years, wr.day_pattern, wr.time_of_day, wr.water_liters
            FROM plant_age_today a
            JOIN plant p ON p.id = a.id
            JOIN zone z ON z.id = p.zone_id
            JOIN park pk ON pk.id = z.park_id
            JOIN species s ON s.id = p.species_id
            LEFT JOIN watering_regime wr
              ON wr.species_id = s.id AND a.age_years BETWEEN wr.min_age_years AND wr.max_age_years
            ORDER BY pk.name, z.name, p.plant_number
            """,
            (args.species, args.species),
        ).fetchall()
        print_rows(rows)


def build_parser():
    parser = argparse.ArgumentParser(description="Park Plantings DB CLI (raw SQL)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # company
    p_company = sub.add_parser("company")
    p_company_sub = p_company.add_subparsers(dest="action", required=True)
    p_company_sub.add_parser("get")
    p_company_set = p_company_sub.add_parser("set")
    p_company_set.add_argument("name")
    p_company_set.add_argument("address")
    p_company.set_defaults(func=cmd_company)

    # species
    p_species = sub.add_parser("species")
    p_species_sub = p_species.add_subparsers(dest="action", required=True)
    sp_add = p_species_sub.add_parser("add")
    sp_add.add_argument("latin")
    sp_add.add_argument("common")
    p_species_sub.add_parser("list")
    sp_upd = p_species_sub.add_parser("update")
    sp_upd.add_argument("id", type=int)
    sp_upd.add_argument("latin")
    sp_upd.add_argument("common")
    sp_del = p_species_sub.add_parser("delete")
    sp_del.add_argument("id", type=int)
    p_species.set_defaults(func=cmd_species)

    # park
    p_park = sub.add_parser("park")
    p_park_sub = p_park.add_subparsers(dest="action", required=True)
    pk_add = p_park_sub.add_parser("add")
    pk_add.add_argument("name")
    pk_add.add_argument("address")
    p_park_sub.add_parser("list")
    pk_upd = p_park_sub.add_parser("update")
    pk_upd.add_argument("id", type=int)
    pk_upd.add_argument("name")
    pk_upd.add_argument("address")
    pk_del = p_park_sub.add_parser("delete")
    pk_del.add_argument("id", type=int)
    p_park.set_defaults(func=cmd_park)

    # zone
    p_zone = sub.add_parser("zone")
    p_zone_sub = p_zone.add_subparsers(dest="action", required=True)
    zn_add = p_zone_sub.add_parser("add")
    zn_add.add_argument("park_id", type=int)
    zn_add.add_argument("name")
    p_zone_sub.add_parser("list")
    zn_upd = p_zone_sub.add_parser("update")
    zn_upd.add_argument("id", type=int)
    zn_upd.add_argument("park_id", type=int)
    zn_upd.add_argument("name")
    zn_del = p_zone_sub.add_parser("delete")
    zn_del.add_argument("id", type=int)
    p_zone.set_defaults(func=cmd_zone)

    # plant
    p_plant = sub.add_parser("plant")
    p_plant_sub = p_plant.add_subparsers(dest="action", required=True)
    pl_add = p_plant_sub.add_parser("add")
    pl_add.add_argument("zone_id", type=int)
    pl_add.add_argument("species_id", type=int)
    pl_add.add_argument("number", type=int)
    pl_add.add_argument("date")
    pl_add.add_argument("age", type=int)
    p_plant_sub.add_parser("list")
    pl_upd = p_plant_sub.add_parser("update")
    pl_upd.add_argument("id", type=int)
    pl_upd.add_argument("zone_id", type=int)
    pl_upd.add_argument("species_id", type=int)
    pl_upd.add_argument("number", type=int)
    pl_upd.add_argument("date")
    pl_upd.add_argument("age", type=int)
    pl_del = p_plant_sub.add_parser("delete")
    pl_del.add_argument("id", type=int)
    p_plant.set_defaults(func=cmd_plant)

    # attendant
    p_att = sub.add_parser("attendant")
    p_att_sub = p_att.add_subparsers(dest="action", required=True)
    at_add = p_att_sub.add_parser("add")
    at_add.add_argument("name")
    at_add.add_argument("birth")
    at_add.add_argument("phone")
    at_add.add_argument("address")
    p_att_sub.add_parser("list")
    at_upd = p_att_sub.add_parser("update")
    at_upd.add_argument("id", type=int)
    at_upd.add_argument("name")
    at_upd.add_argument("birth")
    at_upd.add_argument("phone")
    at_upd.add_argument("address")
    at_del = p_att_sub.add_parser("delete")
    at_del.add_argument("id", type=int)
    p_att.set_defaults(func=cmd_attendant)

    # assignment
    p_asg = sub.add_parser("assignment")
    p_asg_sub = p_asg.add_subparsers(dest="action", required=True)
    as_assign = p_asg_sub.add_parser("assign")
    as_assign.add_argument("plant_id", type=int)
    as_assign.add_argument("date")
    as_assign.add_argument("attendant_id", type=int)
    p_asg_sub.add_parser("list")
    as_del = p_asg_sub.add_parser("delete")
    as_del.add_argument("id", type=int)
    p_asg.set_defaults(func=cmd_assignment)

    # decorator
    p_dec = sub.add_parser("decorator")
    p_dec_sub = p_dec.add_subparsers(dest="action", required=True)
    dc_add = p_dec_sub.add_parser("add")
    dc_add.add_argument("name")
    dc_add.add_argument("birth")
    dc_add.add_argument("phone")
    dc_add.add_argument("address")
    dc_add.add_argument("education")
    dc_add.add_argument("institution")
    dc_add.add_argument("category")
    p_dec_sub.add_parser("list")
    dc_upd = p_dec_sub.add_parser("update")
    dc_upd.add_argument("id", type=int)
    dc_upd.add_argument("name")
    dc_upd.add_argument("birth")
    dc_upd.add_argument("phone")
    dc_upd.add_argument("address")
    dc_upd.add_argument("education")
    dc_upd.add_argument("institution")
    dc_upd.add_argument("category")
    dc_del = p_dec_sub.add_parser("delete")
    dc_del.add_argument("id", type=int)
    p_dec.set_defaults(func=cmd_decorator)

    # watering regime
    p_reg = sub.add_parser("regime")
    p_reg_sub = p_reg.add_subparsers(dest="action", required=True)
    rg_add = p_reg_sub.add_parser("add")
    rg_add.add_argument("species_id", type=int)
    rg_add.add_argument("min_age", type=int)
    rg_add.add_argument("max_age", type=int)
    rg_add.add_argument("pattern")
    rg_add.add_argument("time")
    rg_add.add_argument("liters", type=float)
    p_reg_sub.add_parser("list")
    rg_del = p_reg_sub.add_parser("delete")
    rg_del.add_argument("id", type=int)
    p_reg.set_defaults(func=cmd_regime)

    # watering
    p_wat = sub.add_parser("watering")
    p_wat_sub = p_wat.add_subparsers(dest="action", required=True)
    wt_add = p_wat_sub.add_parser("add")
    wt_add.add_argument("plant_id", type=int)
    wt_add.add_argument("date")
    wt_add.add_argument("time")
    wt_add.add_argument("liters", type=float)
    p_wat_sub.add_parser("list")
    wt_del = p_wat_sub.add_parser("delete")
    wt_del.add_argument("id", type=int)
    p_wat.set_defaults(func=cmd_watering)

    # reports
    p_r1 = sub.add_parser("report_species")
    p_r1.add_argument("species", help="species common or latin name")
    p_r1.set_defaults(func=cmd_report_species)

    p_r2 = sub.add_parser("report_staff_on_date")
    p_r2.add_argument("date")
    p_r2.set_defaults(func=cmd_report_staff_on_date)

    p_r3 = sub.add_parser("report_plants_regimes_today")
    p_r3.add_argument("species")
    p_r3.set_defaults(func=cmd_report_plants_regimes_today)

    return parser


def main(argv):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except sqlite3.IntegrityError as e:
        print(f"Integrity error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])


