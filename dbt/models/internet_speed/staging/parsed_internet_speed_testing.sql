select
    (json:Download:bytes::Float / (json:Download:elapsed::Float / 1000) / 1000000 ) * 8 as Download
    , (json:Upload:bytes::Float / (json:Upload:elapsed::Float / 1000) / 1000000 ) * 8  as Upload
    , json:Ping:high::Float as Ping
    , date_trunc('second',json:Timestamp::Timestamp) as Timestamp
    , json:Download:bytes::Float / 1000000 as Received
    , json:Upload:bytes::Float / 1000000 as Sent
from {{ ref('src__internet_speed_testing') }}