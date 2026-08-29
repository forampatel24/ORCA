-- M1 Polyglot Storage Init - docs 05_DATABASE_DESIGN + 20_DATABSE_ARCHITECTURE
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;

-- users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    preferred_language VARCHAR(10) DEFAULT 'en',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- conversations
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user','assistant','system')),
    content TEXT NOT NULL,
    language VARCHAR(10),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- agent_runs
CREATE TABLE IF NOT EXISTS agent_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending','running','completed','failed')),
    input JSONB,
    output JSONB,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error TEXT
);

CREATE TABLE IF NOT EXISTS tool_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_run_id UUID REFERENCES agent_runs(id) ON DELETE CASCADE,
    tool_name VARCHAR(100) NOT NULL,
    input JSONB,
    output JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error TEXT
);

-- data_sources registry docs 08
CREATE TABLE IF NOT EXISTS data_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    provider VARCHAR(255),
    source_type VARCHAR(50),
    endpoint TEXT,
    category VARCHAR(50),
    format VARCHAR(50),
    update_frequency VARCHAR(50),
    status VARCHAR(20) DEFAULT 'AVAILABLE',
    last_updated TIMESTAMPTZ,
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS ingestion_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    data_source_id UUID REFERENCES data_sources(id),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status VARCHAR(20),
    records_processed INT DEFAULT 0,
    records_inserted INT DEFAULT 0,
    records_updated INT DEFAULT 0,
    records_failed INT DEFAULT 0,
    error TEXT
);

-- PFZ
CREATE TABLE IF NOT EXISTS pfz_observations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES data_sources(id),
    observation_time TIMESTAMPTZ,
    valid_from TIMESTAMPTZ,
    valid_to TIMESTAMPTZ,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    geometry GEOGRAPHY(POINT, 4326),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pfz_geometry ON pfz_observations USING GIST (geometry);

-- ocean
CREATE TABLE IF NOT EXISTS ocean_observations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES data_sources(id),
    observation_time TIMESTAMPTZ,
    location GEOGRAPHY(POINT, 4326),
    sst DOUBLE PRECISION,
    chlorophyll DOUBLE PRECISION,
    wave_height DOUBLE PRECISION,
    wave_period DOUBLE PRECISION,
    wind_speed DOUBLE PRECISION,
    current_speed DOUBLE PRECISION,
    metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_ocean_location ON ocean_observations USING GIST (location);

-- weather
CREATE TABLE IF NOT EXISTS weather_observations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES data_sources(id),
    observation_time TIMESTAMPTZ,
    forecast_time TIMESTAMPTZ,
    location GEOGRAPHY(POINT, 4326),
    temperature DOUBLE PRECISION,
    wind_speed DOUBLE PRECISION,
    wind_direction DOUBLE PRECISION,
    rainfall DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    pressure DOUBLE PRECISION,
    metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_weather_location ON weather_observations USING GIST (location);

-- hazards
CREATE TABLE IF NOT EXISTS marine_hazards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES data_sources(id),
    hazard_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20),
    valid_from TIMESTAMPTZ,
    valid_to TIMESTAMPTZ,
    geometry GEOMETRY(GEOMETRY, 4326),
    description TEXT,
    metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_hazards_geom ON marine_hazards USING GIST (geometry);

-- geofences
CREATE TABLE IF NOT EXISTS geofences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    geofence_type VARCHAR(50),
    geometry GEOMETRY(POLYGON, 4326),
    severity VARCHAR(20),
    description TEXT,
    active BOOLEAN DEFAULT true,
    metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_geofences_geom ON geofences USING GIST (geometry);

CREATE TABLE IF NOT EXISTS protected_areas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255),
    area_type VARCHAR(100),
    geometry GEOMETRY(MULTIPOLYGON, 4326),
    authority VARCHAR(255),
    restrictions TEXT,
    description TEXT,
    metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_protected_geom ON protected_areas USING GIST (geometry);

CREATE TABLE IF NOT EXISTS maritime_boundaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255),
    boundary_type VARCHAR(100),
    geometry GEOMETRY(MULTILINESTRING, 4326),
    country VARCHAR(100),
    description TEXT,
    metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_maritime_geom ON maritime_boundaries USING GIST (geometry);

-- risk
CREATE TABLE IF NOT EXISTS risk_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    location GEOGRAPHY(POINT, 4326),
    assessment_time TIMESTAMPTZ DEFAULT NOW(),
    valid_from TIMESTAMPTZ,
    valid_to TIMESTAMPTZ,
    risk_score INT,
    risk_level VARCHAR(20) CHECK (risk_level IN ('LOW','MODERATE','HIGH','CRITICAL','UNKNOWN')),
    risk_factors JSONB,
    data_quality VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- routes
CREATE TABLE IF NOT EXISTS routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    origin GEOGRAPHY(POINT, 4326),
    destination GEOGRAPHY(POINT, 4326),
    route_geometry GEOMETRY(LINESTRING, 4326),
    distance DOUBLE PRECISION,
    estimated_duration DOUBLE PRECISION,
    risk_score INT,
    route_score DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_routes_geom ON routes USING GIST (route_geometry);

-- alerts
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    alert_type VARCHAR(50),
    severity VARCHAR(20),
    title VARCHAR(255),
    message TEXT,
    location GEOGRAPHY(POINT, 4326),
    valid_from TIMESTAMPTZ,
    valid_to TIMESTAMPTZ,
    source VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- knowledge docs for RAG
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255),
    source VARCHAR(255),
    document_type VARCHAR(50),
    object_storage_key TEXT,
    language VARCHAR(10),
    version VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    chunk_index INT,
    text TEXT,
    language VARCHAR(10),
    embedding_id VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- seed data_sources
INSERT INTO data_sources (name, provider, source_type, category, format, status) VALUES
('INCOIS PFZ', 'INCOIS', 'pfz', 'marine', 'GeoJSON', 'AVAILABLE'),
('INCOIS OSF', 'INCOIS', 'ocean_state', 'ocean', 'NetCDF', 'AVAILABLE'),
('IMD Weather', 'IMD', 'weather', 'meteorological', 'JSON', 'AVAILABLE'),
('IMD Cyclone', 'IMD', 'cyclone', 'hazard', 'JSON', 'AVAILABLE'),
('WDPA Marine Protected Areas', 'Protected Planet', 'protected_area', 'geospatial', 'Shapefile', 'AVAILABLE'),
('Marine Regions EEZ', 'Marine Regions', 'eez', 'geospatial', 'Shapefile', 'AVAILABLE')
ON CONFLICT DO NOTHING;
