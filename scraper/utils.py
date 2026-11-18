import requests
from bs4 import BeautifulSoup

# Some functions that can be exported to other packages

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9",
}


def get_name_and_price(url: str) -> tuple[str, float] | None:
    """Get the name and the current price of a product"""

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Find price

        container_price = soup.find("div", class_="price fx-text fx-text--no-margin")

        if container_price:
            # If there is a discount, the current price is in an span
            span_discount = soup.find("span", class_="price__primary")

            # Check if there is a discount or not
            objective = span_discount if span_discount else container_price

            price_string = str(objective.contents[0]).strip()

            price = float(
                price_string.replace("$", "")
                .replace("€", "")
                .replace(".", "")
                .replace(",", ".")
            )

        else:
            return None

        # Find name

        tag_name = soup.find("h1", attrs={"itemprop": "name"})

        if tag_name:
            name = tag_name.text.strip()

        else:
            return None

        return (name, price)

    else:
        return None
