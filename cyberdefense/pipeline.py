"""
Pipeline de integración entre el módulo Telemetry (Sentinel), el analizador ML de Ciberseguridad y el Enrutador de Tareas.
"""

from dataclasses import dataclass, field
import uuid
from typing import Dict, Any, List, Optional

from telemetry.service import TelemetryService
from telemetry.sensors import TelemetryFrame
from cyberdefense.ml_detector import (
    MLAnomalyDetector,
    SecurityLogEntry,
    AnomalyDetectionResult,
)
from cyberdefense.task_router import (
    TaskRouter,
    TaskWorkload,
    TaskAssignment,
    TaskType,
)


@dataclass
class PipelineResult:
    """Resultado consolidado del ciclo de integración telemétrico y ciberdefensa."""
    telemetry_summary: Dict[str, Any]
    security_analysis: Optional[AnomalyDetectionResult]
    routed_tasks: List[TaskAssignment]

    def to_dict(self) -> dict:
        return {
            "telemetry_summary": self.telemetry_summary,
            "security_analysis": self.security_analysis.to_dict() if self.security_analysis else None,
            "routed_tasks": [task.to_dict() for task in self.routed_tasks],
        }


class CyberDefensePipeline:
    """
    Pipeline Integrado de Ciberdefensa y Telemetría para el Clúster OMNI-SYNAPSE.
    Une las señales telemétricas de Sentinel con la detección probabilística de anomalías ML
    y el enrutamiento inteligente de cargas computacionales (Titán & Laptop Zen).
    """

    def __init__(
        self,
        telemetry_service: Optional[TelemetryService] = None,
        detector: Optional[MLAnomalyDetector] = None,
        router: Optional[TaskRouter] = None,
    ):
        self.telemetry_service = telemetry_service or TelemetryService()
        self.detector = detector or MLAnomalyDetector()
        self.router = router or TaskRouter()

    def process_security_logs(
        self,
        entries: List[SecurityLogEntry],
        environment: str = "Ubuntu 26",
        time_window_seconds: float = 60.0,
    ) -> Dict[str, Any]:
        """
        Analiza logs de seguridad y enruta automáticamente las tareas derivadas:
        - Si hay anomalía CRITICAL o HIGH: enruta inferencia de IA local (LLM_INFERENCE / DENSE_EMBEDDINGS) a Nodo Titán.
        - Para auditoría y filtrado rutinario: enruta (LOG_FILTERING / RAG_PARSING) a Laptop Zen.
        """
        analysis = self.detector.detect(entries, time_window_seconds=time_window_seconds, environment=environment)
        tasks: List[TaskAssignment] = []

        # Tarea por defecto de procesamiento/filtrado de logs para la laptop Zen
        log_task_id = f"task-log-{uuid.uuid4().hex[:8]}"
        tasks.append(
            self.router.route(
                task_id=log_task_id,
                workload=TaskWorkload.LOG_FILTERING,
                payload={"total_entries": len(entries), "environment": environment},
            )
        )

        # Si se detecta anomalía severa, delegar inferencia profunda de IA a Titán (GPU)
        if analysis.is_anomaly and analysis.risk_level in ("HIGH", "CRITICAL"):
            ai_task_id = f"task-ai-analysis-{uuid.uuid4().hex[:8]}"
            tasks.append(
                self.router.route(
                    task_id=ai_task_id,
                    workload=TaskWorkload.LLM_INFERENCE,
                    payload={
                        "anomaly_score": analysis.anomaly_score,
                        "risk_level": analysis.risk_level,
                        "reasons": analysis.reasons,
                    },
                )
            )

        return {
            "analysis": analysis,
            "routed_tasks": tasks,
        }

    def run_integrated_cycle(
        self,
        security_entries: Optional[List[SecurityLogEntry]] = None,
        environment: str = "Ubuntu 26",
    ) -> PipelineResult:
        """
        Ejecuta un ciclo completo integrado:
        1. Captura y evalúa telemetría Sentinel (red, heartbeat, camaradería).
        2. Analiza eventos de ciberseguridad con el detector ML (si se proporcionan logs).
        3. Enruta las tareas resultantes al clúster (Titán GPU / Laptop Zen CPU).
        """
        # 1. Ejecutar ciclo telemétrico
        telemetry_res = self.telemetry_service.run_telemetry_cycle()
        routed_tasks: List[TaskAssignment] = []

        # Enrutamiento de tarea telemétrica a la laptop Zen (CPU_DISTRIBUTED)
        telemetry_task_id = f"task-telemetry-{uuid.uuid4().hex[:8]}"
        routed_tasks.append(
            self.router.route(
                task_id=telemetry_task_id,
                workload=TaskWorkload.TELEMETRY,
                payload={"is_telemetry_anomaly": telemetry_res["is_anomaly"]},
            )
        )

        # 2. Análisis de logs de ciberseguridad si están presentes
        security_analysis: Optional[AnomalyDetectionResult] = None
        if security_entries:
            sec_res = self.process_security_logs(security_entries, environment=environment)
            security_analysis = sec_res["analysis"]
            routed_tasks.extend(sec_res["routed_tasks"])

        return PipelineResult(
            telemetry_summary=telemetry_res,
            security_analysis=security_analysis,
            routed_tasks=routed_tasks,
        )
