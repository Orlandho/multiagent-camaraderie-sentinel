"""
Pruebas unitarias e integración para el Módulo Telemétrico Sentinel (SMCMA).
"""

import pytest
from telemetry import (
    NetworkSensor,
    HeartbeatSensor,
    CamaraderieSensor,
    SentinelEngine,
    SentinelThresholds,
    AlertManager,
    HistoryLogger,
    TelemetryService,
)


def test_network_sensor_collection():
    sensor = NetworkSensor(default_latency=20.0, default_bandwidth=150.0)
    metrics = sensor.collect()
    assert metrics.latency_ms == 20.0
    assert metrics.bandwidth_mbps == 150.0

    sensor.update_metrics(latency_ms=120.0, bandwidth_mbps=5.0)
    metrics_updated = sensor.collect()
    assert metrics_updated.latency_ms == 120.0
    assert metrics_updated.bandwidth_mbps == 5.0


def test_heartbeat_sensor():
    sensor = HeartbeatSensor()
    metrics = sensor.collect()
    assert metrics.total_agents == 5
    assert len(metrics.active_agents) == 5
    assert metrics.availability_ratio == 1.0
    assert len(metrics.missing_agents) == 0

    sensor.set_agent_offline("Hermes")
    metrics_offline = sensor.collect()
    assert "Hermes" in metrics_offline.missing_agents
    assert metrics_offline.availability_ratio == 0.8  # 4/5

    sensor.register_heartbeat("Hermes")
    assert sensor.collect().availability_ratio == 1.0


def test_camaraderie_sensor():
    sensor = CamaraderieSensor(initial_interactions=10, initial_sentiment=0.90)
    metrics = sensor.collect()
    assert metrics.interaction_count == 10
    assert metrics.sentiment_score == 0.90

    sensor.record_interaction(sentiment_delta=0.05)
    assert sensor.collect().interaction_count == 11
    assert sensor.collect().sentiment_score == 0.95

    sensor.update_sentiment(0.60)
    assert sensor.collect().sentiment_score == 0.60


def test_sentinel_engine_normal_state():
    service = TelemetryService()
    frame = service.capture_frame()
    engine = SentinelEngine()
    result = engine.analyze(frame)

    assert result.is_anomaly is False
    assert len(result.reasons) == 0


def test_sentinel_engine_detects_anomalies():
    engine = SentinelEngine(
        thresholds=SentinelThresholds(
            max_latency_ms=50.0,
            min_bandwidth_mbps=20.0,
            min_availability_ratio=0.80,
            min_sentiment_score=0.75,
        )
    )

    network_sensor = NetworkSensor(default_latency=100.0, default_bandwidth=5.0)
    heartbeat_sensor = HeartbeatSensor()
    heartbeat_sensor.set_agent_offline("Hermes")
    heartbeat_sensor.set_agent_offline("Jules")  # 3/5 active = 0.60
    camaraderie_sensor = CamaraderieSensor(initial_sentiment=0.50)

    service = TelemetryService(
        network_sensor=network_sensor,
        heartbeat_sensor=heartbeat_sensor,
        camaraderie_sensor=camaraderie_sensor,
        engine=engine,
    )

    frame = service.capture_frame()
    result = engine.analyze(frame)

    assert result.is_anomaly is True
    assert len(result.reasons) == 4  # High latency, low bandwidth, low availability, low sentiment


def test_alert_manager_and_history_logger():
    alert_manager = AlertManager()
    logger = HistoryLogger()

    service = TelemetryService(
        alert_manager=alert_manager,
        logger=logger,
    )

    # Normal cycle
    res_normal = service.run_telemetry_cycle()
    assert res_normal["is_anomaly"] is False
    assert res_normal["alert"] is None
    assert len(logger.get_history()) == 1

    # Anomaly cycle
    service.network_sensor.update_metrics(latency_ms=200.0, bandwidth_mbps=1.0)
    res_anomaly = service.run_telemetry_cycle()

    assert res_anomaly["is_anomaly"] is True
    assert res_anomaly["alert"] is not None
    assert "Antigravity" in res_anomaly["alert"]["recipients"]
    assert "Hermes" in res_anomaly["alert"]["recipients"]
    assert res_anomaly["alert"]["severity"] == "CRITICAL"
    assert len(logger.get_history()) == 2
    assert len(logger.get_anomalies()) == 1
