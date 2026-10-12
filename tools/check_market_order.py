import re
with open('.venv/lib/python3.13/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py') as f:
    code = f.read()
    
# look for step execution order
print("Execution order inside step():")
for line in code.splitlines():
    if "def _execute_orders" in line: print(line)
    if "def _execute_agent_actions" in line: print(line)
    if "def step(" in line: print(line)
