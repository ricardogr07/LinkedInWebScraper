import pandas as pd
import re
from datetime import datetime, timedelta

from Utils.constants import LOCATION_MAPPING, TECH_STACK_CATEGORIES

class JobDataCleaner:
    def __init__(self, logger):
        self.logger = logger

    def clean_jobs_dataframe(self, df, location_mapping) ->pd.DataFrame:
        """Main method to clean and preprocess the job DataFrame."""
        self.logger.log.info("Starting data cleaning process.")

        if location_mapping != None:
            df = self.process_location_data(df)

        df = self.process_urls_and_job_ids(df)

        df = self.filter_valid_job_ids(df)

        df = self.remove_duplicate_job_ids(df)

        df = self.remove_duplicates_by_columns(df)

        self.logger.log.info("Data cleaning process completed.")
        return df

    def process_location_data(self, df):
        """Clean the Location column and apply location-specific transformations."""
        self.logger.log.info(f"Initial unique locations: {df['Location'].nunique()}")

        df['Location'] = df['Location'].apply(lambda x: x.split(',')[0])

        unmatched_locations = df[~df['Location'].isin(LOCATION_MAPPING.keys())]['Location'].unique()
        self.logger.log.info(f"Unique 'Other' locations before mapping: {unmatched_locations}")

        df['Location'] = df['Location'].apply(lambda loc: LOCATION_MAPPING.get(loc, 'Other'))

        other_count = df[df['Location'] == 'Other'].shape[0]
        self.logger.log.info(f"Found {other_count} 'Other' locations. Dropping them.")

        df = df[df['Location'] != 'Other']

        # Convert Location column to a categorical datatype
        df['Location'] = df['Location'].astype('category')

        self.logger.log.info(f"Locations after renaming and dropping 'Other': {df['Location'].nunique()} unique values.")
        return df

    def process_urls_and_job_ids(self, df):
        """Truncate URLs and extract JobIDs from the URLs."""
        self.logger.log.info("Processing URLs and extracting JobIDs.")

        df['Url'] = df['Url'].apply(lambda url: url.split('?position')[0])

        df['JobID'] = df['Url'].apply(lambda url: url[-10:])

        return df

    def filter_valid_job_ids(self, df):
        """Remove rows with invalid JobIDs (not 10 digits)."""
        original_count = df.shape[0]

        df = df[df['JobID'].notna()]
        df = df[df['JobID'].apply(lambda x: re.fullmatch(r'\d{10}', str(x)) is not None)]

        filtered_count = df.shape[0]
        removed_count = original_count - filtered_count
        self.logger.log.info(f"Removed {removed_count} rows with invalid JobIDs. {filtered_count} records remaining.")

        return df

    def remove_duplicate_job_ids(self, df):
        """Find and remove duplicate JobIDs."""
        duplicate_count = df['JobID'].duplicated().sum()

        if duplicate_count > 0:
            self.logger.log.info(f"Found {duplicate_count} duplicate JobIDs. Removing duplicates.")
            df = df.drop_duplicates(subset='JobID', keep='first').reset_index(drop=True)
        else:
            self.logger.log.info("No duplicate JobIDs found.")

        return df

    def remove_duplicates_by_columns(self, df):
        """Remove duplicates based on Location, Title, and Company."""
        original_count = df.shape[0]
        df = df.drop_duplicates(subset=['Location', 'Title', 'Company']).reset_index(drop=True)
        removed_count = original_count - df.shape[0]
        self.logger.log.info(f"Removed {removed_count} duplicate rows based on Location, Title, and Company.")

        return df

    def clean_extracted_job_data(self, df_jobs):
        """Master function to clean and process extracted enriched job data."""
        df_jobs = self.clean_num_applicants(df_jobs)
        df_jobs = self.clean_seniority_level(df_jobs)
        df_jobs = self.standardize_employment_type(df_jobs)
        df_jobs = self.standardize_job_function(df_jobs)
        df_jobs = self.split_job_functions(df_jobs)
        df_jobs = self.convert_posted_time(df_jobs)
        df_jobs = self.reorder_columns(df_jobs)
        return df_jobs

    def clean_num_applicants(self, df_jobs):
        """Clean and standardize the number of applicants."""

        def extract_num_applicants(text):
            match = re.search(r'\d+', text)
            if match:
                return int(match.group())
            elif "Be among the first 25" in text:
                return 25
            elif "Over 200 applicants" in text:
                return 200
            return 'N/A'

        self.logger.log.info("Cleaning the 'NumApplicants' column.")
        df_jobs['NumApplicants'] = df_jobs['NumApplicants'].apply(extract_num_applicants)
        return df_jobs

    def clean_seniority_level(self, df_jobs):
        """Clean up the 'SeniorityLevel' column."""
        self.logger.log.info("Cleaning the 'SeniorityLevel' column.")
        df_jobs['SeniorityLevel'] = df_jobs['SeniorityLevel'].apply(
            lambda x: 'N/A' if 'Not Applicable' in x else x
        )
        seniority_categories = ['Entry level', 'Mid-Senior level', 'Executive', 'N/A', 'Associate', 'Internship']
        df_jobs['SeniorityLevel'] = pd.Categorical(df_jobs['SeniorityLevel'], categories=seniority_categories)
        return df_jobs

    def standardize_employment_type(self, df_jobs):
        """Standardize 'EmploymentType' as a categorical variable."""
        self.logger.log.info("Standardizing 'EmploymentType' as a categorical variable.")
        df_jobs['EmploymentType'] = pd.Categorical(df_jobs['EmploymentType'], categories=df_jobs['EmploymentType'].unique())
        return df_jobs

    def standardize_job_function(self, df_jobs):
        """Standardize the 'JobFunction' column."""

        def standardize_job_function(text):
            if ' and ' in text:
                text = text.replace(' and ', ', ')
            job_functions = text.split(', ')
            if len(job_functions) > 3:
                job_functions = job_functions[:3]
            return ', '.join(job_functions)

        self.logger.log.info("Standardizing the 'JobFunction' column.")
        df_jobs['JobFunction'] = df_jobs['JobFunction'].replace({
        'Research and Design': 'R&D',
        'Design and Product Management': 'Product Management'
        }, regex=False)

        df_jobs['JobFunction'] = df_jobs['JobFunction'].apply(standardize_job_function)
        return df_jobs

    def split_job_functions(self, df_jobs):
        """Split 'JobFunction' into three separate columns."""

        def split_job_functions(text):
            job_functions = text.split(', ')
            job_function_1 = job_functions[0] if len(job_functions) > 0 else None
            job_function_2 = job_functions[1] if len(job_functions) > 1 else None
            job_function_3 = job_functions[2] if len(job_functions) > 2 else None
            return pd.Series([job_function_1, job_function_2, job_function_3])

        self.logger.log.info("Splitting 'JobFunction' into three separate columns.")
        df_jobs[['JobFunction1', 'JobFunction2', 'JobFunction3']] = df_jobs['JobFunction'].apply(split_job_functions)

        # Fill any None values with 'N/A'
        df_jobs['JobFunction1'] = df_jobs['JobFunction1'].fillna('N/A')
        df_jobs['JobFunction2'] = df_jobs['JobFunction2'].fillna('N/A')
        df_jobs['JobFunction3'] = df_jobs['JobFunction3'].fillna('N/A')

        # Extract unique job function categories
        job_function_categories = list(set(
            df_jobs['JobFunction1'].unique().tolist() +
            df_jobs['JobFunction2'].unique().tolist() +
            df_jobs['JobFunction3'].unique().tolist()
        ))

        # Convert the new columns to categorical data types
        df_jobs['JobFunction1'] = pd.Categorical(df_jobs['JobFunction1'], categories=job_function_categories)
        df_jobs['JobFunction2'] = pd.Categorical(df_jobs['JobFunction2'], categories=job_function_categories)
        df_jobs['JobFunction3'] = pd.Categorical(df_jobs['JobFunction3'], categories=job_function_categories)

        # Drop the original 'JobFunction' column since it's no longer needed
        df_jobs.drop(columns=['JobFunction'], inplace=True)
        return df_jobs

    def convert_posted_time(self, df_jobs):
        """Convert 'PostedTime' into days since the job was posted."""

        def convert_posted_time(text):
            today = datetime.today()

            if 'hour' in text:
                return today
            if 'day' in text:
                days = int(re.search(r'\d+', text).group()) if re.search(r'\d+', text) else 1
                return today - timedelta(days=days)
            if 'week' in text:
                weeks = int(re.search(r'\d+', text).group()) if re.search(r'\d+', text) else 1
                return today - timedelta(days=weeks * 7)
            if 'month' in text:
                months = int(re.search(r'\d+', text).group()) if re.search(r'\d+', text) else 1
                return today - timedelta(days=months * 30)
            return 'N/A'

        self.logger.log.info("Converting 'PostedTime' to DatePosted.")
        df_jobs['PostedTime'] = df_jobs['PostedTime'].apply(convert_posted_time)
        df_jobs.rename(columns={'PostedTime': 'DatePosted'}, inplace=True)
        return df_jobs

    def reorder_columns(self, df_jobs):
        """Reorder the columns in the DataFrame for better organization."""
        self.logger.log.info("Reordering the columns in the DataFrame.")
        new_column_order = [
            'Title', 'Company', 'Location', 'Remote',
            'SeniorityLevel', 'EmploymentType', 'Industries', 
            'DatePosted', 'NumApplicants', 
            'JobFunction1', 'JobFunction2', 'JobFunction3', 
            'Description', 'Url', 'JobID'
        ]
        df_jobs = df_jobs[new_column_order]
        return df_jobs

    def process_enriched_job_data(self, df_jobs:pd.DataFrame, tech_stack_categories:list = None):
        """
        Master function to process job data:
        - Extract minimum years of experience (MinYoE)
        - Categorize study level (MinLevelStudies)
        - Categorize tech stack based on predefined categories

        Args:
            df_jobs (pd.DataFrame): DataFrame containing job information.
            tech_stack_categories (dict): Dictionary of tech stack categories.

        Returns:
            pd.DataFrame: DataFrame with processed job data.
        """

        self.logger.log.info("Starting job data processing.")
        

        df_jobs = self.extract_min_years(df_jobs)
        
        df_jobs = self.categorize_studies(df_jobs)
        
        if tech_stack_categories != None:
            df_jobs = self.categorize_tech_stack(df_jobs, tech_stack_categories)
        
        self.logger.log.info("Completed job data processing.")
        
        return df_jobs

    def extract_min_years(self, df_jobs):
        """Extract the minimum number of years from the YoE (Years of Experience) string and add it as a column."""

        def extract_min_years_from_str(experience_str):
            # Ensure experience_str is a string
            experience_str = str(experience_str)
            
            # Handle 'N/A' and non-numeric cases
            if 'N/A' in experience_str or 'Professional software development experience required' in experience_str:
                return 'N/A'
            
            # Find all numeric values in the string
            numbers = re.findall(r'\d+', experience_str)
            
            # If no numbers found, return 'N/A'
            if not numbers:
                return 'N/A'
            
            # Convert found numbers to integers and return the minimum
            return min(map(int, numbers))

        # Apply the function to the 'YoE' column and create a new 'MinYoE' column
        df_jobs['MinYoE'] = df_jobs['YoE'].apply(extract_min_years_from_str)

        return df_jobs

    def categorize_studies(self, df_jobs):
        """Categorize the minimum level of studies from the given string and add it as a column."""

        def categorize_study_level(level):
            level = level.lower()
            if any(keyword in level for keyword in ["student", "undergraduate"]):
                return "Undergraduate Student"
            elif any(keyword in level for keyword in ["bachelor", "bs", "b.sc", "bachelor's"]):
                return "Bachelor"
            elif any(keyword in level for keyword in ["master", "ms", "m.sc", "master's"]):
                return "Masters"
            elif "phd" in level:
                return "PhD"
            else:
                return "N/A"

        # Apply the function to the 'MinLevelStudies' column and update it with categorized values
        df_jobs['MinLevelStudies'] = df_jobs['MinLevelStudies'].apply(categorize_study_level)

        return df_jobs

    def categorize_tech_stack(self, df_jobs, tech_stack_categories):
        """Categorize the tech stack into predefined categories and add them as columns."""
        
        # Initialize columns with 0s
        for category in tech_stack_categories:
            df_jobs[category] = 0

        # Add 'Other' category
        df_jobs['Other'] = 0

        # Function to categorize tech stack for each row
        def categorize_single_tech_stack(tech_stack, index):
            tech_stack_elements = [element.strip() for element in tech_stack.split(',')]
            category_found = False

            for category, items in tech_stack_categories.items():
                for item in items:
                    if any(item in element for element in tech_stack_elements):
                        df_jobs.at[index, category] = 1
                        category_found = True
            
            if not category_found:
                df_jobs.at[index, 'Other'] = 1

        # Apply categorization to each row
        for index, row in df_jobs.iterrows():
            categorize_single_tech_stack(row['TechStack'], index)

        return df_jobs
