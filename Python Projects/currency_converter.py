import requests

def convert_currency(amount, from_currency, to_currency):
    url = f"https://open.er-api.com/v6/latest/{from_currency}"
    response = requests.get(url)
    data = response.json()

    if "rates" in data and to_currency in data["rates"]:
        rate = data["rates"][to_currency]
        return amount * rate
    else:
        return None
    
if __name__ == "__main__":
    print("💱 Currency Converter (NPR ↔ USD, INR, JPY, etc.)")
    amount = float(input("Enter amount: "))
    from_currency = input("From currency (e.g., NPR, USD, etc.): ").upper()
    to_currency = input("To currency (e.g., NPR, USD, etc.): ").upper()

    result = convert_currency(amount, from_currency, to_currency)

    if result:
        print(f"\n✅ {amount} {from_currency} = {result:.2f} {to_currency}")
    else:
        print("⚠️ Conversion failed. Try again.")