#!/usr/bin/env python
# coding: utf-8

# # CoCo: Analysis of Co-Occurrence of Data Elements in the DIZ
# 
# **Pelin Genc**  
# **October 22, 2024**

# # 📖 **Table of Contents**
# 
# ---
# 
# ## 1. **Introduction**
#    - **Problem Statement**
#    - **Proposed Solution**
# 
# ---
# 
# ## 2. **CoCo: Inputs**
#    - ### 2.1 **FHIR Data and SQL Query**
#      - 2.1.1 Understanding FHIR Data Hierarchy
#      - 2.1.2 Executing SQL Queries in Python
#    - ### 2.2 **Catalogues**
#    - ### 2.3 **Dummy Dataset**
# 
# ---
# 
# ## 3. **CoCo: User Interface**
#    - ### 3.1 **User Interface Components**
#      - 3.1.1 Upload Component
#      - 3.1.2 Dropdown Menu
#      - 3.1.3 Sliders
#        - **All Codes**: Hierarchy Level Slider and Max Number of Visualized Code Pairs
#        - **Individual Codes**: Max Number of Visualized High-Frequency Top Neighbors
#      - 3.1.4 Graphs
#        - **All Codes**
#        - **Individual Codes**
# 
# ---
# 
# ## 4. **CoCo: Methodology**
#    - ### 4.1 **Overview of the Datasets**
#      - 4.1.1 `flat_df`
#      - 4.1.2 `co_occurrence_matrix_df`
#      - 4.1.3 `new_pairs_df`
#    - ### 4.2 **Mathematics Behind the Graphs**
#      - 4.2.1 **PyVis**: Co-Occurrence Matrix
#      - 4.2.2 **Dendrogram**: Distance Matrix
#      - 4.2.3 **Bar Chart**: Relative Frequency Distribution
# 
# ---
# 
# ## 5. **Limitations and Future Improvements**
# 
# ---
# 
# ## 6. **CoCo: Web App Availability (with Dummy Data)**
# 
# ---
# 
# ## 7. **CoCo: The Code and its Explanations**
#    - ### 7.1 **Library**
#    - ### 7.2 **Main Code**
#      - 7.2.1 Colors of Resource Types
#      - 7.2.2 Assigning Resource Types Based on Encoding Properties
#      - 7.2.3 Dash Application Setup Components
#      - 7.2.4 `create_co_occurrence_matrix` Function
#      - 7.2.5 `normalize_weights` Function
#      - 7.2.6 `generate_network_viz` Function
#      - 7.2.7 `create_dendrogram_plot` Function
#      - 7.2.8 `update_slider_visibility` Callback Function
#      - 7.2.9 `fetch_and_process_data` Function
#        - Read Uploaded Data
#        - Check Required Columns and Load Catalogue Data
#        - Get the Labels
#        - Generate Co-occurrence Matrix
#        - Create Code Pairs
#        - Build Hierarchies
#        - Add Parent Nodes
#        - Combine DataFrames
#        - Fill Displays and Full Displays Columns
#        - Segment DataFrames
#        - Generate Co-occurrence Matrices for Resource Types
#      - ### 7.2.10 `upload_file` Callback Function
#      - ### 7.2.11 Dash Callback: `update_graph`
#        - #### **All Codes: Visualization of PyVis Graphs**
#          - Edge Thickness Range
#          - Style Initialization
#          - Code Selection Validation
#          - Data Preparation
#          - Node Size and Shape Mapping
#          - Node Degree Calculation
#          - Top Nodes Selection
#          - Data Filtering by Levels
#          - Weight Calculation
#          - Graph Update Logic
#          - Highlight User Selection
#          - Graph Visualization
#        - #### **Individual Codes: Visualization of PyVis Graphs**
#          - Node Size and Style Initialization
#          - Node Degree Calculation
#          - Top Nodes Selection
#          - Defining Weight Range for Node Size and Edge Thickness Rescaling
#          - Neighbor Retrieval
#          - Nodes and Edges Addition
#          - ResourceType Dependent Co-Occurrence Matrix Processing
#          - Temporary File Generation
#      - ### 7.2.12 Dash Callback: `update_charts`
#        - Initial Validation
#        - Data Retrieval
#        - Frequency Distribution Calculation
#        - Selected Code Labeling
#        - Codes of Interest Handling
#        - Bar Chart Data Preparation
#        - Bar Chart Sorting and Dropping Duplicates
#        - Bar Chart Creation
#        - Dendrogram Creation
# 

# 
# <!-- This line will not be displayed. -->
# 
# ## 1 Introduction
# ### Problem Statement
# The healthcare industry produces vast amounts of complex data, especially in the form of clinical codes such as ICD (International Classification of Diseases), LOINC (Logical Observation Identifiers Names and Codes), and OPS (German Procedure Classification). Analyzing the co-occurrences of these codes can reveal valuable insights into clinical patterns, as well as relationships between diagnoses, tests, and procedures. This application is designed to provide a flexible, interactive platform for visualizing these co-occurrences between Fast Healthcare Interoperability Resources (FHIR) codes using Dash, enabling users to explore the data effectively.
# 
# As datasets grow in size and complexity, interpreting relationships between healthcare codes becomes increasingly challenging. Without specialized visualization tools, healthcare professionals may find it difficult to extract meaningful patterns or insights from the data. The key challenge is to develop a user-friendly interface that allows users to upload datasets and visualize both inter- and intra-relationships across different resource types—such as ICD, LOINC, and OPS. Additionally, such tools should support the exploration of healthcare code co-occurrences to enhance the understanding of patient conditions.
# 
# In clinical decision-making, doctors often need to examine the broader context of a patient’s diagnosis by analyzing associated medical events and conditions. For example, a doctor treating a patient with diabetes may want to investigate which other medical conditions or events frequently co-occur with diabetes. Such an exploration could provide insights into potential comorbidities, complications, or treatment patterns commonly seen in diabetic patients. This type of analysis can inform the doctor’s treatment approach, drawing attention to other conditions that may require consideration or intervention.
# 
# ### Proposed Solution
# ### CoCo: Visual Translation of Healthcare Language
# 
# <img src="images/CoCo.png" alt="Directed Cycle of Resource Types in FHIR" width="800"/>

# 
# ########################################################################################################################## ##########################################################################################################################
# 

# ## 2 CoCo: Inputs
# ### 2.1 FHIR Data and SQL Query
# 
# ### 2.1.1 Understanding FHIR Data Hierarchy
# The FHIR standard defines a set of resource types.
# 
# **Administrative/Financial Resources:**
# - Claim
# - ExplanationOfBenefit
# - ServiceRequest
# - Coverage
# 
# **Clinical Resources:**
# - Condition
# - Procedure
# - DiagnosticReport
# - Observation
# - Immunization
# - CareTeam
# - CarePlan
# - MedicationRequest
# - Encounter
# 
# **Document/Reference Resources:**
# - DocumentReference
# - ImagingStudy
# - Provenance
# 
# These resource types follow an inter-referencing logic, where a particular resource type may reference codes from other resource types to highlight the dependency and flow of events between them. This relationship can be represented as a directed cycle, as shown in the figure below. The key resource types involved in below cyclic graph are Patient, E: Encounter, C: Condition, D: DiagnosticReport, O: Observation, P: Procedure.
# The key resource types involved in the below cyclic graph are **Patient**, **E: Encounter**, **C: Condition**, **D: DiagnosticReport**, **O: Observation**, **P: Procedure**.
# 
# 
# <!-- ![Directed Cycle of Resource Types in FHIR](images/Cycle-Patient-Encounter-Observation-Condition---.png) -->
# 
# <img src="images/Cycle-Patient-Encounter-Observation-Condition---.png" alt="Directed Cycle of Resource Types in FHIR" width="600"/>
# 
# 
# 
# **Figure 1:** Directed Cycle of Resource Types in FHIR
# 
# As shown in Figure 1, this interconnectedness creates a directional cycle among these resource types, where each type can reference others in a coherent manner. For example, the **Patient** resource serves as a fundamental building block in the healthcare domain. Each Patient can be involved in multiple **Encounters**, such as hospital visits, outpatient appointments, or emergency room admissions. During an Encounter, healthcare providers may gather various types of clinical data, which can include **Observations** (e.g., vital signs, lab results), **Conditions** (diagnoses), and **Procedures** (medical interventions). For instance, an Encounter references the Patient while also linking to various Observations and Conditions that arise during that Encounter. This cyclical nature enables comprehensive data modeling that reflects the complexity of patient care in real-world settings.
# 
# In the implementation of CoCo code, it is important to note that only the codes from the **Observation (LOINC)**, **Procedure (OPS)**, and **Condition (ICD)** resource types are utilized.
# 
# ### 2.1.2 Executing SQL Queries in Python
# The code retrieves FHIR data in a three-column dataset format: 'PatientID', 'Code', and 'ResourceType'. It first filters for data between timestamps '2023-02-25 00:00:00' and '2023-02-25 02:00:00' to identify relevant 'PatientID' values associated with specific codes within this period. Then, it retrieves the complete code history of these patients.
# 
# <img src="images/CoCo-timestamp.png" alt="Directed Cycle of Resource Types in FHIR" width="800"/>
# 
# Below is the pseudocode for executing SQL queries (for ICD as an example) using the trino connector in Python. The queries retrieve not only ICD, OPS, and LOINC data from a FHIR dataset that occurred during a specified time interval but also the full history of those codes for the same patients. Complete sql query code is available under https://github.com/pelingenc/CoCo.git.
# 
# ```sql
# icd_query = """
# 
# WITH TimeIntervalICD AS (
#     SELECT
#         encounter.subject.reference AS PatientID,
#         condition_coding.code AS Codes,
#         FROM_ISO8601_TIMESTAMP(condition.onsetdatetime) AS EncounterDate
#     FROM
#         fhir.qs.Encounter encounter
#         LEFT JOIN UNNEST(encounter.diagnosis) AS encounter_diagnosis ON TRUE
#         LEFT JOIN fhir.qs.Condition condition ON encounter_diagnosis.condition.reference = CONCAT('Condition/', condition.id)
#         LEFT JOIN UNNEST(condition.code.coding) AS condition_coding ON TRUE
#     WHERE
#         condition_coding.code IS NOT NULL
#         AND condition_coding.system = 'http://fhir.de/CodeSystem/bfarm/icd-10-gm'
#         AND FROM_ISO8601_TIMESTAMP(condition.onsetdatetime) BETWEEN TIMESTAMP '2023-02-25 00:00:00' AND TIMESTAMP '2023-02-25 02:00:00'
# ),
# 
# AllPatientICDCodes AS (
#     SELECT
#         encounter.subject.reference AS PatientID,
#         condition_coding.code AS Codes,
#         FROM_ISO8601_TIMESTAMP(condition.onsetdatetime) AS EncounterDate
#     FROM
#         fhir.qs.Encounter encounter
#         LEFT JOIN UNNEST(encounter.diagnosis) AS encounter_diagnosis ON TRUE
#         LEFT JOIN fhir.qs.Condition condition ON encounter_diagnosis.condition.reference = CONCAT('Condition/', condition.id)
#         LEFT JOIN UNNEST(condition.code.coding) AS condition_coding ON TRUE
#     WHERE
#         condition_coding.code IS NOT NULL
#         AND condition_coding.system = 'http://fhir.de/CodeSystem/bfarm/icd-10-gm'
# ),
# 
# AllPatientOPSCodes AS (
#     SELECT
#         encounter.subject.reference AS PatientID,
#         procedure_coding.code AS OPSCodes,
#         FROM_ISO8601_TIMESTAMP(procedure.performeddatetime) AS ProcedureDate
#     FROM
#         fhir.qs.Encounter encounter
#         LEFT JOIN fhir.qs.procedure procedure ON encounter.subject.reference = procedure.subject.reference
#         LEFT JOIN UNNEST(procedure.code.coding) AS procedure_coding ON TRUE
#     WHERE
#         procedure_coding.code IS NOT NULL
#         AND procedure_coding.system = 'http://fhir.de/CodeSystem/bfarm/ops'
# ),
# 
# AllPatientLOINCCodes AS (
#     SELECT
#         encounter.subject.reference AS PatientID,
#         observation_coding.code AS LOINCCodes,
#         FROM_ISO8601_TIMESTAMP(observation.effectivedatetime) AS ObservationDate
#     FROM
#         fhir.qs.Encounter encounter
#         LEFT JOIN fhir.qs.observation observation ON encounter.subject.reference = observation.subject.reference
#         LEFT JOIN UNNEST(observation.code.coding) AS observation_coding ON TRUE
#     WHERE
#         observation_coding.code IS NOT NULL
#         AND observation_coding.system = 'http://loinc.org'
# )
# 
# SELECT
#     p.PatientID,
#     ARRAY_AGG(DISTINCT icd.Codes) AS ICDCodesAllTime,
#     ARRAY_AGG(DISTINCT ops.OPSCodes) AS OPSCodesAllTime,
#     ARRAY_AGG(DISTINCT loinc.LOINCCodes) AS LOINCCodesAllTime
# FROM
#     TimeIntervalICD p
# JOIN
#     AllPatientICDCodes icd ON p.PatientID = icd.PatientID
# LEFT JOIN
#     AllPatientOPSCodes ops ON p.PatientID = ops.PatientID
# LEFT JOIN
#     AllPatientLOINCCodes loinc ON p.PatientID = loinc.PatientID
# GROUP BY
#     p.PatientID
# 
# """
# ````
# 
# 
# ### 2.2 Catalogues
# 
# The three catalog files below contain a tree-structured hierarchy of FHIR codes with their labels. In CoCo, these files are used to assign labels and retrieve parent names for child codes. They are available under https://github.com/pelingenc/CoCo.git
# 
# - `ICD_Katalog_2023_DWH_export_202406071440.csv`
# - `OPS_Katalog_2023_DWH_export_202409200944.csv`
# - `LOINC_DWH_export_202409230739.csv`
# 
# ### 2.3 Dummy Dataset
# 
# Since getting the real FHIR data is not trivial, a dummy dataset is available under https://github.com/pelingenc/CoCo.git to play with the software.

# ##########################################################################################################################
# ##########################################################################################################################

# ## 3 CoCo: User Interface
# 
# ### 3.1 User Interface Components
# 
# #### 3.1.1 Upload Component
# In this section, users can upload the FHIR data previously downloaded via a SQL query. The dataset contains three columns: Patient (with anonymized numbering), Codes, and Resource Types, and is formatted as a Parquet file.
# 
# 
# ![Data Upload Process in the Dash Application.](images/Upload_Data.png)
# 
# 
# #### 3.1.2 Dropdown Menu
# This dropdown menu contains all available codes from the FHIR dataset, along with an option labeled **ALL CODES** that allows users to visualize the broader relationships among all codes.
# 
# ![Dropdown Menu for Code Selection](images/Select_a_code.png)
# 
# 
# #### 3.1.3 Sliders
# The application includes two different sliders designed to enhance user interaction and data visualization.
# 
# ##### 3.1.3.a All Codes: Hierarchy Level Slider and the max Number of visualized Code Pairs:
# This slider is displayed when the user selects **selected code = 'ALL codes'**. It allows users to choose from four different levels of hierarchy to visualize the PyVis graph in a hierarchical manner. Each level corresponds to a different depth in the code structure, enabling users both to explore various degrees of relationships among the codes and to avoid the complexity. The hierarchy of the complete codes can be seen in the catalogues.
# 
# User Input for Maximum Codes on Tree Leaves (Enter Value for n): This input box allows users to set the maximum number of codes displayed on the tree leaves, sorted by node degree (the total count of connections) in descending order. The top 'n' nodes are selected for each ResourceType, helping users focus on the most interconnected codes.
# 
# 
# ![Hierarchy Level Slider](images/Hierarchy_Slider.png)
# 
# 
# ##### 3.1.3.b Individual Codes: Max Number of Visualized High Frequency Top Neighbors:
# This slider is utilized when the user selects an individual code. It ranges from 1 to 10, allowing users to specify the number of top neighbors (most co-occurring nodes) to be displayed for the selected code.
# 
# 
# ![Maximum Number of Nodes to Visualize](images/Top_Neighbors_Slider.png)
# 
# #### 3.1.4 Graphs
# The application presents different types of graphs depending on whether an **individual code** or **All codes** are selected.
# 
# ##### 3.1.4.a All Codes:
# 
# When **All codes** is selected, a PyVis graph is displayed to illustrate the big picture of all FHIR codes.
# 
# In the **All Codes** version of the visualization, a slider is provided with four levels to simplify the analysis and reduce complexity. 
# The relationships between parent and child nodes, as well as the inter- and intra-relationships within resource types, are fundamental to understanding the hierarchical structure of codes. The catalogs serve as a valuable resource, detailing which codes function as parents and which serve as children within this structure. The weight assigned to each child code is aggregated and transmitted to its parent, which subsequently sums the weights of all its child nodes. This aggregation process allows higher-level codes to represent the cumulative occurrences of their constituent codes, thereby illustrating the interconnectedness of the coding system.
# 
# Labels can be enabled from **Show Labels** checkbox. To prevent overlapping labels, the text is truncated, similar to the individual code view. However, users can hover over any node to reveal the full display of the code, ensuring that essential information is still accessible.
# 
# 
# <img src="images/All_codes-Hierarchy_Levels.png" alt="All Codes Visualization with Hierarchy Level and Code Highlighting" width="1000"/>
# 
# Additionally, the **Enter Code** feature allows users to highlight a specific code among the entire dataset by coloring its node and the edges connected to it in a vibrant color. 
# 
# 
# <img src="images/All_codes_highlight.png" alt="All Codes Visualization with Hierarchy Level and Code Highlighting" width="700"/>
# 
# PyVis includes a customizable **Physics** that enables users to configure the physical rules governing the visualization environment. Certain settings may cause the nodes to exhibit erratic movements, necessitating the optimization of parameters such as the spring constant, damping factor, and gravitational constant. A key insight is that the Barnes-Hut algorithm is particularly efficient for large datasets, as it effectively groups points to enhance performance. Each of the three algorithms comes with its own default physics settings, but these can be customized manually. This flexibility is essential, especially when dealing with substantial datasets, as it helps mitigate the excessive movement of nodes during visualization.
# 
# <img src="images/Physics.png" alt="All Codes Visualization with Hierarchy Level and Code Highlighting" width="400"/>
# 
# <img src="images/Solver-Types.png" alt="All Codes Visualization with Hierarchy Level and Code Highlighting" width="1000"/>
#     
# ##### 3.1.4.b Individual Codes:
# For individual codes, three types of graphs are provided:
# 
#   - **PyVis Graph:** This graph visualizes the co-occurrences of the top neighbors of an individual code, categorized into three resource types: ICD, OPS, and LOINC. Each resource type is represented by a distinct color, facilitating quick identification of the types of relationships present.
#   
#   - **Dendrogram:** The dendrogram illustrates groups of codes that are likely to occur together, highlighting the likelihood of co-occurrence independent of resource type. Unlike the PyVis graph, which focuses on pairs, the dendrogram can reveal relationships among larger groups of codes, providing a comprehensive view of interconnections.
#   
#   - **Bar Chart:** This chart displays the frequency distribution of the selected code and its top neighbors, offering insights into the prevalence of these codes within the dataset.
#   
#   The maximum number of nodes to be visualized can be adjusted using the top neighbors slider. This functionality is essential for limiting the amount of data presented in the network visualization. The graph generated by this configuration visualizes Individual Codes. It displays the Top Neighbors using PyVis, highlighting clusters in a dendrogram and presenting frequencies in a bar chart. To ensure clarity and prevent overlapping of text labels, the labels are truncated. However, users can hover over a node to view the full label, which provides additional context for the data represented.
# 
# 
# <img src="images/Individual_codes-Top_neighbors_3Graphs_Show_Label-Full_label.png" alt="Graphs for Individual Codes" width="800"/>
# 

# ##########################################################################################################################
# ##########################################################################################################################

# ## 4 CoCo: Methodology
# The Dash application is structured around several key components, each with specific input and output arguments. Below is a breakdown of the code:
# 
# ### 4.1 Overview of the Datasets
# 
# The function **fetch_and_process_data** processes the uploaded data and generates a structured output. It adds two key columns, **Displays** and **Full_Displays**, to the **flat_df**. The **Displays** column provides a truncated version of the information in the **Full_Displays** column, which contains complete and detailed descriptions. 
# The `fetch_and_process_data` function outputs three primary data structures:
# 
# #### 4.1.1 flat_df
# This DataFrame contains three essential columns: `PatientID`, `Codes`, and `ResourceType`. The `PatientID` column includes anonymized integer identifiers starting from 1. The `Codes` column comprises various healthcare-related codes (e.g., ICD, LOINC, or OPS), while the `ResourceType` column categorizes each code's specific type (e.g., ICD for diagnoses, LOINC for lab tests, OPS for procedures).
# 
# | PatientID | Codes    | ResourceType |
# |-----------|----------|--------------|
# | 1         | M87.24   | ICD          |
# | 1         | I41.1    | ICD          |
# | 1         | 9-694.t  | OPS          |
# | 1         | 8-826.0h | OPS          |
# | 1         | 6-008.gs | OPS          |
# | 1         | 5-812.n0 | OPS          |
# | 1         | 2951-2   | LOINC        |
# | 1         | 26450-7  | LOINC        |
# | 1         | 5894-1   | LOINC        |
# | 1         | 1988-5   | LOINC        |
# | 2         | U35.1    | ICD          |
# | 2         | T53.4    | ICD          |
# 
# The function **get_display_label** is employed to retrieve the appropriate display labels based on the provided code, level, and resource type. The labels added to the uploaded **flat_df** are sourced from FHIR catalogs that encompass various coding systems, including ICD, OPS, and LOINC. The following code snippets illustrate how these datasets are loaded:
# 
# ```python
# icd_df = pd.read_csv('ICD_Katalog_2023_DWH_export_202406071440.csv') 
# ops_df = pd.read_csv('OPS_Katalog_2023_DWH_export_202409200944.csv')
# loinc_df = pd.read_csv('LOINC_DWH_export_202409230739.csv')  
# ```
# 
# | PatientID | Codes    | ResourceType | Displays                 | Full_Displays                                                    |
# |-----------|----------|--------------|--------------------------|-----------------------------------------------------------------|
# | 1         | M87.24   | ICD          | Knochennekrose           | Knochennekrose durch vorangegangenes Trauma: ...                |
# | 1         | I41.1    | ICD          | Myokarditis              | Myokarditis bei anderenorts klassifizierten Viruserkrankungen ...|
# | 1         | 9-694.t  | OPS          | Spezifische Behandlung    | Spezifische Behandlung im besonderen Setting bei ...            |
# | 1         | 8-826.0h | OPS          | Doppelfiltrationsplasmapherese | Doppelfiltrationsplasmapherese (DFPP): Ohne K ...             |
# | 1         | 6-008.gs | OPS          | Applikation von Medikamenten | Applikation von Medikamenten, Liste 8: Isavuconazol ...        |
# | 1         | 5-812.n0 | OPS          | Arthroskopie             | Arthroskopische Operation am Gelenkknorpel ...                 |
# | 1         | 2951-2   | LOINC        | Sodium [Moles/volume]    | Sodium [Moles/volume] in Serum or Plasma                        |
# | 1         | 26450-7  | LOINC        | Eosinophils              | Eosinophils/100 leukocytes in Blood                             |
# | 1         | 5894-1   | LOINC        | Prothrombin time         | Prothrombin time (PT) actual/normal in Platelets ...            |
# | 1         | 1988-5   | LOINC        | C reactive protein       | C reactive protein [Mass/volume] in Serum or Plasma            |
# | 2         | U35.1    | ICD          | Nicht belegte Schlüsselnummer | Nicht belegte Schlüsselnummer U35.1                           |
# | 2         | T53.4    | ICD          | Toxische Wirkung         | Toxische Wirkung: Dichlormethan                                 |
# 
# 
# 
# #### 4.1.2 co_occurrence_matrix_df
# This DataFrame illustrates co-occurrences of codes among patients, indicating the number of patients sharing pairs of codes.
# 
# |         | M87.24 | I41.1 | U35.1 | T53.4 | 9-694.t | 8-826.0h | 6-008.gs | 5-812.n0 | 2951-2 | 26450-7 | 5894-1 | 1988-5 |
# |---------|--------|-------|-------|-------|---------|----------|----------|----------|--------|---------|--------|--------|
# | **M87.24** | 1      | 0     | 0     | 0     | 0       | 0        | 0        | 0        | 0      | 0       | 0      | 0      |
# | **I41.1**  | 0      | 1     | 0     | 0     | 0       | 0        | 0        | 0        | 0      | 0       | 0      | 0      |
# | **U35.1**  | 0      | 0     | 1     | 0     | 0       | 0        | 0        | 0        | 0      | 0       | 0      | 0      |
# | **T53.4**  | 0      | 0     | 0     | 1     | 0       | 0        | 0        | 0        | 0      | 0       | 0      | 0      |
# | **9-694.t**| 0      | 0     | 0     | 0     | 1       | 1        | 1        | 1        | 0      | 0       | 0      | 0      |
# | **8-826.0h**| 0      | 0     | 0     | 0     | 1       | 1        | 1        | 1        | 0      | 0       | 0      | 0      |
# | **6-008.gs**| 0      | 0     | 0     | 0     | 1       | 1        | 1        | 1        | 0      | 0       | 0      | 0      |
# | **5-812.n0**| 0      | 0     | 0     | 0     | 1       | 1        | 1        | 1        | 0      | 0       | 0      | 0      |
# | **2951-2** | 0      | 0     | 0     | 0     | 0       | 0        | 0        | 0        | 1      | 1       | 1      | 1      |
# | **26450-7**| 0      | 0     | 0     | 0     | 0       | 0        | 0        | 0        | 1      | 1       | 1      | 1      |
# | **5894-1** | 0      | 0     | 0     | 0     | 0       | 0        | 0        | 0        | 1      | 1       | 1      | 1      |
# | **1988-5** | 0      | 0     | 0     | 0     | 0       | 0        | 0        | 0        | 1      | 1       | 1      | 1      |
# 
# #### 4.1.3 new_pairs_df
# The new_pairs_df dataset is generated by integrating information from both the co-occurrence matrix and relevant catalogs. This dataset presents a structured view of code pairs, along with their corresponding weights and hierarchy levels. The weights represent the strength of the relationship between the code pairs, while the levels indicate their position within a defined hierarchy. 
# 
# 
# |    | Code1      | Code2      | Weight | level | ResourceType | Displays  |
# |----|------------|------------|--------|-------|--------------|-----------|
# | 0  | 1988-5     | 26450-7    | 3      | 4     | NaN          | NaN       |
# | 1  | 1988-5     | 2951-2     | 3      | 4     | NaN          | NaN       |
# | 2  | 1988-5     | 5-812.n0   | 3      | 4     | NaN          | NaN       |
# | 3  | 1988-5     | 5894-1     | 3      | 4     | NaN          | NaN       |
# | 4  | 1988-5     | 6-008.gs   | 1      | 4     | NaN          | NaN       |
# | .. | ...        | ...        | ...    | ...   | ...          | ...       |
# | 97 | Bld        | NFr        | 1      | 2     | LOINC        | Bld       |
# | 98 | NFr        | 26450-7    | 1      | 3     | LOINC        | NFr       |
# | 99 | LOINC      | PPP        | 1      | 1     | LOINC        | LOINC     |
# | 100| PPP        | RelTime    | 1      | 2     | LOINC        | PPP       |
# | 101| RelTime    | 5894-1     | 1      | 3     | LOINC        | RelTime   |
# 
#     
# ### 4.2 Mathematic Behind the Graphs
# #### 4.2.1 Pyvis: Co-Occurrence Matrix
# The application generates a co-occurrence matrix based on the data processed earlier. This matrix quantifies relationships by counting how many patients share same multiple codes. The following code demonstrates how to create a co-occurrence matrix.
# 
# The process begins with a PatientID Codes table, which is transformed into a one-hot encoded matrix. This encoding facilitates the representation of the presence or absence of specific codes for each patient in a binary format, where each column corresponds to a unique code and each row corresponds to a patient.
# 
# To derive the co-occurrence matrix, we multiply this one-hot encoded matrix by its transpose. This operation results in a square matrix where each entry represents the number of times two codes co-occur across all patients. 
# 
# Additionally, the concept of **node size** in this context is defined by the **degree**, which refers to the count of non-zero values in the co-occurrence matrix for each code. This degree reflects the connectivity of each code to others, providing a measure of its importance or prominence within the dataset. A higher degree indicates that a code is associated with many other codes, suggesting its potential significance in the analysis of patient data.
# 
# Also the **edge thickness** is determined from the co-occurance matrix. The edges, or connections, between nodes (codes) in a network visualization are directly influenced by the **values in the co-occurrence matrix**. Specifically, the thickness of each edge reflects the frequency with which the corresponding code pairs co-occur across patient records.
# 
# <img src="images/Co-occurance-matrix.png" alt="Co-Occurrence Matrix" width="800"/>
# 
# 
# #### 4.2.2 Dendogram: Distance Matrix
# A dendrogram is a tree-like diagram that visualizes the arrangement of clusters resulting from hierarchical clustering. The hierarchy presented in a dendrogram emerges from the sorting and grouping of distance values among the codes. This tree-like structure reflects how entities are clustered based on their similarities, with closer proximity indicating a stronger relationship. As the distance values are computed, codes with lower distances—indicating higher co-occurrence and similarity—are grouped together, forming clusters. 
# 
# The Euclidean distance formula is commonly used to calculate distances in a dendrogram. This formula measures the straight-line distance between points in Euclidean space, and it is defined as:
# 
# <img src="images/Dendogram_distance_matrix.png" alt="Co-Occurrence Matrix" width="800"/>
# 
# 
# **Clustering:**
#    - Use a clustering algorithm, such as **Agglomerative Clustering**:
#         - Initialization: Treat each data point (or code) as a single cluster.
#         - Distance Calculation: Calculate the distance between all clusters using a specified distance metric (e.g., Euclidean distance).
#         - Merging Clusters: Identify the two closest clusters and merge them into one.
#         - Repeat: Update the distance matrix to reflect the new cluster structure and repeat the merging process until all points are clustered or the desired number of clusters is achieved.
# 
# **Ward's method - Linkage Criteria:**
#    - Define a linkage criterion (e.g., **Ward's method**) to decide how to merge clusters:
#      - This minimizes the total within-cluster variance. The distance between clusters can be computed using:
# 
# 
# 
# #### 4.2.3 Bar Chart: Relative Frequency Distribution
# To calculate the relative frequency distribution for codes in a dataset, start by counting how many times each unique code appears. This gives you the frequency of each code. Next, determine the total number of code occurrences by summing these frequencies.
# 
# Then, for each code, divide its frequency by the total count to find the relative frequency, which shows the proportion of that code relative to the entire dataset.
# 
# <img src="images/Bar_Chart_freq_dist.png" alt="Co-Occurrence Matrix" width="800"/>
# 

# ##########################################################################################################################
# ##########################################################################################################################

# 
# ## 5 Limitations and Future Improvements
# 
# ### Limitations
# Despite its strengths, the CoCo application has **limitations**:
# 
# 1. **Performance Issues**: With larger dataset sizes, the user experience may be impacted. Significant time is required for data uploads and visualization rendering.
# 2. **Data Imbalance**: A noted imbalance in the prevalence of LOINC codes compared to ICD and OPS codes could skew insights derived from the visualizations. High counts combined with low degrees shows that these code are commonly referenced but potentially lacks relational depth within the dataset. In other words, there are strong intra-resource type relationships among the codes within the same resource type, but relatively weaker inter-resource type relationships with codes from other resource types.
# 
#      
#    <!-- ![Node Degree Distribution](images/Node_degree_distribution.png) -->
#    
#    <img src="images/Node_degree_distribution.png" alt="Node Degree Distribution" width="700" />
# 
#    *Figure: Node Degree Distribution*
# 
# 3. **Missing Codes**: Some codes present in real FHIR datasets may not exist in catalogs, affecting the visualization and label display.
# 
# ### Future improvements
# 
# 1. **Utilization of Small Representative Datasets**: To mitigate performance issues associated with large datasets, leveraging smaller, representative datasets can be beneficial. This approach enables efficient processing while preserving the essential characteristics of the data.
# 
#         Application of Deep Learning Techniques
# 
#         Dimensionality Reduction
# 
#    
# 
# 2. **Batch Processing**: Implementing batch processing strategies allows for the handling of data in smaller, more manageable segments. This method can significantly improve processing times and resource utilization when working with extensive datasets.
# 
# 3. **Prefiltering Options in the GUI**: Incorporating prefiltering options within the graphical user interface (GUI) can enhance user experience by allowing users to focus on relevant parent codes. This selective approach ensures that only pertinent data is considered for analysis, thus streamlining the computational process.
# 
# 

# ##########################################################################################################################
# ##########################################################################################################################

# ## 6 CoCo is available as a Web App with a dummy data!
# 
# 1. **Open the Web Application:**  
#    [https://lmi-co-occurances.onrender.com](https://lmi-co-occurances.onrender.com)
# 
# 2. **Prepare the Directory and put the Catalogues under that directory:**  
#    Place the catalogue files in (as an example) `C:\CoCo_Input` directory and  enter the directory in the space shown below. 
#    ![Data Upload Process in the Dash Application.](images/Upload_Data.png)
#    
#    The catalogue files can be found at: [https://github.com/pelingenc/CoCo.git]
# 
# 3. **Upload the Data:**  
#    Upload `FHIR_dummy_data_.parquet`. It is also available under [https://github.com/pelingenc/CoCo.git].
#    
#    
#    
# ## !! IMPORTANT WORKAROUND
# 
# The current version of the code functions correctly in a local Python environment. However, if you intend to use the web-deployed application, please follow the steps below to load the files.
# 
# 1. Enter directory where the catalogue files are.
# 2. Uplaod the parquet file. 
# 3. Refresh the page.
# 4. Reload the parquet file again.
# 
# Now the data is loaded.
# 

# ##########################################################################################################################
# ##########################################################################################################################

# ## 7 CoCo: The code and its Explanation

# ### 7.1  LIBRARY

# In[1]:


import os
import io
import base64
import tempfile
import re
import numpy as np
import pandas as pd
import networkx as nx
from collections import Counter
from itertools import combinations

import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State

from pyvis.network import Network
import plotly.figure_factory as ff
import plotly.graph_objs as go

import scipy.cluster.hierarchy as sch
from sklearn.cluster import AgglomerativeClustering



# ### 7.2 MAIN CODE

# #### 7.2.1 Colors of Resource Types
# The `SUBGROUP_COLORS` dictionary assigns specific colors to different resource types: **ICD** is represented in **light blue**, **LOINC** in **pink**, and **OPS** in **purple**.
# 

# In[2]:


SUBGROUP_COLORS = {
    'ICD': "#00bfff", #"#00bfff",
    'LOINC': "#ffc0cb", #"#ffc0cb",
    'OPS': "#9a31a8" ##9a31a8"
}


def get_color_for_resource_type(resource_type):
    """Map resource types to colors using SUBGROUP_COLORS."""
    return SUBGROUP_COLORS.get(resource_type, 'gray')  # Default to gray if not found


# #### 7.2.2 Assigning Resource Types depending on their encoding properties
# This code segment provides functions to validate and classify medical codes for ICD, LOINC, and OPS, ensuring that only properly formatted codes are processed within the application.
# 

# In[3]:


def is_icd_code(code):
    """Check if the given code is a valid ICD code."""
    return bool(re.match(r"^[A-Z]", code))

def is_loinc_code(code):
    """Check if the given code is a valid LOINC code with a hyphen at [-2]."""
    return len(code) > 1 and code[-2] == '-'

def is_ops_code(code):
    """Check if the given code is a valid OPS code."""
    return len(code) > 1 and code[1] == '-'

# Function to classify ResourceType based on the code
def get_resource_type(code):
    if re.match(r"^[A-Z]", code):
        return "ICD"
    elif len(code) > 1 and code[-2] == '-':
        return "LOINC"
    elif len(code) > 1 and code[1] == '-':
        return "OPS"
    else:
        return "Unknown"


# #### 7.2.3 Dash Application Setup Components
# 
# - **App Initialization**: `app = dash.Dash(__name__)` initiates the app.
# - **Server Assignment**: `server = app.server` assigns the server attribute.
# - **Main Layout**: `app.layout` defines the structure and layout of the app.
# - **Title Header**: Displays the app title, "CoCo: Co-Occurrences in FHIR Codes".
# - **Upload Button**: `id='upload-data'` - Allows users to upload data files.
# - **Directory Input**: `id='directory-input'` - Text input for the catalog file directory.
# - **Upload Feedback**: `id='upload-feedback'` - Displays feedback after file upload.
# - **Top Neighbor Slider**: `id='num-nodes-slider'` - Slider to set the number of top neighbors.
# - **Hierarchy Level Slider**: `id='level-slider'` - Slider to select the code hierarchy level.
# - **Max Codes Input**: `id='n-input'` - Numerical input for setting maximum displayed codes.
# - **Code Dropdown**: `id='code-dropdown'` - Dropdown menu to select individual codes.
# - **Label Toggle Checklist**: `id='show-labels'` - Checklist to toggle code labels on or off.
# - **Loading Animation**: `id='loading'` - Shows a loading indicator during processing.
# - **Graph Display Area**: `id='graph-iframe'` - Embeds the PyVis network graph visualization.
# - **Search Code Input**: `id='code-input'` - Text input for searching specific codes.
# - **Dendrogram Graph**: `id='dendrogram'` - Displays the hierarchical dendrogram graph.
# - **Bar Chart Graph**: `id='bar-chart'` - Shows relative frequency distribution as a bar chart.
# - **Data Store**: `id='data-store'` - Hidden storage for keeping data throughout callbacks.
# - **Codes of Interest Store**: `id='codes-of-interest-store'` - Stores selected codes for analysis.
# - **Slider Container**: `id='slider-container'` - Container for the top neighbor slider, shown conditionally.
# - **Hierarchy Slider Container**: `id='level-slider-container'` - Container for the hierarchy slider, also shown conditionally.
# - **Data Container**: `id='data-container'` - Hidden div to store data for callbacks.
# 
# Each component is associated with a unique `id` used to reference and update it through callbacks in the Dash application.
# 
# 

# In[4]:


# Dash application setup
app = dash.Dash(__name__)
server = app.server


app.layout = html.Div([
    html.H1("CoCo: Co-Occurrences in FHIR Codes"),

    # Create a row for upload button and directory input
    html.Div(
        [
            dcc.Upload(
                id='upload-data',
                children=html.Button('Upload Data'),
                multiple=False,
                style={'margin-right': '10px'}  # Add some space between button and input
            ),
            # Input box for the user to specify the directory
            html.Label('Enter the directory for the catalog files:', style={'margin-right': '10px'}),
            dcc.Input(
                id='directory-input',
                type='text',
                value='',  # Default value
                style={'width': '300px'},
                debounce=False  
            ),
        ],
        style={'display': 'flex', 'alignItems': 'center', 'margin-bottom': '20px'}  # Flexbox for alignment
    ),

    # Output message area for feedback
    html.Div(id='upload-feedback', children='', style={'color': 'red'}),
    
    # Slider for the number of top neighbor nodes
    html.Div(id='slider-container', children=[
        html.Label("Select the number of nodes to visualize:"),
        dcc.Slider(
            id='num-nodes-slider',
            min=1,
            max=10,
            step=1,
            value=1,
            marks={i: str(i) for i in range(1, 11)},
            tooltip={"placement": "bottom", "always_visible": False}
        )
    ], style={'display': 'none'}),  # Initially hidden
    
    # Slider for the hierarchy levels
    html.Div(id='level-slider-container', children=[
        html.Label("Select the hierarchy level:", style={'margin-right': '10px'}),
        # Wrap the slider in a Div to control the width
        html.Div(
            dcc.Slider(
                id='level-slider',
                min=1,
                max=4,
                step=1,
                value=1,
                marks={i: str(i) for i in range(1, 5)},  # 1 to 4
                tooltip={"placement": "bottom", "always_visible": False}
            ),
            style={'width': '300px'}  # Set a custom width for the slider wrapper
        ),
        # User input for n next to the slider
        html.Div(children=[
            html.Label('Enter value for n, max. number of codes on the leaves of the tree:', style={'margin-left': '10px', 'margin-right': '10px', 'margin-bottom': '5px'}),
            dcc.Input(
                id='n-input',
                type='number',
                value=4,  # Default value for n
                style={'width': '60px'},
                debounce=False 
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'margin-bottom': '20px'} )  # Flexbox for alignment
    ], style={'display': 'none'}),  # Initially hidden
    
    html.Div([
        html.Label("Select a code:"),
        dcc.Dropdown(
            id='code-dropdown',
            options=[],  # Options will be populated after loading data
            placeholder="Select a code",
            clearable=False
        )
    ]),
    dcc.Checklist(
        id='show-labels',
        options=[{'label': 'Show Labels', 'value': 'show'}],
        value=[]  # Start with an empty list so labels are not shown by default
    ),
    
    dcc.Loading(
        id="loading",
        type="circle",
        children=[
            html.Div(id='data-container', style={'display': 'none'}),  # Hidden div for callbacks
            
        ]
    ),

    # Graphs positioned side-by-side using CSS flexbox
    html.Div([
        # Left column - PyVis graph
        html.Div([
            html.Label("Enter code to search:"),
            dcc.Input(id='code-input', type='text', placeholder='Enter code', debounce=False),  # Debounce=False to update as you type
            html.Iframe(id='graph-iframe', style={'width': '100%', 'height': '100%'}),
        ], style={'flex': '1', 'padding': '10px'}),  # PyVis on the left side, takes 50% of space

        # Right column - Bar chart and dendrogram stacked
        html.Div([
            dcc.Store(id='codes-of-interest-store'),
            dcc.Graph(id='dendrogram', style={ 'width': '100%', 'height': '50%'}),  # Dendrogram below bar chart
            dcc.Graph(id='bar-chart', style={'width': '100%', 'height': '50%'})  # Bar chart on top , 'margin-bottom': '20px'
        ], style={'flex': '1', 'padding': '0px'}),  # Bar chart and dendrogram on the right side, takes 50% of space

    ], style={'display': 'flex', 'flex-direction': 'row'}),  # Use flexbox to position the graphs side by side
    
    dcc.Store(id='data-store')  # Hidden store to keep data
])



# #### 7.2.4  `create_co_occurrence_matrix` Function
# 
# This function generates a co-occurrence matrix from a DataFrame containing `PatientID` and associated `Codes`.
# 
# - **Input**: `df`, a pandas DataFrame with columns:
#   - `PatientID`: Unique identifier for each patient.
#   - `Codes`: ICD,OPS, LOINC codes associated with each patient.
# 
# - **Process**:
#   1. **Check for Empty Data**: Returns an empty DataFrame if `df` is empty.
#   2. **Create Patient-Code Matrix**: Builds a matrix with `PatientID` as rows and unique `Codes` as columns. Each cell shows code occurrences per patient.
#   3. **Filter Columns**: Removes columns where all values are zero.
#   4. **Calculate Co-Occurrence Matrix**: Uses the dot product of the matrix with its transpose to calculate co-occurrences.
#   5. **Remove Self-Connections**: Sets diagonal elements to zero to ignore self-co-occurrences.
# 
# - **Output**: A symmetric DataFrame where rows and columns represent codes, and each cell shows the count of co-occurrences between each code pair across patients.
# 

# In[5]:


# Create co-occurrence matrices
def create_co_occurrence_matrix(df):
    if df.empty:
        return pd.DataFrame()
    patient_matrix = df.pivot_table(index='PatientID', columns='Codes', aggfunc='size', fill_value=0)
    patient_matrix = patient_matrix.loc[:, (patient_matrix != 0).any(axis=0)]
    co_occurrence_matrix = patient_matrix.T.dot(patient_matrix)
    np.fill_diagonal(co_occurrence_matrix.values, 0)
    return co_occurrence_matrix


# #### 7.2.5 `normalize_weights` Function
# 
# This function applies normalization to a given weight `value`. The goal is to rescale the node size and edge thickness depending on the variance of the weights in the dataset.
# 
# - **Input**: 
#   - `value`: The weight value to be normalized.
#   - `gain` (optional, default = 1): Multiplier to scale the input `value`.
#   - `offset` (optional, default = 0): Value to add after scaling.
#   - `min_limit` (optional): Minimum allowable value after normalization.
#   - `max_limit` (optional): Maximum allowable value after normalization.
# 
# - **Process**:
#   1. **Scaling and Offset**: Applies the formula `(value * gain) + offset` to scale `value`.
#   2. **Boundary Check**: 
#      - If `min_limit` is specified, the function ensures `normalized_value` is no less than `min_limit`.
#      - If `max_limit` is specified, it ensures `normalized_value` is no more than `max_limit`.
# 
# - **Output**: The normalized value, constrained within specified `min_limit` and `max_limit`, if they are provided.
# 

# In[6]:


def normalize_weights(value, gain=1, offset=0, min_limit=None, max_limit=None):
    # Normalize the value
    normalized_value = (value * gain) + offset
    
    if min_limit is not None:
        normalized_value = max(min_limit, normalized_value)
    if max_limit is not None:
        normalized_value = min(max_limit, normalized_value)

    return normalized_value


# #### 7.2.6 `generate_network_viz` Function
# The `generate_network_viz` function creates a network visualization using the PyVis library, transforming a pandas DataFrame into a NetworkX graph, applying various visual attributes such as node colors, edge colors, and thickness, while also allowing for specific layouts like circular arrangements for nodes at a selected level, and incorporating physics parameters to enhance the visual representation of relationships in the data.
# 
# 
# This function creates an interactive network visualization using PyVis based on input parameters that control the layout, colors, and network physics properties.
# 
# - **Input**:
#   - `df`: DataFrame containing the network edges and weights.
#   - `code1_col` and `code2_col`: Columns in `df` defining the nodes in each edge.
#   - `weight_col`: Column in `df` representing edge weights.
#   - `layout` (default = 'barnes_hut'): Layout algorithm for positioning nodes.
#   - `selected_level` (optional): Level of hierarchy to visually emphasize.
#   - `node_color` (optional): Dictionary specifying colors for each node.
#   - `edge_color` (optional): Dictionary specifying colors for each edge.
#   - `edge_thickness_min` & `edge_thickness_max`: Min/max thickness for edges.
#   - `central_gravity`, `node_distance`, `spring_length`, `spring_constant`, `spring_strength`, `damping`, `min_velocity`: Physics properties for layout behavior.
# 
# - **Process**:
#   1. **Graph Creation**: Converts the DataFrame `df` to a NetworkX graph `G`.
#   2. **PyVis Network Initialization**: Initializes a PyVis `Network` object, applying color and size specifications.
#   3. **Node Customization**: Sets color for nodes based on `node_color` or defaults to gray if no color is provided.
#   4. **Edge Customization**:
#      - Colors each edge using `edge_color` or defaults to semi-transparent white.
#      - Adjusts edge thickness by normalizing `weight_col` values using `normalize_weights`.
#   5. **Layout Adjustment for Selected Level**: Applies a circular layout to nodes at `selected_level`, scaling positions for clear visualization.
#   
# - **Output**: Returns a PyVis `Network` object (`net`) ready for rendering in an interactive visualization.
# 
# #### Physics
# 
# #### net.toggle_physics(True)
# A physics control button will appear in the visualization, allowing users to dynamically adjust the following parameters:
# 
# - **central_gravity**: Influences the strength of the attractive force toward the center of the network.
# - **node_distance**: Sets the minimum distance between nodes in the graph.
# - **spring_length**: Determines the resting length of the springs connecting the nodes.
# - **spring_constant**: Affects the stiffness of the springs; a higher value results in a stronger pull between nodes.
# - **spring_strength**: Governs how strongly nodes are attracted to each other.
# - **damping**: Controls the damping effect, which reduces oscillations in node movement over time.
# - **min_velocity**: Sets the minimum speed for the nodes in the simulation, ensuring they do not come to a complete stop. 
# 
# #### net.toggle_physics(False)
# The `net.toggle_physics(False)` line, when uncommented, disables the physics simulation in the PyVis network visualization, allowing for a static layout of the nodes and edges, which can help maintain the arrangement of the graph when presenting the network without dynamic movement.
# 
# 

# In[7]:


def generate_network_viz(df, code1_col, code2_col, weight_col, 
                         layout='barnes_hut', selected_level=None,  
                         node_color=None, edge_color=None,
                         edge_thickness_min=1, edge_thickness_max=10,
                         central_gravity=0,
                         node_distance=200,
                         spring_length=0,
                         spring_constant=0.3,
                         spring_strength=0.005,
                         damping=0.5,
                        min_velocity=0.75):
    # Generate a NetworkX graph
    G = nx.from_pandas_edgelist(df, source=code1_col, target=code2_col, edge_attr=weight_col)

    bgcolor, font_color = 'white', 'gray'  # Default colors

    # Initiate PyVis network object
    net = Network(
        height='700px', 
        width='100%',
        bgcolor=bgcolor, 
        font_color=font_color, 
        notebook=True
    )

    # Take NetworkX graph and translate it to a PyVis graph format
    net.from_nx(G)

    # Set colors for nodes and sizes
    if node_color is not None:
        for node in G.nodes():
            net.get_node(node)['color'] = node_color.get(node, 'gray')  # Default to gray if no color is provided

    # Set colors and thickness for edges
    if edge_color is not None:
        for u, v in G.edges():
            net.get_edge(u, v)['color'] = edge_color.get((u, v), 'rgba(255, 255, 255, 0.3)')  # Default to white with transparency
            thickness = G.edges[u, v].get(weight_col, 1)  # Default thickness if not set
            thickness = normalize_weights(thickness, gain=5, offset=1, 
                                          edge_thickness_min=edge_thickness_min, 
                                          edge_thickness_max=edge_thickness_max)
            net.get_edge(u, v)['width'] = thickness

    # Apply circular layout only for nodes at the selected level
    if selected_level is not None:
        level_nodes = df[df['level'] == selected_level][code1_col].unique()
        
        # Compute circular layout for all nodes in G
        pos = nx.circular_layout(G)  # Removed the `nodes` argument

        # Setting positions for the network for the selected level nodes
        for node in level_nodes:
            if node in pos:  # Check if node is in the computed positions
                net.get_node(node)['x'] = pos[node][0] * 300  # Scale position for visualization
                net.get_node(node)['y'] = pos[node][1] * 300  # Scale position for visualization
                
    #net.toggle_physics(False)
    net.show_buttons(filter_=['physics'])
    return net


# #### 7.2.7 `create_dendrogram_plot` Function
# 
# This function generates a dendrogram plot using Plotly, displaying hierarchical relationships based on a co-occurrence matrix.
# 
# - **Input**:
#   - `cooccurrence_array`: Matrix array representing co-occurrence distances (inversely proportion with co-occurance matrix values).
#   - `labels`: List of labels for each code in the dendrogram.
#   - `flat_df`: DataFrame containing code and display name information.
#   - `show_labels`: List of options; if it includes 'show', display names will be shown.
# 
# - **Process**:
#   1. **Label Adjustment**:
#      - If `show_labels` includes 'show', retrieves display names from `flat_df` based on `labels`. Defaults to code if display name is missing.
#   2. **Dendrogram Creation**:
#      - Creates a dendrogram plot with Plotly's `create_dendrogram`, arranging the hierarchy with labels at the bottom.
#   3. **Line Color Customization**:
#      - Sets line color of all dendrogram links to gray for visual consistency.
#   4. **Layout Customization**:
#      - Centers the title, hides the x-axis title, sets y-axis title to "Distance," and rotates x-axis labels for readability.
#   
# - **Output**: Returns a Plotly `fig` object containing the dendrogram plot, ready for interactive visualization.
# 
# 

# In[8]:


def create_dendrogram_plot(cooccurrence_array, labels, flat_df, show_labels):

    if 'show' in show_labels:
        # Use 'Displays' from flat_df for labels
        labels = [
            flat_df.loc[flat_df['Codes'] == label, 'Displays'].iloc[0] 
            if not flat_df.loc[flat_df['Codes'] == label, 'Displays'].empty 
            else label  # Fallback to code if display is missing
            for label in labels
        ]

    # Create the dendrogram plot with Plotly
    fig = ff.create_dendrogram(cooccurrence_array, orientation='bottom', labels=labels)

        # Update line color for all links in the dendrogram
    for line in fig.data:
        line.update(line=dict(color='gray'))  # Set your desired color here
    
    # Update layout to improve appearance
    fig.update_layout(
        title='Dendrogram',
        title_x=0.5,
        xaxis_title='',
        yaxis_title='Distance',
        xaxis={'tickangle': -45},  # Rotate labels for better readability
    )
    
    return fig


# #### 7.2.8 `update_slider_visibility` Callback Function
# 
# This function is a Dash callback that dynamically updates the visibility of sliders based on the user's selection in a dropdown menu.
# 
# - **Input**:
#   - `selected_code`: The value of the selected code from the `code-dropdown` component.
# 
# - **Process**:
#   1. **Visibility Logic**:
#      - If the selected code is `'ALL_CODES'`, the function hides the node count slider (`slider-container`) and shows the hierarchy level slider (`level-slider-container`).
#      - For any other selected code, it displays the node count slider and hides the hierarchy level slider.
# 
# - **Outputs**: 
#   - Returns two style dictionaries:
#     - The first controls the display property of `slider-container` (set to `'none'` or `'block'`).
#     - The second controls the display property of `level-slider-container` (set to `'none'` or `'block'`).
# 
# This callback allows the user interface to respond dynamically to user input, improving the overall interactivity of the Dash application.
# 

# In[9]:


@app.callback(
    Output('slider-container', 'style'),
    Output('level-slider-container', 'style'),
    Input('code-dropdown', 'value')
)
def update_slider_visibility(selected_code):
    if selected_code == 'ALL_CODES':
        return {'display': 'none'}, {'display': 'block'}  # Show level slider, hide num-nodes
    else:
        return {'display': 'block'}, {'display': 'none'}  # Show num-nodes slider, hide level slider


# #### 7.2.9 `fetch_and_process_data` Function
# 
# #### Overview
# 
# The `fetch_and_process_data` function is designed to load, validate, and process data from an uploaded file, which contains medical coding information. It integrates this data with additional reference DataFrames (ICD, OPS, and LOINC), generates co-occurrence matrices, and prepares the data for further analysis. This function is essential for handling medical coding data in a structured manner, facilitating better insights and reporting.
#     
# #### Input
# 
# - **`file_content`**:  
#   The raw content of the uploaded file, expected to be in parquet format.
# - **`datasets_dir`**:  
#   Directory of the catalogues that user entered.
#     
# #### Process
# 
# #### 7.2.9.a Read Uploaded Data:
# 
# The function reads the uploaded parquet file into a DataFrame called flat_df.
# 
# #### 7.2.9.b Check Required Columns and Load Catalogue data:
# 
# It checks if the required columns (PatientID, Codes, ResourceType) are present in flat_df. If any are missing, a ValueError is raised. Then load the catalogue data from the user entered directory.
# 
# #### 7.2.9.c Get the labels:
# 
# Here, the parents (and also the labels) of the child codes are derived from the catalogues. A nested function, get_display_label, is defined to retrieve display labels for codes based on their level and resource type (ICD, OPS, LOINC). This function handles different levels of coding (2, 3, and 4) and returns the appropriate display name based on the provided code.
# 
# #### 7.2.9.d Generate Co-occurrence Matrix:
# 
# A co-occurrence matrix is created using the create_co_occurrence_matrix(flat_df), producing a DataFrame that represents the co-occurrence of codes in the dataset.
# 
# #### 7.2.9.e Create Code Pairs:
# 
# Code pairs with their associated weights are generated from the co-occurrence matrix and stored in pairs_df.
# python
# 
# #### 7.2.9.f Build Hierarchies:
# 
# The function builds hierarchies for ICD, OPS, and LOINC codes using the build_hierarchy_and_get_pairs function and catalogue files, which organizes codes into levels, allowing for structured relationships between them.
# 
# #### 7.2.9.g Add Parent Nodes:
# 
# Parent nodes for each resource type (ICD, OPS, LOINC) are added to the new rows list based on their hierarchical structure. This involves counting how many children each parent has and adding that to the new rows.
# 
# #### 7.2.9.h Combine DataFrames:
# 
# The new pairs DataFrame is created by concatenating pairs_df and the new entries generated from the hierarchies. Duplicate pairs are removed using the drop_duplicates method.
# 
# #### 7.2.9.i Fill Displays and Full Displays Column:
# 
# The Displays column in flat_df is populated using the get_display_label function to create meaningful display labels for the codes.
# 
# #### 7.2.9.j Segment DataFrames:
# 
# DataFrames are segmented into ICD_df, LOINC_df, and OPS_df based on the ResourceType, allowing for targeted analysis.
# 
# #### 7.2.9.k Generate Co-occurrence Matrices for Resource Types:
# 
# Co-occurrence matrices for each resource type (ICD, OPS, LOINC) are created using the create_co_occurrence_matrix function, helping to understand the relationships among codes within each type.
# 
# #### Outputs:
# 
# The function returns a dictionary containing the success status, a message, and the processed data, including flat_df, co-occurrence matrices, and new pairs.

# In[10]:


def fetch_and_process_data(file_content,datasets_dir):
    
    
# 7.2.9.a Read Uploaded Data:
    flat_df = pd.read_parquet(io.BytesIO(file_content))
    #print('flat_df:', flat_df)

##################################################################################################    
# 7.2.9.b Check Required Columns and Load Catalogue data:

    required_columns = ['PatientID', 'Codes', 'ResourceType']
    missing_columns = [col for col in required_columns if col not in flat_df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns: {', '.join(missing_columns)}")
        

    dataframes = {}
    file_names = {
        'ICD': 'ICD_Katalog_2023_DWH_export_202406071440.csv',
        'OPS': 'OPS_Katalog_2023_DWH_export_202409200944.csv',
        'LOINC': 'LOINC_DWH_export_202409230739.csv'
    }

    for key, filename in file_names.items():
        file_path = os.path.join(datasets_dir, filename)
        try:
            dataframes[key] = pd.read_csv(file_path)
        except FileNotFoundError:
            return {
                'success': False,
                'message': (
                    f"1. Put the catalogue files into the directory: {datasets_dir}\n"
                    f"2. Refresh the page.\n"
                    f"3. Upload the data.")
            }

    icd_df = dataframes.get('ICD')
    ops_df = dataframes.get('OPS')
    loinc_df = dataframes.get('LOINC')

##################################################################################################
# 7.2.9.c Get the labels:

    def get_display_label(code, level,  resource_type):
        """Retrieve the display label for codes and their associated group or chapter labels based on resource type."""
        code = str(code).strip()

        if resource_type == 'ICD':
            if level == 4:
                result = icd_df.loc[icd_df['ICD_CODE'] == code, 'ICD_NAME']
                if not result.empty:
                    return result.iloc[0]  
            if level == 3:
                gruppe_result = icd_df.loc[icd_df['GRUPPE_CODE'] == code, 'GRUPPE_NURNAME']
                if not gruppe_result.empty:
                    return gruppe_result.iloc[0]
                    
            if level == 2:
                icd_df['KAPITEL_CODE'] = icd_df['KAPITEL_CODE'].astype(str)
                code = str(code).strip()
                kapitel_result = icd_df.loc[icd_df['KAPITEL_CODE'] == code, 'KAPITEL_NURNAME']

                if not kapitel_result.empty:
                    return kapitel_result.iloc[0] 


        elif resource_type == 'OPS':
            if level == 4:
                result = ops_df.loc[ops_df['OPS_CODE'] == code, 'OPS_NAME']
                if not result.empty:
                    return result.iloc[0] 
                
            if level == 3:
                gruppe_result = ops_df.loc[ops_df['GRUPPE_CODE'] == code, 'GRUPPE_NURNAME']
                if not gruppe_result.empty:
                    return gruppe_result.iloc[0] 
                
            if level == 2:
                icd_df['KAPITEL_CODE'] = icd_df['KAPITEL_CODE'].astype(str) 
                code = str(code).strip()
                kapitel_result = ops_df.loc[ops_df['KAPITEL_CODE'] == code, 'KAPITEL_NURNAME']
                if not kapitel_result.empty:
                    return kapitel_result.iloc[0] 

        elif resource_type == 'LOINC':
            if level == 4:            
                result = loinc_df.loc[loinc_df['LOINC_CODE'] == code, 'LOINC_NAME']
                if not result.empty:
                    return result.iloc[0]
                
            if level == 3:
                gruppe_result = loinc_df.loc[loinc_df['LOINC_PROPERTY'] == code, 'LOINC_PROPERTY']
                if not gruppe_result.empty:
                    return gruppe_result.iloc[0] 
                
            if level == 2:
                kapitel_result = loinc_df.loc[loinc_df['LOINC_SYSTEM'] == code, 'LOINC_SYSTEM']
                if not kapitel_result.empty:
                    return kapitel_result.iloc[0] 
        return None  

    
##################################################################################################  
# 7.2.9.d Generate Co-occurrence Matrix:
    
    main_df = create_co_occurrence_matrix(flat_df)
    #print('main_df', main_df)
    
##################################################################################################    
# 7.2.9.e Create Code Pairs:

    code_pairs = []

    for i in range(len(main_df)):
        for j in range(i + 1, len(main_df)):
            code1 = main_df.index[i]
            code2 = main_df.columns[j]
            weight = main_df.iloc[i, j]

            if weight > 0:
                code_pairs.append((code1, code2, weight))

    pairs_df = pd.DataFrame(code_pairs, columns=['Code1', 'Code2', 'Weight'])
    pairs_df['level'] = 4    
    #print('pairs_df', pairs_df)
    
##################################################################################################    
# 7.2.9.f Build Hierarchies:

    def build_hierarchy_and_get_pairs(df, code_column, kapitel_column, gruppe_column):
        if df is None:
            return []

        df = df[df[code_column].isin(flat_df['Codes'])]
        df_subset = df[[kapitel_column, gruppe_column, code_column]]  # Select by column names
        level_0 = []

        for index, row in df_subset.iterrows():
            level_2 = str(row[kapitel_column])
            level_3 = f"{level_2},{str(row[gruppe_column])}"  # Make level unique
            level_4 = f"{level_3},{str(row[code_column])}"

            resource_type1 = get_resource_type(row[code_column])  # Custom function to get resource type

            if resource_type1 == 'ICD':
                level_1 = f"{'ICD'}, {level_4}"
                level_0.append((f"{'FHIR'}, {level_1}"))

            if resource_type1 == 'OPS':
                level_1 = f"{'OPS'}, {level_4}"
                level_0.append((f"{'FHIR'}, {level_1}"))

            if resource_type1 == 'LOINC':
                level_1 = f"{'LOINC'}, {level_4}"
                level_0.append((f"{'FHIR'}, {level_1}"))

        return level_0
    
##################################################################################################    
# 7.2.9.g Add Parent Nodes: 

    icd_level_0 = build_hierarchy_and_get_pairs(icd_df, 'ICD_CODE', 'KAPITEL_CODE', 'GRUPPE_CODE')
    ops_level_0 = build_hierarchy_and_get_pairs(ops_df, 'OPS_CODE', 'KAPITEL_CODE', 'GRUPPE_CODE')  # Adjust column names if necessary
    loinc_level_0 = build_hierarchy_and_get_pairs(loinc_df, 'LOINC_CODE', 'LOINC_SYSTEM', 'LOINC_PROPERTY')  # Adjust column names if necessary

    new_rows = []

    new_rows.append({'Code1':'FHIR' , 'Code2':'ICD' , 'Weight': len(icd_level_0), 'level': 0, 'ResourceType':'ICD'})
    new_rows.append({'Code1':'FHIR' , 'Code2':'OPS' , 'Weight': len(ops_level_0), 'level': 0, 'ResourceType':'OPS'})
    new_rows.append({'Code1':'FHIR' , 'Code2':'LOINC' , 'Weight': len(loinc_level_0), 'level': 0, 'ResourceType':'LOINC'})

    icd_items = [item.split(',')[2] for item in icd_level_0]
    icd_item_counts = Counter(icd_items)

    for item, count in icd_item_counts.items():
        new_rows.append({'Code1': 'ICD', 'Code2': 'icd'+item, 'Weight': count, 'level': 1, 'ResourceType':'ICD',
                        'Displays': 'ICD'})

        icd_items1 = [lvl_0_item.split(',')[3] for lvl_0_item in icd_level_0 if lvl_0_item.split(',')[2] == item]
        icd_item_counts1 = Counter(icd_items1)

        for item1, count1 in icd_item_counts1.items():
            new_rows.append({
                            'Code1': 'icd' + item, 
                            'Code2': item1,          
                            'Weight': count1,        
                            'level': 2,              
                            'ResourceType': 'ICD',   
                            'Displays': get_display_label(item, 2, 'ICD') 
                        })

            icd_items2 = [lvl_0_item.split(',')[4] for lvl_0_item in icd_level_0 if lvl_0_item.split(',')[3] == item1]
            icd_item_counts2 = Counter(icd_items2)

            for item2, count2 in icd_item_counts2.items():
                new_rows.append({
                            'Code1': item1, 
                            'Code2': item2,          
                            'Weight': count2,        
                            'level': 3,              
                            'ResourceType': 'ICD',   
                            'Displays': get_display_label(item1, 3, 'ICD')  
                        })

    ops_items = [item.split(',')[2] for item in ops_level_0]
    ops_item_counts = Counter(ops_items)

    for item, count in ops_item_counts.items():
        new_rows.append({'Code1': 'OPS', 'Code2': 'ops'+item, 'Weight': count, 'level': 1, 'ResourceType':'OPS',
                        'Displays': 'OPS'})

        ops_items1 = [lvl_0_item.split(',')[3] for lvl_0_item in ops_level_0 if lvl_0_item.split(',')[2] == item]
        ops_item_counts1 = Counter(ops_items1)

        for item1, count1 in ops_item_counts1.items():
            new_rows.append({
                            'Code1': 'ops' + item,  
                            'Code2': item1,         
                            'Weight': count1,       
                            'level': 2,              
                            'ResourceType': 'OPS',   
                            'Displays': get_display_label(item, 2, 'OPS')  
                        })

            ops_items2 = [lvl_0_item.split(',')[4] for lvl_0_item in ops_level_0 if lvl_0_item.split(',')[3] == item1]
            ops_item_counts2 = Counter(ops_items2)

            for item2, count2 in ops_item_counts2.items():
                new_rows.append({
                            'Code1': item1,  
                            'Code2': item2,          
                            'Weight': count2,        
                            'level': 3,             
                            'ResourceType': 'OPS',   
                            'Displays': get_display_label(item1, 3, 'OPS')  
                        })

    loinc_items = [item.split(',')[2] for item in loinc_level_0]
    loinc_item_counts = Counter(loinc_items)

    for item, count in loinc_item_counts.items():
        new_rows.append({'Code1': 'LOINC', 'Code2': item, 'Weight': count, 'level': 1, 'ResourceType':'LOINC',
                        'Displays': 'LOINC'})

        loinc_items1 = [lvl_0_item.split(',')[3] for lvl_0_item in loinc_level_0 if lvl_0_item.split(',')[2] == item]
        loinc_item_counts1 = Counter(loinc_items1)

        for item1, count1 in loinc_item_counts1.items():
            new_rows.append({'Code1': item, 'Code2': item1, 'Weight': count1, 'level': 2, 'ResourceType':'LOINC',
                            'Displays':get_display_label(item, 2, 'LOINC') })

            loinc_items2 = [lvl_0_item.split(',')[4] for lvl_0_item in loinc_level_0 if lvl_0_item.split(',')[3] == item1]

            loinc_item_counts2 = Counter(loinc_items2)

            for item2, count2 in loinc_item_counts2.items():
                new_rows.append({'Code1': item1, 'Code2': item2, 'Weight': count2, 'level': 3, 'ResourceType':'LOINC',
                                'Displays':get_display_label(item1, 3, 'LOINC')})


##################################################################################################
# 7.2.9.h Combine DataFrames:¶

    new_entries_df = pd.DataFrame(new_rows)    
    new_pairs_df = pd.concat([pairs_df, new_entries_df], ignore_index=True)
    new_pairs_df = new_pairs_df.drop_duplicates(subset=['Code1', 'Code2', 'Weight','level'])
    #print('new_pairs_df', new_pairs_df)

##################################################################################################
# 7.2.9.i Fill Displays and Full Displays Column:

    flat_df['Displays'] = flat_df.apply(
        lambda row: get_display_label(row['Codes'], 4, row['ResourceType']),
        axis=1
    )

    flat_df['Full_Displays'] = flat_df.apply(
        lambda row: f"{row['Codes']}: {row['Displays']}" if row['ResourceType'] == 'LOINC' else row['Displays'],
        axis=1
    )

    flat_df.loc[flat_df['ResourceType'].isin(['ICD', 'OPS']), 'Displays'] = \
        flat_df.loc[flat_df['ResourceType'].isin(['ICD', 'OPS']), 'Displays'].apply(
            lambda x: ': '.join(x.split(':')[1:]).strip() if isinstance(x, str) else x
        )

    flat_df.loc[flat_df['ResourceType'] == 'LOINC', 'Displays'] = flat_df.loc[flat_df['ResourceType'] == 'LOINC', 'Displays']
   
    
    flat_df['Displays'] = flat_df['Displays'].astype(str)
    
    flat_df['Displays'] = flat_df['Displays'].str.slice(0, 11) + '...'

##################################################################################################
# 7.2.9.j Segment DataFrames:

    ICD_df = flat_df[flat_df['ResourceType'] == 'ICD']
    LOINC_df = flat_df[flat_df['ResourceType'] == 'LOINC']
    OPS_df = flat_df[flat_df['ResourceType'] == 'OPS']
    
##################################################################################################    
# 7.2.9.k Generate Co-occurrence Matrices for Resource Types:
    co_occurrence_matrices = {
        'Main': create_co_occurrence_matrix(flat_df),
        'ICD': create_co_occurrence_matrix(ICD_df),
        'LOINC': create_co_occurrence_matrix(LOINC_df),
        'OPS': create_co_occurrence_matrix(OPS_df)
    }

##################################################################################################
# Outputs:  
    return {
        'success': True,
        'message': 'Data is loaded.',
        'data': {
            'flat_df': flat_df.to_dict(),
            'co_occurrence_matrices': co_occurrence_matrices,
            'new_pairs_df': new_pairs_df.to_dict()  
        }
    }


# #### 7.2.10 `upload_file` Callback Function
# 
# The `upload_file` function is a Dash callback designed to handle file uploads, process the uploaded content, and update the UI accordingly.
# 
# #### Input:
# 
# - **file_content**: The contents of the uploaded file from the `upload-data` component.
# 
# #### Process:
# 
# 1. **Initial Checks**:
#    - If no file is uploaded (`file_content is None`), the function returns a message prompting the user to upload the FHIR dataset, hides the data container, provides an empty list for dropdown options, and sets the data to `None`.
# 
# 2. **Decode Uploaded File**:
#    - If a file is uploaded, the function decodes the base64 encoded content and processes it using the `fetch_and_process_data` function.
# 
# 3. **Handle Processing Result**:
#    - If the processing is successful (`result['success']` is `True`):
#      - Extracts the co-occurrence matrices, the main DataFrame (`flat_df`), and the new pairs DataFrame (`new_pairs_df`).
#      - Prepares dropdown options by prepending "All codes" to the list of available codes extracted from the co-occurrence matrices.
#      - Stores `flat_df`, the co-occurrence matrices (converted to a dictionary), and `new_pairs_df` in a data dictionary for later use.
# 
#    - If processing fails, it captures the failure message to provide feedback to the user.
# 
# #### Outputs:
# 
# - **feedback_message**: A message indicating the result of the file upload (either a success message or a prompt to upload).
# - **data_style**: A style dictionary that controls the display of the data container (set to `'none'` or `'block'`).
# - **options**: The dropdown options for the code selection, including "All codes".
# - **data**: A dictionary containing:
#   - `flat_df`: The processed main DataFrame.
#   - `co_occurrence_matrices`: A dictionary of co-occurrence matrices.
#   - `new_pairs_df`: The DataFrame containing new pairs.
# 
# This callback function enhances user interactivity in the Dash application by dynamically updating the UI based on user file uploads.
# 
# 

# In[11]:


@app.callback(
    Output('upload-feedback', 'children'),
    Output('data-container', 'style'),
    Output('code-dropdown', 'options'),
    Output('data-store', 'data'),  # Store `flat_df` and matrices here
    Input('upload-data', 'contents'),
    Input('directory-input', 'value')  # Capture the directory input
)
def upload_file(file_content, directory):

    datasets_dir = directory.strip()  # Remove leading/trailing whitespace

    if file_content is None:
        return "Please upload the FHIR dataset.", {'display': 'none'}, [], None
    feedback_message = ""
    data_style = {'display': 'none'}
    options = []
    data = {}

    if file_content:
        # Decode and process uploaded file
        content_type, content_string = file_content.split(',')
        decoded = base64.b64decode(content_string)
        result = fetch_and_process_data(decoded, datasets_dir)


        if result['success']:
            co_occurrence_matrices = result['data']['co_occurrence_matrices']
            flat_df = result['data']['flat_df']
            new_pairs_df = result['data']['new_pairs_df']  # Retrieve new_pairs_df
            
            # Prepend "All codes" to the dropdown options
            options = [{'label': 'All codes', 'value': 'ALL_CODES'}] + [{'label': code, 'value': code} for code in co_occurrence_matrices.get('Main', pd.DataFrame()).columns]

            # Update this part in upload_file callback
            data = {
                'flat_df': flat_df,  # Store the `flat_df` here
                'co_occurrence_matrices': {
                    key: matrix.to_dict() for key, matrix in co_occurrence_matrices.items()
                },
                'new_pairs_df': new_pairs_df  # Store new_pairs_df here directly
            }

            feedback_message = result['message']
            data_style = {'display': 'block'}
        else:
            feedback_message = result['message']

    return feedback_message, data_style, options, data



# #### 7.2.11 Dash callback: `update_graph`
# 
# #### Inputs
# 
# - **code-dropdown**:  
#   A dropdown menu that allows users to select a specific code.
# 
# - **num-nodes-slider**:  
#   A slider that determines the number of nodes to visualize in the graph.
# 
# - **level-slider**:  
#   A slider used to set the hierarchy level for graph visualization.
# 
# - **show-labels**:  
#   A toggle switch that allows users to choose whether or not to display labels on the graph.
# 
# - **code-input**:  
#   A text input field for users to enter custom codes to highlight the code and its connections.
# 
# - **n-input**:  
#   A numerical input field that specifies how many top nodes (with highest degrees) should be displayed.
# 
# - **data-store**:  
#   Load necessary data frames (`flat_df`, `co_occurrence_matrices`, `new_pairs_df`, `main_df`) from the `data-store`.
# 
# #### 7.2.11.a All Codes: Visualization of the Pyvis Graphs
# 
# The code implements a Dash callback function called `update_graph`, which dynamically updates various components of a web application based on user input. This input can come from dropdown selections, sliders, and direct text entries. The function utilizes the PyVis library to generate a graph visualization and updates the data stored in the application's backend.
# 
# #### Process
# 
# #### 7.2.11.a.1 Edge Thickness Range:  
#    The function begins by defining constants for edge thickness. It checks if the required data is loaded; if not, it returns default values, which hide the graph and charts.
# 
# #### 7.2.11.a.2 Style Initialization:  
#    The initial styles for graph and chart components are set to hidden, preparing the layout for subsequent updates.
# 
# #### 7.2.11.a.3 Code Selection Validation:  
#    If no code has been selected from the dropdown, the function returns empty data and hides all relevant components.
# 
# #### 7.2.11.a.4 Data Preparation:  
#    The function attempts to read essential data from the `data-store`, retrieving DataFrames such as `flat_df`, `co_occurrence_matrices`, `new_pairs_df`, and `main_df`. If an error occurs during data retrieval, it returns empty data.
# 
# #### 7.2.11.a.5 Node Size and Shape Mapping:  
#    Node sizes and shapes are determined based on their hierarchical levels (0-4), with this information stored in mapping dictionaries for easy reference later on.
# 
# #### 7.2.11.a.6 Node Degree Calculation:  
#    A helper function computes the degree of each node, indicating the number of connections it has. This calculation helps identify the most significant nodes within the graph.
# 
# #### 7.2.11.a.7 Top Nodes Selection:  
#    The function selects the top n nodes based on their degree, grouping them by resource types. This filtered list is crucial for the visualization process.
# 
# #### 7.2.11.a.8 Data Filtering by Levels:  
#    The function iterates through levels from 4 down to 0, filtering `new_pairs_df` to gather relevant connections for the codes of interest. It collects ancestor codes and prepares a consolidated DataFrame named `result_df`.
# 
# #### 7.2.11.a.9 Weight Calculation:  
#    A separate function calculates the weights for nodes based on their hierarchical levels and connections. This weight influences the thickness of edges in the final visualization.
# 
# #### 7.2.11.a.10 Graph Update Logic:  
#    
#    - The core logic for constructing the network graph is executed. The function updates node and edge attributes, such as color and size, based on node types and their connections.
#    
#         ##### Helper Function: `update_fhir_net`
#         The `update_fhir_net` function processes a DataFrame to translate codes between levels and aggregate weight data passed from the child to the parent. By this code, we can see the connection of the codes on each hierarchy level.
# 
#         #### Inputs
# 
#         - **df_int** (`pd.DataFrame`):  
#           The input DataFrame containing columns such as `level`, `Code1`, `Code2`, `Weight`, `ResourceType`, and `Displays`. This DataFrame holds hierarchical coding data that needs to be processed.
# 
#         - **level** (`int`):  
#           An integer specifying the level down to which the processing should occur. The function will work from level 3 down to the specified `level`.
# 
#         #### Process
# 
#         1. **Copy Input DataFrame**:  
#            A copy of the input DataFrame (`df_int`) is created to avoid modifying the original data.
# 
#         2. **Generate Levels to Process**:  
#            A list of levels to process is created, starting from 3 down to one level above the specified `level`. For example, if `level` is 2, the list would be `[3, 2]`.
# 
#         3. **Iterate Over Levels**:  
#            The function iterates over each `current_level` in the `levels_to_process` list:
# 
#            - **Filter Rows for Current Level**:  
#              Rows corresponding to the `current_level` are filtered from the DataFrame.
# 
#            - **Create Translation Dictionary**:  
#              A dictionary (`translation_dict`) is created to map `Code2` values to their corresponding `Code1` values.
# 
#            - **Identify Next Level**:  
#              The next level is determined by incrementing the `current_level`.
# 
#            - **Filter Rows for Next Level**:  
#              Rows for the `next_level` are also filtered from the DataFrame.
# 
#            - **Create Mask for Dropping Rows**:  
#              A mask is created to identify rows in the `next_level` DataFrame where `Code1` or `Code2` are not present in the current level's `Code2`.
# 
#            - **Drop Unnecessary Rows**:  
#              Rows that match the mask criteria are dropped from the main DataFrame.
# 
#            - **Apply Translation to Next Level**:  
#              The `Code1` and `Code2` values in the `next_level` rows are updated using the `translation_dict` to replace values as needed.
# 
#            - **Delete Current Level Rows**:  
#              Rows from the current level are removed from the DataFrame, specifically where `Code1` is equal to `Code2`.
# 
#            - **Group and Aggregate Data**:  
#              The remaining DataFrame is grouped by `Code1`, `Code2`, `level`, `ResourceType`, and `Displays`, summing the `Weight` for duplicate entries.
# 
#            - **Adjust Level Values**:  
#              The level value of entries that were previously at the `current_level + 1` is replaced with the `current_level`.
# 
#            - **Update DataFrame for Next Iteration**:  
#              The grouped DataFrame becomes the new DataFrame for the next iteration.
# 
#         4. **Return Final DataFrame**:  
#            After processing all levels, the function returns the final grouped DataFrame.
# 
#         #### Outputs
# 
#         - **Returns** (`pd.DataFrame`):  
#           The final DataFrame after all processing, containing aggregated rows with updated code translations and summed weights, based on the specified hierarchy of codes.
# 
# 
# 
# #### 7.2.11.a.11 Highlight User Selection:  
#    If a user has entered a code via the `code-input`, that specific node is highlighted in the visualization, along with its related connections.
# 
# #### 7.2.11.a.12 Graph Visualization:  
#    The `generate_network_viz` function is called to create the network graph. The generated graph is saved as an HTML file, which will be displayed in an iframe within the web application.
# 
# #### Outputs
# 
# The function produces multiple outputs, updating the following components:
# 
# - **graph-iframe**:  
#   Displays the generated graph visualization as an HTML element.
# 
# - **codes-of-interest-store**:  
#   Stores information related to codes of interest for future reference.
# 
# - **Various style properties**:  
#   Updates style properties for the graph iframe and other components (such as bar charts and dendrograms).
# 
# 
# 
# #### 7.2.11.b Individual codes: Visualization of the Pyvis Graphs
# 
# This code snippet defines a process for updating a network graph in a Dash application based on selected individul code. It calculates node sizes and edges, visualizes relationships between codes, and prepares data for rendering in an HTML format.
# 
# 
# #### Process
# 
# #### 7.2.11.b.1 Node Size and Style Initialization:  
#    The minimum and maximum node sizes are defined, along with styles for the graph, bar chart, and dendrogram.
# 
# #### 7.2.11.b.2 Node Degree Calculation:  
#    The function calculates the degree (number of neighbors) for each node using `main_df`.
# 
# #### 7.2.11.b.3 Top Nodes Selection:  
#    The top 30 nodes based on degree are identified and their degrees printed.
# 
# #### 7.2.11.b.4 Defining the weight range to rescale the node size and edge thickness:  
#    The minimum and maximum weights from the top degrees are calculated for normalization purposes.
# 
# #### 7.2.11.b.5 Neighbor Retrieval:  
#    If the `selected_code` is not present in `main_df`, the function returns empty data. If present, the neighbors of the selected code are sorted, and the top neighbors are identified.
# 
# #### 7.2.11.b.6 Nodes and Edges Addition:  
#    A helper function, `add_nodes_edges`, is defined to:
#    - Iterate over neighbor codes to find the top neighbor based on the specified group (ICD, LOINC, OPS).
#    - Retrieve top neighbor information and associated labels.
#    - Normalize node sizes based on their degree.
#    - Add nodes and edges to the network, ensuring no duplicate nodes or edges are created.
# 
#         ##### Helper Function: `add_nodes_edges`
# 
#         The `add_nodes_edges` function is designed to construct and enhance a network graph by adding nodes and edges based on neighbor relationships. This function integrates various criteria to ensure that the network accurately represents the connections between nodes.
# 
#         #### Purpose
# 
#         The function performs the following key tasks:
# 
#         - **Identify the Top Neighbor**:  
#           It identifies the most relevant neighbor based on the specified grouping (ICD, LOINC, OPS).
# 
#         - **Add Nodes to the Network**:  
#           The function adds the selected code, the top neighbor, and additional related neighbors as nodes in the graph.
# 
#         - **Establish Connections (Edges)**:  
#           It creates edges between nodes based on their relationships and normalized weights.
# 
#         #### Inputs
# 
#         - **graph**:  
#           The network graph object to which nodes and edges will be added.
# 
#         - **child_df**:  
#           A DataFrame containing connection data between codes, which helps determine relationships and weights.
# 
#         - **group_name**:  
#           A string indicating the group classification for the neighbors (e.g., 'ICD', 'LOINC', 'OPS').
# 
#         #### Processes
# 
#         1. **Initialization**:  
#            The function starts by initializing a variable to store the top neighbor.
# 
#         2. **Identify Top Neighbor**:  
#            The function iterates through a sorted list of neighbor codes to find the first code that matches the specified group type (ICD, LOINC, or OPS). Once a match is found, it sets that code as the top neighbor.
# 
#         3. **Retrieve Neighbor Information**:  
#            If a top neighbor is found, the function retrieves and sorts its connection data from `child_df` to create a list of the most significant neighbors.
# 
#         4. **Extend Codes of Interest**:  
#            The function updates a list of codes of interest by adding the top neighbor and its most significant connections.
# 
#         5. **Determine Node Sizes**:  
#            Node sizes are determined based on their degrees (connections). The size is normalized to fit within specified limits (e.g., `NODE_SIZE_MIN` and `NODE_SIZE_MAX`).
# 
#         6. **Add Nodes**:  
#            - The selected code and the top neighbor are added as nodes to the network if they do not already exist.
#            - The nodes are given attributes such as size, label, and color based on their group classification.
# 
#         7. **Add Edges for Selected Code and Top Neighbor**:  
#            If both the selected code and the top neighbor exist in the network, the function creates an edge between them, normalized by weight.
# 
#         8. **Process Additional Neighbors**:  
#            The function loops through the top neighbors list to:
#            - Add each neighbor as a node if it is not already present.
#            - Create edges between the top neighbor and each of its neighbors based on their connections.
# 
#         9. **Create Edges Between Top Neighbors**:  
#            Finally, the function establishes edges between each pair of top neighbors to reflect their connections.
# 
#         #### Outputs
# 
#         - **Returns**:  
#           The function does not explicitly return a value; however, it modifies the provided `graph` object by adding nodes and edges based on the specified relationships and criteria.
# 
# 
# 
# #### 7.2.11.b.7 ResourceType dependant Co-Occurrence Matrix Processing:  
#    The function checks for specific keys in `co_occurrence_matrices` and calls `add_nodes_edges` for each type (ICD, LOINC, OPS) to populate the network with corresponding edges.
# 
# #### 7.2.11.b.8 Temporary File Generation:  
#    A temporary HTML file is created to store the graph visualization, which is saved and rendered.
# 
# #### Outputs
# 
# - **Graph Visualization**:  
#   The HTML content of the generated graph, which is rendered in the application.
# 
# - **codes_of_interest**:  
#   A list of codes of interest based on the selected code and its neighbors.
# 
# - **top_neighbor_info**:  
#   Information about the top neighbor, including the neighbor list.
# 
# - **graph_style**:  
#   The style properties for the graph visualization.
# 
# - **bar_chart_style**:  
#   The style properties for the bar chart visualization.
# 
# - **dendrogram_style**:  
#   The style properties for the dendrogram visualization.
# 
# 

# In[12]:


@app.callback(
    [Output('graph-iframe', 'srcDoc'),
     Output('codes-of-interest-store', 'data'),
     Output('graph-iframe', 'style'),
     Output('bar-chart', 'style'),
     Output('dendrogram', 'style')],
    [Input('code-dropdown', 'value'),
     Input('num-nodes-slider', 'value'),
     Input('level-slider', 'value'),
     Input('show-labels', 'value'),
     Input('code-input', 'value'),  # Add input for user code
     Input('n-input', 'value'),
     State('data-store', 'data')]
)


def update_graph(selected_code, num_nodes_to_visualize, selected_level, show_labels, user_code, n, data):

#### 7.2.11.a.1 Edge Thickness Range:  

    EDGE_THICKNESS_MIN = 1
    EDGE_THICKNESS_MAX = 32
    
    if not data:
        return "No data loaded.", None, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
    
#### 7.2.11.a.2 Style Initialization: 

    graph_style = {'display': 'none'}
    bar_chart_style = {'display': 'none'}
    dendrogram_style = {'display': 'none'}
    
#### 7.2.11.a.3 Code Selection Validation:  

    if not selected_code:
        return "", {'codes_of_interest': [], 'top_neighbor_info': {}}, graph_style, bar_chart_style, dendrogram_style

    # Initialize PyVis network
    net = Network(notebook=True, cdn_resources='remote')

#### 7.2.11.a.4 Data Preparation: 

    try:
        flat_df = pd.DataFrame(data.get('flat_df', {}))
        co_occurrence_matrices = data.get('co_occurrence_matrices', {})
        new_pairs_df = pd.DataFrame(data.get('new_pairs_df', {}))  # Access new_pairs_df
        main_df = pd.DataFrame(co_occurrence_matrices.get('Main', {}))
    except Exception as e:
        print(f"Error processing data: {e}")
        return "", {'codes_of_interest': [], 'top_neighbor_info': {}}, graph_style, bar_chart_style, dendrogram_style

    codes_of_interest = []
    top_neighbor_info = {}
    flat_df['Color'] = flat_df['ResourceType'].map(SUBGROUP_COLORS)
    color_mapping = flat_df.set_index('ResourceType')['Color'].to_dict()

    
#################################################### IF ALL_CODES ##################################################

    if selected_code == 'ALL_CODES':               

#### 7.2.11.a.5 Node Size and Shape Mapping:  

        NODE_SIZE_MIN = 4
        NODE_SIZE_MAX = 32

        delta_limit = NODE_SIZE_MAX-NODE_SIZE_MIN 

        size_mapping = {
            0: NODE_SIZE_MAX,  # Size for level 0
            1: (delta_limit / 4) * 3,  # Size for level 1
            2: (delta_limit / 4) * 2,  # Size for level 2
            3: (delta_limit / 4) * 2,  # Size for level 3
            4: delta_limit / 4   # Size for level 4
        }
        
        shape_mapping = {
            0: 'dot',          # For level 0 (default)
            1: 'triangleDown',     # For level 1
            2: 'square',      # For level 2
            3: 'star',         # For level 3
            4: 'dot',       # For level 4
        }
        
#### 7.2.11.a.6 Node Degree Calculation: 

        def calculate_node_degrees(co_occurrence_matrix):
            # Degree is the sum of co-occurrences for each node across all neighbors
            node_degrees = co_occurrence_matrix.sum(axis=1).reset_index()
            node_degrees.columns = ['Node', 'Degree']
            return node_degrees
        
        node_degrees = calculate_node_degrees(main_df)

        # Applying get_resource_type to each node
        node_degrees['ResourceType'] = node_degrees['Node'].apply(get_resource_type)
        

#### 7.2.11.a.7 Top Nodes Selection:  

        # Group by ResourceType, sort by Degree in descending order, and take the top 'n' nodes for each group
        top_n_per_resource = node_degrees.groupby('ResourceType').apply(lambda x: x.nlargest(n, 'Degree')).reset_index(drop=True)

        
#### 7.2.11.a.8 Data Filtering by Levels:    

        result_df = pd.DataFrame()

        top_nodes = top_n_per_resource['Node'].tolist()

        # Create a set for level 4 codes using top_nodes
        level4_codes = set(top_nodes)

        # Track Code2 values for ancestors
        ancestor_codes = set()

        # Loop through levels from 4 to 0
        for level in range(4, -1, -1):
            if level == 4:
                level_df = new_pairs_df[(new_pairs_df['level'] == level) & 
                                         (new_pairs_df['Code1'].isin(top_nodes) | 
                                          new_pairs_df['Code2'].isin(top_nodes))]

                ancestor_codes.update(level_df['Code2'].unique())
                prev_level_code1 = set(level_df['Code1']).union(set(level_df['Code2']))

            else:
                level_df = new_pairs_df[(new_pairs_df['level'] == level) & 
                                         (new_pairs_df['Code2'].isin(prev_level_code1)) |
                                         (new_pairs_df['Code1'].isin(ancestor_codes))]  # Include ancestors for all lower levels
                prev_level_code1 = set(level_df['Code1'])
                
            level_code1 = level_df['Code1'].unique()

            result_df = pd.concat([result_df, level_df], ignore_index=True)
        result_df.to_csv('result_df-ancestors.csv')
        
        # Create a dictionary to store total weights for level 3 Code2 values
        level3_weights_dict = {}

        # Iterate over each row in result_df where level is 3
        for index, row in result_df[result_df['level'] == 3].iterrows():
            code2_value = row['Code2']

            # Check if the Code2 value exists in the level 4 codes
            if code2_value in level4_codes:
                # Assign the degree from node_degrees to the level 3 weights dictionary
                degree_value = node_degrees[node_degrees['Node'] == code2_value]['Degree']

                # Check if the degree value exists and assign it
                if not degree_value.empty:
                    level3_weights_dict[code2_value] = degree_value.values[0]
                else:
                    level3_weights_dict[code2_value] = 0  # Default to 0 if not found

        # Update the Weight in level 3 rows based on the calculated total weights
        result_df.loc[result_df['level'] == 3, 'Weight'] = result_df.loc[result_df['level'] == 3, 'Code2'].map(level3_weights_dict)

             
#### 7.2.11.a.9 Weight Calculation:  

        def calculate_weights(levels):
            for current_level in levels:
                # 1: Calculate total weights for each Code1 in the current level
                level_weights = result_df[result_df['level'] == current_level].groupby('Code1')['Weight'].sum().reset_index()
                level_weights.rename(columns={'Weight': 'TotalWeight'}, inplace=True)

                # 2: Assign weights from the current level to the next lower level
                next_level = current_level - 1
                for index, row in result_df[result_df['level'] == next_level].iterrows():
                    code2_value = row['Code2']

                    if code2_value in level_weights['Code1'].values:
                        total_weight = level_weights.loc[level_weights['Code1'] == code2_value, 'TotalWeight'].values[0]
                        result_df.at[index, 'Weight'] = total_weight

        # Call the function with levels in descending order
        calculate_weights(levels=[3, 2, 1])

#### 7.2.11.a.10 Graph Update Logic:  


##### Helper Function: `update_fhir_net` 

        def update_fhir_net(df_int, level):

            df = df_int.copy()  

            levels_to_process = list(range(3, level-1, -1))  # Create a list [3, 2, ..., level]

            for current_level in levels_to_process:
                # 1: Filter rows for the current level
                level_rows = df[df['level'] == current_level].copy()

                # 2: Create a translation dictionary from Code2 to Code1
                translation_dict = dict(zip(level_rows['Code2'], level_rows['Code1']))
                #print('translation_dict', translation_dict)

                next_level = current_level + 1

                # 3: Filter rows for the next level
                df_next_level = df[df['level'] == next_level].copy()

                # 4: Create the mask for rows where Code1 or Code2 are NOT in level_rows['Code2']
                mask = ~df_next_level['Code1'].isin(level_rows['Code2']) | ~df_next_level['Code2'].isin(level_rows['Code2'])

                # 5: Drop rows where mask is True
                df = df.drop(df_next_level[mask].index, errors='ignore')

                # 6: Apply the translation to the next level rows (level + 1)                
                df.loc[df['level'] == next_level, 'Code1'] = df.loc[df['level'] == next_level, 'Code1'].apply(lambda x: translation_dict.get(x, x))
                df.loc[df['level'] == next_level, 'Code2'] = df.loc[df['level'] == next_level, 'Code2'].apply(lambda x: translation_dict.get(x, x))
                
                # 7: Delete rows of the current level
                df_del = df[df['level'] != current_level]
                df_del = df_del[df_del['Code1'] != df_del['Code2']]

                # 8: Group by Code1, Code2, level, ResourceType, and Displays, and sum the weights for duplicates
                df_grouped = df_del.groupby(['Code1', 'Code2', 'level'], as_index=False).agg({
                    'Weight': 'sum',
                    'ResourceType': 'first',
                    'Displays': 'first'
                })

                # 9: Replace level 4 with level 3 (if applicable)
                df_grouped.loc[df_grouped['level'] == current_level + 1, 'level'] = current_level 

                # 10: Update the DataFrame for the next iteration
                df = df_grouped

            return df_grouped
        
        
        if selected_level==4:
            filtered_pairs_df = result_df

        else:
            filtered_pairs_df = update_fhir_net(result_df, selected_level)
    
        fhir_net = generate_network_viz(filtered_pairs_df, 
                                          code1_col='Code1', 
                                          code2_col='Code2', 
                                          weight_col='Weight', 
                                          layout='barnes_hut',
                                          edge_thickness_min=EDGE_THICKNESS_MIN, 
                                          edge_thickness_max=EDGE_THICKNESS_MAX,
                                           selected_level=selected_level)


        min_weight = filtered_pairs_df['Weight'].min()
        max_weight = filtered_pairs_df['Weight'].max()
        
        node_resource_type_map = {}

        for _, row in result_df.iterrows():
            if row['level'] in [1, 2, 3]:  # If level is 1 or 2
                node_resource_type_map[row['Code1'].strip()] = row['ResourceType']
            elif row['level'] == 4:  # If level is 4, assign resource types using the get_resource_type function
                node_resource_type_map[row['Code1'].strip()] = get_resource_type(row['Code1'].strip())
                node_resource_type_map[row['Code2'].strip()] = get_resource_type(row['Code2'].strip())


#         for node, resource_type in node_resource_type_map.items():
#             print(f"{node}: {resource_type}")

        key_nodes_resource_type = {
            'FHIR': 'FHIR',
            'ICD': 'ICD',
            'LOINC': 'LOINC',
            'OPS': 'OPS'
        }

        node_resource_type_map.update(key_nodes_resource_type)

        for edge in fhir_net.edges:
            from_node = edge['from'].strip()
            to_node = edge['to'].strip()

            from_resource_type = node_resource_type_map.get(from_node, None)
            to_resource_type = node_resource_type_map.get(to_node, None)

            edge_color = 'rgba(128, 128, 128, 0.3)'

            if from_resource_type and to_resource_type and from_resource_type == to_resource_type:
                edge_color = color_mapping.get(from_resource_type, 'gray')  # Use the color for the shared resource type
                edge_color = color_mapping.get(to_resource_type, 'gray')
            else:
                if from_node == 'FHIR' and to_node in ['ICD', 'OPS', 'LOINC']:
                    edge_color = color_mapping.get(to_resource_type, 'gray')  # Use color of the connected node
                elif to_node == 'FHIR' and from_node in ['ICD', 'OPS', 'LOINC']:
                    edge_color = color_mapping.get(from_resource_type, 'gray')  # Use color of the connected node

            edge['color'] = edge_color

            weight_value = filtered_pairs_df[
                ((filtered_pairs_df['Code1'].str.strip() == from_node) & 
                 (filtered_pairs_df['Code2'].str.strip() == to_node)) |
                ((filtered_pairs_df['Code1'].str.strip() == to_node) & 
                 (filtered_pairs_df['Code2'].str.strip() == from_node))
            ]['Weight']

            if not weight_value.empty:
                weight_value = weight_value.values[0]

                normalized_thickness = normalize_weights(
                    weight_value,
                    gain=(EDGE_THICKNESS_MAX - EDGE_THICKNESS_MIN) / (max_weight - min_weight),
                    offset=EDGE_THICKNESS_MIN,
                    min_limit=EDGE_THICKNESS_MIN,
                    max_limit=EDGE_THICKNESS_MAX
                )
                edge['width'] = normalized_thickness
            else:
                edge['width'] = EDGE_THICKNESS_MIN  # Default edge thickness

        level_4_nodes_by_type = {}

        for node in fhir_net.nodes:
            level = result_df.loc[result_df['Code1'] == node['id'], 'level'].values
            level = level[0] if len(level) > 0 else None

            node['size'] = size_mapping.get(level, 5)

            if node['id'] == 'FHIR':
                color = 'black' 
                node['title'] = 'Fast Healthcare Interoperability Resources'
            if node['id'] == 'ICD':
                node['title'] = 'International Statistical Classification of Diseases and Related Health Problems'
            if node['id'] == 'OPS':
                node['title'] = 'Operationen- und Prozedurenschlüssel'
            if node['id'] == 'LOINC':
                node['title'] = 'Logical Observation Identifiers Names and Codes'
                
            if level in [1, 2, 3]:  
                resource_type = result_df.loc[result_df['Code1'] == node['id'], 'ResourceType'].values
                if len(resource_type) > 0:
                    color = color_mapping.get(resource_type[0], 'gray')
                else:
                    color = 'gray'

                if 'show' in show_labels: 
                    display_label = result_df.loc[result_df['Code1'] == node['id'], 'Displays'].values
                    if len(display_label) > 0 and display_label[0] is not None:
                        full_display = display_label[0]  
                        truncated_label = full_display[:15]  

                        node['label'] = truncated_label 
                        node['title'] = full_display
                        node['text'] = full_display 
                    else:
                        node['label'] = 'No Label' 
                        node['title'] = 'No Description Available'  

            elif level == 4: 
                
                resource_type = node['id']  
                resource_type_result = get_resource_type(resource_type)
                color = get_color_for_resource_type(resource_type_result)

                level_4_nodes_by_type.setdefault(resource_type_result, []).append(node['id'])

                if 'show' in show_labels:
                    display_label = flat_df.loc[flat_df['Codes'] == node['id'], 'Full_Displays'].values
                    if len(display_label) > 0 and display_label[0] is not None:
                        full_display = display_label[0]
                        node['label'] = full_display[:22] 
                        node['title'] = full_display
                        node['text'] = full_display
                    else:
                        node['label'] = 'No Label'
                        node['title'] = 'No Description Available'
                node['color'] = color 
                
            else:
                node['color'] = 'gray'  

            node['color'] = color 
            node_shape = shape_mapping.get(level, 'dot')  
            node['shape'] = node_shape  
            node['font'] = {'size': 20}
        
            
#### 7.2.11.a.11 Highlight User Selection:

        if user_code:
            for node in fhir_net.nodes:
                if node['id'] == user_code:
                    node['color'] = 'red'  
                    node['size'] += 5  


            for edge in fhir_net.edges:
                if edge['from'] == user_code or edge['to'] == user_code:
                    edge['color'] = 'lime'  
                    edge['width'] += 5  
                    
#### 7.2.11.a.12 Graph Visualization:                    

        fhir_net.show('fhir_interactions_highlighted.html')

        graph_style = {'display': 'block', 'width': '200%', 'height': '750px'}
        try:
            with open('fhir_interactions_highlighted.html', 'r') as file:
                html_content = file.read()
            return html_content, {'codes_of_interest': codes_of_interest, 'top_neighbor_info': top_neighbor_info}, graph_style, bar_chart_style, dendrogram_style
        except Exception as e:
            print(f"Error reading HTML file: {e}")
            return "", {'codes_of_interest': [], 'top_neighbor_info': {}}, graph_style, bar_chart_style, dendrogram_style


#################################################### IF an individual code  ##################################################
    
    else:
        
#### 7.2.11.b.1 Node Size and Style Initialization: 

        NODE_SIZE_MIN = 4
        NODE_SIZE_MAX = 44
        
        
        graph_style = {'display': 'block', 'width': '100%', 'height': '600px'}
        bar_chart_style = {'display': 'block', 'width': '95%', 'height': '300px'}
        dendrogram_style = {'display': 'block', 'width': '95%', 'height': '300px'}

#### 7.2.11.b.2 Node Degree Calculation:  

        node_degree = main_df.astype(bool).sum(axis=1)
    
#### 7.2.11.b.3 Top Nodes Selection:  
        
        top_10_degrees = node_degree.sort_values(ascending=False)
        
#### 7.2.11.b.4 Defining the weight range to rescale the node size and edge thickness:  

        min_weight = top_10_degrees.min()
        max_weight = top_10_degrees.max()
        
#### 7.2.11.b.5 Neighbor Retrieval:  

        if selected_code not in main_df.index:
            return "", {'codes_of_interest': [], 'top_neighbor_info': {}}, graph_style, bar_chart_style, dendrogram_style

        neighbors_sorted = main_df.loc[selected_code].sort_values(ascending=False)
        top_neighbors = list(neighbors_sorted.index[:])

        codes_of_interest = [selected_code]
        top_neighbor_info = {}

#### 7.2.11.b.6 Nodes and Edges Addition:  

        def add_nodes_edges(graph, child_df, group_name):
            top_neighbor = None

            for neighbor_code in neighbors_sorted.index:
                if group_name == 'ICD' and is_icd_code(neighbor_code):
                    top_neighbor = neighbor_code
                    break
                elif group_name == 'LOINC' and is_loinc_code(neighbor_code):
                    top_neighbor = neighbor_code
                    break
                elif group_name == 'OPS' and is_ops_code(neighbor_code):
                    top_neighbor = neighbor_code
                    break

            if top_neighbor:
                top_neighbor_info['top_neighbor'] = top_neighbor
                top_neighbor_row = child_df.loc[top_neighbor].sort_values(ascending=False)
                top_neighbors_list = list(top_neighbor_row.index[:num_nodes_to_visualize])
                top_neighbor_info['top_neighbors_list'] = top_neighbors_list

                codes_of_interest.extend([top_neighbor] + top_neighbors_list)

                if 'show' in show_labels:
                    selected_code_label = flat_df.loc[flat_df['Codes'] == selected_code, 'Displays'].iloc[0] if not flat_df.empty else selected_code
                    top_neighbor_label = flat_df.loc[flat_df['Codes'] == top_neighbor, 'Displays'].iloc[0] if not flat_df.empty else top_neighbor
                else:
                    selected_code_label = selected_code
                    top_neighbor_label = top_neighbor

                group_name1 = 'ICD' if selected_code in co_occurrence_matrices.get('ICD', {}) else \
                              'LOINC' if selected_code in co_occurrence_matrices.get('LOINC', {}) else \
                              'OPS' if selected_code in co_occurrence_matrices.get('OPS', {}) else 'Unknown'               

                node_size = int(node_degree.get(selected_code, 1))
                if max_weight == min_weight:
                    node_size = normalize_weights(
                        node_size,
                        gain=3,  
                        offset=NODE_SIZE_MIN,
                        min_limit=NODE_SIZE_MIN,
                        max_limit=NODE_SIZE_MAX
                    )
                else:
                    node_size = normalize_weights(
                        node_size,
                        gain=(NODE_SIZE_MAX - NODE_SIZE_MIN) / (max_weight - min_weight),
                        offset=NODE_SIZE_MIN,
                        min_limit=NODE_SIZE_MIN,
                        max_limit=NODE_SIZE_MAX
                    )

                if selected_code not in net.get_nodes():
                    net.add_node(selected_code, size=node_size, title=flat_df.loc[flat_df['Codes'] == selected_code, 'Full_Displays'].iloc[0], label=selected_code_label, color=SUBGROUP_COLORS.get(group_name1, 'gray'))

                node_size = int(node_degree.get(top_neighbor, 1))

                if max_weight == min_weight:
                    node_size = normalize_weights(
                        node_size,
                        gain=3,  
                        offset=NODE_SIZE_MIN,
                        min_limit=NODE_SIZE_MIN,
                        max_limit=NODE_SIZE_MAX
                    )
                else:
                    node_size = normalize_weights(
                        node_size,
                        gain=(NODE_SIZE_MAX - NODE_SIZE_MIN) / (max_weight - min_weight),
                        offset=NODE_SIZE_MIN,
                        min_limit=NODE_SIZE_MIN,
                        max_limit=NODE_SIZE_MAX
                    )

                if top_neighbor not in net.get_nodes():
                    net.add_node(top_neighbor, size=node_size, title=flat_df.loc[flat_df['Codes'] == top_neighbor, 'Full_Displays'].iloc[0], label=top_neighbor_label, color=SUBGROUP_COLORS.get(group_name, 'gray'))


                if selected_code in net.get_nodes() and top_neighbor in net.get_nodes() and selected_code != top_neighbor:
                    edge_value = int(main_df.loc[selected_code, top_neighbor])

                    edge_value = normalize_weights(edge_value, gain=5, offset=1, 
                              min_limit=EDGE_THICKNESS_MIN, max_limit=EDGE_THICKNESS_MAX)

                    net.add_edge(selected_code, top_neighbor, value=edge_value, color=SUBGROUP_COLORS.get(group_name, 'gray'))

                top_neighbor_row = child_df.loc[top_neighbor].sort_values(ascending=False)
                top_neighbors_list = list(top_neighbor_row.index[:num_nodes_to_visualize])

                for neighbor in top_neighbors_list:
                    if neighbor != top_neighbor and child_df.loc[top_neighbor, neighbor] > 0:
                        neighbor_label = flat_df.loc[flat_df['Codes'] == neighbor, 'Displays'].iloc[0] if 'show' in show_labels else neighbor

                        node_size = int(node_degree.get(neighbor, 1))

                        if max_weight == min_weight:
                            node_size = normalize_weights(
                                node_size,
                                gain=3,  
                                offset=NODE_SIZE_MIN,
                                min_limit=NODE_SIZE_MIN,
                                max_limit=NODE_SIZE_MAX
                            )
                        else:
                            node_size = normalize_weights(
                                node_size,
                                gain=(NODE_SIZE_MAX - NODE_SIZE_MIN) / (max_weight - min_weight),
                                offset=NODE_SIZE_MIN,
                                min_limit=NODE_SIZE_MIN,
                                max_limit=NODE_SIZE_MAX
                            )

                        if neighbor not in net.get_nodes():
                            net.add_node(neighbor, size=node_size, title=flat_df.loc[flat_df['Codes'] == neighbor, 'Full_Displays'].iloc[0], label=neighbor_label, color=SUBGROUP_COLORS.get(group_name, 'gray'))

                        if top_neighbor in net.get_nodes() and neighbor in net.get_nodes() and top_neighbor != neighbor:
                            edge_value = int(child_df.loc[top_neighbor, neighbor])

                            edge_value = normalize_weights(edge_value, gain=5, offset=1, 
                              min_limit=EDGE_THICKNESS_MIN, max_limit=EDGE_THICKNESS_MAX)
                            net.add_edge(top_neighbor, neighbor, value=edge_value)

                for i in range(len(top_neighbors_list)):
                    for j in range(i + 1, len(top_neighbors_list)):
                        neighbor1 = top_neighbors_list[i]
                        neighbor2 = top_neighbors_list[j]

                        if neighbor1 in child_df.index and neighbor2 in child_df.columns:
                            count = child_df.loc[neighbor1, neighbor2]
                            if count > 0:

                                if neighbor1 in net.get_nodes() and neighbor2 in net.get_nodes() and neighbor1 != neighbor2:
                                    net.add_edge(neighbor1, neighbor2, value=int(count) / 2, color=SUBGROUP_COLORS.get(group_name, 'gray'))


#### 7.2.11.b.7 ResourceType dependant Co-Occurrence Matrix Processing:  

        if 'ICD' in co_occurrence_matrices:
            icd_matrix = pd.DataFrame(co_occurrence_matrices['ICD'])
            add_nodes_edges(net, icd_matrix, 'ICD')

        if 'LOINC' in co_occurrence_matrices:
            loinc_matrix = pd.DataFrame(co_occurrence_matrices['LOINC'])
            add_nodes_edges(net, loinc_matrix, 'LOINC')

        if 'OPS' in co_occurrence_matrices:
            ops_matrix = pd.DataFrame(co_occurrence_matrices['OPS'])
            add_nodes_edges(net, ops_matrix, 'OPS')
            
#### 7.2.11.b.8 Temporary File Generation:  

        temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.html')
        temp_file_name = temp_file.name
        temp_file.close()

        net.show(temp_file_name)
        
        return open(temp_file_name, 'r').read(), {'codes_of_interest': codes_of_interest, 'top_neighbor_info': top_neighbor_info}, graph_style, bar_chart_style, dendrogram_style




# #### 7.2.12  Dash callback: `update_charts`
# 
# The code defines a Dash callback function named `update_charts`, which updates the figures of a bar chart and a dendrogram based on user interactions in the web application. The callback responds to changes in dropdown selections, sliders, and data stored in the application.
# 
# #### Inputs
# 
# - **code-dropdown**:  
#   A dropdown that allows users to select a specific code. If the value is `None` or `'ALL_CODES'`, the charts will indicate that they are not available.
# 
# - **show-labels**:  
#   A toggle that specifies whether to display labels on the charts.
# 
# - **num-nodes-slider**:  
#   A slider that determines the number of nodes to visualize in the dendrogram.
# 
# - **codes-of-interest-store**:  
#   A component that holds data regarding codes of interest, fetched from the application's storage.
# 
# - **data-store**:  
#   A state component that contains the underlying data needed for generating the charts.
# 
# #### Process
# 
# #### 7.2.12.a Initial Validation:  
#    The function first checks if a code has been selected. If not, it returns empty charts with messages indicating their unavailability.
# 
# #### 7.2.12.b Data Retrieval:  
#    Co-occurrence matrices and a flat DataFrame (`flat_df`) are retrieved from the `data` state. The function also determines how many neighbors to display based on the slider's value.
# 
# #### 7.2.12.c Frequency Distribution Calculation:  
#    The function calculates the frequency distribution of codes from the main DataFrame (`main_df`), which is derived from the co-occurrence matrices. This distribution is normalized to represent the proportion of each code.
# 
# #### 7.2.12.d Selected Code Labeling:  
#    It retrieves the label for the selected code, which will be displayed on the charts. If labels are not to be shown, it uses the selected code itself.
# 
# #### 7.2.12.e Codes of Interest Handling:  
#    The function ensures that `codes_of_interest` is treated as a list. 
# 
# #### 7.2.12.f Bar Chart Data Preparation:  
#    A loop iterates through the `codes_of_interest`, computing occurrence counts for each neighbor and preparing data for the bar chart. Colors and line widths are determined based on the neighbor's type and whether it is the selected code.
# 
# #### 7.2.12.g Bar Chart Sorting and and Droping Duplicates:  
#    The bar data is sorted by code, and duplicates are removed while maintaining corresponding y-values and colors. Unique labels, values, colors, and line widths are collected.
# 
# #### 7.2.12.h Bar Chart Creation:  
#    The function constructs the bar chart figure, setting the x and y data, title, axis labels, and other properties.
# 
# #### 7.2.12.i Dendrogram Creation:  
#    - The function attempts to create a dendrogram. It first checks if there are enough codes of interest to perform clustering. If the conditions are met, it creates a sub-co-occurrence matrix and applies Agglomerative Clustering. 
# 
#         #### Helper Function `create_sub_cooccurrence_matrix` 
# 
#         #### Overview
# 
#         The `create_sub_cooccurrence_matrix` function is a utility function that constructs a subset of the co-occurrence matrix based on a specified list of codes. This function is designed to generate a matrix that contains only the selected codes, allowing for a more focused analysis of their relationships, such as clustering or hierarchical analysis. If no valid codes are found in the provided list, the function raises an error.
# 
#         #### Input
# 
#         - **`cooccurrence_dict`**:  
#           A dictionary representing the main co-occurrence data, where each key is a code, and its corresponding value is another dictionary of co-occurring codes with their frequencies.
# 
#         - **`codes`**:  
#           A list of codes for which a sub-co-occurrence matrix is desired. The function will include only these specified codes, if they are found in `cooccurrence_dict`.
# 
#         #### Process
# 
#         #### Filter Valid Codes:
# 
#         The function first identifies codes from the input list that exist in `cooccurrence_dict`. These are considered valid codes for the sub-matrix. If no valid codes are found, the function raises a `ValueError` with a message indicating that no valid codes are available.
# 
#         #### Construct Sub-Matrix:
# 
#         Using the `valid_codes`, the function builds a DataFrame called `sub_matrix`. This matrix includes:
#         - **Rows and Columns**: Each row and column represents one of the valid codes, so the matrix is square.
#         - **Values**: The values within the matrix represent the frequency of co-occurrences between each pair of valid codes, as found in `cooccurrence_dict`. If no co-occurrence frequency is available for a pair of codes, the function defaults that value to zero.
# 
#         ####  Fill Missing Values:
# 
#         After constructing the matrix, the function uses `.fillna(0)` to ensure that any missing values are replaced with zero. This step guarantees that all cell values in the `sub_matrix` are numerical and makes the matrix suitable for further processing.
# 
#         #### Output
# 
#         The function returns `sub_matrix`, a pandas DataFrame containing the co-occurrence frequencies for the specified codes. This output matrix can be used for various analytical tasks, such as clustering and visualization in a dendrogram.
# 
# 
# 
# #### Outputs
# 
# The function returns two outputs:
# 
# - **bar-chart**:  
#   A figure representing the frequency distribution of the selected codes of interest.
# 
# - **dendrogram**:  
#   A figure representing the hierarchical clustering of the selected codes based on co-occurrence data. If an error occurs, it returns an error message instead.
# 

# In[13]:


@app.callback(
    [Output('bar-chart', 'figure'),
     Output('dendrogram', 'figure')],
    [Input('code-dropdown', 'value'),
     Input('show-labels', 'value'),
     Input('num-nodes-slider', 'value'),
     Input('codes-of-interest-store', 'data')],  # Corrected input to fetch 'codes_of_interest'
    State('data-store', 'data')
)



def update_charts(selected_code, show_labels, slider_value, codes_of_interest, data):
    
#### 7.2.12.a Initial Validation:  

    if not selected_code or selected_code == 'ALL_CODES':
        return (
            {
                'data': [],
                'layout': {'title': 'Bar chart not available'}
            },
            {
                'data': [],
                'layout': {'title': 'Dendrogram not available'}
            }
        )
    
#### 7.2.12.b Data Retrieval:  

    co_occurrence_matrices = data.get('co_occurrence_matrices', {})
    flat_df = pd.DataFrame(data.get('flat_df', {}))
    num_neighbors_to_display = slider_value or 0
    
#### 7.2.12.c Frequency Distribution Calculation:  

    main_df = pd.DataFrame(co_occurrence_matrices.get('Main', {}))
    frequency_distribution = main_df.sum(axis=1)
    total_sum = frequency_distribution.sum()
    total_freq_dist = frequency_distribution / total_sum
    
#### 7.2.12.d Selected Code Labeling: 

    selected_code_label = flat_df.loc[flat_df['Codes'] == selected_code, 'Displays'].iloc[0] if 'show' in show_labels else selected_code

#### 7.2.12.e Codes of Interest Handling: 

    codes_of_interest = codes_of_interest.get('codes_of_interest', [])

#### 7.2.12.f Bar Chart Data Preparation:

    bar_data = []
    x_labels = []
    y_values = []
    line_widths = []
    bar_colors = []

    for neighbor in codes_of_interest:
        occurrence_count = total_freq_dist.get(neighbor, 0)
        neighbor_label = flat_df.loc[flat_df['Codes'] == neighbor, 'Displays'].iloc[0] if 'show' in show_labels else neighbor
        bar_data.append({'x': neighbor_label, 'y': occurrence_count, 'code': neighbor})
        x_labels.append(neighbor_label)
        y_values.append(occurrence_count)
        line_widths.append(5 if neighbor == selected_code else 1)
        color = 'gray'
        for subgroup, color_code in SUBGROUP_COLORS.items():
            if neighbor in co_occurrence_matrices.get(subgroup, {}):
                color = color_code
                break
        bar_colors.append(color)

#### 7.2.12.g Bar Chart Sorting and and Droping Duplicates: 

    bar_data_sorted = sorted(bar_data, key=lambda x: x['code'])
    sorted_x = [item['x'] for item in bar_data_sorted]
    sorted_y = [item['y'] for item in bar_data_sorted]
    sorted_line_widths = [line_widths[x_labels.index(item['x'])] for item in bar_data_sorted]
    sorted_colors = [bar_colors[x_labels.index(item['x'])] for item in bar_data_sorted]

    unique_labels = []
    unique_y_values = []
    unique_colors = []
    unique_line_widths = []

    for x, y, color, line_width in zip(sorted_x, sorted_y, sorted_colors, sorted_line_widths):
        if x not in unique_labels:
            unique_labels.append(x)
            unique_y_values.append(y)
            unique_colors.append(color)
            unique_line_widths.append(line_width)
    

#### 7.2.12.h Bar Chart Creation:  

    bar_chart_figure = {
        'data': [{
            'x': unique_labels if 'show' in show_labels else str(unique_labels),  # Conditional for 'x'
            'y': unique_y_values,
            'type': 'bar',
            'name': 'Occurrences',
            'marker': {'color': unique_colors},
            'line': {'width': unique_line_widths},
            'text': unique_labels if 'show' in show_labels else [flat_df.loc[flat_df['Codes'] == label, 'Codes'].iloc[0] for label in unique_labels],#unique_labels,
            'textposition': 'auto'#'none' if 'show' in show_labels else 'auto'
        }],
        'layout': {
            'title': f'Frequency Distribution',
            'xaxis': {
                'title': '',
                'tickangle': -45,  # Rotate x-tick labels for better readability
                'showticklabels': True,  # Show only the labels, no numbers
            },
            'yaxis': {'title': 'Frequency'}
        }
    }


#### 7.2.12.i Dendrogram Creation:

    try:
        if len(codes_of_interest) < 1:
            raise ValueError("Not enough codes for clustering")

        def create_sub_cooccurrence_matrix(cooccurrence_dict, codes):
            valid_codes = [code for code in codes if code in cooccurrence_dict]
            if not valid_codes:
                raise ValueError("No valid codes found for sub-co-occurrence matrix")
            sub_matrix = pd.DataFrame(
                {code: {sub_code: cooccurrence_dict.get(code, {}).get(sub_code, 0) for sub_code in valid_codes} for code in valid_codes}
            ).fillna(0)
            return sub_matrix

        co_dict = co_occurrence_matrices.get('Main', {})
        cooccurrence_dict = create_sub_cooccurrence_matrix(co_dict, codes_of_interest)
        
        if cooccurrence_dict.shape[0] < 2:
            raise ValueError("Sub-co-occurrence matrix does not have enough samples for clustering")

        cooccurrence_matrix = cooccurrence_dict.dot(cooccurrence_dict.T).fillna(0)
        cooccurrence_array = cooccurrence_matrix.values

        clustering = AgglomerativeClustering(n_clusters=1, metric='euclidean', linkage='ward')
        cluster_labels = clustering.fit_predict(cooccurrence_array)
        cooccurrence_matrix['Cluster'] = cluster_labels

        dendrogram_figure = create_dendrogram_plot(cooccurrence_array, cooccurrence_matrix.index.tolist(), flat_df, show_labels)

        return bar_chart_figure, dendrogram_figure
 
    except Exception as e:
        return bar_chart_figure, {'data': [], 'layout': {'title': 'Error generating dendrogram'}}
    
    
if __name__ == '__main__':
    app.run_server(debug=True, port=8052)



# In[ ]:




