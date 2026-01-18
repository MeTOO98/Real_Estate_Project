from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from pathlib import Path
import time
import pandas

def create_result(driver, par):
    try:
        result = driver.find_element(By.XPATH, par).text 
        if result:
            return result
        else:
            return None
    except:
        return None

def main_task():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Let Selenium find chromedriver automatically or use your path
    try:
        driver = webdriver.Chrome(options=options)
    except:
        driver = webdriver.Chrome(
            service=Service("/usr/bin/chromedriver"),
            options=options
        )
    
    urls = [
        "https://www.bayut.eg/en/cairo/properties-for-sale-in-new-cairo-5th-settlement/",
        "https://www.bayut.eg/en/giza/properties-for-sale-in-sheikh-zayed/"
    ]
    
    all_results = []
    
    for base_url in urls:
        counter = 0
        url = base_url
        
        while counter <= 150 and url :
            try:
                print(f"Processing page {counter + 1} for {base_url}")
                driver.get(url)
                wait = WebDriverWait(driver, 10)
                
                # Scroll to load all content
                last_height = driver.execute_script("return document.body.scrollHeight")
                scroll_attempts = 0
                max_scroll_attempts = 10
                
                while scroll_attempts < max_scroll_attempts:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                    scroll_attempts += 1

                # Wait for container
                container = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[contains(@class,'_15877fde')]")
                    )
                )

                # Get all apartment listings
                apartments = container.find_elements(
                    By.XPATH, ".//li[contains(@class,'_92ae6bf0')]"
                )

                # Extract hrefs
                hrefs = set()
                for ap in apartments:
                    try:
                        link = ap.find_element(
                            By.XPATH, ".//a[contains(@class,'_8969fafd')]"
                        )
                        href = link.get_attribute("href")
                        if href:
                            hrefs.add(href)
                    except:
                        continue

                print(f"Found {len(hrefs)} listings on this page")
                
                # Process each listing
                for h in hrefs:
                    result = {}
                    try:
                        driver.get(h)
                        time.sleep(3)
                        result["url"] = h
                        result["Price"] = create_result(driver, "//span[@aria-label='Price']")
                        result["NumOFRooms"] = create_result(driver, "//span[@aria-label='Beds']")
                        result["NumOFBathroom"] = create_result(driver, "//span[@aria-label='Baths']")
                        result["Size"] = create_result(driver, "//span[@aria-label='Area']")
                        result['Type'] = create_result(driver, "//span[@aria-label='Type']")
                        result['Created_date'] = create_result(driver, "//span[@aria-label='Reactivated date']")
                        result["Completion status"] = create_result(driver, "//span[@aria-label='Completion status']")
                        result["location"] = create_result(driver, "//div[@aria-label='Property header']")
                        all_results.append(result)
                    except Exception as e:
                        print(f"Error processing listing {h}: {e}")
                        continue
                
                counter += 1
                
                # Try to find next page
                driver.get(url)
                time.sleep(2)
                
                try:
                    next_button = driver.find_element(By.XPATH, ".//a[@title='Next']")
                    next_url = next_button.get_attribute("href")
                    
                    if not next_url or next_url == url:
                        print("No more pages available")
                        break
                    
                    url = next_url
                except NoSuchElementException:
                    print("Next button not found - reached last page")
                    break
                    
            except TimeoutException:
                print(f"Timeout waiting for page to load: {url}")
                break
            except Exception as e:
                print(f"Error on page {counter + 1}: {e}")
                break
    
    # Save results
    if all_results:
        df = pandas.DataFrame(all_results)
        file_path = Path("/data/bayut_raw.csv")
        df.to_csv(file_path, mode="a", header=False, index=False)
        print(f"Appended {len(all_results)} records to existing file")
    else:
        print("No results collected")

    driver.quit()
main_task()