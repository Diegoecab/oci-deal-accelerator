# OCI Deal Accelerator — Build Automation

.PHONY: help install test validate diagram deck full clean

PYTHON ?= python3
SPEC_DIR = examples
OUTPUT_DIR = output

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements.txt

validate: ## Run WA validation on sample architecture
	$(PYTHON) scripts/validate-architecture.py \
		--profile $(SPEC_DIR)/sample-workload-profile.yaml \
		--architecture $(SPEC_DIR)/sample-architecture.yaml \
		--output $(OUTPUT_DIR)/scorecard.yaml

diagram: ## Generate sample architecture diagram (.drawio)
	@mkdir -p $(OUTPUT_DIR)
	$(PYTHON) tools/oci_diagram_gen.py \
		--spec $(SPEC_DIR)/diagram-spec.yaml \
		--output $(OUTPUT_DIR)/architecture.drawio

deck: ## Generate sample proposal deck (.pptx)
	@mkdir -p $(OUTPUT_DIR)
	$(PYTHON) tools/oci_deck_gen.py \
		--spec $(SPEC_DIR)/proposal-spec.yaml \
		--output $(OUTPUT_DIR)/proposal.pptx

full: diagram deck validate ## Generate all outputs

clean: ## Remove generated output files
	rm -rf $(OUTPUT_DIR)

lint: ## Check YAML files for syntax errors
	@echo "Checking YAML files..."
	@find kb/ config/ templates/ examples/ -name '*.yaml' -exec $(PYTHON) -c \
		"import yaml, sys; yaml.safe_load(open(sys.argv[1]))" {} \; \
		-print 2>&1 | grep -v "^$$" || echo "All YAML files valid."
