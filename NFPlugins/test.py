from nfstream import NFPlugin


class FFE(NFPlugin):
        
    def on_init(self, packet, flow):
        pass

    def on_update(self, packet, flow):
        pass

    def on_expire(self, flow):
        flow.udps.bytes_fea = b"\x01\x02".ljust(100, b"\x00")

    def cleanup(self):
        pass

    @staticmethod
    def get_storage_dimen():
        # the elements of dimen multiplied should be equal to len(flow.udps.bytes_fea)
        dimen = (100)
        return dimen