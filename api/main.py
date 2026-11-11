import json
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

# With FastAPI, the serialization is made by the framework automatically
# Serialize: transforms a python object to Json file
# Deserialize: transforms a Json file in a python object

app = FastAPI()


# We have to modify the domains that can access the api

origins = ["http://localhost:5174"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # allow domains from my own computer
    allow_credentials=True,
    allow_methods=["*"],  # allow all the methods of the API
    allow_headers=["*"],
)


# Change CORS allowed connections to allow another web pages from my computer access the API

allowed_connections = ["http://localhost", "http://localhost:5173"]


@app.get("/products", summary="Get all the products from the database")
def read_products():
    """Get all the products in the database"""

    with open("api/products.json", mode="r", encoding="UTF_8") as file:
        products = json.load(file)
        return products


@app.post(
    "/products",
    summary="Add a new product to the database",
    status_code=status.HTTP_201_CREATED,
)
def create_product(url: str):
    """Add a new product to the database"""

    with open("api/products.json", mode="r+", encoding="UTF_8") as file:
        products = json.load(file)
        uuid = str(uuid4())
        if url in products:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The product is already in the database",
            )
        products[url] = uuid
        file.seek(0)
        file.truncate()
        json.dump(products, file)

    with open("api/prices.json", mode="r+", encoding="UTF_8") as file:
        prices = json.load(file)

        if uuid in prices:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The product is already in the database",
            )

        prices[uuid] = {}
        file.seek(0)
        file.truncate()
        json.dump(prices, file)


@app.get("/products/{uuid}/prices", summary="Read the history of prices from a product")
def read_prices(uuid: str) -> dict | None:
    """Get the prices history of a product"""

    with open("api/prices.json", mode="r", encoding="UTF_8") as file:
        prices = json.load(file)
        if uuid not in prices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no product with that id",
            )
        return prices[uuid]


@app.put(
    "/products/{uuid}/prices",
    summary="Add a new price to the history of a product",
    status_code=status.HTTP_201_CREATED,
)
def put_price(uuid: str, price: float):
    """Add a new price into a product"""

    with open("api/prices.json", mode="r+", encoding="UTF_8") as file:
        prices = json.load(file)
        if uuid not in prices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product wasn't found in the database",
            )

        prices[uuid][datetime.now().isoformat()] = price
        file.seek(0)
        file.truncate()
        json.dump(prices, file)
