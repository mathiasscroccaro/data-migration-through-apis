from main import upload_to_prod_missing_labels

from unittest.mock import patch

from models import ALSUtilitaGet

import json


def read_json_file(file_path):
    try:
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
        return data
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in '{file_path}': {e}")
    except Exception as e:
        print(f"An error occurred while reading '{file_path}': {e}")


def return_value_from_test():
    return [ALSUtilitaGet(**item) for item in read_json_file("fixtures/data_test.json")]


def return_value_from_production():
    return [
        ALSUtilitaGet(**item)
        for item in read_json_file("fixtures/data_production.json")
    ]


@patch("utils.save_label")
@patch("utils.fetch_labels_from_test")
@patch("utils.fetch_labels_from_production")
def test_upload_to_prod_missing_labels(
    mocked_fetch_production, mocked_fetch_test, mocked_save_label
):

    # Replace the original functions with the mock objects in your module
    mocked_fetch_production.return_value = return_value_from_production()
    mocked_fetch_test.return_value = return_value_from_test()

    # Call the function you want to test
    upload_to_prod_missing_labels(
        sensor_code="2008ecb0-ee58-4570-9e68-3392ab4c2fe8",
        from_date="2023-06-01",
        to_date="2023-06-30",
    )

    assert mocked_save_label.assert_called_once_with()
    assert False == True


test_upload_to_prod_missing_labels()
