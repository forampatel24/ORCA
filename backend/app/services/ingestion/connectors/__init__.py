"""Connectors init - Mumbai-only authentic, no hardcoded mocks."""
from app.services.ingestion.connectors.pfz_connector import PFZConnector
from app.services.ingestion.connectors.weather_connector import WeatherConnector
from app.services.ingestion.connectors.ocean_connector import OceanConnector
from app.services.ingestion.connectors.gebco_connector import GEBCOConnector
from app.services.ingestion.connectors.gfw_connector import GFWConnector
