import json
from datetime import datetime
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from scraper import get_name_and_price

# With FastAPI, the serialization is made by the framework automatically
# Serialize: transforms a python object to Json file
# Deserialize: transforms a Json file in a python object

app = FastAPI()


# We have to modify the domains that can access the api

origins = ["http://localhost:5500", "http://127.0.0.1:5500"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # allow domains from my own computer
    allow_credentials=True,
    allow_methods=["*"],  # allow all the methods of the API
    allow_headers=["*"],
)


@app.get("/products", summary="Get all the products from the database")
def read_products():
    """Get all the products in the database"""

    with open("api/products.json", mode="r", encoding="UTF_8") as file:
        products = json.load(file)
        return products


# To add a new product, we send the url in the body of the request

# To do that, we need pydantic models, as we have to define the format of the object we are receiving


class Item(BaseModel):
    url: str


@app.post(
    "/products",
    summary="Add a new product to the database",
    status_code=status.HTTP_201_CREATED,
)
def create_product(item: Item):
    """Add a new product to the database"""

    # Get the name and the price of the product
    result = get_name_and_price(item.url)

    if result is not None:
        name, price = result

    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The URL is not valid",
        )

    with open("api/products.json", mode="r+", encoding="UTF_8") as file:
        products = json.load(file)
        uuid = str(uuid4())
        for product in products:
            if product["url"] == item.url:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="The product is already in the database",
                )

        products.append({"name": name, "url": item.url, "id": uuid})
        file.seek(0)
        file.truncate()
        json.dump(products, file)

    with open("api/prices.json", mode="r+", encoding="UTF_8") as file:
        prices = json.load(file)

        for product_history in prices:
            if product_history["id"] == uuid:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="The product is already in the database",
                )

        prices.append(
            {
                "id": uuid,
                "history": [{"date": datetime.now().isoformat(), "price": price}],
            }
        )
        file.seek(0)
        file.truncate()
        json.dump(prices, file)

    return {"id": uuid, "message": "Product added successfully"}


@app.get("/products/{uuid}/prices", summary="Read the history of prices from a product")
def read_prices(uuid: str) -> list | None:
    """Get the prices history of a product"""

    with open("api/prices.json", mode="r", encoding="UTF_8") as file:
        prices = json.load(file)

        for price in prices:
            if price["id"] == uuid:
                return price["history"]

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no product with that id",
        )


@app.put(
    "/products/{uuid}/prices",
    summary="Add a new price to the history of a product",
    status_code=status.HTTP_201_CREATED,
)
def put_price(uuid: str, price: float):
    """Add a new price into a product"""

    with open("api/prices.json", mode="r+", encoding="UTF_8") as file:
        prices = json.load(file)

        for history in prices:
            if history["id"] == uuid:
                history["history"].append(
                    {"date": datetime.now().isoformat(), "price": price}
                )
                break

        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product wasn't found in the database",
            )

        file.seek(0)
        file.truncate()
        json.dump(prices, file)


@app.get("/products/prices", summary="Get the last price of every product")
def read_current_prices() -> list:
    """Get the current price of every product"""

    with open("api/prices.json", mode="r", encoding="UTF_8") as file:
        prices = json.load(file)

        result = []

        for price in prices:
            if price["history"] == []:
                current_price = -1
            else:
                current_price = price["history"][-1]["price"]
            result.append({"id": price["id"], "price": current_price})

    return result


@app.get("/products/{uuid}", summary="Get product information")
def read_product(uuid: UUID) -> object | None:
    """Get the product with an uuid"""

    with open("api/products.json", mode="r", encoding="UTF_8") as file:
        products = json.load(file)

        for product in products:
            if product["id"] == str(uuid):
                return product

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no product with that id",
        )
