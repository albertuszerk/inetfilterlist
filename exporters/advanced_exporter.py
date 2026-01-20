import os

class AdvancedExporter:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir

    def export_dnsmasq(self, domain_list, filename="xinet_dnsmasq.conf"):
        """Format: address=/domain.com/"""
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            for d in domain_list:
                f.write(f"address=/{d}/\n")
        return path

    def export_unbound(self, domain_list, filename="xinet_unbound.conf"):
        """Format: local-zone: 'domain.com' always_nxdomain"""
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            for d in domain_list:
                f.write(f"local-zone: \"{d}\" always_nxdomain\n")
        return path

    def export_rpz(self, domain_list, filename="xinet_rpz.zone"):
        """Format: domain.com CNAME ."""
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write("$TTL 60\n@ IN SOA localhost. root.localhost. (1 6h 1h 1w 1h)\n")
            f.write("@ IN NS localhost.\n")
            for d in domain_list:
                f.write(f"{d} CNAME .\n")
        return path