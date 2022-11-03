from rest_framework.serializers import ModelSerializer as _RestFrameworkModelSerializer


class ModelSerializer(_RestFrameworkModelSerializer):
    _fields_from_form = []

    def __init__(self, *args, **kwargs):
        # Don't pass the field args up to the superclass
        fields = kwargs.pop("fields", None)
        fields_exclude = kwargs.pop("fields_exclude", [])

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            if isinstance(fields, str):
                allowed = set(fields.split(","))
            else:
                allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        for field_name in fields_exclude:
            self.fields.pop(field_name)

        data = kwargs.get('data', {})
        for key in data:
            if key not in self.fields:
                continue
            if key in self._fields_from_form:
                continue
            self._fields_from_form.append(key)

    def update(self, instance, validated_data):
        for field in self._fields_from_form:
            setattr(instance, f"IS_{field}_FROM_FORM", True)

        return super().update(instance, validated_data)
