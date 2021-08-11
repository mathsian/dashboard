from arango import ArangoClient
import names
import numpy as np

def build_db():
    client = ArangoClient(hosts="http://192.168.1.4:8529")
    sys_db = client.db('_system', username='root', password='Ar_mishy170')
    if sys_db.has_database("testing"):
        sys_db.delete_database("testing")
    sys_db.create_database("testing")
    testing = client.db('testing', username='root', password='Ar_mishy170')
    sf = testing.create_graph("sixthform")
    # Cohorts
    cohorts = sf.create_vertex_collection("cohorts")
    # Populate cohorts
    for chrt in ["19-21", "20-22"]:
        cohorts.insert({
        '_key': chrt,
        'name': chrt
    })
    # Departments
    departments = sf.create_vertex_collection("departments")
    dpts = [('Maths', 'MA'), ('Computer Science', 'CS'), ('Graphics', 'GR')]
    # Subjects
    subjects = sf.create_vertex_collection("subjects")
    sbjs = {'MA': ['L3-MA-AL', 'L3-FM-AL', 'L3-MS-CE'],
            'CS': ['BTEC-CS-DP', 'BTEC-CS-EC', 'BTEC-CS-EX'],
            'GR': ['L3-GR-AL']}
    # subject -> department: in_department
    in_department = sf.create_edge_definition(
        edge_collection="in_department",
        from_vertex_collections=['departments'],
        to_vertex_collections=['subjects'])
    # Assessments
    assessments = sf.create_vertex_collection("assessments")
    # assessment -> subject: in_subject
    in_subject = sf.create_edge_definition(
        edge_collection="in_subject",
        from_vertex_collections=['assessments'],
        to_vertex_collections=['subjects']
    )
    # Populate departments and subjects
    for dpt, dpc in dpts:
        departments.insert({
            '_key': dpc,
            'name': dpt
        })
        for sbj in sbjs.get(dpc):
            subjects.insert({
                '_key': sbj,
                'name': sbj,
            })
            in_department.insert({
                '_from': f'subjects/{sbj}',
                '_to': f'departments/{dpc}'
            })
            ass1 = assessments.insert({
                "_key": f'{sbj}-ass1',
                "date": "2020-11-01",
                "scale": "BTEC-Single" if dpc=="CS" else "A-Level",
                "name": "Assessment 1"
            })
            ass2 = assessments.insert({
                "_key": f'{sbj}-ass2',
                "date": "2021-03-01",
                "scale": "BTEC-Single" if dpc=="CS" else "A-Level",
                "name": "Assessment 2"
            })
            in_subject.insert({
                "_from": f'assessments/{sbj}-ass1',
                "_to": f'subjects/{sbj}'
            })
            in_subject.insert({
                "_from": f'assessments/{sbj}-ass2',
                "_to": f'subjects/{sbj}'
            })

    # Staff
    staff = sf.create_vertex_collection("staff")
    # Teams
    teams = sf.create_vertex_collection("teams")
    # team -> cohort: in_cohort
    in_cohort = sf.create_edge_definition(
        edge_collection="in_cohort",
        from_vertex_collections=["teams", "subjects"],
        to_vertex_collections=["cohorts"]
    )

    # Students
    students = sf.create_vertex_collection("students")
    # student -> team: member
    member = sf.create_edge_definition(
        edge_collection="in_team",
        from_vertex_collections=["students"],
        to_vertex_collections=["teams"])
    # student -> subject: enrolled
    enrolled = sf.create_edge_definition(
        edge_collection="enrolled",
        from_vertex_collections=['students'],
        to_vertex_collections=['subjects'])
    # student -> assessment: sat
    sat = sf.create_edge_definition(
        edge_collection="sat",
        from_vertex_collections=['students'],
        to_vertex_collections=['assessments'])
    # staff -> student: kudos
    kudos = sf.create_edge_definition(
        edge_collection="kudos",
        from_vertex_collections=['staff'],
        to_vertex_collections=['students'])
    # staff -> student: concern
    concern = sf.create_edge_definition(
        edge_collection="concern",
        from_vertex_collections=['staff'],
        to_vertex_collections=['students'])

    # Populate teams, staff, students
    for j in range(8):
        # Create staff
        fn = names.get_first_name()
        ln = names.get_last_name()
        fullname  = ".".join((fn, ln))
        staff.insert({
            '_key': fullname,
            'first_name': fn,
            'last_name': ln,
            'email': f'{fn}@testing.com'
        })
        # Create team
        teams.insert({
            '_key': fn,
            'name': fn})
        chrt = "19-21" if j < 4 else "20-22"
        in_cohort.insert({
            "_from": f'teams/{fn}',
            "_to": f'cohorts/{chrt}'
        })
        # Create students
        pfx = 19000 if j < 4 else 20000
        for st_id in [f"{pfx + 100*j + i}" for i in range(1, 15)]:
            sfn = names.get_first_name()
            sln = names.get_last_name()
            students.insert({
                '_key': st_id,
                'first_name': sfn,
                'last_name': sln,
                'email': f'{sfn}.{sln}@testing.com'
            })
            member.insert({
                "_from": f'students/{st_id}',
                "_to": f'teams/{fn}'
            })
            for dpt, dpc in dpts:
                sbj = np.random.choice(sbjs[dpc])
            enrolled.insert({
                "_from": f'students/{st_id}',
                "_to": f'subjects/{sbj}'
            })
            if dpc == "CS":
                scl = "BTEC-Single"
                grd1, grd2 = np.random.choice(["D", "M", "P"],
                                              size=2)
            else:
                scl = "A-Level"
                grd1, grd2 = np.random.choice(["A", "B", "C"], size=2)
            sat.insert({
                "_from": f'students/{st_id}',
                "_to": f'assessments/{sbj}-ass1',
                "grade": grd1,
            })
            sat.insert({
                "_from": f'students/{st_id}',
                "_to": f'assessments/{sbj}-ass2',
                "grade": grd2,
            })
            kudos.insert({
                "_from": f'staff/{fullname}',
                "_to": f'students/{st_id}',
                "value": "Curiosity",
                "comment": "Yay"
            })
            concern.insert({
                "_from": f'staff/{fullname}',
                "_to": f'students/{st_id}',
                "category": "Academic",
                "comment": "Oh no"
            })
if __name__ == "__main__":
    build_db()
