#from screeninfo import get_monitors
#from calc_str import calculate
import yaml
import re

with open("myyaml/test.yaml", "r") as f:
    data = yaml.safe_load(f)

def flatten_yaml_structure(data, parent_key='', sep='.'):
    items = []
    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_yaml_structure(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

# flatten
flatten_data = flatten_yaml_structure(data)

def extract_variables(string):
    variables = []
    start = string.find("${")
    while start != -1:
        end = string.find("}", start)
        if end == -1:
            break
        variables.append(string[start + 2:end])
        start = string.find("${", end)
    return variables

for k, v in flatten_data.items():
    if type(v) == str:
        if len(extract_variables(v)) != 0:
            for s in extract_variables(v):
                flatten_data[k] = flatten_data[k].replace(f"${{{extract_variables(flatten_data[k])[0]}}}", str(flatten_data[s]))

# 数式記述のものを計算して辞書を書き換え
for k, v in flatten_data.items():
    if type(v) is str:
        if len(re.sub(r"[^a-zA-Z]", "", v)) == 0:
            flatten_data[k] = int(eval(v))

def create_nested_dict(data):
    nested_dict = {}
    for key, value in data.items():
        parts = key.split('.')
        current_dict = nested_dict
        for part in parts[:-1]:
            current_dict = current_dict.setdefault(part, {})
        current_dict[parts[-1]] = value
    return nested_dict

print(create_nested_dict(flatten_data))