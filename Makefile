# OCI Deal Accelerator — Build Automation

.PHONY: help install test validate example diagram deck full clean lint codex-package update-icons freshness freshness-refresh sync-skill sku-discover pptx-icons-refresh archcenter-benchmark-20 diagram-lookup diagram-validate-spec archcenter-descriptions-refresh diagram-spec-audit archcenter-smoke install-hooks archcenter-templates-refresh

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

venv: .venv/.deps-installed ## Create or update venv (idempotent — no-op if requirements.txt unchanged)

# Marker file pattern: the venv only rebuilds when requirements.txt is
# newer than the marker. A fresh `make venv` after a successful install
# is an instant no-op (was 1m53s on Codex sandboxes — every turn).
# To force a rebuild: `rm .venv/.deps-installed` (or `rm -rf .venv`).
.venv/.deps-installed: requirements.txt
	@if [ ! -x .venv/bin/python ]; then \
	  echo "Using $(VENV_PYTHON) to create venv..."; \
	  $(VENV_PYTHON) -m venv .venv; \
	fi
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@touch .venv/.deps-installed
	@echo "Virtual environment ready. Run: source .venv/bin/activate"
	@echo "Tip: run 'make install-hooks' once to enable the pre-commit"
	@echo "     hook that keeps SKILL.md in sync with the Codex copy."

install-hooks: ## Install repo-versioned git hooks (pre-commit auto-syncs SKILL.md)
	@if [ ! -d .git ]; then echo "install-hooks: not a git repo"; exit 1; fi
	git config core.hooksPath .githooks
	@echo "install-hooks: core.hooksPath set to .githooks"
	@echo "  → pre-commit now auto-syncs .agents/skills/.../SKILL.md"
	@echo "    whenever SKILL.md is part of the staged change set."

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

pptx-icons-refresh: ## Refresh bundled OCI_Icons.pptx asset + manifest/index for native PPTX diagrams
	$(PYTHON) tools/refresh_pptx_icon_index.py
	@echo "Updated kb/diagram/oci-pptx-icons-manifest.yaml and oci-pptx-icons-index.json"

archcenter-benchmark-20: ## Run 20-case Oracle Architecture Center native benchmark
	$(PYTHON) tools/oci_archcenter_batch.py \
		--limit 20 \
		--threshold 0.82 \
		--fidelity-threshold 0.90 \
		--output-root examples/eval-2026-04-25-archcenter-native-20-v8

diagram-lookup: ## Find Architecture Center reference patterns. Usage: make diagram-lookup QUERY="mysql heatwave HA"
	@if [ -z "$(QUERY)" ]; then echo "Usage: make diagram-lookup QUERY=\"<topology>\""; exit 1; fi
	$(PYTHON) tools/archcenter_pattern_lookup.py "$(QUERY)" --top $${TOP:-5}

diagram-validate-spec: ## Validate a diagram spec's geometry. Usage: make diagram-validate-spec SPEC=path/to/spec.yaml
	@if [ -z "$(SPEC)" ]; then echo "Usage: make diagram-validate-spec SPEC=<path>"; exit 1; fi
	$(PYTHON) tools/diagram_spec_validator.py --spec "$(SPEC)" --strict

diagram-spec-audit: ## Run spec validator across every diagram-spec in examples/, print pass/fail summary
	@echo "Auditing diagram specs under examples/..."
	@total=0; failed=0; \
	for f in $$(find examples -name 'diagram-spec.yaml' -o -name '*-diagram-spec.yaml'); do \
	  total=$$((total+1)); \
	  $(PYTHON) tools/diagram_spec_validator.py --spec "$$f" --strict >/dev/null 2>&1 || { \
	    failed=$$((failed+1)); echo "  FAIL  $$f"; \
	  }; \
	done; \
	echo "Audited $$total spec(s); $$failed failed."

archcenter-descriptions-refresh: ## Re-fetch _description.md for every Architecture Center entry
	$(PYTHON) tools/archcenter_description_fetcher.py --limit 200 --sleep 0.5

archcenter-templates-refresh: ## Extract absolute_layout YAML scaffolds from every cached .drawio
	$(PYTHON) tools/archcenter_drawio_to_template.py

archcenter-smoke: ## 3-case Architecture Center reconstruction smoke test (CI-friendly)
	$(PYTHON) tools/oci_archcenter_batch.py \
		--limit 3 \
		--threshold 0.78 \
		--fidelity-threshold 0.85 \
		--output-root tmp/archcenter-smoke

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

kb-check: ## KB freshness JSON (used by skill welcome-flow pre-flight)
	@$(PYTHON) tools/kb_freshness.py --check --json

freshness-refresh: ## Run refresh tools for stale KB files that support automation
	@$(PYTHON) tools/kb_freshness.py --auto-refresh

sku-discover: ## Report SKUs present in Oracle API but missing from oci-sku-catalog.yaml
	@$(PYTHON) tools/refresh_sku_catalog.py --discover
