TIME_POSTED_OPTION = {
    'ALL': '',
    'MONTH': 'r2592000',
    'WEEK': 'r604800',
    'DAY': 'r86400'
}

REMOTE_OPTION = {
    'ALL': '',
    'ON-SITE': '1',
    'REMOTE': '2',
    'HYBRID': '3'
}

USER_AGENT_HEADERS = [
    {'User-Agent': 'Mozilla/5.0'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'}
]

LOCATION_MAPPING= {
            'San Pedro Garza García': 'Monterrey Metropolitan Area',
            'Centro de San Pedro Garza García': 'Monterrey Metropolitan Area',
            'Monterrey': 'Monterrey Metropolitan Area',
            'Monterrey Metropolitan Area': 'Monterrey Metropolitan Area',
            'Monterrey metropolitan area': 'Monterrey Metropolitan Area',
            'San Nicolás de los Garza': 'Monterrey Metropolitan Area',
            'San Nicolás de Los Garza': 'Monterrey Metropolitan Area',
            'Garza García': 'Monterrey Metropolitan Area',
            'Santa Catarina': 'Monterrey Metropolitan Area',
            'Guadalupe': 'Monterrey Metropolitan Area',
            'Villa de García': 'Monterrey Metropolitan Area',
            'Guadalajara': 'Guadalajara',
            'Zapopan' : 'Guadalajara',
            'Tlaquepaque' : 'Guadalajara', 
            'Mexico City Metropolitan Area': 'Mexico City Metropolitan Area',
            'Mexico City': 'Mexico City Metropolitan Area',
            'Naucalpan de Juárez': 'Mexico City Metropolitan Area',
            'Gustavo A. Madero': 'Mexico City Metropolitan Area', 
            'Mexico': 'Mexico City Metropolitan Area', 
            'Cuauhtémoc': 'Mexico City Metropolitan Area', 
            'Miguel Hidalgo': 'Mexico City Metropolitan Area', 
            'Álvaro Obregón': 'Mexico City Metropolitan Area', 
            'Ciudad Nezahualcóyotl': 'Mexico City Metropolitan Area', 
            'Benito Juárez': 'Mexico City Metropolitan Area', 
            'Azcapotzalco': 'Mexico City Metropolitan Area', 
            'Tlalnepantla': 'Mexico City Metropolitan Area', 
            'Coyoacán': 'Mexico City Metropolitan Area', 
            'Colonia México': 'Mexico City Metropolitan Area',         
        }

DATA_SCIENCE_KEYWORDS = [
                    'data', 'machine learning', 'ml', 'ai', 'artificial intelligence',
                    'analytics', 'business intelligence', 'bi', 'data science', 'scientist',
                    'statistical', 'statistics', 'nlp', 'deep learning', 'computer vision',
                    'analysis', 'power bi'
                ]

TECH_STACK_CATEGORIES = {
    'Agile Methodologies': [
        'Scrum', 'SAFe', 'Agile', 'Agile SDLC', 'Kanban', 'Agile'
    ],
    'Back-End Development': [
        'Node.js', 'ASP.NET', 'Spring Boot', 'Django', 'Flask', 'Ruby on Rails', 
        '.NET Core', 'FastAPI', 'Golang', 'C#'
    ],
    'Big Data Tools': [
        'Hadoop', 'Spark', 'Hive', 'Databricks', 'Airflow', 'BigQuery', 
        'Teradata', 'ClickHouse', 'AWS Glue', 'Big Data', 'Big Data Stack', 
        'SnapLogic', 'DataDog', 'Alteryx', 'Talend ETL'
    ],
    'Cloud Platforms': [
        'AWS', 'Azure', 'GCP', 'Google Cloud Platform (GCP)', 
        'Cloud Computing', 'Microsoft Azure', 'AWS Redshift', 
        'AWS S3', 'Azure SQL Databases', 'Google BigQuery', 'Azure Data Factory',
        'Azure Synapse', 'Azure API App Services', 'Azure Data Bricks', 
        'Azure Data Lake', 'Azure ADLS Gen2', 'AWS Lambda', 'Google Cloud', 
        'Azure Data Lake Storage', 'Amazon Web Services', 'Cloud Infrastructure'
    ],
    'Containerization and Orchestration': [
        'Docker', 'Kubernetes', 'Containerization', 'ECS', 'LXD'
    ],
    'Data Analysis': [
        'Data Analysis', 'Statistical Modeling', 'Statistical Analysis', 
        'Data Analytics', 'Data Mining', 'Data Quality', 'Data Cleansing', 
        'Data Normalization', 'Data Sanitization', 'Statistical Techniques', 
        'Statistical Methods', 'Analytical Tools', 'Data Management', 
        'Data Science', 'Data Science Tools', 'Data Modeling', 'Data Queries', 
        'Data Flows', 'Data Manipulation', 'Data Platforms', 'Data Warehousing', 
        'Data Engineering', 'Data Visualization', 'Data Visualization Tools'
    ],
    'Data Engineering': [
        'Data Engineering', 'Data Warehousing', 'ETL', 'Data Lakes', 
        'Data Flows', 'Data Migrations', 'Data Integration', 'Data Processing', 
        'Data Platforms', 'Data Quality', 'Data Management'
    ],
    'Data Modeling': [
        'Data Modeling', 'Data Architectures', 'Data Structures', 'Data Schema Design', 
        'Database Modeling', 'Conceptual Data Models', 'Logical Data Models', 
        'Physical Data Models'
    ],
    'Data Visualization': [
        'Power BI', 'Tableau', 'Qlik', 'Matplotlib', 'Plotly', 'D3.js', 
        'Excel', 'Looker', 'Apache Superset', 'Data Visualization Tools', 
        'BI Tools', 'Dashboard Development', 'Visualization Tools'
    ],
    'Database Management': [
        'SQL', 'NoSQL', 'MongoDB', 'SQL Server', 'CosmosDB', 'MySQL', 
        'PostgreSQL', 'Oracle', 'SAP HANA', 'SAP ECC', 'SAP S/4HANA', 
        'Non-SQL Databases', 'DB2', 'PL/SQL', 'Cassandra', 'Redis', 'Sybase', 
        'Data Lake', 'Database', 'Database Management', 'Data Warehouses', 
        'Database Schema Design', 'Stored Procedures', 'Data Migrations', 
        'SQL DW', 'PostgresSQL'
    ],
    'Front-End Development': [
        'React', 'Angular', 'Bootstrap', 'Vue.js', 'CSS', 'HTML', 'SwiftUI', 
        'Front End Development'
    ],
    'Infrastructure as Code (IaC) and Automation': [
        'Terraform', 'Ansible', 'Helm', 'OpenStack', 'Infrastructure-as-Code', 
        'ARM Templates', 'Automation', 'Git', 'CI/CD pipelines'
    ],
    'Machine Learning': [
        'Scikit-Learn', 'TensorFlow', 'PyTorch', 'Keras', 'MLFlow', 
        'Spark ML', 'XGBoost', 'LightGBM', 'Feature Engineering', 
        'A/B Testing', 'Machine Learning', 'Algorithms', 'Google AutoML', 
        'Hugging Face', 'Kubeflow', 'SciPy', 'ML Models'
    ],
    'Networking': [
        'WiFi', 'Networking', 'VPC', 'Network Security', 'Cloud Security'
    ],
    'Python': [
        'Python'
    ],
    'Testing and Quality Assurance': [
        'Unit Testing', 'Integration Testing', 'Feature Testing', 'Performance Tuning', 
        'Load Testing', 'Testing Tools', 'SOAP UI', 'Quality Assurance'
    ]
}