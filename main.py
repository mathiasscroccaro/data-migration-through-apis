from models import ALSUtilitaGet
from models import ALSUtilitaPost

from typing import List
import pandas as pd

from dotenv import load_dotenv

import requests
import os


load_dotenv()


def fetch_labels(
    environment: str, sensor_code: str, from_date: str, to_date: str
) -> List[ALSUtilitaGet]:
    base_url = os.getenv(f"ALS_SERVICE_{environment}")
    endpoint = "/utilita"
    url = base_url + endpoint

    params = {
        "sensor": sensor_code,
        "phase": 1,
        "from_date": from_date,
        "to_date": to_date,
    }

    response = requests.get(url, params=params)
    json_data = response.json()

    return [ALSUtilitaGet(**data) for data in json_data]


def save_label(
    asl_post_label: ALSUtilitaPost,
):
    base_url = os.getenv(f"ALS_LAMBDA_URL_WRITE")
    endpoint = "/utilita"
    url = base_url + endpoint

    body = asl_post_label.model_dump(by_alias=True)

    response = requests.post(url, json=body)
    if response.status_code != 200:
        print(
            asl_post_label.sensor_id,
            asl_post_label.timestamp_tz,
            asl_post_label.active_power,
            asl_post_label.power_factor,
            asl_post_label.event_type,
            asl_post_label.appliance_name,
        )


def fetch_labels_from_test(
    sensor_code: str, from_date: str, to_date: str
) -> List[ALSUtilitaGet]:
    return fetch_labels("TEST", sensor_code, from_date, to_date)


def fetch_labels_from_production(
    sensor_code: str, from_date: str, to_date: str
) -> List[ALSUtilitaGet]:
    return fetch_labels("PRODUCTION", sensor_code, from_date, to_date)


def is_test_label_in_prod_label_list(
    test_label: ALSUtilitaGet, prod_label_list: List[ALSUtilitaGet]
) -> bool:
    def are_labels_equal(first_label: ALSUtilitaGet, second_label: ALSUtilitaGet):
        return all(
            [
                first_label.active_power == second_label.active_power,
                first_label.timestamp_tz == second_label.timestamp_tz,
                first_label.time_zone_id == second_label.time_zone_id,
                first_label.appliance_name == second_label.appliance_name,
                first_label.event_type == second_label.event_type,
                first_label.label_confirmed == second_label.label_confirmed,
                first_label.power_factor == second_label.power_factor,
            ]
        )

    return any(
        [are_labels_equal(test_label, prod_label) for prod_label in prod_label_list]
    )


def upload_to_prod_missing_labels(sensor_code: str, from_date: str, to_date: str):
    test_label_list = fetch_labels_from_test(sensor_code, from_date, to_date)
    prod_label_list = fetch_labels_from_production(sensor_code, from_date, to_date)

    for test_label in test_label_list:
        if not is_test_label_in_prod_label_list(test_label, prod_label_list):
            save_label(ALSUtilitaPost(**test_label.to_als_utilita_post_dict()))


def sync_databases():
    file_name = "Utilita_sensors_copy_labels_test_to_prod.csv"
    df = pd.read_csv(file_name)

    for _, row in df.iterrows():
        sensor_code = row["device"]
        from_date = row["start_date"]
        to_date = row["end_date"]

        upload_to_prod_missing_labels(
            sensor_code,
            from_date,
            to_date,
        )


if __name__ == "__main__":
    sync_databases()
