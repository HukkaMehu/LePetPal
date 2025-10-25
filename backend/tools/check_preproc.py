from huggingface_hub import hf_hub_download
import json

path = hf_hub_download('Shrek0/my_vla_policy', 'policy_preprocessor.json')
with open(path) as f:
    config = json.load(f)
print(json.dumps(config, indent=2))
