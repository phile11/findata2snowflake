{{
    config(
        unique_key='date_day'
    )
}}

with full_date_spine as (
    -- Generates timeline of days
    {{ dbt_date.get_date_dimension("2015-01-01", "2030-12-31") }}
),

trading_holidays as (
    select * from {{ ref('trading_holidays') }}
),

final_calculations as (
    select
        -- Standard Calendar Fields
        fds.date_day,
        fds.year_number,
        fds.month_of_year as month_number,
        fds.day_of_month,
        fds.day_of_week,
        fds.day_of_week_name as day_name,

        -- Define if weekend day
        case 
            when dayofweek(fds.date_day) in (0, 6) then true
            else false 
        end as is_week_end,
                    
        -- Defining trading schedule
        case
            when dayofweek(fds.date_day) in (0, 6) then false
            when th.is_trading_closed = true then false
            else true
        end as is_trading_day
    from full_date_spine fds
    left join trading_holidays th 
        on fds.date_day = th.holiday_date
),

trading_sequences as (
    -- Adds chronological sequences (e.g., T+1, T+2 logic) ignoring closures 
    select
        *,
        case 
            when is_trading_day then 
                row_number() over (partition by is_trading_day order by date_day)
            else null 
        end as trading_day_sequence,
    from final_calculations
)

select * from trading_sequences