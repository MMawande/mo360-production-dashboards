# Databricks notebook source
# MAGIC %md
# MAGIC # Inspektor Failed Data Consolidation
# MAGIC
# MAGIC This notebook consolidates failed data from Inspektor tables into a single consolidated table.
# MAGIC
# MAGIC ## Input Parameters:
# MAGIC - **catalog_schema_name** (MANDATORY): Schema containing Inspektor failed_data tables to be processed
# MAGIC - **failed_data_table_list** (OPTIONAL): Comma separated list of tables containing failed data. If not provided, tables with name **_failed_data will be used
# MAGIC - **record_limit** (OPTIONAL): Count of failed records to be stored for each check_id (default: 100)
# MAGIC - **from_date** (OPTIONAL): Date from which failed data should be processed (format: YYYY-MM-DD). Default is 15 days from current date
# MAGIC - **additional_schema** (OPTIONAL): Schema containing Inspektor failed_data_info table for check run time information
# MAGIC
# MAGIC ## Example Input:
# MAGIC - catalog_schema_name: `westeurope_extollo_platform_it_eu_mbdf_adbv.inspektor_unity_schema_result_case3`
# MAGIC - failed_data_table_list: `products_failed_data, customer_failed_data, rejected_table`
# MAGIC - record_limit: `100`
# MAGIC - from_date: `2024-12-01`
# MAGIC - additional_schema: `westeurope_extollo_platform_it_eu_mbdf_adbv.inspektor_unity_schema_result_info`

# COMMAND ----------

# MAGIC %md
# MAGIC ## Import Required Libraries

# COMMAND ----------
import os
from functools import reduce
from pyspark.sql.functions import *
from pyspark.sql import Window
from pyspark.sql import functions as F
from pyspark.sql.functions import row_number
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from datetime import datetime, timedelta

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Input Widgets

# COMMAND ----------

dbutils.widgets.text("catalog_name", "")
dbutils.widgets.text("catalog_name", "")
dbutils.widgets.text("failed_data_table_list", "")
dbutils.widgets.text("record_limit", "100")
dbutils.widgets.text("from_date (YYYY-MM-DD)", "")
dbutils.widgets.text("additional_schema", "")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Get and Validate Input Parameters

# COMMAND ----------

# Get input parameters from widgets
catalog_name = dbutils.widgets.get("catalog_name")
schema_name = dbutils.widgets.get("schema_name")

if not catalog_name or not schema_name:
    raise ValueError("Both catalog_name and schema_name are required. Please provide values in the respective widgets.")

catalog_schema_name = f"{catalog_name}.{schema_name}"
failed_data_table_list = [item.strip() for item in dbutils.widgets.get("failed_data_table_list").split(',')]
from_date = dbutils.widgets.get("from_date (YYYY-MM-DD)")
additional_schema = dbutils.widgets.get("additional_schema")

# Parse record limit with error handling
try:
    record_limit = int(dbutils.widgets.get("record_limit"))
except ValueError:
    record_limit = 100


# Print input parameters for verification
print('INFO: catalog_schema_name:', catalog_schema_name)
print('INFO: failed_data_table_list:', failed_data_table_list)
print('INFO: record_limit per check:', record_limit)
print('INFO: from_date:', from_date)
print('INFO: additional_schema:', additional_schema)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validate Catalog and Tables

# COMMAND ----------

try:
    # Check if catalog and schema exists
    if spark.catalog.databaseExists(catalog_schema_name):
        print(f"INFO: catalog exists with name : {catalog_schema_name}")
    else:
        raise Exception(f"ERROR: catalog does not exist with name : {catalog_schema_name}")

    # Check all failed data tables exists
    final_table_list = []
    if failed_data_table_list != [''] and len(failed_data_table_list) > 0:
        print("INFO: failed_data_table_list provided. Checking if all tables exists...")
        for table in failed_data_table_list:
            if spark.catalog.tableExists(f"{catalog_schema_name}.{table}"):
                print(f"INFO: table exists with name : {table}")
                final_table_list.append(table)
            else:
                print(f"WARN: table does not exist with name : {table}, skipping from the flow ")
    else:
        # Create failed data table list using schema
        print(
            "INFO: No failed_data_table_list provided. Checking if any **_failed_data table present in the schema. Creating list now...")

        table_list_fetched = spark.catalog.listTables(dbName=catalog_schema_name)
        final_table_list = [table.name for table in table_list_fetched if
                            table.name.endswith("_failed_data") and table.name != "consolidated_failed_data"]

        print("INFO: final_table_list created using schema passed.")

    print("INFO: final_table_list to process: ", final_table_list)

except Exception as e:
    print(f"ERROR: {e}")
    raise e

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configure Date Filtering

# COMMAND ----------

filter_historic_data = False

# Check from_date
if from_date != '':
    print("INFO: from_date provided. Checking if it is valid date...")
    try:
        from_date_dt = datetime.strptime(from_date, '%Y-%m-%d').date()
        print("INFO: from_date : ", from_date_dt)
        filter_historic_data = True
    except ValueError:
        print("ERROR: from_date is not in YYYY-MM-DD format, skipping history filter...")
else:
    print("INFO: No from_date provided. Setting historical filter to last 15 days...")
    from_date_dt = (datetime.now() - timedelta(days=15)).date()
    print("INFO: created from_date : ", from_date_dt)
    filter_historic_data = True

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Failed Data Info Table

# COMMAND ----------

# Check failed_data_info table exists
failed_data_info = []
if filter_historic_data:
    if spark.catalog.tableExists(f"{catalog_schema_name}.failed_data_info"):
        print(
            f"INFO: failed_data_info table found in the {catalog_schema_name}. Using it to get check run time information...")
        failed_data_info = spark.table(f"{catalog_schema_name}.failed_data_info")
    else:
        print("WARN: failed_data_info table not found in the schema. check if additional schema passed...")
        if additional_schema != '':
            if spark.catalog.tableExists(f"{additional_schema}.failed_data_info"):
                failed_data_info = spark.table(f"{additional_schema}.failed_data_info")
                print(
                    f"INFO: failed_data_info table found in the {additional_schema}. Using it to get check run time information...")
            else:
                print(f"WARN: failed_data_info table not found in the {additional_schema}. skipping history filter...")
                filter_historic_data = False
                failed_data_info = None
        else:
            print(
                f"WARN: failed_data_info table not found in the {catalog_schema_name} and additional schema not provided. skipping history filter...")
            filter_historic_data = False
            failed_data_info = None

# COMMAND ----------

# MAGIC %md
# MAGIC ## Early Exit Check - No Tables Found

# COMMAND ----------

if final_table_list == [''] or len(final_table_list) < 1:
    print("INFO: No failed_data table found. Exiting flow now !")
    dbutils.notebook.exit(0)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Filter Checks by Date Range

# COMMAND ----------

if failed_data_info is not None and failed_data_info != []:
    check_to_process_df = failed_data_info.select("check_id", "time") \
        .withColumn("run_date", F.to_date(F.col("time"))) \
        .filter(F.col("run_date") >= from_date_dt).drop("time")  # inclusive of from_date
    display(check_to_process_df)
else:
    check_to_process_df = None

# COMMAND ----------

# Get list of check_ids to process
check_id_list = []
if check_to_process_df is not None:
    check_id_list = [row.check_id for row in check_to_process_df.collect()]
print("Check IDs to process:", check_id_list)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Early Exit Check - No Checks to Process

# COMMAND ----------

if check_id_list == [] and filter_historic_data:
    print(
        f"INFO : No Checks to process after applying historical filter using from_date: {from_date_dt}, Exiting the notebook.")
    dbutils.notebook.exit(0)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Process Failed Data Tables

# COMMAND ----------


all_dfs = []

for table in final_table_list:
    print(f"Processing table: {table}")

    # Load and filter data based on check_id_list if available
    if check_id_list != [''] and len(check_id_list) > 0:
        input_df = spark.table(f"{catalog_schema_name}.{table}") \
            .filter(F.col("check_id").isin(check_id_list)) \
            .withColumn("row_num", F.row_number().over(Window.partitionBy("check_id").orderBy("check_id")))
    else:
        input_df = spark.table(f"{catalog_schema_name}.{table}") \
            .withColumn("row_num", F.row_number().over(Window.partitionBy("check_id").orderBy("check_id")))

    # Apply record limit filter
    filtered_df = input_df.filter(F.col("row_num") <= record_limit).drop("row_num")

    # Cast all columns to StringType
    cast_exprs = [F.col(c).cast(StringType()).alias(c) for c in filtered_df.columns]
    df = filtered_df.select(*cast_exprs)

    # Transform data from wide to long format
    exploded_df = df.select(
        F.explode(
            F.create_map(
                *reduce(lambda x, y: x + y, [[F.lit(col), col] for col in df.columns]))
        )
    )

    # Rename columns and add row numbers
    renamed_df = exploded_df.withColumnRenamed("key", "column_name")
    numbered_df = renamed_df.withColumn("sno",
                                        F.row_number().over(Window.partitionBy("column_name").orderBy("column_name")))

    # Extract check_id information
    check_id_df = numbered_df.filter(F.col("column_name") == "check_id") \
        .select("column_name", "value", "sno") \
        .withColumnRenamed("value", "check_id") \
        .drop("column_name")

    # Join to get final result
    final_result = numbered_df.join(check_id_df, on="sno", how="inner") \
        .select("column_name", "value", "sno", "check_id")

    all_dfs.append(final_result)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Union All DataFrames

# COMMAND ----------

if len(all_dfs) < 1:
    print('No delta data refreshed')
    dbutils.notebook.exit(0)
else:
    unionAllDF = reduce(lambda df1, df2: df1.union(df2), all_dfs)
    print(f"Total records in consolidated dataframe: {unionAllDF.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Display Sample Results

# COMMAND ----------

display(unionAllDF.limit(100))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Save Consolidated Data

# COMMAND ----------

# Configure write options
options = dict(inferSchema=True, header=True, mergeSchema=True)

# Determine target schema and write data
if additional_schema != "":
    target_table = f"{additional_schema}.consolidated_failed_data"
    print(f"Writing to {target_table}")
    unionAllDF.write.format('delta').mode('overwrite').options(**options).saveAsTable(target_table)
else:
    target_table = f"{catalog_schema_name}.consolidated_failed_data"
    print(f"Writing to {target_table}")
    unionAllDF.write.format('delta').mode('overwrite').options(**options).saveAsTable(target_table)

print(f"Successfully saved consolidated failed data to: {target_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Notebook Completion
# MAGIC
# MAGIC Exit the notebook with success message.

# COMMAND ----------

dbutils.notebook.exit("Data Quality Framework Test Results Consolidation completed successfully.")
