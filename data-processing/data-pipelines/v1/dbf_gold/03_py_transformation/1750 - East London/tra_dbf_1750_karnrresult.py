# Databricks notebook source
# MAGIC %md
# MAGIC #Load Data

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    regexp_replace,
    expr,
    sum as _sum,
    substring,
    date_sub,
    lit,
    when,
    split,
    row_number,
    avg,
    count,
    countDistinct,
    current_date,
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

processed_iqvis.display()
tb_einrichtpunkte_baureihe_dbf_1750.display()

# COMMAND ----------

# MAGIC %md
# MAGIC #tb_iqvis

# COMMAND ----------

# MAGIC %md
# MAGIC ## Logic for `messwerttyp_calc`

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
processed_iqvis = processed_iqvis.withColumn("messwerttyp_calc", col("messwerttyp"))

# COMMAND ----------

# DBTITLE 1,Check result
check_df = processed_iqvis.where(col("messwerttyp").like("%5-6_4LG%"))
check_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ##Determine `fzg_typ_calc`

# COMMAND ----------

# Apply transformations to create fzg_typ_calc

processed_iqvis = processed_iqvis.withColumn(
    "fzg_typ_calc",
    regexp_replace(col("fzg_typ"), " ", "")
)

# COMMAND ----------

# DBTITLE 1,Check result
check_df = processed_iqvis.filter(col("anlage_subtyp").like("%SME%"))
check_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ##Determine `origin`

# COMMAND ----------


def calculate_origin(column):
    return (
        when(col(column).like("%SMA%"), "Assembly")
        .when(col(column).like("%BFK%"), lit("Bodyshop"))
        .when(col(column).like("%SME%"), lit("BS-Z4"))
        .otherwise("Rest")
    )


# Apply transformation
processed_iqvis = processed_iqvis.withColumn("origin", calculate_origin("uniqueid"))

# COMMAND ----------

# DBTITLE 1,Check result
check_df = processed_iqvis.where(col("uniqueid").like("%BFK%"))
check_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ##Determine `punkt` in mapping

# COMMAND ----------

# Add new columns using the defined transformations
tb_einrichtpunkte_baureihe_dbf_1750 = tb_einrichtpunkte_baureihe_dbf_1750.withColumn(
    "punkt",
    F.when(F.col("einrichtpunkte") == 1, "Einrichtpunkt").otherwise("Kontrollpunkt"),
)


# COMMAND ----------

# MAGIC %md
# MAGIC ##Apply filter SMA

# COMMAND ----------

# DBTITLE 1,Filter case SMA
# Apply filtering conditions
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

# DBTITLE 1,Join condition SMA

# Join conditions
join_condition_sma = (
    (
        expr("substring(messwerttyp_calc, 1, length(messwerttyp_calc) - 1)")
        == tb_einrichtpunkte_baureihe_dbf_1750["messwerttyp"]
    ) &
    (
        processed_iqvis_filtered_sma["fzg_typ"]
        == tb_einrichtpunkte_baureihe_dbf_1750["fzg_typ"]
    )
    & (
        processed_iqvis_filtered_sma["origin"]
        == tb_einrichtpunkte_baureihe_dbf_1750["origin"]
    )
)

# COMMAND ----------

# DBTITLE 1,Perform join SMA
# Perform the left join and select distinct records
join_result_sma = (
    processed_iqvis_filtered_sma.alias("t1")
    .join(tb_einrichtpunkte_baureihe_dbf_1750, join_condition_sma, "left")
    .distinct()
)

# select only relevant columns that comes from processed_iqvis_filtered_sma
join_result_sma = join_result_sma.select(
    "t1.anlage",
    "t1.anlage_subtyp",
    "t1.process_step",
    "t1.mode",
    "t1.poorest_rating_meas_point",
    "t1.component",
    "t1.offset",
    "t1.timestamp",
    "t1.prodnr",
    "t1.karnr",
    "t1.result",
    "t1.messwerttyp",
    "t1.messwert",
    "t1.messwert_toleranz_min",
    "t1.messwert_toleranz_sec_min",
    "t1.messwert_toleranz_max",
    "t1.messwert_toleranz_sec_max",
    "t1.error_code",
    "t1.error_text",
    "t1.transactiontype",
    "t1.cplant",
    "t1.cmonth",
    "t1.origin",
    "fzg_typ_calc",
    "punkt",
)

# COMMAND ----------

# MAGIC %md
# MAGIC ###Filter case BFK and SME

# COMMAND ----------

# Apply filtering conditions
processed_iqvis_filtered_bfk_sme = processed_iqvis.filter(
    # (col("cmonth") >= split(lit("DATE_SUB(CURRENT_DATE, 50)"), "-")[0]) &
    col("component").isin("F", "G", "Z", "D", "X", "Y", "S", "T", "K", "L")
    & (col("mode") == "SERIE")
    & (col("uniqueid").like("%BFK%"))
    | (col("uniqueid").like("%SME%"))
    & col("prodnr").isNull()
    & col("karnr").isNotNull()
    & (col("transactiontype") == "MEASUREMENT")
    & (col("cplant") == "1750")
)


# COMMAND ----------

# MAGIC %md
# MAGIC ###Join condition BFK and SME

# COMMAND ----------

# Join conditions
join_condition_bfk_sme = (
    (
        expr("substring(messwerttyp_calc, 1, length(messwerttyp_calc) - 1)")
        == tb_einrichtpunkte_baureihe_dbf_1750["messwerttyp"]
    ) &
    (
        processed_iqvis_filtered_bfk_sme["fzg_typ"]
        == tb_einrichtpunkte_baureihe_dbf_1750["fzg_typ"]
    )
    & (
        processed_iqvis_filtered_bfk_sme["origin"]
        == tb_einrichtpunkte_baureihe_dbf_1750["origin"]
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ###Perform join BFK and SME

# COMMAND ----------

# Perform the left join and select distinct records
join_result_bfk_sme = (
    processed_iqvis_filtered_bfk_sme.alias("t1")
    .join(tb_einrichtpunkte_baureihe_dbf_1750, join_condition_bfk_sme, "left")
    .distinct()
)

# select only relevant columns that comes from processed_iqvis_filtered_sma
join_result_bfk_sme = join_result_bfk_sme.select(
    "t1.anlage",
    "t1.anlage_subtyp",
    "t1.process_step",
    "t1.mode",
    "t1.poorest_rating_meas_point",
    "t1.component",
    "t1.offset",
    "t1.timestamp",
    "t1.prodnr",
    "t1.karnr",
    "t1.result",
    "t1.messwerttyp",
    "t1.messwert",
    "t1.messwert_toleranz_min",
    "t1.messwert_toleranz_sec_min",
    "t1.messwert_toleranz_max",
    "t1.messwert_toleranz_sec_max",
    "t1.error_code",
    "t1.error_text",
    "t1.transactiontype",
    "t1.cplant",
    "t1.cmonth",
    "t1.origin",
    "fzg_typ_calc",
    "punkt",
)

# COMMAND ----------

check_df = join_result_bfk_sme.filter(
    (col("punkt").isNotNull()) & (col("origin") == "Bodyshop")
)
check_df.display()


# COMMAND ----------

# MAGIC %md
# MAGIC ##Perform union

# COMMAND ----------

iqvis_final = join_result_sma.unionByName(join_result_bfk_sme)

iqvis_final.display()

# COMMAND ----------

# MAGIC %md
# MAGIC #Determine punkt in final iqvis

# COMMAND ----------

iqvis_final = iqvis_final.withColumn(
    "punkt", when(col("punkt").isNull(), "Kontrollpunkt").otherwise(col("punkt"))
)

iqvis_final.display()

# COMMAND ----------

# MAGIC %md
# MAGIC #tb_result

# COMMAND ----------

# Add 'result' and 'seite' columns
tb_iqvis_transformed = iqvis_final.withColumn(
    "result",
    F.when(
        F.col("messwert").cast("float")
        >= F.col("messwert_toleranz_sec_max").cast("float"),
        "NOK",
    )
    .when(
        F.col("messwert").cast("float")
        <= F.col("messwert_toleranz_sec_min").cast("float"),
        "NOK",
    )
    .otherwise("OK"),
).withColumn(
    "seite",
    F.when(F.col("messwerttyp").like("%L%"), "Links")
    .when(F.col("messwerttyp").like("%R%"), "Rechts")
    .otherwise("Rest"),
)

# Select distinct combinations
distinct_df = tb_iqvis_transformed.select(
    "karnr", "punkt", "origin", "seite"
).distinct()

distinct_df.display()

# COMMAND ----------

# Group by and count occurrences
grouped_df = distinct_df.groupBy("karnr", "punkt", "origin", "seite").agg(
    F.count("*").alias("counter")
)

grouped_df.display()

# COMMAND ----------

check_df = grouped_df.filter(col("counter") > 1)
check_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ##tb_result_final

# COMMAND ----------

# Final transformation with case logic for fahrzeugresult_karno
tb_result_final_df = (
    grouped_df.withColumnRenamed("karnr", "header_measurement_productionids_2")
    .withColumn(
        "fahrzeugresult_karno",
        F.when(F.col("counter") > 1, "NOK")
        .when(F.col("counter") == 1, "OK")
        .otherwise("NULL"),
    )
    .select(
        "header_measurement_productionids_2",
        "punkt",
        "origin",
        "seite",
        "fahrzeugresult_karno",
        "counter",
    )
)

tb_result_final_df.display()

# COMMAND ----------

# check result

check_df = tb_result_final_df.where(col("fahrzeugresult_karno").like("%NOK%"))
check_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC #tb_result_overall

# COMMAND ----------

# Calculate `nok_count`
tb_result_nok = (
    tb_result_final_df.withColumn(
        "nok_count", when(col("fahrzeugresult_karno") == "NOK", 1).otherwise(0)
    )
    .select(
        "header_measurement_productionids_2",
        "punkt",
        "origin",
        "fahrzeugresult_karno",
        "nok_count",
    )
    .distinct()
)

# Aggregate to get the sum of nok_count as counter
tb_result_grouped = tb_result_nok.groupBy(
    "header_measurement_productionids_2", "punkt", "origin"
).agg(_sum("nok_count").alias("counter"))

# Assign fahrzeugresult_overall based on counter
tb_result_overall = tb_result_grouped.withColumn(
    "fahrzeugresult_overall",
    when(col("counter") >= 1, "NOK").when(col("counter") < 1, "OK").otherwise("NULL"),
).select(
    "header_measurement_productionids_2", "punkt", "origin", "fahrzeugresult_overall"
)

# COMMAND ----------

check_df = tb_result_overall.where(col("fahrzeugresult_overall").like("%NOK%"))
check_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC #tb_final

# COMMAND ----------

tb_final = tb_result_final_df.join(
    tb_result_overall,
    on=[
        tb_result_final_df["header_measurement_productionids_2"]
        == tb_result_overall["header_measurement_productionids_2"],
        tb_result_final_df["punkt"] == tb_result_overall["punkt"],
        tb_result_final_df["origin"] == tb_result_overall["origin"],
    ],
    how="left",
).select(tb_result_final_df["*"], tb_result_overall["fahrzeugresult_overall"])

# COMMAND ----------

check_df = tb_final
check_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC #Save as table

# COMMAND ----------

# Define environment stage
dbutils.widgets.dropdown(
    "env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage"
)
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
transformation_schema = "proddshbrd_01_emea_dbf_transformation"

# save as table in unity catalog
tb_final.write.saveAsTable(
    f"`{catalog}`.`{transformation_schema}`.tra_dbf_1750_karnrresult", mode="overwrite"
)
