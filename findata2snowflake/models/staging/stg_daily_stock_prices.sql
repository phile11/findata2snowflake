with stock_prices as (
    select * from {{ source('raw_data', 'daily_stock_prices') }}
)
select
    date,
    symbol,
    open_price,
    high_price,
    low_price,
    close_price,
    vwap,
    volume,
    price_change,
    price_change_percent
from stock_prices