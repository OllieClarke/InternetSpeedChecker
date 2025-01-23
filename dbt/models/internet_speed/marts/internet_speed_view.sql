{{
    config(
        materialized='view'
    )
}}
select
    ROUND(Download, 2) as Download_Mb
    , ROUND(Upload, 2) as Upload_Mb
    , ROUND(Ping, 2) as Ping
    , DATE_TRUNC('second', Timestamp) as Timestamp
    , ROUND(Received, 2) as Mb_Received
    , ROUND(Sent, 2) as Mb_Sent
FROM {{ ref('parsed_internet_speed_testing') }}