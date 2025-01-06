import tkinter as tk
from tkinter import ttk, messagebox
import requests

def download_stations():
    try:
        response = requests.get('https://api.gios.gov.pl/pjp-api/rest/station/findAll')
        response.raise_for_status()
        stations = response.json()

        if not stations:
            raise ValueError('Brak danych o stacjach')

        cities = sorted(list({station['city']['name'] for station in stations if station['city']}))
        return stations, cities
    except (requests.RequestException, ValueError) as error:
        messagebox.showerror('Błąd', f'Nie udało się pobrać danych o stacjach: {error}')
        return [], []

def update_stations(event):
    selected_city = city_combo.get() # pobieranie wybranego miasta
    city_stations = [station for station in stations if station['city'] and station['city']['name'] == selected_city]
    station_combo['values'] = [station['stationName'] for station in city_stations] # aktualizacja listy combo
    station_combo.current(0)

def download_data(station_id):
    try:
        response = requests.get(f'https://api.gios.gov.pl/pjp-api/rest/aqindex/getIndex/{station_id}')
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        messagebox.showerror('Błąd', f'Nie udało się pobrać danych o jakości powietrza: {error}')
        return {}

def show_data():
    selected_station = next((station for station in stations if station['stationName'] == station_combo.get()), None)

    if selected_station is None:
        messagebox.showerror('Błąd', f'Nie znaleziono wybranej stacji pomiarowej.')
        return

    data = download_data(selected_station['id'])

    if data:
        result = (
            f'Jakość powietrza: {data['stIndexLevel']['indexLevelName'] if data.get('stIndexLevel') else 'Brak danych'}\n'
            f'PM10: {data['pm10IndexLevel']['indexLevelName'] if data.get('pm10IndexLevel') else 'Brak danych'}\n'
            f'PM2.5: {data['pm25IndexLevel']['indexLevelName'] if data.get('pm25IndexLevel') else 'Brak danych'}\n'
            f'O3: {data['o3IndexLevel']['indexLevelName'] if data.get('o3IndexLevel') else 'Brak danych'}\n'
            f'NO2: {data['no2IndexLevel']['indexLevelName'] if data.get('no2IndexLevel') else 'Brak danych'}\n'
        )
        result_label.config(text=result)
    else:
        result_label.config(text='Brak danych')

root = tk.Tk()
root.title("Jakość Powietrza")
root.geometry("400x300")
root.configure(bg="#e0f7fa")

style = ttk.Style()
style.theme_use('clam')
style.configure('TLabel', font="Verdana, 12", background="#e0f7fa")
style.configure('TCombobox', font="Verdana, 12")
style.configure('TButton', font="Verdana 12 bold", background="#00796b", foreground="white")

stations, cities = download_stations()

city_label = ttk.Label(root, text='Wybierz miasto')
city_label.pack(pady=5)
city_combo = ttk.Combobox(root, values=cities)
city_combo.pack()

station_label = ttk.Label(root, text='Wybierz stację pomiarową')
station_label.pack(pady=5)
station_combo = ttk.Combobox(root)
station_combo.pack()

city_combo.bind('<<ComboboxSelected>>', update_stations)

download_btn = ttk.Button(root, text="Pobierz dane", command=show_data)
download_btn.pack(pady=10)

result_label = ttk.Label(root, text='', font="Verdana, 12")
result_label.pack(pady=10)

root.mainloop()