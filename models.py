from pydantic import BaseModel
from pydantic import Field


class ALSUtilitaPost(BaseModel):
    sensor_id: str = Field(alias="sensorId")
    active_power: int = Field(alias="activePower")
    timestamp_tz: str = Field(alias="timestampTz")
    timezone_id: str = Field(alias="timeZoneId")
    appliance_name: str = Field(alias="applianceName")
    event_type: str = Field(alias="eventType")
    label_confirmed: bool = Field(alias="labelConfirmed")
    power_factor: int = Field(alias="powerFactor")


class ALSUtilitaGet(BaseModel):
    sensor_id: str
    active_power: int
    timestamp_tz: str
    time_zone_id: str
    appliance_name: str
    event_type: str
    label_confirmed: bool
    power_factor: int

    def to_als_utilita_post_dict(self):
        return {
            "sensorId": self.sensor_id,
            "activePower": self.active_power,
            "timestampTz": self.timestamp_tz,
            "timeZoneId": self.time_zone_id,
            "applianceName": self.appliance_name,
            "eventType": self.event_type.upper(),
            "labelConfirmed": self.label_confirmed,
            "powerFactor": self.power_factor,
        }
