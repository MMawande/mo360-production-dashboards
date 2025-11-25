# Databricks notebook source

from pyspark.sql.functions import col, lit, when, date_format, from_utc_timestamp, expr

# Define environment stage
dbutils.widgets.dropdown("env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage")
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
schema = "proddshbrd_01_emea_dbf_ddx_data"

# Load tables
mrs_emea_actual_dates_raw = spark.table(f"`{catalog}`.`{schema}`.mrs_emea_actual_dates")
mrs_nafta_actual_dates_raw = spark.table(f"`{catalog}`.`{schema}`.mrs_nafta_actual_dates")

# %% [markdown]
# #Union emea and nafta

# %%
# select and union table
mrs_emea_actual_dates = mrs_emea_actual_dates_raw.select(col("lupd_datetime"), col("plant"), col("ingest_time"), col("pmi"), col("actual_checkpoint"), col("destination_checkpoint"), col("event_datetime"), col("sequence_datetime"), col("checkpoint_mark"), col("cancel_datetime"), ("deletion_datetime"))

mrs_nafta_actual_dates = mrs_nafta_actual_dates_raw.select(col("lupd_datetime"), col("plant"), col("ingest_time"), col("pmi"), col("actual_checkpoint"), col("destination_checkpoint"), col("event_datetime"), col("sequence_datetime"), col("checkpoint_mark"), col("cancel_datetime"), ("deletion_datetime"))

mrs_actual_dates_union = mrs_emea_actual_dates.unionByName(mrs_nafta_actual_dates)

# %% [markdown]
# #Saved as a table in {dbf-staging}

# %%

# Define environment stage
dbutils.widgets.dropdown("env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage")
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
output_schema = "proddshbrd_01_emea_dbf_staging"

# save as table in unity catalog
mrs_actual_dates_union.write.saveAsTable(f"`{catalog}`.`{output_schema}`.stg_mrs_actual_dates", mode="overwrite")
