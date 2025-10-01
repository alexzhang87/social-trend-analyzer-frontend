# Makefile for Trend Analyzer Backend
# 使用 PowerShell 作为默认 shell（Windows 兼容）
SHELL := powershell.exe
.SHELLFLAGS := -NoProfile -Command

# 项目配置
PROJECT_NAME := trend-analyzer-backend
PYTHON := python
PIP := pip
PYTEST := pytest
BLACK := black
FLAKE8 := flake8
MYPY := mypy
ISORT := isort
BANDIT := bandit
COVERAGE := coverage

# 目录配置
SRC_DIR := app
TEST_DIR := tests
DOCS_DIR := docs
COVERAGE_DIR := htmlcov

# 颜色定义（PowerShell 兼容）
define PRINT_HELP
	@echo "Available commands:"
	@echo "  help          Show this help message"
	@echo "  install       Install dependencies"
	@echo "  install-dev   Install development dependencies"
	@echo "  test          Run tests"
	@echo "  test-cov      Run tests with coverage"
	@echo "  test-fast     Run tests in parallel"
	@echo "  lint          Run all linting tools"
	@echo "  format        Format code with black and isort"
	@echo "  type-check    Run type checking with mypy"
	@echo "  security      Run security checks with bandit"
	@echo "  quality       Run all quality checks"
	@echo "  clean         Clean build artifacts"
	@echo "  dev-setup     Setup development environment"
	@echo "  run           Run the development server"
	@echo "  run-prod      Run the production server"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-run    Run Docker container"
	@echo "  docs          Generate documentation"
	@echo "  pre-commit    Install pre-commit hooks"
endef

# 默认目标
.PHONY: help
help:
	$(PRINT_HELP)

# 安装依赖
.PHONY: install
install:
	@echo "Installing dependencies..."
	$(PIP) install -r requirements.txt

.PHONY: install-dev
install-dev:
	@echo "Installing development dependencies..."
	$(PIP) install -r requirements-test.txt
	$(PIP) install -e .

# 测试相关
.PHONY: test
test:
	@echo "Running tests..."
	$(PYTEST) $(TEST_DIR) -v

.PHONY: test-cov
test-cov:
	@echo "Running tests with coverage..."
	$(PYTEST) $(TEST_DIR) --cov=$(SRC_DIR) --cov-report=html --cov-report=term-missing

.PHONY: test-fast
test-fast:
	@echo "Running tests in parallel..."
	$(PYTEST) $(TEST_DIR) -n auto

.PHONY: test-unit
test-unit:
	@echo "Running unit tests..."
	$(PYTEST) $(TEST_DIR) -m "unit" -v

.PHONY: test-integration
test-integration:
	@echo "Running integration tests..."
	$(PYTEST) $(TEST_DIR) -m "integration" -v

.PHONY: test-api
test-api:
	@echo "Running API tests..."
	$(PYTEST) $(TEST_DIR) -m "api" -v

.PHONY: test-watch
test-watch:
	@echo "Running tests in watch mode..."
	$(PYTEST) $(TEST_DIR) -f

# 代码质量检查
.PHONY: lint
lint:
	@echo "Running linting..."
	$(FLAKE8) $(SRC_DIR) $(TEST_DIR)

.PHONY: format
format:
	@echo "Formatting code..."
	$(BLACK) $(SRC_DIR) $(TEST_DIR)
	$(ISORT) $(SRC_DIR) $(TEST_DIR)

.PHONY: format-check
format-check:
	@echo "Checking code formatting..."
	$(BLACK) --check $(SRC_DIR) $(TEST_DIR)
	$(ISORT) --check-only $(SRC_DIR) $(TEST_DIR)

.PHONY: type-check
type-check:
	@echo "Running type checking..."
	$(MYPY) $(SRC_DIR)

.PHONY: security
security:
	@echo "Running security checks..."
	$(BANDIT) -r $(SRC_DIR) -f json -o bandit-report.json
	$(BANDIT) -r $(SRC_DIR)

.PHONY: quality
quality: format-check lint type-check security
	@echo "All quality checks completed!"

# 清理
.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
	if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
	if (Test-Path "*.egg-info") { Remove-Item -Recurse -Force "*.egg-info" }
	if (Test-Path "$(COVERAGE_DIR)") { Remove-Item -Recurse -Force "$(COVERAGE_DIR)" }
	if (Test-Path ".coverage") { Remove-Item -Force ".coverage" }
	if (Test-Path "coverage.xml") { Remove-Item -Force "coverage.xml" }
	if (Test-Path "bandit-report.json") { Remove-Item -Force "bandit-report.json" }
	if (Test-Path ".pytest_cache") { Remove-Item -Recurse -Force ".pytest_cache" }
	if (Test-Path ".mypy_cache") { Remove-Item -Recurse -Force ".mypy_cache" }
	Get-ChildItem -Path . -Name "__pycache__" -Recurse | Remove-Item -Recurse -Force
	Get-ChildItem -Path . -Name "*.pyc" -Recurse | Remove-Item -Force
	Get-ChildItem -Path . -Name "*.pyo" -Recurse | Remove-Item -Force

# 开发环境设置
.PHONY: dev-setup
dev-setup: install-dev pre-commit
	@echo "Development environment setup completed!"

.PHONY: pre-commit
pre-commit:
	@echo "Installing pre-commit hooks..."
	pre-commit install
	pre-commit install --hook-type commit-msg

# 运行服务器
.PHONY: run
run:
	@echo "Starting development server..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: run-prod
run-prod:
	@echo "Starting production server..."
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

.PHONY: run-debug
run-debug:
	@echo "Starting debug server..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

# Docker 相关
.PHONY: docker-build
docker-build:
	@echo "Building Docker image..."
	docker build -t $(PROJECT_NAME) .

.PHONY: docker-run
docker-run:
	@echo "Running Docker container..."
	docker run -p 8000:8000 --env-file .env $(PROJECT_NAME)

.PHONY: docker-dev
docker-dev:
	@echo "Running Docker container in development mode..."
	docker-compose up --build

.PHONY: docker-down
docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down

# 数据库相关
.PHONY: db-upgrade
db-upgrade:
	@echo "Upgrading database..."
	alembic upgrade head

.PHONY: db-downgrade
db-downgrade:
	@echo "Downgrading database..."
	alembic downgrade -1

.PHONY: db-migration
db-migration:
	@echo "Creating new migration..."
	@if ($$args.Count -eq 0) { \
		Write-Host "Usage: make db-migration MESSAGE='migration message'"; \
		exit 1; \
	}
	alembic revision --autogenerate -m "$(MESSAGE)"

.PHONY: db-reset
db-reset:
	@echo "Resetting database..."
	alembic downgrade base
	alembic upgrade head

# 性能测试
.PHONY: benchmark
benchmark:
	@echo "Running performance benchmarks..."
	$(PYTEST) $(TEST_DIR) --benchmark-only

.PHONY: load-test
load-test:
	@echo "Running load tests..."
	locust -f tests/load_tests.py --host=http://localhost:8000

# 文档生成
.PHONY: docs
docs:
	@echo "Generating documentation..."
	mkdocs build

.PHONY: docs-serve
docs-serve:
	@echo "Serving documentation..."
	mkdocs serve

# 依赖管理
.PHONY: deps-update
deps-update:
	@echo "Updating dependencies..."
	$(PIP) list --outdated

.PHONY: deps-check
deps-check:
	@echo "Checking for security vulnerabilities..."
	safety check

# 代码分析
.PHONY: complexity
complexity:
	@echo "Analyzing code complexity..."
	radon cc $(SRC_DIR) -a

.PHONY: maintainability
maintainability:
	@echo "Analyzing maintainability index..."
	radon mi $(SRC_DIR) -a

# 完整的CI流程
.PHONY: ci
ci: clean install-dev quality test-cov
	@echo "CI pipeline completed successfully!"

# 发布准备
.PHONY: build
build: clean
	@echo "Building package..."
	$(PYTHON) -m build

.PHONY: release-check
release-check: quality test-cov build
	@echo "Release checks completed!"

# 环境信息
.PHONY: info
info:
	@echo "Project Information:"
	@echo "  Name: $(PROJECT_NAME)"
	@echo "  Python: $$($(PYTHON) --version)"
	@echo "  Pip: $$($(PIP) --version)"
	@echo "  Source: $(SRC_DIR)"
	@echo "  Tests: $(TEST_DIR)"
	@echo ""
	@echo "Installed packages:"
	@$(PIP) list

# 快速开发命令
.PHONY: quick-test
quick-test:
	@echo "Running quick tests..."
	$(PYTEST) $(TEST_DIR) -x --ff

.PHONY: fix
fix: format
	@echo "Auto-fixing code issues..."
	autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place $(SRC_DIR) $(TEST_DIR)

# 监控和日志
.PHONY: logs
logs:
	@echo "Showing application logs..."
	tail -f logs/app.log

.PHONY: monitor
monitor:
	@echo "Starting application monitoring..."
	# 这里可以添加监控命令

# 备份和恢复
.PHONY: backup
backup:
	@echo "Creating backup..."
	# 添加备份逻辑

.PHONY: restore
restore:
	@echo "Restoring from backup..."
	# 添加恢复逻辑

# 特殊目标：显示所有可用命令
.PHONY: list
list:
	@echo "Available make targets:"
	@Get-Content Makefile | Select-String "^\.PHONY:" | ForEach-Object { $_.ToString().Replace(".PHONY: ", "  ") }