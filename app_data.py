from configparser import ConfigParser
import psycopg
from psycopg.rows import dict_row
import os

# Get connection settings
config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'config.ini')
config_object = ConfigParser()
config_object.read(config_file)
pg_settings = config_object["POSTGRES"]
pg_uid = pg_settings["username"]
pg_pwd = pg_settings["password"]
pg_db = pg_settings["database"]


def get_cohort_list():
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor() as cur:
            cur.execute("""
            select name from cohorts order by name;
            """)
            # default is list of tuples
            result = [c[0] for c in cur.fetchall()]
    return result


def get_cohorts_by_employer(employer):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor() as cur:
            cur.execute("""
            select distinct name
            from cohorts
            left join students on students.cohort_id = cohorts.id
            where students.employer = %(employer)s
            order by name;
            """, {"employer": employer})
            # default is list of tuples
            result = [c[0] for c in cur.fetchall()]
    return result


def get_employer_list():
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor() as cur:
            cur.execute("""
            select distinct employer from students order by employer;
            """)
            # default is list of tuples
            result = [c[0] for c in cur.fetchall()]
    return result


def get_module_list():
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor() as cur:
            cur.execute("""
            select name from modules order by name;
            """)
            # default is list of tuples
            result = [c[0] for c in cur.fetchall()]
    return result


def get_instances_of_module(module_name):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select * from modules left join instances on instances.module_id = modules.id where modules.name = %(module_name)s order by start_date desc;
            """, {"module_name": module_name})
            result = cur.fetchall()
    return result


def get_students_by_cohort_name(cohort_name):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select students.id student_id, given_name, family_name, employer, status, cohorts.name cohort_name from students
            left join cohorts on cohorts.id = students.cohort_id where cohorts.name = %(cohort_name)s
            order by family_name, given_name;
            """, {"cohort_name": cohort_name})
            result = cur.fetchall()
    return result


def get_students_by_employer(employer):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select students.id student_id, given_name, family_name, employer, status, cohorts.name cohort_name from students
            left join cohorts on cohorts.id = students.cohort_id where students.employer = %(employer)s
            order by family_name, given_name;
            """, {"employer": employer})
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


def get_results_for_cohort_name(cohort_name):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select * from instances
            left join components on instances.id = components.instance_id
            left join results on components.id = results.component_id
            left join students on results.student_id = students.id
            left join cohorts on cohorts.id = students.cohort_id
            where cohorts.name = %(cohort_name)s;
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


def get_student_results_by_cohort_instance(cohort_name, instance_code):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select given_name, family_name, students.id student_id,
            component_name, value, capped, weight
            from results
            left join components on components.id = results.component_id
            left join instances on instances.id = components.instance_id
            left join students on students.id = results.student_id
            left join cohorts on cohorts.id = students.cohort_id
            where cohorts.name = %(cohort_name)s and instances.code = %(instance_code)s
            """, {
                    "cohort_name": cohort_name,
                    "instance_code": instance_code
                })
            result = cur.fetchall()
    return result


def get_student_results_by_employer_cohort(employer, cohort_name=None):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            sql = """
                select
                    s.family_name
                    , s.given_name
                    , m.level
                    , m.name
                    , m.short
                    , i.start_date
                    , i.code
                    , round(cast(sum(r.value * c.weight) as float)/sum(c.weight)) mark
                from cohorts h
                left join students s on h.id = s.cohort_id
                left join results r on s.id = r.student_id
                left join components c on r.component_id = c.id
                left join instances i on c.instance_id = i.id
                left join modules m on i.module_id = m.id
                where s.employer = %(employer)s
                """
            if cohort_name and cohort_name != "All":
                sql += """
                and h.name = %(cohort_name)s
                """
            sql += """
                group by
                s.family_name
                , s.given_name
                , m.level
                , m.name
                , m.short
                , i.start_date
                , i.code;
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
            select modules.level as level, modules.name as name, instances.code as code, round(cast(sum(value * weight) as numeric) / cast(sum(weight) as numeric),0)::int total
            from results
            left join components on components.id = results.component_id
            left join instances on instances.id = components.instance_id
            left join students on students.id = results.student_id
            left join modules on instances.module_id = modules.id
            where students.id = %(student_id)s
            group by modules.name, modules.level, instances.code
            order by modules.level, modules.name, instances.code
            """, {"student_id": student_id})
            result = cur.fetchall()
    return result


def get_detailed_results_for_student(student_id):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select code, level, credits, modules.name "name", round(cast(sum(value * weight) as numeric) / cast(sum(weight) as numeric),0)::int total, moderated
            from results
            left join components on components.id = results.component_id
            left join instances on instances.id = components.instance_id
            left join students on students.id = results.student_id
            left join modules on instances.module_id = modules.id
            where students.id = %(student_id)s
            group by modules.name, level, credits, code, moderated
            """, {"student_id": student_id})
            result = cur.fetchall()
    return result


def get_results_for_cohort_employer(cohort, employer):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                select level as "Level", m.name as "Module", code as "Instance", s.id as "student_id", round(cast(sum(value * weight) as numeric) / cast(sum(weight) as numeric),0)::int as "total"
                from results
                left join components c on results.component_id = c.id
                left join instances i on c.instance_id = i.id
                left join modules m on i.module_id = m.id
                left join students s on results.student_id = s.id
                left join cohorts c2 on s.cohort_id = c2.id
                where c2.name = %(cohort)s and s.employer = %(employer)s
                group by level, m.name, code, s.id;
           """, {
                    'cohort': cohort,
                    'employer': employer
                })
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
                    when grouping(c.name) = 1 then round(cast(sum(r.value * c.weight) as float)/sum(c.weight))
                    else r.value
                end ::integer "Mark"
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
            select students.id, sum(value * weight) vw, sum(weight) w, round(sum(value * weight) / sum(weight), 1) total
            from results
            left join components on components.id = results.component_id
            left join instances on instances.id = components.instance_id
            left join students on students.id = results.student_id
            where instances.code = %(instance_code)s
            group by students.id;
            """, {"instance_code": instance_code})
            result = cur.fetchall()
    return result


def get_student_by_id(student_id):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select family_name, given_name, status, employer, cohorts.name cohort_name, college_email
            from students
            left join cohorts on cohort_id = cohorts.id
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


def get_results_by_employer_cohort_module(employer, cohort, module):
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            select employer, h.name cohort_name, m.name module_name, i.code instance_code, given_name, family_name,
                round(sum(value * weight) / sum(weight), 1) total
            from results r
            left join components c on r.component_id = c.id
            left join instances i on c.instance_id = i.id
            left join modules m on i.module_id = m.id
            left join students s on r.student_id = s.id
            left join cohorts h on s.cohort_id = h.id
            where employer = %(employer)s and h.name = %(cohort)s and m.name = %(module)s
            group by employer, h.name cohort_name, m.name module_name, i.code instance_code, given_name, family_name,
            """, {
                    "employer": employer,
                    "cohort": cohort,
                    "module": module
                })
            result = cur.fetchall()
    return result


def get_upcoming_class_lists():
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                select
                i.code code
                , i.start_date start_date
                , si.student_id student_id
                , s.given_name given_name
                , s.family_name family_name
                , s.college_email email
                , s.employer employer
                , c.name cohort
                from students_instances si
                left join students s on si.student_id = s.id
                left join instances i on si.instance_id = i.id
                left join cohorts c on c.id = s.cohort_id
                where date_part('days', i.start_date - now()) > -90
           """)
            result = cur.fetchall()
    return result



def set_result(result_id, new_value, new_capped, new_comment, lecturer):
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


def set_results(results, lecturer):
    return_value = False
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            for result in results:
                cur.execute(
                    """
                update results set value = %(new_value)s, capped = %(new_capped)s, missing = false,
                comment = %(new_comment)s, lecturer = %(lecturer)s, updated_at = CURRENT_TIMESTAMP
                where results.id = %(result_id)s;
                """, {
                        "new_value": result["new_value"],
                        "new_capped": result["new_capped"],
                        "new_comment": result["new_comment"],
                        "lecturer": lecturer,
                        "result_id": result["result_id"]
                    })
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


def add_cohort(name):
    return_value = False
    with psycopg.connect(
            f'dbname={pg_db} user={pg_uid} password={pg_pwd}') as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
            insert into cohorts (name, inserted_at, updated_at)
            values (%(name)s, current_timestamp, current_timestamp)
            on conflict do nothing;
            """, {"name": name})
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
insert into students (id, given_name, family_name, status, employer, cohort_id, inserted_at, updated_at)
                values (%(student_id)s, %(given_name)s, %(family_name)s, %(status)s, %(employer)s, (select id from cohorts where name = %(cohort)s), current_timestamp, current_timestamp)
                on conflict (id) do update
                set given_name = excluded.given_name,
                    family_name = excluded.family_name,
                    status = excluded.status,
                    employer = excluded.employer,
                    cohort_id = excluded.cohort_id,
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


if __name__ == "__main__":
    # print(get_user_list())
    # print(get_results_for_instance('SDL010'))
    pass
