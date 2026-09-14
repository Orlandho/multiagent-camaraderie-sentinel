"""
Servicio de Telemetría Principal para el Módulo Telemétrico Sentinel (SMCMA).
Orquesta la recolección de sensores, análisis en Sentinel Engine y despacho de alertas/registro.
"""

from typing import Dict, Any, Optional
from telemetry.sensors import (
    NetworkSensor,
    HeartbeatSensor,
    CamaraderieSensor,
    TelemetryFrame,
)
from telemetry.engine import SentinelEngine, SentinelThresholds, AnalysisResult
from telemetry.alerts import AlertManager, HistoryLogger, AlertNotification


class TelemetryService:
    """Servicio orquestador del ciclo de telemetría."""

    def __init__(
        self,
        network_sensor: Optional[NetworkSensor] = None,
        heartbeat_sensor: Optional[HeartbeatSensor] = None,
        camaraderie_sensor: Optional[CamaraderieSensor] = None,
        engine: Optional[SentinelEngine] = None,
        alert_manager: Optional[AlertManager] = None,
        logger: Optional[HistoryLogger] = None,
    ):
        self.network_sensor = network_sensor or NetworkSensor()
        self.heartbeat_sensor = heartbeat_sensor or HeartbeatSensor()
        self.camaraderie_sensor = camaraderie_sensor or CamaraderieSensor()
        self.engine = engine or SentinelEngine()
        self.alert_manager = alert_manager or AlertManager()
        self.logger = logger or HistoryLogger()

    def capture_frame(self) -> TelemetryFrame:
        """Captura métricas de todos los sensores registrados."""
        return TelemetryFrame(
            network=self.network_sensor.collect(),
            heartbeat=self.heartbeat_sensor.collect(),
            camaraderie=self.camaraderie_sensor.collect(),
        )

    def run_telemetry_cycle(self) -> Dict[str, Any]:
        """
        Ejecuta un ciclo telemétrico completo:
        1. Captura fotograma telemétrico.
        2. Analiza fotograma con Sentinel Engine.
        3. Si hay anomalía -> Genera y despacha Alerta Crítica a Antigravity y Hermes.
        4. Si no -> Registra en el Histórico.
        5. Retorna resumen de ejecución.
        """
        frame = self.capture_frame()
        analysis = self.engine.analyze(frame)

        alert_issued: Optional[AlertNotification] = None
        if analysis.is_anomaly:
            alert_issued = self.alert_manager.dispatch_alert(analysis, severity="CRITICAL")

        log_entry = self.logger.log_cycle(analysis)

        return {
            "is_anomaly": analysis.is_anomaly,
            "reasons": analysis.reasons,
            "alert": alert_issued.to_dict() if alert_issued else None,
            "log": log_entry,
            "frame": frame.to_dict(),
        }
