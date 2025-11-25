# Databricks notebook source
# MAGIC %md
# MAGIC ### Driver Notebook: 04_py_marts
# MAGIC This notebook sets up environment widgets and executes a list of mart notebooks with inherited parameters.

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

# List of mart notebook paths
notebooks = [
    "/Workspace/data-pipelines/v1/dbf_gold/04_py_marts/mrt_dbf_0500",
    "/Workspace/data-pipelines/v1/dbf_gold/04_py_marts/mrt_dbf_0540",
    "/Workspace/data-pipelines/v1/dbf_gold/04_py_marts/mrt_dbf_0670",
    "/Workspace/data-pipelines/v1/dbf_gold/04_py_marts/mrt_dbf_1380",
    "/Workspace/data-pipelines/v1/dbf_gold/04_py_marts/mrt_dbf_1750",
    "/Workspace/data-pipelines/v1/dbf_gold/04_py_marts/mrt_dbf_all",
]

# COMMAND ----------

# Sequentially run each notebook
for notebook_path in notebooks:
    print(f"[INFO] Running: {notebook_path}")
    try:
        result = dbutils.notebook.run(
            notebook_path,
            timeout_seconds=0,
            arguments={
                "config_path": config_path,
                "constant_path": constant_path,
                "env_stage": env_stage
            }
        )
        print(f"✓ Success: {notebook_path} returned -> {result}")
    except Exception as e:
        print(f"✗ Failed to run {notebook_path}: {e}")
