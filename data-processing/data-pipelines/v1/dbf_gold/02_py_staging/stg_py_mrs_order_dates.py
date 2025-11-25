# Databricks notebook source

from pyspark.sql.functions import col, lit, when, date_format, from_utc_timestamp, expr

# Define environment stage
dbutils.widgets.dropdown("env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage")
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
schema = "proddshbrd_01_emea_dbf_ddx_data"

# Load tables
mrs_emea_order_dates_raw = spark.table(f"`{catalog}`.`{schema}`.mrs_emea_order_dates")
mrs_nafta_order_dates_raw = spark.table(f"`{catalog}`.`{schema}`.mrs_nafta_order_dates")

# %% [markdown]
# #Union emea and nafta

# %%
# select and union table
selected_columns = [
    col("lupd_datetime"),
    col("plant"),
    col("ingest_time"),
    col("deletion_datetime"),
    col("poi"),
    col("checkpoint_mark"),
    col("fulfilled_plant"),
    col("fulfilled_checkpoint"),
    col("fulfilled_datetime"),
    col("fulfilled_shift_flag"),
    col("fulfilled_shift_seq_flag"),
    col("fulfilled_p_shift"),
    col("fulfilled_p_week"),
    col("fulfilled_c_week"),
    col("fulfilled_counter"),
    col("is_fulfilled"),
    col("planned_plant"),
    col("planned_checkpoint"),
    col("planned_datetime"),
    col("planned_shift_flag"),
    col("planned_shift_seq_flag"),
    col("planned_p_shift"),
    col("planned_p_week"),
    col("planned_c_week"),
    col("plan_sequence_number"),
    col("due_plant"),
    col("due_checkpoint"),
    col("due_datetime"),
    col("due_shift_flag"),
    col("due_shift_seq_flag"),
    col("due_p_shift"),
    col("due_p_week"),
    col("due_c_week"),
    col("due_sequence_number"),
    col("jisp_sequence_number"),
    col("jisp_no_is_valid")
]

mrs_emea_order_dates = (
    mrs_emea_order_dates_raw
    .filter(col("deletion_datetime").isNull())
    .select(*selected_columns)
)
mrs_nafta_order_dates = (
    mrs_nafta_order_dates_raw
    .filter(col("deletion_datetime").isNull())
    .select(*selected_columns)
)

mrs_order_dates_union = mrs_emea_order_dates.unionByName(mrs_nafta_order_dates)

# %% [markdown]
# #Saved as a table in {dbf-staging}

# %%
# COMMAND ----------


# Define environment stage
dbutils.widgets.dropdown("env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage")
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
output_schema = "proddshbrd_01_emea_dbf_staging"

# save as table in unity catalog
mrs_order_dates_union.write.saveAsTable(f"`{catalog}`.`{output_schema}`.stg_mrs_order_dates", mode="overwrite")
