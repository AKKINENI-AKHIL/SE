
import hashlib
import json
import shutil
from datetime import date
from pathlib import Path

SERVICE_RATES = {
    "Oil Change": 1500,
    "Wheel Alignment": 800,
    "General": 2500,
    "Brake Check": 1200,
}

service_records = {}


def add_service(vehicle_no, service_type="General", history=None):
    """Add a service booking and record the vehicle in history."""
    if history is None:
        history = []

    cost = SERVICE_RATES.get(service_type, 0)
    entry = {
        "type": service_type,
        "cost": cost,
        "date": str(date.today()),
    }
    service_records.setdefault(vehicle_no, []).append(entry)
    history.append(vehicle_no)
    return history


def cancel_service(vehicle_no, service_type):
    """Cancel matching service jobs for a vehicle."""
    try:
        jobs = service_records[vehicle_no]
    except KeyError:
        print("No records for", vehicle_no)
        return False

    remaining = [
        job for job in jobs if job["type"] != service_type
    ]
    service_records[vehicle_no] = remaining
    return len(remaining) < len(jobs)


def get_total_cost(vehicle_no):
    """Calculate the total service cost for a vehicle."""
    return sum(
        job["cost"]
        for job in service_records.get(vehicle_no, [])
    )


def job_card_id(vehicle_no):
    """Generate a short, deterministic job card identifier."""
    return hashlib.sha256(
        vehicle_no.encode("utf-8")
    ).hexdigest()[:8]


def busiest_vehicle():
    """Return the vehicle with the most recorded service jobs."""
    if not service_records:
        return None

    return max(
        service_records,
        key=lambda vehicle: len(service_records[vehicle]),
    )


def save_records(file_name="services.json"):
    """Save all service records to a JSON file."""
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(service_records, file, indent=2)


def load_records(file_name="services.json"):
    """Load service records from a JSON file."""
    with open(file_name, encoding="utf-8") as file:
        return json.load(file)


def backup_records(folder):
    """Copy the service records file into a backup folder."""
    source = Path("services.json")
    destination = Path(folder)
    destination.mkdir(parents=True, exist_ok=True)

    if not source.is_file():
        raise FileNotFoundError(
            f"Service records file not found: {source}"
        )

    shutil.copy2(source, destination / source.name)


def main():
    """Run a demonstration of the vehicle service system."""
    service_records.clear()

    add_service("KA01AB1234", "Oil Change")
    add_service("KA01AB1234", "Wheel Alignment")
    add_service("KA05XY9876")
    add_service("KA03MN4455", "Brake Check")

    cancel_service("KA05XY9876", "Brake Check")
    cancel_service("KA09ZZ0001", "General")
    cancel_service("KA03MN4455", "Brake Check")

    print(
        "Total for KA01AB1234:",
        get_total_cost("KA01AB1234"),
    )
    print(
        "Total for KA05XY9876:",
        get_total_cost("KA05XY9876"),
    )
    print(
        "Job card for KA01AB1234:",
        job_card_id("KA01AB1234"),
    )

    save_records()
    loaded_records = load_records()

    print(
        "Vehicles on file:",
        len(loaded_records),
        "| busiest vehicle:",
        busiest_vehicle(),
    )


if __name__ == "__main__":
    main()