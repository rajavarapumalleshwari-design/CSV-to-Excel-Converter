import argparse
import logging
import os
import pandas as pd


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def clean_data(df):
    """Clean and normalize the DataFrame."""

    # Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w]", "", regex=True)
    )

    # Strip whitespace from string columns
    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    # Replace empty strings with missing values
    df.replace("", pd.NA, inplace=True)

    # Fill missing values
    for column in df.columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            df[column] = df[column].fillna(0)
        else:
            df[column] = df[column].fillna("Unknown")

    # Try to parse columns containing date/time
    for column in df.columns:
        if "date" in column or "time" in column:
            try:
                df[column] = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )
            except Exception:
                logging.warning(
                    "Could not parse date column: %s", column
                )

    return df


def convert_csv_to_excel(input_file, output_file):
    """Convert a CSV file to an Excel file."""

    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(
                f"Input file not found: {input_file}"
            )

        if not input_file.lower().endswith(".csv"):
            raise ValueError("Input file must be a CSV file.")

        logging.info("Reading CSV: %s", input_file)

        df = pd.read_csv(input_file)

        if df.empty:
            raise ValueError("The CSV file is empty.")

        logging.info("Cleaning data...")
        df = clean_data(df)

        # Example column renames
        rename_columns = {
            "fname": "first_name",
            "lname": "last_name"
        }

        df.rename(columns=rename_columns, inplace=True)

        # Export to Excel
        logging.info("Writing Excel file: %s", output_file)

        df.to_excel(
            output_file,
            index=False,
            engine="openpyxl"
        )

        logging.info(
            "Conversion successful! %d rows exported.",
            len(df)
        )

    except pd.errors.EmptyDataError:
        logging.error("The CSV file contains no data.")

    except pd.errors.ParserError:
        logging.error(
            "Could not parse the CSV file. Check its format."
        )

    except PermissionError:
        logging.error(
            "Permission denied. Check the input/output file permissions."
        )

    except Exception as error:
        logging.error("Conversion failed: %s", error)


def main():
    parser = argparse.ArgumentParser(
        description="Convert and clean CSV files to Excel."
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Path to the input CSV file"
    )

    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Path to the output Excel file"
    )

    args = parser.parse_args()

    convert_csv_to_excel(
        args.input,
        args.output
    )


if __name__ == "__main__":
    main()