from __future__ import annotations

import re
from datetime import datetime, timedelta

import pandas as pd

from linkedin_web_scraper.config.constants import normalize_location_name
from linkedin_web_scraper.infra.logging import resolve_logger


class JobDataCleaner:
    """Clean and normalize raw LinkedIn job data frames."""

    def __init__(self, logger=None):
        self.logger = resolve_logger(logger, name=__name__)

    def clean_jobs_dataframe(self, df: pd.DataFrame, location_mapping) -> pd.DataFrame:
        """Clean the raw scrape output into a normalized jobs dataframe."""
        self.logger.info("Starting data cleaning process.")

        if location_mapping is not None:
            df = self.process_location_data(df, location_mapping)

        df = self.process_urls_and_job_ids(df)
        if df.empty:
            self.logger.info("No rows remaining after location and URL processing.")
            return df.reset_index(drop=True)

        df = self.filter_valid_job_ids(df)
        if df.empty:
            self.logger.info("No rows remaining after JobID validation.")
            return df.reset_index(drop=True)

        df = self.remove_duplicate_job_ids(df)
        if df.empty:
            self.logger.info("No rows remaining after duplicate JobID removal.")
            return df.reset_index(drop=True)

        df = self.remove_duplicates_by_columns(df)

        self.logger.info("Data cleaning process completed.")
        return df

    def process_location_data(self, df: pd.DataFrame, location_mapping: dict[str, str]) -> pd.DataFrame:
        """Clean the Location column and apply location-specific transformations."""
        self.logger.info("Initial unique locations: %s", df["Location"].nunique())

        normalized_mapping = {
            normalize_location_name(key): value for key, value in location_mapping.items()
        }
        df["Location"] = df["Location"].apply(
            lambda value: normalize_location_name(value.split(",")[0])
        )

        unmatched_locations = df[~df["Location"].isin(normalized_mapping.keys())][
            "Location"
        ].unique()
        self.logger.info("Unique 'Other' locations before mapping: %s", unmatched_locations)

        df["Location"] = df["Location"].apply(lambda loc: normalized_mapping.get(loc, "Other"))

        other_count = df[df["Location"] == "Other"].shape[0]
        self.logger.info("Found %s 'Other' locations. Dropping them.", other_count)

        df = df[df["Location"] != "Other"].copy()
        df["Location"] = df["Location"].astype("category")

        self.logger.info(
            "Locations after renaming and dropping 'Other': %s unique values.",
            df["Location"].nunique(),
        )
        return df

    def process_urls_and_job_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        """Truncate URLs and extract JobIDs from the URLs."""
        self.logger.info("Processing URLs and extracting JobIDs.")
        df["Url"] = df["Url"].apply(lambda url: url.split("?position")[0])
        df["JobID"] = df["Url"].apply(lambda url: url[-10:])
        return df

    def filter_valid_job_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove rows with invalid JobIDs (not 10 digits)."""
        original_count = df.shape[0]
        df = df[df["JobID"].notna()]
        df = df[df["JobID"].apply(lambda value: re.fullmatch(r"\d{10}", str(value)) is not None)]

        filtered_count = df.shape[0]
        removed_count = original_count - filtered_count
        self.logger.info(
            "Removed %s rows with invalid JobIDs. %s records remaining.",
            removed_count,
            filtered_count,
        )
        return df

    def remove_duplicate_job_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        """Find and remove duplicate JobIDs."""
        duplicate_count = df["JobID"].duplicated().sum()

        if duplicate_count > 0:
            self.logger.info("Found %s duplicate JobIDs. Removing duplicates.", duplicate_count)
            return df.drop_duplicates(subset="JobID", keep="first").reset_index(drop=True)

        self.logger.info("No duplicate JobIDs found.")
        return df

    def remove_duplicates_by_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicates based on Location, Title, and Company."""
        original_count = df.shape[0]
        df = df.drop_duplicates(subset=["Location", "Title", "Company"]).reset_index(drop=True)
        removed_count = original_count - df.shape[0]
        self.logger.info(
            "Removed %s duplicate rows based on Location, Title, and Company.",
            removed_count,
        )
        return df

    def clean_extracted_job_data(self, df_jobs: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize extracted job details."""
        df_jobs = self.clean_num_applicants(df_jobs)
        df_jobs = self.clean_seniority_level(df_jobs)
        df_jobs = self.standardize_employment_type(df_jobs)
        df_jobs = self.standardize_job_function(df_jobs)
        df_jobs = self.split_job_functions(df_jobs)
        df_jobs = self.convert_posted_time(df_jobs)
        df_jobs = self.reorder_columns(df_jobs)
        return df_jobs

    def clean_num_applicants(self, df_jobs: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the number of applicants."""

        def extract_num_applicants(text: str) -> int | str:
            match = re.search(r"\d+", text)
            if match:
                return int(match.group())
            if "Be among the first 25" in text:
                return 25
            if "Over 200 applicants" in text:
                return 200
            return "N/A"

        self.logger.info("Cleaning the 'NumApplicants' column.")
        df_jobs["NumApplicants"] = df_jobs["NumApplicants"].apply(extract_num_applicants)
        return df_jobs

    def clean_seniority_level(self, df_jobs: pd.DataFrame) -> pd.DataFrame:
        """Clean up the 'SeniorityLevel' column."""
        self.logger.info("Cleaning the 'SeniorityLevel' column.")
        df_jobs["SeniorityLevel"] = df_jobs["SeniorityLevel"].apply(
            lambda value: "N/A" if "Not Applicable" in value else value
        )
        seniority_categories = [
            "Entry level",
            "Mid-Senior level",
            "Executive",
            "N/A",
            "Associate",
            "Internship",
        ]
        df_jobs["SeniorityLevel"] = pd.Categorical(
            df_jobs["SeniorityLevel"], categories=seniority_categories
        )
        return df_jobs

    def standardize_employment_type(self, df_jobs: pd.DataFrame) -> pd.DataFrame:
        """Standardize 'EmploymentType' as a categorical variable."""
        self.logger.info("Standardizing 'EmploymentType' as a categorical variable.")
        df_jobs["EmploymentType"] = pd.Categorical(
            df_jobs["EmploymentType"], categories=df_jobs["EmploymentType"].unique()
        )
        return df_jobs

    def standardize_job_function(self, df_jobs: pd.DataFrame) -> pd.DataFrame:
        """Standardize the 'JobFunction' column."""

        def standardize_job_function(text: str) -> str:
            if " and " in text:
                text = text.replace(" and ", ", ")
            job_functions = text.split(", ")
            if len(job_functions) > 3:
                job_functions = job_functions[:3]
            return ", ".join(job_functions)

        self.logger.info("Standardizing the 'JobFunction' column.")
        df_jobs["JobFunction"] = df_jobs["JobFunction"].replace(
            {"Research and Design": "R&D", "Design and Product Management": "Product Management"},
            regex=False,
        )
        df_jobs["JobFunction"] = df_jobs["JobFunction"].apply(standardize_job_function)
        return df_jobs

    def split_job_functions(self, df_jobs: pd.DataFrame) -> pd.DataFrame:
        """Split 'JobFunction' into three separate columns."""

        def split_job_functions(text: str) -> pd.Series:
            job_functions = text.split(", ")
            values = [
                job_functions[index] if len(job_functions) > index else None
                for index in range(3)
            ]
            return pd.Series(values)

        self.logger.info("Splitting 'JobFunction' into three separate columns.")
        df_jobs[["JobFunction1", "JobFunction2", "JobFunction3"]] = df_jobs["JobFunction"].apply(
            split_job_functions
        )

        df_jobs["JobFunction1"] = df_jobs["JobFunction1"].fillna("N/A")
        df_jobs["JobFunction2"] = df_jobs["JobFunction2"].fillna("N/A")
        df_jobs["JobFunction3"] = df_jobs["JobFunction3"].fillna("N/A")

        job_function_categories = list(
            set(
                df_jobs["JobFunction1"].unique().tolist()
                + df_jobs["JobFunction2"].unique().tolist()
                + df_jobs["JobFunction3"].unique().tolist()
            )
        )

        df_jobs["JobFunction1"] = pd.Categorical(
            df_jobs["JobFunction1"], categories=job_function_categories
        )
        df_jobs["JobFunction2"] = pd.Categorical(
            df_jobs["JobFunction2"], categories=job_function_categories
        )
        df_jobs["JobFunction3"] = pd.Categorical(
            df_jobs["JobFunction3"], categories=job_function_categories
        )

        df_jobs.drop(columns=["JobFunction"], inplace=True)
        return df_jobs

    def convert_posted_time(self, df_jobs: pd.DataFrame) -> pd.DataFrame:
        """Convert 'PostedTime' into dates."""

        def convert_posted_time(text: str):
            today = datetime.today()

            if "hour" in text:
                return today
            if "day" in text:
                days = int(re.search(r"\d+", text).group()) if re.search(r"\d+", text) else 1
                return today - timedelta(days=days)
            if "week" in text:
                weeks = int(re.search(r"\d+", text).group()) if re.search(r"\d+", text) else 1
                return today - timedelta(days=weeks * 7)
            if "month" in text:
                months = int(re.search(r"\d+", text).group()) if re.search(r"\d+", text) else 1
                return today - timedelta(days=months * 30)
            return "N/A"

        self.logger.info("Converting 'PostedTime' to DatePosted.")
        df_jobs["PostedTime"] = df_jobs["PostedTime"].apply(convert_posted_time)
        df_jobs.rename(columns={"PostedTime": "DatePosted"}, inplace=True)
        return df_jobs

    def reorder_columns(self, df_jobs: pd.DataFrame) -> pd.DataFrame:
        """Reorder the columns in the dataframe for better organization."""
        self.logger.info("Reordering the columns in the DataFrame.")
        new_column_order = [
            "Title",
            "Company",
            "Location",
            "Remote",
            "SeniorityLevel",
            "EmploymentType",
            "Industries",
            "DatePosted",
            "NumApplicants",
            "JobFunction1",
            "JobFunction2",
            "JobFunction3",
            "Description",
            "Url",
            "JobID",
        ]
        return df_jobs[new_column_order]

    def process_enriched_job_data(
        self, df_jobs: pd.DataFrame, tech_stack_categories: dict[str, list[str]] | None = None
    ) -> pd.DataFrame:
        """Post-process enriched job data."""
        self.logger.info("Starting job data processing.")
        df_jobs = self.extract_min_years(df_jobs)
        df_jobs = self.categorize_studies(df_jobs)

        if tech_stack_categories is not None:
            df_jobs = self.categorize_tech_stack(df_jobs, tech_stack_categories)

        self.logger.info("Completed job data processing.")
        return df_jobs

    def extract_min_years(self, df_jobs: pd.DataFrame) -> pd.DataFrame:
        """Extract the minimum number of years from the experience string."""

        def extract_min_years_from_str(experience_str: str) -> int | str:
            experience_str = str(experience_str)
            if (
                "N/A" in experience_str
                or "Professional software development experience required" in experience_str
            ):
                return "N/A"

            numbers = re.findall(r"\d+", experience_str)
            if not numbers:
                return "N/A"
            return min(map(int, numbers))

        df_jobs["MinYoE"] = df_jobs["YoE"].apply(extract_min_years_from_str)
        return df_jobs

    def categorize_studies(self, df_jobs: pd.DataFrame) -> pd.DataFrame:
        """Categorize the minimum level of studies."""

        def categorize_study_level(level: str) -> str:
            normalized_level = level.lower()
            if any(keyword in normalized_level for keyword in ["student", "undergraduate"]):
                return "Undergraduate Student"
            if any(
                keyword in normalized_level
                for keyword in ["bachelor", "bs", "b.sc", "bachelor's"]
            ):
                return "Bachelor"
            if any(
                keyword in normalized_level for keyword in ["master", "ms", "m.sc", "master's"]
            ):
                return "Masters"
            if "phd" in normalized_level:
                return "PhD"
            return "N/A"

        df_jobs["MinLevelStudies"] = df_jobs["MinLevelStudies"].apply(categorize_study_level)
        return df_jobs

    def categorize_tech_stack(
        self, df_jobs: pd.DataFrame, tech_stack_categories: dict[str, list[str]]
    ) -> pd.DataFrame:
        """Categorize tech stack values into predefined groups."""
        for category in tech_stack_categories:
            df_jobs[category] = 0

        df_jobs["Other"] = 0

        def categorize_single_tech_stack(tech_stack: str, index: int) -> None:
            tech_stack_elements = [element.strip() for element in tech_stack.split(",")]
            category_found = False

            for category, items in tech_stack_categories.items():
                for item in items:
                    if any(item in element for element in tech_stack_elements):
                        df_jobs.at[index, category] = 1
                        category_found = True

            if not category_found:
                df_jobs.at[index, "Other"] = 1

        for index, row in df_jobs.iterrows():
            categorize_single_tech_stack(row["TechStack"], index)

        return df_jobs