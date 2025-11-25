# Databricks notebook source
from pyspark.sql.types import StringType, StructField, StructType, DoubleType, TimestampType
from pyspark.sql import DataFrame
import pyspark.sql.functions as f
import pyspark.sql.types as t

# COMMAND ----------

IQVIS = StructType(
    [
        StructField(
            "header",
            StructType(
                [
                    StructField(
                        "authentification",
                        StructType(
                            [
                                StructField("client", StringType()),
                                StructField("clientversion", StringType()),
                                StructField("iqvisuser", StringType()),
                                StructField("user", StringType()),
                            ]
                        ),
                    ),
                    StructField("filename", StringType()),
                    StructField(
                        "measurement",
                        StructType(
                            [
                                StructField(
                                    "attributes",
                                    StructType(
                                        [
                                            StructField("measid", StringType()),
                                            StructField("mode", StringType()),
                                            StructField("plc-code", StringType()),
                                            StructField("rating", StringType()),
                                            StructField("process-step", StringType()),
                                        ]
                                    ),
                                ),
                                StructField("inspectionplan", StringType()),
                                StructField("meastime", StringType()),
                                StructField("model", StringType()),
                                StructField(
                                    "productionids",
                                    StructType(
                                        [
                                            StructField("1", StringType()),
                                            StructField("2", StringType()),
                                        ]
                                    ),
                                ),
                                StructField(
                                    "statussummary",
                                    StructType(
                                        [
                                            StructField(
                                                "failed-calculation", StringType()
                                            ),
                                            StructField(
                                                "failed-measurement", StringType()
                                            ),
                                            StructField(
                                                "features-to-measure", StringType()
                                            ),
                                        ]
                                    ),
                                ),
                                StructField("system", StringType()),
                                StructField("typeseries", StringType()),
                            ]
                        ),
                    ),
                ]
            ),
        ),
        StructField(
            "measurement",
            StructType(
                [
                    StructField(
                        "attributes",
                        StructType(
                            [
                                StructField("analysis-strategy", StringType()),
                                StructField("calctype", StringType()),
                            ]
                        ),
                    ),
                    StructField("component", StringType()),
                    StructField(
                        "details",
                        StructType(
                            [
                                StructField("offset", StringType()),
                                StructField("stddev", StringType()),
                                StructField("target", StringType()),
                                StructField("unit", StringType()),
                            ]
                        ),
                    ),
                    StructField("featurename", StringType()),
                    StructField(
                        "limits",
                        StructType(
                            [
                                StructField(
                                    "1",
                                    StructType(
                                        [
                                            StructField("lower", StringType()),
                                            StructField("upper", StringType()),
                                        ]
                                    ),
                                ),
                                StructField(
                                    "2",
                                    StructType(
                                        [
                                            StructField("lower", StringType()),
                                            StructField("upper", StringType()),
                                        ]
                                    ),
                                ),
                                StructField(
                                    "3",
                                    StructType(
                                        [
                                            StructField("lower", StringType()),
                                            StructField("upper", StringType()),
                                        ]
                                    ),
                                ),
                            ]
                        ),
                    ),
                    StructField("rating", StringType()),
                    StructField(
                        "status",
                        StructType(
                            [
                                StructField("calcstatus", StringType()),
                                StructField("measstatus", StringType()),
                                StructField("measured", StringType()),
                                StructField("rating", StringType()),
                            ]
                        ),
                    ),
                    StructField("value", StringType()),
                ]
            ),
        ),
    ]
)

ANLAGE = StructType(
    [
        StructField("$", StructType([StructField("desc", StringType())])),
        StructField("_", StringType()),
    ]
)

REVERSED_ANLAGE_SUBTYP = [
    "W214_SME_Bau46",
    "X254_SME_Bau46",
    "X254_SME_Bau30",
    "BFK_X167_FD_RE",
    "BFK_C167_RT_M2",
    "BFK_V167_FD_LI_M2",
    "BFK_C167_MH_M2",
    "BFK_V167_FA_RE_M2",
    "BFK_X167_FA_LI",
    "BFK_C167_FD_LI_M2",
    "BFK_C167_FA_LI_M2",
    "BFK_V167_FA_LI_M2",
    "BFK_V167_FD_RE_M2",
    "BFK_V167_KV_LI_M1",
    "BFK_V167_RT_M2",
    "BFK_X167_RT",
    "BFK_X167_FD_LI",
    "BFK_V167_FA_RE_M1",
    "BFK_V167_MH_M2",
    "BFK_C167_FA_RE_M2",
    "BFK_C167_FD_RE_M2",
    "BFK_V167_MH_M1",
    "BFK_V167_FD_RE_M1",
    "BFK_V167_KV_LI_M2",
    "BFK_V167_KV_RE_M1",
    "BFK_X167_KV_LI",
    "BFK_V167_FA_LI_M1",
    "BFK_V167_RT_M1",
    "BFK_X167_KV_RE",
    "BFK_V167_KV_RE_M2",
    "BFK_X167_FA_RE",
    "BFK_C167_KV_RE_M2",
    "BFK_X167_MH",
    "BFK_C167_KV_LI_M2",
    "BFK_V167_FD_LI_M1",
    "C167_SMA",
    "SME_X294",
    "SME_X296",
    "Sensortest_SMA",
    "V167_AMG",
    "V167_SMA",
    "X167_AMG",
    "X167_SMA",
]

COLUMNS = [
    "anlage",
    "anlage_subtyp",
    "process_step",
    "mode",
    "poorest_rating_meas_point",
    "component",
    "offset",
    "timestamp",
    "prodnr",
    "karnr",
    "result",
    "messwerttyp",
    "messwert",
    "messwert_toleranz_min",
    "messwert_toleranz_sec_min",
    "messwert_toleranz_max",
    "messwert_toleranz_sec_max",
    "error_code",
    "error_text",
    "transactiontype",
    "cplant",
    "cmonth",
]

# COMMAND ----------


def iqvis_transformation(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("cplant", f.split(f.col("MSBTopic"), "/")[7])
        .withColumn("cmonth", f.concat_ws("-", f.year(f.to_date(f.col("ingest_date"))), f.month(f.to_date(f.col("ingest_date")))))
        .withColumn("cyear", f.year(f.to_date(f.col("ingest_date"))))
        .filter(f.col("type") == "IQVIS")
        .filter(f.col("subtype") == "IMT")
        .filter(f.col("transactiontype").isin(["MEASUREMENT", "MEASUREMENT_W138"]))
        .filter(f.col("cplant").isin(["1750", "0670", "1380", "0540", "0500"]))
        .withColumn("body", f.from_json(f.col("body"), IQVIS))
        .filter(f.col("body.header.measurement.meastime").isNotNull())
        .withColumn("anlage", f.lit("Fugen"))
        .withColumn(
            "anlage_subtyp",
            f.when(
                f.col("body.header.measurement.inspectionplan").startswith("{"),
                f.from_json(
                    f.col("body.header.measurement.inspectionplan"), ANLAGE
                )["$"]["desc"],
            ).otherwise(f.col("body.header.measurement.inspectionplan")),
        )
        .withColumn(
            "prodnr",
            f.when(
                f.col("anlage_subtyp").isin(REVERSED_ANLAGE_SUBTYP),
                f.when(
                    f.length(
                        f.split(
                            f.col("body.header.measurement.productionids.2"), "_"
                        )[0]
                    )
                    >= 7,
                    f.split(f.col("body.header.measurement.productionids.2"), "_")[
                        0
                    ],
                ),
            ).otherwise(
                f.when(
                    f.length(
                        f.split(
                            f.col("body.header.measurement.productionids.1"), "_"
                        )[0]
                    )
                    >= 7,
                    f.split(f.col("body.header.measurement.productionids.1"), "_")[
                        0
                    ],
                )
            ),
        )
        .withColumn(
            "karnr",
            f.when(
                f.col("anlage_subtyp").isin(REVERSED_ANLAGE_SUBTYP),
                f.when(
                    f.length(
                        f.split(
                            f.col("body.header.measurement.productionids.1"), "_"
                        )[0]
                    )
                    >= 7,
                    f.split(f.col("body.header.measurement.productionids.1"), "_")[
                        0
                    ],
                ),
            ).otherwise(
                f.when(
                    f.length(
                        f.split(
                            f.col("body.header.measurement.productionids.2"), "_"
                        )[0]
                    )
                    >= 7,
                    f.split(f.col("body.header.measurement.productionids.2"), "_")[
                        0
                    ],
                )
            ),
        )
        .filter(f.col("prodnr").isNotNull() | f.col("karnr").isNotNull())
        .withColumn(
            "process_step", f.col("body.header.measurement.attributes.process-step")
        )
        .withColumn("mode", f.col("body.header.measurement.attributes.mode"))
        .withColumn("model", f.col("body.header.measurement.model"))
        .withColumn(
            "typeseries",
            f.regexp_extract(
                f.col("body.header.measurement.typeseries"), r"(\d{3})", 1
            ),
        )
        .withColumn(
            "fzg_typ",
            f.when(f.col("typeseries") == "", None)
            .when(
                f.length(f.rtrim(f.col("model"))) == 1,
                f.concat(f.col("model"), f.col("typeseries")),
            )
            .otherwise(None),
        )
        .withColumn("component", f.col("body.measurement.component"))
        .withColumn(
            "messwerttyp",
            f.concat(f.col("body.measurement.featurename"), f.col("component")),
        )
        .withColumn("messwert", f.col("body.measurement.value").cast(DoubleType()))
        .withColumn(
            "messwert_toleranz_min",
            f.col("body.measurement.limits.1.lower").cast(DoubleType()),
        )
        .withColumn(
            "messwert_toleranz_sec_min",
            f.col("body.measurement.limits.2.lower").cast(DoubleType()),
        )
        .withColumn(
            "messwert_toleranz_max",
            f.col("body.measurement.limits.1.upper").cast(DoubleType()),
        )
        .withColumn(
            "messwert_toleranz_sec_max",
            f.col("body.measurement.limits.2.upper").cast(DoubleType()),
        )
        .withColumn(
            "result",
            f.when(
                f.col("messwert").between(
                    f.col("messwert_toleranz_min"),
                    f.col("messwert_toleranz_max"),
                ),
                "OK",
            ).otherwise("NOK"),
        )
        .withColumn(
            "error_text",
            f.when(
                f.col("messwert") < f.col("messwert_toleranz_min"),
                f.lit("unterschritten"),
            ).when(
                f.col("messwert") > f.col("messwert_toleranz_max"),
                f.lit("überschritten"),
            ),
        )
        .withColumn(
            "error_code",
            f.when(
                f.col("messwert") < f.col("messwert_toleranz_min"),
                f.col("messwerttyp"),
            ).when(
                f.col("messwert") > f.col("messwert_toleranz_max"),
                f.col("messwerttyp"),
            ),
        )
        .withColumn("poorest_rating_meas_point", f.col("body.measurement.rating"))
        .withColumn("offset", f.col("body.measurement.details.offset"))
        .withColumn(
            "timestamp",
            f.col("body.header.measurement.meastime").cast(TimestampType()),
        )
        .withColumn(
            "cmonth", f.date_format(f.to_date(f.col("timestamp")), "yyyy-MM")
        )
        .select(COLUMNS + ["model", "typeseries", "fzg_typ", "uniqueid"])
    )

# COMMAND ----------

# COMMAND ----------


# Define environment stage from notebook widget
dbutils.widgets.dropdown("env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage")
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
schema = "proddshbrd_01_emea_dbf_ddx_data"
output_schema = "proddshbrd_01_emea_dbf_source_data"

# COMMAND ----------

# Read and transform IQVIS data from MSB locations
df_msb_067_iqvis = spark.read.table(f"`{catalog}`.`{schema}`.msb_067_generic").transform(iqvis_transformation)
df_msb_138_iqvis = spark.read.table(f"`{catalog}`.`{schema}`.msb_138_generic").transform(iqvis_transformation)
df_msb_175_iqvis = spark.read.table(f"`{catalog}`.`{schema}`.msb_175_generic").transform(iqvis_transformation)
df_msb_054_iqvis = spark.read.table(f"`{catalog}`.`{schema}`.msb_054_generic").transform(iqvis_transformation)
df_msb_050_iqvis = spark.read.table(f"`{catalog}`.`{schema}`.msb_050_generic").transform(iqvis_transformation)

# COMMAND ----------

# Union all MSB IQVIS data
df_msb_iqvis = (
    df_msb_067_iqvis
    .unionByName(df_msb_138_iqvis)
    .unionByName(df_msb_175_iqvis)
    .unionByName(df_msb_054_iqvis)
    .unionByName(df_msb_050_iqvis)
)

# COMMAND ----------

# Define environment stage from notebook widget
dbutils.widgets.dropdown("env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage")
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
schema = "proddshbrd_01_emea_dbf_source_data"

# Save the unified dataset
df_msb_iqvis.write.mode("overwrite").saveAsTable(f"`{catalog}`.`{output_schema}`.processed_iqvis")
