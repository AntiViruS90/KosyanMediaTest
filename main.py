import xml.etree.ElementTree as ET
import pandas as pd


def parse_flights_to_dataframe(xml_content):
    """Парсинг XML и преобразование данных в DataFrame."""
    root = ET.fromstring(xml_content)
    data = []

    for flights in root.findall(".//Flights"):
        for flight in flights.findall(".//OnwardPricedItinerary/Flights/Flight"):
            flight_data = {
                "Type": "Onward",
                "Carrier": flight.find("Carrier").text,
                "FlightNumber": flight.find("FlightNumber").text,
                "Source": flight.find("Source").text,
                "Destination": flight.find("Destination").text,
                "DepartureTimeStamp": flight.find("DepartureTimeStamp").text,
                "ArrivalTimeStamp": flight.find("ArrivalTimeStamp").text,
                "Class": flight.find("Class").text,
                "NumberOfStops": int(flight.find("NumberOfStops").text),
                "FareBasis": flight.find("FareBasis").text.strip(),
                "TicketType": flight.find("TicketType").text,
            }
            data.append(flight_data)

        for flight in flights.findall(".//ReturnPricedItinerary/Flights/Flight"):
            flight_data = {
                "Type": "Return",
                "Carrier": flight.find("Carrier").text,
                "FlightNumber": flight.find("FlightNumber").text,
                "Source": flight.find("Source").text,
                "Destination": flight.find("Destination").text,
                "DepartureTimeStamp": flight.find("DepartureTimeStamp").text,
                "ArrivalTimeStamp": flight.find("ArrivalTimeStamp").text,
                "Class": flight.find("Class").text,
                "NumberOfStops": int(flight.find("NumberOfStops").text),
                "FareBasis": flight.find("FareBasis").text.strip(),
                "TicketType": flight.find("TicketType").text,
            }
            data.append(flight_data)

        for charge in flights.findall(".//Pricing/ServiceCharges"):
            charge_type = charge.get("ChargeType")
            passenger_type = charge.get("type")
            amount = float(charge.text)
            pricing_data = {
                "Type": "Pricing",
                "PassengerType": passenger_type,
                "ChargeType": charge_type,
                "Amount": amount,
            }
            data.append(pricing_data)
    df = pd.DataFrame(data)
    return df


def compare_dataframes(df1, df2):
    """Сравнение двух DataFrame и вывод отличий."""
    differences = {}

    flights_df1 = df1[df1["Type"].isin(["Onward", "Return"])]
    flights_df2 = df2[df2["Type"].isin(["Onward", "Return"])]
    flights_diff = pd.concat([flights_df1, flights_df2]).drop_duplicates(keep=False)
    if not flights_diff.empty:
        differences['изменения в рейсах'] = flights_diff

    pricing_df1 = df1[df1["Type"] == "Pricing"]
    pricing_df2 = df2[df2["Type"] == "Pricing"]
    pricing_diff = pd.concat([pricing_df1, pricing_df2]).drop_duplicates(keep=False)
    if not pricing_diff.empty:
        differences['изменения в ценах'] = flights_diff

    return differences


with open("RS_Via-3.xml", "r", encoding="utf-8") as file:
    xml_content1 = file.read()

with open("RS_ViaOW.xml", "r", encoding="utf-8") as file:
    xml_content2 = file.read()

df1 = parse_flights_to_dataframe(xml_content1)
df2 = parse_flights_to_dataframe(xml_content2)

differences = compare_dataframes(df1, df2)

if differences:
    print("Найдены отличия:")
    for key, diff in differences.items():
        print(key)
        print(diff)

        # Запись в CSV
        filename = f"{key.replace(' ', '_').lower()}.csv"
        diff.to_csv(filename, index=False, encoding="utf-8")
        print(f"Результаты сохранены в файл: {filename}")

        excel_filename = f"{key.replace(' ', '_').lower()}.xlsx"
        diff.to_excel(excel_filename, index=False, engine="openpyxl")
        print(f"Результаты сохранены в Excel-файл: {excel_filename}")
else:
    print("Отличий не найдено.")