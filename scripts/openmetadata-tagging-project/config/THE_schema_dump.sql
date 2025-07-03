-- script to dump all tables, views and materialized views from THE schema in either DBQ01 or DBP01

SELECT 'TABLE' as object_type, table_name as object_name
FROM all_tables
UNION ALL 
SELECT 'VIEW', view_name
FROM all_views
UNION ALL
SELECT 'MATERIALIZED VIEW', mview_name 
FROM all_mviews