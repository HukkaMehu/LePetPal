from lerobot.configs.policies import PreTrainedConfig

cfg = PreTrainedConfig.from_pretrained('Shrek0/my_vla_policy')

print("Input features:")
for k, ft in cfg.input_features.items():
    print(f"  {k}: type={getattr(ft, 'type', None)}, shape={getattr(ft, 'shape', None)}")

print("\nOutput features:")
for k, ft in cfg.output_features.items():
    print(f"  {k}: type={getattr(ft, 'type', None)}, shape={getattr(ft, 'shape', None)}")
