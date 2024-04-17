with learners as (
    SELECT
        trim(STUD_Student_ID) student_id
    from remslive.dbo.STUDstudent
    -- for skills coach
    left join remslive.dbo.STYRstudentYR on styr_year = iif(month(getdate()) < 8, year(getdate()) - 1, year(getdate()))
        and STYR_Student_ID = STUD_Student_ID
    where trim(STYR_Personal_Tutor) = '{{tsc}}'
     ),
attendance_marks as (
    select
    student_id
    , format(REGS_Session_Date, 'yyyy-MM-dd')                session_date
    , format(REGS_Start_Time, 'HH:mm')                       session_time
    , regt_Provision_Code                                    provision_code
    , REGT_Provision_Instance                                provision_instance
    , cast(RGAT_Actual as tinyint)                           actual
    , cast(RGAT_Possible as tinyint)                         possible
    , cast(IIF(REGD_Attendance_Mark = 'L', 1, 0) as tinyint) late

    from learners

    --student registers
    left join remslive.dbo.REGTrgstudt
        on trim(REGT_Student_ID) = learners.student_id
    left join remslive.dbo.REGHrghdr
        on REGTrgstudt.REGT_REGH_ISN = REGHrghdr.REGH_ISN

    left join remslive.dbo.REGSrgsessn
        on REGHrghdr.REGH_ISN = REGSrgsessn.REGS_REGH_ISN

    left join remslive.dbo.REGDropin
        on REGSrgsessn.REGS_REGH_ISN = REGDropin.REGD_REGH_ISN AND REGSrgsessn.REGS_Session_No = REGDropin.REGD_Session_No and REGDropin.REGD_Student_ID = REGTrgstudt.REGT_Student_ID

    left join remslive.dbo.RGATAttendance
        on REGDropin.REGD_Attendance_Mark = RGATAttendance.RGAT_Attendance_Code

    --provision
    left join  [REMSLive].[dbo].[PRPIProvisionInstance]
    on PRPI_Code=isnull(REGT_Provision_Code,REGH_Provision_Code)
    and PRPI_Instance=isnull(REGT_Provision_Instance,regh_provision_instance)

    --Provision Annual ILR for funding stream in case STEN is null
    left join [REMSLive].[dbo].[PRILILR]
    on PRIL_Code=PRPI_Code
    and PRIL_Instance=PRPI_Instance
    and PRIL_Year=REGH_Year

    where PRIL_Funding_A10 = '36'
      and RGAT_Attendance_Code is not null
      and REGS_Session_Date>=REGT_Start_Date
      and (REGS_Session_Date <=REGT_End_Date or REGT_End_Date is null)

),
all_time_attendance as (
    select
        student_id
        , sum(possible) sessions
        , sum(actual) present
        , sum(late) late
        , round(100 * cast(sum(Actual) as float) / cast(nullif(sum(Possible), 0) as float), 1) attendance
        , 100 - round(100 * cast(sum(late) as float) / cast(nullif(sum(Actual), 0) as float), 1) punctuality
    from attendance_marks
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
    from attendance_marks
    where datediff(dd, session_date, getdate()) <= 90
    group by student_id
)
select
    cast(learners.student_id as int) "Student ID"
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
from learners
left join all_time_attendance on learners.student_id = all_time_attendance.student_id
left join ninety_days_attendance on learners.student_id = ninety_days_attendance.student_id;