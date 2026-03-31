import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
import psutil
import time
import os
from flask import json
from confluent_kafka import Consumer
from api.src.kafkaOption.consumer import _make_consumer
from api.src.training.modele_pytorch import train_pytorch
from api.src.training.modele_tensorflow import train_tensorflow

benchmark_jobs = {}
benchmark_lock = threading.Lock()
current_job_id = None


def _consumer_loop_benchmark(topic):
    consumer = _make_consumer(topic)
    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Kafka error [{topic}]: {msg.error()}")
                continue
            data = json.loads(msg.value().decode("utf-8"))
            with benchmark_lock:
                if current_job_id and current_job_id in benchmark_jobs:
                    benchmark_jobs[current_job_id]["results"][topic]["history"].append(data)
        except Exception as e:
            print(f"Consumer error [{topic}]: {e}")


#un thread consumer dédié par topic
threading.Thread(target=_consumer_loop_benchmark, args=("pytorch",), daemon=True).start()
threading.Thread(target=_consumer_loop_benchmark, args=("tensorflow",), daemon=True).start()



def create_job(dataset, epochs=15):
    global current_job_id
    job_id = str(uuid.uuid4())

    with benchmark_lock:
        current_job_id = job_id
        benchmark_jobs[job_id] = {
            "job_id": job_id,
            "dataset": dataset,
            "epochs": epochs,
            "status": "running",
            "results": {
                "pytorch": {"history": [], "done": False},
                "tensorflow": {"history": [], "done": False}
            }
        }

    executor = ThreadPoolExecutor(max_workers=2)
    executor.submit(run_benchmark_parallel, job_id, dataset, epochs)

    return job_id


def train_with_monitoring(train_func, dataset, epochs, lib_name):
    cpu_samples = []
    ram_samples = []

    result = train_func(dataset, epochs, cpu_samples, ram_samples)

    avg_cpu = round(sum(cpu_samples) / len(cpu_samples), 2) if cpu_samples else 0
    max_cpu = round(max(cpu_samples), 2) if cpu_samples else 0
    avg_ram = round(sum(ram_samples) / len(ram_samples), 2) if ram_samples else 0
    max_ram = round(max(ram_samples), 2) if ram_samples else 0

    return {
        "result": result,
        "stats": {
            "cpu_avg": avg_cpu,
            "cpu_max": max_cpu,
            "ram_avg_gb": avg_ram,
            "ram_max_gb": max_ram,
        }
    }


def run_benchmark_parallel(job_id, dataset, epochs):
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            pytorch_future = pool.submit(
                train_with_monitoring, train_pytorch, dataset, epochs, "pytorch"
            )
            tensorflow_future = pool.submit(
                train_with_monitoring, train_tensorflow, dataset, epochs, "tensorflow"
            )

            pytorch_output = pytorch_future.result()
            tensorflow_output = tensorflow_future.result()

        pytorch_result = pytorch_output["result"]
        tensorflow_result = tensorflow_output["result"]
        pytorch_stats = pytorch_output["stats"]
        tensorflow_stats = tensorflow_output["stats"]

        with benchmark_lock:
            benchmark_jobs[job_id]["results"]["pytorch"].update({
                "done": True,
                "final": pytorch_result,
                "history": pytorch_result.get("history", []),
                "CPU_usage": pytorch_stats["cpu_avg"],
                "CPU_peak": pytorch_stats["cpu_max"],
                "RAM_usage": pytorch_stats["ram_avg_gb"],
                "RAM_peak": pytorch_stats["ram_max_gb"],
            })
            benchmark_jobs[job_id]["results"]["tensorflow"].update({
                "done": True,
                "final": tensorflow_result,
                "history": tensorflow_result.get("history", []),
                "CPU_usage": tensorflow_stats["cpu_avg"],
                "CPU_peak": tensorflow_stats["cpu_max"],
                "RAM_usage": tensorflow_stats["ram_avg_gb"],
                "RAM_peak": tensorflow_stats["ram_max_gb"],
            })
            benchmark_jobs[job_id]["status"] = "finished"

    except Exception as e:
        with benchmark_lock:
            benchmark_jobs[job_id]["status"] = "failed"
            benchmark_jobs[job_id]["error"] = str(e)


def get_job_status(job_id):
    with benchmark_lock:
        return benchmark_jobs.get(job_id)
