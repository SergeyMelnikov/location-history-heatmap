#!/usr/bin/python3
import json
import geopy.distance
from datetime import datetime


def filter(records: list[dict], min_delta_seconds: int, min_delta_meters: int, max_speed_kmp_h: int) -> list:
    prev = (60, 30)
    ptime = datetime.fromisoformat('1970-01-01T00:00:00.000Z')
    filtered = []
    cnt = 0
    ignored = {
        'BadFormat': 0,
        'Time': 0,
        'Distance': 0,
        'Speed': 0,
    }
    print(f"Processing {len(records)} records")
    for p in records:
        cnt += 1
        if cnt % 50000 == 0:
            print(
                f"{cnt * 100 // len(records)}% {cnt}/{len(records)} -> {len(filtered)}",
                f"({len(filtered) / cnt:.5f})",
                f"({prev[0]:.7f}, {prev[1]:.7f}) {p['timestamp']}")
            print(ignored)

        if 'latitudeE7' not in p or 'longitudeE7' not in p:
            ignored['BadFormat'] += 1
            continue

        coord = (p['latitudeE7'] * 1e-7, p['longitudeE7'] * 1e-7)
        time = datetime.fromisoformat(p['timestamp'])
        delta_time_seconds = (time - ptime).seconds
        if delta_time_seconds < min_delta_seconds:
            ignored['Time'] += 1
            continue
        dist = geopy.distance.geodesic(coord, prev)
        speed_kmph = dist.km / (delta_time_seconds / 60 / 60)
        if dist.m < min_delta_meters:
            ignored['Distance'] += 1
            continue
        if speed_kmph > max_speed_kmp_h:
            prev = coord
            ptime = time
            ignored['Speed'] += 1
            continue
        filtered.append((p['latitudeE7'], p['longitudeE7']))

        prev = coord
        ptime = time
    print(f"Compression: {len(filtered) / len(records)}")
    return filtered


srcFilename = "Records-002.json"
# srcFilename = "head.json"
print(f"Loading {srcFilename}")
src = json.load(open(srcFilename))["locations"]
print(f"Loaded {srcFilename}")

data = filter(src, 10, 10, 300)
dstFilename = "data.json"
print(f"Saving {dstFilename}")
with open(dstFilename, "w") as out:
    json.dump(data, out)
print(f"Saved {dstFilename}")

dstFilename = "data.js"
print(f"Saving {dstFilename}")
with open(dstFilename, "w") as out:
    print("var data = ", file=out)
    json.dump(data, out)
    print(";", file=out)
print(f"Saved {dstFilename}")
