from prometheus_client import start_http_server, Counter

REQUESTS_TOTAL = Counter(
    'llm_requests_total',
    'Total number of successful LLM requests.',
    ['model', 'guard']
)

UNSAFE_PROMPTS_TOTAL = Counter(
    'llm_unsafe_prompts_total',
    'Total number of requests flagged as unsafe by the guard.',
    ['model', 'guard']
)

REPROMPTING_TOTAL = Counter(
    'llm_reprompting_total',
    'Total count of internal re-prompting or re-generations.',
    ['model', 'guard']
)

def register_request(model_name: str, guard_name: str):
    REQUESTS_TOTAL.labels(model=model_name, guard=guard_name).inc()

def register_unsafe_request(model_name: str, guard_name: str):
    UNSAFE_PROMPTS_TOTAL.labels(model=model_name, guard=guard_name).inc()

def register_reprompting(model_name: str, guard_name: str):
    REPROMPTING_TOTAL.labels(model=model_name, guard=guard_name).inc()


def start_metrics_server(port=8000):
    """
    Starts the Prometheus HTTP server and the metric generation
    in a non-blocking background thread.
    """
    start_http_server(port)
    print(f"Prometheus metrics server started on port {port}...")