with marks as (

    select
    trim(REGT_Student_ID)                                    student_id
    , format(REGS_Session_Date, 'yyyy-MM-dd')                session_date
    , format(REGS_Start_Time, 'HH:mm')                       session_time
    , regt_Provision_Code                                    provision_code
    , REGT_Provision_Instance                                provision_instance
    , cast(RGAT_Actual as tinyint)                           actual
    , cast(RGAT_Possible as tinyint)                         possible
    , cast(IIF(REGD_Attendance_Mark = 'L', 1, 0) as tinyint) late

 --registers
from remslive.dbo.REGHrghdr

--register sessions
inner join  remslive.dbo.REGSrgsessn
on REGH_ISN = REGS_REGH_ISN

--student registers
left join [REMSLive].[dbo].[REGTrgstudt]
on REGT_REGH_ISN=REGH_ISN
and REGS_Session_Date>=REGT_Start_Date
and (REGS_Session_Date <=REGT_End_Date or REGT_End_Date is null)

--student register marks
left join remslive.dbo.REGDropin
on REGD_Student_ID=REGT_Student_ID
and REGD_REGH_ISN=REGH_ISN
and REGD_Session_No=REGS_Session_No

--register marks meaning
left join remslive.dbo.RGATAttendance
on REGD_Attendance_Mark = RGAT_Attendance_Code

--provision
left join  [REMSLive].[dbo].[PRPIProvisionInstance]
on PRPI_Code=isnull(REGT_Provision_Code,REGH_Provision_Code)
and PRPI_Instance=isnull(REGT_Provision_Instance,regh_provision_instance)

--Provision Annual ILR for funding stream if STEN is null
left join [REMSLive].[dbo].[PRILILR]
on PRIL_Code=PRPI_Code
and PRIL_Instance=PRPI_Instance
and PRIL_Year=REGH_Year

where PRIL_Funding_A10 = '36' and RGAT_Attendance_Code is not null
),
all_time_attendance as (
    select
        student_id
        , sum(possible) sessions
        , sum(actual) present
        , sum(late) late
        , round(100 * cast(sum(Actual) as float) / cast(nullif(sum(Possible),0) as float), 1) attendance
        , 100 - round(100 * cast(sum(late) as float) / cast(nullif(sum(Actual),0) as float), 1) punctuality
    from marks
    group by student_id
),
ninety_days_attendance as (
    select
        student_id
        , sum(possible) sessions
        , sum(actual) present
        , sum(late) late
        , round(100 * cast(sum(Actual) as float) / cast(nullif(sum(Possible), 0) as float), 1) attendance
        , 100 - round(100 * cast(sum(late) as float) / cast(nullif(sum(Actual), 0) as float), 1) punctuality
    from marks
    where datediff(dd, session_date, getdate()) < 91
    group by student_id
)
select
    m.student_id "Student ID"
    , CMPN_Company_Name "Employer"
    , iif(STUD_Known_As = '', STUD_Forename_1, stud_known_as) "Given name"
    , stud_surname                                          "Family name"
    , concat_ws('-', trim(Provision_Code), trim(Provision_Instance)) Cohort
    , all_time_attendance.sessions "All time sessions"
    , all_time_attendance.present "All time present"
    , all_time_attendance.late "All time late"
    , all_time_attendance.attendance "All time attendance (%)"
    , all_time_attendance.punctuality "All time punctuality (%)"
    , ninety_days_attendance.sessions "90 day sessions"
    , ninety_days_attendance.present "90 day present"
    , ninety_days_attendance.late "90 day late"
    , ninety_days_attendance.attendance "90 day attendance (%)"
    , ninety_days_attendance.punctuality "90 day punctuality (%)"
from (select distinct student_id, provision_code, provision_instance from marks)  m
left join all_time_attendance on m.student_id = all_time_attendance.student_id
left join ninety_days_attendance on m.student_id = ninety_days_attendance.student_id
-- for learner
left join remslive.dbo.STUDstudent on m.student_id = STUD_Student_ID
-- for enrolment
left join remslive.dbo.STEM on STEM_Provision_Code = Provision_Code
                                   and STEM_Provision_Instance = Provision_Instance
                                   and STEM_Student_ID = m.Student_ID
                                   and STEM_Aim_Type = 1
-- for status
left join remslive.dbo.STEN on sten_isn = (select top 1 sten_isn from remslive.dbo.sten
                                            where STEN_Student_ID = STEM_Student_ID
                                            and STEN_Provision_Instance = STEM_Provision_Instance
                                            and STEN_Provision_Code = STEM_Provision_Code
                                            and STEN_Reason_ended <> 40
                                            order by sten_year desc, sten_isn desc)
-- for employer
left join REMSLive.dbo.STESLearnerEmpStatus
    on STES_Student_ID = m.Student_ID
    and STES_ISN = (select max(u.stes_ISN) from remslive.dbo.STESLearnerEmpStatus as u
                         where u.STES_Student_ID = m.Student_ID
                         and u.stes_empid is not null)
left join REMSLive.dbo.CMPN_Company_main
    on STES_EmpId = CMPN_Company_Code
where STEN_Completion_Stat = 1
and CMPN_Company_Name = '{{employer}}'
and ('{{cohort}}' = 'All' or concat_ws('-', trim(Provision_Code), trim(Provision_Instance)) = '{{cohort}}');
