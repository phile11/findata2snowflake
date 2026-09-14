with snapshot_data as (
    select * from {{ ref('snp_company') }}
),

transformed_data as (
    select
        --Generated Surrogate Primary Key
        {{ dbt_utils.generate_surrogate_key(['symbol', 'dbt_valid_from']) }} as company_key,
        
        symbol,
        company_name,
        cik,
        isin,
        cusip,
        exchange_code as exchange,
        sector,
        industry,
        ipo_date,
        coalesce(is_etf, false) as is_etf,
        coalesce(is_actively_trading, false) as is_actively_trading,
        coalesce(is_adr, false) as is_adr,
        coalesce(is_fund, false) as is_fund,
        
        --SCD Type 2 Audit Columns
        dbt_valid_from as valid_from,
        coalesce(dbt_valid_to, '9999-12-31'::timestamp) as valid_to,
        case when dbt_valid_to is null then true else false end as is_current
    from snapshot_data
)

select * from transformed_data