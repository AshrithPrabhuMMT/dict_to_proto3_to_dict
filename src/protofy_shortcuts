__author__ = 'ujjwal tak'

from dict_to_proto3_to_dict import dict_to_protobuf, protobuf_to_dict


def parse_proto_message(message, proto_class):
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
    item = protobuf_to_dict(proto_obj)

    return item


def get_protofy_response(data_dict, proto_class):
    """
    Get protofied response.

    :param data_dict (dict): json data to be converted into proto.
    :param proto_class: proto class from the source.
    :return: bytes or str.
    """
    proto_obj = proto_class()
    dict_to_protobuf(data_dict, proto_obj)
    item = proto_obj.SerializeToString()
    return item