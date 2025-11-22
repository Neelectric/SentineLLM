import time
from prometheus_client import start_http_server, Gauge
import random

# Create a Gauge metric
# 'my_test_gauge' is the metric name
# 'Just a test metric' is the metric description
MY_TEST_GAUGE = Gauge('my_test_gauge', 'Just a test metric that increases over time')

def process_request():
    """A loop that updates the metric value."""
    while True:
        # Increment the gauge by a random number between 0 and 1
        MY_TEST_GAUGE.inc(random.random())
        time.sleep(1) # Wait 1 second

if __name__ == '__main__':
    # Start up the HTTP server to expose the metrics.
    # Metrics will be available at http://localhost:8000/metrics
    start_http_server(8000)
    print("Prometheus metrics server started on port 8000...")
    
    # Generate the metric data forever
    process_request()