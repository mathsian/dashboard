with outcomes as (
select
    [Student ID] student_id
    , [Given name] given_name
    , [Family name] family_name
    , [Cohort] cohort
    , isnull([Employer], 'No employer') employer
    , [Skills coach] skills_coach
    , [Start date] start_date
    , isnull([Actual end date], [Planned end date]) end_date
    , [Status] status
    , dense_rank() over (partition by [Student ID] order by [Enrolment year] desc, case Status
        when 'Continuing' then 0
        when 'Break in learning' then 1
        when 'Withdrawn' then 2
        when 'Internal transfer' then 3
        else 4 end) latest
    , dense_rank() over (partition by [Student ID] order by [Enrolment year], case Status
        when 'Continuing' then 4
        when 'Break in learning' then 3
        when 'Withdrawn' then 2
        when 'Internal transfer' then 1
        else 0 end) earliest
from reports.dash.vw_ap_outcomes)
select
    latest_outcomes.student_id
    , latest_outcomes.given_name
    , latest_outcomes.family_name
    , latest_outcomes.cohort
    , latest_outcomes.employer
    , earliest_outcome.start_date
    , latest_outcomes.end_date
    , latest_outcomes.status
	, latest_outcomes.skills_coach
from outcomes as latest_outcomes
left join outcomes as earliest_outcome on latest_outcomes.student_id = earliest_outcome.student_id and earliest_outcome.earliest = 1
where latest_outcomes.latest = 1;
