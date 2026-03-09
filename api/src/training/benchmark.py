import threading
import uuid
from concurrent.futures import ThreadPoolExecutor

import psutil

import time

from concurrent.futures import ProcessPoolExecutor
from api.src.training.modele_pytorch import train_pytorch
from api.src.training.modele_tensorflow import train_tensorflow

benchmark_jobs = {}
benchmark_lock = threading.Lock()


def create_job(dataset, epochs=15):
    job_id = str(uuid.uuid4())

    with benchmark_lock:
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


def train_with_monitoring(train_func, dataset, epochs, progress_callback, lib_name):
    """Wrapper qui exécute l'entraînement ET monitore ses propres ressources"""
    stop_event = threading.Event()
    cpu_samples = []
    ram_samples = []

    def _monitor():
        proc = psutil.Process()
        while not stop_event.is_set():
            cpu_samples.append(proc.cpu_percent(interval=None))
            ram_samples.append(proc.memory_info().rss / (1024 ** 3))
            time.sleep(0.5)

    monitor_thread = threading.Thread(target=_monitor, daemon=True)
    monitor_thread.start()

    result, point = train_func(dataset, epochs, progress_callback, cpu_samples, ram_samples)

    stop_event.set()
    monitor_thread.join()

    print("Stats for", lib_name)
    print()
    return {"result": result}

def update_progress(job_id, library, point):
    with benchmark_lock:
        benchmark_jobs[job_id]["results"][library]["history"].append(point)


def run_benchmark_parallel(job_id, dataset, epochs):
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            pytorch_future = pool.submit(
                train_with_monitoring,
                train_pytorch,
                dataset,
                epochs,
                lambda lib, point: update_progress(job_id, lib, point),
                "pytorch"
            )
            tensorflow_future = pool.submit(
                train_with_monitoring,
                train_tensorflow,
                dataset,
                epochs,
                lambda lib, point: update_progress(job_id, lib, point),
                "tensorflow"
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
                "CPU_usage": pytorch_stats["cpu_avg"],
                "CPU_peak": pytorch_stats["cpu_max"],
                "RAM_usage": pytorch_stats["ram_avg_gb"],
                "RAM_peak": pytorch_stats["ram_max_gb"],
            })
            benchmark_jobs[job_id]["results"]["tensorflow"].update({
                "done": True,
                "final": tensorflow_result,
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