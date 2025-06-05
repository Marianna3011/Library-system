from backend.db import session

def count_reservations():
    try:
        query = "SELECT COUNT(*) FROM reservations"
        result = session.execute(query)
        count = result.one()[0]
        print(f"Total reservations: {count}")
    except Exception as e:
        print(f"Error counting reservations: {e}")

if __name__ == "__main__":
    count_reservations()