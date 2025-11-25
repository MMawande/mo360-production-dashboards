# Databricks notebook source
# MAGIC %md
# MAGIC # Main orchestrator notebook to deploy billing dashboard.

# COMMAND ----------

# MAGIC %run ../imports

# COMMAND ----------


import dbdemos

dbutils.widgets.text("config_path", "/Workspace/data-pipelines/v1/999_config/etl-config.jsonc")

# COMMAND ----------

config_path = dbutils.widgets.get("config_path")

# COMMAND ----------

mo_config_mngr = MO360DPConfigManager(
    dbutils.widgets.get("config_path"), MO360DPDatabricksUtils.get_version()
)
logger = mo_config_mngr.setup_logging()
mo_dbutils = MO360DPDatabricksUtils(mo_config_mngr.get_constant("usecaseName"), logger)

# COMMAND ----------

catalog_name = mo_config_mngr.get_constant("usecaseCatalog")
schema_name = mo_config_mngr.get_constant("usecaseSchema")

# COMMAND ----------

workspaceUrl = spark.conf.get('spark.databricks.workspaceUrl')

# Proceed with the installation if the values are valid
dbdemos.install(
    'uc-04-system-tables',
    catalog=catalog_name,
    schema=schema_name,
    skip_genie_rooms=True,
    workspace_url=f'https://{workspaceUrl}/',
    path='./',
    overwrite=True,
    use_current_cluster=True
)
