CoCo/
│
├── MAIN CODE-GitHub.ipynb                  # Main application file for data  datasets
│   ├── FHIR_dummy_data_.parquet            # Sample FHIR data in Parquet format
│   ├── ICD_Katalog_2023_DWH_export_202406071440.csv  # ICD-10 GM catalog data
│   ├── LOINC_DWH_export_202409230739.csv   # LOINC catalog data
│   └── OPS_Katalog_2023_DWH_export_202409200944.csv  # OPS catalog data
├── requirements.txt                         # List of dependencies required 


#### File Descriptions ###############################################

MAIN CODE-GitHub.ipynb: This is the main Jupyter Notebook containing the code for data analysis. It includes detailed calculations for distances between healthcare entities based on their attributes.

FHIR_dummy_data_.parquet: A sample dataset in Parquet format for testing and demonstration purposes.

ICD_Katalog_2023_DWH_export_202406071440.csv: A CSV file containing the ICD-10 GM catalog data.

LOINC_DWH_export_202409230739.csv: A CSV file containing the LOINC catalog data.

OPS_Katalog_2023_DWH_export_202409200944.csv: A CSV file containing the OPS catalog data.

requirements.txt: A text file that lists all the Python dependencies required to run the Jupyter Notebook successfully. Ensure to install these packages in your Python environment.


#### Getting Started ###############################################

To get started with this repository, follow these steps:

Clone the repository to your local machine:

bash
Code kopieren
git clone https://github.com/pelingenc/CoCo.git
Navigate to the project directory:

bash
Code kopieren
cd CoCo
Install the required dependencies:

bash
Code kopieren
pip install -r requirements.txt
Open the Jupyter Notebook:

bash
Code kopieren
jupyter notebook MAIN CODE-GitHub.ipynb
Run the analysis within the notebook, and explore the datasets!

Contributing
Contributions are welcome! If you would like to contribute to this project, create a pull request with your changes.

