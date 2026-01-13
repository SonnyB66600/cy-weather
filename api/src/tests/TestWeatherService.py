import pytest
import httpx
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

# Import du service et des modèles
# Note : Ajuste l'import selon la structure de ton projet
from src.services.weather_service import weather_service, WeatherService
from src.models.Weather import WeatherResponse, ForecastResponse

@pytest.mark.asyncio
class TestWeatherService:

    @pytest.fixture
    def mock_geocoding_response(self):
        return {
            "results": [{
                "latitude": 48.8566,
                "longitude": 2.3522,
                "name": "Paris",
                "country_code": "FR"
            }]
        }

    @pytest.fixture
    def mock_current_weather_response(self):
        return {
            "current": {
                "time": "2024-01-20T12:00",
                "temperature_2m": 15.5,
                "relative_humidity_2m": 65,
                "apparent_temperature": 14.2,
                "pressure_msl": 1013.2,
                "wind_speed_10m": 10.5,
                "weather_code": 0
            }
        }

    @pytest.fixture
    def mock_forecast_response(self):
        return {
            "daily": {
                "time": ["2024-01-20", "2024-01-21"],
                "weather_code": [0, 61],
                "temperature_2m_max": [18.0, 14.0],
                "temperature_2m_min": [10.0, 8.0],
                "apparent_temperature_max": [17.0, 13.0],
                "apparent_temperature_min": [9.0, 7.0],
                "precipitation_probability_max": [0, 80],
                "wind_speed_10m_max": [15.0, 20.0]
            }
        }

    async def test_get_coordinates_success(self, mocker, mock_geocoding_response):
        """Teste la récupération réussie des coordonnées"""
        # Mock de httpx.AsyncClient.get
        mock_get = mocker.patch("httpx.AsyncClient.get", new_callable=AsyncMock)
        mock_get.return_value = MagicMock(spec=httpx.Response)
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_geocoding_response

        lat, lon, name, country = await weather_service._get_coordinates("Paris")

        assert lat == 48.8566
        assert lon == 2.3522
        assert name == "Paris"
        assert country == "FR"

    async def test_get_coordinates_city_not_found(self, mocker):
        """Teste l'erreur quand une ville n'est pas trouvée"""
        mock_get = mocker.patch("httpx.AsyncClient.get", new_callable=AsyncMock)
        mock_get.return_value = MagicMock(spec=httpx.Response)
        mock_get.return_value.json.return_value = {"results": []}

        with pytest.raises(ValueError, match="Ville 'Inexistante' non trouvée"):
            await weather_service._get_coordinates("Inexistante")

    async def test_get_current_weather(self, mocker, mock_geocoding_response, mock_current_weather_response):
        """Teste la récupération de la météo actuelle"""
        # On mock les deux appels API successifs
        mock_get = mocker.patch("httpx.AsyncClient.get", new_callable=AsyncMock)
        
        # Premier retour : Géocodage, Deuxième retour : Météo
        mock_res1 = MagicMock(spec=httpx.Response)
        mock_res1.json.return_value = mock_geocoding_response
        mock_res1.status_code = 200
        
        mock_res2 = MagicMock(spec=httpx.Response)
        mock_res2.json.return_value = mock_current_weather_response
        mock_res2.status_code = 200
        
        mock_get.side_effect = [mock_res1, mock_res2]

        result = await weather_service.get_current_weather("Paris")

        assert isinstance(result, WeatherResponse)
        assert result.city == "Paris"
        assert result.weather.temperature == 15.5
        assert result.weather.description == "Ciel dégagé"
        assert result.weather.icon == "01d"

    async def test_get_forecast(self, mocker, mock_geocoding_response, mock_forecast_response):
        """Teste la récupération des prévisions"""
        mock_get = mocker.patch("httpx.AsyncClient.get", new_callable=AsyncMock)
        
        mock_res1 = MagicMock(spec=httpx.Response)
        mock_res1.json.return_value = mock_geocoding_response
        mock_res1.status_code = 200
        
        mock_res2 = MagicMock(spec=httpx.Response)
        mock_res2.json.return_value = mock_forecast_response
        mock_res2.status_code = 200
        
        mock_get.side_effect = [mock_res1, mock_res2]

        result = await weather_service.get_forecast("Paris")

        assert isinstance(result, ForecastResponse)
        assert len(result.forecast) == 2
        assert result.forecast[0].temp_max == 18.0
        assert result.forecast[1].description == "Pluie légère"
        assert result.forecast[1].precipitation_probability == 80

    def test_wmo_descriptions(self):
        """Vérifie que les descriptions WMO sont correctes"""
        assert weather_service._get_weather_description(0) == "Ciel dégagé"
        assert weather_service._get_weather_description(95) == "Orage"
        assert weather_service._get_weather_description(999) == "Conditions inconnues"
