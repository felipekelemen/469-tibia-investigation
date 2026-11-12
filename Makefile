PYTHON ?= python3
.PHONY: sources audit experiments round2 round3 round4 round5 round6 round7 round8 round9 round10 round11 round12 research-audit test reproduce
sources:
	$(PYTHON) scripts/bootstrap_sources.py
audit:
	$(PYTHON) scripts/audit_corpus.py
experiments: audit
	$(PYTHON) scripts/structural_experiments.py > results/structural.log
	$(PYTHON) scripts/audit_claimed_translation.py
	$(PYTHON) scripts/reproduce_upstream_validation.py
	$(PYTHON) scripts/matrix_experiments.py
	$(PYTHON) scripts/cipher_battery.py
round2: audit
	$(PYTHON) scripts/hill29_experiments.py
	$(PYTHON) scripts/homophonic_controls.py
	$(PYTHON) scripts/residual_channel.py
	$(PYTHON) scripts/map_geometry.py
round3:
	$(PYTHON) scripts/source_validation_inventory.py
	$(PYTHON) scripts/homophonic_benchmark.py --run
	$(PYTHON) scripts/qualification_gate.py
	$(PYTHON) scripts/generative_comparison.py
	$(PYTHON) scripts/matrix_walk_experiment.py
round4:
	$(PYTHON) scripts/run_round4.py
round5:
	$(PYTHON) scripts/run_round5.py
round6:
	$(PYTHON) scripts/run_round6.py
round7:
	$(PYTHON) scripts/run_round7.py
round8:
	$(PYTHON) scripts/run_round8.py
round9:
	$(PYTHON) scripts/run_round9.py
round10:
	$(PYTHON) scripts/run_round10.py
round11:
	$(PYTHON) scripts/run_round11.py
round12:
	$(PYTHON) scripts/run_round12.py
research-audit:
	$(PYTHON) scripts/audit_external_samples.py
test:
	$(PYTHON) -m unittest discover -s tests -v
reproduce: sources experiments test
