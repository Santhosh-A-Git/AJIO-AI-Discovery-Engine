import sqlite3

conn = sqlite3.connect('data/warehouse/ajio_warehouse.db')
cursor = conn.cursor()

updates = [
    (3, "App Crashes"),
    (4, "App Performance"),
    (7, "Fake Delivery and OTP"),
    (8, "Delayed Deliveries"),
    (9, "Return Pickup Issues"),
    (10, "General Fulfillment")
]

for cluster_id, new_name in updates:
    cursor.execute("UPDATE clusters SET cluster_name=? WHERE cluster_id=?", (new_name, cluster_id))

conn.commit()
print("Updated successfully")
conn.close()
