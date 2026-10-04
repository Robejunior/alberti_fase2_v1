# 🚀 Guia de Deployment - TIA Fase 2

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Docker - Desenvolvimento](#docker---desenvolvimento)
3. [Docker Compose - Local](#docker-compose---local)
4. [Kubernetes - Produção](#kubernetes---produção)
5. [GitHub Actions - CI/CD](#github-actions---cicd)
6. [Monitoramento e Logs](#monitoramento-e-logs)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

```
┌──────────────────────────────────────────────────────────┐
│                    PIPELINE DE DEPLOYMENT                 │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  1. Desenvolvimento Local                                 │
│     ├─ docker-compose up                                 │
│     └─ Testes locais com MySQL containerizado             │
│                                                            │
│  2. GitHub Push                                           │
│     ├─ CI/CD dispara (GitHub Actions)                    │
│     ├─ Testes automatizados                              │
│     ├─ Build Docker image                                │
│     └─ Push para Docker Registry                         │
│                                                            │
│  3. Pull Request → Staging                                │
│     ├─ Deploy para Kubernetes Staging                    │
│     └─ Smoke tests                                        │
│                                                            │
│  4. Merge para main → Produção                            │
│     ├─ Security scanning                                  │
│     ├─ Deploy para Kubernetes Production                 │
│     ├─ Blue-Green Deployment                             │
│     └─ Rollback automático se falhar                     │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

---

## 🐳 Docker - Desenvolvimento

### Construir Imagem Docker

```bash
# Build local
docker build -t tia-api:latest .

# Verificar imagem
docker images | grep tia-api
```

### Correr Container Isolado

```bash
# Com variáveis de ambiente
docker run -d \
  --name tia-api-dev \
  -p 5000:5000 \
  -e MYSQL_HOST=host.docker.internal \
  -e MYSQL_USER=root \
  -e MYSQL_PASSWORD=Pan.tin.fox-191 \
  -e MYSQL_DATABASE=tia_fase2 \
  -e DEBUG=True \
  tia-api:latest

# Ver logs
docker logs -f tia-api-dev

# Parar container
docker stop tia-api-dev
docker rm tia-api-dev
```

### Tamanho da Imagem

```bash
# Verificar tamanho
docker images tia-api
# REPOSITORY   TAG      IMAGE ID     SIZE
# tia-api      latest   abc123...    250MB  (Multi-stage reduz para ~250MB)
```

---

## 🐳 Docker Compose - Local (Recomendado)

### Iniciar Ambiente Completo

```bash
# Criar arquivo .env (se não existir)
cp .env.example .env

# Iniciar serviços
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f api

# Parar tudo
docker-compose down

# Parar e remover volumes (limpar tudo)
docker-compose down -v
```

### Acessar Serviços

```bash
# API
curl http://localhost:5000/api/v1/saude

# MySQL
mysql -h 127.0.0.1 -u root -p tia_fase2

# Conectar ao container MySQL
docker-compose exec db mysql -u root -p tia_fase2
```

### Estrutura de Volumes

```
Volume: mysql_data
  ├─ Persiste entre restarts
  ├─ Local: /var/lib/docker/volumes/tia_api_mysql_data/_data
  └─ Limpar: docker volume rm tia_api_mysql_data
```

---

## ☸️ Kubernetes - Produção

### Pré-requisitos

```bash
# Instalar kubectl
kubectl version --client

# Verificar conexão com cluster
kubectl cluster-info

# Instalar Helm (opcional, para gerenciamento simplificado)
helm version
```

### Deploy Inicial

```bash
# Aplicar configurações
kubectl apply -f k8s-deployment.yaml

# Verificar namespace
kubectl get namespaces
kubectl get all -n tia-projeto10

# Verificar pods
kubectl get pods -n tia-projeto10 -w

# Ver status do deployment
kubectl describe deployment tia-api -n tia-projeto10
```

### Logs e Debugging

```bash
# Ver logs da API
kubectl logs -f deployment/tia-api -n tia-projeto10

# Ver logs de um pod específico
kubectl logs -f pod/tia-api-xyz -n tia-projeto10

# Executar comando no container
kubectl exec -it pod/tia-api-xyz -n tia-projeto10 -- bash

# Descrição detalhada do pod
kubectl describe pod/tia-api-xyz -n tia-projeto10
```

### Escalar Manualmente

```bash
# Aumentar/diminuir replicas
kubectl scale deployment tia-api --replicas=5 -n tia-projeto10

# Ver HPA status
kubectl get hpa -n tia-projeto10

# Monitorar HPA
kubectl describe hpa tia-api-hpa -n tia-projeto10
```

### Atualizar Imagem

```bash
# Forçar rollout de nova imagem
kubectl set image deployment/tia-api \
  api=ghcr.io/seu-usuario/tia-api:new-tag \
  -n tia-projeto10

# Acompanhar deployment
kubectl rollout status deployment/tia-api -n tia-projeto10

# Histórico de deployments
kubectl rollout history deployment/tia-api -n tia-projeto10

# Rollback para versão anterior
kubectl rollout undo deployment/tia-api -n tia-projeto10
```

### Acessar Serviço

```bash
# Obter IP externo do serviço
kubectl get svc tia-api-service -n tia-projeto10

# Port-forward para testes locais
kubectl port-forward svc/tia-api-service 8080:80 -n tia-projeto10

# Acessar em http://localhost:8080/api/v1/saude
```

### Deletar Resources

```bash
# Remover tudo do namespace
kubectl delete namespace tia-projeto10

# Remover um recurso específico
kubectl delete deployment tia-api -n tia-projeto10
```

---

## 🔄 GitHub Actions - CI/CD

### Configuração de Secrets

No repositório GitHub, vá para **Settings → Secrets and variables → Actions** e adicione:

```
KUBE_CONFIG_STAGING = <conteúdo de ~/.kube/config>
KUBE_CONFIG_PRODUCTION = <conteúdo de ~/.kube/config>
```

### Workflow Automático

```
Push para branch
    ↓
GitHub Actions Dispara
    ├─ Job 1: Test (rodar testes)
    ├─ Job 2: Build (construir Docker image)
    ├─ Job 3: Deploy Staging (se PR)
    └─ Job 4: Deploy Production (se merge em main)
```

### Monitorar CI/CD

```bash
# Ver ações no repositório
https://github.com/seu-usuario/tia-api/actions

# CLI: listar workflows
gh workflow list

# CLI: ver resultado de uma run
gh run list --repo seu-usuario/tia-api
gh run view <run-id>
```

---

## 📊 Monitoramento e Logs

### Prometheus + Grafana

```yaml
# Adicionar ao docker-compose.yml (futuro)
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
```

### Ver Logs da Aplicação

```bash
# Docker
docker logs tia_api

# Docker Compose
docker-compose logs api

# Kubernetes
kubectl logs deployment/tia-api -n tia-projeto10 --tail=100

# Salvar logs em arquivo
kubectl logs deployment/tia-api -n tia-projeto10 > api-logs.txt
```

### Health Checks

```bash
# Via Docker
curl http://localhost:5000/api/v1/saude

# Via Kubernetes
kubectl get pods -n tia-projeto10 -o wide

# Status das probes
kubectl describe pod <pod-name> -n tia-projeto10 | grep -A 5 "Liveness\|Readiness"
```

---

## 🔧 Troubleshooting

### Docker Compose não inicia

```bash
# Verificar se porta está em uso
netstat -an | grep 5000
netstat -an | grep 3306

# Limpar e reconstruir
docker-compose down -v
docker-compose build --no-cache
docker-compose up

# Ver logs de erro
docker-compose logs db api
```

### Erro de Conexão MySQL

```bash
# Verificar se MySQL está rodando
docker-compose ps db

# Verificar conectividade
docker-compose exec api curl http://db:3306

# Verificar variáveis de ambiente
docker-compose config | grep MYSQL
```

### Pod não inicia em Kubernetes

```bash
# Ver eventos do pod
kubectl describe pod <pod-name> -n tia-projeto10

# Ver logs de erro
kubectl logs <pod-name> -n tia-projeto10

# Verificar limitações de recurso
kubectl top nodes
kubectl top pods -n tia-projeto10
```

### Erro "ImagePullBackOff"

```bash
# Verificar se imagem existe no registry
docker image inspect ghcr.io/usuario/tia-api:tag

# Re-fazer push
docker push ghcr.io/usuario/tia-api:tag

# Verificar credenciais
kubectl get secrets -n tia-projeto10
```

### Aplicação lenta / timeout

```bash
# Aumentar recursos
kubectl set resources deployment tia-api \
  --requests=cpu=500m,memory=512Mi \
  --limits=cpu=1000m,memory=1Gi \
  -n tia-projeto10

# Verificar métricas
kubectl top pods -n tia-projeto10 --use-protocol-buffers

# Verificar query performance (MySQL)
kubectl exec -it <mysql-pod> -n tia-projeto10 -- \
  mysql -u root -p -e "SHOW PROCESSLIST;"
```

---

## 📋 Checklist de Deployment

### Antes de Deploy em Staging

```
Código:
 ☐ Testes passando (8/8 segurança, 8/8 funcional)
 ☐ Sem credenciais hardcoded
 ☐ Linting passou
 ☐ Code review aprovado

Imagem Docker:
 ☐ Dockerfile criado e testado
 ☐ Multi-stage build configurado
 ☐ Usuário não-root adicionado
 ☐ Health checks implementados

Kubernetes:
 ☐ Manifests validados
 ☐ Secrets configurados
 ☐ PVC para dados persistentes
 ☐ Resource requests/limits definidos
```

### Antes de Deploy em Produção

```
Segurança:
 ☐ Trivy scan - sem vulnerabilidades críticas
 ☐ RBAC configurado
 ☐ NetworkPolicy ativo
 ☐ Secrets não expostos em logs

Performance:
 ☐ Load testing passou (>100 req/s)
 ☐ Memory leaks investigados
 ☐ Database replication ativo
 ☐ Backup automático configurado

Monitoramento:
 ☐ Prometheus + Grafana ativo
 ☐ Alertas configurados
 ☐ Log aggregation ativo
 ☐ Plano de rollback documentado
```

---

## 📞 Suporte

### Verificar Status

```bash
# Resumo geral
kubectl get all -n tia-projeto10

# Verificar eventos
kubectl get events -n tia-projeto10 --sort-by=.metadata.creationTimestamp

# Diagnosticar problema
kubectl describe deployment/tia-api -n tia-projeto10
kubectl describe pvc -n tia-projeto10
kubectl describe hpa -n tia-projeto10
```

---

**Última atualização:** 2026-10-03

**Versão:** 1.0.0

**Status:** ✅ Completo e Pronto para Deploy
