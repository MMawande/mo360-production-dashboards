# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC #Load table

# COMMAND ----------

# Define environment stage from notebook widget
from pyspark.sql.functions import col, when, lit
from pyspark.sql import functions as F

dbutils.widgets.dropdown(
    "env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage"
)
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
marts_schema = "proddshbrd_01_emea_dbf_marts"

# COMMAND ----------

# Load tables (from Unity Catalog schema)
mrt_dbf_0500 = spark.table(f"`{catalog}`.`{marts_schema}`.mrt_dbf_0500")
mrt_dbf_0540 = spark.table(f"`{catalog}`.`{marts_schema}`.mrt_dbf_0540")
mrt_dbf_0670 = spark.table(f"`{catalog}`.`{marts_schema}`.mrt_dbf_0670")
mrt_dbf_1750 = spark.table(f"`{catalog}`.`{marts_schema}`.mrt_dbf_1380")
mrt_dbf_1380 = spark.table(f"`{catalog}`.`{marts_schema}`.mrt_dbf_1750")


# COMMAND ----------

mrt_dbf_0500.display()

# COMMAND ----------

# MAGIC %md
# MAGIC #Perform union operation

# COMMAND ----------

mrt_dbf_all = (
    mrt_dbf_0500
    .unionByName(mrt_dbf_0540)
    .unionByName(mrt_dbf_0670)
    .unionByName(mrt_dbf_1750)
    .unionByName(mrt_dbf_1380)
    .where(col("punkt") == "Einrichtpunkt")
)

# COMMAND ----------

mrt_dbf_all = mrt_dbf_all.withColumn(

    "logischer_bereich_ref",

    when(col("logischer_bereich") == "Assembly", "Assembly")

    .when(col("logischer_bereich") == "Bodyshop", "Bodyshop")

    .when(

        (col("source") == "mrs") &

        (col("logischer_bereich").isin("MA41/42-RB", "MA21/22-RB", "MA51/52-RB")),

        "Bodyshop"

    )

    .when(

        (col("source") == "mrs") &

        (col("logischer_bereich").isin("SMA-MO", "Montage")),

        "Assembly"

    )

    .otherwise(None)

)


# COMMAND ----------


df = spark.table(f"`{catalog}`.`{marts_schema}`.mrt_dbf_all")

# Add new column with default value (e.g., None)
df_new = df.withColumn("logischer_bereich", F.lit(None).cast("string"))

# Overwrite the existing table with new schema
df_new.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"`{catalog}`.`{marts_schema}`.mrt_dbf_all")


# COMMAND ----------

# MAGIC %md
# MAGIC # Save as table

# COMMAND ----------

# save as table in unity catalog
mrt_dbf_all.write.saveAsTable(f"`{catalog}`.`{marts_schema}`.mrt_dbf_all", mode="overwrite")
