from prometheus_client import start_http_server, Gauge, Info
import time

REGISTERED_LABELS = set()
DATA_FINDINGS_TOTAL = Gauge(
    'data_findings_total',
    'Total number of data findings.',
    ['model', 'guard', 'refusal'] 
)

TRACE_INFO =  Info(
    'trace',
    'Trace information for the selected finding.'
)

LATEST_FINDING_INFO = Info(
    'latest_finding',
    'Context for the latest data finding that requires action.'
)

DATASET_REFINEMENT_PROGRESS = Gauge(
     'dataset_refinment_progress',
     'percentage progress for the dataset refiniment action'
)

def register_data_finding(id: str, model_name: str, guard_name: str, prompt: str, answer: str, refusal: str):
    REGISTERED_LABELS.add((model_name, guard_name))
    DATA_FINDINGS_TOTAL.labels(model=model_name, guard=guard_name, refusal=str(refusal)).inc()
    LATEST_FINDING_INFO.info({
        'id': str(id),
        'model': model_name,
        'guard': guard_name,
        'prompt': prompt,
        'answer': answer,
        'refusal': str(refusal),
        'timestamp': str(int(time.time() * 1000))
    })

def reset_findings():
    labels_to_wipe = list(REGISTERED_LABELS)
    for model, guard in labels_to_wipe:
            DATA_FINDINGS_TOTAL.labels(model=model, guard=guard).set(0)

def register_trace(id: str, text: str):
     TRACE_INFO.info({
        'id': str(id),
        'text': text
     })

def register_refinment_progress(stage: int):
    DATASET_REFINEMENT_PROGRESS.set(int)

def start_metrics_server(port=8004):
    """
    Starts the Prometheus HTTP server and the metric generation
    in a non-blocking background thread.
    """
    start_http_server(port)
    print(f"Prometheus metrics server started on port {port}...")