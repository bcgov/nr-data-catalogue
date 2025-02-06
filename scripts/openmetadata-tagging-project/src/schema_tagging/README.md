The scripts in this folder should be run in the following order within the pipenv shell or development environment. These should only be run after `main.py`. Some of the scripts have descriptions and comments embedded in them for more context.

1. To populate CONSEP schema assets only:

- To run in dry-run mode:
  ```
  python src/schema_tagging/consep_schema.py --dry-run
  ```

- To apply tags to the CONSEP schema:
  ```
  python src/schema_tagging/consep_schema.py
  ```
2. To populate remaning apps that have distinct schema names that are not CONSEP or FTA:

  a. A mapping JSON file needs to be create prior to running the main script:
   - To run:
     ```
     python src/schema_tagging/openmedatadata_mapping_generator.py
     ```

  b. The mapping JSON file will need to be cleaned:
   - To run:
     ```
     python src/schema_tagging/clean_mapping_names.py
     ```
     This renames the application name, removes references to CONSEP/CNS schema and THE schema. In addition it cleans up all occurences of _replication.

  c. Once JSON file created and cleaned then:
   - To run in dry-run mode::
     ```
     python src/schema_tagging/schema_based_omd_tagger.py --dry-run
     ```

   - To apply tags to the CONSEP schema:
     ```
     python src/schema_tagging/consep_schema.py
     ```
3. To populate FTA tables in THE schema only:
   There is a manual process to this process and can likely be improved. Two SQL script need to run against DBP01 (or DBQ01) and ERSPRD1. The results generated need to
   be saved to a CSV from the queries on each DB to the `data` folder.

   - Open your favorite database query tool.
   - Run `er_studio_fta_tables_views.sql`. Save results to CSV.
   - Run `THE_schema_dump.sql`. Save results to CSV.

   The next step to create the CSV referenced in the `fta_tagger_csv.py` script. The following script will compare the two CSV files created in the previous step.
   - To run:
     ```
     python src/schema_tagging/fta_tagging/fta_matched.py
     ```
   
   Once the CSV has been created the FTA tagging script can be run.
   - To run in dry-run mode::
     ```
     python src/schema_tagging/fta_tagging/fta_tagger_csv.py --dry-run
     ```

   - To apply tags to the THE (FTA tables only) schema:
     ```
     python src/schema_tagging/fta_tagging/fta_tagger_csv.py
     ```

This is not perfect and will need to be refactored. The desire was to have the process and scripts where anyone could access them. Ideally `main.py` would run everything in a sequenced order. Currently there is no test for the scripts in the `schema_tagging` folder.
