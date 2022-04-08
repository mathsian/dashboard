-- apprentice cohorts
with enrolments as (
-- ranked app enrolments
    select trim(STEM_Student_ID)                                                                   student_id
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
) select distinct concat(trim(code),'-',trim(instance))  cohort
from enrolments;
