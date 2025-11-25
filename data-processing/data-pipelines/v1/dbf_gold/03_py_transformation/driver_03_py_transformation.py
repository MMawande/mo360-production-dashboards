# Databricks notebook source
# MAGIC %md
# MAGIC ### Driver Notebook: 03_py_transformation
# MAGIC This notebook configures widgets and runs plant-specific transformation notebooks with consistent environment context.

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

# Define all transformation notebooks to run
notebooks = [
    # Additional MRS transformations
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/tra_py_mrs_actualdates",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/tra_py_mrs_orders",

    # Sindelfingen
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/0500 - Sindelfingen/tra_dbf_0500_additionalchecks",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/0500 - Sindelfingen/tra_dbf_0500_karnrresult",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/0500 - Sindelfingen/tra_dbf_0500_korrelation",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/0500 - Sindelfingen/tra_dbf_0500_mrs",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/0500 - Sindelfingen/tra_dbf_0500_main",

    # Rastatt
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/0540 - Rastatt/tra_dbf_0540_additionalchecks",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/0540 - Rastatt/tra_dbf_0540_karnrresult",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/0540 - Rastatt/tra_dbf_0540_korrelation",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/0540 - Rastatt/tra_dbf_0540_main",

    # Bremen
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/0670 - Bremen/tra_dbf_0670_additionalchecks",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/0670 - Bremen/tra_dbf_0670_karnrresult",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/0670 - Bremen/tra_dbf_0670_korrelation",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/0670 - Bremen/tra_dbf_0670_mrs",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/0670 - Bremen/tra_dbf_0670_main",

    # Tuscaloosa
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/1380 - Tuscaloosa/tra_dbf_1380_additionalchecks",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/1380 - Tuscaloosa/tra_dbf_1380_karnrresult",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/1380 - Tuscaloosa/tra_dbf_1380_korrelation",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/1380 - Tuscaloosa/tra_dbf_1380_mrs",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/1380 - Tuscaloosa/tra_dbf_1380_main",

    # East London
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/1750 - East London/tra_dbf_1750_additionalchecks",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/1750 - East London/tra_dbf_1750_karnrresult",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/1750 - East London/tra_dbf_1750_korrelation",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/1750 - East London/tra_dbf_1750_mrs",
    "/Workspace/data-pipelines/v1/dbf_gold/03_py_transformation/1750 - East London/tra_dbf_1750_main",
]

# COMMAND ----------

# Execute all transformation notebooks with inherited parameters
for notebook_path in notebooks:
    print(f"[INFO] Running: {notebook_path}")
    try:
        result = dbutils.notebook.run(
            notebook_path,
            timeout_seconds=0,
            arguments={
                "env_stage": env_stage,
                "config_path": config_path,
                "constant_path": constant_path
            }
        )
        print(f"✓ Success: {notebook_path} returned -> {result}")
    except Exception as e:
        print(f"✗ Failed to run {notebook_path}: {e}")
