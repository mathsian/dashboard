with outcomes as (
select
    [Student ID] student_id
    , [Given name] given_name
    , [Family name] family_name
    , [Cohort] cohort
    , [Employer] employer
    , [Start date] start_date
    , [Hybrid end date] end_date
    , [Status] status
    , dense_rank() over (partition by [Student ID] order by [Enrolment year] desc, case Status
        when 'Continuing' then 0
        when 'Break in learning' then 1
        when 'Withdrawn' then 2
        when 'Internal transfer' then 3
        else 4 end) rank
from reports.dash.vw_ap_outcomes)
select
    outcomes.*
    , trim(STYR_Personal_Tutor) skills_coach
from outcomes
left join remslive.dbo.STYRstudentYR on STYR_Year = iif(month(getdate()) < 8, year(getdate()) - 1, year(getdate())) and STYR_Student_ID = student_id
where rank = 1;
