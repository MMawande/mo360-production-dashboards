# Databricks notebook source

# COMMAND ----------

# --- Imports ---
from pyspark.sql import functions as F
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    substring,
    date_sub,
    lit,
    when,
    split,
    row_number,
    avg,
)
from pyspark.sql.window import Window

# COMMAND ----------

# --- Define environment stage ---
dbutils.widgets.dropdown(
    "env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage"
)
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
schema = "proddshbrd_01_emea_dbf_staging"

# COMMAND ----------

# --- Load tables (from Unity Catalog schema) ---
stg_mrs_orders = spark.table(f"`{catalog}`.`{schema}`.stg_mrs_orders")
stg_mrs_poi_pmi_mapping = spark.table(f"`{catalog}`.`{schema}`.stg_mrs_poi_pmi_mapping")
stg_mrs_modules = spark.table(f"`{catalog}`.`{schema}`.stg_mrs_modules")
stg_mrs_order_variants = spark.table(f"`{catalog}`.`{schema}`.stg_mrs_order_variants")

# COMMAND ----------

# --- Perform INNER JOIN between orders and poi_pmi_mapping ---
orders_poi_joined = stg_mrs_orders.alias("orders").join(
    stg_mrs_poi_pmi_mapping.alias("poi_pmi_mapping"),
    (F.col("orders.poi") == F.col("poi_pmi_mapping.poi_latest"))
    & (F.col("orders.plant") == F.col("poi_pmi_mapping.plant")),
    "inner",
)

# COMMAND ----------

# --- Perform INNER JOIN between the previous result and modules ---
orders_poi_modules_joined = orders_poi_joined.join(
    stg_mrs_modules.alias("modules"),
    (F.col("modules.pmi") == F.col("poi_pmi_mapping.pmi"))
    & (F.col("modules.plant") == F.col("orders.plant")),
    "inner",
)

# COMMAND ----------

# --- Perform LEFT JOIN with order_variants ---
final_df = orders_poi_modules_joined.join(
    stg_mrs_order_variants.alias("order_variants"),
    (F.col("orders.poi") == F.col("order_variants.poi"))
    & (F.col("orders.plant") == F.col("order_variants.plant")),
    "left",
)

# COMMAND ----------

# --- Apply filters where modules.body_number IS NOT NULL and other conditions ---
final_df = final_df.filter(
    F.col("modules.body_number").isNotNull()
    & F.col("poi_pmi_mapping.pmi").rlike("^(BN|VO)")
    & F.col("orders.vehicle_type").isNotNull()
)

# COMMAND ----------

# --- Add ROW_NUMBER() OVER (PARTITION BY poi_pmi_mapping.pmi ORDER BY orders.ingest_time DESC) ---
window_spec = Window.partitionBy("poi_pmi_mapping.pmi").orderBy(
    F.col("orders.ingest_time").desc()
)
final_df = final_df.withColumn("row_num", F.row_number().over(window_spec))

# COMMAND ----------

# --- Filter where row_num = 1 ---
final_df = final_df.filter(F.col("row_num") == 1)

# COMMAND ----------

# --- Select the necessary columns as in the SQL query ---
tra_mrs_orders = final_df.select(
    "orders.plant",
    "orders.vehicle_type",
    "orders.ingest_time",
    "orders.production_number",
    "orders.vin",
    "orders.baumuster",
    "orders.poi",
    "poi_pmi_mapping.pmi",
    "modules.body_number",
)

# COMMAND ----------

# --- Define environment stage again ---
dbutils.widgets.dropdown(
    "env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage"
)
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
schema = "proddshbrd_01_emea_dbf_transformation"

# COMMAND ----------

# --- Save as a Table in Unity Catalog ---
tra_mrs_orders.write.saveAsTable(
    f"`{catalog}`.`{schema}`.tra_mrs_orders", mode="overwrite"
)
