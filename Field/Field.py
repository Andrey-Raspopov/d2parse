from Field.FieldModelEnum import FieldModelEnum

fieldTypeDecoders = {
    "bool": "booleanDecoder",
    "char": "stringDecoder",
    "color32": "unsignedDecoder",
    "int16": "signedDecoder",
    "int32": "signedDecoder",
    "int64": "signedDecoder",
    "int8": "signedDecoder",
    "uint16": "unsignedDecoder",
    "uint32": "unsignedDecoder",
    "uint8": "unsignedDecoder",

    "CBodyComponent": "componentDecoder",
    "CGameSceneNodeHandle": "unsignedDecoder",
    "Color": "unsignedDecoder",
    "CPhysicsComponent": "componentDecoder",
    "CRenderComponent": "componentDecoder",
    "CUtlString": "stringDecoder",
    "CUtlStringToken": "unsignedDecoder",
    "CUtlSymbolLarge": "stringDecoder",
}

class Field:
    def __init__(self, ser, f):
        self.parent_name = None

        if f.var_name_sym != 0:
            self.var_name = ser.symbols[f.var_name_sym]
        else:
            self.var_name = None

        if f.var_type_sym != 0:
            self.var_type = ser.symbols[f.var_type_sym]
        else:
            self.var_type = None

        if f.send_node_sym != 0:
            self.send_node = ser.symbols[f.send_node_sym]
        else:
            self.send_node = None

        if f.field_serializer_name_sym != 0:
            self.serializer_name = ser.symbols[f.field_serializer_name_sym]
        elif f.field_serializer_name_sym == 0 and self.var_type == "CBodyComponent":
            self.serializer_name = ser.symbols[f.field_serializer_name_sym]
        else:
            self.serializer_name = None

        self.serializer_version = f.field_serializer_version

        if f.var_encoder_sym != 0:
            self.encoder = ser.symbols[f.var_encoder_sym]
        else:
            self.encoder = None

        self.encode_flags = f.encode_flags
        self.bit_count = f.bit_count
        self.low_value = f.low_value
        self.high_value = f.high_value
        self.field_type = None
        self.serializer = None
        self.value = None
        self.model = FieldModelEnum.fieldModelSimple

        self.decoder = None
        self.base_decoder = None
        self.child_decoder = None

        if self.send_node == "(root)":
            self.send_node = ""

    def set_model(self, model):
        self.model = model

        if model == FieldModelEnum.fieldModelFixedArray.value:
            if self.field_type.base_type == "float32":
                if self.encoder == "coord":
                    self.decoder = "floatCoordDecoder"
                elif self.encoder == "simtime":
                    self.decoder = "simulationTimeDecoder"
                elif self.encoder == "runeTimeDecoder":
                    self.decoder = "runeTimeDecoder"
                elif self.bit_count == None or self.bit_count <= 0 or self.bit_count >= 32:
                    self.decoder = "noscaleDecoder"
                else:
                    self.decoder = "QuantizedFloatDecoder"
            elif self.field_type.base_type == "CNetworkedQuantizedFloat":
                self.decoder = "QuantizedFloatDecoder"
            elif self.field_type.base_type == "Vector":
                if self.encoder == "normal":
                    self.decoder = "vectorNormalDecoder"
                else:
                    if self.encoder == "coord":
                        self.decoder = "floatCoordDecoder_3"
                    elif self.encoder == "simtime":
                        self.decoder = "simulationTimeDecoder_3"
                    elif self.encoder == "runetime":
                        self.decoder = "runeTimeDecoder_3"
                    elif self.bit_count == None or self.bit_count <= 0 or self.bit_count >= 32:
                        self.decoder = "noscaleDecoder_3"
                    else:
                        self.decoder = "quantizedFactor_3"
            elif self.field_type.base_type == "Vector2D":
                if self.encoder == "coord":
                    self.decoder = "floatCoordDecoder_2"
                elif self.encoder == "simtime":
                    self.decoder = "simulationTimeDecoder_2"
                elif self.encoder == "runetime":
                    self.decoder = "runeTimeDecoder_2"
                elif self.bit_count == None or self.bit_count <= 0 or self.bit_count >= 32:
                    self.decoder = "noscaleDecoder_2"
                else:
                    self.decoder = "quantizedFactor_2"
            elif self.field_type.base_type == "Vector4D":
                if self.encoder == "coord":
                    self.decoder = "floatCoordDecoder_4"
                elif self.encoder == "simtime":
                    self.decoder = "simulationTimeDecoder_4"
                elif self.encoder == "runetime":
                    self.decoder = "runeTimeDecoder_4"
                elif self.bit_count == None or self.bit_count <= 0 or self.bit_count >= 32:
                    self.decoder = "noscaleDecoder_4"
                else:
                    self.decoder = "quantizedFactor_4"
            elif self.field_type.base_type == "uint64":
                if self.encoder == "fixed64":
                    self.decoder = "fixed64Decoder"
                else:
                    self.decoder = "unsigned64Decoder"
            elif self.field_type.base_type == "QAngle":
                if self.encoder == "qangle_pitch_yaw":
                    n = int(self.bit_count)
                    self.decoder = "QAngle_1"
                elif self.bit_count == 0 and self.bit_count != None:
                    n = int(self.bit_count)
                    self.decoder = "QAngle_2"
                else:
                    self.decoder = "QAngle_3"
            elif self.field_type.base_type == "CHandle":
                self.decoder = "unsignedDecoder"
            elif self.field_type.base_type == "CStrongHandle":
                if self.encoder == "fixed64":
                    self.decoder = "fixed64Decoder"
                else:
                    self.decoder = "unsigned64Decoder"
            elif self.field_type.base_type == "CEntityHandle":
                self.decoder = "unsignedDecoder"
            elif self.field_type.base_type in fieldTypeDecoders:
                self.decoder = fieldTypeDecoders[self.field_type.base_type]
            else:
                self.decoder = "defaultDecoder"
        elif model == FieldModelEnum.fieldModelFixedTable.value:
            self.base_decoder = "booleanDecoder"
        elif model == FieldModelEnum.fieldModelVariableArray.value:
            if self.field_type.generic_type == None:
                print("return")
                return -1

            self.base_decoder = "unsignedDecoder"
            if self.field_type.generic_type.base_type in fieldTypeDecoders:
                self.child_decoder = fieldTypeDecoders[self.field_type.generic_type.base_type]
            else:
                self.child_decoder = "defaultDecoder"
        elif model == FieldModelEnum.fieldModelVariableTable.value:
            self.base_decoder = "unsignedDecoder"
        elif model == FieldModelEnum.fieldModelSimple.value:
            if self.field_type.base_type == "float32":
                if self.encoder == "coord":
                    self.decoder = "floatCoordDecoder"
                elif self.encoder == "simtime":
                    self.decoder = "simulationTimeDecoder"
                elif self.encoder == "runeTimeDecoder":
                    self.decoder = "runeTimeDecoder"
                elif self.bit_count == None or self.bit_count <= 0 or self.bit_count >= 32:
                    self.decoder = "noscaleDecoder"
                else:
                    self.decoder = "QuantizedFloatDecoder"
            elif self.field_type.base_type == "CNetworkedQuantizedFloat":
                self.decoder = "QuantizedFloatDecoder"
            elif self.field_type.base_type == "Vector":
                if self.encoder == "normal":
                    self.decoder = "vectorNormalDecoder"
                else:
                    if self.encoder == "coord":
                        self.decoder = "floatCoordDecoder_3"
                    elif self.encoder == "simtime":
                        self.decoder = "simulationTimeDecoder_3"
                    elif self.encoder == "runetime":
                        self.decoder = "runeTimeDecoder_3"
                    elif self.bit_count == None or self.bit_count <= 0 or self.bit_count >= 32:
                        self.decoder = "noscaleDecoder_3"
                    else:
                        self.decoder = "quantizedFactor_3"
            elif self.field_type.base_type == "Vector2D":
                if self.encoder == "coord":
                    self.decoder = "floatCoordDecoder_2"
                elif self.encoder == "simtime":
                    self.decoder = "simulationTimeDecoder_2"
                elif self.encoder == "runetime":
                    self.decoder = "runeTimeDecoder_2"
                elif self.bit_count == None or self.bit_count <= 0 or self.bit_count >= 32:
                    self.decoder = "noscaleDecoder_2"
                else:
                    self.decoder = "quantizedFactor_2"
            elif self.field_type.base_type == "Vector4D":
                if self.encoder == "coord":
                    self.decoder = "floatCoordDecoder_4"
                elif self.encoder == "simtime":
                    self.decoder = "simulationTimeDecoder_4"
                elif self.encoder == "runetime":
                    self.decoder = "runeTimeDecoder_4"
                elif self.bit_count == None or self.bit_count <= 0 or self.bit_count >= 32:
                    self.decoder = "noscaleDecoder_4"
                else:
                    self.decoder = "quantizedFactor_4"
            elif self.field_type.base_type == "uint64":
                if self.encoder == "fixed64":
                    self.decoder = "fixed64Decoder"
                else:
                    self.decoder = "unsigned64Decoder"
            elif self.field_type.base_type == "QAngle":
                if self.encoder == "qangle_pitch_yaw":
                    n = int(self.bit_count)
                    self.decoder = "QAngle_1"
                elif self.bit_count != 0 and self.bit_count != None:
                    n = int(self.bit_count)
                    self.decoder = "QAngle_2"
                else:
                    self.decoder = "QAngle_3"
            elif self.field_type.base_type == "CHandle":
                self.decoder = "unsignedDecoder"
            elif self.field_type.base_type == "CStrongHandle":
                if self.encoder == "fixed64":
                    self.decoder = "fixed64Decoder"
                else:
                    self.decoder = "unsigned64Decoder"
            elif self.field_type.base_type == "CEntityHandle":
                self.decoder = "unsignedDecoder"
            elif self.field_type.base_type in fieldTypeDecoders:
                self.decoder = fieldTypeDecoders[self.field_type.base_type]
            else:
                self.decoder = "defaultDecoder"
