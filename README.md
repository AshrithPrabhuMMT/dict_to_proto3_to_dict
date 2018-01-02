# dict_to_proto3_to_dict
A python helper library to create a proto3 object from a dict and also the other way round, i.e, a dict from a proto3 object.  Handles Maps and filling up of default values in the dict created.


## What's handled
 - Standard basic scalars, repeated fields, enums, etc.
 - Most importantly **_maps_** are handled
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

## Tests

Tests are under `src/tests/` folder. To run, we use [nosetests](https://nose.readthedocs.io/en/latest/)

```sh
$ nosetests src/tests/
```


