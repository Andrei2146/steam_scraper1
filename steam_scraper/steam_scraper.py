import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://store.steampowered.com/search/?filter=topsellers"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def scrape_steam_games(pages=1):
    game_data = []

    for page in range(1, pages + 1):
        url = f"{BASE_URL}&page={page}"
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")

        games = soup.find_all("a", class_="search_result_row")
        print(f"Found {len(games)} games on page {page}")

        for game in games:
            title = game.find("span", class_="title").text.strip()

            price_element = game.find("div", class_="discount_block")
            if price_element and "data-price-final" in price_element.attrs:
                price = int(price_element["data-price-final"]) / 100 
                price = f"{price:.2f}€"
            else:
                price = "Free" if "free" in game.text.lower() else "Unknown"
            discount = price_element["data-discount"] + "%" if price_element and "data-discount" in price_element.attrs else "0%"

            print(f" {title} | Price: {price} | Discount: {discount}")

            game_data.append({"Title": title, "Price": price, "Discount": discount})

        time.sleep(1)

    return game_data

games_list = scrape_steam_games(pages=2)

df = pd.DataFrame(games_list)

df["Price"] = df["Price"].replace("Free", "0").str.replace("€", "", regex=False).astype(float)
df["Discount"] = df["Discount"].str.replace("%", "", regex=False).astype(int)

print("\n Choose sorting option:")
print("1  Discount (highest to lowest)")
print("2  Price (lowest to highest)")
print("3  Name (A-Z)")

choice = input("\nEnter your choice (1-3): ")

if choice == "1":
    df = df.sort_values(by="Discount", ascending=False)
elif choice == "2":
    df = df.sort_values(by="Price", ascending=True)
elif choice == "3":
    df = df.sort_values(by="Title", ascending=True)
else:
    print(" Invalid choice. Defaulting to Name (A-Z).")
    df = df.sort_values(by="Title", ascending=True)

    
df.to_excel("steam_games.xlsx", index=False)

print(" Sorted data saved to 'steam_games.xlsx'! ")
