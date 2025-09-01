# OCR Hospital Management System - Cross-platform Commands

.PHONY: help dev prod stop clean logs backup setup-windows

help: ## Show this help message
	@echo "OCR Hospital Management System - Commands"
	@echo "========================================"
	@echo "Windows users: Use PowerShell scripts or these make commands"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup-windows: ## Create directories and setup for Windows
	@echo "🔧 Setting up for Windows..."
	@powershell -Command "New-Item -ItemType Directory -Force -Path uploads, logs, nginx, ssl, backups | Out-Null"
	@echo "✅ Directories created!"
	@echo "📋 Use: make dev, make prod, or PowerShell scripts in scripts/ folder"

dev: setup-windows ## Start development environment
	@echo "🚀 Starting development environment..."
	@docker-compose -f docker-compose.yml --env-file .env.docker up --build -d
	@echo "✅ Development environment started!"
	@echo "📊 API: http://localhost:5000/api/v1/swagger"
	@echo "📊 Nginx: http://localhost"

prod: setup-windows ## Start production environment
	@echo "🚀 Starting production environment..."
	@docker-compose -f docker-compose.prod.yml --env-file .env.prod up --build -d
	@echo "✅ Production environment started!"

stop: ## Stop all services
	@echo "🛑 Stopping services..."
	@docker-compose -f docker-compose.yml down 2>nul || echo ""
	@docker-compose -f docker-compose.prod.yml down 2>nul || echo ""

logs: ## Show logs
	@docker-compose -f docker-compose.yml logs -f --tail=100 2>nul || docker-compose -f docker-compose.prod.yml logs -f --tail=100

status: ## Show service status
	@echo "📊 Service Status:"
	@docker-compose -f docker-compose.yml ps 2>nul || echo "Development not running"
	@docker-compose -f docker-compose.prod.yml ps 2>nul || echo "Production not running"

health: ## Check service health
	@echo "🏥 Health Check:"
	@powershell -Command "try { (Invoke-WebRequest -Uri 'http://localhost/health' -UseBasicParsing).Content | ConvertFrom-Json | ConvertTo-Json } catch { 'Services not accessible' }"