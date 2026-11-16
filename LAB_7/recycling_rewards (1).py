import math

def parse_collection(text):
    if not isinstance(text, str):
        return None
    parts = text.split(':')
    if len(parts) != 2:
        return None
    material = parts[0].strip()
    if not material:
        return None
    try:
        kg = float(parts[1])
    except ValueError:
        return None
    if not math.isfinite(kg) or kg < 0:
        return None
    return material.title(), kg

def weight_average(weights_csv):
    if not isinstance(weights_csv, str):
        return None
    values = []
    for item in weights_csv.split(','):
        try:
            v = float(item)
        except ValueError:
            return None
        if not math.isfinite(v) or v < 0:
            return None
        values.append(v)
    if not values:
        return None
    return sum(values) / len(values)

def net_points(text):
    if not isinstance(text, str):
        return None
    parts = text.split('|')
    if len(parts) != 2:
        return None
    try:
        points = float(parts[0])
        penalty = float(parts[1])
    except ValueError:
        return None
    if not (math.isfinite(points) and math.isfinite(penalty)):
        return None
    total = points * 2 - penalty
    if not math.isfinite(total):
        return None
    return max(total, 0)

def show(label, result):
    print(label, result if result is not None else "Invalid input")

def main():
    print("==== Running parse_collection ====")
    user_input = input("Enter material:weight in kg (e.g. paper:12): ")
    show("Material and Weight:", parse_collection(user_input))

    print("\n==== Running weight_average ====")
    user_input = input("Enter weights in kg as CSV (e.g. 5,12,20): ")
    show("Average Weight:", weight_average(user_input))

    print("\n==== Running net_points ====")
    user_input = input("Enter points|penalty (e.g. 80|10): ")
    show("Net Points:", net_points(user_input))

if __name__ == "__main__":
    main()
