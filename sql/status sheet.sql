with ap_enrolments as (select
                           concat_ws('-', trim(STEN_Provision_Code), STEN_Provision_Instance) Provision
                            , format(STEM_Start_Date, 'yyyy-MM') Start_Date
                            , StandardName
                            , case
                                when styr_age_end_aug < 18 then '<18'
                                when styr_age_end_aug = 18 then '18'
                                when styr_age_end_aug > 18 then '19+'
                            end Age
                       , case
                           when STEN_Completion_Stat = 1 then 'Continuing'
                       when STEN_Completion_Stat = 6 then 'Break in learning'
                       when STEN_Completion_Stat = 3 then 'Withdrawn'
                       when STEN_Completion_Stat = 2 then 'Completed'
                       else 'Unknown'
                       end Status
                       from remslive.dbo.STEN
                                left join remslive.dbo.STEM on STEN.STEN_Student_ID = STEM.STEM_Student_ID and
                                                               STEN.STEN_Provision_Code = STEM.STEM_Provision_Code and
                                                               STEN.STEN_Provision_Instance =
                                                               STEM.STEM_Provision_Instance
                                left join remslive.dbo.STUDstudent on STEM.STEM_Student_ID = STUDstudent.STUD_Student_ID
                       left join lars.dbo.Core_LARS_Standard on STEM_Apprenticeship_Standard = Core_LARS_Standard.StandardCode
                       left join remslive.dbo.styrstudentyr on sten_year = styr_year and sten_student_id = styr_student_id
                       where STEN_Year = iif(month(getdate()) < 8, year(getdate()) - 1, year(getdate()))
                         and STEN_Funding_Stream = 36
                         and (STEN_Completion_Stat <> '3' or STEN_Reason_ended <> 40)
                         and STEM_Aim_Type = 1)
select
    iif(grouping(Start_Date) = 1, 'All start dates', Start_Date) Start
    , iif(grouping(StandardName) = 1, 'All standards', StandardName) Standard
    , iif(grouping(Provision) = 1, 'All provisions', Provision) Provision
    , iif(grouping(Age) = 1, 'All ages', Age) "Age at end of August"
    , iif(grouping(Status) = 1, 'All status', Status) Status
    , count(*) Count
from ap_enrolments
group by cube (Start_Date, StandardName, Provision, Age, Status)
order by Start, Provision, Age, Status;
