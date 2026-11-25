PYTHON ?= python3
.PHONY: round31
.PHONY: sources audit experiments round2 round3 round4 round5 round6 round7 round8 round9 round10 round11 round12 round13 round14 round15 round15-full round16 round17 round18 round19 round20 round21 round22 round23 round24 round25 round26 round27 round27-full round28 round28-full round29 round29-full round30 research-audit test reproduce
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
round13:
	$(PYTHON) scripts/run_round13.py
round14:
	$(PYTHON) scripts/run_round14.py
round15:
	$(PYTHON) scripts/check_round15.py
round15-full:
	$(PYTHON) scripts/check_round15.py --full
round16:
	$(PYTHON) scripts/run_round16.py
round17:
	$(PYTHON) scripts/run_round17.py
round18:
	$(PYTHON) scripts/run_round18.py
round19:
	$(PYTHON) scripts/run_round19.py
round20:
	$(PYTHON) scripts/run_round20.py
round21:
	$(PYTHON) scripts/run_round21.py
round22:
	$(PYTHON) scripts/run_round22.py
round23:
	$(PYTHON) scripts/run_round23.py
round24:
	$(PYTHON) scripts/run_round24.py
round25:
	$(PYTHON) scripts/run_round25.py
round26:
	$(PYTHON) scripts/run_round26.py
round27:
	$(PYTHON) scripts/run_round27.py
round27-full:
	$(PYTHON) scripts/replay_round27_cached.py --full
round28:
	$(PYTHON) scripts/run_round28.py
round28-full:
	$(PYTHON) scripts/run_round28.py --full
round29:
	OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 $(PYTHON) scripts/run_round29.py
round29-full:
	OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 $(PYTHON) scripts/run_round29.py --full
round30:
	$(PYTHON) scripts/run_round30.py
round31:
	$(PYTHON) scripts/run_round31.py
research-audit:
	$(PYTHON) scripts/audit_external_samples.py
test:
	$(PYTHON) -m unittest discover -s tests -v
reproduce: sources experiments test
