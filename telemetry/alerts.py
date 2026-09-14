"""
Gestor de Alertas y Registro Histórico para el Módulo Telemétrico Sentinel.
Permite notificar alertas críticas a los miembros del equipo y mantener historial.
"""

from dataclasses import dataclass, field
import time
from typing import List, Dict, Any, Optional
from telemetry.engine import AnalysisResult


@dataclass
class AlertNotification:
    """Representa una notificación de alerta telemétrica."""
    recipients: List[str]
    severity: str  # e.g., "CRITICAL", "WARNING", "INFO"
    summary: str
    details: List[str]
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "recipients": self.recipients,
            "severity": self.severity,
            "summary": self.summary,
            "details": self.details,
            "timestamp": self.timestamp,
        }


class AlertManager:
    """Gestor encargado de emitir alertas a los agentes de orquestación e infraestructura."""

    DEFAULT_RECIPIENTS = ["Antigravity", "Hermes"]

    def __init__(self, recipients: Optional[List[str]] = None):
        self.recipients = recipients or list(self.DEFAULT_RECIPIENTS)
        self.alerts_history: List[AlertNotification] = []

    def dispatch_alert(self, analysis: AnalysisResult, severity: str = "CRITICAL") -> AlertNotification:
        summary = "Alerta Crítica Detectada por Sentinel Engine" if severity == "CRITICAL" else "Advertencia Telemétrica"
        notification = AlertNotification(
            recipients=list(self.recipients),
            severity=severity,
            summary=summary,
            details=list(analysis.reasons),
        )
        self.alerts_history.append(notification)
        return notification


class HistoryLogger:
    """Registro de historial telemétrico para auditoría y métricas del sistema SMCMA."""

    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def log_cycle(self, analysis: AnalysisResult) -> Dict[str, Any]:
        entry = {
            "timestamp": analysis.frame.timestamp,
            "is_anomaly": analysis.is_anomaly,
            "reasons_count": len(analysis.reasons),
            "reasons": analysis.reasons,
            "metrics": analysis.frame.to_dict(),
        }
        self.history.append(entry)
        return entry

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history

    def get_anomalies(self) -> List[Dict[str, Any]]:
        return [entry for entry in self.history if entry["is_anomaly"]]
