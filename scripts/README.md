# OpenMetadata - Batch Processing Scripts

This folder contains scripts for batch processing metadata from CSV files stored in `reference_csvs` into the OpenMetadata data catalog. 

These scripts primarily handle tagging, but some also manage applying and removing users to data assets.

## Folder Structure

- **`reference_csvs/`**: Folder containing CSV files used as input data for batch processing.
- **`apply_user.py`**: Script for applying users to data assets in the data catalog.
- **`batch_upload_tags.py`**: Script for uploading multiple tags in batches from a CSV.
- **`config.py`**: Configuration file for setting up API connections and project settings.
- **`patch_column_tags.ipynb`**: Jupyter notebook for updating or patching column level tags.
- **`remove_user.py`**: Script to remove users and related tags from specific metadata items.
- **`removing_tags.py`**: Script to remove tags from metadata items in the catalog.
- **`spreadsheet_iteration.py`**: Iterates through a spreadsheet to apply tags or other metadata updates.
- **`tagging_object.py`**: Applying a tag to a single data asset.
