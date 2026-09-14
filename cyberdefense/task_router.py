"""
Enrutador de tareas computacionales para clúster heterogéneo Titán-Zen.
Asigna tareas GPU_ACCELERATED a Titán (RTX 5060 Ti) y tareas CPU_DISTRIBUTED a Laptop Zen (Ryzen 5).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional


class TaskType(str, Enum):
    """Categorías de tareas computacionales."""
    GPU_ACCELERATED = "GPU_ACCELERATED"  # Inferencia LLM local, visión por computadora, embeddings densos
    CPU_DISTRIBUTED = "CPU_DISTRIBUTED"  # Filtrado de logs, RAG parsing, telemetría


class TaskWorkload(str, Enum):
    """Tipos específicos de carga de trabajo dentro del clúster."""
    LLM_INFERENCE = "LLM_INFERENCE"
    COMPUTER_VISION = "COMPUTER_VISION"
    DENSE_EMBEDDINGS = "DENSE_EMBEDDINGS"
    LOG_FILTERING = "LOG_FILTERING"
    RAG_PARSING = "RAG_PARSING"
    TELEMETRY = "TELEMETRY"


@dataclass
class ClusterNode:
    """Información y estado de un nodo del clúster heterogéneo."""
    node_id: str
    name: str
    ip_address: str
    hardware: str
    capabilities: List[TaskType]
    is_active: bool = True

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "ip_address": self.ip_address,
            "hardware": self.hardware,
            "capabilities": [cap.value for cap in self.capabilities],
            "is_active": self.is_active,
        }


@dataclass
class TaskAssignment:
    """Asignación de una tarea a un nodo específico."""
    task_id: str
    task_type: TaskType
    workload: TaskWorkload
    assigned_node: ClusterNode
    payload: Dict[str, Any]

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "workload": self.workload.value,
            "assigned_node": self.assigned_node.to_dict(),
            "payload": self.payload,
        }


class TaskRouter:
    """
    Enrutador de tareas inter-nodo para el clúster OMNI-SYNAPSE (Titán & Laptop Zen).
    """

    NODE_TITAN = ClusterNode(
        node_id="titan-gpu-01",
        name="Nodo Titán",
        ip_address="192.168.1.105",
        hardware="NVIDIA GeForce RTX 5060 Ti",
        capabilities=[TaskType.GPU_ACCELERATED],
    )

    NODE_ZEN = ClusterNode(
        node_id="zen-cpu-01",
        name="Nodo Laptop Zen",
        ip_address="192.168.1.108",
        hardware="AMD Ryzen 5 7520U",
        capabilities=[TaskType.CPU_DISTRIBUTED],
    )

    WORKLOAD_MAPPING: Dict[TaskWorkload, TaskType] = {
        TaskWorkload.LLM_INFERENCE: TaskType.GPU_ACCELERATED,
        TaskWorkload.COMPUTER_VISION: TaskType.GPU_ACCELERATED,
        TaskWorkload.DENSE_EMBEDDINGS: TaskType.GPU_ACCELERATED,
        TaskWorkload.LOG_FILTERING: TaskType.CPU_DISTRIBUTED,
        TaskWorkload.RAG_PARSING: TaskType.CPU_DISTRIBUTED,
        TaskWorkload.TELEMETRY: TaskType.CPU_DISTRIBUTED,
    }

    def __init__(self, custom_nodes: Optional[List[ClusterNode]] = None):
        if custom_nodes:
            self.nodes = {node.node_id: node for node in custom_nodes}
        else:
            self.nodes = {
                self.NODE_TITAN.node_id: self.NODE_TITAN,
                self.NODE_ZEN.node_id: self.NODE_ZEN,
            }

    def resolve_task_type(self, workload: TaskWorkload) -> TaskType:
        """Determina si la carga requiere GPU o CPU."""
        return self.WORKLOAD_MAPPING.get(workload, TaskType.CPU_DISTRIBUTED)

    def route(self, task_id: str, workload: TaskWorkload, payload: Optional[Dict[str, Any]] = None) -> TaskAssignment:
        """
        Enruta una tarea computacional al nodo correspondiente.
        - GPU_ACCELERATED -> Nodo Titán (192.168.1.105, RTX 5060 Ti)
        - CPU_DISTRIBUTED -> Nodo Laptop Zen (192.168.1.108, Ryzen 5)
        """
        task_type = self.resolve_task_type(workload)
        payload = payload or {}

        target_node: Optional[ClusterNode] = None
        for node in self.nodes.values():
            if node.is_active and task_type in node.capabilities:
                target_node = node
                break

        if not target_node:
            # Fallback al nodo Titán si estuviera disponible, o Zen por defecto
            target_node = self.nodes.get(self.NODE_TITAN.node_id, self.NODE_ZEN)

        return TaskAssignment(
            task_id=task_id,
            task_type=task_type,
            workload=workload,
            assigned_node=target_node,
            payload=payload,
        )
