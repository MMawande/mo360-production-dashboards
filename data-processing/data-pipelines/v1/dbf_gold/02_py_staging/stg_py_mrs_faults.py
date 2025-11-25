# Databricks notebook source

from pyspark.sql.functions import col, lit, when, date_format, from_utc_timestamp, expr

# Define environment stage
dbutils.widgets.dropdown("env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage")
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
schema = "proddshbrd_01_emea_dbf_ddx_data"

# Load tables
mrs_emea_faults_raw = spark.table(f"`{catalog}`.`{schema}`.mrs_emea_faults")
mrs_nafta_faults_raw = spark.table(f"`{catalog}`.`{schema}`.mrs_nafta_faults")

# %% [markdown]
# #Union emea and nafta

# %%
# select and union table
selected_columns = [
    col("c_checkpoint"),
    col("c_code_system"),
    col("c_code_system_type"),
    col("c_comment"),
    col("c_costcenter"),
    col("c_employee_id"),
    col("c_fault_location"),
    col("c_fault_type"),
    col("c_faultpriority"),
    col("c_fpos_picture_id"),
    col("c_fpos_tile_no_x"),
    col("c_fpos_tile_no_y"),
    col("c_group_id"),
    col("c_inherited_fault_flag"),
    col("c_input_p_shift"),
    col("c_input_shift_flag"),
    col("c_input_timestamp"),
    col("c_operator"),
    col("c_pferd_causer_entity_id"),
    col("c_pferd_installer_entity_id"),
    col("c_recording_costcenter"),
    col("c_recording_group"),
    col("c_shift_flag"),
    col("controlunit"),
    col("cu_di_ident"),
    col("cu_hw_ident"),
    col("cu_part_no"),
    col("cu_sw_ident"),
    col("deletion_datetime"),
    col("ingest_time"),
    col("is_cause_captured"),
    col("is_checkpoint"),
    col("is_employee_id"),
    col("is_error_code"),
    col("is_error_text"),
    col("is_rework_captured"),
    col("is_tester"),
    col("is_tester_group"),
    col("is_timestamp"),
    col("lupd_datetime"),
    col("plant"),
    col("pmi"),
    col("r_acquire_checkpoint"),
    col("r_checkpoint"),
    col("r_input_p_shift"),
    col("r_input_shift_flag"),
    col("r_input_timestamp"),
    col("r_operator"),
    col("r_recording_costcenter"),
    col("r_recording_group"),
    col("r_rework"),
    col("r_rework_action"),
    col("r_rework_comment"),
    col("r_rework_costcenter"),
    col("r_rework_duration"),
    col("r_rework_flag"),
    col("r_rework_group"),
    col("r_shift_flag"),
    col("rectified"),
    col("s_checkpoint"),
    col("s_code_system"),
    col("s_code_system_type"),
    col("s_comment"),
    col("s_costcenter"),
    col("s_employee_id"),
    col("s_fault_location"),
    col("s_fault_type"),
    col("s_faultpriority"),
    col("s_fpos_picture_id"),
    col("s_fpos_tile_no_x"),
    col("s_fpos_tile_no_y"),
    col("s_group_id"),
    col("s_inherited_fault_flag"),
    col("s_input_p_shift"),
    col("s_input_shift_flag"),
    col("s_input_timestamp"),
    col("s_operator"),
    col("s_pferd_causer_entity_id"),
    col("s_pferd_installer_entity_id"),
    col("s_recording_costcenter"),
    col("s_recording_group"),
    col("s_shift_flag"),
    col("status_costcenter_id"),
    col("status_group_id"),
    col("status_inherited_fault_flag"),
    col("status_rework_state"),
    col("workstep_id")
]

mrs_emea_faults = (
    mrs_emea_faults_raw
    .filter(col("deletion_datetime").isNull())
    .select(*selected_columns)
)
mrs_nafta_faults = (
    mrs_nafta_faults_raw
    .filter(col("deletion_datetime").isNull())
    .select(*selected_columns)
)

mrs_faults_union = mrs_emea_faults.unionByName(mrs_nafta_faults)

# %% [markdown]
# #Saved as a table in {dbf-staging}

# %%
# COMMAND ----------

# Define environment stage
dbutils.widgets.dropdown("env_stage", "dev", ["dev", "int", "uat", "prd"], "Select Environment Stage")
env_stage = dbutils.widgets.get("env_stage")

catalog = f"westeurope_mo360dp_usecases_{env_stage}"
output_schema = "proddshbrd_01_emea_dbf_staging"

# save as table in unity catalog
mrs_faults_union.write.saveAsTable(f"`{catalog}`.`{output_schema}`.stg_mrs_faults", mode="overwrite")
