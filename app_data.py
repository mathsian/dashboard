from configparser import ConfigParser
import psycopg
from psycopg.rows import dict_row

# Get connection settings
config_object = ConfigParser()
config_object.read("config.ini")
pg_settings = config_object["POSTGRES"]
pg_uid = pg_settings["username"]
pg_pwd = pg_settings["password"]
pg_db = pg_settings["database"]

def get_cohort_list():
    with psycopg.connect(f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor() as cur:
            cur.execute("""
            select cohort_name from cohorts order by cohort_name;
            """)
            # default is list of tuples
            result = [c[0] for c in cur.fetchall()]
    return result


def get_module_list():
    with psycopg.connect(f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor() as cur:
            cur.execute("""
            select module_name from modules order by module_name;
            """)
            # default is list of tuples
            result = [c[0] for c in cur.fetchall()]
    return result


def get_instances_of_module(module_name):
    with psycopg.connect(f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
            select * from modules left join instances on instances.module_id = modules.id where modules.module_name = %(module_name)s order by start_date desc;
            """, {"module_name": module_name})
            result = cur.fetchall()
    return result


def get_students_by_cohort_name(cohort_name):
    with psycopg.connect(f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
            select students.id student_id, given_name, family_name, employer, status from students
            left join cohorts on cohorts.id = students.cohort_id where cohort_name = %(cohort_name)s;
            """, {"cohort_name": cohort_name})
            result = cur.fetchall()
    return result

def get_instances_from_cohort_name(cohort_name):
    with psycopg.connect(f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor() as cur:
            cur.execute("""
            select distinct start_date, module_name, instance_code from instances
            left join modules on modules.id = instances.module_id
            left join components on instances.id = components.instance_id
            left join results on components.id = results.component_id
            left join students on results.student_id = students.id
            left join cohorts on students.cohort_id = cohorts.id
            where cohort_name = %(cohort_name)s
            order by start_date desc;
            """, {"cohort_name": cohort_name})
            result = cur.fetchall()
    return result


def get_results_for_cohort_name(cohort_name):
    with psycopg.connect(f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
            select * from instances
            left join components on instances.id = components.instance_id
            left join results on components.id = results.component_id
            left join students on results.student_id = students.id
            left join cohorts on cohorts.id = students.cohort_id
            where cohorts.cohort_name = %(cohort_name)s;
            """, {"cohort_name": cohort_name})
            result = cur.fetchall()
    return result


def get_results_for_instance_code(instance_code):
    with psycopg.connect(f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
            select given_name, family_name, students.id student_id,
            component_name, value, capped, weight
            from results
            left join components on results.component_id = components.id
            left join instances on instances.id = components.instance_id
            left join students on results.student_id = students.id
            where instances.instance_code = %(instance_code)s
            order by family_name, given_name, component_name;
            """, {"instance_code": instance_code})
            result = cur.fetchall()
    return result


def get_student_results_by_cohort_instance(cohort_name, instance_code):
    with psycopg.connect(f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
            select given_name, family_name, students.id student_id,
            component_name, value, capped, weight
            from results
            left join components on components.id = results.component_id
            left join instances on instances.id = components.instance_id
            left join students on students.id = results.student_id
            left join cohorts on cohorts.id = students.cohort_id
            where cohort_name = %(cohort_name)s and instance_code = %(instance_code)s
            """, {"cohort_name": cohort_name, "instance_code": instance_code})
            result = cur.fetchall()
    return result

def get_results_for_student(student_id):
    with psycopg.connect(f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
            select instance_code, round(cast(sum(value * weight) as numeric) / cast(sum(weight) as numeric),0) total
            from results
            left join components on components.id = results.component_id
            left join instances on instances.id = components.instance_id
            left join students on students.id = results.student_id
            where students.id = %(student_id)s
            group by instance_code
            """, {"student_id": student_id})
            result = cur.fetchall()
    return result


def get_results_for_instance(instance_code):
    with psycopg.connect(f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
            select students.id, round(cast(sum(value * weight) as numeric)/cast(sum(weight) as numeric),0) total
            from results
            left join components on components.id = results.component_id
            left join instances on instances.id = components.instance_id
            left join students on students.id = results.student_id
            where instances.instance_code = %(instance_code)s
            group by students.id;
            """, {"instance_code": instance_code})
            result = cur.fetchall()
    return result


def get_student_by_id(student_id):
    with psycopg.connect(f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
            select * from students where students.id = %(student_id)s;
            """, {"student_id": student_id})
            result = cur.fetchone()
    return result


def get_components_by_instance_code(instance_code):
    with psycopg.connect(f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
            select * from components
            left join instances on instances.id = components.instance_id
            where instances.instance_code = %(instance_code)s;
            """, {"instance_code": instance_code})
            result = cur.fetchall()
    return result


if __name__ == "__main__":
    print(get_results_for_cohort_name('L-L4-DA-NOV-20'))
