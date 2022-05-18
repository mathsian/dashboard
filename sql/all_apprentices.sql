-- all apprentices latest cohort and status
with enrolments as (
-- ranked app enrolments
    select STEM_Student_ID                                                                   student_id
         , STEM_Provision_Code                                                               code
         , STEM_Provision_Instance                                                           instance
         , STEM_Start_Date                                                                   start
         , sten_year                                                                         year
         , STEN_Reason_ended                                                                 reason
         , STEN_Completion_Stat                                                              completion_stat
         , row_number() over (partition by STEM_Student_ID order by STEM_Start_Date desc) as rank
    from remslive.dbo.STEM
             left join remslive.dbo.sten on sten_isn = (select top 1 STEN_ISN
                                                        from REMSLive.dbo.STEN
                                                        where STEM.STEM_Student_ID = STEN.STEN_Student_ID
                                                          and STEM.STEM_Provision_Code = STEN.STEN_Provision_Code
                                                          and STEM.STEM_Provision_Instance = STEN.STEN_Provision_Instance
                                                        order by sten_year desc)
    where STEM_Aim_Type = 1
      and STEN_Funding_Stream = 36
)
select
    cast(student_id as integer) student_id
    , iif(STUD_Known_As = '', STUD_Forename_1, STUD_Known_As) given_name
    , STUD_Surname family_name
    , concat(trim(code), '-', trim(instance)) cohort
    , isnull(CMPN_Company_Name, 'No employer') employer
    , case
               when completion_stat = 1 and year < '2021'
                   then 'Withdrawn'
               when completion_stat = 1 then 'Continuing'
               when completion_stat = 3 and reason = 40 then 'Transferred'
               when completion_stat = 3 then 'Withdrawn'
               when completion_stat = 2 then 'Completed'
               when completion_stat = 6 then 'Break in learning'
               else 'Unknown'
        end                        status
from enrolments
left join remslive.dbo.STUDstudent on student_id = STUD_Student_ID
left join remslive.dbo.STESLearnerEmpStatus on stes_isn = (select top 1 stes_isn from remslive.dbo.STESLearnerEmpStatus
where student_id = STES_Student_ID
order by STES_Year desc, STES_DateEmpStatApp desc)
left join remslive.dbo.CMPN_Company_main on STESLearnerEmpStatus.STES_EmpId = CMPN_Company_main.CMPN_Company_Code
where rank = 1;
