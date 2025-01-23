--heavily inspired by https://gist.github.com/jeremyyeo/67f07c06c4cc6943838e7262728e3f7a
{% test freshness(model, timestamp_field, warn_after=none, error_after=none) -%}
 {% if warn_after and error_after -%}
    {{ config(warn_if='=1', error_if='=2') }}

    with max_timestamp as (
        select max({{ timestamp_field }}) as max_loaded_at
        from {{ model }}
    ),
    current_time as (
        select sysdate() as now
    ),
     check_conditions as (
        select
            max_loaded_at,
            now,
            'warn' as condition,
            datediff({{warn_after.period}}, max_loaded_at, now) as since_last_load
        from max_timestamp, current_time
        union
        select
            max_loaded_at,
            now,
            'error' as condition,
            datediff({{error_after.period}}, max_loaded_at, now) as since_last_load
        from max_timestamp, current_time
    )
    , check_against as(
        select
            'warn' as condition
            , {{warn_after.count}}::number as amount
        union
        select
            'error' as condition
            , {{error_after.count}}::number as amount
    )
    , output_check as(
    select *
    from check_conditions a
    join check_against b on a.condition = b.condition
    where since_last_load > amount)

{% elif warn_after -%}
    {{ config(warn_if='=1', error_if='=2') }}

    with max_timestamp as (
        select max({{ timestamp_field }}) as max_loaded_at
        from {{ model }}
    ),
    current_time as (
        select sysdate() as now
    ),
     check_conditions as (
        select
            max_loaded_at,
            now,
            'warn' as condition,
            datediff({{warn_after.period}}, max_loaded_at, now) as since_last_load
        from max_timestamp, current_time
    )
    , output_check as(
    select *
    from check_conditions
    where since_last_load > {{warn_after.count}}::Number)

{% elif error_after -%}
    {{ config(error_if='=1') }}

    with max_timestamp as (
        select max({{ timestamp_field }}) as max_loaded_at
        from {{ model }}
    ),
    current_time as (
        select sysdate() as now
    ),
     check_conditions as (
        select
            max_loaded_at,
            now,
            'error' as condition,
            datediff({{error_after.period}}, max_loaded_at, now) as since_last_load
        from max_timestamp, current_time
    )
    , output_check as(
    select *
    from check_conditions
    where since_last_load > {{error_after.count}}::Number)

{% else -%}
    {% do exceptions.raise_compiler_error('Freshness test applied to model ' ~ model ~ 'but missing warn_after/error_after configs.') %}
{% endif -%}

select * from output_check

{%- endtest -%}