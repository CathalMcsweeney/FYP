import xml.etree.ElementTree as ET
import csv
from collections import defaultdict


def parse_trip_outputs(columns, org, rer, pony):
    data_rows = [columns]
    data_dict = defaultdict(list)
    for output_path in [org, rer, pony]:
        root = ET.parse(output_path).getroot()
        for child in root.iter():
            if child.tag == "tripinfo":
                veh_id = int(child.attrib["id"])
                data_dict[veh_id].append(float(child.attrib["duration"]))
    for k, v in data_dict.items():
        data_rows.append([k]+v)
    return data_rows


def write_2_csv(data_rows, csv_output):
    with open(csv_output, "w") as output:
        cw = csv.writer(output)
        cw.writerows(data_rows)


def main():
    trip_output_org = "../outputs/trips/8x8_trip_org.xml"
    trip_output_rer = "../outputs/trips/8x8_trip_rer.xml"
    trip_output_pony ="../outputs/trips/8x8_trip.xml"
    csv_output = "../outputs/traveltime_cmp.csv"

    columns = ["veh_id", "org", "rer", "pony"]

    data_rows = parse_trip_outputs(columns, trip_output_org, trip_output_rer, trip_output_pony)

    write_2_csv(data_rows, csv_output)


if __name__ == '__main__':
    main()
