# Databricks notebook source

from pyspark.sql.functions import col, lit, when, date_format, from_utc_timestamp, expr

# Define environment stage
dbutils.widgets.dropdown("env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage")
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
schema = "proddshbrd_01_emea_dbf_ddx_data"

# Load tables
mrs_emea_order_prod_codes_md_raw = spark.table(f"`{catalog}`.`{schema}`.mrs_emea_order_prod_codes_md")
mrs_nafta_order_prod_codes_md_raw = spark.table(f"`{catalog}`.`{schema}`.mrs_nafta_order_prod_codes_md")

# %% [markdown]
# #Union emea and nafta

# %%
# select and union table
selected_columns = [
    col("deletion_datetime"),
    col("ingest_datetime"),
    col("optioncode"),
    col("optioncodedescription"),
    col("production_plant").alias("plant"),
]

mrs_emea_order_prod_codes_md = (
    mrs_emea_order_prod_codes_md_raw
    .filter(col("deletion_datetime").isNull())
    .select(*selected_columns)
)
mrs_nafta_order_prod_codes_md = (
    mrs_nafta_order_prod_codes_md_raw
    .filter(col("deletion_datetime").isNull())
    .select(*selected_columns)
)

mrs_order_prod_codes_md_union = mrs_emea_order_prod_codes_md.unionByName(mrs_nafta_order_prod_codes_md)

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
mrs_order_prod_codes_md_union.write.saveAsTable(f"`{catalog}`.`{output_schema}`.stg_mrs_order_prod_codes_md", mode="overwrite")
