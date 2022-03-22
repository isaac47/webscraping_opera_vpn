from src.my_scraper.scaper import apply_scraping

if __name__ == "__main__":
    # Test urls
    urls = [
        "https://www.nordstrom.com/browse/sale/women/maternity?breadcrumb=Home%2FSale%2FWomen%2FMaternity&origin=topnav"
    ]
    apply_scraping(urls)
