# Dokumentacja projetu: OBD II Telemetry App 

## Zespoł projetowy:
_Kacper Zoła_

## Opis projektu
Aplikacja służąca do analizy danych pozyskiwanych z urządzenia [_OBD II car data reader_](https://github.com/K4-pi/OBD-II-car-data-reader).

## Zakres projektu opis funkcjonalności:
- Komunikacje z urządzeniem pozyskującym dane (UART)
- Dynamiczna wizualizacja danych w formie _grafów_, _kart_ 
- Wyświetlanie punktów na mapie na podstawie danych z modułu GPS
- Generowanie raportu z pozyskanych danych

## Panele / zakładki aplikacji
![Current Data](images/main.png)

![Fuel Trim](images/trim.png)

## Funkcjonalność
- Dynamiczna analiza danych w formie grafów,
- Interaktywna mapa geograficzna
- Backend z baządanych do pobierania zdjęć dla mapy z pliku .mbtiles (Flask, SQLlite)
- Komunikacja z urządzeniem ESP32 poprzez protokół UART
- Generowanie raprotu z zebranych danych do formatu .svg

## Wykorzystane biblioteki:
- PyQt6    -> GUI
- PyQtGraph  -> Tworzenie grafów danych 
- QSerialPort -> Komunikacja z urządzeniem zczytającym dane
- QtWebEngineWidgets -> Wyświetlanie mapy GPS
- Flask + Sqlite -> Lokalna komunikacja z bazą danych dla mapy GPS
- QtSvg -> Generowanie raportu .svg
- vininfo -> Analiza numeru VIN samochodu

## Instrukcja uruchomienia aplikacji
Aplikacje można uruchomić poprzez użycie interpretera python na plik _main.py_.

```bash
python main.py
```

Domyślną mapą jest mapa Podkarpacia jako plik _src/map/telemetry_map.mbtiles_, w celu zmiany mapy należy pobrać ją z internetu i zastąpić ją tą samą nazwą.
