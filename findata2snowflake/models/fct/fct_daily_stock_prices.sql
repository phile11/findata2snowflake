{{
    config(
        materialized='incremental',
        unique_key=['date_key', 'company_key'],
        incremental_strategy='merge',
        cluster_by=['trade_date']
    )
}}

with stage_data as (
    select * from {{ ref('stg_daily_stock_prices') }}
),
dim_date as (
    select * from {{ ref('dim_date') }}
),
dim_company as (
    select * from {{ ref('dim_company') }}
),
transformed_data as (
    select
        -- Surrogate Keys joining to your Dimensions
        dim_date.date_key as date_key,
        dim_co.company_key as company_key,
        dim_date.trade_date as trade_date,
        stg.symbol,
        stg.open_price,
        stg.high_price,
        stg.low_price,
        stg.close_price,
        stg.vwap,
        stg.volume,
        stg.price_change,
        stg.price_change_percent,
        -- Metadata
        current_timestamp() as inserted_at,
        current_timestamp() as updated_at

    from stage_data stg
    join dim_date 
        on stg.date = dim_date.trade_date
    join dim_company  dim_co
        on stg.symbol = dim_co.symbol

    {% if is_incremental() %}
    -- Only process new data since the last run to optimize performance
    where stg.date >= (select max(d.trade_date) from {{ this }} f join dim_date d on f.date_key = d.date_key
    {% endif %}
)
select * from transformed_data