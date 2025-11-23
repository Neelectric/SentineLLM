from prometheus_client import start_http_server, Gauge, Info
import time

REGISTERED_LABELS = set()
DATA_FINDINGS_TOTAL = Gauge(
    'data_findings_total',
    'Total number of data findings.',
    ['model', 'guard'] 
)

TRACE_INFO =  Info(
    'trace',
    'Trace information for the selected finding.'
)

LATEST_FINDING_INFO = Info(
    'latest_finding',
    'Context for the latest data finding that requires action.'
)

def register_data_finding(id: str, model_name: str, guard_name: str, prompt: str):
    REGISTERED_LABELS.add((model_name, guard_name))
    DATA_FINDINGS_TOTAL.labels(model=model_name, guard=guard_name).inc()
    LATEST_FINDING_INFO.info({
        'id': id,
        'model': model_name,
        'guard': guard_name,
        'message': prompt,
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

def start_metrics_server(port=8004):
    """
    Starts the Prometheus HTTP server and the metric generation
    in a non-blocking background thread.
    """
    start_http_server(port)
    print(f"Prometheus metrics server started on port {port}...")