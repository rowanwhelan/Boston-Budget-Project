PYTHON = python3
PIP = pip
REQUIREMENTS = requirements.txt
SCRIPT = models/budget_modelling.py

install:
	$(PIP) install -r $(REQUIREMENTS)
run:
	$(PYTHON) $(SCRIPT)
clean:
	rm -rf __pycache__
start: install run
