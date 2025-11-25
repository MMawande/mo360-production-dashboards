# Databricks notebook source
# MAGIC %md
# MAGIC ## Run configuration
# MAGIC
# MAGIC The section below adds the required imports and and other utility definitions

# COMMAND ----------

# MAGIC %run ../imports

# COMMAND ----------

import pyspark.sql.functions as f
from datetime import datetime, timedelta
from pyspark.sql import DataFrame
from pyspark.sql.types import IntegerType


# COMMAND ----------


def create_predefined_time_periods(cut_off, start_date=None) -> DataFrame:
    """
    creates a table with three columns, date, period and order, period is divided into 5 categories today, yesterday, 14 days, 30 days adn freie Auswahl
    for every period the included dates in this period are listed seperatly,
    this means the date of today, for example, is listed 4 times, in the today, 14 days, 30 days period and freie Auswahl
    the order column is for sorting in PowerBI
    """
    if cut_off <= 30:
        raise ValueError("cut_off_days_import must be at least greater than 30")
    if start_date is None:
        today = datetime.today().date().strftime("%Y-%m-%d")
        yesterday = (datetime.today().date()-timedelta(days=1)).strftime("%Y-%m-%d")
        end_7 = (datetime.today().date()-timedelta(days=7)).strftime("%Y-%m-%d")
        last_7 = spark.sql(f"select explode(sequence(to_date('{end_7}'), to_date('{yesterday}'), interval 1 day)) as date_iso")
        end_14 = (datetime.today().date()-timedelta(days=14)).strftime("%Y-%m-%d")
        last_14 = spark.sql(f"select explode(sequence(to_date('{end_14}'), to_date('{yesterday}'), interval 1 day)) as date_iso")
        end_30 = (datetime.today().date()-timedelta(days=30)).strftime("%Y-%m-%d")
        last_30 = spark.sql(f"select explode(sequence(to_date('{end_30}'), to_date('{yesterday}'), interval 1 day)) as date_iso")
        end_90 = (datetime.today().date()-timedelta(days=cut_off-1)).strftime("%Y-%m-%d")
        last_90 = spark.sql(f"select explode(sequence(to_date('{end_90}'), to_date('{today}'), interval 1 day)) as date_iso")

        last_2 = spark.createDataFrame([(today, "Heute", "2"),
                                        (yesterday, "Gestern", "1")],
                                       schema=["date_iso", "period", "order"])
    else:
        today = start_date

        yesterday = (start_date-timedelta(days=1)).strftime("%Y-%m-%d")
        end_7 = (start_date-timedelta(days=7)).strftime("%Y-%m-%d")
        last_7 = spark.sql(f"select explode(sequence(to_date('{end_7}'), to_date('{yesterday}'), interval 1 day)) as date_iso")
        end_14 = (start_date-timedelta(days=14)).strftime("%Y-%m-%d")
        last_14 = spark.sql(f"select explode(sequence(to_date('{end_14}'), to_date('{yesterday}'), interval 1 day)) as date_iso")
        end_30 = (start_date-timedelta(days=30)).strftime("%Y-%m-%d")
        last_30 = spark.sql(f"select explode(sequence(to_date('{end_30}'), to_date('{yesterday}'), interval 1 day)) as date_iso")
        end_90 = (start_date-timedelta(days=cut_off-1)).strftime("%Y-%m-%d")
        last_90 = spark.sql(f"select explode(sequence(to_date('{end_90}'), to_date('{today}'), interval 1 day)) as date_iso")

        last_2 = spark.createDataFrame([(today.strftime('%Y-%m-%d'), "Heute", "2"),
                                        (yesterday, "Gestern", "1")],
                                       schema=["date_iso", "period", "order"])

    predefined_periods = (last_2.union(last_7.withColumn("period", f.lit("Letzte 7 Tage")).withColumn("order", f.lit("3")))
                                .union(last_14.withColumn("period", f.lit("Letzte 14 Tage")).withColumn("order", f.lit("4")))
                                .union(last_30.withColumn("period", f.lit("Letzte 30 Tage")).withColumn("order", f.lit("5")))
                                .union(last_90.withColumn("period", f.lit("freie Auswahl")).withColumn("order", f.lit("6")))
                                .withColumn("period_de", f.col("period"))
                                .withColumn("period_en", f.when(f.col("period") == "Heute", "Today")
                                                          .when(f.col("period") == "Gestern", "Yesterday")
                                                          .when(f.col("period") == "Letzte 7 Tage", "Last 7 Days")
                                                          .when(f.col("period") == "Letzte 14 Tage", "Last 14 Days")
                                                          .when(f.col("period") == "Letzte 30 Tage", "Last 30 Days")
                                                          .when(f.col("period") == "freie Auswahl", "Free Selection")
                                            )
                                .withColumn("date_key_iso", f.date_format(f.col("date_iso"), "yyyyMMdd").cast("int"))
                                .withColumn("date_iso", f.to_date("date_iso")))

    return predefined_periods

# COMMAND ----------


dbutils.widgets.dropdown(
    "display_results", "False", ["True", "False"], "Display Results"
)
dbutils.widgets.dropdown("write_output", "True", ["True", "False"], "Write Output")
dbutils.widgets.text(
    "config_path",
    "/Workspace/data-pipelines/v1/999_config/etl-dev.jsonc",
    "Configuration Path",
)

# COMMAND ----------

mo_config_mngr = MO360DPConfigManager(
    dbutils.widgets.get("config_path"), MO360DPDatabricksUtils.get_version()
)
logger = mo_config_mngr.setup_logging()
mo_dbutils = MO360DPDatabricksUtils(mo_config_mngr.get_constant("usecaseName"), logger)

# COMMAND ----------

display_results = dbutils.widgets.get("display_results") == "True"
write_output = dbutils.widgets.get("write_output") == "True"

# COMMAND ----------

today = datetime.today()
cut_off = mo_config_mngr.get_constant("cut_off_date_in_days")
cut_off_period = mo_config_mngr.get_constant("cut_off_date_in_days")

cut_off_days_import = (today - timedelta(days=mo_config_mngr.get_constant("cut_off_date_in_days"))).date()

df_date_dimension = create_rolling_date_dimension(1 - cut_off, 0)
df_predefined_periods = create_predefined_time_periods(cut_off_period, start_date=today)

df_predefined_periods = df_predefined_periods.withColumn("order", df_predefined_periods["order"].cast(IntegerType()))

df_date_dimension = (df_date_dimension
                     .withColumn("day", df_date_dimension["day"].cast(IntegerType()))
                     .withColumn("month", df_date_dimension["month"].cast(IntegerType()))
                     .withColumn("year", df_date_dimension["year"].cast(IntegerType()))
                     .withColumn("day_of_year", df_date_dimension["day_of_year"].cast(IntegerType()))
                     )
# COMMAND ----------

# Define environment stage from notebook widget
dbutils.widgets.dropdown("env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage")
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
schema = "proddshbrd_01_emea_dbf_source_data"

# COMMAND ----------

df_date_dimension.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"`{catalog}`.`{schema}`.dim_date")
df_predefined_periods.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"`{catalog}`.`{schema}`.dim_predefined_periods")
