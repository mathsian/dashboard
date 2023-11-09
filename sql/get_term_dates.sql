with this_year AS (
    select * from remslive.dbo.CCALCalend where ccal_year = iif(month(getdate()) < 8, year(getdate()) - 1, year(getdate()))
     )
select top 1
    ccal_year year
     , format(year_start, 'yyyy-MM-dd') year_start
     , term
     , format(term_start, 'yyyy-MM-dd') term_start
     , half_term
     , format(half_term_start, 'yyyy-MM-dd') half_term_start
from this_year
CROSS APPLY
    (
        select
            this_year.CCAL_Acad_Start year_start
            , 'Autumn' term
            , this_year.CCAL_Autumn_Term_Start term_start
            , 'Autumn 1' half_term
            , this_year.CCAL_Autumn_Term_Start half_term_start
        union ALL
        select
            this_year.CCAL_Acad_Start year_start
            , 'Autumn' term
            , this_year.CCAL_Autumn_Term_Start term_start
            , 'Autumn 2' half_term
            , this_year.CCAL_Autumn_2nd_Half_Start half_term_start
        union ALL
                select
            this_year.CCAL_Acad_Start year_start
            , 'Spring' term
            , this_year.CCAL_Spring_Term_Start term_start
            , 'Spring 1' half_term
            , this_year.CCAL_Spring_Term_Start half_term_start
        union ALL
                select
            this_year.CCAL_Acad_Start year_start
            , 'Spring' term
            , this_year.CCAL_Spring_Term_Start term_start
            , 'Spring 2' half_term
            , this_year.CCAL_Spring_2nd_Half_Start half_term_start
        union ALL
                select
            this_year.CCAL_Acad_Start year_start
            , 'Summer' term
            , this_year.CCAL_Summer_Term_Start term_start
            , 'Summer 1' half_term
            , this_year.CCAL_Summer_Term_Start half_term_start
        union ALL
                select
            this_year.CCAL_Acad_Start year_start
            , 'Summer' term
            , this_year.CCAL_Summer_Term_Start term_start
            , 'Summer 2' half_term
            , this_year.CCAL_Summer_2nd_Half_Start half_term_start
    ) cal
where half_term_start <= getdate()
order by Half_Term_Start desc;