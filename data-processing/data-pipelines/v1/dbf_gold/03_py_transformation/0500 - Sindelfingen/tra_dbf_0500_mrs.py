# Databricks notebook source

# COMMAND ----------

# --- Imports ---
from pyspark.sql.functions import (
    col,
    lit,
    when,
    date_format,
    from_utc_timestamp,
    expr,
    to_date,
    date_sub,
    current_date,
    to_timestamp,
)
from pyspark.sql.window import Window
from pyspark.sql.types import DecimalType, IntegerType, StringType, TimestampType

# Load tables (from unity schema) --> should be adjusted
# Define environment stage from notebook widget
dbutils.widgets.dropdown(
    "env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage"
)
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
processed_schema = "proddshbrd_01_emea_dbf_transformation"

# COMMAND ----------
# Load tables (from unity schema) -->

tra_mrs_actualdates = spark.table(
    f"`{catalog}`.`{processed_schema}`.tra_mrs_actualdates"
)
tra_mrs_orders = spark.table(f"`{catalog}`.`{processed_schema}`.tra_mrs_orders")

# COMMAND ----------


# MAGIC ## Join and filter

# COMMAND ----------

# Join and filter

joined_filtered_df = (
    tra_mrs_actualdates.alias("t1")
    .join(tra_mrs_orders.alias("t2"), col("t1.pmi") == col("t2.pmi"))
    .filter(
        (col("t1.plant") == "0500")
        & (col("t2.plant") == "0500")
        & (col("t1.actual_checkpoint").isin("00000068"))
        & (col("t2.vehicle_type").isNotNull())
        & (to_date(col("t1.sequence_datetime")) >= date_sub(current_date(), 90))
    )
)


# MAGIC ##Select with transformation

# COMMAND ----------

# Select and transform columns
result_df = joined_filtered_df.select(
    lit(None).cast(StringType()).alias("anlage_subtyp"),
    lit(None).cast(TimestampType()).alias("timestamp"),
    lit(None).alias("offset").cast(DecimalType(10, 2)).alias("offset"),
    col("t2.body_number").cast(StringType()).alias("header_measurement_productionids_2"),
    lit(None).cast(StringType()).alias("header_measurement_productionids_1"),
    lit(None).cast(StringType()).alias("baureihe"),
    lit(None).cast(StringType()).alias("header_measurement_typeseries"),
    col("t2.vehicle_type").cast(StringType()).alias("fzg_typ"),
    col("t1.plant").cast(StringType()).alias("cplant"),
    lit(None).cast(StringType()).alias("result_notcalc"),
    lit("Einrichtpunkt").cast(StringType()).alias("punkt"),
    lit(None).cast(StringType()).alias("measurement_featurename"),
    lit(None).alias("measurement_value").cast(DecimalType(10, 2)).alias("measurement_value"),
    lit(None).alias("produktionsstunde").cast(IntegerType()).alias("produktionsstunde"),
    lit(None).cast(IntegerType()).alias("pd1"),
    lit(None).cast(IntegerType()).alias("pd2"),
    lit(None).cast(StringType()).alias("pd3"),
    lit(None).alias("messwert_toleranz_min").cast(DecimalType(10, 2)),
    lit(None).alias("messwert_toleranz_max").cast(DecimalType(10, 2)),
    lit(None).alias("messwert_toleranz_sec_min").cast(DecimalType(10, 2)),
    lit(None).alias("messwert_toleranz_sec_max").cast(DecimalType(10, 2)),
    lit(None).cast(StringType()).alias("result"),
    lit(None).cast(StringType()).alias("kennerfuge"),
    lit(None).cast(StringType()).alias("seite"),
    lit(None).cast(StringType()).alias("kennerfg"),
    lit(None).cast(StringType()).alias("over_under"),
    lit(None).cast(StringType()).alias("position"),
    lit(None).cast(StringType()).alias("art"),
    lit(None).cast(StringType()).alias("measure"),
    lit(None).cast(StringType()).alias("name"),
    lit(None).cast(StringType()).alias("fahrzeugresult_karno"),
    lit(None).cast(StringType()).alias("fahrzeugresult_overall"),
    lit(None).alias("calc").cast(DecimalType(10, 2)),
    lit(None).cast(StringType()).alias("allmeasures"),
    lit(None).cast(StringType()).alias("lastmeasure"),
    lit("mrs").cast(StringType()).alias("source"),
    lit(None).cast(StringType()).alias("all_checks"),
    when(
        col("t1.checkpoint_description").isin("B31 MA74 Kickout", "B31 MA64 KICKOUT"),
        "Bodyshop",
    )
    .otherwise("Assembly")
    .alias("origin"),
    to_timestamp(col("t1.sequence_datetime")).alias("header_measurement_meastime"),
    to_date(col("t1.sequence_datetime")).alias("ingest_date"),
    when(
        col("t1.checkpoint_description").isin("B31 MA74 Kickout", "B31 MA64 KICKOUT"),
        "Bodyshop",
    )
    .otherwise("Assembly")
    .alias("logischer_bereich"),
    to_date(col("t1.sequence_datetime")).alias("date"),
    date_format(to_timestamp(col("t1.sequence_datetime")), "HH:mm:ss").alias("time"),
)


# MAGIC #Save as a Table

# COMMAND ----------

# save as table in unity catalog
# Define environment stage from notebook widget
dbutils.widgets.dropdown(
    "env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage"
)
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
processed_schema = "proddshbrd_01_emea_dbf_transformation"

# COMMAND ----------
# Load tables (from unity schema) -->
result_df.write.saveAsTable(
    f"`{catalog}`.`{processed_schema}`.tra_dbf_0500_mrs", mode="overwrite"
)
