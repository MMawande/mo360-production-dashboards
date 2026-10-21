# MO360 Production Dashboards

Production dashboards and analytics for **E/E requirements** in automotive assembly processes.

The solution supports analysis of electrical and electronic errors during vehicle assembly. It enables errors per vehicle to be identified and investigated by assembly roles, while Assembly Process Intelligence dashboards provide visibility into plant and assembly processes such as filling plant, wedding, window, and roof operations.

The dashboards support planning and analysis of assembly problems for **Sindelfingen F56**.

## Scope

MO360 Production Dashboards are built on the **MO360 Data Platform** and integrate data from multiple systems and Data Products.

Key sources include:

- MRS EMEA & NAFTA
- IQvis
- iPortal
- MSB
- Additional MO360 Data Products

Data from these sources is processed and stored through the platform's data-engineering layer and presented to users through **Microsoft Power BI**.

## High-Level Architecture

```text
MRS / IQvis / iPortal / MSB / Other Data Products
                        |
                        v
               MO360 Data Platform
                        |
                        v
                  Azure Databricks
                Data Processing / ETL
                        |
                        v
                  Processed Data
                        |
                        v
                 Microsoft Power BI
                        |
                        v
             Production Dashboards
```

## Repository Structure

The repository is organised around infrastructure, data processing, deployment pipelines, and project documentation.

```text
mo360-production-dashboards/
|
|-- .github/
|-- _infrastructure/
|-- cicd-pipelines/
|-- data-processing/
|-- documents/
|-- pipelines/
|
|-- .cz.toml
|-- .editorconfig
|-- .flake8
|-- .gitattributes
|-- .gitignore
|-- .markdownlintrc
|-- .pre-commit-config.yaml
|-- .yamllint
|-- LICENSE.md
|-- README.md
`-- requirements-code-quality.txt
```

## Technology Stack

The solution uses technologies across data engineering, analytics, DevOps, and reporting:

- MO360 Data Platform
- Azure Databricks
- Microsoft Power BI
- Azure DevOps
- Git and GitHub Enterprise
- CI/CD pipelines
- Python code-quality tooling
- YAML configuration and pipeline definitions

## Data Engineering

### Prerequisites

Data engineers require:

- Access to the Databricks workspace
- `MO360_PRODUCTION_DASHBOARDS_ETL_DEVELOPER` Alice role
- Access to this Git repository
- GitHub Enterprise authentication in Databricks
- A Personal Access Token (PAT) where required for repository integration

For initial setup, access Databricks through the Azure portal, add the repository to the workspace, and configure GitHub Enterprise authentication.

## Development and Release Process

Development work is managed through **Azure DevOps Sprint Boards** and PBIs.

### Development Workflow

1. Select the assigned PBI from the Azure DevOps Sprint Board.
2. Create a feature branch from `main`.
3. Follow the required branch naming convention.
4. Implement and test the required change.
5. Commit and push the feature branch.
6. Open a draft Pull Request in GitHub.
7. Complete the Pull Request description using the repository template.
8. Allow the automated quality gates and pipelines to run.
9. Resolve any pipeline or quality-gate failures.
10. Move the Pull Request to review after successful validation.
11. Obtain approval and complete development testing.
12. Merge the feature branch into `main`.
13. Deploy the approved version through the required environments.

> Feature branches should be created directly from `main`, not from other feature branches.

## Pull Request Quality Gates

Pull Requests are automatically validated through checks such as:

- Branch naming validation
- Pull Request title validation
- Code-quality checks
- Deployment-readiness checks

If another Pull Request is merged while development is in progress, bring the latest `main` changes into the feature branch and resolve conflicts before completing the Pull Request.

## Databricks Deployment

ETL changes can be deployed to development using the configured Databricks deployment pipeline.

Developers select:

- The feature branch
- The required development index
- The required deployment step

The release path is:

```text
DEV -> INT -> UAT -> PRD
```

For workspace deployment, `index-00` is used for Pull Request testing and deployment of the `main` branch.

## Frontend Engineering

The frontend reporting layer is implemented using **Microsoft Power BI**.

### Prerequisites

Power BI developers require:

- Power BI Desktop
- Access to the required Power BI workspaces
- Databricks access
- Git repository access

### Power BI Development Workflow

1. Select the assigned PBI in Azure DevOps.
2. Change the PBI status from `New` to `Committed` when development begins.
3. Create a feature branch from `main`.
4. Modify the Power BI report.
5. Commit and push the changes to the feature branch.
6. Thoroughly test the report.
7. Deploy the report to the PR workspace for validation.
8. Create or update the Pull Request.
9. Link the completed PBI and include the report link where required.
10. Merge approved changes into `main`.
11. Update the PBI status to `Done` and record the development effort.

### Power BI Report

The Power BI report file is:

```text
proddshbrdreport/v1/proddshbrd.pbix
```

PBIX files are binary files and cannot be merged like normal source-code files. Developers should therefore coordinate changes so that only one developer modifies the PBIX file at a time.

## Deploy to Power BI PR Workspace

For PR-workspace testing:

1. Locate the Power BI configuration files under the development configuration.
2. Update `workspaceName` from `dev` to `pr`.
3. Commit and push the configuration change.
4. Run the configured Power BI deployment pipeline in Azure DevOps.
5. Test the report in the PR workspace.
6. Change `workspaceName` back from `pr` to `dev`.
7. Commit and push the reverted configuration.

The relevant configuration files include:

```text
proddshbrd-report-config.json
workspace-config.json
```

For testing several features together, dedicated development workspaces can be used and connected to the corresponding Databricks development environment.

## CI/CD Flow

```text
Feature Branch
      |
      v
Draft Pull Request
      |
      v
Quality Gates
      |
      v
PR / Development Testing
      |
      v
Code Review and Approval
      |
      v
Main Branch
      |
      v
DEV -> INT -> UAT -> PRD
```

This process ensures that code and dashboard changes are validated before they reach production.

## Contribution Guidelines

When contributing to the repository:

- Always start from the latest `main` branch.
- Follow the prescribed branch and Pull Request naming conventions.
- Associate work with the corresponding Azure DevOps PBI.
- Test changes before requesting review.
- Do not merge while required quality gates are failing.
- Keep the feature branch aligned with `main` when concurrent changes are merged.
- Coordinate PBIX modifications with other Power BI developers.
- Complete the Pull Request description and provide the required testing information.

## Maintainers

**Main Developer & Data Engineer**  
Mawanda Mbaza (175)

**Product Owner, Business**  
Nora Ocros (050), Sindelfingen

## Purpose

MO360 Production Dashboards provide manufacturing stakeholders with a consolidated analytics capability for monitoring and investigating electrical/electronic errors and important assembly processes.

By combining data from MO360 Data Products, Databricks-based data processing, controlled CI/CD deployment, and Power BI visualisation, the solution supports operational analysis, manufacturing problem investigation, planning, and data-driven decision making.
