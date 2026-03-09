import threading
import uuid
from concurrent.futures import ThreadPoolExecutor

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


def update_progress(job_id, library, point):
    with benchmark_lock:
        benchmark_jobs[job_id]["results"][library]["history"].append(point)


def run_benchmark_parallel(job_id, dataset, epochs):
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            pytorch_future = pool.submit(
                train_pytorch,
                dataset,
                epochs,
                lambda lib, point: update_progress(job_id, lib, point)
            )
            tensorflow_future = pool.submit(
                train_tensorflow,
                dataset,
                epochs,
                lambda lib, point: update_progress(job_id, lib, point)
            )

            pytorch_result = pytorch_future.result()
            tensorflow_result = tensorflow_future.result()

        with benchmark_lock:
            benchmark_jobs[job_id]["results"]["pytorch"]["done"] = True
            benchmark_jobs[job_id]["results"]["tensorflow"]["done"] = True
            benchmark_jobs[job_id]["results"]["pytorch"]["final"] = pytorch_result
            benchmark_jobs[job_id]["results"]["tensorflow"]["final"] = tensorflow_result
            benchmark_jobs[job_id]["status"] = "finished"

    except Exception as e:
        with benchmark_lock:
            benchmark_jobs[job_id]["status"] = "failed"
            benchmark_jobs[job_id]["error"] = str(e)


def get_job_status(job_id):
    with benchmark_lock:
        return benchmark_jobs.get(job_id)