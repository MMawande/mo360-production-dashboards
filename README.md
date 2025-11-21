# MO360 Production Dashboards

Production Dashboards and analytics for E/E requirements. The dashboards enable analyses regarding electric and electronic errors in assembly processes. Errors per vehicle can be detected and analyzed more deeply by roles in assembly. Assembly Process Intelligence Dashboards visualize and predict certain plant values of the assembly, such as filling plant, wedding, window, and roof. The dashboards are used for planning and analyzing assembly problems for Sindelfingen F56.

## Scope of MO360 Production Dashboards

MO360 Production Dashboards rely on the latest cloud technology from the MO360 Data Platform. The dashboards can access data from various systems and Data Products such as MRS EMEA & NAFTA, IoT Data Products (IQvis, iPortal, MSB), and many more. Data from different products is processed, stored, and visualized in Microsoft Power BI. MO360 Production Dashboards provide a seamless user experience.

## Data Engineering

### Development and Release Process

#### Prerequisites

1. Access to the Databricks workspace and the Alice role of `MO360_PRODUCTION_DASHBOARDS_ETL_DEVELOPER`. First-time users should navigate to portal.azure.com and launch Databricks from there.
2. Add the MO360 Production Dashboards repo to the workspace environment and update your GitHub Enterprise authorization details in Databricks by creating a PAT token.

#### How to Contribute

1. We use Azure DevOps Sprint Boards, where you can find PBIs assigned to you.
2. For every PBI, create a new feature branch out of the main branch. Branches should not be created from other branches.
3. Branches must follow [specific naming conventions](https://daimler.visualstudio.com/MO360DP/_wiki/wikis/MO360DP.wiki/47913/pull-request-lifecycle). These will be checked after creating a pull request, which must also follow the naming convention.
4. Git quality gate checks will be applied to the Pull Request, including branch naming checks, PR title checks, code quality checks, and deployment readiness checks for the MO360 Production Dashboards code changes.
5. If everything works as expected, open your draft pull request in GitHub. Ensure the branch and PR names match the naming convention, or the quality gate will fail. Fill out the description using the provided pull request template.
6. The pull request will trigger pipelines that check naming conventions and code. If a pipeline fails, investigate and resolve the issue. If everything runs smoothly, move your PR to review. If other PRs are merged during your branch's lifecycle, merge the main branch into your branch to avoid conflicts.
7. To restart a failed pipeline, copy the commit ID, click on the pipeline details, and restart the pipeline from the desired commit.
8. To deploy ETL changes to dev manually, use the [databricks.deploy.custom.dev](https://dev.azure.com/daimler/MO360dpSfD/_build?definitionId=38324) pipeline. Select the branch and dev index (e.g., dev-02) for deployment, as well as the pipeline steps (e.g., only deployCustom).
9. After PR approval and successful deployment to dev, merge the feature branch into the main branch. Then, use the [mo360-production-dashboards-deploy](https://dev.azure.com/daimler/MO360dpSfD/_build?definitionId=38324) pipeline to deploy to all environments (dev, int, uat, prd).

### Deploy Workspace Databricks

For all environments, we use a single index to develop features:

- `index-00`: Used for pull request testing and deploying the main branch.

## Frontend Engineering

### Prerequisites

- Power BI Desktop installed.
- Access to Power BI Workspaces.
- Access to Databricks.

### Workflow

1. Find PBIs assigned to you in the Azure DevOps Sprint Board. Update the status of PBIs from "New" to "Committed" once started.
2. Create a new branch from the main branch of the repository for any changes to the Power BI file. Follow [specific naming conventions](https://daimler.visualstudio.com/MO360DP/_wiki/wikis/MO360DP.wiki/47913/pull-request-lifecycle).
3. The Power BI file `proddshbrd.pbix` is located in `proddshbrdreport\v1`.
4. After modifying the PBIX file, commit and push changes to your branch. As PBIX files are binary, only one developer can work on the file at a time. Coordinate with other Power BI developers as necessary.
5. After making changes, thoroughly test the Power BI report. Deploy the report to the PR-Workspace using the [Deploy to Power BI PR Workspace](#deploy-to-power-bi-pr-workspace) instructions.
6. For testing multiple features, use dedicated workspaces such as `mo360dp-productiondashboards-dev`, and connect to the Databricks dev environment.
7. After testing, merge the updated Power BI file into the main branch. Create a pull request following the [specific naming conventions](https://daimler.visualstudio.com/MO360DP/_wiki/wikis/MO360DP.wiki/47913/pull-request-lifecycle). Link the completed PBIs and include the report link in the pull request.
8. Once the PBI is completed, update the status to "done" and log the effort.

### Deploy to Power BI PR Workspace

1. Modify the config files (`proddshbrd-report-config.json` and `workspace-config.json`) located in `mo360-production-dashboards\configs\dev\powerbi`. Change the `workspaceName` from dev to pr.
2. Commit and push the changes.
3. Run the [powerbi.deploy.dev](https://dev.azure.com/daimler/MO360dpSfD/_build?definitionId=38324) pipeline in Azure DevOps.
4. Test the report in the PR-Workspace.
5. After testing, revert the `workspaceName` in the config files to dev, commit, and push the changes.

Main contact is
Mawanda Mbaza 175 & Nora Ocros 050
