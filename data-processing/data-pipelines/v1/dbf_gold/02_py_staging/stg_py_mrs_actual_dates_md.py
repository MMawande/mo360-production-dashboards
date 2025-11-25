# Databricks notebook source

from pyspark.sql.functions import col, lit, when, date_format, from_utc_timestamp, expr

# Define environment stage
dbutils.widgets.dropdown("env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage")
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
schema = "proddshbrd_01_emea_dbf_ddx_data"

# Load tables
mrs_emea_actual_dates_md_raw = spark.table(f"`{catalog}`.`{schema}`.mrs_emea_actual_dates_md")
mrs_nafta_actual_dates_md_raw = spark.table(f"`{catalog}`.`{schema}`.mrs_nafta_actual_dates_md")

# %% [markdown]
# #Union emea and nafta

# %%
# select and union table
mrs_emea_actual_dates_md = mrs_emea_actual_dates_md_raw.select(col("plant"), col("checkpoint"), col("checkpoint_mark"), col("hall"), col("location_progress"), col("checkpoint_description"), col("ingest_datetime"), col("deletion_datetime"))

mrs_nafta_actual_dates_md = mrs_nafta_actual_dates_md_raw.select(col("plant"), col("checkpoint"), col("checkpoint_mark"), col("hall"), col("location_progress"), col("checkpoint_description"), col("ingest_datetime"), col("deletion_datetime"))

mrs_actual_dates_md_union = mrs_emea_actual_dates_md.unionByName(mrs_nafta_actual_dates_md)

# %% [markdown]
# #Saved as a table in {dbf-staging}

# %%
# Define environment stage from notebook widget
dbutils.widgets.dropdown("env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage")
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
output_schema = "proddshbrd_01_emea_dbf_staging"

# COMMAND ----------

# save as table in unity catalog
mrs_actual_dates_md_union.write.saveAsTable(f"`{catalog}`.`{output_schema}`.stg_mrs_actual_dates_md", mode="overwrite")
