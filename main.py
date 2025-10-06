from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import numpy as np
from datetime import datetime, timedelta
import json

app = FastAPI(title="La Chica del Clima - NASA TEMPO", 
              description="Dashboard para protección de poblaciones vulnerables ante la contaminación del aire")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

class AdvancedTempoProcessor:
    def __init__(self):
        self.openaq_url = "https://api.openaq.org/v2/latest"
        self.weather_url = "https://api.open-meteo.com/v1/forecast"
        self.cache = {}
        self.cache_ttl = 300
    
    def get_air_quality_dashboard(self, lat: float, lon: float):
        cache_key = f"{round(lat, 2)}_{round(lon, 2)}"
        
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.utcnow() - timestamp).seconds < self.cache_ttl:
                return cached_data
        
        try:
            openaq_data = self._get_openaq_data(lat, lon)
            weather_data = self._get_weather_data(lat, lon)
            
            tempo_simulation = self._simulate_tempo_advanced(lat, lon, weather_data)
            
            vulnerability_analysis = self._analyze_vulnerability(lat, lon, tempo_simulation['no2'])
            
            recommendations = self._generate_recommendations(
                tempo_simulation['no2'], 
                vulnerability_analysis['risk_level'],
                vulnerability_analysis['vulnerable_groups']
            )
            
            historical_trend = self._generate_historical_trend(lat, lon)
            
            result = {
                'air_quality': {
                    'no2_tropospheric': round(tempo_simulation['no2'], 2),
                    'pm25': openaq_data.get('pm25', 15.5),
                    'quality_index': self._calculate_quality(tempo_simulation['no2']),
                    'aqi_value': self._calculate_aqi(tempo_simulation['no2']),
                    'timestamp': datetime.utcnow().isoformat()
                },
                
                'weather': {
                    'temperature': weather_data.get('temperature'),
                    'wind_speed': weather_data.get('wind_speed'),
                    'humidity': weather_data.get('humidity'),
                    'condition': self._get_weather_condition(weather_data)
                },
                
                'vulnerability_analysis': vulnerability_analysis,
                
                'recommendations': recommendations,
                
                'visualization_data': {
                    'historical_trend': historical_trend,
                    'forecast': self._generate_forecast(lat, lon),
                    'risk_map': self._generate_risk_map_data(lat, lon)
                },
                
                'metadata': {
                    'data_source': 'NASA TEMPO Simulation + OpenAQ + Open-Meteo',
                    'location': f"{lat}, {lon}",
                    'last_updated': datetime.utcnow().isoformat(),
                    'resolution': '2km x 5.5km'
                }
            }
            
            self.cache[cache_key] = (result, datetime.utcnow())
            
            return result
            
        except Exception as e:
            print(f"Error en get_air_quality_dashboard: {str(e)}")
            return self._get_fallback_dashboard(lat, lon)

    def _analyze_vulnerability(self, lat: float, lon: float, no2_level: float):
        area_type = self._classify_area(lat, lon)
        vulnerable_groups = self._identify_vulnerable_groups(area_type)
        risk_level = self._calculate_risk_level(no2_level, area_type)
        
        return {
            'area_type': area_type,
            'vulnerable_groups': vulnerable_groups,
            'risk_level': risk_level,
            'risk_factors': self._get_risk_factors(area_type, no2_level),
            'protection_priority': 'Alta' if risk_level in ['Alto', 'Muy Alto'] else 'Media'
        }

    def _generate_recommendations(self, no2_level: float, risk_level: str, vulnerable_groups: list):
        recommendations = {
            'general': [],
            'for_schools': [],
            'for_elderly': [],
            'for_health_centers': [],
            'immediate_actions': []
        }
        
        if no2_level > 80:
            recommendations['general'].extend([
                "Evitar actividades al aire libre prolongadas",
                "Usar mascarilla en exteriores",
                "Mantener ventanas cerradas"
            ])
            recommendations['immediate_actions'].append("Activar protocolos de calidad del aire")
        elif no2_level > 50:
            recommendations['general'].extend([
                "Limitar actividades físicas intensas al aire libre",
                "Monitorear síntomas respiratorios"
            ])
        else:
            recommendations['general'].append("Calidad del aire aceptable, tomar precauciones normales")
        
        if 'schools' in vulnerable_groups:
            if no2_level > 70:
                recommendations['for_schools'].extend([
                    "Suspender educación física al aire libre",
                    "Mantener estudiantes en interiores durante recreo",
                    "Activar sistema de purificación de aire en aulas"
                ])
            elif no2_level > 50:
                recommendations['for_schools'].extend([
                    "Reducir tiempo de actividades al aire libre",
                    "Monitorear estudiantes con asma o condiciones respiratorias"
                ])
        
        if 'elderly' in vulnerable_groups:
            if no2_level > 60:
                recommendations['for_elderly'].extend([
                    "Evitar salidas no esenciales",
                    "Realizar ejercicios en interiores",
                    "Monitorear síntomas respiratorios"
                ])
            elif no2_level > 50:
                recommendations['for_elderly'].extend([
                    "Limitar tiempo al aire libre",
                    "Tener medicamentos respiratorios a mano"
                ])
        
        if 'hospitals' in vulnerable_groups:
            if no2_level > 60:
                recommendations['for_health_centers'].extend([
                    "Prepararse para posible aumento de casos respiratorios",
                    "Revisar inventario de medicamentos para asma",
                    "Alertar personal sobre condiciones ambientales"
                ])
        
        return recommendations

    def _classify_area(self, lat: float, lon: float) -> str:
        if abs(lat - 19.43) < 0.5 and abs(lon + 99.13) < 0.5:
            return "urban_center_high"
        elif abs(lat - 40.7) < 0.5 and abs(lon + 74.0) < 0.5:
            return "urban_center"
        elif abs(lat - 34.0) < 0.5 and abs(lon + 118.2) < 0.5:
            return "urban_center_high"
        elif abs(lat - 25.7) < 1.0 and abs(lon + 100.3) < 1.0:
            return "industrial_heavy"
        elif abs(lat - 32.5) < 1.0 and abs(lon + 117.0) < 1.0:
            return "industrial"
        elif abs(lat - 28.6) < 1.0 and abs(lon - 77.2) < 1.0:
            return "urban_center_extreme"
        elif abs(lat - 39.9) < 1.0 and abs(lon - 116.4) < 1.0:
            return "urban_center_extreme"
        elif self._is_major_urban(lat, lon):
            return "urban_center"
        else:
            return "residential"

    def _is_major_urban(self, lat, lon):
        return abs(lat) > 10 and abs(lat) < 60

    def _identify_vulnerable_groups(self, area_type: str) -> list:
        groups = ['children', 'elderly', 'asthmatics']
        
        if area_type in ["urban_center_high", "urban_center_extreme"]:
            groups.extend(['schools', 'hospitals', 'outdoor_workers', 'low_income'])
        elif area_type == "urban_center":
            groups.extend(['schools', 'hospitals', 'outdoor_workers'])
        elif area_type in ["industrial", "industrial_heavy"]:
            groups.extend(['schools', 'low_income', 'outdoor_workers'])
        elif area_type == "residential":
            groups.extend(['schools', 'elderly_communities'])
            
        return groups

    def _calculate_risk_level(self, no2_level: float, area_type: str) -> str:
        base_risk = "Bajo"
        if no2_level > 150:
            base_risk = "Muy Alto"
        elif no2_level > 100:
            base_risk = "Alto"
        elif no2_level > 50:
            base_risk = "Moderado"
        
        if area_type in ["urban_center_extreme", "industrial_heavy"]:
            if base_risk == "Bajo":
                return "Moderado"
            elif base_risk == "Moderado":
                return "Alto"
            elif base_risk == "Alto":
                return "Muy Alto"
        elif area_type in ["urban_center_high", "industrial"]:
            if base_risk == "Bajo":
                return "Moderado"
            elif base_risk == "Moderado":
                return "Alto"
            
        return base_risk

    def _generate_historical_trend(self, lat, lon):
        days = 7
        trend = []
        area_type = self._classify_area(lat, lon)
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days-i-1)
            base_no2 = self._get_base_no2_for_area(lat, lon, area_type)
            daily_variation = np.sin(i * 0.8) * 15 + np.random.normal(0, 8)
            no2_value = max(10, base_no2 + daily_variation)
            
            trend.append({
                'date': date.strftime('%Y-%m-%d'),
                'no2': round(no2_value, 2),
                'quality': self._calculate_quality(no2_value)
            })
        
        return trend

    def _generate_forecast(self, lat: float, lon: float):
        forecast = []
        current_hour = datetime.utcnow().hour
        area_type = self._classify_area(lat, lon)
        base_no2 = self._get_base_no2_for_area(lat, lon, area_type)
        
        for hour in range(24):
            future_hour = (current_hour + hour) % 24
            traffic_peak = 1.0
            if 7 <= future_hour <= 9:
                traffic_peak = 1.8
            elif 17 <= future_hour <= 20:
                traffic_peak = 1.9
            elif 12 <= future_hour <= 14:
                traffic_peak = 1.3
            elif 23 <= future_hour or future_hour <= 5:
                traffic_peak = 0.6
            
            hourly_no2 = base_no2 * traffic_peak + np.random.normal(0, 5)
            
            forecast.append({
                'hour': future_hour,
                'no2': round(max(10, hourly_no2), 2),
                'quality': self._calculate_quality(hourly_no2)
            })
        
        return forecast

    def _get_base_no2_for_area(self, lat, lon, area_type):
        if area_type == "urban_center_extreme":
            return 120 + np.random.normal(0, 20)
        elif area_type == "urban_center_high":
            return 80 + np.random.normal(0, 15)
        elif area_type == "industrial_heavy":
            return 90 + np.random.normal(0, 15)
        elif area_type == "urban_center":
            return 60 + np.random.normal(0, 12)
        elif area_type == "industrial":
            return 70 + np.random.normal(0, 12)
        else:
            return 30 + np.random.normal(0, 8)

    def _get_openaq_data(self, lat, lon, radius=50000):
        try:
            params = {
                'coordinates': f"{lat},{lon}",
                'radius': radius,
                'limit': 1
            }
            response = requests.get(self.openaq_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    measurements = data['results'][0].get('measurements', [])
                    pm25 = next((m['value'] for m in measurements if m['parameter'] == 'pm25'), None)
                    if pm25:
                        return {'pm25': round(pm25, 2)}
            return {}
        except Exception as e:
            print(f"Error al obtener datos de OpenAQ: {str(e)}")
            return {}

    def _get_weather_data(self, lat, lon):
        try:
            params = {
                'latitude': lat,
                'longitude': lon,
                'current_weather': 'true',
                'hourly': 'relative_humidity_2m'
            }
            response = requests.get(self.weather_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                current = data.get('current_weather', {})
                hourly = data.get('hourly', {})
                humidity_list = hourly.get('relative_humidity_2m', [60])
                return {
                    'temperature': round(current.get('temperature', 20), 1),
                    'wind_speed': round(current.get('windspeed', 5), 1),
                    'humidity': round(humidity_list[0] if humidity_list else 60, 1)
                }
            return {}
        except Exception as e:
            print(f"Error al obtener datos meteorológicos: {str(e)}")
            return {}

    def _simulate_tempo_advanced(self, lat, lon, weather_data):
        area_type = self._classify_area(lat, lon)
        
        urban_factor_map = {
            "urban_center_extreme": 4.5,
            "urban_center_high": 3.2,
            "urban_center": 2.0,
            "industrial_heavy": 3.5,
            "industrial": 2.5,
            "residential": 1.0
        }
        urban_factor = urban_factor_map.get(area_type, 1.0)
        
        hour = datetime.utcnow().hour
        if 7 <= hour <= 9 or 17 <= hour <= 20:
            traffic_pattern = 1.8
        elif 12 <= hour <= 14:
            traffic_pattern = 1.3
        elif 23 <= hour or hour <= 5:
            traffic_pattern = 0.6
        else:
            traffic_pattern = 1.0
        
        wind_speed = weather_data.get('wind_speed', 5)
        if wind_speed > 15:
            wind_factor = 0.5
        elif wind_speed > 10:
            wind_factor = 0.7
        elif wind_speed > 5:
            wind_factor = 0.85
        else:
            wind_factor = 1.0
        
        temp = weather_data.get('temperature', 20)
        if temp < 10:
            temp_factor = 1.3
        elif temp > 30:
            temp_factor = 1.2
        else:
            temp_factor = 1.0
        
        base_no2 = self._get_base_no2_for_area(lat, lon, area_type)
        
        final_no2 = base_no2 * urban_factor * traffic_pattern * wind_factor * temp_factor
        
        final_no2 = final_no2 + np.random.normal(0, 3)
        
        return {'no2': max(5.0, final_no2)}

    def _is_urban_area(self, lat, lon):
        major_cities = [
            (19.43, -99.13),
            (40.7, -74.0),
            (34.0, -118.2),
            (25.7, -100.3),
            (32.5, -117.0),
            (28.6, 77.2),
            (39.9, 116.4),
        ]
        return any(abs(lat - city[0]) < 2 and abs(lon - city[1]) < 2 for city in major_cities)

    def _calculate_quality(self, no2_value):
        if no2_value < 40:
            return 'Buena'
        elif no2_value < 80:
            return 'Moderada'
        elif no2_value < 120:
            return 'Mala'
        elif no2_value < 160:
            return 'Muy Mala'
        else:
            return 'Peligrosa'

    def _calculate_aqi(self, no2_value):
        if no2_value < 40:
            return int(no2_value * 1.25)
        elif no2_value < 80:
            return int(50 + (no2_value - 40) * 1.25)
        elif no2_value < 120:
            return int(100 + (no2_value - 80) * 1.5)
        elif no2_value < 160:
            return int(150 + (no2_value - 120) * 2)
        else:
            return min(300, int(200 + (no2_value - 160) * 2.5))

    def _get_weather_condition(self, weather_data):
        temp = weather_data.get('temperature', 20)
        if temp > 30: return "Caluroso"
        elif temp > 20: return "Templado"
        else: return "Frío"

    def _get_risk_factors(self, area_type, no2_level):
        factors = []
        if no2_level > 80:
            factors.append("Alta concentración de NO2")
        if no2_level > 120:
            factors.append("Niveles peligrosos de contaminación")
        if area_type in ["urban_center_high", "urban_center_extreme"]:
            factors.append("Alta densidad de tráfico vehicular")
        if area_type in ["industrial", "industrial_heavy"]:
            factors.append("Proximidad a zonas industriales")
        if area_type == "urban_center_extreme":
            factors.append("Zona crítica de contaminación")
        if not factors:
            factors.append("Condiciones normales")
        return factors

    def _generate_risk_map_data(self, lat, lon):
        return {
            'center': [lat, lon],
            'risk_zones': [
                {
                    'coords': [lat + 0.01, lon + 0.01],
                    'risk': 'high',
                    'radius': 1000
                }
            ]
        }

    def _get_fallback_dashboard(self, lat, lon):
        area_type = self._classify_area(lat, lon)
        fallback_no2 = self._get_base_no2_for_area(lat, lon, area_type)
        
        return {
            'air_quality': {
                'no2_tropospheric': round(fallback_no2, 2),
                'pm25': 15.5,
                'quality_index': self._calculate_quality(fallback_no2),
                'aqi_value': self._calculate_aqi(fallback_no2),
                'timestamp': datetime.utcnow().isoformat()
            },
            'weather': {
                'temperature': 22.0,
                'wind_speed': 5.0,
                'humidity': 60.0,
                'condition': 'Templado'
            },
            'vulnerability_analysis': {
                'area_type': area_type,
                'risk_level': self._calculate_risk_level(fallback_no2, area_type),
                'vulnerable_groups': self._identify_vulnerable_groups(area_type),
                'risk_factors': self._get_risk_factors(area_type, fallback_no2),
                'protection_priority': 'Alta' if fallback_no2 > 80 else 'Media'
            },
            'recommendations': {
                'general': ['Monitorear calidad del aire', 'Evitar zonas de alto tráfico'],
                'for_schools': ['Limitar recreo al aire libre si la calidad empeora'],
                'for_elderly': ['Tomar precauciones normales'],
                'for_health_centers': ['Estar preparado para consultas respiratorias'],
                'immediate_actions': []
            },
            'visualization_data': {
                'historical_trend': self._generate_historical_trend(lat, lon),
                'forecast': self._generate_forecast(lat, lon),
                'risk_map': self._generate_risk_map_data(lat, lon)
            },
            'metadata': {
                'data_source': 'Fallback data',
                'location': f"{lat}, {lon}",
                'last_updated': datetime.utcnow().isoformat(),
                'resolution': '2km x 5.5km'
            }
        }

processor = AdvancedTempoProcessor()

@app.get("/api/dashboard")
async def get_dashboard_data(lat: float, lon: float):
    try:
        data = processor.get_air_quality_dashboard(lat, lon)
        return data
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail="Error al conectar con las APIs externas.")
    except Exception as e:
        print(f"Error en endpoint /api/dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "La Chica del Clima API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
