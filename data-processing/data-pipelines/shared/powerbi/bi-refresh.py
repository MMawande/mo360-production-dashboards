# Databricks notebook source
# MAGIC %md
# MAGIC # Power BI Dataset Refresh
# MAGIC
# MAGIC This notebook refreshes Power BI datasets using:
# MAGIC - **DefaultAzureCredential** for authentication
# MAGIC - **pbipy** for Power BI operations
# MAGIC - **Configurable parameters** for flexible refresh options
# MAGIC - **Multiple reports support**

# COMMAND ----------

# MAGIC %pip install azure-identity pbipy msal
# MAGIC %restart_python

# COMMAND ----------

from azure.identity import DefaultAzureCredential, ClientSecretCredential
from pbipy import PowerBI
from datetime import datetime
import os

# Create widgets
dbutils.widgets.text("fabric_workspace", "", "Fabric Workspace")
dbutils.widgets.text("sp_secret_scope_name", "", "Service Principal Secret Scope Name")
dbutils.widgets.text("sp_secret_scope_client_secret_key", "", "Secret Scope Client Secret Key")
dbutils.widgets.text("sp_tenant_id", "9652d7c2-1ccf-4940-8151-4a92bd474ed0", "Service Principal Tenant")
dbutils.widgets.text("sp_client_id", "", "Service Principal Client ID")
dbutils.widgets.text("fabric_reports", "", "Fabric Reports")
dbutils.widgets.dropdown("wait_for_refresh", "False", ["True", "False"], "Wait for Report Dataset Refresh")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Install Required Libraries

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration Parameters

# COMMAND ----------

# Workspace and Reports Configuration
fabric_workspace_name = dbutils.widgets.get("fabric_workspace")  # Replace with your workspace name

fabric_reports_str = dbutils.widgets.get("fabric_reports")  # Returns: "MBUI_RLS, Another_Report"
reports_names = [name.strip() for name in fabric_reports_str.split(",") if name.strip()]

# Refresh Behavior Parameters
wait_for_refresh_str = dbutils.widgets.get("wait_for_refresh")
wait_for_refresh = wait_for_refresh_str.lower() == 'true'  # Whether to wait for refresh completion

# Authentication scope
scope = 'https://analysis.windows.net/powerbi/api/.default'
sp_secret_scope_name = dbutils.widgets.get("sp_secret_scope_name")
sp_secret_scope_client_secret_key = dbutils.widgets.get("sp_secret_scope_client_secret_key")
sp_tenant_id = dbutils.widgets.get("sp_tenant_id")
sp_client_id = dbutils.widgets.get("sp_client_id")

print("📋 Configuration Parameters:")
print(f"   Fabric Workspace: {fabric_workspace_name}")
print(f"   Reports: {reports_names}")
print(f"   Wait for Refresh: {wait_for_refresh}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Import Libraries and Setup

# COMMAND ----------

print("Libraries imported successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Authenticate and Create Power BI Client

# COMMAND ----------

# Set up authentication parameters
client_secret = dbutils.secrets.get(
    scope=sp_secret_scope_name,
    key=sp_secret_scope_client_secret_key,
)

# Set the tenant ID, client ID, and client secret
os.environ["AZURE_TENANT_ID"] = sp_tenant_id
os.environ["AZURE_CLIENT_ID"] = sp_client_id
os.environ["AZURE_CLIENT_SECRET"] = client_secret

# Use DefaultAzureCredential for automatic authentication
credential = ClientSecretCredential(
    tenant_id=sp_tenant_id,
    client_id=sp_client_id,
    client_secret=client_secret,
)

# Get token for Power BI
token = credential.get_token(scope)

# Create Power BI client
pbi = PowerBI(bearer_token=token.token)

print(" Power BI client created successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Find Workspace by Name

# COMMAND ----------

# Get all workspaces
workspaces = pbi.groups(filter=f"name eq '{fabric_workspace_name}'", top=1)

# Find the target workspace
target_workspace = None
if len(workspaces) > 0:
    target_workspace = workspaces[0]
    print(f"  Found workspace: {target_workspace.name}")
    print(f"   Workspace ID: {target_workspace.id}")
else:
    print(f"  Workspace '{fabric_workspace_name}' not found")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Find Reports and Get Datasets

# COMMAND ----------

target_reports = []
target_datasets = []

if target_workspace:
    print(f"  Looking for reports in workspace: {target_workspace.name}")
    print("-" * 50)

    reports = pbi.reports(group=target_workspace.id)
    for report in reports:
        if report.name in reports_names:
            target_reports.append(report)
            print(f"✅ Found report: {report.name}")
            print(f"   Report ID: {report.id}")
            # Get the associated dataset
            dataset_id = report.dataset_id
            target_dataset = pbi.dataset(dataset_id, group=target_workspace.id)
            target_datasets.append(target_dataset)

            print(f"   Associated dataset: {target_dataset.name}")
            print(f"   Dataset ID: {target_dataset.id}")


print(f"  Found {len(target_datasets)} datasets to process")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Display Dataset Information

# COMMAND ----------

if target_datasets:
    print("  Dataset Information Summary:")
    print("-" * 70)

    for i, dataset in enumerate(target_datasets, 1):
        print(f"{i}. Dataset: {dataset.name}")
        print(f"   ID: {dataset.id}")
        print()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Get Current Refresh History

# COMMAND ----------

if target_datasets:
    print("  Recent Refresh History:")
    print("=" * 70)

    for dataset in target_datasets:
        print(f"\n  Dataset: {dataset.name}")
        print("-" * 50)

        try:
            # Get last refresh record
            history = dataset.refresh_history(top=1)

            for i, refresh in enumerate(history, 1):
                status = refresh.get('status', 'Unknown')
                start_time = refresh.get('startTime', 'Unknown')
                refresh_type = refresh.get('refreshType', 'Unknown')

                # Format datetime if available
                if start_time != 'Unknown':
                    try:
                        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        start_time = start_dt.strftime('%Y-%m-%d %H:%M:%S UTC')
                    except:
                        pass

                print(f"{i}. Status: {status} | Type: {refresh_type} | Started: {start_time}")

        except Exception as e:
            print(f"   Could not retrieve refresh history: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Trigger Dataset Refresh

# COMMAND ----------

if target_datasets:
    print(f"  Processing {len(target_datasets)} datasets...")
    print(f"  Timestamp: {datetime.now()}")
    print("=" * 70)

    for i, dataset in enumerate(target_datasets, 1):
        print(f"\n{i}. Processing dataset: {dataset.name}")
        print("-" * 50)

        dataset.take_over()

        try:
            if wait_for_refresh:
                print("  Triggering refresh and waiting for completion...")
                dataset.refresh_and_wait(
                    retry_count=3,
                    check_interval=10
                )

                # Get latest refresh status
                refresh_history = dataset.refresh_history(top=1)
                for refresh in refresh_history:
                    status = refresh.get('status', 'Unknown')
                    start_time = refresh.get('startTime', 'Unknown')
                    refresh_type = refresh.get('refreshType', 'Unknown')

                    if start_time != 'Unknown':
                        try:
                            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                            start_time = start_dt.strftime('%Y-%m-%d %H:%M:%S UTC')
                        except:
                            pass

                    print(f"   Final Status: {status} | Type: {refresh_type} | Started: {start_time}")

                print(f"  SUCCESS! Dataset refresh completed for: {dataset.name}")

            else:
                print("🚀 Triggering refresh (not waiting for completion)...")
                refresh_request_id = dataset.refresh(
                    retry_count=3
                )

                print(f"  SUCCESS! Dataset refresh triggered for: {dataset.name}")
                print(f"   Refresh Request ID: {refresh_request_id}")

        except Exception as e:
            print(f"  Failed to process dataset '{dataset.name}': {str(e)}")

    print(f"\n  Processing completed for all datasets!")
    print(f"   Workspace: {target_workspace.name}")
    print(f"   Total Datasets: {len(target_datasets)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Widget Management (Optional)

# COMMAND ----------

# Uncomment to remove all widgets (useful for testing)
dbutils.widgets.removeAll()
