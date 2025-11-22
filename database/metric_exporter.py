from prometheus_client import start_http_server, Gauge

REGISTERED_LABELS = set()
DATA_FINDINGS_TOTAL = Gauge(
    'data_findings_total',
    'Total number of data findings.',
    ['model', 'guard'] 
)

def register_data_finding(model_name: str, guard_name: str):
    REGISTERED_LABELS.add((model_name, guard_name))
    DATA_FINDINGS_TOTAL.labels(model=model_name, guard=guard_name).inc()

def reset_findings():
    labels_to_wipe = list(REGISTERED_LABELS)
    for model, guard in labels_to_wipe:
            DATA_FINDINGS_TOTAL.labels(model=model, guard=guard).set(0)

def start_metrics_server(port=8004):
    """
    Starts the Prometheus HTTP server and the metric generation
    in a non-blocking background thread.
    """
    start_http_server(port)
    print(f"Prometheus metrics server started on port {port}...")