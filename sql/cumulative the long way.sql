select
  isnull(t.REGT_Student_ID, 'All') student_id
  , isnull(format(t.Month_Start, 'yyyy-MM'), 'Year') date
  , t.attendance attendance
  , round(100 * 
  cast (sum(t.present) over (
  partition by t.REGT_Student_Id, case when t.Month_Start is null then 0 else 1 end order by t.Month_Start) as float) 
  / cast (sum(t.possible) over (
  partition by t.REGT_Student_Id, case when t.Month_Start is null then 0 else 1 end order by t.Month_Start) as float), 1) cumulative
  from (
    select
	s.Month_start
    , s.REGT_Student_Id
    , sum(s.RGAT_Present) present
    , sum(s.RGAT_Possible) possible
	, round(
	100*
	cast(sum(s.RGAT_Present) as float) /
	cast(sum(s.RGAT_Possible) as float)
	, 1) attendance
    from (
      select
        REGH_Year
        ,cast(case when datepart(mm,getdate())<8 then datepart(yyyy,getdate())-1
      else datepart(yyyy,getdate())
      end as smallint) CurrentYear
        ,REGH_ISN --Register ID
        ,REGS_ISN -- Register Session ID
        ,REGH_Register_Title
        ,REGH_Class_Register

        --register start and end date
        ,REGH_Start_Time
        ,REGH_End_Time
        ,REGH_Duration --duration in minutes
        ,REGS_Session_No
        ,regt_isn -- student register ID
        ,STEN_ISN -- student enrolment ID
        ,REGT_Start_Date --register start date
        ,REGT_End_Date -- register end date
        ,trim(REGT_Student_ID)REGT_Student_ID
        ,isnull(STEN_Provision_Code,REGT_Provision_Code) Provision_Code
        ,isnull(STEN_Provision_Instance,REGT_Provision_Instance) Provision_Instance
        ,PRPI_Title  Provision_Title
        ,REGD_Attendance_Mark
        ,REGS_Session_Date -- mark date
        ,DATEADD(dd, (REGS_Session_No - 1) * 7, CCAL_Acad_Start) AS Wk_Start

        ,cast(DATEFROMPARTS(YEAR(REGS_Session_Date),MONTH(REGS_Session_Date),1) as datetime) Month_Start
        ,datepart(dw,regs_session_Date) DW_Order
        ,datename(dw,regs_session_Date) DW_Name
        ,cast(RGAT_Actual as tinyint) RGAT_Actual
        ,case when RGAT_Present='Y' then 1 else 0 end RGAT_Present
        ,cast(RGAT_Possible as tinyint) RGAT_Possible
        ,cast(case when REGD_Attendance_Mark='L' then 1 else 0 end as tinyint) Late
        ,cast(case when REGD_Attendance_Mark is null then 1 else 0 end as tinyint)MissingMark
        ,cast(case when REGD_Attendance_Mark='U' then 1 else 0 end as tinyint) Unauthorised
        ,cast(case when REGD_Attendance_Mark='N' then 1 else 0 end as tinyint) NotPresent

        ,cast(case when RGAT_Possible=1 and RGAT_Present='N' and REGD_Attendance_Mark not in ('U','N') then 1 else 0 end as tinyint) Authorised
        ,case when regt_student_id in (select STEN_Student_ID  from remslive.dbo.sten where STEN_Completion_Stat='1' and sten_year = REGH_Year ) then 1 else 0 end LiveStu
        ,case when isnull(sten_funding_stream,[PRIL_Funding_A10])='36' then 'AP' else 'SF'end StuType
        ,case when REGS_Session_Date <= getdate() then 1 else 0 end Past
        ,case when REGS_Session_Date between [CCAL_Autumn_Term_Start] and [CCAL_Autumn_1st_Half_End] then 'HT1'
      when REGS_Session_Date between [CCAL_Autumn_2nd_Half_Start] and [CCAL_Autumn_2nd_Half_End] then 'HT2'
      when REGS_Session_Date between [CCAL_Spring_Term_Start] and [CCAL_Spring_1st_Half_End] then 'HT3'
      when REGS_Session_Date between [CCAL_Spring_2nd_Half_Start] and [CCAL_Spring_2nd_Half_End] then 'HT4'
      when REGS_Session_Date between [CCAL_Summer_Term_Start] and [CCAL_Summer_1st_Half_End] then 'HT5'
      when REGS_Session_Date between [CCAL_Summer_2nd_Half_Start] and [CCAL_Summer_2nd_Half_End] then 'HT6'
      else 'Holiday'
      end Term
      ,case when REGS_Session_Date=convert(datetime,convert(varchar(10),getdate(),103),103) then 1 else 0 end Today
      ,case when datediff(dd,DATEADD(dd, (REGS_Session_No - 1) * 7, CCAL_Acad_Start),getdate()) between 0 and 6 then 1 else 0 end This_Wk


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

      --enrolments
      left join REMSLive.dbo.STEN
      on STEN_Student_ID=REGT_Student_ID
      and STEN_Provision_Code=REGT_Provision_Code
      and STEN_Provision_Instance=REGT_Provision_Instance
      and STEN_Year=REGH_Year

      --provision
      left join  [REMSLive].[dbo].[PRPIProvisionInstance]
      on PRPI_Code=isnull(REGT_Provision_Code,REGH_Provision_Code)
      and PRPI_Instance=isnull(REGT_Provision_Instance,regh_provision_instance)

      --Provision Annual ILR for funding stream if STEN is null
      left join [REMSLive].[dbo].[PRILILR]
      on PRIL_Code=PRPI_Code
      and PRIL_Instance=PRPI_Instance
      and PRIL_Year=REGH_Year

      --academic year calendar
      left join [REMSLive].[dbo].[CCALCalend]
      on REGH_Year=CCAL_Year

	  where REGH_Year = '2020'
      ) s
	  where  StuType = 'SF'
	  and s.RGAT_Possible = 1
	  group by cube(month_start, REGT_Student_ID)
	  
) t
order by t.REGT_Student_ID, t.Month_Start
