__author__ = 'ujjwal tak'

from .dict_to_proto3_to_dict import dict_to_protobuf, protobuf_to_dict

__all__ = ['get_dict_from_proto_message', 'get_proto_message_from_dict']

def get_dict_from_proto_message(message, proto_class):
    """
    Get parsed proto message.

    :param message : (bytes/str) proto message to be converted into dict.
    :param proto_class: (class) proto class from the source.
    :return: (dict)
    """
    proto_obj = proto_class()

    # Deserialize proto
    proto_obj.ParseFromString(message)

    # get a dict out
    return protobuf_to_dict(proto_obj)


def get_proto_message_from_dict(data_dict, proto_class):
    """
    Get protofied response.

    :param data_dict (dict): json data to be converted into proto.
    :param proto_class: proto class from the source.
    :return: bytes or str.
    """
    proto_obj = proto_class()

    # Populate the proto object from the dict
    dict_to_protobuf(data_dict, proto_obj)

    # Serialize proto
    return proto_obj.SerializeToString()

