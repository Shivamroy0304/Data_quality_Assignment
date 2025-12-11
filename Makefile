.PHONY: help install run test clean docs

help:
	@echo "Workflow Engine - Available Commands"
	@echo "===================================="
	@echo ""
	@echo "make install     - Install dependencies"
	@echo "make run         - Run the API server"
	@echo "make test        - Run tests"
	@echo "make clean       - Clean up cache files"
	@echo "make docs        - Show documentation files"
	@echo "make help        - Show this help message"
	@echo ""

install:
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

run:
	python run.py

test:
	python test_engine.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "✓ Cleaned up cache files"

docs:
	@echo "Documentation Files:"
	@echo "===================="
	@echo ""
	@echo "README.md          - Main project documentation"
	@echo "ARCHITECTURE.md    - System design and architecture"
	@echo "API_REFERENCE.md   - Complete API endpoint reference"
	@echo ""
	@echo "To view in your editor:"
	@echo "  - Open README.md for getting started"
	@echo "  - Open ARCHITECTURE.md for design details"
	@echo "  - Open API_REFERENCE.md for endpoint documentation"
	@echo ""
	@echo "When running the server, visit:"
	@echo "  - http://localhost:8000/docs (Swagger UI)"
	@echo "  - http://localhost:8000/redoc (ReDoc)"
	@echo ""
