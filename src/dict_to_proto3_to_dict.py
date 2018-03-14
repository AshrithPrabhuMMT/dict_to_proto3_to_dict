#coding=utf-8

import collections
import os
import sys

# Using the cpp implemenation to speed up proto processing. Though the api_implementation
# module defaults it to cpp, so we can safely comment out the next line of code.
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "cpp"

from google.protobuf.descriptor import FieldDescriptor

__all__ = ['dict_to_protobuf', 'protobuf_to_dict']

if sys.version_info[0] < 3:
    LONG_TYPE = long
    UNICODE_TYPE = unicode
    BASESTRING_TYPE = basestring
else:
    LONG_TYPE = int
    UNICODE_TYPE = str
    BASESTRING_TYPE = str

FIELD_CAST_MAP = {
    FieldDescriptor.TYPE_BOOL: bool,
    FieldDescriptor.TYPE_BYTES: lambda b: b.encode("base64"),
    FieldDescriptor.TYPE_DOUBLE: float,
    FieldDescriptor.TYPE_ENUM: int,
    FieldDescriptor.TYPE_FIXED32: int,
    FieldDescriptor.TYPE_FIXED64: LONG_TYPE,
    FieldDescriptor.TYPE_FLOAT: float,
    FieldDescriptor.TYPE_INT32: int,
    FieldDescriptor.TYPE_INT64: LONG_TYPE,
    FieldDescriptor.TYPE_SFIXED32: int,
    FieldDescriptor.TYPE_SFIXED64: LONG_TYPE,
    FieldDescriptor.TYPE_SINT32: int,
    FieldDescriptor.TYPE_SINT64: LONG_TYPE,
    FieldDescriptor.TYPE_STRING: UNICODE_TYPE,
    FieldDescriptor.TYPE_UINT32: int,
    FieldDescriptor.TYPE_UINT64: LONG_TYPE
}

FIELD_DEFAULT_VALS = {
    FieldDescriptor.TYPE_BOOL: False,
    FieldDescriptor.TYPE_BYTES: "",
    FieldDescriptor.TYPE_DOUBLE: 0.0,
    FieldDescriptor.TYPE_ENUM: 0,
    FieldDescriptor.TYPE_FIXED32: 0,
    FieldDescriptor.TYPE_FIXED64: 0,
    FieldDescriptor.TYPE_FLOAT: 0.0,
    FieldDescriptor.TYPE_INT32: 0,
    FieldDescriptor.TYPE_INT64: 0,
    FieldDescriptor.TYPE_SFIXED32: 0,
    FieldDescriptor.TYPE_SFIXED64: 0,
    FieldDescriptor.TYPE_SINT32: 0,
    FieldDescriptor.TYPE_SINT64: 0,
    FieldDescriptor.TYPE_STRING: "",
    FieldDescriptor.TYPE_UINT32: 0,
    FieldDescriptor.TYPE_UINT64: 0
}

def _is_field_a_map(field, message):
    """
    Checks if the field is a map
    """
    return field.type == FieldDescriptor.TYPE_MESSAGE and \
                isinstance(getattr(message, field.name), collections.Mapping)

def _constant_from_enum_label(field, value):
    """
    Converts the string label to the enum constant
    """
    try:
        val = field.enum_type.values_by_name[value].number
    except KeyError:
        raise KeyError("%s is not a valid label in the enum %s" % (val, field.name))

    return val


def _handle_repeated(values, message, field):
    """
    Hanldes repeated field when converting a dict to protobuf
    """
    if values:
        # List of messages
        if field.type == FieldDescriptor.TYPE_MESSAGE:
            for val in values:
                cmd = message.add()
                _dict_to_protobuf(val, cmd)
        # List of enums
        elif field.type == FieldDescriptor.TYPE_ENUM:
            for val in values:
                if isinstance(val, BASESTRING_TYPE):
                    message.append(_constant_from_enum_label(field, val))
                else:
                    raise ValueError("""Value %s passed to enum %s is of type %s """
                        """, not string or unicode""", val, field.name, type(val))
        # List of scalars. Well, other than enums.
        else:
            message.extend(values)


def _dict_to_protobuf(values, message):
    """
    Converts the python dictionary to proto object representation which will then be
    serialized by proto library. Here
    """

    for key, value in values.items():
        field = message.DESCRIPTOR.fields_by_name.get(key, None)

        # If field is not there or value passed is empty/None
        if field is None or not value:
            continue

        if field.label == FieldDescriptor.LABEL_REPEATED:

            # Handling map<Type1, Type2> here.
            if _is_field_a_map(field, message):

                    msg = getattr(message, field.name)
                    val_field = field.message_type.fields_by_name['value']

                    for ky, val in value.items():
                        if val_field.type == FieldDescriptor.TYPE_MESSAGE:
                            _dict_to_protobuf(val, msg[ky])
                        elif val_field.type == FieldDescriptor.TYPE_ENUM:
                            msg[ky] = _constant_from_enum_label(val_field, val)
                        else:
                            msg[ky] = val
            else:
                # Handling lists in general, including list of messages, as
                # list of messages too has field type as TYPE_MESSAGE
                _handle_repeated(value, getattr(message, field.name), field)

        # Handle a sub message
        elif field.type == FieldDescriptor.TYPE_MESSAGE:
            _dict_to_protobuf(value, getattr(message, field.name))

        else:
            if field.type == FieldDescriptor.TYPE_ENUM and isinstance(value, BASESTRING_TYPE):
                value = _constant_from_enum_label(field, value)
            elif field.type == FieldDescriptor.TYPE_BYTES:
                value = value.decode("base64")
            setattr(message, field.name, value)


def dict_to_protobuf(values, message):
    return _dict_to_protobuf(values, message)


def _enum_label_from_constant(field, value):
    """
    Gets the enum field label from the int constant of the same
    """
    return field.enum_type.values_by_number[int(value)].name


def _get_type_cast_callable(message, field):
    """
    Gets the callable casting function to map the values from proto domain to
    python's, say int32 in proto maps to int, int64 to long, sint32 to int, etc.
    """
    if field.type == FieldDescriptor.TYPE_MESSAGE:
        # Encode the nested message
        return lambda message: _protobuf_to_dict(message)

    if field.type == FieldDescriptor.TYPE_ENUM:
        return lambda value: _enum_label_from_constant(field, value)

    if field.type in FIELD_CAST_MAP:
        return FIELD_CAST_MAP[field.type]

    raise TypeError("Field %s.%s has unrecognised type id %d" % (
        message.__class__.__name__, field.name, field.type))


def _repeated(type_cast_callable):
    return lambda list_vals: [type_cast_callable(val) for val in list_vals]


def _get_dict_to_fill(message):
    """
    We are populating an empty dictionary from the message descriptor fields. This solves
    the problem of proto not sending zeroed values, say empty string (""), zero value in
    an int, 0 constant of an enum, etc.

    We just populate an empty dictionary with the default values and then let the looping
    over the proto object to override the default values
    """
    default_val_dct = {}

    for field in message.DESCRIPTOR.fields:
        if field.label == FieldDescriptor.LABEL_REPEATED:
            if _is_field_a_map(field, message):
                    val = {}
            else:
                val = []

        elif field.type == FieldDescriptor.TYPE_MESSAGE:
            val = {}

        elif field.type == FieldDescriptor.TYPE_ENUM:
            # The first enum value must be zero in proto3. So not sending an enum value
            # can be implicitly assumed to be an intention of sending the value 0.
            val = _enum_label_from_constant(field, 0)

        elif field.type in FIELD_DEFAULT_VALS:
            val = FIELD_DEFAULT_VALS.get(field.type, "")

        default_val_dct[field.name] = val

    return default_val_dct


def _protobuf_to_dict(message):
    """
    Converts a proto object to a python dictionary.
    """

    # Get default value populated dict from the message descriptor.
    result_dict = _get_dict_to_fill(message)

    # Loop over the actual proto object and update the field values, which
    # are set to default
    for field, value in message.ListFields():

        if field.label == FieldDescriptor.LABEL_REPEATED:
            if _is_field_a_map(field, message):
                val_field = field.message_type.fields_by_name['value']
                containing_dict = {}
                for key, val in value.items():
                    if val_field.type == FieldDescriptor.TYPE_MESSAGE:
                        containing_dict[key] = _protobuf_to_dict(val)
                    elif val_field.type == FieldDescriptor.TYPE_ENUM:
                        containing_dict[key] = _enum_label_from_constant(val_field, val)
                    else:
                        containing_dict[key] = val
                result_dict[field.name] = containing_dict

            else:
                type_cast_callable = _get_type_cast_callable(message, field)
                # For a list entity, we need to loop over and type cast each
                result_dict[field.name] = _repeated(type_cast_callable)(value)

        else:
            result_dict[field.name] = _get_type_cast_callable(message, field)(value)

    return result_dict


def protobuf_to_dict(message):
    return _protobuf_to_dict(message)
