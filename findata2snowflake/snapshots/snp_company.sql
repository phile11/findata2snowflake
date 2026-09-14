{% snapshot snp_company %}

{{
    config(
      target_schema='snapshots',
      unique_key='symbol',
      strategy='check',
check_cols=['company_name', 'exchange_code','sector', 'industry', 'is_actively_trading', 'is_etf', 'is_adr', 'is_fund'],
    )
}}

select
    symbol,
    company_name,
    cik,
    isin,
    cusip,
    exchange_code,
    sector,
    industry,
    ipo_date,
    is_etf,
    is_actively_trading,
    is_adr,
    is_fund
from {{ source('raw_data', 'COMPANY_PROFILES') }}

{% endsnapshot %}