import requests
from concurrent.futures import ThreadPoolExecutor

URL = "http://127.0.0.1:5000/buy_ticket"

def buy():
    response = requests.post(URL)
    return response.status_code

if __name__ == "__main__":
    success = 0
    failure = 0

    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(lambda _: buy(), range(1000)))

    for r in results:
        if r == 200:
            success += 1
        elif r == 410:
            failure += 1

    print("Successful purchases:", success)
    print("Failed purchases (sold out):", failure)
