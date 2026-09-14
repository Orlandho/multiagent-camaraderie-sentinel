"""
Motor de Análisis Sentinel para la detección de anomalías telemétricas.
Evalúa fotogramas telemétricos en función de umbrales configurables.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from telemetry.sensors import TelemetryFrame


@dataclass
class SentinelThresholds:
    """Umbrales de tolerancia para las métricas telemétricas."""
    max_latency_ms: float = 100.0
    min_bandwidth_mbps: float = 10.0
    min_availability_ratio: float = 0.80
    min_sentiment_score: float = 0.70


@dataclass
class AnalysisResult:
    """Resultado del análisis telemétrico realizado por el Motor Sentinel."""
    is_anomaly: bool
    reasons: List[str]
    frame: TelemetryFrame

    def to_dict(self) -> dict:
        return {
            "is_anomaly": self.is_anomaly,
            "reasons": self.reasons,
            "frame": self.frame.to_dict(),
        }


class SentinelEngine:
    """Motor de Análisis que evalúa anomalías en la red, pulso de agentes y camaradería."""

    def __init__(self, thresholds: Optional[SentinelThresholds] = None):
        self.thresholds = thresholds or SentinelThresholds()

    def analyze(self, frame: TelemetryFrame) -> AnalysisResult:
        reasons: List[str] = []

        # 1. Evaluación de Red
        if frame.network.latency_ms > self.thresholds.max_latency_ms:
            reasons.append(
                f"Latencia alta detectada: {frame.network.latency_ms}ms > {self.thresholds.max_latency_ms}ms"
            )
        if frame.network.bandwidth_mbps < self.thresholds.min_bandwidth_mbps:
            reasons.append(
                f"Ancho de banda bajo detectado: {frame.network.bandwidth_mbps}Mbps < {self.thresholds.min_bandwidth_mbps}Mbps"
            )

        # 2. Evaluación de Heartbeat
        if frame.heartbeat.availability_ratio < self.thresholds.min_availability_ratio:
            missing_str = ", ".join(frame.heartbeat.missing_agents)
            reasons.append(
                f"Disponibilidad de agentes baja ({frame.heartbeat.availability_ratio * 100:.1f}%). Agentes faltantes: [{missing_str}]"
            )

        # 3. Evaluación de Camaradería
        if frame.camaraderie.sentiment_score < self.thresholds.min_sentiment_score:
            reasons.append(
                f"Índice de camaradería bajo: {frame.camaraderie.sentiment_score} < {self.thresholds.min_sentiment_score}"
            )

        is_anomaly = len(reasons) > 0
        return AnalysisResult(
            is_anomaly=is_anomaly,
            reasons=reasons,
            frame=frame,
        )
