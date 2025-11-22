from prometheus_client import start_http_server, Counter

DATA_FINDINGS_TOTAL = Counter(
    'data_findings_total',
    'Total number of data findings.',
    ['model', 'guard'] 
)

def register_data_finding(model_name: str, guard_name: str):
    DATA_FINDINGS_TOTAL.labels(model=model_name, guard=guard_name).inc()

def start_metrics_server(port=8004):
    """
    Starts the Prometheus HTTP server and the metric generation
    in a non-blocking background thread.
    """
    start_http_server(port)
    print(f"Prometheus metrics server started on port {port}...")