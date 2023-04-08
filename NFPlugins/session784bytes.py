from nfstream import NFPlugin


class FFE(NFPlugin) :

    @staticmethod
    def __get_pk_pad(packet):
        tmp = packet.ip_packet

        # handle IP layer
        if packet.ip_version == 4: # ipv4
            pad = tmp[:12] + tmp[20:]
        elif packet.ip_version == 6: # ipv6
            pad = tmp[:8] + tmp[40:]
        else:
            pass
        return pad

    @staticmethod
    def __padding_with_size(seq: str, size: int) -> str:
        if seq:
            seq = seq.ljust(size, b"\x00")[:size]
        else:
            seq = b"\x00" * size
        return seq
        
    def on_init(self, packet, flow):
        flow.udps.bytes_fea = self.__get_pk_pad(packet)

    def on_update(self, packet, flow):
        pad_size = len(flow.udps.bytes_fea)
        if pad_size < 784:
            flow.udps.bytes_fea += self.__get_pk_pad(packet)[:784-pad_size]

    def on_expire(self, flow):
        flow.udps.bytes_fea = self.__padding_with_size(flow.udps.bytes_fea, 28 * 28)

    def cleanup(self):
        pass

    @staticmethod
    def get_storage_dimen():
        # the elements of dimen multiplied should be equal to len(flow.udps.bytes_fea)
        dimen = (28, 28)
        return dimen
