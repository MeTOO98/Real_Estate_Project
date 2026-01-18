# Real Estate ETL Pipeline

A comprehensive ETL (Extract, Transform, Load) pipeline for scraping real estate data from Bayut.eg, processing it through multiple transformation stages, and loading it into a SQL Server data warehouse with dimensional modeling.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Pipeline Stages](#pipeline-stages)
- [Data Model](#data-model)
- [Visualization](#visualization)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project automates the extraction of real estate property data from Bayut.eg (focusing on New Cairo 5th Settlement and Sheikh Zayed areas), transforms it through multiple ETL stages using SSIS packages, and loads it into a dimensional data warehouse for analytics and visualization in Power BI.

The pipeline supports both **initial full load** and **incremental updates** to keep the data warehouse current.

## Architecture

![Uploading arc_image.png…]()

```
┌─────────────────┐
│  Bayut.eg       │
│  (Data Source)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  Apache Airflow (Orchestration)                         │
│  ┌──────────────────┐    ┌──────────────────┐           │ 
│  │ Initial Load DAG │    │ Incremental DAG  │           │
│  └──────────────────┘    └──────────────────┘           │
└───┬─────────────────────────────────────────────────┬───┘
    │                                                 │
    ▼                                                 ▼
┌─────────────────┐                          ┌─────────────────┐
│ Docker Container│                          │ Docker Container│
│ (Initial Scrape)│                          │ (Incr. Scrape)  │
└────────┬────────┘                          └────────┬────────┘
         │                                            │
         ▼                                            ▼
    ┌────────────┐                              ┌────────────┐
    │ CSV File   │                              │ CSV File   │
    └─────┬──────┘                              └─────┬──────┘
          │                                           │
          └───────────────┬───────────────────────────┘
                          │
                          ▼
                ┌──────────────────┐
                │  SQL Server      │
                │  (Raw Data)      │
                └────────┬─────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │  SSIS Transformation Packages      │
        │  ┌──────────────────────────────┐  │
        │  │ 1. Raw Data Load             │  │
        │  │ 2. First Step Transformation │  │
        │  │ 3. Second Step Transformation│  │
        │  │ 4. Final Transformation      │  │
        │  └──────────────────────────────┘  │
        └────────────────┬───────────────────┘
                         │
                         ▼
                ┌──────────────────┐
                │  SQL Server      │
                │  (Core Schema)   │
                │  - Dim_Date      │
                │  - Dim_Location  │
                │  - Fact_Table    │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │    Power BI      │
                │  (Visualization) │
                └──────────────────┘

```

## Features

- **Automated Web Scraping**: Selenium-based scraping from Bayut.eg
- **Dual Load Modes**: 
  - Initial full load for first-time setup
  - Incremental load for daily updates
- **Docker Containerization**: Isolated scraping environment
- **Orchestration**: Apache Airflow for workflow management
- **ETL Processing**: Multi-stage SSIS packages for data transformation
- **Dimensional Modeling**: Star schema with fact and dimension tables
- **Data Quality**: Handles null values, duplicates, and data type conversions
- **SSH Integration**: Remote SSIS package execution
- **Visualization Ready**: Power BI integration for dashboards

## Tech Stack

### Extraction
- **Python**
- **Selenium WebDriver**: Web scraping
- **Pandas**: Data manipulation
- **Docker**: Containerization

### Orchestration
- **Apache Airflow**: Workflow management
- **Docker Operator**: Container execution
- **SSH Operator**: Remote package execution

### Transformation & Loading
- **SQL Server Integration Services (SSIS)**: ETL processes
- **Microsoft SQL Server**: Data warehouse

### Visualization
- **Power BI**: Business intelligence and reporting

## 📁 Project Structure

```
real-estate-etl/
│
├── airflow/
│   ├── Inc_Real_EState_ETL.py         # Incremental load DAG
│   └── Real_EState_ETL.py             # Initial load DAG
│
├── scraping/
│   ├── Get_Data_From_Bayut.py         # Initial scraping script
│   ├── increm_scraping.py             # Incremental scraping script
│   └── Dockerfile                      # Docker configuration
│
├── sql/
│   ├── raw_datasql.sql                # Raw data schema
│   └── core_layer.sql                 # Dimensional model schema
│
├── ssis/
│   ├── initial_load/
│   │   ├── Load_raw_data.dtsx
│   │   ├── First_Step.dtsx
│   │   ├── Second_Step.dtsx
│   │   └── Truncate_tables.dtsx
│   │
│   └── incremental_load/
│       ├── Raw_Package.dtsx
│       ├── ETL.dtsx
│       ├── Package.dtsx
│       └── Package.dtsx (final)
│
├── data/
│   ├── bayut_raw.csv                  # Initial load output
│   ├── inc_bayut_raw.csv              # Incremental load output
│   └── date.json                      # Last scrape timestamp
│
└── README.md
``

## Pipeline Stages

### Stage 1: Data Extraction

**Initial Load:**
- Scrapes up to 150 pages from two locations
- Extracts: Price, Rooms, Bathrooms, Size, Type, Date, Status, Location
- Outputs to: `bayut_raw.csv`

**Incremental Load:**
- Reads last scrape date from `date.json`
- Scrapes only new listings
- Stops when reaching previously scraped data
- Outputs to: `inc_bayut_raw.csv`

### Stage 2: Raw Data Load (SSIS)

- Loads CSV data into SQL Server raw schema
- Table: `raw_data.data`
- Preserves all data types as VARCHAR for flexibility

### Stage 3: First Transformation

- Splits location column into multiple fields
- Creates dimension tables (Dim_Date, Dim_Location)
- Handles NULL values
- Generates surrogate keys

### Stage 4: Second Transformation

- Performs lookups between fact and dimension tables
- Data type conversions
- Business rule applications
- Creates middle staging table

### Stage 5: Final Transformation

- Identifies changed records (SCD Type 1)
- Updates existing records
- Inserts new records
- Populates Fact_Table
- Truncates temporary tables

## Data Model

### Fact Table: `Core.Fact_Table`

| Column | Type | Description |
|--------|------|-------------|
| property_id | INT | Primary Key |
| Price | VARCHAR(150) | Property price |
| NumOfRooms | INT | Number of bedrooms |
| NumofBathRooms | INT | Number of bathrooms |
| Size | INT | Property size (sqm) |
| Type | VARCHAR(150) | Property type |
| completion_status | VARCHAR(150) | Ready/Off-plan |
| Date_Id | VARCHAR(100) | Foreign Key to Dim_Date |
| Location_id | INT | Foreign Key to Dim_Location |

### Dimension Table: `Core.Dim_Date`

| Column | Type | Description |
|--------|------|-------------|
| date_id | VARCHAR(100) | Primary Key |
| date | VARCHAR(150) | Full date |
| day | INT | Day of month |
| Month | INT | Month number |
| Year | INT | Year |

### Dimension Table: `Core.Dim_Location`

| Column | Type | Description |
|--------|------|-------------|
| Location_id | INT | Primary Key (Identity) |
| Location | VARCHAR(250) | Full location string |
| Compound | VARCHAR(250) | Compound name |
| City | VARCHAR(250) | City name |
| Gov | VARCHAR(250) | Governorate |

<img width="1357" height="587" alt="model" src="https://github.com/user-attachments/assets/f610c478-b189-427e-a939-5b912b1f2be2" />

## 📈 Visualization

### Power BI Dashboard

The project includes a comprehensive Power BI dashboard for real estate market analysis.

**[View Live Dashboard](https://app.powerbi.com/view?r=eyJrIjoiNmNhZmI2ZTktYTdjNi00Mjc0LTlkNWUtZTUxZTNkOGNjODk1IiwidCI6ImM5NDdhYWExLTUxYzUtNDY3Yi04YWUwLTFhYTY0NzUxNmJjZiJ9&pageName=8ab163ecb04bcd72b5a0)**

### Dashboard Features

The interactive dashboard provides:

#### Key Metrics
- **Number of Properties**: Total property count
- **Average Price Per Meter**: Market rate analysis
- **Total Market Value**: Aggregate market valuation

#### Location Analysis
- Filter by **Compound** (1st District, 2nd District, etc.)
- Filter by **City** (5th Settlement, Sheikh Zayed)
- Filter by **Property Type** (Apartment, Villa, Duplex, etc.)

#### Market Insights
1. **Price Per Meter by Size Category and Type**
   - Line chart showing price trends across different property sizes
   - Segmented by property type (Apartment, Duplex, Penthouse, Townhouse)
   - Size categories: <100m², 100-149m², 200-299m², 150-199m², 300+m²

2. **Average Price Per Meter by Type**
   - Horizontal bar chart comparing property types
   - Hotel Apartment: 98K ج.م
   - Villa: 82K ج.م
   - Twin House: 75K ج.م
   - Townhouse: 75K ج.م

3. **Number of Properties by Compound and Type**
   - Stacked bar chart showing property distribution
   - Breakdown by location and property type
   - 5th Settlement: 1.8K Apartments, 0.4K other types
   - Sheikh Zayed: 1.5K properties across various types

4. **Ready % and Off-Plan %**
   - Pie chart showing completion status
   - Ready properties: 20%
   - Off-Plan properties: 80%
