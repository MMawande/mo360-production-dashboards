# Databricks notebook source
# MAGIC %md
# MAGIC # Complete  Data Quality Framework (DQF) Validation
# MAGIC
# MAGIC This notebook runs comprehensive DQF quality checks on data using multiple validation profiles.


# COMMAND ----------
import os

from dqf.main import CheckProject
# the modules below are in the DPT Whl file.

from mo_utils.config_manager.config_manager import MO360DPConfigManager
from mo_utils.dbx_utils.dbx_utils import MO360DPDatabricksUtils
# COMMAND ----------

# Create widget with empty default
dbutils.widgets.text("dqf_config_path", "", "Config Path")

dbutils.widgets.text("dqf_version", "v1", "Version")

# Get and validate the config path
dqf_config_path = dbutils.widgets.get("dqf_config_path").strip()
dqf_version = dbutils.widgets.get("dqf_version").strip()

if not dqf_config_path:
    raise ValueError("Config path is required. Please provide a path in the dqf_config_path widget.")

# Validate file exists
if not os.path.exists(dqf_config_path):
    raise FileNotFoundError(f"Config file not found at: {dqf_config_path}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## DQF Configurations
# MAGIC
# MAGIC Multiple validation profiles for different quality checking scenarios

# COMMAND ----------
mo_config_mngr = MO360DPConfigManager(dqf_config_path, dqf_version)
logger = mo_config_mngr.setup_logging()
mo_dbutils = MO360DPDatabricksUtils(mo_config_mngr.get_constant("usecaseName"), logger)

# DQF configurations list
# Load configurations
configs = mo_config_mngr.get_data_quality()

current_stage = mo_dbutils.get_current_stage()

dqf_secret_scope_name = mo_config_mngr.get_constant("dqf_secret_scope_name")
dqf_api_key_name = mo_config_mngr.get_constant("dqf_api_key_name")

apikey_dev_secret = None
apikey_prd_secret = None


if current_stage in ('dev', 'int', 'uat'):
    print(f"current stage is '{current_stage}', using development secret.")
    apikey_dev_secret = dbutils.secrets.get(scope=dqf_secret_scope_name, key=dqf_api_key_name)
elif current_stage == 'prd':
    print(f"current stage is '{current_stage}', using productive secret.")
    apikey_prd_secret = dbutils.secrets.get(scope=dqf_secret_scope_name, key=dqf_api_key_name)
else:
    print("no valid stages set, api will not be used.")

print(f"Loaded {len(configs)} DQF configurations")


# COMMAND ----------

# MAGIC %md
# MAGIC ## DQF Execution Functions

# COMMAND ----------

# Use a specific configuration
def run_dqf_for_config(config_index=0):
    config_obj = configs[config_index]

    # Access all metadata
    catalog = config_obj["catalog"]
    schema = config_obj["schema"]
    table = config_obj["table"]

    # Build full table path
    full_table_path = f"{catalog}.{schema}.{table}"

    # Get the DQF configuration
    dqf_config = config_obj["configuration"]

    # Run DQF with full table name as dataframe
    checkProj = CheckProject(
        config=dqf_config,
        dataframe=full_table_path,
        result_path=f"{catalog}.{schema}",
        unity_catalog=True,
        incremental_flag=True,
        api_key_dev=apikey_dev_secret,
        api_key=apikey_prd_secret,
    )

    checkProj.run()
    return checkProj


# Run DQF for all configurations
def run_all_dqf_configs():
    results = []

    for i, config_obj in enumerate(configs):
        try:
            catalog = config_obj["catalog"]
            schema = config_obj["schema"]
            table = config_obj["table"]
            profile_name = config_obj["configuration"]["profile_name"]

            print(f"Running DQF {i + 1}/{len(configs)}: {profile_name} on {catalog}.{schema}.{table}")

            result = run_dqf_for_config(i)
            results.append({
                "config_index": i,
                "profile_name": profile_name,
                "table": f"{catalog}.{schema}.{table}",
                "status": "SUCCESS",
                "result": result
            })

            print(f"✅ Completed: {profile_name}")

        except Exception as e:
            print(f"❌ Failed: {profile_name} - {str(e)}")
            results.append({
                "config_index": i,
                "profile_name": profile_name,
                "table": f"{catalog}.{schema}.{table}",
                "status": "FAILED",
                "error": str(e)
            })

    return results


def safe_display_dataframe(df, name="DataFrame"):
    """Safely display a DataFrame regardless of type"""
    if df is None:
        print(f"No {name} found.")
        return

    try:
        # Check DataFrame type
        df_type = type(df).__name__
        print(f"{name} type: {df_type}")

        # Try to get row count
        try:
            if hasattr(df, 'count'):
                row_count = df.count()  # Spark DataFrame
            elif hasattr(df, '__len__'):
                row_count = len(df)  # Pandas DataFrame
            else:
                row_count = "unknown"

            print(f"{name} row count: {row_count}")

            if row_count == 0:
                print(f"{name} is empty.")
                return

        except Exception as count_error:
            print(f"Could not determine row count for {name}: {count_error}")

        # Try to display
        display(df)

    except Exception as e:
        print(f"Error displaying {name}: {e}")

        # Try alternative display methods
        try:
            if hasattr(df, 'show'):
                print(f"Showing {name} using .show():")
                df.show(5)
            elif hasattr(df, 'head'):
                print(f"Showing {name} using .head():")
                print(df.head())
        except Exception as e2:
            print(f"Alternative display methods also failed: {e2}")


print("DQF execution functions defined")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Execute All DQF Validations

# COMMAND ----------

# Run all DQF configurations
all_results = run_all_dqf_configs()

print(f"Executed {len(all_results)} DQF configurations")
# Process and display results
# Use the safe display function
for result in all_results:
    if result["status"] == "SUCCESS":
        dqf_result = result["result"]

        if hasattr(dqf_result, 'df_profile_results'):
            safe_display_dataframe(dqf_result.df_profile_results, "Profile results")

        if hasattr(dqf_result, 'df_check_results'):
            safe_display_dataframe(dqf_result.df_check_results, "Check results")
    else:
        print(f"❌ {result['profile_name']} on {result['table']} failed: {result['error']}")


# COMMAND ----------

# MAGIC %md
# MAGIC ## Notebook Completion
# MAGIC
# MAGIC Exit the notebook with success message.

# COMMAND ----------

dbutils.notebook.exit("Data Quality Framework Tests completed successfully.")
