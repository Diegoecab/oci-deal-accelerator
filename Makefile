# OCI Deal Accelerator — Build Automation

.PHONY: help install test validate example diagram deck full clean lint codex-package update-icons freshness freshness-refresh sync-skill

# Use venv if present, otherwise find best available python3
ifneq (,$(wildcard .venv/bin/python))
  PYTHON ?= .venv/bin/python
else ifneq (,$(shell command -v python3.12 2>/dev/null))
  PYTHON ?= python3.12
else
  PYTHON ?= python3
endif
SPEC_DIR = examples
OUTPUT_DIR = examples/sample-output

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

VENV_PYTHON := $(shell command -v python3.12 2>/dev/null || command -v python3.11 2>/dev/null || command -v python3.10 2>/dev/null || echo python3)

venv: ## Create virtual environment and install dependencies
	@echo "Using $(VENV_PYTHON) to create venv..."
	$(VENV_PYTHON) -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@echo "Virtual environment ready. Run: source .venv/bin/activate"

install: ## Install Python dependencies (system-wide)
	pip install -r requirements.txt

validate: ## Validate imports and configs
	$(PYTHON) -c "from tools.oci_diagram_gen import OCIDiagramGenerator; print('Diagram Generator OK')"
	$(PYTHON) -c "from tools.oci_deck_gen import OCIDeckGenerator; print('Deck Generator OK')"
	$(PYTHON) -c "import yaml; yaml.safe_load(open('config/workload-profile-schema.yaml')); print('Schema OK')"
	$(PYTHON) -c "import yaml; yaml.safe_load(open('config/service-categories.yaml')); print('Categories OK')"
	@echo "All validations passed"

example: ## Generate sample architecture diagram (.drawio)
	@mkdir -p $(OUTPUT_DIR)
	$(PYTHON) tools/oci_diagram_gen.py \
		--spec $(SPEC_DIR)/migration-adb-ha-dr.yaml \
		--output $(OUTPUT_DIR)/architecture.drawio
	@echo "Generated $(OUTPUT_DIR)/architecture.drawio"

diagram: example ## Alias for example

deck: ## Generate sample proposal deck (.pptx)
	@mkdir -p $(OUTPUT_DIR)
	$(PYTHON) tools/oci_deck_gen.py \
		--spec $(SPEC_DIR)/migration-adb-ha-dr.yaml \
		--output $(OUTPUT_DIR)/architecture-proposal.pptx
	@echo "Generated $(OUTPUT_DIR)/architecture-proposal.pptx"

full: ## Generate all outputs via orchestrator
	$(PYTHON) tools/oci_output.py \
		--spec $(SPEC_DIR)/migration-adb-ha-dr.yaml \
		--output-dir $(OUTPUT_DIR) \
		--format full
	@echo "Generated all outputs in $(OUTPUT_DIR)/"

codex-package: ## Package as Codex skill
	@mkdir -p codex/tools
	cp tools/oci_diagram_gen.py codex/tools/
	cp tools/oci_deck_gen.py codex/tools/
	cp tools/oci_output.py codex/tools/
	cp -r kb codex/
	cp -r config codex/
	@echo "Codex skill package ready in codex/"

update-icons: ## Re-extract OCI icons after updating OCI Library.xml
	$(PYTHON) tools/oci_icon_extractor.py
	@echo "Updated kb/diagram/oci-icons.json from OCI Library.xml"

clean: ## Remove generated output files
	rm -f examples/sample-output/*.drawio
	rm -f examples/sample-output/*.pptx
	rm -f examples/sample-output/*.xlsx
	rm -f examples/sample-output/*.docx

lint: ## Check YAML files for syntax errors and validate SKILL.md sync
	@echo "Checking YAML files..."
	@find kb/ config/ examples/ -name '*.yaml' -exec $(PYTHON) -c \
		"import yaml, sys; list(yaml.safe_load_all(open(sys.argv[1])))" {} \; \
		-print 2>&1 | grep -v "^$$" || echo "All YAML files valid."
	@echo "Checking SKILL.md sync..."
	@$(PYTHON) scripts/sync-skill.py --check

sync-skill: ## Regenerate .agents/skills/oci-deal-accelerator/SKILL.md from root SKILL.md
	@$(PYTHON) scripts/sync-skill.py

freshness: ## Report stale KB files (informational, never fails)
	-@$(PYTHON) tools/kb_freshness.py --check

freshness-refresh: ## Run refresh tools for stale KB files that support automation
	@$(PYTHON) tools/kb_freshness.py --auto-refresh
