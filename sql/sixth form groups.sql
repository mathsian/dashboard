select
    student_id
    , aim subject_name
    , aim_code aim
    , trim(provision_code) subject_code
    , year_of_student
from reports.dash.vw_sf_outcomes
where enrolment_year = iif(month(getdate()) < 8, year(getdate()) - 1, year(getdate()))
and completion in ('continuing', 'completed');