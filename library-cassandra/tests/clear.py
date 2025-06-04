from backend.db import session

def clear_reservations():
    try:
        session.execute("TRUNCATE reservations")
        print("All reservations have been deleted.")
    except Exception as e:
        print(f"Error clearing reservations: {e}")

if __name__ == "__main__":
    clear_reservations()