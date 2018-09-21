import unittest

from .sample_pb2 import SomeSubMessage
from shortcuts import get_dict_from_proto_message, get_proto_message_from_dict


class TestProtoShortcuts(unittest.TestCase):

    def setUp(self):
        dct = dict(
            a_str='ujjwal',
            a_long=1234567890,
            lst_longs=[1234567890, 9876543210]
        )
        self.data_dict = dct
        self.main_msg_fields = self.data_dict.keys()

    def tearDown(self):
        self.data_dct, self.main_msg_fields = None, None

    def test_protofy(self):
        proto_resp = get_proto_message_from_dict(self.data_dict, SomeSubMessage)

        d_dict = get_dict_from_proto_message(proto_resp, SomeSubMessage)

        self.assertEqual(d_dict, self.data_dict)
