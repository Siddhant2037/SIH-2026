"""Example adapter contract. Replace internals with a validated parser."""
class HikvisionAdapter:
    vendor = "HIKVISION"
    def identify(self, source): return {"vendor": self.vendor, "confidence": 0.98}
    def parse_filesystem(self, image): raise NotImplementedError
    def extract_metadata(self, image): raise NotImplementedError
    def recover_recordings(self, image, filters=None): raise NotImplementedError
    def decode_stream(self, recording): raise NotImplementedError
