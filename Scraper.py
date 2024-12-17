from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import time
import bs4
import pandas as pd


#Example URLs
#https://bringatrailer.com/porsche/996-911/
#https://bringatrailer.com/nissan/r33-skyline/

url = input("What is the BaT page you want to scrape?: ")
trans_flag = int(input("Does this car have a manual trans option?[1-YES, 0-No]: "))
model_input_list = input("Please provide a list of model options seperated by commas (ex. NISMO,Black Edition,etc): ")
body_flag = int(input("Does this vehicle have multiple body types? (ie Cabriolet, coupe, etc) 1-YES, 0-No]: "))
# Open the page
options = Options()
options.headless = True
web_driver = webdriver.Firefox(options=options)
web_driver.get(url)

# Wait for the page to load
time.sleep(3)  # You can adjust this depending on your connection speed

load_more = True

# Start loop to click "Show More" button

while load_more:
    try:
        # Wait until the "Show More" button is clickable using the updated XPath for the span
        show_more_button = WebDriverWait(web_driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Show More']"))
        )

        # Scroll the button into view (if necessary)
        web_driver.execute_script("arguments[0].scrollIntoView(true);", show_more_button)

        # Click the "Show More" button
        show_more_button.click()

        # Wait for content to load (you can adjust the time if needed)
        time.sleep(2)

    except Exception as e:
        print(f"An error occurred: {e}")
        break  # Exit the loop if an error occurs (e.g., no "Show More" button found)



# Continue with other scraping or actions after this
soup = bs4.BeautifulSoup(web_driver.page_source, 'html.parser')
raw_results_title = soup.find_all("h3", {"data-bind": "html: title"})


#works above this line
raw_results_price = soup.find_all("div", {'class': 'item-results'})

# Extract titles and prices into lists
titles = [title.text.strip() for title in raw_results_title]
prices = [price.text.strip() for price in raw_results_price]
prices = list(filter(None, prices))

# Create a DataFrame
df = pd.DataFrame({'Title': titles, 'Price line': prices})
df['date'] = df['Price line'].str[-10:]
df['date'] = df['date'].str[-8:]
df['date'] = df['date'].replace('n ','',regex=True)
df['date'] = df['date'].replace(' ','',regex=True)
df['Price'] = df['Price line'].str.extract(r'(\$[0-9,.]+)')
df['Price'] = df['Price'].str[1:]
df['status'] = df['Price line'].str[:4]
df['status'] = df['status'].replace(' ','',regex=True)
df['Miles'] = df['Price line'].str.extract('(\d{1,3}[,k ]\d{0,3}) ?miles')
df['Year'] = df['Title'].str.extract(r'(\d{4})')

# Use boolean indexing to identify rows with '6-speed' and assign 'man'
print(trans_flag)
if trans_flag == 1:
    df['Trans'] = 'auto'
    df.loc[df['Title'].str.contains('Speed'), 'Trans'] = 'man'
    
print(df.head)
model_input_list = model_input_list.split(",")

#Defining Model
i=len(model_input_list)
x=0
df['Model'] = 'base'
while x < i:
    
    
    df.loc[df['Title'].str.contains(model_input_list[x],case=False, na=False),'Model'] = model_input_list[x]
    x=x+1
    


#Defining Body Type
if body_flag == 1:
    
    df['Body'] = 'Coupe'
    df.loc[df['Title'].str.contains('Coupe'), 'Body'] = 'Coupe'
    df.loc[df['Title'].str.contains('Cabriolet'), 'Body'] = 'Cabriolet'
    df.loc[df['Title'].str.contains('Targa'), 'Body'] = 'Targa'
    df.loc[df['Title'].str.contains('Convertible'), 'Body'] = 'Convertible'

    

df['Miles'] = df['Title'].str.extract(r'(\d+)k-Mile')
df['Miles'].fillna(100,inplace=True)
# Convert the extracted mileage to a numeric value
df['Miles'] = df['Miles'].astype(int) * 1000

#Final Cleaning
df_cleaned_cars = df.loc[~(df['Year'].isnull())]
df_cleaned_not_cars = df.loc[(df['Year'].isnull())]

#Export to CSV
df_cleaned_cars.to_csv('df_cleaned_cars.csv')
df_cleaned_not_cars.to_csv('df_cleaned_not_cars.csv')

