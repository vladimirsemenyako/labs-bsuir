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

def call_procedure(procedure_name, params=None, has_out_param=False, show_error=True):
    """Вызов хранимой процедуры или функции PostgreSQL
    
    Args:
        procedure_name: имя процедуры или функции
        params: список параметров
        has_out_param: если True, функция возвращает значение (используется SELECT)
        show_error: показывать ли ошибки пользователю
    """
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if has_out_param:
                # Для функций используем SELECT
                if params:
                    placeholders = ', '.join(['%s'] * len(params))
                    query = f"SELECT {procedure_name}({placeholders}) as result"
                    cur.execute(query, params)
                else:
                    query = f"SELECT {procedure_name}() as result"
                    cur.execute(query)
                result_row = cur.fetchone()
                result = result_row['result'] if result_row else None
            else:
                # Для обычных процедур используем CALL
                if params:
                    placeholders = ', '.join(['%s'] * len(params))
                    query = f"CALL {procedure_name}({placeholders})"
                    cur.execute(query, params)
                else:
                    query = f"CALL {procedure_name}()"
                    cur.execute(query)
                result = True
            
            conn.commit()
            return result
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
            st.error(f"Ошибка выполнения процедуры: {e}")
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
        firms = execute_query("SELECT * FROM fn_get_all_firms()")
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
                    result = call_procedure(
                        "sp_add_firm",
                        (name, legal_address or None),
                        has_out_param=True
                    )
                    if result:
                        st.success(f"Фирма '{name}' успешно добавлена!" + (f" ID: {result}" if result else ""))
                        st.rerun()
                else:
                    st.error("Название фирмы обязательно")
    
    with tab3:
        firms = execute_query("SELECT * FROM fn_get_firms_list()")
        if firms:
            firm_options = {f"{f['name']} (ID: {f['firm_id']})": f['firm_id'] for f in firms}
            selected = st.selectbox("Выберите фирму", list(firm_options.keys()), key="edit_firm_select")
            
            if selected:
                firm_id = firm_options[selected]
                firm_data = execute_query("SELECT * FROM fn_get_firm_by_id(%s)", (firm_id,))
                
                if firm_data:
                    with st.form("edit_firm"):
                        name = st.text_input("Название", value=firm_data[0]['name'], key="edit_firm_name")
                        legal_address = st.text_area("Юридический адрес", value=firm_data[0]['legal_address'] or "", key="edit_firm_address")
                        
                        if st.form_submit_button("Обновить"):
                            result = call_procedure(
                                "sp_update_firm",
                                (firm_id, name, legal_address or None),
                                has_out_param=False
                            )
                            if result:
                                st.success("Фирма обновлена!")
                                st.rerun()
        else:
            st.info("Нет фирм для редактирования")
    
    with tab4:
        firms = execute_query("SELECT * FROM fn_get_firms_list()")
        if firms:
            firm_options = {f"{f['name']} (ID: {f['firm_id']})": f['firm_id'] for f in firms}
            selected = st.selectbox("Выберите фирму для удаления", list(firm_options.keys()), key="delete_firm_select")
            
            if selected:
                firm_id = firm_options[selected]
                
                with st.form("delete_firm"):
                    st.warning(f"Вы уверены, что хотите удалить эту фирму? Это действие нельзя отменить!")
                    if st.form_submit_button("Удалить", type="primary"):
                        result = call_procedure("sp_delete_firm", (firm_id,), has_out_param=False)
                        if result:
                            st.success("Фирма удалена!")
                            st.rerun()
        else:
            st.info("Нет фирм для удаления")

def page_parks_zones():
    st.header("Управление парками и зонами")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Парки", "Добавить парк", "Редактировать парк", "Удалить парк", "Зоны", "Добавить зону"])
    
    with tab1:
        parks = execute_query("SELECT * FROM fn_get_all_parks()")
        
        if parks:
            st.dataframe(parks, use_container_width=True)
        else:
            st.info("Парки не найдены")
    
    with tab2:
        firms = execute_query("SELECT * FROM fn_get_firms_list()")
        if firms:
            firm_options = {f['name']: f['firm_id'] for f in firms}
            selected_firm = st.selectbox("Выберите фирму", list(firm_options.keys()), key="add_park_firm")
            
            with st.form("add_park"):
                park_name = st.text_input("Название парка *", key="add_park_name")
                
                if st.form_submit_button("Добавить парк"):
                    if park_name:
                        result = call_procedure(
                            "sp_add_park",
                            (firm_options[selected_firm], park_name),
                            has_out_param=True
                        )
                        if result:
                            st.success("Парк добавлен!")
                            st.rerun()
                    else:
                        st.error("Название парка обязательно")
        else:
            st.warning("Сначала добавьте фирму")
    
    with tab3:
        parks = execute_query("SELECT * FROM fn_get_all_parks()")
        
        if parks:
            park_options = {f"{p['name']} ({p['firm_name']})": p['park_id'] for p in parks}
            selected = st.selectbox("Выберите парк для редактирования", list(park_options.keys()), key="edit_park_select")
            
            if selected:
                park_id = park_options[selected]
                park_data = execute_query("SELECT * FROM fn_get_park_by_id(%s)", (park_id,))
                
                if park_data:
                    with st.form("edit_park"):
                        new_name = st.text_input("Название", value=park_data[0]['name'], key="edit_park_name")
                        
                        if st.form_submit_button("Обновить"):
                            result = call_procedure(
                                "sp_update_park",
                                (park_id, new_name),
                                has_out_param=False
                            )
                            if result:
                                st.success("Парк обновлен!")
                                st.rerun()
        else:
            st.info("Нет парков для редактирования")
    
    with tab4:
        parks = execute_query("SELECT * FROM fn_get_all_parks()")
        
        if parks:
            park_options = {f"{p['name']} ({p['firm_name']})": p['park_id'] for p in parks}
            selected = st.selectbox("Выберите парк для удаления", list(park_options.keys()), key="delete_park_select")
            
            if selected:
                park_id = park_options[selected]
                
                with st.form("delete_park"):
                    st.warning(f"Вы уверены, что хотите удалить этот парк? Это действие нельзя отменить!")
                    if st.form_submit_button("Удалить", type="primary"):
                        result = call_procedure("sp_delete_park", (park_id,), has_out_param=False)
                        if result:
                            st.success("Парк удален!")
                            st.rerun()
        else:
            st.info("Нет парков для удаления")
    
    with tab5:
        zones = execute_query("SELECT * FROM fn_get_all_zones()")
        
        if zones:
            st.dataframe(zones, use_container_width=True)
        else:
            st.info("Зоны не найдены")
    
    with tab6:
        parks = execute_query("SELECT * FROM fn_get_parks_list()")
        if parks:
            park_options = {p['name']: p['park_id'] for p in parks}
            selected_park = st.selectbox("Выберите парк", list(park_options.keys()), key="add_zone_park")
            
            with st.form("add_zone"):
                zone_name = st.text_input("Название зоны *", key="add_zone_name")
                
                if st.form_submit_button("Добавить зону"):
                    if zone_name:
                        result = call_procedure(
                            "sp_add_zone",
                            (park_options[selected_park], zone_name),
                            has_out_param=True
                        )
                        if result:
                            st.success("Зона добавлена!")
                            st.rerun()
                    else:
                        st.error("Название зоны обязательно")
        else:
            st.warning("Сначала добавьте парк")
        
        zones = execute_query("SELECT * FROM fn_get_all_zones()")
        
        if zones:
            st.markdown("---")
            st.subheader("Редактирование и удаление зон")
            
            zone_tabs = st.tabs(["Редактировать", "Удалить"])
            
            with zone_tabs[0]:
                zone_options = {f"{z['name']} ({z['park_name']})": z['zone_id'] for z in zones}
                selected = st.selectbox("Выберите зону для редактирования", list(zone_options.keys()), key="edit_zone_select")
                
                if selected:
                    zone_id = zone_options[selected]
                    zone_data = execute_query("SELECT * FROM fn_get_zone_by_id(%s)", (zone_id,))
                    
                    if zone_data:
                        with st.form("edit_zone"):
                            new_name = st.text_input("Название", value=zone_data[0]['name'], key="edit_zone_name")
                            
                            if st.form_submit_button("Обновить"):
                                result = call_procedure(
                                    "sp_update_zone",
                                    (zone_id, new_name),
                                    has_out_param=False
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
                            result = call_procedure("sp_delete_zone", (zone_id,), has_out_param=False)
                            if result:
                                st.success("Зона удалена!")
                                st.rerun()

def page_plants():
    st.header("Управление растениями")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Просмотр", "Добавить", "Редактировать", "Удалить"])
    
    with tab1:
        plants = execute_query("SELECT * FROM fn_get_all_plants()")
        if plants:
            st.dataframe(plants, use_container_width=True)
        else:
            st.info("Растения не найдены")
    
    with tab2:
        zones = execute_query("SELECT * FROM fn_get_zones_list()")
        species = execute_query("SELECT * FROM fn_get_species_list()")
        
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
                        result = call_procedure(
                            "sp_add_plant",
                            (local_number, zone_options[selected_zone], species_options[selected_species], 
                             date_planted, age_months),
                            has_out_param=True
                        )
                        if result:
                            st.success("Растение добавлено!")
                            st.rerun()
                    else:
                        st.error("Уникальный номер обязателен")
    
    with tab3:
        plants = execute_query("SELECT * FROM fn_get_plants_list()")
        if plants:
            plant_options = {f"{p['local_plant_number']} ({p['species_name']})": p['plant_id'] for p in plants}
            selected = st.selectbox("Выберите растение", list(plant_options.keys()), key="edit_plant_select")
            
            if selected:
                plant_id = plant_options[selected]
                plant_data = execute_query("SELECT * FROM fn_get_plant_by_id(%s)", (plant_id,))
                
                if plant_data:
                    with st.form("edit_plant"):
                        zones = execute_query("SELECT * FROM fn_get_zones_list()")
                        zone_options = {f"{z['name']} ({z['park_name']})": z['zone_id'] for z in zones}
                        current_zone = plant_data[0]['zone_id']
                        selected_zone = st.selectbox("Зона", list(zone_options.keys()), 
                                                     index=list(zone_options.values()).index(current_zone) if current_zone in zone_options.values() else 0,
                                                     key="edit_plant_zone")
                        
                        species = execute_query("SELECT * FROM fn_get_species_list()")
                        species_options = {s['species_name']: s['species_id'] for s in species}
                        current_species = plant_data[0]['species_id']
                        selected_species = st.selectbox("Вид", list(species_options.keys()),
                                                         index=list(species_options.values()).index(current_species) if current_species in species_options.values() else 0,
                                                         key="edit_plant_species")
                        
                        local_number = st.text_input("Номер в зоне", value=plant_data[0]['local_plant_number'], key="edit_plant_number")
                        date_planted = st.date_input("Дата высадки", value=plant_data[0]['date_planted'], key="edit_plant_date")
                        age_months = st.number_input("Возраст при высадке (месяцев)", min_value=0, 
                                                    value=int(plant_data[0]['age_at_planting_months']), key="edit_plant_age")
                        
                        if st.form_submit_button("Обновить"):
                            result = call_procedure(
                                "sp_update_plant",
                                (plant_id, local_number, zone_options[selected_zone], species_options[selected_species],
                                 date_planted, age_months),
                                has_out_param=False
                            )
                            if result:
                                st.success("Растение обновлено!")
                                st.rerun()
        else:
            st.info("Нет растений для редактирования")
    
    with tab4:
        plants = execute_query("SELECT * FROM fn_get_plants_list()")
        if plants:
            plant_options = {f"{p['local_plant_number']} ({p['species_name']})": p['plant_id'] for p in plants}
            selected = st.selectbox("Выберите растение для удаления", list(plant_options.keys()), key="delete_plant_select")
            
            if selected:
                plant_id = plant_options[selected]
                
                with st.form("delete_plant"):
                    st.warning(f"Вы уверены, что хотите удалить это растение? Это действие нельзя отменить!")
                    if st.form_submit_button("Удалить", type="primary"):
                        result = call_procedure("sp_delete_plant", (plant_id,), has_out_param=False)
                        if result:
                            st.success("Растение удалено!")
                            st.rerun()
        else:
            st.info("Нет растений для удаления")

def page_employees():
    st.header("Управление персоналом")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Служители", "Добавить служителя", "Редактировать служителя", "Удалить служителя", "Декораторы", "Добавить декоратора"])
    
    with tab1:
        caretakers = execute_query("SELECT * FROM fn_get_all_caretakers()")
        
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
                    result = call_procedure(
                        "sp_add_caretaker",
                        (full_name, phone or None, address or None),
                        has_out_param=True
                    )
                    if result:
                        st.success("Служитель добавлен!")
                        st.rerun()
                else:
                    st.error("ФИО обязательно")
    
    with tab3:
        caretakers = execute_query("SELECT * FROM fn_get_all_caretakers()")
        
        if caretakers:
            caretaker_options = {f"{c['full_name']}": c['employee_id'] for c in caretakers}
            selected = st.selectbox("Выберите служителя", list(caretaker_options.keys()), key="edit_caretaker_select")
            
            if selected:
                emp_id = caretaker_options[selected]
                emp_data = execute_query("SELECT * FROM fn_get_employee_by_id(%s)", (emp_id,))
                
                if emp_data:
                    with st.form("edit_caretaker"):
                        full_name = st.text_input("ФИО", value=emp_data[0]['full_name'], key="edit_caretaker_name")
                        phone = st.text_input("Телефон", value=emp_data[0]['phone'] or "", key="edit_caretaker_phone")
                        address = st.text_area("Адрес", value=emp_data[0]['address'] or "", key="edit_caretaker_address")
                        
                        if st.form_submit_button("Обновить"):
                            result = call_procedure(
                                "sp_update_caretaker",
                                (emp_id, full_name, phone or None, address or None),
                                has_out_param=False
                            )
                            if result:
                                st.success("Служитель обновлен!")
                                st.rerun()
        else:
            st.info("Нет служителей для редактирования")
    
    with tab4:
        caretakers = execute_query("SELECT * FROM fn_get_all_caretakers()")
        
        if caretakers:
            caretaker_options = {f"{c['full_name']}": c['employee_id'] for c in caretakers}
            selected = st.selectbox("Выберите служителя для удаления", list(caretaker_options.keys()), key="delete_caretaker_select")
            
            if selected:
                emp_id = caretaker_options[selected]
                
                with st.form("delete_caretaker"):
                    st.warning(f"Вы уверены, что хотите удалить этого служителя? Это действие нельзя отменить!")
                    if st.form_submit_button("Удалить", type="primary"):
                        result = call_procedure("sp_delete_employee", (emp_id,), has_out_param=False)
                        if result:
                            st.success("Служитель удален!")
                            st.rerun()
        else:
            st.info("Нет служителей для удаления")
    
    with tab5:
        decorators = execute_query("SELECT * FROM fn_get_all_decorators()")
        
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
                    result = call_procedure(
                        "sp_add_decorator",
                        (full_name, phone or None, address or None, education or None, university or None, category),
                        has_out_param=True
                    )
                    if result:
                        st.success("Декоратор добавлен!")
                        st.rerun()
                else:
                    st.error("ФИО обязательно")
        
        decorators = execute_query("SELECT * FROM fn_get_all_decorators()")
        
        if decorators:
            st.markdown("---")
            st.subheader("Редактирование и удаление декораторов")
            
            decorator_tabs = st.tabs(["Редактировать", "Удалить"])
            
            with decorator_tabs[0]:
                decorator_options = {f"{d['full_name']}": d['employee_id'] for d in decorators}
                selected = st.selectbox("Выберите декоратора", list(decorator_options.keys()), key="edit_decorator_select")
                
                if selected:
                    emp_id = decorator_options[selected]
                    emp_data = execute_query("SELECT * FROM fn_get_employee_by_id(%s)", (emp_id,))
                    
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
                                result = call_procedure(
                                    "sp_update_decorator",
                                    (emp_id, full_name, phone or None, address or None, education or None, 
                                     university or None, category),
                                    has_out_param=False
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
                            result = call_procedure("sp_delete_employee", (emp_id,), has_out_param=False)
                            if result:
                                st.success("Декоратор удален!")
                                st.rerun()

def page_schedule():
    st.header("График работ")
    
    tab1, tab2 = st.tabs(["Добавить назначение", "Просмотр графика"])
    
    with tab1:
        plants = execute_query("SELECT * FROM fn_get_plants_list()")
        caretakers = execute_query("SELECT * FROM fn_get_caretakers_list()")
        
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
                    result = call_procedure(
                        "sp_add_schedule",
                        (plant_options[selected_plant], caretaker_options[selected_caretaker], assignment_date),
                        has_out_param=True
                    )
                    if result:
                        st.success("Назначение добавлено в график!")
                        st.rerun()
    
    with tab2:
        st.subheader("Просмотр графика")
        
        view_date = st.date_input("Выберите дату для просмотра", value=date.today(), key="view_schedule_date")
        
        schedule = execute_query("SELECT * FROM fn_get_schedule_by_date(%s)", (view_date,))
        
        if schedule:
            st.dataframe(schedule, use_container_width=True)
        else:
            st.info(f"На {view_date} нет назначений")

def page_watering_regimes():
    st.header("Управление режимами полива")
    
    st.info("""
    ℹ️ **Правило системы:** Для одного вида растения с одинаковым возрастом может быть только один режим полива.
    
    Растения разного возраста имеют разные режимы полива.
    """)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Просмотр всех режимов", 
        "Добавить режим", 
        "Редактировать режим", 
        "Удалить режим",
        "Проверка пересечений"
    ])
    
    with tab1:
        st.subheader("Все режимы полива")
        
        regimes = execute_query("SELECT * FROM fn_get_all_watering_regimes()")
        if regimes:
            # Форматируем данные для отображения
            formatted_regimes = []
            for r in regimes:
                formatted_regimes.append({
                    'ID режима': r['regime_id'],
                    'Вид растения': r['species_name'],
                    'Возраст от (мес)': r['min_age_months'],
                    'Возраст до (мес)': r['max_age_months'] if r['max_age_months'] else '∞',
                    'Периодичность': r['periodicity'],
                    'Время': str(r['time_of_day']) if r['time_of_day'] else '-',
                    'Вода (л)': r['water_liters']
                })
            st.dataframe(formatted_regimes, use_container_width=True)
            
            # Группировка по видам
            st.markdown("---")
            st.subheader("Режимы по видам растений")
            
            species_list = execute_query("SELECT * FROM fn_get_species_list()")
            if species_list:
                selected_species = st.selectbox(
                    "Выберите вид для просмотра его режимов",
                    [s['species_name'] for s in species_list],
                    key="view_regimes_species"
                )
                
                species_regimes = [r for r in formatted_regimes if r['Вид растения'] == selected_species]
                if species_regimes:
                    st.dataframe(species_regimes, use_container_width=True)
                    
                    # Визуализация диапазонов
                    st.markdown("**Возрастные диапазоны:**")
                    for regime in species_regimes:
                        max_age = regime['Возраст до (мес)']
                        if max_age == '∞':
                            st.write(f"🌱 {regime['Возраст от (мес)']}+ месяцев → {regime['Периодичность']}, {regime['Вода (л)']} л")
                        else:
                            st.write(f"🌱 {regime['Возраст от (мес)']}-{max_age} месяцев → {regime['Периодичность']}, {regime['Вода (л)']} л")
                else:
                    st.info(f"Для вида '{selected_species}' нет режимов полива")
        else:
            st.info("Режимы полива не найдены")
    
    with tab2:
        st.subheader("Добавить новый режим полива")
        
        with st.form("add_watering_regime"):
            species_list = execute_query("SELECT * FROM fn_get_species_list()")
            
            if species_list:
                species_options = {s['species_name']: s['species_id'] for s in species_list}
                selected_species = st.selectbox("Вид растения *", list(species_options.keys()), key="add_regime_species")
                
                col1, col2 = st.columns(2)
                with col1:
                    min_age = st.number_input("Минимальный возраст (месяцы) *", min_value=0, value=0, key="add_min_age")
                with col2:
                    use_max_age = st.checkbox("Указать максимальный возраст", value=True, key="add_use_max_age")
                    if use_max_age:
                        max_age = st.number_input("Максимальный возраст (месяцы)", min_value=min_age+1, value=min_age+12, key="add_max_age")
                    else:
                        max_age = None
                        st.info("Режим будет применяться для всех растений старше минимального возраста")
                
                periodicity = st.selectbox(
                    "Периодичность полива *",
                    ["ежедневно", "раз в неделю", "раз в 2 недели", "раз в месяц"],
                    key="add_periodicity"
                )
                
                col3, col4 = st.columns(2)
                with col3:
                    time_of_day = st.time_input("Время полива", key="add_time")
                with col4:
                    water_liters = st.number_input("Количество воды (литры) *", min_value=0.1, value=5.0, step=0.5, key="add_water")
                
                st.markdown("---")
                st.markdown("**Предпросмотр:**")
                if max_age:
                    st.write(f"🌱 {selected_species}: {min_age}-{max_age} месяцев → {periodicity}, {water_liters} л, время: {time_of_day}")
                else:
                    st.write(f"🌱 {selected_species}: {min_age}+ месяцев → {periodicity}, {water_liters} л, время: {time_of_day}")
                
                if st.form_submit_button("Добавить режим"):
                    species_id = species_options[selected_species]
                    
                    # Сначала проверяем пересечение
                    overlap_check = execute_query(
                        "SELECT * FROM fn_check_watering_regime_overlap(%s, %s, %s, NULL)",
                        (species_id, min_age, max_age)
                    )
                    
                    if overlap_check and overlap_check[0]['has_overlap']:
                        overlap = overlap_check[0]
                        max_age_str = str(overlap['overlapping_max_age']) if overlap['overlapping_max_age'] else '∞'
                        st.error(f"""
                        ❌ **Невозможно добавить режим!**
                        
                        Возрастной диапазон {min_age}-{max_age if max_age else '∞'} месяцев пересекается 
                        с существующим режимом (ID={overlap['overlapping_regime_id']}, 
                        диапазон {overlap['overlapping_min_age']}-{max_age_str} месяцев).
                        
                        **Правило:** Для растений одного вида с одинаковым возрастом может быть только один режим полива.
                        """)
                    else:
                        # Добавляем режим
                        result = call_procedure(
                            "sp_add_watering_regime",
                            (species_id, min_age, max_age, periodicity, time_of_day, water_liters),
                            has_out_param=True
                        )
                        if result:
                            st.success(f"✅ Режим полива успешно добавлен! (ID={result})")
                            st.rerun()
            else:
                st.warning("Сначала добавьте виды растений")
    
    with tab3:
        st.subheader("Редактировать режим полива")
        
        regimes = execute_query("SELECT * FROM fn_get_all_watering_regimes()")
        if regimes:
            regime_options = {
                f"{r['species_name']} ({r['min_age_months']}-{r['max_age_months'] if r['max_age_months'] else '∞'} мес)": r
                for r in regimes
            }
            
            selected_regime_str = st.selectbox(
                "Выберите режим для редактирования",
                list(regime_options.keys()),
                key="edit_regime_select"
            )
            
            if selected_regime_str:
                regime = regime_options[selected_regime_str]
                
                with st.form("edit_watering_regime"):
                    st.info(f"Редактирование режима ID={regime['regime_id']}")
                    
                    species_list = execute_query("SELECT * FROM fn_get_species_list()")
                    species_options = {s['species_name']: s['species_id'] for s in species_list}
                    
                    selected_species = st.selectbox(
                        "Вид растения *",
                        list(species_options.keys()),
                        index=list(species_options.keys()).index(regime['species_name']),
                        key="edit_regime_species"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        min_age = st.number_input(
                            "Минимальный возраст (месяцы) *",
                            min_value=0,
                            value=regime['min_age_months'],
                            key="edit_min_age"
                        )
                    with col2:
                        use_max_age = st.checkbox(
                            "Указать максимальный возраст",
                            value=regime['max_age_months'] is not None,
                            key="edit_use_max_age"
                        )
                        if use_max_age:
                            max_age = st.number_input(
                                "Максимальный возраст (месяцы)",
                                min_value=min_age+1,
                                value=regime['max_age_months'] if regime['max_age_months'] else min_age+12,
                                key="edit_max_age"
                            )
                        else:
                            max_age = None
                    
                    periodicity = st.selectbox(
                        "Периодичность полива *",
                        ["ежедневно", "раз в неделю", "раз в 2 недели", "раз в месяц"],
                        index=["ежедневно", "раз в неделю", "раз в 2 недели", "раз в месяц"].index(regime['periodicity']),
                        key="edit_periodicity"
                    )
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        time_of_day = st.time_input(
                            "Время полива",
                            value=regime['time_of_day'],
                            key="edit_time"
                        )
                    with col4:
                        water_liters = st.number_input(
                            "Количество воды (литры) *",
                            min_value=0.1,
                            value=float(regime['water_liters']),
                            step=0.5,
                            key="edit_water"
                        )
                    
                    if st.form_submit_button("Сохранить изменения"):
                        species_id = species_options[selected_species]
                        
                        # Проверяем пересечение (исключая текущий режим)
                        overlap_check = execute_query(
                            "SELECT * FROM fn_check_watering_regime_overlap(%s, %s, %s, %s)",
                            (species_id, min_age, max_age, regime['regime_id'])
                        )
                        
                        if overlap_check and overlap_check[0]['has_overlap']:
                            overlap = overlap_check[0]
                            max_age_str = str(overlap['overlapping_max_age']) if overlap['overlapping_max_age'] else '∞'
                            st.error(f"""
                            ❌ **Невозможно обновить режим!**
                            
                            Возрастной диапазон {min_age}-{max_age if max_age else '∞'} месяцев пересекается 
                            с существующим режимом (ID={overlap['overlapping_regime_id']}, 
                            диапазон {overlap['overlapping_min_age']}-{max_age_str} месяцев).
                            """)
                        else:
                            result = call_procedure(
                                "sp_update_watering_regime",
                                (regime['regime_id'], species_id, min_age, max_age, periodicity, time_of_day, water_liters),
                                has_out_param=False
                            )
                            if result:
                                st.success("✅ Режим полива успешно обновлен!")
                                st.rerun()
        else:
            st.info("Режимы полива не найдены")
    
    with tab4:
        st.subheader("Удалить режим полива")
        
        regimes = execute_query("SELECT * FROM fn_get_all_watering_regimes()")
        if regimes:
            regime_options = {
                f"ID={r['regime_id']}: {r['species_name']} ({r['min_age_months']}-{r['max_age_months'] if r['max_age_months'] else '∞'} мес, {r['periodicity']})": r['regime_id']
                for r in regimes
            }
            
            selected_regime = st.selectbox(
                "Выберите режим для удаления",
                list(regime_options.keys()),
                key="delete_regime_select"
            )
            
            if selected_regime:
                regime_id = regime_options[selected_regime]
                
                st.warning(f"⚠️ Вы уверены, что хотите удалить режим {selected_regime}?")
                
                if st.button("Удалить", key="delete_regime_btn", type="primary"):
                    result = call_procedure("sp_delete_watering_regime", (regime_id,), has_out_param=False)
                    if result:
                        st.success("✅ Режим полива успешно удален!")
                        st.rerun()
        else:
            st.info("Режимы полива не найдены")
    
    with tab5:
        st.subheader("Проверка пересечений возрастных диапазонов")
        
        st.info("""
        Используйте эту вкладку для проверки, будет ли новый возрастной диапазон 
        пересекаться с существующими режимами полива для выбранного вида.
        """)
        
        species_list = execute_query("SELECT * FROM fn_get_species_list()")
        
        if species_list:
            species_options = {s['species_name']: s['species_id'] for s in species_list}
            selected_species = st.selectbox(
                "Вид растения",
                list(species_options.keys()),
                key="check_species"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                check_min_age = st.number_input("Минимальный возраст (месяцы)", min_value=0, value=0, key="check_min_age")
            with col2:
                use_check_max = st.checkbox("Указать максимальный возраст", value=True, key="check_use_max")
                if use_check_max:
                    check_max_age = st.number_input("Максимальный возраст (месяцы)", min_value=check_min_age+1, value=check_min_age+12, key="check_max_age")
                else:
                    check_max_age = None
            
            if st.button("Проверить пересечение", key="check_overlap_btn"):
                species_id = species_options[selected_species]
                
                overlap_check = execute_query(
                    "SELECT * FROM fn_check_watering_regime_overlap(%s, %s, %s, NULL)",
                    (species_id, check_min_age, check_max_age)
                )
                
                if overlap_check and overlap_check[0]['has_overlap']:
                    overlap = overlap_check[0]
                    max_age_str = str(overlap['overlapping_max_age']) if overlap['overlapping_max_age'] else '∞'
                    
                    st.error(f"""
                    ❌ **Обнаружено пересечение!**
                    
                    Диапазон {check_min_age}-{check_max_age if check_max_age else '∞'} месяцев 
                    пересекается с существующим режимом:
                    - **ID режима:** {overlap['overlapping_regime_id']}
                    - **Диапазон:** {overlap['overlapping_min_age']}-{max_age_str} месяцев
                    
                    Вы не сможете добавить режим с таким диапазоном.
                    """)
                    
                    # Показываем все существующие режимы для этого вида
                    st.markdown("**Существующие режимы для этого вида:**")
                    existing_regimes = execute_query(
                        "SELECT * FROM fn_get_all_watering_regimes() WHERE species_id = %s",
                        (species_id,)
                    )
                    if existing_regimes:
                        for r in existing_regimes:
                            max_age_display = r['max_age_months'] if r['max_age_months'] else '∞'
                            st.write(f"- ID={r['regime_id']}: {r['min_age_months']}-{max_age_display} месяцев")
                else:
                    st.success(f"""
                    ✅ **Пересечений не обнаружено!**
                    
                    Диапазон {check_min_age}-{check_max_age if check_max_age else '∞'} месяцев 
                    для вида "{selected_species}" можно использовать.
                    
                    Вы можете добавить режим с этим диапазоном.
                    """)
                    
                    # Показываем визуализацию
                    st.markdown("**Визуализация диапазонов:**")
                    existing_regimes = execute_query(
                        "SELECT * FROM fn_get_all_watering_regimes() WHERE species_id = %s ORDER BY min_age_months",
                        (species_id,)
                    )
                    
                    if existing_regimes:
                        st.write("Существующие диапазоны:")
                        for r in existing_regimes:
                            max_age_display = r['max_age_months'] if r['max_age_months'] else '∞'
                            st.write(f"  🟦 {r['min_age_months']}-{max_age_display} мес (ID={r['regime_id']})")
                        
                        st.write(f"Новый диапазон:")
                        st.write(f"  🟩 {check_min_age}-{check_max_age if check_max_age else '∞'} мес (новый)")
                    else:
                        st.info("Для этого вида еще нет режимов полива")
        else:
            st.warning("Сначала добавьте виды растений")

def page_reports():
    st.header("Отчеты")
    
    tab1, tab2, tab3 = st.tabs([
        "Насаждения по виду",
        "Сотрудники на дату",
        "Растения и режимы полива"
    ])
    
    with tab1:
        st.subheader("Просмотр полной информации по насаждениям заданного вида")
        
        species = execute_query("SELECT * FROM fn_get_species_names()")
        if species:
            species_options = [s['species_name'] for s in species]
            selected_species = st.selectbox("Выберите вид растения", species_options, key="report_species_select")
            
            if st.button("Показать", key="report_species_btn"):
                plants = execute_query("SELECT * FROM fn_get_plants_by_species(%s)", (selected_species,))
                
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
            employees = execute_query("SELECT * FROM fn_get_employees_by_date(%s)", (report_date,))
            
            if employees:
                st.dataframe(employees, use_container_width=True)
            else:
                st.info(f"На {report_date} нет работающих сотрудников")
    
    with tab3:
        st.subheader("Просмотр перечня всех растений заданного вида и режимы их полива")
        
        species = execute_query("SELECT * FROM fn_get_species_names()")
        if species:
            species_options = [s['species_name'] for s in species]
            selected_species = st.selectbox("Выберите вид растения", species_options, key="report_regime_select")
            
            if st.button("Показать", key="report_regime_btn"):
                plants = execute_query("SELECT * FROM fn_get_plant_regimes_by_species(%s)", (selected_species,))
                
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
        species = execute_query("SELECT * FROM fn_get_all_species()")
        if species:
            st.dataframe(species, use_container_width=True)
        else:
            st.info("Виды растений не найдены")
    
    with tab2:
        with st.form("add_species"):
            species_name = st.text_input("Название вида *", key="add_species_name")
            
            if st.form_submit_button("Добавить"):
                if species_name:
                    result = call_procedure(
                        "sp_add_species",
                        (species_name,),
                        has_out_param=True
                    )
                    if result:
                        st.success("Вид добавлен!")
                        st.rerun()
                else:
                    st.error("Название вида обязательно")
    
    with tab3:
        species = execute_query("SELECT * FROM fn_get_all_species()")
        if species:
            species_options = {f"{s['species_name']}": s['species_id'] for s in species}
            selected = st.selectbox("Выберите вид для редактирования", list(species_options.keys()), key="edit_species_select")
            
            if selected:
                species_id = species_options[selected]
                species_data = execute_query("SELECT * FROM fn_get_species_by_id(%s)", (species_id,))
                
                if species_data:
                    with st.form("edit_species"):
                        new_name = st.text_input("Название вида", value=species_data[0]['species_name'], key="edit_species_name")
                        
                        if st.form_submit_button("Обновить"):
                            result = call_procedure(
                                "sp_update_species",
                                (species_id, new_name),
                                has_out_param=False
                            )
                            if result:
                                st.success("Вид обновлен!")
                                st.rerun()
        else:
            st.info("Нет видов для редактирования")
    
    with tab4:
        species = execute_query("SELECT * FROM fn_get_all_species()")
        if species:
            species_options = {f"{s['species_name']}": s['species_id'] for s in species}
            selected = st.selectbox("Выберите вид для удаления", list(species_options.keys()), key="delete_species_select")
            
            if selected:
                species_id = species_options[selected]
                
                with st.form("delete_species"):
                    st.warning(f"Вы уверены, что хотите удалить этот вид? Это действие нельзя отменить!")
                    if st.form_submit_button("Удалить", type="primary"):
                        result = call_procedure("sp_delete_species", (species_id,), has_out_param=False)
                        if result:
                            st.success("Вид удален!")
                            st.rerun()
        else:
            st.info("Нет видов для удаления")

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
    
    firms_count = execute_query("SELECT fn_get_firms_count() as count")
    parks_count = execute_query("SELECT fn_get_parks_count() as count")
    plants_count = execute_query("SELECT fn_get_plants_count() as count")
    employees_count = execute_query("SELECT fn_get_employees_count() as count")
    
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
            ["Главная", "Фирма", "Парки и зоны", "Растения", "Виды растений", "Режимы полива", "Персонал", "График работ", "Отчеты"]
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
    elif page == "Режимы полива":
        page_watering_regimes()
    elif page == "Персонал":
        page_employees()
    elif page == "График работ":
        page_schedule()
    elif page == "Отчеты":
        page_reports()

if __name__ == "__main__":
    main()
