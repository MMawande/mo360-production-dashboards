# Databricks notebook source

from pyspark.sql.functions import col, lit, when, date_format, from_utc_timestamp, expr

# Load tables
dbutils.widgets.dropdown("env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage")
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
schema = "proddshbrd_01_emea_dbf_ddx_data"

# Load tables
mrs_emea_modules_raw = spark.table(f"`{catalog}`.`{schema}`.mrs_emea_modules")
mrs_nafta_modules_raw = spark.table(f"`{catalog}`.`{schema}`.mrs_nafta_modules")

# %% [markdown]
# # Union emea and nafta

# %%
# Define the selected columns
selected_columns = [
    col("assembly_section"),
    col("battery_number"),
    col("body_number"),
    col("body_number_historic"),
    col("checkpoint"),
    col("checkpoint_plant"),
    col("completion_datetime"),
    col("component_id"),
    col("component_part_no"),
    col("creation_date"),
    col("deletion_datetime"),
    col("destination_checkpoint"),
    col("destination_plant"),
    col("distribution_dest_key"),
    col("distribution_nodename"),
    col("engine_number"),
    col("event_datetime"),
    col("external_engine_id"),
    col("ingest_time"),
    col("is_blocked"),
    col("is_cepra_archiving_done"),
    col("is_remake"),
    col("is_scrapped"),
    col("location_progress"),
    col("lupd_datetime"),
    col("manufacturing_progress"),
    col("manufacturing_state"),
    col("module_type"),
    col("parking_area"),
    col("plant"),
    col("pmi"),
    col("quality_audit_state"),
    col("reess_code"),
    col("shipment_datetime"),
    col("skid_number"),
    col("transponder_number"),
    col("variable_ident"),
    col("vedoc_series_number"),
    col("vehicle_properties")
]

# Load and filter EMEA data
mrs_emea_modules = (
    mrs_emea_modules_raw
    .filter(col("deletion_datetime").isNull())
    .select(*selected_columns)
)

# Load and filter NAFTA data
mrs_nafta_modules = (
    mrs_nafta_modules_raw
    .filter(col("deletion_datetime").isNull())
    .select(*selected_columns)
)

# Union the two DataFrames
mrs_modules_union = mrs_emea_modules.unionByName(mrs_nafta_modules)

# %% [markdown]
# # Save as Table

# %%
# save as table in unity catalog

# Define environment stage from notebook widget
dbutils.widgets.dropdown("env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage")
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
output_schema = "proddshbrd_01_emea_dbf_staging"

# COMMAND ----------

# save as table in unity catalog
mrs_modules_union.write.saveAsTable(f"`{catalog}`.`{output_schema}`.stg_mrs_modules", mode="overwrite")
