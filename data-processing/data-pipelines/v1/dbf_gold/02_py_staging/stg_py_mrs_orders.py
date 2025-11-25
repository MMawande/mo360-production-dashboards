# Databricks notebook source

from pyspark.sql.functions import col, lit, when, date_format, from_utc_timestamp, expr

# Define environment stage
dbutils.widgets.dropdown("env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage")
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
schema = "proddshbrd_01_emea_dbf_ddx_data"

# Load tables
mrs_emea_orders_raw = spark.table(f"`{catalog}`.`{schema}`.mrs_emea_orders")
mrs_nafta_orders_raw = spark.table(f"`{catalog}`.`{schema}`.mrs_nafta_orders")

# %% [markdown]
# #Union emea and nafta

# %%
# select and union table
selected_columns = [
    col("baumuster"),
    col("body_shape"),
    col("consumer_country"),
    col("customer_order_number"),
    col("deletion_datetime"),
    col("engine"),
    col("ib_hall_mark"),
    col("ingest_time"),
    col("lupd_datetime"),
    col("model"),
    col("order_type"),
    col("pa1_flag"),
    col("paint_bottom"),
    col("paint_bottom_desc"),
    col("paint_top"),
    col("paint_top_desc"),
    col("plant"),
    col("poi"),
    col("production_number"),
    col("purpose"),
    col("scheduling_plant"),
    col("steering"),
    col("technical_status_actual"),
    col("technicat_status_original"),
    col("transmission"),
    col("upholstery"),
    col("vehicle_type"),
    col("vin"),
    col("von")
]

mrs_emea_orders = (
    mrs_emea_orders_raw
    .filter(col("deletion_datetime").isNull())
    .select(*selected_columns)
)
mrs_nafta_orders = (
    mrs_nafta_orders_raw
    .filter(col("deletion_datetime").isNull())
    .select(*selected_columns)
)

mrs_orders_union = mrs_emea_orders.unionByName(mrs_nafta_orders)

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
mrs_orders_union.write.saveAsTable(f"`{catalog}`.`{output_schema}`.stg_mrs_orders", mode="overwrite")
