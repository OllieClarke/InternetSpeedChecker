# InternetSpeedChecker

![schematic_diagram_of_the_project](./images/project%20diagram.png)

## Background

I wanted to practise an end-to-end analytical engineering project. As I had an unused Raspberry Pi I thought I could use it to check the internet speeds I get in my flat. My plan was to have a python script run on a schedule on the Raspberry Pi, checking my internet speed, then writing its results to a table in Snowflake. I wanted to practise my dbt too, so I was going to keep the data pretty raw in snowflake, and use dbt to parse the data, apply tests and documentation. Finally I'd build a simple dashboard in Tableau linking Tableau and dbt Cloud together via data health tiles and auto-exposures.

#### Mistakes Made

I made a number of mistakes while making this project, and the python script I have now is **very** different from the one I started with.
Originally I used the snowflake.connector python library to insert into a snowflake table my results directly. Running this python script on an aggressive schedule resulted in an unexpectedly high credit spend in snowflake.
Other lessons learned include:

- binding variables to strings to prevent SQL injection
- including logging in bash scripts to demystify why nothing worked
- my ISP doesn't allow port forwarding for remote ssh
- real-time data that is rapidly changing can be expensive to have
- raspbian/buster and debian/buster are similar enough for installing the packages I needed

I also have questions of the accuracy of the results I'm seeing. I haven't worked out yet if this is a hardware limitation on my Raspberry Pi, or if there's a network setting I need to find...

## Extraction

I made use of the [ookla speedtest-cli](https://www.speedtest.net/apps/cli) to get my current internet speed test.
This is very simple to use, I write my results in json format to a text file in my directory (speedoutput.txt).

My bash script, having created a timestamp function for logging and navigated to the correct location, deletes the extant speedoutput.txt, then runs the cli to output a new speedoutput.txt.

### Python

My [python script](script.py) is very simple.

It reads in the created speedoutput.txt and cleans up the json a bit. It also removes some information about my network to sanitise the data.

It then uses the boto3 library to write the cleaned json as a timestamped .json file to an S3 bucket. Writing the data to a staging layer in S3 means that I can still have a very high-granularity data set, without constantly running a warehouse in Snowflake. I write my data to S3 at high-frequency, but I can then injest it to Snowflake at a lower (read cheaper) frequency.

I made a specific AWS Policy, User and S3 Bucket for this project for security and easy monitoring.

### Automating

You can see [the shell script](find-internet-speed.sh) which installs packages, deletes the old output file, runs the cli and then the python script.

In order to automate that script, I used a cronjob on my Raspberry Pi. This was:

```bash
*/15 * * * * /bin/bash /home/pi/InternetSpeedChecker/find-internet-speed.sh 1> /home/pi/log.txt 2>/home/pi/err.txt
```

This command is conceptually in 3 parts:

#### Schedule

```
*/15 * * * *
```

This is a [cron](https://en.wikipedia.org/wiki/Cron) schedule which says run every 15 minutes run the following command...

#### Command

```bash
/bin/bash /home/pi/InternetSpeedChecker/find-internet-speed.sh
```

This says run the [find-internet-speed.sh](find-internet-speed.sh) shell script using bash

#### Logging

```
1> /home/pi/log.txt 2>/home/pi/err.txt
```

This command writes logs of two different kinds.
Firstly I write the messages created by the shell script to a log.txt file (overwriting what was there before).
Secondly I write any error messages created by the shell script to a err.txt file (overwriting what was there before).

## Loading

Once the data is in S3, I can easily pull it into Snowflake.
Originally I was going to use a [Snowpipe](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-intro) to pull in data from my S3 bucket, but for my purposes I don't need real-time data. It's more cost-efficient for me to have a scheduled task which pulls in the new data.

My task is as follows:

```sql
create or replace task input_internet
    warehouse = <warehouse>
    schedule = 'USING CRON 15 9 * * 1-5 Europe/London'
    as
    COPY INTO <table>
      FROM (
            select $1::varchar as JSON
            , METADATA$file_last_modified as __uploaded from
            @OLLIE_INTERNET_SPEED
            where __uploaded > (select max(__uploaded) from <table>)
      )
       file_format = (format_name = json);
```

Again I'm using cron syntax to specify that I want this task to run at 09:15 am (London time) Monday through Friday.

This uses the external stage **OLLIE_INTERNET_SPEED** and file format **json** which I created in order to copy in fresh data from the S3 bucket.

I only want to copy in fresh data, so I use the file_last_modified value as my unique key for incremental loading.
![my_s3_bucket](./images/S3%20Bucket.png)

The reason I cast my json into a varchar is that my table had historic data from when I was loading directly into Snowflake, so I had to align my data types (rather than using variant).

## Transformation

Now I've got the raw(ish) json loaded in Snowflake, I used dbt cloud in order to prepare this data for visualising.

![dbt_lineage](/images/dbt%20lineage.png)

#### Staging

I used a [source model](dbt/models/internet_speed/staging/src__internet_speed_testing.sql) to stage my data. I also only wanted to load in successful speedtests, so I filter out any unsuccessful json results.

I then [parse the json](dbt/models/internet_speed/staging/parsed_internet_speed_testing.sql) to extract the only fields I care about:
|Field | Notes |
|:-----|:------|
|Download|The Download speed in Mbps. Calculated from Download (in bytes) and Elapsed, and converted to bits|
|Upload|The Upload speed in Mbps. Calculated from Upload (in bytes) and Elapsed, and converted to bits|
|Ping|The highest Ping value|
|Timestamp|The timestamp of the speedtest|
|Received|The size of total downloaded megabytes|
|Sent|The size of total uploaded megabytes|

#### Marts

I made 2 models based on this parsed data for use by Tableau.

Firstly I made a [view](dbt/models/internet_speed/marts/internet_speed_view.sql) with the data rounded, and renamed.

I also made an [incremental table](dbt/models/internet_speed/marts/internet_speed_snapshot.sql) with the data rounded, and renamed.

The reason for this duplication was mostly so I could demo the differences and the incremental functionality.

| Final Data  | Description                                            | Data Type |
| :---------- | :----------------------------------------------------- | --------: |
| Download_Mb | The download speed in Mbps rounded to 2 dp             |     Float |
| Upload_Mb   | The upload speed in Mbps rounded to 2 dp               |     Float |
| Ping        | The high ping rounded to 2 dp                          |     Float |
| Timestamp   | The timestamp of the speed test rounded to seconds     |  Datetime |
| Mb_Received | The total data downloaded in megabytes rounded to 2 dp |     Float |
| Mb_Sent     | The total data uploaded in megabytes rounded to 2 dp   |     Float |

#### Tests

I implemented data source freshness tests along with in-built tests of not_null and uniqueness to my source table along with my models.

I also wanted a test which would warn or error based on a timestamp field of a model if the max value was not recent enough.
dbt's freshness checks can only be applied to sources, rather than models, and the tests which I found in packages online tended to compare table-level timestamp field, rather than a row-level timestamp field.

I took heavy inspiration from this [post I found by Jeremy Yeo](https://gist.github.com/jeremyyeo/67f07c06c4cc6943838e7262728e3f7a)
and wrote my own [test for model freshness](dbt/tests/generic/freshness.sql).

#### Jobs

I set up 3 dbt jobs to build my models.

Firstly an incremental build which I scheduled to run every 8 hours during the week:

```
dbt source freshness
dbt build -s source:internet_speed_testing+
dbt docs generate

0 */8 * * 1-5
```

Secondly a full-refresh build to run every Sunday at 8pm:

```
dbt source freshness
dbt build -s source:internet_speed_testing+ --full-refresh
dbt docs generate

0 20 * * 7
```

Finally an hourly test during the week:

```
dbt test -s source:internet_speed_testing+

0 9-17 * * 1-5
```

## Visualisation

I took advantage of dbt's [auto-exposure](https://docs.getdbt.com/docs/collaborate/auto-exposures) capabilities to surface the 2 dashboard's I made in Tableau and add them to my lineage.
![dbt_lineage_with_tableau](images/dbt%20exposures.png)

I also embedded [data health tiles](https://docs.getdbt.com/docs/collaborate/data-tile) in both my dashboards.
![data_health_tile_in_dashboard](images/Data%20Health%20Tile.png)
