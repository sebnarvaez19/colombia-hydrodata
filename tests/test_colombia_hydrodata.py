import pytest
import pandas as pd
import numpy as np
from colombia_hydrodata.filters import Filters
from colombia_hydrodata.attributes import Location, Hydrographic, Variable
from colombia_hydrodata.dataset import Dataset
from colombia_hydrodata.station import Station
from colombia_hydrodata.utils import tsa

def test_filters():
    f = Filters(category="Limnimetrica", department="Bolivar")
    d = f.to_dict()
    assert d == {"category": "Limnimetrica", "department": "Bolivar"}
    assert "status" not in d

def test_location():
    loc = Location(altitude=100.0, longitude=-75.0, latitude=5.0)
    assert str(loc) == "Location: altitude=100.00 [-75.000; 5.000]"

def test_hydrographic():
    hyd = Hydrographic(hydrographic_area="Area", hydrographic_zone="Zone", hydrographic_subzone="Subzone")
    assert str(hyd) == "Hydrographic: area=Area zone=Zone subzone=Subzone"

def test_variable():
    var = Variable(param="NIVEL", label="NV_MEDIA_D", id=123)
    assert str(var) == "NIVEL@NV_MEDIA_D"

def test_dataset_transform():
    loc = Location(altitude=100.0, longitude=-75.0, latitude=5.0)
    hyd = Hydrographic(hydrographic_area="Area", hydrographic_zone="Zone", hydrographic_subzone="Subzone")
    station = Station(
        id="123",
        name="Test Station",
        category="Limnimetrica",
        technology="Manual",
        status="Activa",
        department="Bolivar",
        municipality="Cartagena",
        installation_date=None,
        suspension_date=None,
        owner="IDEAM",
        location=loc,
        hydrographic=hyd,
        variables={}
    )
    var = Variable(param="NIVEL", label="NV_MEDIA_D", id=123)
    data = pd.DataFrame({
        "timestamp": pd.date_range(start="2026-01-01", periods=5, freq="D"),
        "value": [1.0, 2.0, 3.0, 4.0, 5.0]
    })
    
    ds = Dataset(station=station, variable=var, data=data)
    
    # Test sight_level
    ds_sight = ds.sight_level(0.5)
    assert list(ds_sight.data["value"]) == [0.5, 1.5, 2.5, 3.5, 4.5]
    
    # Test rescale
    ds_rescale = ds.rescale(2.0)
    assert list(ds_rescale.data["value"]) == [2.0, 4.0, 6.0, 8.0, 10.0]
    
    # Test interpolate
    data_missing = pd.DataFrame({
        "timestamp": pd.date_range(start="2026-01-01", periods=3, freq="D"),
        "value": [1.0, None, 3.0]
    })
    ds_missing = Dataset(station=station, variable=var, data=data_missing)
    ds_interp = ds_missing.interpolate(time_precision="D")
    assert list(ds_interp.data["value"]) == [1.0, 2.0, 3.0]

def test_tsa_utilities():
    timestamp = pd.Series(pd.date_range(start="2026-01-01", periods=24, freq="ME"))
    value = pd.Series([float(i % 12) + 0.1 * i for i in range(24)])
    
    # detrend - moving average
    trend, detrended = tsa.detrend(value, trend="ma", window=3)
    assert len(trend) == 24
    assert len(detrended) == 24
    np.testing.assert_allclose(value - trend, detrended)
    
    # detrend - linear model
    trend_lm, detrended_lm = tsa.detrend(value, trend="lm", robust=False)
    assert len(trend_lm) == 24
    
    # seasonal_series
    season = tsa.seasonal_series(detrended, timestamp)
    assert len(season) == 24
    # Check that January has same seasonal value for both years
    assert season.iloc[0] == season.iloc[12]
    
    # anomalies_series
    anom = tsa.anomalies_series(detrended, season)
    assert len(anom) == 24
    np.testing.assert_allclose(detrended - season, anom)

    # deconstruction
    decomp = tsa.deconstruction(value, timestamp, trend="ma", window=3)
    assert list(decomp.columns) == ["timestamp", "value", "trend", "detrended", "seasonal", "anomalies"]


def test_client_station_id_normalization():
    from colombia_hydrodata import Client
    client = Client()
    
    # Test that we can fetch using padded ID
    station_padded = client.fetch_station("0029037020")
    assert station_padded.id == "0029037020"
    
    # Test that we can fetch using unpadded ID
    station_unpadded = client.fetch_station("29037020")
    assert station_unpadded.id == "0029037020"
    
    # Test stations_in_list with mixed format IDs
    df = client.stations_in_list(["29037020"])
    assert not df.empty
    assert "0029037020" in df["id"].values
