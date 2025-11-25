# Databricks notebook source

from pyspark.sql.functions import col, lit, when, date_format, from_utc_timestamp, expr

# Define environment stage
dbutils.widgets.dropdown("env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage")
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
schema = "proddshbrd_01_emea_dbf_ddx_data"

# Load tables
mrs_emea_poi_pmi_mapping_raw = spark.table(f"`{catalog}`.`{schema}`.mrs_emea_poi_pmi_mapping")
mrs_nafta_poi_pmi_mapping_raw = spark.table(f"`{catalog}`.`{schema}`.mrs_nafta_poi_pmi_mapping")

# %% [markdown]
# #Union emea and nafta

# %%
# select and union table
selected_columns = [
    col("deletion_datetime"),
    col("hierarchy_lupd_datetime"),
    col("ingest_timstamp_utc"),
    col("lupd_datetime"),
    col("plant"),
    col("pmi"),
    col("poi_direct_linked"),
    col("poi_latest"),
    col("poi_parent")
]

mrs_emea_poi_pmi_mapping = (
    mrs_emea_poi_pmi_mapping_raw
    .filter(col("deletion_datetime").isNull())
    .select(*selected_columns)
)
mrs_nafta_poi_pmi_mapping = (
    mrs_nafta_poi_pmi_mapping_raw
    .filter(col("deletion_datetime").isNull())
    .select(*selected_columns)
)

mrs_poi_pmi_mapping_union = mrs_emea_poi_pmi_mapping.unionByName(mrs_nafta_poi_pmi_mapping)

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
mrs_poi_pmi_mapping_union.write.saveAsTable(f"`{catalog}`.`{output_schema}`.stg_mrs_poi_pmi_mapping", mode="overwrite")
