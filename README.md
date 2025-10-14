# ML FastAPI Project

A comprehensive machine learning API with training, ETL, inference, and automation capabilities.

## Project Structure Overview

### 🏗️ Core Components

- **`app/main.py`** - FastAPI application entry point
- **`app/core/`** - Configuration and security settings
- **`app/models/`** - Pydantic schemas for data validation
- **`app/utils/`** - Utility functions and logging

### 📊 Data Layer

- **`app/data/etl.py`** - ETL operations for database interactions
- **Location**: `app/data/etl.py`

#### How to program ETL operations:

```python
# Example ETL operation
from app.data.etl import DataETL
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize ETL
etl = DataETL()

# Extract data from database
def extract_training_data():
    try:
        data = etl.extract_data(
            query="SELECT * FROM training_data WHERE date >= %s",
            params=("2024-01-01",)
        )
        logger.info(f"Extracted {len(data)} records")
        return data
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise

# Transform data
def transform_data(raw_data):
    # Add your transformation logic here
    transformed = etl.clean_data(raw_data)
    transformed = etl.feature_engineering(transformed)
    return transformed

# Load processed data
def load_processed_data(processed_data, table_name):
    etl.load_data(processed_data, table_name)