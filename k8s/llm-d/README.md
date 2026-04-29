# Red Hat AI Inference - llm-d Intelligent Scheduling Benchmark

This benchmark compares vanilla vLLM (round-robin routing) against llm-d (intelligent scheduling) using identical hardware: 3 NVIDIA MIG 3g.71gb GPU slices serving Qwen/Qwen3-4B across 3 replicas.

## Prerequisites

- Kubernetes cluster with GPU nodes (OpenShift, EKS, AKS, CoreWeave, etc.)
- [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/getting-started.html) installed
- [Node Feature Discovery (NFD)](https://kubernetes-sigs.github.io/node-feature-discovery/) installed
- [KServe](https://kserve.github.io/website/) installed
- [llm-d operator](https://github.com/llm-d/llm-d-operator) installed
- [Gateway API](https://gateway-api.sigs.k8s.io/) CRDs and an implementation (Envoy Gateway, Istio, etc.)
- `kubectl` or `oc` CLI configured
- 3 GPU instances available (MIG 3g.71gb or equivalent)

> **Note:** This guide uses `kubectl` commands throughout. On OpenShift, you can substitute `oc` for `kubectl`.

## Step 0: Gateway Setup (if not already present)

If your cluster does not already have a Gateway API gateway configured, create one:

```bash
kubectl apply -f llm-d/base/gateway.yaml
```

Edit `llm-d/base/gateway.yaml` to set the `gatewayClassName` for your environment:
- **OpenShift**: `openshift-default`
- **Envoy Gateway**: `eg`
- **Istio**: `istio`

Verify the gateway is programmed:

```bash
kubectl get gateways -A
```

> **Skip this step** if your cluster already has a gateway (e.g., OpenShift clusters with `openshift-ai-inference` gateway pre-configured).

## Step 1: Enable Metrics Collection

### OpenShift

Enable user workload monitoring:

```bash
kubectl -n openshift-monitoring get configmap cluster-monitoring-config -o yaml 2>/dev/null || \
cat << 'EOF' | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-monitoring-config
  namespace: openshift-monitoring
data:
  config.yaml: |
    enableUserWorkload: true
EOF
```

Verify monitoring pods:

```bash
kubectl -n openshift-user-workload-monitoring get pod
```

### Other Kubernetes Distributions

Ensure Prometheus is installed (e.g., via [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)) and configured to scrape pod metrics from your target namespace.

## Step 2: Deploy Performance Dashboard

### OpenShift Console Dashboard

To use the dashboard on OpenShift, edit `monitoring/openshift-dashboard.yaml` and uncomment the `namespace: openshift-config-managed` and `console.openshift.io/*` labels, then apply:

```bash
kubectl apply -f monitoring/openshift-dashboard.yaml
```

Access via **Observe > Dashboards > LLM-D Performance Dashboard** in the OpenShift Console.

### Grafana (Any Cluster)

The dashboard JSON in `monitoring/openshift-dashboard.yaml` is standard Grafana-compatible JSON. Import it directly into your Grafana instance, or apply the ConfigMap to your monitoring namespace and configure Grafana to auto-load dashboards from it.

**Key Metrics:**
- **KV Cache Hit Rate**: Higher is better (llm-d ~90%+ vs round-robin ~60%)
- **Time to First Token (TTFT)**: Lower is better
- **Requests per Second**: Overall throughput
- **GPU Cache Utilization**: Should be balanced across replicas

## Step 3: Generate Test Data

### Understanding KV Cache Capacity

After vLLM loads the model, check logs for cache size:

```
INFO [kv_cache_utils.py] GPU KV cache size: 350,304 tokens
```

### Create Benchmark Namespace and PVC

```bash
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: Namespace
metadata:
  name: demo-llm-benchmarks
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: benchmark-data
  namespace: demo-llm-benchmarks
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
EOF
```

### Generate and Upload Test Prompts

Install the test data generator:

```bash
pip install pandas guidellm
```

Generate prompts sized to exercise KV cache reuse:

```bash
cd test-data-generator/prefix
python kv-cache-prompt-generator.py \
  --kv-cache-size 350304 \
  --num-replicas 3 \
  --prompt-size 8000 \
  --num-pairs 8 \
  --output prompts.csv
```

Upload to the cluster:

```bash
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: benchmark-data-loader
  namespace: demo-llm-benchmarks
spec:
  restartPolicy: Never
  containers:
    - name: loader
      image: registry.access.redhat.com/ubi9/ubi:latest
      command: ["sleep", "3600"]
      volumeMounts:
        - name: data
          mountPath: /data
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: benchmark-data
EOF

kubectl wait --for=condition=ready pod/benchmark-data-loader -n demo-llm-benchmarks --timeout=120s
kubectl cp prompts.csv demo-llm-benchmarks/benchmark-data-loader:/data/prompts.csv
kubectl delete pod benchmark-data-loader -n demo-llm-benchmarks
```

## Step 4: Deploy vLLM Baseline (4 Replicas)

Deploy vanilla vLLM with round-robin load balancing:

```bash
kubectl apply -k vllm/qwen
```

Wait for all replicas:

```bash
kubectl wait --for=condition=ready pod \
  -l serving.kserve.io/inferenceservice=qwen-vllm \
  -n demo-llm --timeout=600s

kubectl get pods -n demo-llm -l serving.kserve.io/inferenceservice=qwen-vllm
```

The deployment creates:
- **ServingRuntime** (`vllm-runtime`): upstream vLLM with `--max-model-len=16000`
- **InferenceService** (`qwen-vllm`): 3 replicas, 1 MIG GPU each
- **Service** (`qwen-vllm-lb`): ClusterIP load balancer
- **PodMonitor**: Prometheus metrics scraping

## Step 5: Benchmark vLLM

Run GuideLLM against the vLLM baseline:

```bash
kubectl apply -k guidellm/overlays/vllm

kubectl logs -f job/vllm-guidellm-benchmark -n demo-llm-benchmarks
```

Wait for completion:

```bash
kubectl wait --for=condition=complete job/vllm-guidellm-benchmark \
  -n demo-llm-benchmarks --timeout=600s
```

Observe in your dashboard: KV Cache Hit Rate ~54%, elevated TTFT values.

## Step 6: Replace vLLM with llm-d

Tear down the vLLM baseline:

```bash
kubectl delete -k vllm/qwen
```

Deploy llm-d with intelligent scheduling:

```bash
kubectl apply -k llm-d/qwen
```

Wait for replicas:

```bash
kubectl wait --for=condition=ready pod \
  -l app.kubernetes.io/name=qwen \
  -n demo-llm --timeout=600s

kubectl get pods -n demo-llm -l app.kubernetes.io/name=qwen
```

The llm-d deployment includes:
- **Gateway** (optional, see Step 0): Standard Gateway API ingress
- **HardwareProfile**: MIG 3g.71gb GPU resource spec
- **LLMInferenceService** (`qwen`): 3 replicas with intelligent scoring:
  - `prefix-cache-scorer` (weight: 3): Routes to replicas with cached prefix
  - `active-request-scorer` (weight: 2): Balances active requests
  - `queue-scorer` (weight: 2): Avoids overloaded replicas

## Step 7: Benchmark llm-d

Run GuideLLM against llm-d:

```bash
kubectl apply -k guidellm/overlays/llm-d

kubectl logs -f job/llm-d-guidellm-benchmark -n demo-llm-benchmarks
```

Wait for completion:

```bash
kubectl wait --for=condition=complete job/llm-d-guidellm-benchmark \
  -n demo-llm-benchmarks --timeout=600s
```

Observe in your dashboard: KV Cache Hit Rate ~92%, steadily declining TTFT values.

## Step 8: Compare Results

### Time to First Token (TTFT)

| Concurrency | vLLM Mdn (ms) | vLLM p95 (ms) | llm-d Mdn (ms) | llm-d p95 (ms) | Improvement |
|---|---|---|---|---|---|
| 8 | ~150 | ~675 | ~52 | ~556 | ~65% faster (Mdn) |
| 16 | ~204 | ~875 | ~60 | ~310 | ~70% faster (Mdn) |

### KV Cache Hit Rate

| System | Hit Rate |
|---|---|
| vLLM (round-robin) | ~60% |
| llm-d (intelligent) | ~92% |

### Why llm-d Performs Better

1. **Lower TTFT**: Routes to replicas with cached prefixes, avoiding redundant prefill computation
2. **Higher cache hit rates**: Round-robin gives repeated prompts 1-in-N chance of hitting the cached replica; llm-d's prefix-cache-scorer routes correctly every time

## Clean Up

```bash
kubectl delete -k llm-d/qwen
kubectl delete -f monitoring/openshift-dashboard.yaml
kubectl delete namespace demo-llm-benchmarks
```

## Adapting for Your Environment

### Different GPU Types

Edit the resource requests in `vllm/base/inference-service.yaml` and `llm-d/base/llm-infra.yaml`:

```yaml
resources:
  limits:
    nvidia.com/gpu: "1"        # Full GPU
    # nvidia.com/mig-3g.71gb: "1"  # MIG slice
```

### Different Models

Create a new Kustomize overlay (like `vllm/qwen/`) pointing to your model's Hugging Face URI.

### Gateway Configuration

The `llm-d/base/gateway.yaml` creates a Gateway resource. Update the `gatewayClassName` to match your cluster's Gateway API implementation:
- **OpenShift**: `openshift-default`
- **Envoy Gateway**: `eg`
- **Istio**: `istio`

If your cluster already has a gateway configured, you can skip applying `gateway.yaml` and remove it from `llm-d/base/kustomization.yaml`.
