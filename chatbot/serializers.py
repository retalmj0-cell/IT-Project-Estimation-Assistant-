import math
from rest_framework import serializers

class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000)
    agent = serializers.ChoiceField(
        choices=("pert_agent", "budget_agent", "sprint_agent"),
        required=False,
    )
    parameters = serializers.DictField(required=False, default=dict)

    @staticmethod
    def validate_parameters(values):
        numeric_fields = {
            "optimistic": float, "most_likely": float, "pessimistic": float,
            "hours": float, "hourly_rate": float, "contingency_percent": float,
            "team_size": int, "days": int, "focus_factor": float
        }
        for field, cast in numeric_fields.items():
            if field not in values:
                continue
            raw = values[field]
            if isinstance(raw, bool):
                raise serializers.ValidationError({field: "Boolean not allowed"})
            try:
                number = float(raw)
                if not math.isfinite(number):
                    raise ValueError
                if cast is int and not number.is_integer():
                    raise ValueError
                values[field] = cast(number)
            except (TypeError, ValueError, OverflowError):
                raise serializers.ValidationError({field: "Invalid number"})
        return values