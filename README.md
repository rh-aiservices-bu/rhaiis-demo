# Red Hat AI Inference Demos

Demonstrations of [Red Hat AI Inference](https://www.redhat.com/en/technologies/cloud-computing/ai-inference) capabilities across deployment targets.

## Demos

### [Linux (Bare Metal / VM)](linux/)

Deploy a GPU-accelerated CRM assistant on RHEL 10 using IBM Granite models, vLLM, and PostgreSQL. Designed for single-node EC2/bare-metal environments with NVIDIA GPUs.

### [Kubernetes (llm-d Intelligent Scheduling)](k8s/llm-d/)

Benchmark llm-d's intelligent inference scheduling against vanilla vLLM round-robin routing on any Kubernetes cluster (OpenShift, EKS, AKS, CoreWeave, etc.) using 3 GPU replicas. Demonstrates how prefix-cache-aware routing delivers higher KV cache hit rates and dramatically lower time-to-first-token latency.

## Prerequisites

| Demo | Requirements |
|------|-------------|
| Linux | RHEL 10, NVIDIA GPU (A10G+), 64GB RAM |
| Kubernetes | K8s cluster with GPU nodes, KServe, llm-d operator, Gateway API |

## License

MIT License - see [LICENSE](LICENSE) for details.
