# Sentinel Trace: Open-Source AI Monitoring Dashboard With Pre-Training Data Tracing And In-Flight DPO Dataset Creation
Note: This README was written with the help of Claude. Feel free to also refer to our report under https://docs.google.com/document/d/1FcI0xWdU8hrhCA6KTin5BG4n8h8b6LKuNvQ5iUqLFWU/edit?usp=sharing.
## Abstract

SentinelTrace is a comprehensive safety monitoring system for Large Language Models (LLMs) that implements a closed-loop feedback cycle for detecting, analyzing, and mitigating unsafe model outputs. The system combines adversarial testing, guardrail evaluation, training data attribution, and automated dataset generation to enable continuous model improvement through Direct Preference Optimization (DPO).

## System Architecture

The platform employs a microservices architecture with the following components:

- **Frontier LLM Server** (Port 8001): OLMo-2-0425-1B-Instruct served via vLLM
- **Guard Model Server** (Port 8002): Qwen3Guard-Gen-0.6B for safety classification
- **Database API** (Port 8003): FastAPI service managing SQLite persistence
- **Metrics Exporters** (Ports 8000, 8004): Prometheus metric endpoints
- **Monitoring Stack**: Prometheus (Port 9090) and Grafana (Port 3000)

## Core Functionality

### 1. Adversarial Testing

The user simulator (`src/async_user_simulator.py`) generates synthetic adversarial traffic to evaluate model safety under load. Key features include:

- Asynchronous request processing with exponential arrival times (50 requests/second)
- Combined dataset from WildGuardMix and WildJailBreak benchmarks
- Automatic re-prompting with safety instructions for flagged outputs
- Generation of preference pairs for DPO training

### 2. Safety Evaluation Pipeline

The dual-model architecture separates generation from safety classification:

1. Prompts are submitted to the frontier model
2. Responses are evaluated by the guard model
3. Unsafe outputs trigger re-generation with injected safety constraints
4. All interactions are logged with guard ratings and timestamps

### 3. Training Data Attribution

Integration with OLMoTrace (Liu et al., 2025) enables tracing model outputs to their origins in the pre-training corpus:

- Queries Allen AI's Infini-gram API for n-gram occurrence lookup
- Retrieves source documents from training data shards
- Computes longest common substring (LCS) for precise attribution
- Returns HTML-formatted results with highlighted matching segments

### 4. Automated Dataset Curation

The refinement endpoint (`/refine`) automates the creation of DPO training datasets:

- Extracts unsafe outputs and their safe counterparts from the database
- Formats data according to TRL's DPO trainer specifications
- Publishes datasets to HuggingFace under `Neelectric/<model>_DPO`
- Enables immediate fine-tuning for model improvement

## API Endpoints

### Database Service (Port 8003)

- `POST /data`: Log new findings with prompt, response, and guard evaluation
- `GET /data`: Retrieve all logged entries
- `GET /data_unsafe`: Filter for entries flagged as unsafe
- `GET /refine`: Generate and upload DPO dataset to HuggingFace
- `GET /trace?finding_id=<id>`: Trace specific finding to training data
- `GET /wipedb`: Clear all database entries

## Monitoring and Observability

### Prometheus Metrics

**User Simulator Metrics:**
- `llm_requests_total`: Total requests processed
- `llm_unsafe_prompts_total`: Requests flagged by guard model
- `llm_reprompting_total`: Re-generation attempts

**Database Metrics:**
- `data_findings_total`: Count of logged findings
- `latest_finding`: Metadata about most recent entry
- `trace`: OLMoTrace attribution results
- `dataset_refinement_progress`: DPO dataset creation status

### Grafana Dashboard

Pre-configured dashboard (`GrafanaDashboard.json`) visualizes:
- Request throughput and error rates
- Safety violation trends
- Re-prompting effectiveness
- Dataset refinement progress

## Installation and Setup

### Prerequisites

- Python 3.11+
- CUDA-compatible GPU (recommended: 2 GPUs for parallel model serving)
- UV package manager

### Dependency Installation

```bash
uv sync
```

### Service Startup

1. **Start Prometheus:**
   ```bash
   ./prometheus --config.file=prometheus.yml
   ```

2. **Start Grafana:**
   ```bash
   grafana-server.exe
   ```
   Access at `http://localhost:3000`
   or on MacOS
   ```bash
   brew services start grafana
   ```

3. **Start Frontier Model:**
   ```bash
   CUDA_VISIBLE_DEVICES=0 vllm serve allenai/OLMo-2-0425-1B-Instruct --port 8001
   ```

4. **Start Guard Model:**
   ```bash
   CUDA_VISIBLE_DEVICES=1 vllm serve Qwen/Qwen3Guard-Gen-0.6B --port 8002
   ```

5. **Start Database Service:**
   ```bash
   cd database
   python main.py
   ```

6. **Run User Simulator:**
   ```bash
   cd src
   python async_user_simulator.py
   ```

## DPO Training
NOTE: Not yet fully implented
Fine-tune models using collected preference pairs:

```bash
cd dpo_training
python dpo_train.py
```

## Technical Implementation

### Database Schema

```sql
CREATE TABLE data_entries (
    prompt_id TEXT PRIMARY KEY,
    prompt TEXT,
    answer TEXT,
    rejected_answer TEXT,
    refusal BOOLEAN,
    guard_rating TEXT,
    guard_model TEXT,
    model TEXT,
    timestamp TEXT
);
```

### Dataset Construction

Safety datasets are sourced from Allen AI repositories:
- **WildGuardMix**: General prompt-response pairs (subsampled)
- **WildJailBreak**: Adversarial jailbreak attempts

Combined datasets are shuffled and deduplicated before testing.

### OLMoTrace Methodology

The attribution pipeline implements the following algorithm:

1. Query Infini-gram API for n-gram occurrences in training corpus
2. Retrieve document content from specified corpus shards
3. Compute token-level longest common substring between output and source
4. Extract context window (50 tokens before/after match)
5. Generate HTML with highlighting for visual inspection

## Research Context

This system implements findings from recent AI safety research:

- **Training Data Attribution**: Based on OLMoTrace (Liu et al., 2025, arXiv:2504.07096)
- **Direct Preference Optimization**: Rafailov et al., 2023
- **Adversarial Testing**: WildGuardMix and WildJailBreak benchmarks

## Performance Characteristics

- Request throughput: Up to 50 requests/second (exponential distribution)
- Guard model latency: Sub-second classification
- Database write latency: Async, non-blocking
- Training data attribution: 2-5 seconds per query (API-dependent)

## Limitations and Future Work

- Current implementation uses small models for demonstration purposes
- OLMoTrace limited to OLMo family training data
- Single-node deployment; horizontal scaling not yet implemented
- Guard model accuracy depends on specific safety taxonomy

## References

- Liu et al. (2025). "OLMoTrace: Tracing Language Model Outputs to Training Data." arXiv:2504.07096
- Rafailov et al. (2023). "Direct Preference Optimization: Your Language Model is Secretly a Reward Model."
- Allen AI Infini-gram: https://infini-gram.readthedocs.io/

## License

See LICENSE file for details.

## Citation

If you use this system in your research, please cite:

```bibtex
@software{sentineltrace2025,
  title={Sentinel Trace: Open-Source AI Monitoring Dashboard With Pre-Training Data Tracing And In-Flight DPO Dataset Creation},
  author={Neel Rajani and Pedro Ginel Camacho},
  year={2025},
  url={https://github.com/Neelectric/SentineLLM}
}
```
