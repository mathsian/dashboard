select
    [Student ID] student_id
    , [Given name] given_name
    , [Family name] family_name
    , [Cohort] cohort
    , [Employer] employer
    , [Start date] start_date
    , [Hybrid end date] end_date
    , trim(STYR_Personal_Tutor) skills_coach
    , [Status] status
from reports.dash.vw_ap_outcomes
left join remslive.dbo.STYRstudentYR on STYR_Year = iif(month(getdate()) < 8, year(getdate()) - 1, year(getdate())) and STYR_Student_ID = [Student ID];
