# How to run

## Grafana
Go to where you donwloaded it (C:Program Files/GrafanaLabs/grafana/bin) and grafana-server.exe as admin, default credentials are usr: admin pwd: admin

## Run Prometheus server
1 - ensure the prometheys.yml is targettting the same ports you expose on
2 - run in the terminal:
    Windows: `./prometheus.exe --config.file=prometheus.yml`
    Linux: `chmod`
3 - verify targets at localhost:9090

## Run python database
go to database file and run: "uvicorn main:app --reload"

# How to expose metrics in python
- Make sure you ahve prometheus_client lib installed
- from prometheus_client import start_http_server, Gauge (or any other type of metric)
- instantiate a metering object: myGauge = Gauge("name","desc",["label1key","label2key"]) (you need to set labels later with myGauge.labels("label1value","label2value"))
- run start_http_server(8000) in main file to expose metrics on port 8000
- use the metering object to expose a metric: myGauge.inc(1)

# How to make requests from Grafana to python
- In grafana setup a canvas element and create a button type
- In the config set up the sending on a request to a given url (eg.: localhost:8000/button-action)
- In python make sure the main loop runs: uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True) or something like that
- Define an endpoint for the request:

```
@app.post("/button-action")
async def handle_button_press(request: Request):
...
```

### Different metrics we can use:
- Counter, exposes a number and they only go up (.inc(int))
- Gauge, exposes a number but they can go up and down (.inc(int) and .dec(int))
    use @gaugeInstance.track_progess() on top of a function to inc when functhing entered and dec when exited
- Summary, size and number of events, for example tracking latency of a function (.observe(int))
- Histogram, tacks number and size of events in buckets, use buckets arg to change (.observe(int))
- Info, key value pairs, apparently they don't work in multiprocess mode (.info(dict))
- Enum, which of a set of states is true (.state(string)), so you can switch what the state of the process is

# How to serve the 'frontier' LLM and the guard on one GPU
Serving the LLM
```
CUDA_VISIBLE_DEVICES=0 vllm serve \
allenai/OLMo-2-0425-1B-Instruct \
--port 8001 \
--max-model-len 4096 \
--gpu-memory-utilization 0.9
```

Serving the guard
```
CUDA_VISIBLE_DEVICES=1 vllm serve \
Qwen/Qwen3Guard-Gen-0.6B \
--port 8002 \
--max-model-len 8192 \
--gpu-memory-utilization 0.9
```


