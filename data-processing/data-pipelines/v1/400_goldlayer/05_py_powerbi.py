# Databricks notebook source

# MAGIC %run ../imports

# COMMAND ----------

dbutils.widgets.dropdown(
    "display_results", "False", ["True", "False"], "Display Results"
)
dbutils.widgets.dropdown("write_output", "True", ["True", "False"], "Write Output")
dbutils.widgets.text("config_path", "/Workspace/data-pipelines/v1/999_config/etl-config.jsonc", "Configuration Path")
dbutils.widgets.text("constant_path", "/Workspace/data-pipelines/v1/999_config/etl-dev.jsonc", "Configuration Path With Constants Per Environment")

# COMMAND ----------

mo_config_mngr = MO360DPConfigManager(
    dbutils.widgets.get("config_path"), MO360DPDatabricksUtils.get_version()
)
mo_config_mngr = MO360DPConfigManager(
    dbutils.widgets.get("constant_path"), MO360DPDatabricksUtils.get_version()
)

# MAGIC ## Refresh Power BI Report
# COMMAND ----------

mo_powerbi_client = MO360PowerBIUtils(
    mo_config_mngr.get_constant("usecaseName"),
    mo_config_mngr.get_constant("fabric_workspace_name"),
    mo_config_mngr.get_constant("fabric_report_name"),
    mo_config_mngr.get_constant("sql_endpoint_name"),
)

mo_powerbi_client.update_powerbi_dataset()
