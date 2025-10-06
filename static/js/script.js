document.addEventListener('DOMContentLoaded', () => {
    let map;
    window.currentData = {};

    const configForm = document.getElementById('configForm');
    const latitudeInput = document.getElementById('latitude');
    const longitudeInput = document.getElementById('longitude');
    const personaRadios = document.querySelectorAll('input[name="persona"]');
    const evaluarBtn = document.getElementById('evaluarBtn');

    const no2ValueSpan = document.getElementById('no2Value');
    const pm25ValueSpan = document.getElementById('pm25Value');
    const qualityIndexSpan = document.getElementById('qualityIndex');
    const aqiValueSpan = document.getElementById('aqiValue');
    const lastUpdatedAQISpan = document.getElementById('lastUpdatedAQI');

    const temperatureSpan = document.getElementById('temperature');
    const windSpeedSpan = document.getElementById('windSpeed');
    const humiditySpan = document.getElementById('humidity');
    const weatherConditionSpan = document.getElementById('weatherCondition');

    const areaTypeSpan = document.getElementById('areaType');
    const riskLevelSpan = document.getElementById('riskLevel');
    const vulnerableGroupsSpan = document.getElementById('vulnerableGroups');
    const riskFactorsSpan = document.getElementById('riskFactors');
    const protectionPrioritySpan = document.getElementById('protectionPriority');

    const selectedPersonaSpan = document.getElementById('selectedPersona');
    const generalRecommendationsList = document.querySelector('#generalRecommendations .recommendation-list');
    const specificRecommendationsDiv = document.getElementById('specificRecommendations');
    const immediateActionsList = document.querySelector('#immediateActions .recommendation-list');

    let historicalChartInstance = null;
    let forecastChartInstance = null;

    // Función para obtener recomendaciones personalizadas
    const getCustomRecommendations = (selectedPersona, airQualityIndex) => {
        const recommendations = {
            children: {
                'Buena': {
                    general: ['Perfecto para jugar al aire libre', 'Disfrutar actividades deportivas sin restricción'],
                    specific: ['Ideal para recreos escolares prolongados', 'Pueden realizar educación física normal'],
                    immediate: []
                },
                'Moderada': {
                    general: ['Reducir actividades intensas al aire libre', 'Preferir juegos en interiores'],
                    specific: ['Limitar recreos a 20-30 minutos', 'Evitar deportes de alta intensidad'],
                    immediate: ['Supervisar a niños con asma de cerca']
                },
                'Mala': {
                    general: ['Evitar juegos al aire libre', 'Mantener ventanas cerradas'],
                    specific: ['Cancelar clases de educación física', 'Recreos solo en interiores'],
                    immediate: ['Contactar a padres de niños vulnerables', 'Tener inhaladores disponibles']
                },
                'Muy Mala': {
                    general: ['Permanecer en interiores', 'No salir bajo ninguna circunstancia'],
                    specific: ['Suspender clases presenciales si es posible', 'Cerrar escuelas en zonas críticas'],
                    immediate: ['Evacuación inmediata de niños con problemas respiratorios', 'Activar protocolo de emergencia escolar']
                }
            },
            elderly: {
                'Buena': {
                    general: ['Disfrute de caminatas tranquilas', 'Ventile su hogar normalmente'],
                    specific: ['Puede realizar ejercicio ligero al aire libre', 'Ideal para paseos matutinos'],
                    immediate: []
                },
                'Moderada': {
                    general: ['Reduzca el tiempo al aire libre', 'Evite esfuerzos físicos'],
                    specific: ['Caminatas cortas de máximo 15 minutos', 'Preferir horarios de menor contaminación'],
                    immediate: ['Tenga sus medicamentos a mano']
                },
                'Mala': {
                    general: ['Permanezca en interiores', 'Use purificadores de aire'],
                    specific: ['Cancele actividades al aire libre', 'Monitoree síntomas respiratorios'],
                    immediate: ['Contacte a su médico si siente molestias', 'Tenga oxígeno disponible si lo requiere']
                },
                'Muy Mala': {
                    general: ['No salga de casa', 'Selle puertas y ventanas'],
                    specific: ['Considere reubicación temporal', 'Monitoreo médico constante'],
                    immediate: ['Llame a emergencias si tiene dificultad para respirar', 'Active red de apoyo familiar']
                }
            },
            adults: {
                'Buena': {
                    general: ['Condiciones ideales para actividades normales', 'Ejercicio sin restricciones'],
                    specific: ['Puede hacer deportes intensos', 'Ideal para actividades al aire libre'],
                    immediate: []
                },
                'Moderada': {
                    general: ['Reduzca ejercicio intenso prolongado', 'Monitoree su respiración'],
                    specific: ['Limite entrenamientos a 45 minutos', 'Evite horas pico de tráfico'],
                    immediate: []
                },
                'Mala': {
                    general: ['Evite ejercicio al aire libre', 'Use cubrebocas N95 si debe salir'],
                    specific: ['Ejercicio solo en gimnasios cerrados', 'Trabaje desde casa si es posible'],
                    immediate: ['Tenga antihistamínicos disponibles']
                },
                'Muy Mala': {
                    general: ['Permanezca en interiores', 'Cierre ventanas y puertas'],
                    specific: ['No salga salvo emergencia', 'Use purificadores de aire'],
                    immediate: ['Use mascarilla N95 si debe salir', 'Evite cualquier esfuerzo físico']
                }
            },
            asthmatics: {
                'Buena': {
                    general: ['Condiciones seguras', 'Puede realizar actividades normales'],
                    specific: ['Lleve su inhalador de rescate', 'Ejercicio moderado permitido'],
                    immediate: []
                },
                'Moderada': {
                    general: ['Limite actividades al aire libre', 'Esté alerta a síntomas'],
                    specific: ['Use inhalador preventivo antes de salir', 'Evite áreas con mucho tráfico'],
                    immediate: ['Tenga su plan de acción para asma listo']
                },
                'Mala': {
                    general: ['Permanezca en interiores', 'No haga ejercicio'],
                    specific: ['Use inhalador preventivo cada 4-6 horas', 'Evite cualquier irritante adicional'],
                    immediate: ['Contacte a su médico', 'Tenga medicamento de emergencia disponible']
                },
                'Muy Mala': {
                    general: ['Alerta máxima', 'No salga bajo ninguna circunstancia'],
                    specific: ['Monitoreo constante de saturación de oxígeno', 'Aumente dosis preventiva según indicación médica'],
                    immediate: ['Vaya a urgencias si tiene sibilancias o dificultad respiratoria', 'Tenga nebulizador listo']
                }
            },
            outdoor_workers: {
                'Buena': {
                    general: ['Trabajo normal sin restricciones', 'Manténgase hidratado'],
                    specific: ['Puede laborar jornada completa', 'Use protección solar'],
                    immediate: []
                },
                'Moderada': {
                    general: ['Reduzca ritmo de trabajo', 'Tome descansos frecuentes'],
                    specific: ['Limite trabajos pesados a 6 horas', 'Use cubrebocas en áreas con polvo'],
                    immediate: ['Tenga agua disponible constantemente']
                },
                'Mala': {
                    general: ['Suspenda trabajos no esenciales', 'Use equipo de protección'],
                    specific: ['Mascarilla N95 obligatoria', 'Turnos reducidos a 4 horas máximo'],
                    immediate: ['Reporte síntomas respiratorios inmediatamente', 'Trabajos críticos solo con protección completa']
                },
                'Muy Mala': {
                    general: ['Suspenda labores al aire libre', 'Emergencia laboral'],
                    specific: ['Solo personal de emergencia con equipo especializado', 'Reubique operaciones a interiores'],
                    immediate: ['Evacue área si es posible', 'Atención médica para cualquier síntoma']
                }
            },
            schools: {
                'Buena': {
                    general: ['Actividades escolares normales', 'Ventilación natural adecuada'],
                    specific: ['Educación física sin restricción', 'Recreos prolongados permitidos'],
                    immediate: []
                },
                'Moderada': {
                    general: ['Limitar actividades al aire libre', 'Monitorear estudiantes sensibles'],
                    specific: ['Reducir tiempo de recreo a 20 minutos', 'Educación física moderada'],
                    immediate: ['Notificar a padres de niños vulnerables']
                },
                'Mala': {
                    general: ['Suspender actividades al aire libre', 'Cerrar ventanas'],
                    specific: ['Cancelar educación física', 'Recreos solo en interiores'],
                    immediate: ['Activar protocolo de calidad del aire', 'Contactar autoridades de salud']
                },
                'Muy Mala': {
                    general: ['Considerar cierre temporal', 'Clases virtuales'],
                    specific: ['Suspensión de clases presenciales', 'Solo personal administrativo esencial'],
                    immediate: ['Notificación inmediata a padres', 'Coordinación con autoridades educativas']
                }
            },
            hospitals: {
                'Buena': {
                    general: ['Operación normal', 'Ventilación estándar'],
                    specific: ['Pacientes pueden usar áreas exteriores', 'Visitas sin restricción'],
                    immediate: []
                },
                'Moderada': {
                    general: ['Monitoreo aumentado', 'Reforzar filtración de aire'],
                    specific: ['Limitar tiempo de pacientes en exteriores', 'Alertar a pacientes respiratorios'],
                    immediate: ['Aumentar disponibilidad de inhaladores y oxígeno']
                },
                'Mala': {
                    general: ['Protocolo de emergencia ambiental', 'Sellado de instalaciones'],
                    specific: ['Prohibir salidas de pacientes', 'Reforzar UCI y urgencias'],
                    immediate: ['Preparar para aumento de consultas respiratorias', 'Activar equipo de respuesta']
                },
                'Muy Mala': {
                    general: ['Alerta máxima hospitalaria', 'Plan de contingencia total'],
                    specific: ['Solo ingresos de emergencia', 'Máxima capacidad de atención respiratoria'],
                    immediate: ['Coordinar con otros hospitales', 'Solicitar apoyo gubernamental']
                }
            }
        };

        const personaRecs = recommendations[selectedPersona];
        if (!personaRecs || !personaRecs[airQualityIndex]) {
            return {
                general: ['No hay recomendaciones disponibles para esta combinación'],
                specific: [],
                immediate: []
            };
        }

        const recs = personaRecs[airQualityIndex];
        return {
            general: recs.general,
            for_schools: recs.specific,
            for_elderly: recs.specific,
            for_health_centers: recs.specific,
            immediate_actions: recs.immediate
        };
    };

    const updateRecommendations = (recommendations, selectedPersona) => {
        generalRecommendationsList.innerHTML = '';
        specificRecommendationsDiv.innerHTML = '';
        immediateActionsList.innerHTML = '';

        if (recommendations.general && recommendations.general.length > 0) {
            recommendations.general.forEach(rec => {
                const li = document.createElement('li');
                li.textContent = rec;
                generalRecommendationsList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'No hay recomendaciones generales en este momento.';
            generalRecommendationsList.appendChild(li);
        }

        const personaKeyMap = {
            'children': 'for_schools',
            'elderly': 'for_elderly',
            'schools': 'for_schools',
            'hospitals': 'for_health_centers',
            'asthmatics': 'general',
            'outdoor_workers': 'general',
            'adults': 'general'
        };

        const recommendationKey = personaKeyMap[selectedPersona] || 'general';
        const specificRecs = recommendations[recommendationKey];

        if (specificRecs && specificRecs.length > 0) {
            const h4 = document.createElement('h4');
            h4.textContent = `Específicas para ${getPersonaDisplayName(selectedPersona)}:`;
            specificRecommendationsDiv.appendChild(h4);

            const ul = document.createElement('ul');
            ul.className = 'recommendation-list';
            specificRecs.forEach(rec => {
                const li = document.createElement('li');
                li.textContent = rec;
                ul.appendChild(li);
            });
            specificRecommendationsDiv.appendChild(ul);
        }

        if (recommendations.immediate_actions && recommendations.immediate_actions.length > 0) {
            recommendations.immediate_actions.forEach(action => {
                const li = document.createElement('li');
                li.textContent = action;
                li.style.fontWeight = 'bold';
                li.style.borderLeftColor = '#FFC107';
                immediateActionsList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'No hay acciones inmediatas requeridas.';
            immediateActionsList.appendChild(li);
        }
    };

    const fetchDashboardData = async () => {
        const lat = latitudeInput.value;
        const lon = longitudeInput.value;
        const selectedPersona = document.querySelector('input[name="persona"]:checked').value;

        selectedPersonaSpan.textContent = getPersonaDisplayName(selectedPersona);

        if (!lat || !lon) {
            alert('Por favor, ingresa la latitud y longitud.');
            return;
        }

        try {
            evaluarBtn.disabled = true;
            evaluarBtn.textContent = 'Cargando datos...';

            const response = await fetch(`/api/dashboard?lat=${lat}&lon=${lon}`);
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            const data = await response.json();
            console.log('Datos recibidos del backend:', data);

            window.currentData = data;

            const parsedLat = parseFloat(lat) || 19.43;
            const parsedLon = parseFloat(lon) || -99.13;
            const riskMapData = data.visualization_data?.risk_map || { 
                center: [parsedLat, parsedLon], 
                risk_zones: []
            };

            initializeMap(riskMapData.center[0], riskMapData.center[1], riskMapData.risk_zones);

            no2ValueSpan.textContent = data.air_quality.no2_tropospheric;
            pm25ValueSpan.textContent = data.air_quality.pm25 || 'N/D';
            qualityIndexSpan.textContent = data.air_quality.quality_index;
            aqiValueSpan.textContent = data.air_quality.aqi_value;
            lastUpdatedAQISpan.textContent = new Date(data.air_quality.timestamp).toLocaleString();

            aqiValueSpan.className = '';
            qualityIndexSpan.className = '';
            switch (data.air_quality.quality_index) {
                case 'Buena':
                    aqiValueSpan.classList.add('quality-good');
                    qualityIndexSpan.classList.add('quality-good');
                    break;
                case 'Moderada':
                    aqiValueSpan.classList.add('quality-moderate');
                    qualityIndexSpan.classList.add('quality-moderate');
                    break;
                case 'Mala':
                    aqiValueSpan.classList.add('quality-bad');
                    qualityIndexSpan.classList.add('quality-bad');
                    break;
                case 'Muy Mala':
                    aqiValueSpan.classList.add('quality-very-bad');
                    qualityIndexSpan.classList.add('quality-very-bad');
                    break;
            }

            temperatureSpan.textContent = data.weather.temperature || 'N/D';
            windSpeedSpan.textContent = data.weather.wind_speed || 'N/D';
            humiditySpan.textContent = data.weather.humidity || 'N/D';
            weatherConditionSpan.textContent = data.weather.condition || 'N/D';

            areaTypeSpan.textContent = data.vulnerability_analysis.area_type || 'N/D';
            riskLevelSpan.textContent = data.vulnerability_analysis.risk_level || 'N/D';
            vulnerableGroupsSpan.textContent = (data.vulnerability_analysis.vulnerable_groups || [])
                .map(g => getPersonaDisplayName(g)).join(', ') || 'N/D';
            riskFactorsSpan.textContent = (data.vulnerability_analysis.risk_factors || []).join(', ') || 'N/D';
            protectionPrioritySpan.textContent = data.vulnerability_analysis.protection_priority || 'N/D';

            const customRecs = getCustomRecommendations(selectedPersona, data.air_quality.quality_index);
            updateRecommendations(customRecs, selectedPersona);

            renderCharts(data.visualization_data.historical_trend, data.visualization_data.forecast);

        } catch (error) {
            console.error('Error al obtener los datos del dashboard:', error);
            alert('No se pudieron cargar los datos del dashboard. Inténtalo de nuevo más tarde.');
        } finally {
            evaluarBtn.disabled = false;
            evaluarBtn.textContent = 'Obtener Datos';
        }
    };

    const initializeMap = (lat, lon, riskZones) => {
        if (map) {
            map.remove();
        }
        
        map = L.map('map').setView([lat, lon], 13);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors | Datos simulados de NASA TEMPO & OpenAQ'
        }).addTo(map);
        
        const mainMarker = L.marker([lat, lon]).addTo(map);
        mainMarker.bindPopup(`
            <b>Ubicación Principal</b><br>
            Lat: ${lat.toFixed(4)}<br>
            Lon: ${lon.toFixed(4)}<br>
            NO2 Actual: ${getNo2FromData().toFixed(1)} ppb<br>
            Riesgo General: ${getRiskText()}
        `).openPopup();
        
        riskZones.forEach((zone, index) => {
            const circle = L.circle([zone.coords[0], zone.coords[1]], {
                color: getRiskColor(zone.risk),
                fillColor: getRiskColor(zone.risk),
                fillOpacity: 0.6,
                radius: zone.radius || 500,
                weight: 2
            }).addTo(map);
            
            circle.bindPopup(`
                <b>Zona de Riesgo ${index + 1}</b><br>
                Nivel: ${zone.risk.toUpperCase()}<br>
                Radio: ${zone.radius || 500}m<br>
                Recomendación: ${getZoneRecommendation(zone.risk)}
            `);
        });
        
        const mapInfo = document.getElementById('map-info');
        if (mapInfo) {
            mapInfo.innerHTML = `
                <strong>Mapa actualizado para ${lat.toFixed(4)}, ${lon.toFixed(4)}.</strong><br>
                ${riskZones.length} zonas de riesgo detectadas. Zoom y pan para explorar.
            `;
        }
        
        const mapSection = document.getElementById('map-section');
        if (mapSection) {
            mapSection.style.display = 'block';
        }
    };

    const getRiskColor = (risk) => {
        switch (risk) {
            case 'high': return '#FF0000';
            case 'medium': return '#FFA500';
            case 'low': return '#00FF00';
            default: return '#20B2AA';
        }
    };

    const getNo2FromData = () => {
        return window.currentData?.air_quality?.no2_tropospheric || 25.5;
    };

    const getRiskText = () => {
        return window.currentData?.vulnerability_analysis?.risk_level || 'Bajo';
    };

    const getZoneRecommendation = (risk) => {
        switch (risk) {
            case 'high': return 'Evitar completamente el área (NO2 > 40 ppb).';
            case 'medium': return 'Monitorear y limitar exposición.';
            case 'low': return 'Seguro para actividades normales.';
            default: return 'Evaluar localmente.';
        }
    };

    const getPersonaDisplayName = (personaValue) => {
        const displayNames = {
            'children': 'Niños',
            'elderly': 'Adultos Mayores',
            'adults': 'Adultos',
            'asthmatics': 'Asmáticos',
            'outdoor_workers': 'Trabajadores al Aire Libre',
            'schools': 'Escuelas',
            'hospitals': 'Hospitales',
            'low_income': 'Bajos Ingresos',
            'elderly_communities': 'Comunidades de Adultos Mayores'
        };
        return displayNames[personaValue] || 'General';
    };

    const renderCharts = (historicalData, forecastData) => {
        if (historicalChartInstance) {
            historicalChartInstance.destroy();
        }
        if (forecastChartInstance) {
            forecastChartInstance.destroy();
        }

        const ctxHistorical = document.getElementById('historicalChart').getContext('2d');
        const ctxForecast = document.getElementById('forecastChart').getContext('2d');

        historicalChartInstance = new Chart(ctxHistorical, {
            type: 'line',
            data: {
                labels: historicalData.map(d => d.date),
                datasets: [{
                    label: 'NO2 (µg/m³)',
                    data: historicalData.map(d => d.no2),
                    borderColor: 'rgba(100, 255, 218, 1)',
                    backgroundColor: 'rgba(100, 255, 218, 0.2)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: { 
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        labels: { color: '#CCD6F6' }
                    }
                },
                scales: {
                    x: { ticks: { color: '#8892B0' } },
                    y: { ticks: { color: '#8892B0' } }
                }
            }
        });

        forecastChartInstance = new Chart(ctxForecast, {
            type: 'line',
            data: {
                labels: forecastData.map(d => `${d.hour}:00`),
                datasets: [{
                    label: 'NO2 (µg/m³)',
                    data: forecastData.map(d => d.no2),
                    borderColor: 'rgba(255, 193, 7, 1)',
                    backgroundColor: 'rgba(255, 193, 7, 0.2)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: { 
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        labels: { color: '#CCD6F6' }
                    }
                },
                scales: {
                    x: { ticks: { color: '#8892B0' } },
                    y: { ticks: { color: '#8892B0' } }
                }
            }
        });
    };

    configForm.addEventListener('submit', (event) => {
        event.preventDefault();
        fetchDashboardData();
    });

    personaRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            const selectedPersona = document.querySelector('input[name="persona"]:checked').value;
            selectedPersonaSpan.textContent = getPersonaDisplayName(selectedPersona);
        });
    });

    fetchDashboardData();
});
