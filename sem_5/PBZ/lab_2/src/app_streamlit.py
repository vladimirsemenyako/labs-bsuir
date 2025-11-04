import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'park_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Ошибка подключения к БД: {e}")
        return None

def execute_query(query, params=None, fetch=True, show_error=True):
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch:
                result = cur.fetchall()
                conn.commit()
                return result
            else:
                conn.commit()
                return True
    except psycopg2.errors.UniqueViolation as e:
        conn.rollback()
        if show_error:
            error_msg = str(e)
            if 'firm' in error_msg.lower() and 'name' in error_msg.lower():
                st.error("Фирма с таким названием уже существует!")
            elif 'plants' in error_msg.lower() and 'local_plant_number' in error_msg.lower():
                st.error("Растение с таким номером уже существует в этой зоне!")
            elif 'employees' in error_msg.lower() and 'phone' in error_msg.lower():
                st.error("Сотрудник с таким телефоном уже существует!")
            elif 'schedule' in error_msg.lower():
                st.error("На эту дату уже назначен служитель для этого растения!")
            else:
                st.error(f"Ошибка: запись с такими данными уже существует!")
        return None
    except psycopg2.errors.NotNullViolation as e:
        conn.rollback()
        if show_error:
            st.error("Ошибка: не заполнены обязательные поля!")
        return None
    except psycopg2.errors.ForeignKeyViolation as e:
        conn.rollback()
        if show_error:
            st.error("Ошибка: ссылка на несуществующую запись!")
        return None
    except Exception as e:
        conn.rollback()
        if show_error:
            st.error(f"Ошибка выполнения запроса: {e}")
        return None
    finally:
        conn.close()

def init_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = 'Главная'

def page_firm():
    st.header("Управление информацией о фирме")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Просмотр", "Добавить", "Редактировать", "Удалить"])
    
    with tab1:
        firms = execute_query("SELECT * FROM firm ORDER BY firm_id")
        if firms:
            st.dataframe(firms, use_container_width=True)
        else:
            st.info("Фирма не найдена")
    
    with tab2:
        with st.form("add_firm"):
            name = st.text_input("Название фирмы *", key="add_firm_name")
            legal_address = st.text_area("Юридический адрес", key="add_firm_address")
            
            if st.form_submit_button("Добавить"):
                if name:
                    result = execute_query(
                        "INSERT INTO firm (name, legal_address) VALUES (%s, %s) RETURNING firm_id",
                        (name, legal_address or None),
                        fetch=True
                    )
                    if result:
                        st.success(f"Фирма '{name}' успешно добавлена!")
                        st.rerun()
                else:
                    st.error("Название фирмы обязательно")
    
    with tab3:
        firms = execute_query("SELECT firm_id, name FROM firm ORDER BY firm_id")
        if firms:
            firm_options = {f"{f['name']} (ID: {f['firm_id']})": f['firm_id'] for f in firms}
            selected = st.selectbox("Выберите фирму", list(firm_options.keys()), key="edit_firm_select")
            
            if selected:
                firm_id = firm_options[selected]
                firm_data = execute_query("SELECT * FROM firm WHERE firm_id = %s", (firm_id,))
                
                if firm_data:
                    with st.form("edit_firm"):
                        name = st.text_input("Название", value=firm_data[0]['name'], key="edit_firm_name")
                        legal_address = st.text_area("Юридический адрес", value=firm_data[0]['legal_address'] or "", key="edit_firm_address")
                        
                        if st.form_submit_button("Обновить"):
                            result = execute_query(
                                "UPDATE firm SET name = %s, legal_address = %s WHERE firm_id = %s",
                                (name, legal_address or None, firm_id),
                                fetch=False
                            )
                            if result:
                                st.success("Фирма обновлена!")
                                st.rerun()
        else:
            st.info("Нет фирм для редактирования")
    
    with tab4:
        firms = execute_query("SELECT firm_id, name FROM firm ORDER BY firm_id")
        if firms:
            firm_options = {f"{f['name']} (ID: {f['firm_id']})": f['firm_id'] for f in firms}
            selected = st.selectbox("Выберите фирму для удаления", list(firm_options.keys()), key="delete_firm_select")
            
            if selected:
                firm_id = firm_options[selected]
                
                with st.form("delete_firm"):
                    st.warning(f"Вы уверены, что хотите удалить эту фирму? Это действие нельзя отменить!")
                    if st.form_submit_button("Удалить", type="primary"):
                        result = execute_query("DELETE FROM firm WHERE firm_id = %s", (firm_id,), fetch=False)
                        if result:
                            st.success("Фирма удалена!")
                            st.rerun()
        else:
            st.info("Нет фирм для удаления")

def page_parks_zones():
    st.header("Управление парками и зонами")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Парки", "Добавить парк", "Редактировать парк", "Удалить парк", "Зоны", "Добавить зону"])
    
    with tab1:
        parks = execute_query("""
            SELECT p.park_id, p.name, f.name as firm_name 
            FROM parks p 
            JOIN firm f ON p.firm_id = f.firm_id 
            ORDER BY p.park_id
        """)
        
        if parks:
            st.dataframe(parks, use_container_width=True)
        else:
            st.info("Парки не найдены")
    
    with tab2:
        firms = execute_query("SELECT firm_id, name FROM firm ORDER BY firm_id")
        if firms:
            firm_options = {f['name']: f['firm_id'] for f in firms}
            selected_firm = st.selectbox("Выберите фирму", list(firm_options.keys()), key="add_park_firm")
            
            with st.form("add_park"):
                park_name = st.text_input("Название парка *", key="add_park_name")
                
                if st.form_submit_button("Добавить парк"):
                    if park_name:
                        result = execute_query(
                            "INSERT INTO parks (firm_id, name) VALUES (%s, %s)",
                            (firm_options[selected_firm], park_name),
                            fetch=False
                        )
                        if result:
                            st.success("Парк добавлен!")
                            st.rerun()
                    else:
                        st.error("Название парка обязательно")
        else:
            st.warning("Сначала добавьте фирму")
    
    with tab3:
        parks = execute_query("""
            SELECT p.park_id, p.name, f.name as firm_name 
            FROM parks p 
            JOIN firm f ON p.firm_id = f.firm_id 
            ORDER BY p.park_id
        """)
        
        if parks:
            park_options = {f"{p['name']} ({p['firm_name']})": p['park_id'] for p in parks}
            selected = st.selectbox("Выберите парк для редактирования", list(park_options.keys()), key="edit_park_select")
            
            if selected:
                park_id = park_options[selected]
                park_data = execute_query("SELECT * FROM parks WHERE park_id = %s", (park_id,))
                
                if park_data:
                    with st.form("edit_park"):
                        new_name = st.text_input("Название", value=park_data[0]['name'], key="edit_park_name")
                        
                        if st.form_submit_button("Обновить"):
                            result = execute_query(
                                "UPDATE parks SET name = %s WHERE park_id = %s",
                                (new_name, park_id),
                                fetch=False
                            )
                            if result:
                                st.success("Парк обновлен!")
                                st.rerun()
        else:
            st.info("Нет парков для редактирования")
    
    with tab4:
        parks = execute_query("""
            SELECT p.park_id, p.name, f.name as firm_name 
            FROM parks p 
            JOIN firm f ON p.firm_id = f.firm_id 
            ORDER BY p.park_id
        """)
        
        if parks:
            park_options = {f"{p['name']} ({p['firm_name']})": p['park_id'] for p in parks}
            selected = st.selectbox("Выберите парк для удаления", list(park_options.keys()), key="delete_park_select")
            
            if selected:
                park_id = park_options[selected]
                
                with st.form("delete_park"):
                    st.warning(f"Вы уверены, что хотите удалить этот парк? Это действие нельзя отменить!")
                    if st.form_submit_button("Удалить", type="primary"):
                        result = execute_query("DELETE FROM parks WHERE park_id = %s", (park_id,), fetch=False)
                        if result:
                            st.success("Парк удален!")
                            st.rerun()
        else:
            st.info("Нет парков для удаления")
    
    with tab5:
        zones = execute_query("""
            SELECT z.zone_id, z.name, p.name as park_name 
            FROM zones z 
            JOIN parks p ON z.park_id = p.park_id 
            ORDER BY z.zone_id
        """)
        
        if zones:
            st.dataframe(zones, use_container_width=True)
        else:
            st.info("Зоны не найдены")
    
    with tab6:
        parks = execute_query("SELECT park_id, name FROM parks ORDER BY park_id")
        if parks:
            park_options = {p['name']: p['park_id'] for p in parks}
            selected_park = st.selectbox("Выберите парк", list(park_options.keys()), key="add_zone_park")
            
            with st.form("add_zone"):
                zone_name = st.text_input("Название зоны *", key="add_zone_name")
                
                if st.form_submit_button("Добавить зону"):
                    if zone_name:
                        result = execute_query(
                            "INSERT INTO zones (park_id, name) VALUES (%s, %s)",
                            (park_options[selected_park], zone_name),
                            fetch=False
                        )
                        if result:
                            st.success("Зона добавлена!")
                            st.rerun()
                    else:
                        st.error("Название зоны обязательно")
        else:
            st.warning("Сначала добавьте парк")
        
        zones = execute_query("""
            SELECT z.zone_id, z.name, p.name as park_name 
            FROM zones z 
            JOIN parks p ON z.park_id = p.park_id 
            ORDER BY z.zone_id
        """)
        
        if zones:
            st.markdown("---")
            st.subheader("Редактирование и удаление зон")
            
            zone_tabs = st.tabs(["Редактировать", "Удалить"])
            
            with zone_tabs[0]:
                zone_options = {f"{z['name']} ({z['park_name']})": z['zone_id'] for z in zones}
                selected = st.selectbox("Выберите зону для редактирования", list(zone_options.keys()), key="edit_zone_select")
                
                if selected:
                    zone_id = zone_options[selected]
                    zone_data = execute_query("SELECT * FROM zones WHERE zone_id = %s", (zone_id,))
                    
                    if zone_data:
                        with st.form("edit_zone"):
                            new_name = st.text_input("Название", value=zone_data[0]['name'], key="edit_zone_name")
                            
                            if st.form_submit_button("Обновить"):
                                result = execute_query(
                                    "UPDATE zones SET name = %s WHERE zone_id = %s",
                                    (new_name, zone_id),
                                    fetch=False
                                )
                                if result:
                                    st.success("Зона обновлена!")
                                    st.rerun()
            
            with zone_tabs[1]:
                zone_options = {f"{z['name']} ({z['park_name']})": z['zone_id'] for z in zones}
                selected = st.selectbox("Выберите зону для удаления", list(zone_options.keys()), key="delete_zone_select")
                
                if selected:
                    zone_id = zone_options[selected]
                    
                    with st.form("delete_zone"):
                        st.warning(f"Вы уверены, что хотите удалить эту зону? Это действие нельзя отменить!")
                        if st.form_submit_button("Удалить", type="primary"):
                            result = execute_query("DELETE FROM zones WHERE zone_id = %s", (zone_id,), fetch=False)
                            if result:
                                st.success("Зона удалена!")
                                st.rerun()

def page_plants():
    st.header("Управление растениями")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Просмотр", "Добавить", "Редактировать", "Удалить"])
    
    with tab1:
        plants = execute_query("SELECT * FROM v_all_plants_info ORDER BY plant_id")
        if plants:
            st.dataframe(plants, use_container_width=True)
        else:
            st.info("Растения не найдены")
    
    with tab2:
        zones = execute_query("""
            SELECT z.zone_id, z.name, p.name as park_name 
            FROM zones z 
            JOIN parks p ON z.park_id = p.park_id 
            ORDER BY z.zone_id
        """)
        
        species = execute_query("SELECT species_id, species_name FROM plant_species ORDER BY species_name")
        
        if not zones:
            st.warning("Сначала добавьте зону")
        elif not species:
            st.warning("Сначала добавьте вид растения")
        else:
            with st.form("add_plant"):
                zone_options = {f"{z['name']} ({z['park_name']})": z['zone_id'] for z in zones}
                selected_zone = st.selectbox("Выберите зону *", list(zone_options.keys()), key="add_plant_zone")
                
                species_options = {s['species_name']: s['species_id'] for s in species}
                selected_species = st.selectbox("Выберите вид растения *", list(species_options.keys()), key="add_plant_species")
                
                local_number = st.text_input("Уникальный номер в зоне *", key="add_plant_number")
                date_planted = st.date_input("Дата высадки", value=date.today(), key="add_plant_date")
                age_months = st.number_input("Возраст при высадке (месяцев) *", min_value=0, value=0, key="add_plant_age")
                
                if st.form_submit_button("Добавить растение"):
                    if local_number:
                        result = execute_query(
                            """INSERT INTO plants (local_plant_number, zone_id, species_id, date_planted, age_at_planting_months) 
                               VALUES (%s, %s, %s, %s, %s)""",
                            (local_number, zone_options[selected_zone], species_options[selected_species], 
                             date_planted, age_months),
                            fetch=False
                        )
                        if result:
                            st.success("Растение добавлено!")
                            st.rerun()
                    else:
                        st.error("Уникальный номер обязателен")
    
    with tab3:
        plants = execute_query("SELECT plant_id, local_plant_number, species_name FROM v_all_plants_info ORDER BY plant_id")
        if plants:
            plant_options = {f"{p['local_plant_number']} ({p['species_name']})": p['plant_id'] for p in plants}
            selected = st.selectbox("Выберите растение", list(plant_options.keys()), key="edit_plant_select")
            
            if selected:
                plant_id = plant_options[selected]
                plant_data = execute_query("SELECT * FROM plants WHERE plant_id = %s", (plant_id,))
                
                if plant_data:
                    with st.form("edit_plant"):
                        zones = execute_query("SELECT zone_id, name FROM zones ORDER BY zone_id")
                        zone_options = {z['name']: z['zone_id'] for z in zones}
                        current_zone = next((z['zone_id'] for z in zones if z['zone_id'] == plant_data[0]['zone_id']), None)
                        selected_zone = st.selectbox("Зона", list(zone_options.keys()), 
                                                     index=list(zone_options.values()).index(current_zone) if current_zone else 0,
                                                     key="edit_plant_zone")
                        
                        species = execute_query("SELECT species_id, species_name FROM plant_species ORDER BY species_name")
                        species_options = {s['species_name']: s['species_id'] for s in species}
                        current_species = next((s['species_id'] for s in species if s['species_id'] == plant_data[0]['species_id']), None)
                        selected_species = st.selectbox("Вид", list(species_options.keys()),
                                                         index=list(species_options.values()).index(current_species) if current_species else 0,
                                                         key="edit_plant_species")
                        
                        local_number = st.text_input("Номер в зоне", value=plant_data[0]['local_plant_number'], key="edit_plant_number")
                        date_planted = st.date_input("Дата высадки", value=plant_data[0]['date_planted'], key="edit_plant_date")
                        age_months = st.number_input("Возраст при высадке (месяцев)", min_value=0, 
                                                    value=int(plant_data[0]['age_at_planting_months']), key="edit_plant_age")
                        
                        if st.form_submit_button("Обновить"):
                            result = execute_query(
                                """UPDATE plants SET local_plant_number = %s, zone_id = %s, species_id = %s, 
                                   date_planted = %s, age_at_planting_months = %s WHERE plant_id = %s""",
                                (local_number, zone_options[selected_zone], species_options[selected_species],
                                 date_planted, age_months, plant_id),
                                fetch=False
                            )
                            if result:
                                st.success("Растение обновлено!")
                                st.rerun()
        else:
            st.info("Нет растений для редактирования")
    
    with tab4:
        plants = execute_query("SELECT plant_id, local_plant_number, species_name FROM v_all_plants_info ORDER BY plant_id")
        if plants:
            plant_options = {f"{p['local_plant_number']} ({p['species_name']})": p['plant_id'] for p in plants}
            selected = st.selectbox("Выберите растение для удаления", list(plant_options.keys()), key="delete_plant_select")
            
            if selected:
                plant_id = plant_options[selected]
                
                with st.form("delete_plant"):
                    st.warning(f"Вы уверены, что хотите удалить это растение? Это действие нельзя отменить!")
                    if st.form_submit_button("Удалить", type="primary"):
                        result = execute_query("DELETE FROM plants WHERE plant_id = %s", (plant_id,), fetch=False)
                        if result:
                            st.success("Растение удалено!")
                            st.rerun()
        else:
            st.info("Нет растений для удаления")

def page_employees():
    st.header("Управление персоналом")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Служители", "Добавить служителя", "Редактировать служителя", "Удалить служителя", "Декораторы", "Добавить декоратора"])
    
    with tab1:
        caretakers = execute_query("""
            SELECT employee_id, full_name, phone, address 
            FROM employees 
            WHERE employee_type = 'служитель' 
            ORDER BY employee_id
        """)
        
        if caretakers:
            st.dataframe(caretakers, use_container_width=True)
        else:
            st.info("Служители не найдены")
    
    with tab2:
        with st.form("add_caretaker"):
            full_name = st.text_input("ФИО *", key="add_caretaker_name")
            phone = st.text_input("Телефон", key="add_caretaker_phone")
            address = st.text_area("Адрес", key="add_caretaker_address")
            
            if st.form_submit_button("Добавить служителя"):
                if full_name:
                    result = execute_query(
                        "INSERT INTO employees (full_name, phone, address, employee_type) VALUES (%s, %s, %s, 'служитель')",
                        (full_name, phone or None, address or None),
                        fetch=False
                    )
                    if result:
                        st.success("Служитель добавлен!")
                        st.rerun()
                else:
                    st.error("ФИО обязательно")
    
    with tab3:
        caretakers = execute_query("""
            SELECT employee_id, full_name, phone, address 
            FROM employees 
            WHERE employee_type = 'служитель' 
            ORDER BY employee_id
        """)
        
        if caretakers:
            caretaker_options = {f"{c['full_name']}": c['employee_id'] for c in caretakers}
            selected = st.selectbox("Выберите служителя", list(caretaker_options.keys()), key="edit_caretaker_select")
            
            if selected:
                emp_id = caretaker_options[selected]
                emp_data = execute_query("SELECT * FROM employees WHERE employee_id = %s", (emp_id,))
                
                if emp_data:
                    with st.form("edit_caretaker"):
                        full_name = st.text_input("ФИО", value=emp_data[0]['full_name'], key="edit_caretaker_name")
                        phone = st.text_input("Телефон", value=emp_data[0]['phone'] or "", key="edit_caretaker_phone")
                        address = st.text_area("Адрес", value=emp_data[0]['address'] or "", key="edit_caretaker_address")
                        
                        if st.form_submit_button("Обновить"):
                            result = execute_query(
                                "UPDATE employees SET full_name = %s, phone = %s, address = %s WHERE employee_id = %s",
                                (full_name, phone or None, address or None, emp_id),
                                fetch=False
                            )
                            if result:
                                st.success("Служитель обновлен!")
                                st.rerun()
        else:
            st.info("Нет служителей для редактирования")
    
    with tab4:
        caretakers = execute_query("""
            SELECT employee_id, full_name 
            FROM employees 
            WHERE employee_type = 'служитель' 
            ORDER BY employee_id
        """)
        
        if caretakers:
            caretaker_options = {f"{c['full_name']}": c['employee_id'] for c in caretakers}
            selected = st.selectbox("Выберите служителя для удаления", list(caretaker_options.keys()), key="delete_caretaker_select")
            
            if selected:
                emp_id = caretaker_options[selected]
                
                with st.form("delete_caretaker"):
                    st.warning(f"Вы уверены, что хотите удалить этого служителя? Это действие нельзя отменить!")
                    if st.form_submit_button("Удалить", type="primary"):
                        result = execute_query("DELETE FROM employees WHERE employee_id = %s", (emp_id,), fetch=False)
                        if result:
                            st.success("Служитель удален!")
                            st.rerun()
        else:
            st.info("Нет служителей для удаления")
    
    with tab5:
        decorators = execute_query("""
            SELECT employee_id, full_name, phone, address, education, university, category 
            FROM employees 
            WHERE employee_type = 'декоратор' 
            ORDER BY employee_id
        """)
        
        if decorators:
            st.dataframe(decorators, use_container_width=True)
        else:
            st.info("Декораторы не найдены")
    
    with tab6:
        with st.form("add_decorator"):
            full_name = st.text_input("ФИО *", key="add_decorator_name")
            phone = st.text_input("Телефон", key="add_decorator_phone")
            address = st.text_area("Адрес", key="add_decorator_address")
            education = st.text_input("Образование", key="add_decorator_education")
            university = st.text_input("Учебное заведение", key="add_decorator_university")
            category = st.selectbox("Категория", ["высшая", "первая", "средняя", "без категории"], key="add_decorator_category")
            
            if st.form_submit_button("Добавить декоратора"):
                if full_name:
                    result = execute_query(
                        """INSERT INTO employees (full_name, phone, address, employee_type, education, university, category) 
                           VALUES (%s, %s, %s, 'декоратор', %s, %s, %s)""",
                        (full_name, phone or None, address or None, education or None, university or None, category),
                        fetch=False
                    )
                    if result:
                        st.success("Декоратор добавлен!")
                        st.rerun()
                else:
                    st.error("ФИО обязательно")
        
        decorators = execute_query("""
            SELECT employee_id, full_name, phone, address, education, university, category 
            FROM employees 
            WHERE employee_type = 'декоратор' 
            ORDER BY employee_id
        """)
        
        if decorators:
            st.markdown("---")
            st.subheader("Редактирование и удаление декораторов")
            
            decorator_tabs = st.tabs(["Редактировать", "Удалить"])
            
            with decorator_tabs[0]:
                decorator_options = {f"{d['full_name']}": d['employee_id'] for d in decorators}
                selected = st.selectbox("Выберите декоратора", list(decorator_options.keys()), key="edit_decorator_select")
                
                if selected:
                    emp_id = decorator_options[selected]
                    emp_data = execute_query("SELECT * FROM employees WHERE employee_id = %s", (emp_id,))
                    
                    if emp_data:
                        with st.form("edit_decorator"):
                            full_name = st.text_input("ФИО", value=emp_data[0]['full_name'], key="edit_decorator_name")
                            phone = st.text_input("Телефон", value=emp_data[0]['phone'] or "", key="edit_decorator_phone")
                            address = st.text_area("Адрес", value=emp_data[0]['address'] or "", key="edit_decorator_address")
                            education = st.text_input("Образование", value=emp_data[0]['education'] or "", key="edit_decorator_education")
                            university = st.text_input("Учебное заведение", value=emp_data[0]['university'] or "", key="edit_decorator_university")
                            category = st.selectbox("Категория", ["высшая", "первая", "средняя", "без категории"],
                                                   index=["высшая", "первая", "средняя", "без категории"].index(emp_data[0]['category']) 
                                                   if emp_data[0]['category'] else 3, key="edit_decorator_category")
                            
                            if st.form_submit_button("Обновить"):
                                result = execute_query(
                                    """UPDATE employees SET full_name = %s, phone = %s, address = %s, 
                                       education = %s, university = %s, category = %s WHERE employee_id = %s""",
                                    (full_name, phone or None, address or None, education or None, 
                                     university or None, category, emp_id),
                                    fetch=False
                                )
                                if result:
                                    st.success("Декоратор обновлен!")
                                    st.rerun()
            
            with decorator_tabs[1]:
                decorator_options = {f"{d['full_name']}": d['employee_id'] for d in decorators}
                selected = st.selectbox("Выберите декоратора для удаления", list(decorator_options.keys()), key="delete_decorator_select")
                
                if selected:
                    emp_id = decorator_options[selected]
                    
                    with st.form("delete_decorator"):
                        st.warning(f"Вы уверены, что хотите удалить этого декоратора? Это действие нельзя отменить!")
                        if st.form_submit_button("Удалить", type="primary"):
                            result = execute_query("DELETE FROM employees WHERE employee_id = %s", (emp_id,), fetch=False)
                            if result:
                                st.success("Декоратор удален!")
                                st.rerun()

def page_schedule():
    st.header("График работ")
    
    tab1, tab2 = st.tabs(["Добавить назначение", "Просмотр графика"])
    
    with tab1:
        plants = execute_query("SELECT plant_id, local_plant_number, species_name FROM v_all_plants_info ORDER BY plant_id")
        caretakers = execute_query("""
            SELECT employee_id, full_name 
            FROM employees 
            WHERE employee_type = 'служитель' 
            ORDER BY full_name
        """)
        
        if not plants:
            st.warning("Сначала добавьте растение")
        elif not caretakers:
            st.warning("Сначала добавьте служителя")
        else:
            with st.form("add_schedule"):
                plant_options = {f"{p['local_plant_number']} ({p['species_name']})": p['plant_id'] for p in plants}
                selected_plant = st.selectbox("Выберите растение *", list(plant_options.keys()), key="add_schedule_plant")
                
                caretaker_options = {c['full_name']: c['employee_id'] for c in caretakers}
                selected_caretaker = st.selectbox("Выберите служителя *", list(caretaker_options.keys()), key="add_schedule_caretaker")
                
                assignment_date = st.date_input("Дата назначения *", value=date.today(), key="add_schedule_date")
                
                if st.form_submit_button("Добавить в график"):
                    result = execute_query(
                        "INSERT INTO schedule (plant_id, employee_id, assignment_date) VALUES (%s, %s, %s)",
                        (plant_options[selected_plant], caretaker_options[selected_caretaker], assignment_date),
                        fetch=False
                    )
                    if result:
                        st.success("Назначение добавлено в график!")
                        st.rerun()
    
    with tab2:
        st.subheader("Просмотр графика")
        
        view_date = st.date_input("Выберите дату для просмотра", value=date.today(), key="view_schedule_date")
        
        schedule = execute_query("""
            SELECT * FROM v_employee_schedule 
            WHERE assignment_date = %s 
            ORDER BY assignment_date, full_name
        """, (view_date,))
        
        if schedule:
            st.dataframe(schedule, use_container_width=True)
        else:
            st.info(f"На {view_date} нет назначений")

def page_reports():
    st.header("Отчеты")
    
    tab1, tab2, tab3 = st.tabs([
        "Насаждения по виду",
        "Сотрудники на дату",
        "Растения и режимы полива"
    ])
    
    with tab1:
        st.subheader("Просмотр полной информации по насаждениям заданного вида")
        
        species = execute_query("SELECT species_name FROM plant_species ORDER BY species_name")
        if species:
            species_options = [s['species_name'] for s in species]
            selected_species = st.selectbox("Выберите вид растения", species_options, key="report_species_select")
            
            if st.button("Показать", key="report_species_btn"):
                plants = execute_query(
                    "SELECT * FROM v_all_plants_info WHERE species_name = %s ORDER BY plant_id",
                    (selected_species,)
                )
                
                if plants:
                    st.dataframe(plants, use_container_width=True)
                else:
                    st.info(f"Растения вида '{selected_species}' не найдены")
        else:
            st.info("Сначала добавьте виды растений")
    
    with tab2:
        st.subheader("Просмотр списка сотрудников, работающих на заданную дату")
        
        report_date = st.date_input("Выберите дату", value=date.today(), key="report_date_select")
        
        if st.button("Показать", key="report_date_btn"):
            employees = execute_query(
                "SELECT full_name, phone, address FROM v_employee_schedule WHERE assignment_date = %s ORDER BY full_name",
                (report_date,)
            )
            
            if employees:
                st.dataframe(employees, use_container_width=True)
            else:
                st.info(f"На {report_date} нет работающих сотрудников")
    
    with tab3:
        st.subheader("Просмотр перечня всех растений заданного вида и режимы их полива")
        
        species = execute_query("SELECT species_name FROM plant_species ORDER BY species_name")
        if species:
            species_options = [s['species_name'] for s in species]
            selected_species = st.selectbox("Выберите вид растения", species_options, key="report_regime_select")
            
            if st.button("Показать", key="report_regime_btn"):
                plants = execute_query(
                    "SELECT * FROM v_plant_current_regimes WHERE species_name = %s ORDER BY plant_id",
                    (selected_species,)
                )
                
                if plants:
                    st.dataframe(plants, use_container_width=True)
                else:
                    st.info(f"Растения вида '{selected_species}' не найдены или для них нет режима полива")
        else:
            st.info("Сначала добавьте виды растений")

def page_species():
    st.header("Управление видами растений")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Просмотр", "Добавить", "Редактировать", "Удалить"])
    
    with tab1:
        species = execute_query("SELECT * FROM plant_species ORDER BY species_name")
        if species:
            st.dataframe(species, use_container_width=True)
        else:
            st.info("Виды растений не найдены")
    
    with tab2:
        with st.form("add_species"):
            species_name = st.text_input("Название вида *", key="add_species_name")
            
            if st.form_submit_button("Добавить"):
                if species_name:
                    result = execute_query(
                        "INSERT INTO plant_species (species_name) VALUES (%s)",
                        (species_name,),
                        fetch=False
                    )
                    if result:
                        st.success("Вид добавлен!")
                        st.rerun()
                else:
                    st.error("Название вида обязательно")
    
    with tab3:
        species = execute_query("SELECT * FROM plant_species ORDER BY species_name")
        if species:
            species_options = {f"{s['species_name']}": s['species_id'] for s in species}
            selected = st.selectbox("Выберите вид для редактирования", list(species_options.keys()), key="edit_species_select")
            
            if selected:
                species_id = species_options[selected]
                species_data = execute_query("SELECT * FROM plant_species WHERE species_id = %s", (species_id,))
                
                if species_data:
                    with st.form("edit_species"):
                        new_name = st.text_input("Название вида", value=species_data[0]['species_name'], key="edit_species_name")
                        
                        if st.form_submit_button("Обновить"):
                            result = execute_query(
                                "UPDATE plant_species SET species_name = %s WHERE species_id = %s",
                                (new_name, species_id),
                                fetch=False
                            )
                            if result:
                                st.success("Вид обновлен!")
                                st.rerun()
        else:
            st.info("Нет видов для редактирования")
    
    with tab4:
        species = execute_query("SELECT * FROM plant_species ORDER BY species_name")
        if species:
            species_options = {f"{s['species_name']}": s['species_id'] for s in species}
            selected = st.selectbox("Выберите вид для удаления", list(species_options.keys()), key="delete_species_select")
            
            if selected:
                species_id = species_options[selected]
                
                with st.form("delete_species"):
                    st.warning(f"Вы уверены, что хотите удалить этот вид? Это действие нельзя отменить!")
                    if st.form_submit_button("Удалить", type="primary"):
                        result = execute_query(
                            "DELETE FROM plant_species WHERE species_id = %s",
                            (species_id,),
                            fetch=False
                        )
                        if result:
                            st.success("Вид удален!")
                            st.rerun()
        else:
            st.info("Нет видов для удаления")

def page_reference():
    st.header("Справочники")
    
    st.subheader("Режимы полива")
    
    species = execute_query("SELECT species_id, species_name FROM plant_species ORDER BY species_name")
    
    if not species:
        st.warning("Сначала добавьте вид растения")
    else:
        with st.expander("Добавить режим полива"):
            species_options = {s['species_name']: s['species_id'] for s in species}
            selected_species = st.selectbox("Выберите вид", list(species_options.keys()), key="add_regime_species")
            
            with st.form("add_regime"):
                min_age = st.number_input("Минимальный возраст (месяцев) *", min_value=0, value=0, key="add_regime_min_age")
                max_age = st.number_input("Максимальный возраст (месяцев)", min_value=0, value=None, key="add_regime_max_age")
                periodicity = st.selectbox("Периодичность *", ["ежедневно", "раз в неделю", "раз в 2 недели", "раз в месяц"], key="add_regime_periodicity")
                time_of_day = st.time_input("Время полива", value=None, key="add_regime_time")
                water_liters = st.number_input("Норма воды (литры) *", min_value=0.01, value=1.0, step=0.1, key="add_regime_liters")
                
                if st.form_submit_button("Добавить режим"):
                    result = execute_query(
                        """INSERT INTO watering_regimes (species_id, min_age_months, max_age_months, 
                           periodicity, time_of_day, water_liters) VALUES (%s, %s, %s, %s, %s, %s)""",
                        (species_options[selected_species], min_age, max_age if max_age else None, 
                         periodicity, time_of_day, water_liters),
                        fetch=False
                    )
                    if result:
                        st.success("Режим полива добавлен!")
                        st.rerun()
    
    regimes = execute_query("""
        SELECT wr.regime_id, ps.species_name, wr.min_age_months, wr.max_age_months, 
               wr.periodicity, wr.time_of_day, wr.water_liters
        FROM watering_regimes wr
        JOIN plant_species ps ON wr.species_id = ps.species_id
        ORDER BY ps.species_name, wr.min_age_months
    """)
    
    if regimes:
        st.dataframe(regimes, use_container_width=True)
    else:
        st.info("Режимы полива не найдены")

def page_main():
    st.title("Банк данных насаждений парков")
    st.markdown("---")
    
    st.subheader("Функциональность системы:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Управление данными:**
        - Фирма
        - Парки и зоны
        - Растения
        - Виды растений
        - Персонал (служители и декораторы)
        - График работ
        """)
    
    with col2:
        st.markdown("""
        **Отчеты:**
        - Насаждения по виду
        - Сотрудники на дату
        - Растения и режимы полива
        """)
    
    st.markdown("---")
    
    st.subheader("Статистика")
    
    col1, col2, col3, col4 = st.columns(4)
    
    firms_count = execute_query("SELECT COUNT(*) as count FROM firm")
    parks_count = execute_query("SELECT COUNT(*) as count FROM parks")
    plants_count = execute_query("SELECT COUNT(*) as count FROM plants")
    employees_count = execute_query("SELECT COUNT(*) as count FROM employees")
    
    with col1:
        st.metric("Фирм", firms_count[0]['count'] if firms_count else 0)
    with col2:
        st.metric("Парков", parks_count[0]['count'] if parks_count else 0)
    with col3:
        st.metric("Растений", plants_count[0]['count'] if plants_count else 0)
    with col4:
        st.metric("Сотрудников", employees_count[0]['count'] if employees_count else 0)

def main():
    st.set_page_config(
        page_title="Банк данных насаждений парков",
        layout="wide"
    )
    
    init_session_state()
    
    with st.sidebar:
        st.title("Меню")
        
        page = st.radio(
            "Выберите раздел:",
            ["Главная", "Фирма", "Парки и зоны", "Растения", "Виды растений", "Персонал", "График работ", "Отчеты", "Справочники"]
        )
    
    if page == "Главная":
        page_main()
    elif page == "Фирма":
        page_firm()
    elif page == "Парки и зоны":
        page_parks_zones()
    elif page == "Растения":
        page_plants()
    elif page == "Виды растений":
        page_species()
    elif page == "Персонал":
        page_employees()
    elif page == "График работ":
        page_schedule()
    elif page == "Отчеты":
        page_reports()
    elif page == "Справочники":
        page_reference()

if __name__ == "__main__":
    main()
