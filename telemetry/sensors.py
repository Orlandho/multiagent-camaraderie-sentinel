"""
Módulo de Sensores de Monitoreo para el Sistema Telemétrico Sentinel (SMCMA).
Captura métricas de red, disponibilidad de agentes (heartbeat) e índice de camaradería.
"""

from dataclasses import dataclass, field
import time
from typing import Dict, List, Optional


@dataclass
class NetworkMetrics:
    """Métricas de red de la infraestructura."""
    latency_ms: float
    bandwidth_mbps: float

    def to_dict(self) -> dict:
        return {
            "latency_ms": self.latency_ms,
            "bandwidth_mbps": self.bandwidth_mbps,
        }


@dataclass
class HeartbeatMetrics:
    """Métricas de estado y presencia de agentes en el sistema."""
    active_agents: List[str]
    missing_agents: List[str]
    total_agents: int

    @property
    def availability_ratio(self) -> float:
        if self.total_agents == 0:
            return 0.0
        return len(self.active_agents) / self.total_agents

    def to_dict(self) -> dict:
        return {
            "active_agents": self.active_agents,
            "missing_agents": self.missing_agents,
            "total_agents": self.total_agents,
            "availability_ratio": round(self.availability_ratio, 2),
        }


@dataclass
class CamaraderieMetrics:
    """Métricas de interacción y salud del clima de colaboración (camaradería)."""
    interaction_count: int
    sentiment_score: float  # Escala 0.0 a 1.0

    def to_dict(self) -> dict:
        return {
            "interaction_count": self.interaction_count,
            "sentiment_score": self.sentiment_score,
        }


@dataclass
class TelemetryFrame:
    """Fotograma telemétrico completo capturado en un instante de tiempo."""
    network: NetworkMetrics
    heartbeat: HeartbeatMetrics
    camaraderie: CamaraderieMetrics
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "network": self.network.to_dict(),
            "heartbeat": self.heartbeat.to_dict(),
            "camaraderie": self.camaraderie.to_dict(),
        }


class NetworkSensor:
    """Sensor encargado de medir latencia y ancho de banda."""

    def __init__(self, default_latency: float = 15.0, default_bandwidth: float = 100.0):
        self.latency_ms = default_latency
        self.bandwidth_mbps = default_bandwidth

    def update_metrics(self, latency_ms: float, bandwidth_mbps: float) -> None:
        self.latency_ms = latency_ms
        self.bandwidth_mbps = bandwidth_mbps

    def collect(self) -> NetworkMetrics:
        return NetworkMetrics(
            latency_ms=self.latency_ms,
            bandwidth_mbps=self.bandwidth_mbps,
        )


class HeartbeatSensor:
    """Sensor encargado de monitorear el pulso y disponibilidad de los agentes."""

    DEFAULT_AGENTS = ["Orlando", "Antigravity", "Atenea", "Hermes", "Jules"]

    def __init__(self, expected_agents: Optional[List[str]] = None):
        self.expected_agents = expected_agents or list(self.DEFAULT_AGENTS)
        self._active_agents = set(self.expected_agents)

    def register_heartbeat(self, agent_name: str) -> None:
        if agent_name in self.expected_agents:
            self._active_agents.add(agent_name)

    def set_agent_offline(self, agent_name: str) -> None:
        self._active_agents.discard(agent_name)

    def collect(self) -> HeartbeatMetrics:
        active = [agent for agent in self.expected_agents if agent in self._active_agents]
        missing = [agent for agent in self.expected_agents if agent not in self._active_agents]
        return HeartbeatMetrics(
            active_agents=active,
            missing_agents=missing,
            total_agents=len(self.expected_agents),
        )


class CamaraderieSensor:
    """Sensor encargado de monitorear el índice de camaradería y sentimiento."""

    def __init__(self, initial_interactions: int = 10, initial_sentiment: float = 0.95):
        self.interaction_count = initial_interactions
        self.sentiment_score = initial_sentiment

    def record_interaction(self, sentiment_delta: float = 0.01) -> None:
        self.interaction_count += 1
        self.sentiment_score = max(0.0, min(1.0, self.sentiment_score + sentiment_delta))

    def update_sentiment(self, score: float) -> None:
        self.sentiment_score = max(0.0, min(1.0, score))

    def collect(self) -> CamaraderieMetrics:
        return CamaraderieMetrics(
            interaction_count=self.interaction_count,
            sentiment_score=round(self.sentiment_score, 3),
        )
