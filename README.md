# dict_to_proto3_to_dict
A python helper library to create a proto3 object from a dict and also the other way round, i.e, a dict from a proto3 object.  Handles Maps and filling up of default values in the dict created.


## What's handled
 - Standard basic scalars, repeated fields, enums, etc.
 - Most importantly **_maps_** are handled
 - **_Timestamp_** data type is handled. And the code could be modified on lines to accommodate other well known types.
 - Getting default values in the proto to dict conversion. Comes handy in our ecosystem
   as we are not making apps look in the schema to know the type of the field to decipher the default value. Is particularly handy in case of enums, where we want to get constant 0 label name,
   rather than the constant 0/1/etc.
 - Extensions are not handled, as we haven't used that in our ecosystem yet.

## Installation

To install,
```sh
$ python setup.py install
```

## Example Usage
For a proto schema, named say sample.proto, and having the contents like

```protobuf
syntax = "proto3";

message MyMessage {
  string name = 1;
  repeated string languages_known = 2;
  string favourite_movie = 3;
  map<string, string> degree_college_map = 4;
}
```

We can generate the python binding by typing the follwing command in the folder where sample.proto is ( can read more
on the usage and language guide in general [here](https://developers.google.com/protocol-buffers/docs/proto3) )

```sh
protoc --python_out=.  sample.proto
```

Once we have generated sample_pb2.py file, we can go about handling messages like

```python
from dict_to_proto3_to_dict.dict_to_proto3_to_dict import dict_to_protobuf, protobuf_to_dict
from sample_pb2 import MyMessage

data_dct = {"name": "Neeraj Koul", "languages_known": ["Kashmiri", "Hindi", "English"], 
            "favourite_movie": "The Grapes of Wrath", 
            "degree_college_map": {"B.Tech": "NIT Trichy", "12th": "JK Board"}
            }
message = MyMessage()

# Populate the proto object from the dict
dict_to_protobuf(data_dct, message)

# Serialize proto
proto_serialised_str = message.SerializeToString()

recv_message = MyMessage()
# Deserialize proto
recv_message.ParseFromString(proto_serialised_str)

# Get a dict out
protobuf_to_dict(recv_message)
```

Some shortcuts can be used here.
```python
from dict_to_proto3_to_dict.shortcuts import get_dict_from_proto_message, get_proto_message_from_dict
from sample_pb2 import MyMessage

data_dct = {
    "name": "Neeraj Koul", "languages_known": ["Kashmiri", "Hindi", "English"], 
    "favourite_movie": "The Grapes of Wrath", 
    "degree_college_map": {"B.Tech": "NIT Trichy", "12th": "JK Board"}
}

resp_message = get_proto_message_from_dict(data_dct, MyMessage)

resp_dct = get_dict_from_proto_message(resp_message, MyMessage)

```

## Note on protobuf3 Timestamp
First of all, protobuf timestamp objects in python can be created like
```python
from google.protobuf.timestamp_pb2 import Timestamp

from datetime import datetime
time_now = datetime.now()

time_stamp_now = Timestamp()
time_stamp_now.FromDatetime(time_now)

# OR

some_timestamp = Timestamp()
some_timestamp.FromJsonString("2018-06-01T00:00:0Z")
```

protobuf Timestamp preserves seconds from epoch ( 1-1-1970 start of day as UTC) and has no timezone info embedded.So if we are creating an object like

```python
from datetime import datetime
time_now = datetime.now()
```

It is in our local timezone ( say India, in my case). And now if someone in US is deciphering the proto message, he/she will maybe think of time in its own timezone and it will decipher it as some time in future (even though we might have meant now, assuimg message reaching in some milliseconds over the wire, and hence under a second's fidelity). The trick is standardisation, just send everything in UTC and decrpyt in the same. So if we had converted to UTC, the reader at the other side too would have decrypted it that way, and now would have remained just now.

Have written a couple of helper functions **_convert_to_utc_**  and **_convert_to_local_timezone_** to convert Timestamp obejcts to utc and from utc in our local timezone. Could be used like
```python
from datetime import datetime

from dict_to_proto3_to_dict.dict_to_proto3_to_dict import convert_to_utc, convert_to_local_timezone

time_now = datetime.now()

time_stamp_now = Timestamp()
time_stamp_now.FromDatetime(time_now)
convert_to_utc(time_stamp_now)

# Send it over the wire and at the receiving end, could have gotten now in there through
convert_to_local_timezone(timestamp_received)

```

## Tests

Tests are under `src/tests/` folder. To run, we use [nosetests](https://nose.readthedocs.io/en/latest/)

```sh
$ nosetests src/tests/
```



