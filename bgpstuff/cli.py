import bgpstuff

client = bgpstuff.Client()

def cli():
    total_v4 = client.get_totals()
    total_v6 = client.get_totals()
    print(f"{client.total_v4} IPv4 Routes")
    print(f"{client.total_v6} IPv6 Routes")
