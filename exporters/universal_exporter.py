import os

class UniversalExporter:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir

    def export_hosts(self, domain_list, filename="xinet_hosts.txt"):
        """Standard HOSTS Format: 0.0.0.0 domain.com"""
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write("# X-iNet Universal HOSTS Filter\n")
            for d in domain_list:
                f.write(f"0.0.0.0 {d}\n")
        return path

    def export_pihole(self, domain_list, filename="xinet_pihole.txt"):
        """Pi-hole braucht oft nur eine reine Liste."""
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            for d in domain_list:
                f.write(f"{d}\n")
        return path