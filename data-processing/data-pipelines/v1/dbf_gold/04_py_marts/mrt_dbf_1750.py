# Databricks notebook source

# MAGIC %md

# MAGIC #Load Table

# COMMAND ----------

# --- Imports
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
    date_format,
    to_date,
    current_date,
)
from pyspark.sql.window import Window
from pyspark.sql.types import DecimalType, IntegerType

# Define environment stage from notebook widget
dbutils.widgets.dropdown(
    "env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage"
)
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
transformation_schema = "proddshbrd_01_emea_dbf_transformation"

# Load tables (from unity schema) -->
tra_dbf_1750_main = spark.table(
    f"`{catalog}`.`{transformation_schema}`.tra_dbf_1750_main"
)
tra_dbf_1750_korrelation = spark.table(
    f"`{catalog}`.`{transformation_schema}`.tra_dbf_1750_korrelation"
)
tra_dbf_1750_karnrresult = spark.table(
    f"`{catalog}`.`{transformation_schema}`.tra_dbf_1750_karnrresult"
)
tra_dbf_1750_additionalchecks = spark.table(
    f"`{catalog}`.`{transformation_schema}`.tra_dbf_1750_additionalchecks"
)
tra_dbf_1750_mrs = spark.table(
    f"`{catalog}`.`{transformation_schema}`.tra_dbf_1750_mrs"
)


# COMMAND ----------

# Test data source
tra_dbf_1750_korrelation.display()

# COMMAND ----------

# MAGIC %md
# MAGIC #Join tables

# COMMAND ----------

# Define base DataFrame t1 first
t1 = tra_dbf_1750_main.filter(col("ingest_date") >= date_sub(current_date(), 90)).alias("t1")

# reference t1.columns
mrt_dbf_1750 = (
    t1.join(
        tra_dbf_1750_karnrresult.alias("t2"),
        (
            col("t1.header_measurement_productionids_2")
            == col("t2.header_measurement_productionids_2")
        )
        & (col("t1.punkt") == col("t2.punkt"))
        & (col("t1.origin") == col("t2.origin"))
        & (col("t1.seite") == col("t2.seite")),
        how="left",
    )
    .join(
        tra_dbf_1750_korrelation.alias("t3"),
        (col("t1.measurement_featurename") == col("t3.measurement_featurename"))
        & (
            col("t1.header_measurement_productionids_1")
            == col("t3.header_measurement_productionids_1")
        )
        & (
            col("t1.header_measurement_productionids_2")
            == col("t3.header_measurement_productionids_2")
        ),
        how="left",
    )
    .join(
        tra_dbf_1750_additionalchecks.alias("t4"),
        (col("t1.header_measurement_productionids_2") == col("t4.karnr"))
        & (col("t1.origin") == col("t4.origin")),
        how="left",
    )
    .select(
        *[col("t1." + c) for c in t1.columns],
        col("t2.fahrzeugresult_karno"),
        col("t2.fahrzeugresult_overall"),
        col("t3.calc"),
        col("t1.origin").alias("logischer_bereich"),
        col("t4.allmeasures"),
        col("t4.lastmeasure"),
        lit("iqvis").alias("source"),
        when(
            (col("t4.allmeasures") == "OK") & (col("t4.lastmeasure") == "vollständig"),
            "OK",
        )
        .otherwise("NOK")
        .alias("all_checks"),
        to_date("t1.header_measurement_meastime").alias("date"),
        date_format(
            col("t1.header_measurement_meastime").cast("timestamp"), "HH:mm:ss"
        ).alias("time"),
    )
)

# COMMAND ----------

mrt_dbf_1750.display()

# COMMAND ----------

# Select final fields and cast types
mrt_dbf_1750_final = mrt_dbf_1750.select(
    "anlage_subtyp",
    "timestamp",
    col("offset").cast(DecimalType(10, 2)).alias("offset"),
    "header_measurement_productionids_2",
    "header_measurement_productionids_1",
    "baureihe",
    "header_measurement_typeseries",
    "fzg_typ",
    "cplant",
    "result_notcalc",
    "punkt",
    "measurement_featurename",
    col("measurement_value").cast(DecimalType(10, 2)).alias("measurement_value"),
    col("produktionsstunde").cast(IntegerType()).alias("produktionsstunde"),
    "pd1",
    "pd2",
    "pd3",
    col("messwert_toleranz_min").cast(DecimalType(10, 2)),
    col("messwert_toleranz_max").cast(DecimalType(10, 2)),
    col("messwert_toleranz_sec_min").cast(DecimalType(10, 2)),
    col("messwert_toleranz_sec_max").cast(DecimalType(10, 2)),
    "result",
    "kennerfuge",
    "seite",
    "kennerfg",
    "over_under",
    "position",
    "art",
    "measure",
    "name",
    "fahrzeugresult_karno",
    "fahrzeugresult_overall",
    col("calc").cast(DecimalType(10, 2)),
    "allmeasures",
    "lastmeasure",
    "source",
    "all_checks",
    "origin",
    "header_measurement_meastime",
    "ingest_date",
    "logischer_bereich",
    "date",
    "time",
)

mrt_dbf_1750_final.display()

# COMMAND ----------

# MAGIC %md
# MAGIC # Union mrs

# COMMAND ----------

# Final union with tra_dbf_050_mrs
result_df = mrt_dbf_1750_final.unionByName(tra_dbf_1750_mrs)

# COMMAND ----------

# MAGIC %md
# MAGIC # Save as a table

# COMMAND ----------

# Define environment stage again
dbutils.widgets.dropdown(
    "env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage"
)
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
marts_schema = "proddshbrd_01_emea_dbf_marts"

# save as table in unity catalog
result_df.write.saveAsTable(
    f"`{catalog}`.`{marts_schema}`.mrt_dbf_1750", mode="overwrite"
)
