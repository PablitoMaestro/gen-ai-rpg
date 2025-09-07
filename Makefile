# Makefile for AI-powered RPG project

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Get current branch
BRANCH := $(shell git branch --show-current)

# Default target
.PHONY: help
help:
	@echo "$(GREEN)Available commands:$(NC)"
	@echo "  make runl       - Run all services locally (frontend, backend, supabase)"
	@echo "  make commitq    - Quick commit and push all changes to current branch"
	@echo "  make stop       - Stop all running services"
	@echo "  make status     - Check status of all services"
	@echo "  make logs       - Show logs from all services"
	@echo "  make resetdb    - Reset database and reseed storage buckets"
	@echo "  make seed-storage - Reseed storage buckets from local files"
	@echo ""
	@echo "$(YELLOW)Current branch: $(BRANCH)$(NC)"

# Run all services locally
.PHONY: runl
runl:
	@echo "$(GREEN)Starting all services locally...$(NC)"
	@echo "$(YELLOW)Starting Supabase...$(NC)"
	@cd supabase && supabase start &
	@sleep 5
	@echo "$(YELLOW)Starting Backend...$(NC)"
	@cd backend && source venv/bin/activate 2>/dev/null || python -m venv venv && source venv/bin/activate && uvicorn main:app --reload --port 8000 &
	@sleep 3
	@echo "$(YELLOW)Starting Frontend...$(NC)"
	@cd frontend && npm run dev &
	@sleep 3
	@echo "$(GREEN)All services started!$(NC)"
	@echo "$(GREEN)Frontend: http://localhost:3000$(NC)"
	@echo "$(GREEN)Backend: http://localhost:8000$(NC)"
	@echo "$(GREEN)Supabase Studio: http://localhost:54323$(NC)"
	@echo ""
	@echo "$(YELLOW)Press Ctrl+C to stop all services or run 'make stop'$(NC)"
	@wait

# Quick commit and push
.PHONY: commitq
commitq:
	@echo "$(YELLOW)Current branch: $(BRANCH)$(NC)"
	@echo "$(GREEN)Adding all changes...$(NC)"
	@git add -A
	@echo "$(GREEN)Creating commit...$(NC)"
	@read -p "Enter commit message: " msg; \
	git commit -m "$$msg" || (echo "$(RED)No changes to commit$(NC)" && exit 1)
	@echo "$(GREEN)Pushing to origin/$(BRANCH)...$(NC)"
	@git push origin $(BRANCH) || git push --set-upstream origin $(BRANCH)
	@echo "$(GREEN)Successfully pushed to $(BRANCH)!$(NC)"

# Stop all services
.PHONY: stop
stop:
	@echo "$(YELLOW)Stopping all services...$(NC)"
	@-pkill -f "uvicorn main:app" 2>/dev/null || true
	@-pkill -f "next-server" 2>/dev/null || true
	@-pkill -f "npm run dev" 2>/dev/null || true
	@-cd supabase && supabase stop 2>/dev/null || true
	@echo "$(GREEN)All services stopped!$(NC)"

# Check status of services
.PHONY: status
status:
	@echo "$(YELLOW)Checking service status...$(NC)"
	@echo ""
	@if lsof -i:3000 >/dev/null 2>&1; then \
		echo "$(GREEN)✓ Frontend is running on port 3000$(NC)"; \
	else \
		echo "$(RED)✗ Frontend is not running$(NC)"; \
	fi
	@if lsof -i:8000 >/dev/null 2>&1; then \
		echo "$(GREEN)✓ Backend is running on port 8000$(NC)"; \
	else \
		echo "$(RED)✗ Backend is not running$(NC)"; \
	fi
	@if lsof -i:54321 >/dev/null 2>&1; then \
		echo "$(GREEN)✓ Supabase is running on port 54321$(NC)"; \
	else \
		echo "$(RED)✗ Supabase is not running$(NC)"; \
	fi

# Show logs from all services
.PHONY: logs
logs:
	@echo "$(YELLOW)Showing recent logs...$(NC)"
	@echo "$(GREEN)--- Supabase Logs ---$(NC)"
	@-cd supabase && supabase status 2>/dev/null || echo "Supabase not running"
	@echo ""
	@echo "$(YELLOW)For live logs, services must be running in foreground$(NC)"

# Install dependencies
.PHONY: install
install:
	@echo "$(GREEN)Installing dependencies...$(NC)"
	@cd frontend && npm install
	@cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt 2>/dev/null || pip install fastapi uvicorn pydantic python-dotenv
	@echo "$(GREEN)Dependencies installed!$(NC)"

# Clean up
.PHONY: clean
clean:
	@echo "$(YELLOW)Cleaning up...$(NC)"
	@rm -rf frontend/node_modules frontend/.next
	@rm -rf backend/__pycache__ backend/venv
	@echo "$(GREEN)Cleanup complete!$(NC)"

# Development shortcuts
.PHONY: dev-frontend
dev-frontend:
	@cd frontend && npm run dev

.PHONY: dev-backend
dev-backend:
	@cd backend && source venv/bin/activate && uvicorn main:app --reload

.PHONY: dev-db
dev-db:
	@cd supabase && supabase start

# Database operations
.PHONY: resetdb
resetdb:
	@echo "$(YELLOW)Resetting database and storage...$(NC)"
	@cd supabase && supabase db reset
	@echo "$(GREEN)Database reset complete!$(NC)"
	@echo "$(YELLOW)Seeding storage buckets...$(NC)"
	@cd supabase && supabase seed buckets
	@echo "$(GREEN)Storage buckets seeded successfully!$(NC)"

.PHONY: seed-storage
seed-storage:
	@echo "$(YELLOW)Seeding storage buckets from local files...$(NC)"
	@cd supabase && supabase seed buckets
	@echo "$(GREEN)Storage buckets seeded successfully!$(NC)"
	@echo "$(GREEN)Files uploaded from supabase/character-images/ to storage$(NC)"

# Git shortcuts
.PHONY: pull
pull:
	@git pull origin $(BRANCH)

.PHONY: sync
sync:
	@git fetch --all
	@git pull origin $(BRANCH)
	@echo "$(GREEN)Synced with origin/$(BRANCH)$(NC)"