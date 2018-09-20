import unittest

from .sample_pb2 import SomeSubMessage
from protofy_shortcuts import parse_proto_message, get_protofy_response


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
        proto_resp = get_protofy_response(self.data_dict, SomeSubMessage)

        d_dict = parse_proto_message(proto_resp, SomeSubMessage)

        self.assertEqual(d_dict, self.data_dict)
