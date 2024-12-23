import random
import json
from typing import Dict
from datetime import datetime, timedelta

class MockYandexAPI:
    def __init__(self):
        try:
            with open('cities_data.json', 'r', encoding='utf-8') as file:
                self.cities_data = json.load(file)
            with open('sights_descriptions.json', 'r', encoding='utf-8') as file:
                self.sights_descriptions = json.load(file)
        except FileNotFoundError as e:
            print(f"Ошибка: Файл {e.filename} не найден")
            self.cities_data = {}
            self.sights_descriptions = {}
        except json.JSONDecodeError as e:
            print(f"Ошибка: Некорректный формат JSON файла: {e}")
            self.cities_data = {}
            self.sights_descriptions = {}

    def get_city_info(self, city: str) -> Dict:
        city = city.lower()
        if city not in self.cities_data:
            return None
        
        city_data = self.cities_data[city]
        return {
            "достопримечательности": city_data["достопримечательности"],
            "рестораны": city_data["рестораны"],
            "погода": {
                "температура": random.randint(
                    city_data["погода"]["температура_мин"],
                    city_data["погода"]["температура_макс"]
                ),
                "описание": random.choice(city_data["погода"]["описания"])
            }
        }

    def get_weather_and_time(self, city: str) -> Dict:
        city = city.lower()
        if city not in self.cities_data:
            return None
        
        city_data = self.cities_data[city]
        utc_now = datetime.utcnow()
        local_time = utc_now + timedelta(hours=city_data["часовой_пояс"])
        
        return {
            "погода": {
                "температура": random.randint(
                    city_data["погода"]["температура_мин"],
                    city_data["погода"]["температура_макс"]
                ),
                "описание": random.choice(city_data["погода"]["описания"])
            },
            "время": local_time.strftime("%H:%M"),
            "дата": local_time.strftime("%d.%m.%Y")
        }

    def get_transport_info(self, city: str) -> Dict:
        city = city.lower()
        if city not in self.cities_data:
            return None
        
        return self.cities_data[city]["транспорт"]

    def get_sights_info(self, city: str) -> Dict:
        city = city.lower()
        if city not in self.cities_data or city not in self.sights_descriptions:
            return None
        
        city_data = self.cities_data[city]
        sights_data = self.sights_descriptions[city]
        
        result = {
            "достопримечательности": []
        }
        
        for sight in city_data["достопримечательности"]:
            if sight in sights_data:
                sight_info = sights_data[sight].copy()
                sight_info["название"] = sight
                result["достопримечательности"].append(sight_info)
        
        return result

    def get_history_info(self, city: str) -> Dict:
        city = city.lower()
        if city not in self.cities_data:
            return None
        
        return self.cities_data[city]["история"]

    def get_events_info(self, city: str) -> Dict:
        city = city.lower()
        if city not in self.cities_data:
            return None
        
        return self.cities_data[city]["мероприятия"]