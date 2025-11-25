# Databricks notebook source
# Load Data

# COMMAND ----------

# --- Imports ---
from pyspark.sql import SparkSession
from pyspark.sql.functions import expr, from_utc_timestamp, date_format
from pyspark.sql.functions import (
    col,
    substring,
    date_sub,
    lit,
    when,
    split,
    row_number,
    avg,
    count,
    countDistinct,
)
from pyspark.sql.window import Window
from pyspark.sql import functions as F

# Load tables (from unity schema) -->
# Define environment stage from notebook widget
dbutils.widgets.dropdown(
    "env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage"
)
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
processed_schema = "proddshbrd_01_emea_dbf_source_data"
mapping_schema = "proddshbrd_01_emea_dbf_mappings"

# COMMAND ----------

processed_iqvis = spark.table(f"`{catalog}`.`{processed_schema}`.processed_iqvis")
tb_einrichtpunkte_baureihe_dbf_0540 = spark.table(
    f"`{catalog}`.`{mapping_schema}`.tb_einrichtpunkte_baureihe_dbf_0540"
)

# COMMAND ----------


# tb_iqvis

# COMMAND ----------


# Logic for `messwerttyp_calc`

# COMMAND ----------

# # Define a function to apply the complex CASE logic for `messwerttyp_calc` ---> for 1380 only
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

# # Show results
# processed_iqvis.select("messwerttyp", "messwerttyp_calc").show(10, truncate=False)


# Logic for `fzg_typ_calc`

# COMMAND ----------

# Apply transformations to create fzg_typ_calc
processed_iqvis = processed_iqvis.withColumn("fzg_typ_calc", col("fzg_typ"))


# Logic for `origin`

# COMMAND ----------

# Apply transformation to create origin
processed_iqvis = processed_iqvis.withColumn(
    "origin",
    when(col("uniqueid").like("%SMA%"), lit("Assembly"))
    .when(col("uniqueid").like("%BFK%"), lit("Bodyshop"))
    .when(col("uniqueid").like("%SME%"), lit("Assembly"))
    .otherwise(lit("Rest")),  # Default case
)


# Logic for filter

# COMMAND ----------

# DBTITLE 1,Filter case BFK & SME
# Apply filtering conditions
processed_iqvis_filtered_sma = processed_iqvis.filter(
    # (col("cmonth") >= split(lit("DATE_SUB(CURRENT_DATE, 50)"), "-")[0]) &
    col("component").isin("F", "G", "Z", "D", "X", "Y", "S", "T", "K", "L")
    & (col("mode") == "SERIE")
    & (col("uniqueid").like("%SMA%"))
    & col("prodnr").isNotNull()
    & col("karnr").isNotNull()
    & (col("transactiontype") == "MEASUREMENT")
    & (col("cplant") == "0540")
)

# ((col("uniqueid").like("%SMA%")) |
#  (col("uniqueid").like("%BFK%")) |
#  (col("uniqueid").like("%SME%"))) &

# Apply filtering conditions
processed_iqvis_filtered_rest = processed_iqvis.filter(
    # (col("cmonth") >= split(lit("DATE_SUB(CURRENT_DATE, 50)"), "-")[0]) &
    col("component").isin("F", "G", "Z", "D", "X", "Y", "S", "T", "K", "L")
    & (col("mode") == "SERIE")
    & ((col("uniqueid").like("%BFK%")) | (col("uniqueid").like("%SME%")))
    & col("prodnr").isNull()
    & col("karnr").isNotNull()
    & (col("transactiontype") == "MEASUREMENT")
    & (col("cplant") == "0540")
)

# Note: Es gibt keine SME

# COMMAND ----------


# Union filter case

# COMMAND ----------

# DBTITLE 1,Union
iqvis_final = processed_iqvis_filtered_sma.union(
    processed_iqvis_filtered_rest
).distinct()


# tb_einrichpunkte

# COMMAND ----------

tb_einrichpunkte = tb_einrichtpunkte_baureihe_dbf_0540.select(
    col("messwerttyp"),
    col("fzg_typ"),
    col("origin"),
    when(col("einrichtpunkte") == 1, "Einrichtpunkt")
    .otherwise("Kontrollpunkt")
    .alias("punkt"),
)


# tb_lastpoint

# COMMAND ----------

# Compute tb_lastpoint
tb_lastpoint = (
    iqvis_final.select("karnr").distinct().withColumn("lastmeasure", lit("vollständig"))
)


# tb_prodnumber

# COMMAND ----------

# Apply transformations
tb_prodnumber = (
    processed_iqvis.filter(
        (col("prodnr").isNotNull())
        & (col("karnr").isNotNull())
        & (col("cplant") == "0540")
        & (col("mode") == "SERIE")
    )
    .select(col("prodnr"), col("karnr"), col("fzg_typ"))
    .distinct()  # Equivalent to SELECT DISTINCT
)


# Final table

# COMMAND ----------


# Perform LEFT JOIN

# COMMAND ----------

# Perform LEFT JOIN with tb_einrichpunkte
df_joined = (
    iqvis_final.alias("iq")
    .join(
        tb_einrichpunkte.alias("ep"),
        (col("iq.origin") == col("ep.origin"))
        & (col("iq.fzg_typ") == col("ep.fzg_typ"))
        & (col("iq.messwerttyp") == col("ep.messwerttyp")),
        "left",
    )
    .join(
        tb_prodnumber.alias("pn"),
        (col("iq.fzg_typ") == col("pn.fzg_typ")) & (col("iq.karnr") == col("pn.karnr")),
        "left",
    )
)

# COMMAND ----------

# DBTITLE 1,Apply CASE WHEN for header_measurement_productionids_1
df_joined = df_joined.withColumn(
    "header_measurement_productionids_1",
    when(col("iq.prodnr").isNull(), col("pn.prodnr")).otherwise(col("iq.prodnr")),
)

# COMMAND ----------

# DBTITLE 1,Apply FROM_UTC_TIMESTAMP() for header_measurement_meastime

df_joined = df_joined.withColumn("header_measurement_meastime", col("iq.timestamp"))

# COMMAND ----------

# DBTITLE 1,Apply DATE and INTERVAL Logic for ingest_date

df_joined = df_joined.withColumn("ingest_date", col("iq.timestamp"))

# COMMAND ----------

# DBTITLE 1,Apply DATE_FORMAT() for produktionsstunde


df_joined = df_joined.withColumn(
    "produktionsstunde", date_format(col("timestamp"), "HH")
)

# COMMAND ----------

# DBTITLE 1,Apply CASE WHEN for result
df_joined = df_joined.withColumn(
    "result",
    when(col("iq.messwert").isNull(), "NOK")
    .when(
        col("iq.messwert").cast("float")
        > col("iq.messwert_toleranz_sec_max").cast("float"),
        "NOK",
    )
    .when(
        col("iq.messwert").cast("float")
        < col("iq.messwert_toleranz_sec_min").cast("float"),
        "NOK",
    )
    .otherwise("OK"),
)


# COMMAND ----------

# DBTITLE 1,Apply CASE WHEN for kennerfuge python Copy Edit
df_joined = df_joined.withColumn(
    "kennerfuge",
    when(col("iq.messwerttyp").like("1_1%"), "1_1")
    .when(col("iq.messwerttyp").like("1-10%"), "1-10")
    .when(col("iq.messwerttyp").like("1-4%"), "1-4")
    .when(col("iq.messwerttyp").like("1-5%"), "1-5")
    .when(col("iq.messwerttyp").like("1-6%"), "1-6")
    .when(col("iq.messwerttyp").like("1-7%"), "1-7")
    .when(col("iq.messwerttyp").like("1-8%"), "1-8")
    .when(col("iq.messwerttyp").like("5-6%"), "5-6")
    .when(col("iq.messwerttyp").like("6-6%"), "6-6")
    .when(col("iq.messwerttyp").like("6-7%"), "6-7")
    .when(col("iq.messwerttyp").like("7-8%"), "7-8")
    .when(col("iq.messwerttyp").like("8-8%"), "8-8")
    .when(col("iq.messwerttyp").like("8-1%"), "8-1")
    .otherwise("Rest"),
)

# COMMAND ----------

# DBTITLE 1,Apply CASE WHEN for seite
df_joined = df_joined.withColumn(
    "seite",
    when(col("iq.messwerttyp").like("%L%"), "Links")
    .when(col("iq.messwerttyp").like("%R%"), "Rechts")
    .otherwise("Rest"),
)

# COMMAND ----------

# DBTITLE 1,Apply CASE WHEN for kennerfg
df_joined = df_joined.withColumn(
    "kennerfg",
    when(col("iq.messwerttyp").like("%F%"), "Flush")
    .when(col("iq.messwerttyp").like("%G%"), "Gap")
    .otherwise("Rest"),
)

# COMMAND ----------

# DBTITLE 1,Apply CASE WHEN for over_under
df_joined = df_joined.withColumn(
    "over_under",
    when(col("iq.messwert") < col("iq.messwert_toleranz_sec_min"), "U")
    .when(col("iq.messwert") > col("iq.messwert_toleranz_sec_max"), "O")
    .otherwise("F"),
)

# COMMAND ----------

# DBTITLE 1,Apply Substring Operations
df_joined = (
    df_joined.withColumn(
        "position", col("iq.messwerttyp").substr(-2, 1)  # LEFT(RIGHT(...), 1)
    )
    .withColumn("art", col("iq.messwerttyp").substr(-1, 1))  # RIGHT(...)
    .withColumn(
        "measure",
        expr(
            "LEFT(iq.messwerttyp, LENGTH(iq.messwerttyp) - 2)"
        ),  # LEFT(..., LENGTH(...) - 2)
    )
    .withColumn("name", col("iq.messwerttyp").substr(1, 1))  # LEFT(..., 1)
)


# COMMAND ----------


# Select Final Column

# COMMAND ----------

df_final = df_joined

# COMMAND ----------

df_final = df_joined.select(
    col("iq.anlage_subtyp"),
    col("iq.timestamp"),
    col("iq.offset"),
    col("iq.karnr").alias("header_measurement_productionids_2"),
    col("header_measurement_productionids_1"),
    col("iq.typeseries").alias("baureihe"),
    col("iq.typeseries").alias("header_measurement_typeseries"),
    col("iq.fzg_typ_calc").alias("fzg_typ"),
    col("iq.cplant"),
    col("iq.origin"),
    col("result").alias("result_notcalc"),
    col("punkt"),
    col("pn.prodnr").alias("pd3"),
    col("iq.messwerttyp_calc").alias("measurement_featurename"),
    col("iq.messwert").cast("float").alias("measurement_value"),
    col("header_measurement_meastime"),
    col("ingest_date"),
    col("produktionsstunde"),
    col("header_measurement_productionids_1").cast("int").alias("pd1"),
    col("header_measurement_productionids_2").cast("int").alias("pd2"),
    col("iq.messwert_toleranz_min").cast("float"),
    col("iq.messwert_toleranz_max").cast("float"),
    col("iq.messwert_toleranz_sec_min").cast("float"),
    col("iq.messwert_toleranz_sec_max").cast("float"),
    col("result"),
    col("kennerfuge"),
    col("seite"),
    col("kennerfg"),
    col("over_under"),
    col("position"),
    col("art"),
    col("measure"),
    col("name"),
)


# Save as table

# COMMAND ----------

# save as table in unity catalog
# Define environment stage from notebook widget
dbutils.widgets.dropdown(
    "env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage"
)
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
processed_schema = "proddshbrd_01_emea_dbf_transformation"
df_final.write.saveAsTable(
    f"`{catalog}`.`{processed_schema}`.tra_dbf_0540_main", mode="overwrite"
)
