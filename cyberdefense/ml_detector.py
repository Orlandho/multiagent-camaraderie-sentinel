"""
Detector de anomalías ML para logs de seguridad y tráfico de red en entornos virtuales de laboratorio.
Soporta Ubuntu 26, Fedora, Kali y Metasploitable2.
Extrae características (frecuencia de peticiones, ratio de puertos, entropía de comandos) y realiza clasificación adaptativa.
"""

from dataclasses import dataclass
import math
from typing import List, Optional


@dataclass
class SecurityLogEntry:
    """Entrada de log de seguridad o registro de tráfico de red."""
    source_ip: str
    target_ip: str
    port: int
    command_payload: str
    timestamp: float
    environment: str = "Ubuntu 26"  # Ubuntu 26, Fedora, Kali, Metasploitable2

    def to_dict(self) -> dict:
        return {
            "source_ip": self.source_ip,
            "target_ip": self.target_ip,
            "port": self.port,
            "command_payload": self.command_payload,
            "timestamp": self.timestamp,
            "environment": self.environment,
        }


@dataclass
class ExtractedFeatures:
    """Características extraídas de un lote de peticiones/logs."""
    request_frequency: float  # peticiones por segundo
    port_ratio: float         # ratio de puertos únicos / total peticiones
    command_entropy: float    # entropía de Shannon de la carga de comandos
    total_requests: int
    unique_ports: int

    def to_dict(self) -> dict:
        return {
            "request_frequency": self.request_frequency,
            "port_ratio": self.port_ratio,
            "command_entropy": self.command_entropy,
            "total_requests": self.total_requests,
            "unique_ports": self.unique_ports,
        }


class FeatureExtractor:
    """Extractor de características estadísticas y de entropía para tráfico de red y comandos."""

    @staticmethod
    def calculate_shannon_entropy(text: str) -> float:
        """Calcula la entropía de Shannon de una cadena de texto."""
        if not text:
            return 0.0
        length = len(text)
        frequency = {}
        for char in text:
            frequency[char] = frequency.get(char, 0) + 1
        entropy = 0.0
        for count in frequency.values():
            p = count / length
            entropy -= p * math.log2(p)
        return round(entropy, 4)

    def extract(self, entries: List[SecurityLogEntry], time_window_seconds: float = 60.0) -> ExtractedFeatures:
        """Extrae características del conjunto de entradas provistas en una ventana de tiempo."""
        if not entries:
            return ExtractedFeatures(
                request_frequency=0.0,
                port_ratio=0.0,
                command_entropy=0.0,
                total_requests=0,
                unique_ports=0,
            )

        total_requests = len(entries)
        ports = {entry.port for entry in entries}
        unique_ports = len(ports)
        port_ratio = round(unique_ports / total_requests, 4)

        duration = max(time_window_seconds, 1.0)
        request_frequency = round(total_requests / duration, 4)

        combined_commands = " ".join(entry.command_payload for entry in entries if entry.command_payload)
        command_entropy = self.calculate_shannon_entropy(combined_commands)

        return ExtractedFeatures(
            request_frequency=request_frequency,
            port_ratio=port_ratio,
            command_entropy=command_entropy,
            total_requests=total_requests,
            unique_ports=unique_ports,
        )


@dataclass
class AnomalyDetectionResult:
    """Resultado de la evaluación de anomalía por el modelo ML."""
    is_anomaly: bool
    anomaly_score: float
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    reasons: List[str]
    features: ExtractedFeatures
    environment: str

    def to_dict(self) -> dict:
        return {
            "is_anomaly": self.is_anomaly,
            "anomaly_score": self.anomaly_score,
            "risk_level": self.risk_level,
            "reasons": self.reasons,
            "features": self.features.to_dict(),
            "environment": self.environment,
        }


class MLAnomalyDetector:
    """
    Detector de anomalías con modelo de scoring heurístico y probabilístico adaptativo.
    Ajusta la sensibilidad según el entorno virtual (Ubuntu 26, Fedora, Kali, Metasploitable2).
    """

    SUPPORTED_ENVIRONMENTS = {"Ubuntu 26", "Fedora", "Kali", "Metasploitable2"}

    def __init__(
        self,
        freq_threshold: float = 5.0,
        port_ratio_threshold: float = 0.5,
        entropy_threshold: float = 4.5,
        anomaly_score_threshold: float = 0.6,
    ):
        self.freq_threshold = freq_threshold
        self.port_ratio_threshold = port_ratio_threshold
        self.entropy_threshold = entropy_threshold
        self.anomaly_score_threshold = anomaly_score_threshold

    def evaluate_features(self, features: ExtractedFeatures, environment: str = "Ubuntu 26") -> AnomalyDetectionResult:
        """Evalúa las características contra umbrales probabilísticos adaptativos."""
        reasons: List[str] = []
        score_components: List[float] = []

        # Factor de sensibilidad por entorno virtual de laboratorio
        env_sensitivity = 1.0
        if environment in ("Kali", "Metasploitable2"):
            env_sensitivity = 1.15

        # 1. Frecuencia de Peticiones
        freq_score = min(1.0, features.request_frequency / self.freq_threshold)
        if features.request_frequency > self.freq_threshold:
            reasons.append(
                f"Alta frecuencia de peticiones: {features.request_frequency} req/s (> {self.freq_threshold})"
            )
        score_components.append(freq_score * 0.35)

        # 2. Ratio de Puertos (escaneo de puertos)
        port_score = min(1.0, features.port_ratio / self.port_ratio_threshold)
        if features.port_ratio > self.port_ratio_threshold:
            reasons.append(
                f"Posible escaneo de puertos (port ratio: {features.port_ratio} > {self.port_ratio_threshold})"
            )
        score_components.append(port_score * 0.35)

        # 3. Entropía de Comandos (payloads ofuscados)
        entropy_score = min(1.0, features.command_entropy / self.entropy_threshold)
        if features.command_entropy > self.entropy_threshold:
            reasons.append(
                f"Alta entropía de comandos (payload anómalo): {features.command_entropy} (> {self.entropy_threshold})"
            )
        score_components.append(entropy_score * 0.30)

        base_score = sum(score_components)
        anomaly_score = round(min(1.0, base_score * env_sensitivity), 3)

        is_anomaly = anomaly_score >= self.anomaly_score_threshold or len(reasons) > 0

        if anomaly_score >= 0.8:
            risk_level = "CRITICAL"
        elif anomaly_score >= 0.6:
            risk_level = "HIGH"
        elif anomaly_score >= 0.3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return AnomalyDetectionResult(
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            risk_level=risk_level,
            reasons=reasons,
            features=features,
            environment=environment,
        )

    def detect(
        self,
        entries: List[SecurityLogEntry],
        time_window_seconds: float = 60.0,
        environment: str = "Ubuntu 26",
    ) -> AnomalyDetectionResult:
        """Procesa una lista de entradas de logs y genera un diagnóstico de anomalía."""
        extractor = FeatureExtractor()
        features = extractor.extract(entries, time_window_seconds=time_window_seconds)
        return self.evaluate_features(features, environment=environment)
