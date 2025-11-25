# Databricks notebook source

# COMMAND ----------

# --- Imports ---
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, substring, date_sub, lit, when, split, row_number, avg
from pyspark.sql.window import Window

# COMMAND ----------

# --- Define environment stage ---
dbutils.widgets.dropdown("env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage")
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
schema = "proddshbrd_01_emea_dbf_staging"

# COMMAND ----------

# --- Load tables (from Unity Catalog schema) ---
stg_mrs_actual_dates = spark.table(f"`{catalog}`.`{schema}`.stg_mrs_actual_dates")
stg_mrs_actual_dates_md = spark.table(f"`{catalog}`.`{schema}`.stg_mrs_actual_dates_md")

# COMMAND ----------

# --- Perform INNER JOIN ---
tra_mrs_actualdates = stg_mrs_actual_dates.alias("t1").join(
    stg_mrs_actual_dates_md.alias("t2"),
    (col("t1.plant") == col("t2.plant")) &
    (col("t1.actual_checkpoint") == col("t2.checkpoint")),
    "inner"
).select(col("t1.plant"),
         col("t1.pmi"),
         "actual_checkpoint",
         "destination_checkpoint",
         "event_datetime",
         "sequence_datetime",
         col("t1.checkpoint_mark"),
         "cancel_datetime",
         col("t1.deletion_datetime"),
         "hall",
         "location_progress",
         "checkpoint_description")

# COMMAND ----------

# --- Define environment stage again ---
dbutils.widgets.dropdown("env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage")
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
schema = "proddshbrd_01_emea_dbf_transformation"

# COMMAND ----------

# --- Save as a Table in Unity Catalog ---
tra_mrs_actualdates.write.saveAsTable(f"`{catalog}`.`{schema}`.tra_mrs_actualdates", mode="overwrite")
