# OCI Deal Accelerator — Build Automation

.PHONY: help install test validate example diagram deck full clean lint codex-package

PYTHON ?= python3
SPEC_DIR = examples
OUTPUT_DIR = examples/sample-output

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
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

clean: ## Remove generated output files
	rm -f examples/sample-output/*.drawio
	rm -f examples/sample-output/*.pptx
	rm -f examples/sample-output/*.xlsx
	rm -f examples/sample-output/*.docx

lint: ## Check YAML files for syntax errors
	@echo "Checking YAML files..."
	@find kb/ config/ examples/ -name '*.yaml' -exec $(PYTHON) -c \
		"import yaml, sys; yaml.safe_load(open(sys.argv[1]))" {} \; \
		-print 2>&1 | grep -v "^$$" || echo "All YAML files valid."
