import copy
import time
import unittest

from google.protobuf.timestamp_pb2 import Timestamp

from dict_to_proto3_to_dict import dict_to_protobuf, protobuf_to_dict, convert_to_utc,\
                                   convert_to_local_timezone
from tests.sample_pb2 import MainMessage

_FIRST_JUNE_2018_SECONDS_FROM_EPOCH = 1527811200
_SECONDS_IN_A_DAY = 24 * 60 * 60

class TestProtoUtilModule(unittest.TestCase):

    def setUp(self):
        dct = {}
        dct["a_str"] = "Neeraj Koul"
        dct["an_enum"] = "second"
        dct["an_int"] = 2
        dct["lst_ints"] = [0, 1, 2]
        dct["lst_messages"] = [{"a_str": "first_five_non_zero_odd_nos", "a_long": 5L, "lst_longs": [1L, 3L, 5L, 7L, 9L]},
                               {"a_str": "first_three_prime_nos", "a_long": 3L, "lst_longs": [2L, 3L, 5L]}
                              ]
        dct["lst_enums"] = ["first", "second", "first"]
        dct["int_to_lst_ints_map"] = {1: {"lst_ints": [0, 1]},
                                      2: {"lst_ints": [2, 3]},
                                      3: {"lst_ints": [4, 5]}
                                     }
        dct["str_to_message_map"] = {"where_from" : 
                                             {"a_str": "Kashmir", 
                                              "a_long": 1L, 
                                              "lst_longs": [1L, 2L, 3L]
                                              }
                                        }
        dct["str_to_int_map"] = {"some_str": 1}
        dct["str_to_enum_map"] = {"first_key": "first", "second_key": "second"}
        dct["sub_message"] = {"a_str": "bangalore", "a_long": 560048L, "lst_longs": [1L, 2L, 3L]}

        timestamp_1, timestamp_2, timestamp_3, timestamp_4 = Timestamp(), Timestamp(), \
                                                             Timestamp(), Timestamp()
        timestamp_1.FromJsonString("2018-06-01T05:30:00+5:30")
        timestamp_2.FromJsonString("2018-06-02T00:00:00Z")
        timestamp_3.FromJsonString("2018-06-03T00:00:00Z")
        timestamp_4.FromJsonString("2018-06-04T00:00:00Z")
        dct["a_timestamp"] = timestamp_1
        dct["lst_timestamps"] = [timestamp_2, timestamp_3]
        dct["str_to_timestamp_map"] = {"some_timestamp": timestamp_4}

        self.data_dct = dct
        self.main_msg_fields = self.data_dct.keys()

    def tearDown(self):
        self.data_dct, self.main_msg_fields = None, None

    def _are_fields_in_proto_msg(self, message, fields=[]):
        name_map = {}
        for field, _ in message.ListFields():
            name_map[field.name] = None
        for field in fields:
            if field not in name_map:
                return False
        return True

    def test_all_populated(self):
        msg = MainMessage()
        dict_to_protobuf(self.data_dct, msg)

        self.assertTrue(self._are_fields_in_proto_msg(msg, self.data_dct.keys()))

        dct = protobuf_to_dict(msg)

        self.assertEqual(dct, self.data_dct)

    def test_all_populated_with_serialisation_deserialisation(self):
        msg = MainMessage()
        dict_to_protobuf(self.data_dct, msg)

        self.assertTrue(self._are_fields_in_proto_msg(msg, self.data_dct.keys()))

        # Serialize the proto object
        proto_serialised_str = msg.SerializeToString()

        # Deserialise to proto object
        recv_message = MainMessage()
        recv_message.ParseFromString(proto_serialised_str)

        dct = protobuf_to_dict(recv_message)

        self.assertEqual(dct, self.data_dct)

    def test_basic_scalar_manipulation(self):
        self.data_dct.pop("a_str")
        self.data_dct.pop("an_int")

        msg = MainMessage()
        dict_to_protobuf(self.data_dct, msg)

        self.assertFalse(self._are_fields_in_proto_msg(msg, ["a_str", "an_int"]))

        dct = protobuf_to_dict(msg)
        self.assertEqual(dct["a_str"], "")
        self.assertEqual(dct["an_int"], 0)


    def test_message_manipulation(self):

        self.data_dct["sub_message"]["a_long"] = 560103L

        msg = MainMessage()
        dict_to_protobuf(self.data_dct, msg)

        self.assertTrue(self._are_fields_in_proto_msg(msg, ["sub_message"]))

        dct = protobuf_to_dict(msg)
        self.assertEqual(dct["sub_message"]["a_long"], 560103L)

    def test_list_manipulation(self):
        self.data_dct["lst_ints"] = []
        self.data_dct["lst_messages"].pop(1)
        self.data_dct["lst_enums"].append("second")
        msg = MainMessage()
        dict_to_protobuf(self.data_dct, msg)

        self.assertFalse(self._are_fields_in_proto_msg(msg, ["lst_ints"]))
        self.assertTrue(self._are_fields_in_proto_msg(msg, ["lst_enums", "lst_messages"]))
        self.assertEqual(len(getattr(msg, "lst_enums")), 4)
        self.assertEqual(len(getattr(msg, "lst_messages")), 1)

        dct = protobuf_to_dict(msg)
        self.assertEqual(dct["lst_ints"], [])
        self.assertEqual(dct["lst_enums"], ["first", "second", "first", "second"])
        self.assertEqual(dct["lst_messages"], self.data_dct["lst_messages"])

    def test_enum_manipulation(self):
        self.data_dct["an_enum"] = "first"
        msg = MainMessage()
        dict_to_protobuf(self.data_dct, msg)

        # Am constant value 0 is not sent in enum even if we explicitly set it
        self.assertFalse(self._are_fields_in_proto_msg(msg, ["an_enum"]))

        dct = protobuf_to_dict(msg)
        self.assertEqual(dct["an_enum"], "first")
        self.assertEqual(dct["str_to_enum_map"]["first_key"], "first")


        # We check for the constant 1, which will be sent in the proto message
        self.data_dct["an_enum"] = "second"
        msg = MainMessage()
        dict_to_protobuf(self.data_dct, msg)

        # As constant value 0 is not sent in enum even if we explicitly set it
        self.assertTrue(self._are_fields_in_proto_msg(msg, ["an_enum"]))

    def test_map_manipulation(self):
        self.data_dct["int_to_lst_ints_map"][1] = {}
        self.data_dct["int_to_lst_ints_map"].pop(2)

        self.data_dct["str_to_message_map"]["where_from"].pop("a_long")

        msg = MainMessage()
        dict_to_protobuf(self.data_dct, msg)

        self.assertTrue(1 in getattr(msg, "int_to_lst_ints_map").keys())
        self.assertTrue(2 not in getattr(msg, "int_to_lst_ints_map").keys())
        self.assertTrue("first_key" in getattr(msg, "str_to_enum_map").keys())

        dct = protobuf_to_dict(msg)
        self.assertEqual(dct["int_to_lst_ints_map"][1], {"lst_ints": []})
        self.assertEqual(dct["int_to_lst_ints_map"][3], self.data_dct["int_to_lst_ints_map"][3])
        self.assertEqual(dct["str_to_enum_map"]["first_key"], "first")
        self.assertEqual(dct["str_to_int_map"]["some_str"], 1)

        check_dct = {"a_str": "Kashmir", "lst_longs": [1L, 2L, 3L], "a_long": 0L}
        self.assertEqual(dct["str_to_message_map"]["where_from"], check_dct)

    def test_serialising_data_which_is_not_part_of_schema(self):
        data_dct_copy = copy.deepcopy(self.data_dct)

        self.data_dct["new_int"] = 11
        msg = MainMessage()
        dict_to_protobuf(self.data_dct, msg)

        self.assertFalse(self._are_fields_in_proto_msg(msg, ["new_int"]))

        dct = protobuf_to_dict(msg)

        self.assertEqual(dct, data_dct_copy)

    def test_timestamps(self):
        msg = MainMessage()
        dict_to_protobuf(self.data_dct, msg)

        self.assertEqual(getattr(msg, "a_timestamp").seconds, _FIRST_JUNE_2018_SECONDS_FROM_EPOCH)
        self.assertEqual(getattr(msg, "lst_timestamps")[0].seconds,
            _FIRST_JUNE_2018_SECONDS_FROM_EPOCH + _SECONDS_IN_A_DAY)
        #dct["str_to_timestamp_map"] = {"some_timestamp": timestamp_4}
        self.assertEqual(getattr(msg, "str_to_timestamp_map")["some_timestamp"].seconds,
            _FIRST_JUNE_2018_SECONDS_FROM_EPOCH + (3* _SECONDS_IN_A_DAY))

        dct = protobuf_to_dict(msg)

        self.assertEqual(dct["a_timestamp"].seconds, _FIRST_JUNE_2018_SECONDS_FROM_EPOCH)
        self.assertEqual(dct["lst_timestamps"][0].seconds,
            _FIRST_JUNE_2018_SECONDS_FROM_EPOCH + _SECONDS_IN_A_DAY)
        self.assertEqual(dct["str_to_timestamp_map"]["some_timestamp"].seconds,
            _FIRST_JUNE_2018_SECONDS_FROM_EPOCH + (3* _SECONDS_IN_A_DAY))

    def test_convert_to_utc(self):
        ts = Timestamp()
        ts.FromJsonString("2018-06-01T00:00:00+5:30")
        ts_old_seconds = ts.seconds

        convert_to_utc(ts)
        ts_new_seconds = ts.seconds

        self.assertEqual(ts_old_seconds - ts_new_seconds, (5*60*60+30*60))

    def test_convert_to_local_timezone(self):
        ts = Timestamp()
        ts.FromJsonString("2018-06-01T00:00:00Z")

        ts_old_seconds = ts.seconds
        offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
        convert_to_local_timezone(ts)
        ts_new_seconds = ts.seconds

        self.assertEqual(ts_old_seconds - ts_new_seconds, offset)
