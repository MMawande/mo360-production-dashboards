# Databricks notebook source
# Load Table

# COMMAND ----------

# --- Imports ---
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    regexp_replace,
    substring,
    date_sub,
    lit,
    when,
    split,
    row_number,
    avg,
    count,
    countDistinct,
    expr,
)
from pyspark.sql.window import Window
from pyspark.sql import functions as F

# Define environment stage
dbutils.widgets.dropdown(
    "env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage"
)
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
mappings_schema = "proddshbrd_01_emea_dbf_mappings"
processed_iqvis_schema = "proddshbrd_01_emea_dbf_source_data"

# Load tables (from unity schema)
processed_iqvis = spark.table(f"`{catalog}`.`{processed_iqvis_schema}`.processed_iqvis")
tb_einrichtpunkte_baureihe_dbf_1750 = spark.table(
    f"`{catalog}`.`{mappings_schema}`.tb_einrichtpunkte_baureihe_dbf_1750"
)

# COMMAND ----------


# tb_iqvis

# COMMAND ----------


# Logic for `messwerttyp_calc`

# COMMAND ----------

# Define a function to apply the complex CASE logic for `messwerttyp_calc` --> for 1380 only
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
#         (column.like('%1-5_RZ610LG%'), '1-5_RZ610LG'),
#         # Add all other conditions here following the same pattern
#     ]

#     # Initialize a when() condition
#     case_expr = when(*conditions[0])

#     # Loop through the rest of the conditions
#     for condition in conditions[1:]:
#         case_expr = case_expr.when(*condition)

#     # Default case: if no match, return the original column
#     return case_expr.otherwise(column)

# Apply the function to create the new column
# processed_iqvis = processed_iqvis.withColumn("messwerttyp_calc", messwerttyp_case(col("messwerttyp"))) --> for 1380 only
processed_iqvis = processed_iqvis.withColumn("messwerttyp_calc", col("messwerttyp"))

# Show results
processed_iqvis.select("messwerttyp", "messwerttyp_calc").show(10, truncate=False)


# COMMAND ----------

# DBTITLE 1,Check result
# check_df = processed_iqvis.where(col("messwerttyp").like ("%5-6_4LG%"))

# check_df.display()

# COMMAND ----------


# Logic for `fzg_typ_calc`

# COMMAND ----------

# Apply transformations to create fzg_typ_calc
# Apply transformations to create fzg_typ_calc

processed_iqvis = processed_iqvis.withColumn(
    "fzg_typ_calc",
    regexp_replace(col("fzg_typ"), " ", "")
)

# COMMAND ----------

# DBTITLE 1,Check result
check_df = processed_iqvis

check_df.display()

# COMMAND ----------


# Logic for `origin`

# COMMAND ----------

# Apply transformation to create origin
processed_iqvis = processed_iqvis.withColumn(
    "origin",
    when(col("uniqueid").like("%SMA%"), lit("Assembly"))
    .when(col("uniqueid").like("%BFK%"), lit("Bodyshop"))
    .when(col("uniqueid").like("%SME%"), lit("BS-Z4"))
    .otherwise(lit("Rest")),  # Default case
)

# COMMAND ----------

# DBTITLE 1,Check result
check_df = processed_iqvis.where(col("uniqueid").like("%BFK%"))
check_df.display()


# COMMAND ----------


# Logic for filter

# COMMAND ----------

# DBTITLE 1,Filter case SMA
# Apply filtering conditions for SMA
processed_iqvis_filtered_sma = processed_iqvis.filter(
    # (col("cmonth") >= split(lit("DATE_SUB(CURRENT_DATE, 50)"), "-")[0]) &
    col("component").isin("F", "G", "Z", "D", "X", "Y", "S", "T", "K", "L")
    & (col("mode") == "SERIE")
    & (col("uniqueid").like("%SMA%"))
    & col("prodnr").isNotNull()
    & col("karnr").isNotNull()
    & (col("transactiontype") == "MEASUREMENT")
    & (col("cplant") == "1750")
)


# COMMAND ----------

processed_iqvis_filtered_sma.display()

# COMMAND ----------

# DBTITLE 1,Filter case BFK & SME
# Apply filtering conditions for SMA and SME
processed_iqvis_filtered_rest = processed_iqvis.filter(
    # (col("cmonth") >= split(lit("DATE_SUB(CURRENT_DATE, 50)"), "-")[0]) &
    col("component").isin("F", "G", "Z", "D", "X", "Y", "S", "T", "K", "L")
    & (col("mode") == "SERIE")
    & ((col("uniqueid").like("%BFK%")) | (col("uniqueid").like("%SME%")))
    & col("prodnr").isNull()
    & col("karnr").isNotNull()
    & (col("transactiontype") == "MEASUREMENT")
    & (col("cplant") == "1750")
)


# COMMAND ----------

# DBTITLE 1,Check result
check_df = processed_iqvis_filtered_rest.where(col("uniqueid").like("%BFK%"))
check_df.display()


# COMMAND ----------


# Union filter case

# COMMAND ----------

# DBTITLE 1,Union
iqvis_final = processed_iqvis_filtered_sma.unionByName(processed_iqvis_filtered_rest)

# COMMAND ----------

check_df = iqvis_final.where(col("uniqueid").like("%BFK%"))
check_df.display()

# COMMAND ----------


# tb_einrichtpunkte

# COMMAND ----------

# DBTITLE 1,Transform logic
tb_einrichpunkte = tb_einrichtpunkte_baureihe_dbf_1750.select(
    col("messwerttyp"),
    col("fzg_typ"),
    col("origin"),
    when(col("einrichtpunkte") == 1, "Einrichtpunkt")
    .otherwise("Kontrollpunkt")
    .alias("punkt"),
)

# COMMAND ----------

# DBTITLE 1,Check result
check_df = tb_einrichpunkte.where(col("origin").like("%Bodyshop%"))

check_df.display()

# COMMAND ----------


# tb_lastpoint

# COMMAND ----------

# Compute tb_lastpoint
tb_lastpoint = (
    iqvis_final.select("karnr").distinct().withColumn("lastmeasure", lit("vollständig"))
)

# COMMAND ----------

# DBTITLE 1,Check result
check_df = tb_lastpoint
check_df.display()

# COMMAND ----------


# tb_minamount

# COMMAND ----------

# Load the source DataFrame

# Compute tb_minamount
tb_minamount = (
    tb_einrichtpunkte_baureihe_dbf_1750.filter(
        col("einrichtpunkte") == 1
    ).distinct()  # WHERE einrichtpunkte = 1
    .groupBy("fzg_typ", "origin")  # GROUP BY fzg_typ, origin
    .agg(count("messwerttyp").alias("minamount"))  # COUNT(messwerttyp) AS minamount
)


# COMMAND ----------

# DBTITLE 1,Check result
check_df = tb_minamount

check_df.display()

# COMMAND ----------

# DBTITLE 1,Compare with current
# %sql
#     SELECT
#         origin,
#         fzg_typ,
#         COUNT(messwerttyp) AS minamount
#     FROM `hive_metastore`.`proddshbrd_dbt_mappings`.`tb_einrichtpunkte_baureihe_dbf_138`
#     WHERE einrichtpunkte = 1
#     GROUP BY fzg_typ, origin

# COMMAND ----------


# tb_checkallpoints

# COMMAND ----------

# Perform INNER JOIN between tb_iqvis and tb_einrichpunkte
tb_checkallpoints = (
    iqvis_final.alias("iq")
    .join(
        tb_einrichpunkte.alias("ep"),
        (col("iq.origin") == col("ep.origin"))
        & (col("iq.fzg_typ_calc") == col("ep.fzg_typ"))
        & (
            expr("substring(messwerttyp_calc, 1, length(messwerttyp_calc) - 1)")
            == tb_einrichpunkte["messwerttyp"]
        ),
        "inner",
    )
    .join(
        tb_minamount.alias("min"),
        (col("iq.fzg_typ_calc") == col("min.fzg_typ"))
        & (col("iq.origin") == col("min.origin")),
        "inner",
    )
    .filter((col("ep.punkt") == "Einrichtpunkt") & col("iq.messwert").isNotNull())
    .groupBy("iq.karnr", "iq.fzg_typ_calc", "iq.origin", "min.minamount")
    .agg(
        countDistinct(col("iq.messwerttyp_calc")).alias("amount")
    )  # FIXED: Use countDistinct()
    .select(
        col("karnr"),
        col("fzg_typ_calc").alias("fzg_typ"),
        col("origin"),
        when(col("amount") == col("minamount"), "OK")
        .otherwise("NOK")
        .alias("allmeasures"),
    )
)

# COMMAND ----------


# Final table

# COMMAND ----------

# Perform LEFT JOIN between tb_checkallpoints and tb_lastpoint
final_df = (
    tb_checkallpoints.alias("cp")
    .join(
        tb_lastpoint.alias("lp"),
        col("cp.karnr") == col("lp.karnr"),  # Join condition
        "left",  # LEFT JOIN
    )
    .select(
        col("cp.karnr"),
        col("cp.origin"),
        col("cp.allmeasures"),
        col("lp.lastmeasure"),  # Comes from tb_lastpoint
    )
    .distinct()  # Equivalent to SELECT DISTINCT
)

# Display results
final_df.display()

# COMMAND ----------


# Save as a table

# COMMAND ----------

# Define environment stage
dbutils.widgets.dropdown(
    "env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage"
)
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
transformation_schema = "proddshbrd_01_emea_dbf_transformation"

# save as table in unity catalog
final_df.write.saveAsTable(
    f"`{catalog}`.`{transformation_schema}`.tra_dbf_1750_additionalchecks",
    mode="overwrite",
)
