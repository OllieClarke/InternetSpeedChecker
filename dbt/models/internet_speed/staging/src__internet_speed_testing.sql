--Just bring in the proper json from the reformatted upload
select
    parse_json(json)as json,
   __uploaded
from {{ source('internet_speed_testing', 'INTERNET_SPEED_TEST') }}
where json ILIKE '%"Type": "result"%'
OR json ILIKE '%"Type":"result"%'