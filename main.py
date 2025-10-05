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
        
        if no2_level > 40:
            recommendations['general'].extend([
                "Evitar actividades al aire libre prolongadas",
                "Usar mascarilla en exteriores",
                "Mantener ventanas cerradas"
            ])
            recommendations['immediate_actions'].append("Activar protocolos de calidad del aire")
        elif no2_level > 20:
            recommendations['general'].extend([
                "Limitar actividades físicas intensas al aire libre",
                "Monitorear síntomas respiratorios"
            ])
        else:
            recommendations['general'].append("Calidad del aire aceptable, tomar precauciones normales")
        
        if 'schools' in vulnerable_groups:
            if no2_level > 35:
                recommendations['for_schools'].extend([
                    "Suspender educación física al aire libre",
                    "Mantener estudiantes en interiores durante recreo",
                    "Activar sistema de purificación de aire en aulas"
                ])
            elif no2_level > 20:
                recommendations['for_schools'].extend([
                    "Reducir tiempo de actividades al aire libre",
                    "Monitorear estudiantes con asma o condiciones respiratorias"
                ])
        
        if 'elderly' in vulnerable_groups:
            if no2_level > 30:
                recommendations['for_elderly'].extend([
                    "Evitar salidas no esenciales",
                    "Realizar ejercicios en interiores",
                    "Monitorear síntomas respiratorios"
                ])
            elif no2_level > 20:
                recommendations['for_elderly'].extend([
                    "Limitar tiempo al aire libre",
                    "Tener medicamentos respiratorios a mano"
                ])
        
        if 'hospitals' in vulnerable_groups:
            if no2_level > 30:
                recommendations['for_health_centers'].extend([
                    "Prepararse para posible aumento de casos respiratorios",
                    "Revisar inventario de medicamentos para asma",
                    "Alertar personal sobre condiciones ambientales"
                ])
        
        return recommendations

    def _classify_area(self, lat: float, lon: float) -> str:
        if abs(lat - 19.43) < 0.5 and abs(lon + 99.13) < 0.5:
            return "urban_center"
        elif abs(lat - 40.7) < 0.5 and abs(lon + 74.0) < 0.5:
            return "urban_center"
        elif abs(lat - 34.0) < 0.5 and abs(lon + 118.2) < 0.5:
            return "urban_center"
        elif abs(lat - 25.7) < 1.0 and abs(lon + 100.3) < 1.0:
            return "industrial"
        elif abs(lat - 32.5) < 1.0 and abs(lon + 117.0) < 1.0:
            return "industrial"
        else:
            return "residential"

    def _identify_vulnerable_groups(self, area_type: str) -> list:
        groups = ['children', 'elderly', 'asthmatics']
        
        if area_type == "urban_center":
            groups.extend(['schools', 'hospitals', 'outdoor_workers'])
        elif area_type == "industrial":
            groups.extend(['schools', 'low_income', 'outdoor_workers'])
        elif area_type == "residential":
            groups.extend(['schools', 'elderly_communities'])
            
        return groups

    def _calculate_risk_level(self, no2_level: float, area_type: str) -> str:
        base_risk = "Bajo"
        if no2_level > 60:
            base_risk = "Muy Alto"
        elif no2_level > 40:
            base_risk = "Alto"
        elif no2_level > 20:
            base_risk = "Moderado"
        
        if area_type in ["urban_center", "industrial"] and base_risk in ["Moderado", "Alto"]:
            return "Alto" if base_risk == "Moderado" else "Muy Alto"
            
        return base_risk

    def _generate_historical_trend(self, lat: float, lon: float):
        days = 7
        trend = []
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days-i-1)
            base_no2 = 10 + abs(lat) * 0.3 + np.sin(i * 0.5) * 8
            trend.append({
                'date': date.strftime('%Y-%m-%d'),
                'no2': round(max(5, base_no2 + np.random.normal(0, 3)), 2),
                'quality': self._calculate_quality(base_no2)
            })
        
        return trend

    def _generate_forecast(self, lat: float, lon: float):
        forecast = []
        current_hour = datetime.utcnow().hour
        
        for hour in range(24):
            future_hour = (current_hour + hour) % 24
            traffic_peak = 2.0 if (7 <= future_hour <= 9) or (17 <= future_hour <= 19) else 1.0
            base_no2 = 8 + abs(lat) * 0.3 * traffic_peak
            
            forecast.append({
                'hour': future_hour,
                'no2': round(max(5, base_no2 + np.random.normal(0, 2)), 2),
                'quality': self._calculate_quality(base_no2)
            })
        
        return forecast

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
        urban_factor = 2.5 if self._is_urban_area(lat, lon) else 1.0
        hour = datetime.utcnow().hour
        traffic_pattern = 1.0 + 0.5 * np.sin((hour - 8) * np.pi / 12)
        wind_speed = weather_data.get('wind_speed', 5)
        wind_factor = max(0.3, 1.0 - (wind_speed * 0.1))
        
        base_no2 = 8.0 + (abs(lat) * 0.3)
        final_no2 = base_no2 * urban_factor * traffic_pattern * wind_factor
        
        return {'no2': max(1.0, final_no2 + np.random.normal(0, 1.5))}

    def _is_urban_area(self, lat, lon):
        major_cities = [
            (19.43, -99.13),
            (40.7, -74.0),
            (34.0, -118.2),
            (25.7, -100.3),
            (32.5, -117.0)
        ]
        return any(abs(lat - city[0]) < 2 and abs(lon - city[1]) < 2 for city in major_cities)

    def _calculate_quality(self, no2_value):
        if no2_value < 20: return 'Buena'
        elif no2_value < 40: return 'Moderada'
        elif no2_value < 60: return 'Mala'
        else: return 'Muy Mala'

    def _calculate_aqi(self, no2_value):
        if no2_value < 20: return 25
        elif no2_value < 40: return 50
        elif no2_value < 60: return 75
        else: return 100

    def _get_weather_condition(self, weather_data):
        temp = weather_data.get('temperature', 20)
        if temp > 30: return "Caluroso"
        elif temp > 20: return "Templado"
        else: return "Frío"

    def _get_risk_factors(self, area_type, no2_level):
        factors = []
        if no2_level > 30:
            factors.append("Alta concentración de NO2")
        if area_type == "urban_center":
            factors.append("Alta densidad de tráfico")
        if area_type == "industrial":
            factors.append("Proximidad a zonas industriales")
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
        return {
            'air_quality': {
                'no2_tropospheric': 15.0,
                'pm25': 15.5,
                'quality_index': 'Moderada',
                'aqi_value': 50,
                'timestamp': datetime.utcnow().isoformat()
            },
            'weather': {
                'temperature': 22.0,
                'wind_speed': 5.0,
                'humidity': 60.0,
                'condition': 'Templado'
            },
            'vulnerability_analysis': {
                'area_type': 'residential',
                'risk_level': 'Moderado',
                'vulnerable_groups': ['children', 'elderly', 'schools'],
                'risk_factors': ['Datos limitados disponibles'],
                'protection_priority': 'Media'
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
