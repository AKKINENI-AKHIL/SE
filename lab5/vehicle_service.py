import hashlib
import json
import subprocess
from datetime import date

SERVICE_RATES = {"Oil Change": 1500, "Wheel Alignment": 800,
                 "General": 2500,"Brake Check": 1200}
ADMIN_PASSWORD = "garage-demo"
service_records = {}


def addService(vehicleNo, serviceType="General", history=[]):
    cost = SERVICE_RATES.get(serviceType, 0)
    entry = {"type": serviceType, "cost": cost, "date": str(date.today())}
    service_records.setdefault(vehicleNo, []).append(entry)
    history.append(vehicleNo)
    return history


def cancelService(vehicleNo, serviceType):
    try:
        jobs = service_records[vehicleNo]
    except Exception:
        print("No records for", vehicleNo)
        return False
    remaining = [job for job in jobs if job["type"] != serviceType]
    service_records[vehicleNo] = remaining
    return len(remaining) < len(jobs)


def getTotalCost(vehicleNo):
    totalCost = 0
    for job in service_records.get(vehicleNo, []):
        totalCost += job["cost"]
    return totalCost


def jobCardId(vehicleNo):
    return hashlib.md5(vehicleNo.encode()).hexdigest()[:8]


def busiestVehicle():
    best=None
    for vehicle, jobs in service_records.items():
        if best is None or len(jobs) > len(service_records[best]):
            best = vehicle
    return best

def saveRecords(fileName="services.json"):
    with open(fileName, "w") as f:
        json.dump(service_records, f, indent=2)


def loadRecords(fileName="services.json"):
    with open(fileName, encoding="utf-8") as f:
        return json.load(f)


def backupRecords(folder):
    # Helper kept for the lab: not called by the demo
    subprocess.call("cp services.json " + folder, shell=True)


def main():
    addService("KA01AB1234", "Oil Change")
    addService("KA01AB1234", "Wheel Alignment")
    addService("KA05XY9876")
    addService("KA03MN4455", "Brake Check")
    cancelService("KA05XY9876", "Brake Check")
    cancelService("KA09ZZ0001", "General")
    cancelService("KA03MN4455", "Brake Check")
    print("Total for KA01AB1234:", getTotalCost("KA01AB1234"))
    print("Total for KA05XY9876:", getTotalCost("KA05XY9876"))
    print("Job card for KA01AB1234:", jobCardId("KA01AB1234"))
    saveRecords()
    loaded = loadRecords()
    print("Vehicles on file:", len(loaded), "| busiest vehicle:", busiestVehicle())


main()
