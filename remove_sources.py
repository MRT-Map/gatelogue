import json

with open("data.json", "r") as f:
    j = json.load(f)

def remove_sources(o):
    if isinstance(o, dict):
        if 'v' in o and 's' in o:
            return remove_sources(o['v'])
        return {k: remove_sources(v) for k, v in o.items()}
    elif isinstance(o, list):
        return [remove_sources(a) for a in o]
    return o

j = remove_sources(j)

with open("data_no_sources.json", "w") as f:
    json.dump(j, f)
