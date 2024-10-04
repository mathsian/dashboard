-- all apprentices latest cohort and status
with enrolments as (
-- ranked app enrolments
    select STEM_Student_ID                                                                   student_id
         , STEM_Provision_Code                                                               code
         , STEM_Provision_Instance                                                           instance
         , sten_year                                                                         year
         , STEN_Reason_ended                                                                 reason
         , STEN_Completion_Stat                                                              completion_stat
         , convert(varchar, min(STEM_Start_Date) over (partition by STEM_Student_ID), 23)    start_date
         , convert(varchar, case when sten_completion_stat in (1, 6) then stem_expctd_end_date
             else STEN_Actual_End_Date end, 23)                                              end_date
         , row_number() over (partition by STEM_Student_ID order by STEN_Year desc, STEM_Start_Date desc) as rank
    from remslive.dbo.STEM
             left join remslive.dbo.sten on sten_isn = (select top 1 STEN_ISN
                                                        from REMSLive.dbo.STEN
                                                        where STEM.STEM_Student_ID = STEN.STEN_Student_ID
                                                          and STEM.STEM_Provision_Code = STEN.STEN_Provision_Code
                                                          and STEM.STEM_Provision_Instance = STEN.STEN_Provision_Instance
                                                        order by sten_year desc)
    where STEM_Aim_Type = 1
      and STEN_Funding_Stream = 36
      and sten_reason_ended <> '40')
select
    cast(student_id as integer) student_id
    , trim(case
        when STUD_Forename_1 like 'XXX%' then ''
        when STUD_Known_As = '' then STUD_Forename_1
        else STUD_Known_As
      end) given_name
    , trim(STUD_Surname) family_name
    , concat(trim(code), '-', trim(instance)) cohort
    , isnull(CMPN_Company_Name, 'No employer') employer
    , start_date
    , end_date
    , trim(STYR_Personal_Tutor) skills_coach
    , case
               when completion_stat = 1 and year < iif(month(getdate()) < 8, year(getdate()) - 1, year(getdate()))
                   then 'Withdrawn (stale)'
               when completion_stat = 1 then 'Continuing'
               when completion_stat = 3 and reason = 40 then 'Transferred'
               when completion_stat = 3 then 'Withdrawn'
               when completion_stat = 2 then 'Completed'
               when completion_stat = 6 and year < iif(month(getdate()) < 8, year(getdate()) - 1, year(getdate()))
                    then 'Withdrawn (overdue)'
               when completion_stat = 6 then 'Break in learning'
               else 'Unknown'
        end                        status
from enrolments
left join remslive.dbo.STUDstudent on student_id = STUD_Student_ID
left join remslive.dbo.STESLearnerEmpStatus on stes_isn = (select top 1 stes_isn from remslive.dbo.STESLearnerEmpStatus
where student_id = STES_Student_ID
order by STES_Year desc, STES_DateEmpStatApp desc)
left join remslive.dbo.CMPN_Company_main on STESLearnerEmpStatus.STES_EmpId = CMPN_Company_main.CMPN_Company_Code
left join remslive.dbo.STYRstudentYR on STYR_Year = iif(month(getdate()) < 8, year(getdate()) - 1, year(getdate())) and STYR_Student_ID = student_id
where rank = 1;
