# Databricks notebook source
# MAGIC %md
# MAGIC ### Driver Notebook: 02_py_staging
# MAGIC This notebook sets up environment widgets and executes a list of child notebooks with inherited parameters.

# COMMAND ----------

# Set up widgets
dbutils.widgets.text("config_path", "")
dbutils.widgets.text("constant_path", "")
dbutils.widgets.text("env_stage", "")

# Retrieve widget values
config_path = dbutils.widgets.get("config_path")
constant_path = dbutils.widgets.get("constant_path")
env_stage = dbutils.widgets.get("env_stage")

print(f"[INFO] config_path: {config_path}")
print(f"[INFO] constant_path: {constant_path}")
print(f"[INFO] env_stage: {env_stage}")

# COMMAND ----------

# List of child notebooks to run
notebooks = [
    "/Workspace/data-pipelines/v1/dbf_gold/02_py_staging/stg_py_mrs_poi_pmi_mapping",
    "/Workspace/data-pipelines/v1/dbf_gold/02_py_staging/stg_py_mrs_actual_dates_md",
    "/Workspace/data-pipelines/v1/dbf_gold/02_py_staging/stg_py_mrs_actual_dates",
    "/Workspace/data-pipelines/v1/dbf_gold/02_py_staging/stg_py_mrs_faults",
    "/Workspace/data-pipelines/v1/dbf_gold/02_py_staging/stg_py_mrs_order_dates",
    "/Workspace/data-pipelines/v1/dbf_gold/02_py_staging/stg_py_mrs_order_prod_codes",
    "/Workspace/data-pipelines/v1/dbf_gold/02_py_staging/stg_py_mrs_order_prod_codes_md",
    "/Workspace/data-pipelines/v1/dbf_gold/02_py_staging/stg_py_mrs_order_variants",
    "/Workspace/data-pipelines/v1/dbf_gold/02_py_staging/stg_py_mrs_orders",
    "/Workspace/data-pipelines/v1/dbf_gold/02_py_staging/stg_py_mrs_modules"
]

# COMMAND ----------

# Run each child notebook with parameter inheritance
for path in notebooks:
    print(f"[INFO] Running: {path}")
    try:
        result = dbutils.notebook.run(
            path,
            timeout_seconds=0,
            arguments={
                "env_stage": env_stage,
                "config_path": config_path,
                "constant_path": constant_path
            }
        )
        print(f"✓ Success: {path} returned -> {result}")
    except Exception as e:
        print(f"✗ Failed to run {path}: {e}")
