# Databricks notebook source

# Set up variables, config, and create/refresh logic

import os
from pyspark.sql.utils import AnalysisException
from pyspark.sql import SparkSession
from dataclasses import dataclass
from typing import Dict

# Define catalog structure
# Define environment stage from notebook widget
dbutils.widgets.dropdown("env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage")
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
schema = "proddshbrd_01_emea_dbf_ddx_data"

# Set up Spark session
spark = SparkSession.builder.getOrCreate()

# Authentication configuration for ADLS
SPARK_CONFIG = {
    "fs.azure.account.auth.type": "OAuth",
    "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
    "fs.azure.account.oauth2.client.id": dbutils.secrets.get(scope="proddshbrd-databricks-etl", key="client-id"),
    "fs.azure.account.oauth2.client.secret": dbutils.secrets.get(scope="proddshbrd-databricks-etl", key="client-secret"),
    "fs.azure.account.oauth2.client.endpoint": "https://login.microsoftonline.com/9652d7c2-1ccf-4940-8151-4a92bd474ed0/oauth2/token"
}

# Apply Spark config
for k, v in SPARK_CONFIG.items():
    spark.conf.set(k, v)


# Define the Table class
@dataclass
class Table:
    name: str
    location: str

    def create(self):
        try:
            df = spark.read.format("delta").load(self.location)
            if spark.catalog.tableExists(self.name):
                print(f"  🔁 Table exists: Refreshing {self.name}")
            else:
                print(f"  🆕 Creating table: {self.name}")
            df.write.mode("overwrite").format("delta").saveAsTable(self.name)
            print(f"  ✅ Table written: {self.name}")
        except AnalysisException as e:
            print(f"  ⚠️ Failed to create or refresh table {self.name}: {e}")
        except Exception as e:
            import traceback
            print(f"  ⚠️ Failed to create or refresh table {self.name}: {e}")
            traceback.print_exc()


def create_tables(source_tables: Dict[str, str], target_catalog: str, target_schema: str):
    print("\n▶️ Creating tables for:", target_schema.split(".")[-1].upper())
    for table_name, source_path in source_tables.items():
        print(f"  🔧 Creating {table_name}...")
        full_table_name = f"{target_catalog}.{target_schema}.{table_name}"
        table = Table(name=full_table_name, location=source_path)
        table.create()


# %%
# COMMAND ----------
# MRS EMEA TABLES

mrs_emea_sources = {
    "mrs_emea_actual_dates": "abfss://mrs-data-clients-mo360-fs-prod@mrsdatadatalakeprod.dfs.core.windows.net/DataProducts/ActualDates/Delta",
    "mrs_emea_order_dates": "abfss://mrs-data-clients-mo360-fs-prod@mrsdatadatalakeprod.dfs.core.windows.net/DataProducts/OrderDates/Delta",
    "mrs_emea_actual_dates_md": "abfss://mrs-data-clients-mo360-fs-prod@mrsdatadatalakeprod.dfs.core.windows.net/DataProducts/ActualDatesMD/Delta",
    "mrs_emea_modules": "abfss://mrs-data-clients-mo360-fs-prod@mrsdatadatalakeprod.dfs.core.windows.net/DataProducts/Modules/Delta",
    "mrs_emea_order_prod_codes_md": "abfss://mrs-data-clients-mo360-fs-prod@mrsdatadatalakeprod.dfs.core.windows.net/DataProducts/OrderProdCodesMD/Delta",
    "mrs_emea_order_prod_codes": "abfss://mrs-data-clients-mo360-fs-prod@mrsdatadatalakeprod.dfs.core.windows.net/DataProducts/OrderProductionCodes/Delta",
    "mrs_emea_order_variants": "abfss://mrs-data-clients-mo360-fs-prod@mrsdatadatalakeprod.dfs.core.windows.net/DataProducts/OrderVariants/Delta",
    "mrs_emea_faults": "abfss://mrs-data-clients-mo360-fs-prod@mrsdatadatalakeprod.dfs.core.windows.net/DataProducts/Faults/Delta",
    "mrs_emea_orders": "abfss://mrs-data-clients-mo360-fs-prod@mrsdatadatalakeprod.dfs.core.windows.net/DataProducts/Orders/Delta",
    "mrs_emea_poi_pmi_mapping": "abfss://mrs-data-clients-mo360-fs-prod@mrsdatadatalakeprod.dfs.core.windows.net/DataProducts/PoiPmiMapping/Delta",
}

print("▶️ Creating tables for: MRS EMEA")
for name, source in mrs_emea_sources.items():
    print(f"  🔧 Creating {name}...")
    table = Table(f"{catalog}.{schema}.{name}", source)
    table.create()


# %%
# COMMAND ----------
# MRS NAFTA TABLES

mrs_nafta_sources = {
    "mrs_nafta_actual_dates": "abfss://mrs-data-clients-mo360-fs-prod-nafta@mrsdatadatalakeprodnafta.dfs.core.windows.net/DataProducts/ActualDates/Delta",
    "mrs_nafta_order_dates": "abfss://mrs-data-clients-mo360-fs-prod-nafta@mrsdatadatalakeprodnafta.dfs.core.windows.net/DataProducts/OrderDates/Delta",
    "mrs_nafta_actual_dates_md": "abfss://mrs-data-clients-mo360-fs-prod-nafta@mrsdatadatalakeprodnafta.dfs.core.windows.net/DataProducts/ActualDatesMD/Delta",
    "mrs_nafta_modules": "abfss://mrs-data-clients-mo360-fs-prod-nafta@mrsdatadatalakeprodnafta.dfs.core.windows.net/DataProducts/Modules/Delta",
    "mrs_nafta_order_prod_codes_md": "abfss://mrs-data-clients-mo360-fs-prod-nafta@mrsdatadatalakeprodnafta.dfs.core.windows.net/DataProducts/OrderProdCodesMD/Delta",
    "mrs_nafta_order_prod_codes": "abfss://mrs-data-clients-mo360-fs-prod-nafta@mrsdatadatalakeprodnafta.dfs.core.windows.net/DataProducts/OrderProductionCodes/Delta",
    "mrs_nafta_order_variants": "abfss://mrs-data-clients-mo360-fs-prod-nafta@mrsdatadatalakeprodnafta.dfs.core.windows.net/DataProducts/OrderVariants/Delta",
    "mrs_nafta_faults": "abfss://mrs-data-clients-mo360-fs-prod-nafta@mrsdatadatalakeprodnafta.dfs.core.windows.net/DataProducts/Faults/Delta",
    "mrs_nafta_orders": "abfss://mrs-data-clients-mo360-fs-prod-nafta@mrsdatadatalakeprodnafta.dfs.core.windows.net/DataProducts/Orders/Delta",
    "mrs_nafta_poi_pmi_mapping": "abfss://mrs-data-clients-mo360-fs-prod-nafta@mrsdatadatalakeprodnafta.dfs.core.windows.net/DataProducts/PoiPmiMapping/Delta",
}

print("▶️ Creating tables for: MRS NAFTA")
for name, source in mrs_nafta_sources.items():
    print(f"  🔧 Creating {name}...")
    table = Table(f"{catalog}.{schema}.{name}", source)
    table.create()


# %%
# COMMAND ----------
# MSB TABLES

msb_sources = {
    "msb_138_generic": "abfss://001@streamsilverprod.dfs.core.windows.net/138/msb.app/",
    "msb_175_generic": "abfss://001@streamsilverprod.dfs.core.windows.net/175/msb.app/",
    "msb_067_generic": "abfss://001@streamsilverprod.dfs.core.windows.net/067/msb.app/",
    "msb_054_generic": "abfss://001@streamsilverprod.dfs.core.windows.net/054/msb.app/",
    "msb_050_generic": "abfss://001@streamsilverprod.dfs.core.windows.net/050/msb.app/"
}

print("▶️ Creating tables for: MSB")
for name, source in msb_sources.items():
    print(f"  🔧 Creating {name}...")
    table = Table(f"{catalog}.{schema}.{name}", source)
    table.create()
