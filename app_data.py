from configparser import ConfigParser
import pyodbc
import psycopg
import jinja2
from psycopg.rows import dict_row
import pandas as pd
import os
import numpy as np
import data
from icecream import ic
from plotly import graph_objects as go
import plotly.express as px

# Get postgres connection settings
config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'config.ini')
config_object = ConfigParser()
config_object.read(config_file)
pg_settings = config_object["POSTGRES"]
pg_uid = pg_settings["username"]
pg_pwd = pg_settings["password"]
pg_db = pg_settings["database"]

# Get REMS connection settings
rems_settings = config_object["REMS"]
rems_server = rems_settings["ip"]
rems_uid = rems_settings["uid"]
rems_pwd = rems_settings["pwd"]


def get_cohort(cohort):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
            select 
                cohorts.name
                , cohorts.start_date
                , programmes.short
                , programmes.degree
                , programmes.title
                , programmes.pathway
                , cohorts.top_up
            from cohorts
            left join programmes on cohorts.programme_id = programmes.id
            where cohorts.name = %(cohort)s
            """, {"cohort": cohort})
            result = cur.fetchall()
    if not result:
        return False
    else:
        return result[0]


def get_apprentice_attendance_by_employer_cohort(employer, cohort):
    sql_jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader('sql')
    )
    sql_template = sql_jinja_env.get_template('apprentice attendance by employer and cohort.sql')
    sql = sql_template.render(employer=employer, cohort=cohort)
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={rems_server};DATABASE=Reports;UID={rems_uid};PWD={rems_pwd}'
    )
    attendance_df = pd.read_sql(sql, conn)
    return attendance_df.to_dict(orient='records')


def get_apprentice_attendance(student_id):
    sql_jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader('sql')
    )
    sql_template = sql_jinja_env.get_template('apprentice attendance.sql')
    sql = sql_template.render(student_id=student_id)
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={rems_server};DATABASE=Reports;UID={rems_uid};PWD={rems_pwd}'
    )
    attendance_df = pd.read_sql(sql, conn)
    return attendance_df.to_dict(orient='records')


def get_apprentice_attendance_by_employer(employer):
    sql_jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader('sql')
    )
    sql_template = sql_jinja_env.get_template('apprentice attendance by employer.sql')
    sql = sql_template.render(employer=employer)
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={rems_server};DATABASE=Reports;UID={rems_uid};PWD={rems_pwd}'
    )
    attendance_df = pd.read_sql(sql, conn)
    return attendance_df.to_dict(orient='records')


def get_apprentice_attendance_by_student_list(student_id_list):
    sql_jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader('sql')
    )
    sql_template = sql_jinja_env.get_template('apprentice attendance by student list.sql')
    sql = sql_template.render(student_id_list=student_id_list)
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={rems_server};DATABASE=Reports;UID={rems_uid};PWD={rems_pwd}'
    )
    attendance_df = pd.read_sql(sql, conn)
    return attendance_df.to_dict(orient='records')


def get_apprentice_attendance_by_tsc(tsc):
    sql_jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader('sql')
    )
    sql_template = sql_jinja_env.get_template('apprentice attendance by tsc.sql')
    sql = sql_template.render(tsc=tsc)
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={rems_server};DATABASE=Reports;UID={rems_uid};PWD={rems_pwd}'
    )
    attendance_df = pd.read_sql(sql, conn)
    return attendance_df.to_dict(orient='records')


def get_cohort_list():
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}', options='-c search_path=public') as conn:
        with conn.cursor() as cur:
            cur.execute("""
            select name from cohorts order by start_date desc, name;
            """)
            # default is list of tuples
            result = [c[0] for c in cur.fetchall()]
    return result


def get_cohorts_by_employer(employer):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor() as cur:
            cur.execute("""
            select distinct name, min(start_date)
            from cohorts
            left join students on students.cohort_id = cohorts.id
            where students.employer = %(employer)s
            group by name 
            order by min(start_date) desc, name;
            """, {"employer": employer})
            # default is list of tuples
            result = [c[0] for c in cur.fetchall()]
    return result


def get_employer_list():
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}', options='-c search_path=public') as conn:
        with conn.cursor() as cur:
            cur.execute("""
            select distinct employer from students order by employer;
            """)
            # default is list of tuples
            result = [c[0] for c in cur.fetchall()]
    return result


def get_tsc_list():
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}', options='-c search_path=public') as conn:
        with conn.cursor() as cur:
            cur.execute("""
            select distinct skills_coach from students order by skills_coach;
            """)
            # default is list of tuples
            result = [c[0] for c in cur.fetchall()]
    return result


def get_module_list():
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
            select short, name from modules order by short;
            """)
            result = cur.fetchall()
    return result


def get_instances_of_module(module_short):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select * from modules left join instances on instances.module_id = modules.id where modules.short = %(module_short)s order by start_date desc;
            """, {"module_short": module_short})
            result = cur.fetchall()
    return result


def get_students_by_cohort_name(cohort_name):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select students.id student_id, given_name, family_name, employer, status, cohorts.name cohort from students
            left join cohorts on cohorts.id = students.cohort_id where cohorts.name = %(cohort_name)s
            order by family_name, given_name;
            """, {"cohort_name": cohort_name})
            result = cur.fetchall()
    return result


def get_students_by_employer(employer, selected_cohorts=False):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            if selected_cohorts:
                cur.execute(
                    """
                select students.id student_id, given_name, family_name, college_email, employer, status, cohorts.name cohort, cohorts.start_date from students
                left join cohorts on cohorts.id = students.cohort_id where students.employer = %(employer)s and cohorts.name = ANY(%(selected_cohorts)s)
                order by family_name, given_name;
                """, {"employer": employer, "selected_cohorts": selected_cohorts})
            else:
                cur.execute(
                    """
                select students.id student_id, given_name, family_name, college_email, employer, status, cohorts.name cohort, cohorts.start_date from students
                left join cohorts on cohorts.id = students.cohort_id where students.employer = %(employer)s
                order by family_name, given_name;
                """, {"employer": employer})
            result = cur.fetchall()
    return result


def get_active_cohorts():
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select c.name from students s left join cohorts c on s.cohort_id = c.id
                where s.status not in ('Completed', 'Withdrawn')
                group by c.name
                having count(*) > 0
                """
            )
            result = cur.fetchall()
    return [r[0] for r in result if r]


def get_students_by_tsc(tsc):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select students.id student_id, given_name, family_name, college_email, employer, status, cohorts.name cohort, cohorts.start_date from students
            left join cohorts on cohorts.id = students.cohort_id where students.skills_coach = %(tsc)s
            order by family_name, given_name;
            """, {"tsc": tsc})
            result = cur.fetchall()
    return result


def get_all_students():
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
            select students.id student_id, given_name, family_name, employer, status, cohorts.name cohort_name from students
            left join cohorts on cohorts.id = students.cohort_id order by family_name, given_name;
            """)
            result = cur.fetchall()
    return result


def get_instances_from_cohort_name(cohort_name):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
            select distinct start_date, modules.name, instances.code from instances
            left join modules on modules.id = instances.module_id
            left join components on instances.id = components.instance_id
            left join results on components.id = results.component_id
            left join students on results.student_id = students.id
            left join cohorts on students.cohort_id = cohorts.id
            where cohorts.name = %(cohort_name)s
            order by start_date desc;
            """, {"cohort_name": cohort_name})
            result = cur.fetchall()
    return result


def get_results_for_instance_code(instance_code):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select results.id result_id, given_name, family_name, college_email, students.id student_id,
            components.name, value, capped, weight, comment
            from results
            left join components on results.component_id = components.id
            left join instances on instances.id = components.instance_id
            left join students on results.student_id = students.id
            where instances.code = %(instance_code)s
            order by family_name, given_name, components.name;
            """, {"instance_code": instance_code})
            result = cur.fetchall()
    return result


def get_student_results_by_employer(employer, selected_cohorts=False):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            if selected_cohorts:
                sql = """
                                    select
                                        s.id student_id
                                        , m.level
                                        , m.name
                                        , rv.short
                                        , i.start_date
                                        , rv.code
                                        , rv.total mark
                                        , rv.credits 
                                    from students s
                                    left join results_view rv on rv.student_id = s.id
                                    left join instances i on rv.code = i.code
                                    left join modules m on i.module_id = m.id
                                    left join cohorts c on s.cohort_id = c.id
                                    where s.employer = %(employer)s
                                    and (rv.rank = 1 or rv.rank is null)
                                    and c.name = ANY(%(selected_cohorts)s)
                                    """
                cur.execute(sql, {
                    "employer": employer, "selected_cohorts": selected_cohorts
                })
            else:
                sql = """
                    select
                        s.id student_id
                        , m.level
                        , m.name
                        , rv.short
                        , i.start_date
                        , rv.code
                        , rv.total mark
                        , rv.credits 
                    from students s
                    left join results_view rv on rv.student_id = s.id
                    left join instances i on rv.code = i.code
                    left join modules m on i.module_id = m.id
                    where s.employer = %(employer)s
                    and (rv.rank = 1 or rv.rank is null)
                    """
                cur.execute(sql, {
                    "employer": employer
                })
            result = cur.fetchall()
    return result


def get_student_results_by_tsc(tsc):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            sql = """
                select
                    s.id student_id
                    , m.level
                    , m.name
                    , rv.short
                    , i.start_date
                    , rv.code
                    , rv.total mark
                    , rv.credits 
                from students s
                left join results_view rv on rv.student_id = s.id
                left join instances i on rv.code = i.code
                left join modules m on i.module_id = m.id
                where s.skills_coach = %(tsc)s
                and (rv.rank = 1 or rv.rank is null)
                """
            cur.execute(sql, {
                "tsc": tsc
            })
            result = cur.fetchall()
    return result


def get_student_results_by_employer_cohort(employer, cohort_name=None):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            sql = """
                select
                    s.id student_id
                    , h.name cohort
                    , s.family_name family_name
                    , s.given_name given_name
                    , s.status
                    , m.level
                    , m.name
                    , rv.short
                    , i.start_date
                    , rv.code
                    , rv.total mark
                    , rv.credits 
                from students s
                left join results_view rv on rv.student_id = s.id
                left join cohorts h on h.id = s.cohort_id
                left join instances i on rv.code = i.code
                left join modules m on i.module_id = m.id
                where s.employer = %(employer)s
                and rv.rank = 1 or rv.rank is null
                """
            if cohort_name and cohort_name != "All":
                sql += """
                and h.name = %(cohort_name)s
                """
            cur.execute(sql, {
                "cohort_name": cohort_name,
                "employer": employer
            })
            result = cur.fetchall()
    return result


def get_results_for_student(student_id):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select 
             modules.name
             , modules.level
             , results_view.total
             , results_view.credits
             , results_view.short
             , results_view.code
            from results_view
            left join modules on modules.short = results_view.short
            where student_id = %(student_id)s and rank = 1
            """, {"student_id": student_id})
            result = cur.fetchall()
    return result


def get_results_report_for_student(student_id, top_up=False):
    results = pd.DataFrame.from_records(get_results_for_student(student_id),
                    columns=['name', 'level', 'total', 'credits', 'short', 'code']).fillna(0)
    if top_up:
        counted_results = results.query('level == 6')
    else:
        counted_results = results

    if len(counted_results) < 1 or counted_results['credits'].sum() < 1:
        average_result = "-"
    else:
        average_result = counted_results['total'].mul(counted_results['credits']).sum() / counted_results['credits'].sum()
        average_result = round_normal(float(average_result))

    credits = results['credits'].sum()
    results = results.sort_values(['level', 'name']).to_dict(orient='records')
    return results, credits, average_result


def get_passing_results_for_student(student_id):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                select
                    level "Level"
                    , pass_view.credits "Credits"
                    , modules.name "Module"
                    , total "Mark"
                from pass_view
                left join instances on pass_view.code = instances.code
                left join modules on instances.module_id = modules.id
                where instances.moderated and student_id = %(student_id)s
                """, {"student_id": student_id})
            result = cur.fetchall()
    return result


def get_result_for_instance(student_id, instance_code):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select
                case
                    when grouping(c.name) = 1 then 'Total'
                    else c.name
                end "Component"
                , case
                    when grouping(c.name) = 0 then c.weight
                    else sum(c.weight)
                end ::integer "Weighting"
                , case
                    when grouping(c.name) = 1 then round(sum(c.weight::numeric * r.value) / sum(c.weight))
                    else r.value
                end "Mark"
                from instances i
                left join components c on i.id = c.instance_id
                left join results r on c.id = r.component_id
                left join modules m on i.module_id = m.id
                where i.id = (select id from instances where code = %(instance_code)s)
                and r.student_id = %(student_id)s
                group by grouping sets((c.name, c.weight, r.value), ())
                order by grouping(c.name), c.name;
                """, {
                    'student_id': student_id,
                    'instance_code': instance_code
                })
            result = cur.fetchall()
    return result


def get_students_by_instance(instance_code):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select distinct results.student_id student_id
                from instances
                left join components on components.instance_id = instances.id
                left join results on results.component_id = components.id
                where instances.code = %(instance_code)s
                """, {"instance_code": instance_code})
            result = cur.fetchall()
        return [r[0] for r in result]


def get_results_for_instance(instance_code):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select 
                student_id
                , total
            from results_view
            where code = %(instance_code)s;
            """, {"instance_code": instance_code})
            result = cur.fetchall()
    return result


def get_student_by_id(student_id):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select family_name, given_name, status, employer, cohorts.name cohort_name, college_email, cohorts.start_date
            , cohorts.top_up or students.top_up top_up, programmes.degree, programmes.title, programmes.pathway
            from students
            left join cohorts on cohort_id = cohorts.id
            left join programmes on programmes.id = cohorts.programme_id
            where students.id = %(student_id)s;
            """, {"student_id": student_id})
            result = cur.fetchone()
    return result


def get_student_list_by_instance_code(code):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
            select distinct student_id
            from results
            left join components on results.component_id = components.id
            left join instances on components.instance_id = instances.id
            where code = %(code)s;
            """, {"code": code})
            result = [c[0] for c in cur.fetchall()]
    return result


def get_missing_results():
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select m.name, m.short, i.code, count(distinct r.student_id)
            from instances i
            left join modules m on i.module_id = m.id
            left join components c on c.instance_id = i.id
            left join results r on r.component_id = c.id
            where r.value is null or r.value = 0 
            group by m.name, m.short, i.code, i.start_date
            order by i.start_date;
            """)
            result = cur.fetchall()
    return result


def get_permissions(email):
    '''
    Returns a dict of permissions for the user identified by email
    '''
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select * from users where email = %(email)s;
            """, {"email": email})
            result = cur.fetchone()
    return result


def get_user_list():
    '''
    Returns a list of known users
    '''
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor() as cur:
            cur.execute("""
            select email from users;
            """)
            result = [e[0] for e in cur.fetchall()]
    return result


def get_components_by_instance_code(instance_code):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select * from components
            left join instances on instances.id = components.instance_id
            where instances.code = %(instance_code)s;
            """, {"instance_code": instance_code})
            result = cur.fetchall()
    return result


def get_instance_by_instance_code(instance_code):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select instances.id instance_id, modules.name, start_date, second_date, moderated from instances
            left join modules on modules.id = instances.module_id
            where instances.code = %(instance_code)s;
            """, {"instance_code": instance_code})
            result = cur.fetchone()
    return result


def get_student_list_by_employer_cohort(employer, cohort):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
            select s.id student_id
            from students s
            left join cohorts h on s.cohort_id = h.id
            where employer = %(employer)s and h.name = %(cohort)s
            """, {
                    "employer": employer,
                    "cohort": cohort
                })
            result = [e[0] for e in cur.fetchall()]
    return result


def get_upcoming_students_instances():
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                select distinct
                  i.code code
                , s.id student_id
                from students s
                left join results r on r.student_id = s.id
                left join components p on p.id = r.component_id
                left join instances i on i.id = p.instance_id
                where date_part('days', i.start_date - now()) > -90
           """)
            result = cur.fetchall()
    return result


def get_upcoming_class_lists():
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                select distinct
                i.code code
                , i.start_date start_date
                , s.id student_id
                , s.given_name given_name
                , s.family_name family_name
                , s.college_email email
                , s.employer employer
                , c.name cohort
                from instances i
                left join components p on p.instance_id = i.id
                left join results r on r.component_id = p.id
                left join students s on r.student_id = s.id
                left join cohorts c on c.id = s.cohort_id
                where date_part('days', i.start_date - now()) > -90
                order by start_date desc, code, family_name, given_name
           """)
            result = cur.fetchall()
    return result


def update_result_by_id(result_id, new_value, new_capped, new_comment, lecturer):
    return_value = False
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            update results set value = %(new_value)s, capped = %(new_capped)s, updated_at = CURRENT_TIMESTAMP,
            comment = %(new_comment)s, missing = false, lecturer = %(lecturer)s where results.id = %(result_id)s;
            """, {
                    "new_value": new_value,
                    "new_capped": new_capped,
                    "new_comment": new_comment,
                    "lecturer": lecturer,
                    "result_id": result_id
                })
            return_value = cur.rowcount
    return return_value


def set_result_by_component_name_instance_code(student_id, new_value,
                                               component_name, instance_code,
                                               lecturer):
    return_value = False
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            update results set value = %(new_value)s, missing = false, lecturer = %(lecturer)s, updated_at = CURRENT_TIMESTAMP
            from components c
            left join instances i on c.instance_id = i.id
            where student_id = %(student_id)s
            and c.name = %(component_name)s
            and i.code = %(instance_code)s
            and results.component_id = c.id;
            """, {
                    "new_value": new_value,
                    "lecturer": lecturer,
                    "student_id": student_id,
                    "component_name": component_name,
                    "instance_code": instance_code
                })
            if cur.rowcount > 1:
                conn.rollback()
            return_value = cur.rowcount
    return return_value


def set_moderated_by_instance_code(instance_code, moderated):
    return_value = False
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            update instances set moderated = %(moderated)s, updated_at = CURRENT_TIMESTAMP
            where instances.code = %(instance_code)s
            """, {
                    "moderated": moderated,
                    "instance_code": instance_code
                })
            if cur.rowcount > 1:
                conn.rollback()
            else:
                return_value = True

    return return_value


def add_module(short, name, level, credits):
    return_value = False
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            insert into modules (short, name, level, credits, inserted_at, updated_at)
            values (%(short)s, %(name)s, %(level)s, %(credits)s, current_timestamp, current_timestamp)
            on conflict do nothing;
            """, {
                    "short": short,
                    "name": name,
                    "level": level,
                    "credits": credits
                })
            return_value = cur.rowcount
    return return_value


def add_cohort(name, start_date):
    return_value = False
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            insert into cohorts (name, start_date, inserted_at, updated_at)
            values (%(name)s, %(start_date)s, current_timestamp, current_timestamp)
            on conflict (name) do update set (start_date, updated_at) = (excluded.start_date, current_timestamp);
            """, {"name": name, "start_date": start_date})
            return_value = cur.rowcount
    return return_value


def add_instance(short, code, start_date, second_date=None):
    return_value = False
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            try:
                cur.execute(
                    """
                insert into instances (code, start_date, second_date, module_id, inserted_at, updated_at)
                values (%(code)s, %(start_date)s, %(second_date)s, (select id from modules where short = %(short)s), current_timestamp, current_timestamp)
                on conflict do nothing;
                """, {
                        "code": code,
                        "short": short,
                        "start_date": start_date,
                        "second_date": second_date
                    })
                return_value = cur.rowcount
            except psycopg.errors.NotNullViolation:
                return_value = False
    return return_value


def add_component_to_instance(code, name, weight):
    return_value = False
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            try:
                cur.execute(
                    """
                insert into components (name, weight, instance_id, inserted_at, updated_at)
                values (%(name)s, %(weight)s, (select instances.id from instances where instances.code = %(code)s), current_timestamp, current_timestamp)
                on conflict do nothing;
                """, {
                        "code": code,
                        "name": name,
                        "weight": weight
                    })
                return_value = cur.rowcount
            except psycopg.errors.NotNullViolation:
                return_value = False
    return return_value


def add_student_to_instance(student_id, code, lecturer):
    return_value = False
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            try:
                cur.execute(
                    """
                insert into results (lecturer, missing, component_id, student_id, inserted_at, updated_at)
                (select %(lecturer)s, True, components.id, %(student_id)s, current_timestamp, current_timestamp
                from instances left join components on components.instance_id = instances.id
                where code = %(code)s)
                on conflict do nothing;
                """, {
                        "lecturer": lecturer,
                        "student_id": int(student_id),
                        "code": code
                    })
                return_value = cur.rowcount
            except psycopg.errors.NotNullViolation:
                return_value = False
    return return_value


def add_students_to_instance(student_ids, code, lecturer):
    return_value = False
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            return_value = 0
            for student_id in student_ids:
                try:
                    cur.execute(
                        """
                    insert into results (lecturer, missing, component_id, student_id, inserted_at, updated_at)
                    (select %(lecturer)s, True, components.id, %(student_id)s, current_timestamp, current_timestamp
                    from instances left join components on components.instance_id = instances.id
                    where code = %(code)s)
                    on conflict do nothing;
                    """, {
                            "lecturer": lecturer,
                            "student_id": int(student_id),
                            "code": code
                        })
                    return_value += cur.rowcount
                except psycopg.errors.NotNullViolation:
                    return_value = False
    return return_value


def update_learners(learners):
    return_value = False
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            return_value = 0
            for learner in learners:
                cur.execute(
                    """
insert into students (id, given_name, family_name, status, employer, cohort_id, start_date, skills_coach, inserted_at, updated_at)
                values (%(student_id)s, %(given_name)s, %(family_name)s, %(status)s, %(employer)s, (select id from cohorts where name = %(cohort)s), %(start_date)s, %(skills_coach)s, current_timestamp, current_timestamp)
                on conflict (id) do update
                set given_name = excluded.given_name,
                    family_name = excluded.family_name,
                    status = excluded.status,
                    employer = excluded.employer,
                    cohort_id = excluded.cohort_id,
                    start_date = excluded.start_date,
                    skills_coach = excluded.skills_coach,
                    updated_at = excluded.updated_at;
                """, learner)
                return_value += cur.rowcount
    return return_value


def update_component_name(instance_code, old_name, new_name, weight):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                    update components set name = %(new_name)s, weight = %(weight)s
                    where name = %(old_name)s and instance_id = (select id from instances where code = %(instance_code)s);
                    """, {
                    "old_name": old_name,
                    "new_name": new_name,
                    "instance_code": instance_code,
                    "weight": weight
                })
            return_value = cur.rowcount
    return return_value


def delete_student_from_instance(student_id, code):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                delete from results where
                component_id in (select id from components where instance_id = (select id from instances where code = %(code)s)) and student_id = %(student_id)s and value is null;
                    """, {
                    "code": code,
                    "student_id": student_id
                })
            return_value = cur.rowcount
    return return_value


def round_normal(x):
    if x is None or np.isnan(x):
        result = '-'
    else:
        result = int(np.floor(np.add(x, 0.5)))
    return result


def parse_cohort(cohort):
    location = 'MCR' if cohort.startswith('M-') else 'LDN'
    cohort_dict = get_cohort(cohort)
    year = cohort_dict.get('start_date').year
    if cohort_dict.get('top_up', False):
        cohort_dict.update({'short': cohort_dict.get('short') + ' 1Y'})
    intake = 'Autumn' if cohort_dict.get('start_date').month > 7 else 'Spring'
    cohort_dict.update({'location': location,
                        'year': year,
                        'intake': intake,
                        'year_intake': f'{year} {intake}'})
    return cohort_dict


def graph_grade_profile(results_df, mark_column_name='total'):
    if len(results_df) == 0:
        return {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "height": 320
            }
        }
    labels = ["Incomplete", "Fail", "Pass", "Merit", "Distinction", "Error"]
    axis_labels = ["Incomplete", "Fail", "Pass", "Merit", "Distinction"]
    # Cut doesn't like NaN so set to something in the missing bin
    results_df[mark_column_name] = results_df[mark_column_name].fillna(-99)
    results_df["class"] = pd.cut(results_df[mark_column_name], [-float("inf"), 0, 39.5, 59.5, 69.5, 101, float("inf")],
                                 labels=labels, right=False)
    results_df["class"] = pd.Categorical(results_df["class"], axis_labels)
    bar_trace = go.Histogram(
        x=results_df["class"],
        # hovertemplate="%{y:.0f}% %{x}<extra></extra>",
        texttemplate="%{y:.0f}%",
        histfunc='count',
        marker_color='steelblue',
        histnorm='percent'
    )
    fig = go.Figure()
    fig.update_xaxes(
        categoryorder='array',
        categoryarray=axis_labels,
        range=(-1, 5)
    )
    fig.add_trace(bar_trace)
    return fig


def graph_learner_volumes(learners_df):
    if len(learners_df) == 0:
        return {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "height": 320
            }
        }

    cohort_expansion_df = learners_df[['cohort']].apply(lambda row: pd.Series(parse_cohort(row['cohort'])), axis=1)[['year_intake']]
    learners_df = cohort_expansion_df.join(learners_df)
    year_intakes = learners_df.sort_values('start_date')['year_intake'].unique()
    learners_df['year_intake'] = pd.Categorical(learners_df['year_intake'], categories=year_intakes)
    learners_df['status'] = pd.Categorical(learners_df['status'], categories=['Continuing', 'Withdrawn', 'Break in learning', 'Completed'])

    counts_df = learners_df[['year_intake', 'status']].groupby(['year_intake', 'status'], as_index=False).size()
    counts_df.columns = map(data.snake_to_title, counts_df.columns)
    fig = px.bar(counts_df.reset_index(), x='Year Intake', y='Size', color='Status', text_auto=True, color_discrete_sequence=px.colors.qualitative.Safe)

    return fig


if __name__ == "__main__":
    pass


