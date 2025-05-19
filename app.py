from ospf import synchronize_routers, print_forwarding_tables, print_preferred_path
from router import get_topology_from_user # moved to router from app.py

def main():
    topology = get_topology_from_user()
    routers = synchronize_routers(topology)

    choice = input("Enter 1 to print all routing tables, 2 to get preferred path between two routers: ").strip()
    if choice == "1":
        print_forwarding_tables(routers)
    elif choice == "2":
        src = int(input("Enter source router ID: "))
        dst = int(input("Enter destination router ID: "))
        print_preferred_path(routers, src, dst)
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
