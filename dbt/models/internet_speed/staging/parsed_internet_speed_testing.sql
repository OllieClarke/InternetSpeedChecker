--dealing with the two types of json structure
with src as(
    select * from {{ ref('src__internet_speed_testing') }}
)

--first the old style
, old as(
select
    (json:Download:bytes::Float / (json:Download:elapsed::Float / 1000) / 1000000 ) * 8 as Download
    , (json:Upload:bytes::Float / (json:Upload:elapsed::Float / 1000) / 1000000 ) * 8  as Upload
    , json:Ping:high::Float as Ping
    , date_trunc('second',json:Timestamp::Timestamp) as Timestamp
    , json:Download:bytes::Float / 1000000 as Received
    , json:Upload:bytes::Float / 1000000 as Sent
from src
where JSON ILIKE '{"Download":{"bandwidth"%'
)

-- then new style
, new as(
select 
    json:Download::float / 1000000 as Download
    , json:Upload::float / 1000000 as Upload
    , json:Ping::float as Ping
    , date_trunc('second',json:Timestamp::Timestamp) as Timestamp
    , json:Bytes_Received::float / 1000000 as Received
    , json:Bytes_Sent::float /1000000 as Sent
from src
where json:Bytes_Received is not null
)

--combine together 
, comb as(
Select 
    Download
    , Upload
    , Ping
    , Timestamp
    , Received
    , Sent
from old
union all
select
    Download
    , Upload
    , Ping
    , Timestamp
    , Received
    , Sent
from new
)

select * from comb