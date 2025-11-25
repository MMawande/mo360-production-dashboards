# Databricks notebook source

# MAGIC # 0500 - Sindelfingen

# COMMAND ----------


# MAGIC #Korrelation

# COMMAND ----------


# MAGIC ##Load table

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

# Load tables (from hive schema) -->
# Define environment stage from notebook widget
dbutils.widgets.dropdown(
    "env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage"
)
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
processed_schema = "proddshbrd_01_emea_dbf_source_data"
mapping_schema = "proddshbrd_01_emea_dbf_mappings"

# Load tables (from unity schema) -->
processed_iqvis = spark.table(f"`{catalog}`.`{processed_schema}`.processed_iqvis")
tb_einrichtpunkte_baureihe_dbf_0500 = spark.table(
    f"`{catalog}`.`{mapping_schema}`.tb_einrichtpunkte_baureihe_dbf_0500"
)

# COMMAND ----------

processed_iqvis.display()

# COMMAND ----------

tb_einrichtpunkte_baureihe_dbf_0500.display()

# COMMAND ----------


# MAGIC ##tb_id

# COMMAND ----------


tb_id = (
    processed_iqvis.filter(
        (F.col("cmonth") >= F.date_format(F.date_sub(F.current_date(), 50), "yyyy-MM"))
        & (F.col("mode") == "SERIE")
        & (
            F.col("uniqueid").like("%BFK%")
            | F.col("uniqueid").like("%SMA%")
            | F.col("uniqueid").like("%SME%")
        )
        & (F.col("prodnr").isNotNull())
        & (F.col("karnr").isNotNull())
        & (F.col("transactiontype") == "MEASUREMENT")
        & (F.col("cplant") == "0500")
    )
    .select("karnr", "prodnr", "cplant")
    .distinct()
)

# Show the resulting DataFrame
tb_id.display()

# COMMAND ----------


# MAGIC ##tb_iqvis

# COMMAND ----------

# Define a function to apply the complex CASE logic for `messwerttyp_calc` ---> for 1380 only
# def messwerttyp_case(column):
#     # You can extend this list with all your conditions
#     conditions = [
#         (column.like('%1L Z HEIGHTZ%'), '1L Z HEIGHTZ'),
#         (column.like('%1L KICKUPF%'), '1L KICKUPF'),
#         (column.like('%5-6_4LG%'), '5-6_4LG'),
#         (column.like('%5-6_4LF%'), '5-6_4LF'),
#         (column.like('%5-6_1LG%'), '5-6_1LG'),
#         (column.like('%5-6_1LF%'), '5-6_1LF'),
#         (column.like('%1R Z HEIGHTZ%'), '1R Z HEIGHTZ'),
#         (column.like('%1R KICKUPF%'), '1R KICKUPF'),
#         (column.like('%5-6_4RG%'), '5-6_4RG'),
#         (column.like('%5-6_4RF%'), '5-6_4RF'),
#         (column.like('%5-6_1RG%'), '5-6_1RG'),
#         (column.like('%5-6_1RF%'), '5-6_1RF'),
#         (column.like('%2L Z HEIGHTZ%'), '2L Z HEIGHTZ'),
#         (column.like('%1-5_2LG%'), '1-5_2LG'),
#         (column.like('%1-5_2LF%'), '1-5_2LF'),
#         (column.like('%1-5_12LG%'), '1-5_12LG'),
#         (column.like('%1-5_12LF%'), '1-5_12LF'),
#         (column.like('%2L KICKUPZ%'), '2L KICKUPZ'),
#         (column.like('%2R Z HEIGHTZ%'), '2R Z HEIGHTZ'),
#         (column.like('%2R KICKUPZ%'), '2R KICKUPZ'),
#         (column.like('%1-5_2RG%'), '1-5_2RG'),
#         (column.like('%1-5_2RF%'), '1-5_2RF'),
#         (column.like('%1-5_12RG%'), '1-5_12RG'),
#         (column.like('%1-5_12RF%'), '1-5_12RF'),
#         (column.like('%1-5_14LG%'), '1-5_14LG'),
#         (column.like('%1-5_14LF%'), '1-5_14LF'),
#         (column.like('%1-5_14RG%'), '1-5_14RG'),
#         (column.like('%1-5_14RF%'), '1-5_14RF'),
#         (column.like('%1-5_19bLG%'), '1-5_19bLG'),
#         (column.like('%1-5_6LG%'), '1-5_6LG'),
#         (column.like('%1-5_6LF%'), '1-5_6LF'),
#         (column.like('%1-5_19aLG%'), '1-5_19aLG'),
#         (column.like('%1-5_19aLF%'), '1-5_19aLF'),
#         (column.like('%1-5_19bRG%'), '1-5_19bRG'),
#         (column.like('%1-5_6RG%'), '1-5_6RG'),
#         (column.like('%1-5_6RF%'), '1-5_6RF'),
#         (column.like('%1-5_19aRG%'), '1-5_19aRG'),
#         (column.like('%1-5_19aRF%'), '1-5_19aRF'),
#         (column.like('%1L_Z_HEIGHTZ%'), '1L_Z_HEIGHTZ'),
#         (column.like('%1L_KICKUPF%'), '1L_KICKUPF'),
#         (column.like('%5-6_RZ580LG%'), '5-6_RZ580LG'),
#         (column.like('%5-6_RZ580LF%'), '5-6_RZ580LF'),
#         (column.like('%5-6_RZ25LG%'), '5-6_RZ25LG'),
#         (column.like('%5-6_RZ25LF%'), '5-6_RZ25LF'),
#         (column.like('%1L_GAP_PART%'), '1L_GAP_PART'),
#         (column.like('%2L_Z_HeightZ%'), '2L_Z_HeightZ'),
#         (column.like('%1-5_RZ640LG%'), '1-5_RZ640LG'),
#         (column.like('%1-5_RZ640LF%'), '1-5_RZ640LF'),
#         (column.like('%1-5_RZ100LG%'), '1-5_RZ100LG'),
#         (column.like('%1-5_RZ100LF%'), '1-5_RZ100LF'),
#         (column.like('%1R_Z_HEIGHTZ%'), '1R_Z_HEIGHTZ'),
#         (column.like('%1R_KICKUPF%'), '1R_KICKUPF'),
#         (column.like('%5-6_RZ580RG%'), '5-6_RZ580RG'),
#         (column.like('%5-6_RZ580RF%'), '5-6_RZ580RF'),
#         (column.like('%5-6_RZ25RG%'), '5-6_RZ25RG'),
#         (column.like('%5-6_RZ25RF%'), '5-6_RZ25RF'),
#         (column.like('%1R_GAP_PART%'), '1R_GAP_PART'),
#         (column.like('%2R_Z_HeightZ%'), '2R_Z_HeightZ'),
#         (column.like('%1-5_RZ640RG%'), '1-5_RZ640RG'),
#         (column.like('%1-5_RZ640RF%'), '1-5_RZ640RF'),
#         (column.like('%1-5_RZ100RG%'), '1-5_RZ100RG'),
#         (column.like('%1-5_RZ100RF%'), '1-5_RZ100RF'),
#         (column.like('%2R_KICKUPZ%'), '2R_KICKUPZ'),
#         (column.like('%1-5_RZ110RF%'), '1-5_RZ110RF'),
#         (column.like('%1-5_RZ110RG%'), '1-5_RZ110RG'),
#         (column.like('%1-5_RZ610RF%'), '1-5_RZ610RF'),
#         (column.like('%1-5_RZ610RG%'), '1-5_RZ610RG'),
#         (column.like('%2L_KICKUPZ%'), '2L_KICKUPZ'),
#         (column.like('%1-5_RZ110LF%'), '1-5_RZ110LF'),
#         (column.like('%1-5_RZ110LG%'), '1-5_RZ110LG'),
#         (column.like('%1-5_RZ610LF%'), '1-5_RZ610LF'),
#         (column.like('%1-5_RZ610LG%'), '1-5_RZ610LG')
#     ]
#     # Default case
#     default_expr = F.when(column.like('%1-5_RZ610LG%'), '1-5_RZ610LG').otherwise(column)
#     # Build the case statement
#     case_expr = F.when(*conditions[0])
#     for condition in conditions[1:]:
#         case_expr = case_expr.when(*condition)
#     return case_expr.otherwise(default_expr)

# Transformation for the first SELECT statement
tb_iqvis_tra_1 = (
    processed_iqvis.filter(
        (F.col("cmonth") >= F.date_format(F.date_sub(F.current_date(), 50), "yyyy-MM"))
        & (F.col("component").isin("F", "G", "Z", "D", "X", "Y", "S", "T", "K", "L"))
        & (F.col("mode") == "SERIE")
        & (F.col("uniqueid").like("%SMA%"))
        & (F.col("prodnr").isNotNull())
        & (F.col("karnr").isNotNull())
        & (F.col("transactiontype") == "MEASUREMENT")
        & (F.col("cplant") == "0500")
    )
    .withColumn(
        "fzg_typ_calc",
        F.when(
            F.col("anlage_subtyp").like("%BFK%"),
            F.split(F.col("anlage_subtyp"), "_")[1],
        )
        .when(
            F.col("anlage_subtyp").like("%AMG%"),
            F.split(F.col("anlage_subtyp"), "_")[0],
        )
        .when(
            F.col("anlage_subtyp").like("%SMA%"),
            F.split(F.col("anlage_subtyp"), "_")[0],
        )
        .when(
            F.col("anlage_subtyp").like("%SME%"),
            F.split(F.col("anlage_subtyp"), "_")[1],
        ),
    )
    .withColumn(
        "origin", F.when(F.col("uniqueid").like("%SMA%"), "Assembly").otherwise("Rest")
    )
    .withColumn("messwerttyp_calc", col("messwerttyp"))
)


# Transformation for the second SELECT statement
tb_iqvis_tra_2 = (
    processed_iqvis.filter(
        (F.col("cmonth") >= F.date_format(F.date_sub(F.current_date(), 50), "yyyy-MM"))
        & (F.col("component").isin("F", "G", "Z", "D", "X", "Y", "S", "T", "K", "L"))
        & (F.col("mode") == "SERIE")
        & ((F.col("uniqueid").like("%BFK%")) | (F.col("uniqueid").like("%SME%")))
        & (F.col("prodnr").isNull())
        & (F.col("karnr").isNotNull())
        & (F.col("transactiontype") == "MEASUREMENT")
        & (F.col("cplant") == "0500")
    )
    .withColumn(
        "fzg_typ_calc",
        F.when(
            F.col("anlage_subtyp").like("%BFK%"),
            F.split(F.col("anlage_subtyp"), "_")[1],
        )
        .when(
            F.col("anlage_subtyp").like("%AMG%"),
            F.split(F.col("anlage_subtyp"), "_")[0],
        )
        .when(
            F.col("anlage_subtyp").like("%SMA%"),
            F.split(F.col("anlage_subtyp"), "_")[0],
        )
        .when(
            F.col("anlage_subtyp").like("%SME%"),
            F.split(F.col("anlage_subtyp"), "_")[1],
        ),
    )
    .withColumn(
        "origin",
        F.when(F.col("uniqueid").like("%BFK%"), "Bodyshop")
        .when(F.col("uniqueid").like("%SME%"), "BS-Z4")
        .otherwise("Rest"),
    )
    .withColumn("messwerttyp_calc", col("messwerttyp"))
)

# Union the two DataFrames
tb_iqvis = tb_iqvis_tra_1.unionByName(tb_iqvis_tra_2)

# Use DISTINCT
tb_iqvis = tb_iqvis.distinct()

# Show the resulting DataFrame
tb_iqvis.display(truncate=False)

# COMMAND ----------

check_df = tb_iqvis.filter(col("origin") == "Bodyshop")
check_df.display()

# COMMAND ----------


# MAGIC ##test_df

# COMMAND ----------

# Perform the inner join
# Alias the DataFrames inline during join
test_df = tb_iqvis.alias("iqv").join(tb_id.alias("id"), tb_iqvis["karnr"] == tb_id["karnr"], "inner")

# Selecting and renaming columns, keeping tb_iqvis naming
test_df = test_df.select(
    col("iqv.messwerttyp_calc").alias("measurement_featurename"),
    col("iqv.messwert").alias("measurement_value"),
    col("iqv.timestamp"),
    col("id.karnr").alias("header_measurement_productionids_2"),
    col("id.prodnr").alias("header_measurement_productionids_1"),
    col("iqv.origin"),
)

# COMMAND ----------


# MAGIC ##final_df

# COMMAND ----------

# define the window specification for the row number operation
windowSpec = Window.partitionBy(
    "measurement_featurename",
    "header_measurement_productionids_2",
    "header_measurement_productionids_1",
    "origin",
).orderBy(F.desc("timestamp"))

# Apply the ROW_NUMBER() function
ranked_df = test_df.withColumn("rownum", F.row_number().over(windowSpec))

# Filter to keep only the first row per partition
filtered_df = ranked_df.filter(F.col("rownum") == 1).drop("rownum")

# Perform the pivot operation
pivoted_df = (
    filtered_df.groupBy(
        "measurement_featurename",
        "header_measurement_productionids_2",
        "header_measurement_productionids_1",
    )
    .pivot("origin", ["Bodyshop", "Assembly"])
    .agg(F.avg("measurement_value").alias("messwert_new"))
)

# Calculate the difference between assembly and bodyshop, casting the result to float
final_df = pivoted_df.withColumn(
    "calc", (F.col("Assembly") - F.col("Bodyshop")).cast("float")
)

# Filter rows where either bodyshop or assembly is null
final_df = final_df.filter(
    F.col("Bodyshop").isNotNull() & F.col("Assembly").isNotNull()
)

# Show the resulting DataFrame
final_df.display(truncate=False)

# COMMAND ----------


# MAGIC #Save as a table

# COMMAND ----------

# save as table in unity catalog
# Define environment stage from notebook widget
dbutils.widgets.dropdown(
    "env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage"
)
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
schema = "proddshbrd_01_emea_dbf_transformation"

# COMMAND ----------

# save as table in unity catalog
final_df.write.saveAsTable(
    f"`{catalog}`.`{schema}`.tra_dbf_0500_korrelation", mode="overwrite"
)
