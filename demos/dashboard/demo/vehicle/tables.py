from demo.vehicle.data import VehicleData

from wildcoeus.dashboards.component.table import TableSerializer


class VehicleTableSerializer(TableSerializer):
    class Meta:
        title = "Vehicle table"
        columns = {
            "ref": "Reference",
            "type": "Type",
            "number_plate": "Number Plate",
            "current_mileage": "Mileage",
            "next_mot_due": "MOT Due",
        }

    @classmethod
    def get_queryset(cls, **kwargs):
        return VehicleData.get_queryset(filters=kwargs["filters"])