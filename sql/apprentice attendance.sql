with marks as (
    select
        rgat_actual Actual
        , rgat_possible Possible
        , Late
        , iif(datediff(dd, REGS_Session_Date, getdate()) <= 90, 1, 0) ninety_day
    from reports.dash.vw_register_marks
    where REGT_Student_ID = '{{student_id}}' and past = 1 and StuType = 'AP'
)
select
        round(100 * cast(sum(Actual) as float) / cast(nullif(sum(Possible), 0) as float), 1) "All time attendance (%)"
        , 100 - round(100 * cast(sum(Late) as float) / cast(nullif(sum(Actual), 0) as float), 1) "All time punctuality (%)"
        , round(100 * cast(sum(Actual * ninety_day) as float) / cast(nullif(sum(Possible * ninety_day), 0) as float), 1) "90 day attendance (%)"
        , 100 - round(100 * cast(sum(Late * ninety_day) as float) / cast(nullif(sum(Actual * ninety_day), 0) as float), 1) "90 day punctuality (%)"
from marks;