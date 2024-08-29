# GMaps-Insight-Tool
# GMaps Insight Tool

## Description

The GMaps Insight Tool is a Python-based scraper using Playwright to extract business data from Google Maps. This tool can scrape information such as business names, addresses, websites, phone numbers, reviews count, and average reviews.

## Features

- Scrapes business data from Google Maps.
- Extracts business names, addresses, websites, phone numbers, reviews count, and average reviews.
- Saves the data to Excel and CSV files.
- Scrolls through each pages.

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/MhmdSalman18/GMaps-Insight-Tool.git
    ```

2. **Navigate to the project directory:**

    ```bash
    cd GMaps-Insight-Tool
    ```

3. **Create a virtual environment (optional but recommended):**

    ```bash
    python -m venv venv
    ```

4. **Activate the virtual environment:**

    - On Windows:

      ```bash
      venv\Scripts\activate
      ```

    - On macOS/Linux:

      ```bash
      source venv/bin/activate
      ```

5. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Run the script:**

    ```bash
    python main.py -s "search query" -t number_of_results
    ```

   Replace `"search query"` with the desired search term and `number_of_results` with the number of results to scrape.

## Contributing

Feel free to fork the repository and submit pull requests with improvements or bug fixes.


