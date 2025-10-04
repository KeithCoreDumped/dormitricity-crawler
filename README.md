# Dormitricity Crawler

This directory contains the Python-based web crawler for the Dormitricity project. Its primary responsibility is to fetch electricity balance data for various dormitories and submit it to the backend worker for processing and storage.

## How It Works

The crawler operates in a distributed manner, coordinated by the backend worker.

1.  **Job Claiming**: The crawler starts by making a POST request to the `/crawler/claim` endpoint of the backend worker. It sends a `job_id` and receives a "slice" of dormitories to query. If there are no more dormitories to process, the endpoint returns an empty response, and the crawler exits.
2.  **Data Scraping**: For each dormitory in the claimed slice, the crawler determines whether to use the "new" or "legacy" backend to fetch the data.
    *   **Legacy Backend**: Uses the `requests` library to query older, simpler systems.
    *   **New Backend**: Uses `selenium` and a headless Chrome browser to interact with more complex, JavaScript-heavy university power portals.
3.  **Data Ingestion**: After querying all dormitories in the slice, the crawler packages the results (both successes and failures) into a payload. This payload is sent to the `/crawler/ingest` endpoint of the backend worker. This process is idempotent, using a key composed of the job ID and slice index.
4.  **Looping**: The crawler repeats this claim-scrape-ingest cycle until the backend has no more slices to distribute for the given job.

## Setup and Dependencies

The crawler is written in Python 3.11 and relies on two main external libraries.

*   **Dependencies**:
    *   `requests`: For making HTTP API calls to the worker.
    *   `selenium`: For browser automation to scrape data from modern web portals.

*   **Installation**:
    ```bash
    pip install -r requirements.txt
    ```

*   **Browser Driver**:
    The crawler requires Google Chrome and the corresponding `chromedriver` to be installed and available in the system's PATH, as it uses `selenium` for web scraping.

## Running Locally

To run the crawler on a local machine for testing or development:

1.  **Create `secret.py`**: Create a file named `secret.py` in the root of the crawler directory. This file is git-ignored and should contain the necessary credentials for the legacy and new backends.

    ```python
    # secret.py
    legacy_backend_cookies = {
        "JSESSIONID": "...",
        # other cookies...
    }

    new_backend_url = "https://your-university-power-system.com/login"
    ```

2.  **Set Environment Variables**: The crawler needs environment variables to communicate with the worker. You can set them in your shell:

    ```bash
    export WORKERS_BASE="http://127.0.0.1:8787" # Example for a local worker
    export JOB_ID="local_test_job"
    export TOKEN="your_secret_worker_token"
    ```

3.  **Execute the script**:

    ```bash
    python main.py
    ```

    When run without command-line arguments, the script automatically uses the `secret.py` file for its parameters.

## Deployment (GitHub Actions)

The crawler is designed to be deployed as a scheduled or manually triggered job using GitHub Actions. The workflow is defined in `.github/workflows/crawler.yml`.

*   **Trigger**: The workflow is triggered by a `workflow_dispatch` event, which requires a `job_id` and a `token` to be passed as inputs. This is typically initiated by the backend worker itself.
*   **Environment**: The job runs on an `ubuntu-latest` runner. It sets up Python, installs dependencies from `requirements.txt`, and uses the `nanasess/setup-chromedriver` action to install Chrome and its driver.
*   **Execution**: The `main.py` script is executed with its parameters passed as a Base64-encoded JSON string. Secrets like the worker URL (`WORKERS_BASE`) and the crawler parameters (`PARAMS`) are managed via GitHub Secrets.

## Configuration

The crawler's behavior is configured through environment variables and, for production runs, a JSON object.

*   **Environment Variables**:
    *   `JOB_ID`: A unique identifier for the crawling job.
    *   `TOKEN`: The authorization token required by the worker API.
    *   `WORKERS_BASE`: The base URL for the Dormitricity worker API (e.g., `https://dormitricity-worker.example.com`).

*   **Parameters (`params`)**:
    For production runs (like in GitHub Actions), the script receives a Base64-encoded JSON string as a command-line argument. This JSON object contains the necessary credentials and configurations, such as cookies for the legacy backend and the URL for the new backend. This avoids storing sensitive information directly in the repository.
