from playwright.sync_api import sync_playwright  # Import Playwright for browser automation
from dataclasses import dataclass, asdict, field  # Import dataclass for creating data structures
import pandas as pd  # Import pandas for handling data and saving it to files
import argparse  # Import argparse for command-line argument parsing
import os  # Import os for file and directory handling
import sys  # Import sys for system-specific parameters and functions 
# and functions 
# Data class to hold business information newwwwwwwwwwwwwww
# and functions 
@dataclass
class Business:
    name: str = ""  # Business name
    address: str = ""  # Business address new
    website: str = ""  # Business website
    phone_number: str = ""  # Business phone number
    reviews_count: int = 0  # Number of reviews
    reviews_average: float = 0.0  # Average review rating
    latitude: float = 0.0  # Latitude coordinate
    longitude: float = 0.0  # Longitude coordinate

# Data class to manage a list of Business objects and save them to files
@dataclass
class BusinessList:
    business_list: list[Business] = field(default_factory=list)  # List of Business objects
    save_at: str = 'output'  # Directory to save the output files

    # Convert business list to a pandas DataFrame
    def dataframe(self):
        return pd.json_normalize(
            (asdict(business) for business in self.business_list), sep="_"
        )

    # Save the DataFrame to an Excel file
    def save_to_excel(self, filename: str):
        if not os.path.exists(self.save_at):  # Check if the output directory exists
            os.makedirs(self.save_at)  # Create the directory if it doesn't exist
        self.dataframe().to_excel(os.path.join(self.save_at, f"{filename}.xlsx"), index=False)

    # Save the DataFrame to a CSV file
    def save_to_csv(self, filename: str):
        if not os.path.exists(self.save_at):  # Check if the output directory exists
            os.makedirs(self.save_at)  # Create the directory if it doesn't exist
        self.dataframe().to_csv(os.path.join(self.save_at, f"{filename}.csv"), index=False)

# Extract latitude and longitude from Google Maps URL
def extract_coordinates_from_url(url: str) -> tuple[float, float]:
    coordinates = url.split('/@')[-1].split('/')[0]  # Extract the coordinates part from the URL
    return tuple(map(float, coordinates.split(',')[:2]))  # Convert to a tuple of floats (latitude, longitude)

def main():
    # Argument parsing
    parser = argparse.ArgumentParser()  # Create an ArgumentParser object
    parser.add_argument("-s", "--search", type=str, help="Search term for Google Maps")  # Add search argument
    parser.add_argument("-t", "--total", type=int, default=1000000, help="Total results to scrape")  # Add total argument
    args = parser.parse_args()  # Parse the command-line arguments

    # Handle search terms
    search_list = [args.search] if args.search else []  # Use the search term if provided
    if not search_list:  # If no search term is provided
        input_file_path = os.path.join(os.getcwd(), 'input.txt')  # Get the path to input.txt
        if os.path.exists(input_file_path):  # Check if input.txt exists
            with open(input_file_path, 'r') as file:  # Open input.txt and read search terms
                search_list = file.readlines()
        if not search_list:  # If no search terms are found
            print('Error: Provide a search term with -s or add searches to input.txt')  # Print error message
            sys.exit()  # Exit the program

    # Scraping process
    with sync_playwright() as p:  # Start Playwright
        browser = p.chromium.launch(headless=False)  # Launch a Chromium browser instance
        page = browser.new_page()  # Open a new page (tab)

        page.goto("https://www.google.com/maps", timeout=60000)  # Navigate to Google Maps
        page.wait_for_timeout(5000)  # Wait for the page to load

        for search_for in search_list:  # Loop through each search term
            search_for = search_for.strip()  # Remove any leading/trailing whitespace
            print(f"Scraping for: {search_for}")  # Print the current search term

            # Search for the business
            page.locator('//input[@id="searchboxinput"]').fill(search_for)  # Fill the search box with the term
            page.keyboard.press("Enter")  # Press Enter to start the search
            page.wait_for_timeout(5000)  # Wait for search results to load

            # Scroll through listings
            page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')  # Hover over a listing

            # Retrieve business listings
            listings = []
            previously_counted = 0  # Keep track of the number of listings previously counted
            while len(listings) < args.total:  # Keep scrolling until the desired number of listings is reached
                page.mouse.wheel(0, 10000)  # Scroll down
                page.wait_for_timeout(3000)  # Wait for the page to load more listings

                current_count = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count()
                if current_count == previously_counted:  # If no new listings are found
                    break  # Stop scrolling

                previously_counted = current_count  # Update the previously counted listings
                listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()[:args.total]
                listings = [listing.locator("xpath=..") for listing in listings]  # Get the parent element of each listing
                print(f"Total Scraped: {len(listings)}")  # Print the total number of listings scraped

            business_list = BusinessList()  # Create a BusinessList object

            # Extract data for each listing
            for listing in listings:  # Loop through each listing
                try:
                    listing.click()  # Click on the listing to view details
                    page.wait_for_timeout(5000)  # Wait for the details page to load

                    business = Business(
                        name=listing.get_attribute('aria-label', ""),  # Get the business name
                        address=page.locator('//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]').text_content(),  # Get the business address
                        website=page.locator('//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]').text_content(),  # Get the business website
                        phone_number=page.locator('//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]').text_content(),  # Get the phone number
                        reviews_count=int(page.locator('//button[@jsaction="pane.reviewChart.moreReviews"]//span').text_content().split()[0].replace(',', '')),  # Get the review count
                        reviews_average=float(page.locator('//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]').get_attribute('aria-label').split()[0].replace(',', '.')),  # Get the average review rating
                        latitude=extract_coordinates_from_url(page.url)[0],  # Get the latitude
                        longitude=extract_coordinates_from_url(page.url)[1]  # Get the longitude
                    )
                    business_list.business_list.append(business)  # Add the business to the list
                except Exception as e:  # Handle any errors during scraping
                    print(f'Error: {e}')  # Print the error message

            # Save the results to files
            filename = f"google_maps_data_{search_for.replace(' ', '_')}"  # Create a filename based on the search term
            business_list.save_to_excel(filename)  # Save the data to an Excel file
            business_list.save_to_csv(filename)  # Save the data to a CSV file

        browser.close()  # Close the browser

if __name__ == "__main__":
    main()  # Run the main function
