import tkinter as tk
from backend import utils
from datetime import date, datetime
from tkcalendar import DateEntry
import tkinter.ttk as ttk

app = tk.Tk() 

ROOMS = [1, 2, 3, 4, 5]
HOURS = list(range(8, 16))  

style = ttk.Style()
style.theme_use('clam')  # Try 'clam' or another theme
style.configure('Reserved.TButton', background='cornflower blue')
style.configure('Free.TButton', background='light gray')


def get_selected_date():
    try:
        return main_date_entry.get()
    except Exception as e:
        print(f"Error getting selected date: {e}")
        return date.today().strftime("%Y-%m-%d")

def group_reservations_for_matrix(reservations):
    """Group consecutive reservations by the same user for a room."""
    if not reservations:
        return []
    reservations = sorted(reservations, key=lambda r: r.hour)
    groups = []
    start = end = reservations[0].hour
    user_id = reservations[0].user_id
    for prev, curr in zip(reservations, reservations[1:]):
        if curr.user_id == user_id and curr.hour == end + 1:
            end = curr.hour
        else:
            groups.append((user_id, start, end))
            user_id = curr.user_id
            start = end = curr.hour
    groups.append((user_id, start, end))
    return groups

def load_matrix():
    try:
        for widget in matrix_frame.winfo_children():
            widget.destroy()
        selected_date = get_selected_date()
        
        reservations_by_room = {room: utils.get_reservations(room, selected_date) for room in ROOMS}
        grouped_by_room = {room: group_reservations_for_matrix(reservations_by_room[room]) for room in ROOMS}

        tk.Label(matrix_frame, text="Room/Hour").grid(row=0, column=0)
        for j, hour in enumerate(HOURS):
            tk.Label(matrix_frame, text=f"{hour}:00").grid(row=0, column=j+1)

        
        for i, room in enumerate(ROOMS):
            tk.Label(matrix_frame, text=f"Room {room}").grid(row=i+1, column=0)
            col = 1
            hour = HOURS[0]
            groups = grouped_by_room[room]
            group_idx = 0
            while hour <= HOURS[-1]:
                if group_idx < len(groups) and groups[group_idx][1] == hour:
                    user_id, start, end = groups[group_idx]
                    span = end - start + 1
                    btn = ttk.Button(
                        matrix_frame,
                        style='Reserved.TButton',
                        width=8 * span,
                        text="",
                        command=lambda r=room, h=start: on_reserve_click(r, h)
                    )
                    btn.grid(row=i+1, column=col, columnspan=span, padx=1, pady=1, sticky="nsew")
                    hour = end + 1
                    col += span
                    group_idx += 1
                else:
                    btn = ttk.Button(
                        matrix_frame,
                        style='Free.TButton',
                        width=8,
                        text="",
                        command=lambda r=room, h=hour: make_reservation(r, h)
                    )
                    btn.grid(row=i+1, column=col, padx=1, pady=1, sticky="nsew")
                    hour += 1
                    col += 1
    except Exception as e:
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, f"Error loading matrix: {e}\n")
        print(f"Error loading matrix: {e}")


def on_reserve_click(room, hour):
    try:
        global selected_group
        selected_date = get_selected_date()
        reservations = utils.get_reservations(room, selected_date)
        groups = group_reservations_for_matrix(reservations)
        for user_id, start, end in groups:
            if start <= hour <= end:
                
                room_var.set(room)
                edit_date_entry.set_date(selected_date)  
                start_hour_entry.delete(0, tk.END)
                start_hour_entry.insert(0, start)
                end_hour_entry.delete(0, tk.END)
                end_hour_entry.insert(0, end + 1)  
                result_box.delete("1.0", tk.END)
                result_box.insert(
                    tk.END,
                    f"Room {room}, Date {selected_date}, Hours {start}:00–{end+1}:00, User {user_id}\nEdit and update as needed."
                )
                
                selected_group = {
                    "room": room,
                    "date": selected_date,
                    "start_hour": start,
                    "end_hour": end,
                    "user_id": user_id
                }
                show_edit_fields()
                break
    except Exception as e:
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, f"Error selecting reservation: {e}\n")
        print(f"Error selecting reservation: {e}")

def make_reservation(room, hour):
    try:
        selected_date = get_selected_date()
        user_id = int(prompt_for_user_id())
        while user_id is None:
            return
        try:
            utils.make_reservation(room, selected_date, hour, user_id)
            result_box.delete("1.0", tk.END)
            result_box.insert(tk.END, f"Reserved Room {room} on {selected_date} at {hour}:00\n")
            load_matrix()
        except Exception as e:
            result_box.delete("1.0", tk.END)
            result_box.insert(tk.END, f"Error: {e}\n")
    except Exception as e:
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, f"Error making reservation: {e}\n")
        print(f"Error making reservation: {e}")

def prompt_for_user_id():
    try:
        popup = tk.Toplevel(app)
        popup.title("Enter User ID for the reservation")
        tk.Label(popup, text="User ID for the reservation:").pack(pady=5)
        user_id_entry = tk.Entry(popup)
        user_id_entry.pack(pady=5)

        result = {"user_id": None}

        def submit():
            try:
                result["user_id"] = int(user_id_entry.get())
                popup.destroy()
            except ValueError:
                tk.Label(popup, text="Please enter a valid number.", fg="red").pack()

        tk.Button(popup, text="Submit", command=submit).pack(pady=5)
        popup.grab_set()
        app.wait_window(popup)
        return result["user_id"]
    except Exception as e:
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, f"Error prompting for user ID: {e}\n")
        print(f"Error prompting for user ID: {e}")
        return None


def update_reservation():
    try:
        global selected_group
        try:
            new_room = int(room_var.get())
            new_date = edit_date_entry.get()
            new_start = int(start_hour_entry.get())
            new_end = int(end_hour_entry.get()) - 1
            if not (8 <= new_start <= 15 and 8 <= new_end+1 <= 16 and new_start <= new_end):
                raise ValueError
        except ValueError:
            result_box.delete("1.0", tk.END)
            result_box.insert(tk.END, "Please enter valid room, date, and hour range (8–15, end > start).\n")
            return

        # Check for conflicts
        reservations = utils.get_reservations(new_room, new_date)
        for row in reservations:
            if row.user_id != selected_group["user_id"] and new_start <= row.hour <= new_end:
                result_box.delete("1.0", tk.END)
                result_box.insert(tk.END, f"Conflict: Room {new_room} already reserved at {row.hour}:00 by another user.\n")
                return

        for hour in range(selected_group["start_hour"], selected_group["end_hour"] + 1):
            utils.delete_reservation(selected_group["room"], selected_group["date"], hour)
        import uuid
        for hour in range(new_start, new_end + 1):
            utils.insert_reservation(new_room, new_date, hour, selected_group["user_id"], uuid.uuid4())

        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, "Reservation updated.\n")
        load_matrix()
    except Exception as e:
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, f"Error updating reservation: {e}\n")
        print(f"Error updating reservation: {e}")

def cancel_reservation():
    try:
        global selected_group
        no_res = utils.check_next(selected_group['room'], selected_group['date'], selected_group['start_hour'], selected_group['user_id'])
        for i in range(no_res):
            utils.cancel_reservations([selected_group['room'], selected_group['date'], selected_group['start_hour']+i])
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, f"Reservation of room {selected_group['room']} at {selected_group['start_hour']}:00 hour has been canceled.\n")
        hide_edit_fields()
        load_matrix()
    except Exception as e:
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, f"Error canceling reservation: {e}\n")
        print(f"Error canceling reservation: {e}")

def show_matrix_for_date():
    try:
        for widget in matrix_frame.winfo_children():
            widget.destroy()
        load_matrix()
        matrix_frame.pack(pady=10)
    except Exception as e:
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, f"Error showing matrix for date: {e}\n")
        print(f"Error showing matrix for date: {e}")


tk.Label(app, text="Date (YYYY-MM-DD):").pack()
main_date_entry = DateEntry(app, date_pattern='yyyy-mm-dd')
main_date_entry.pack()

legend_frame = tk.Frame(app)
tk.Label(legend_frame, text="Legend:").pack(side=tk.LEFT)
tk.Label(legend_frame, bg="cornflower blue", width=4, text="").pack(side=tk.LEFT, padx=2)
tk.Label(legend_frame, text="Reserved").pack(side=tk.LEFT)
tk.Label(legend_frame, bg="light gray", width=4, text="").pack(side=tk.LEFT, padx=2)
tk.Label(legend_frame, text="Free").pack(side=tk.LEFT)
legend_frame.pack(pady=5)

def on_main_date_change(event):
    hide_edit_fields()
    if main_date_entry.get():
        show_matrix_for_date()
    else:
        for widget in matrix_frame.winfo_children():
            widget.destroy()
        for widget in legend_frame.winfo_children():
            widget.destroy()

main_date_entry.bind("<<DateEntrySelected>>", on_main_date_change)


matrix_frame = tk.Frame(app)

result_box = tk.Text(app, height=4, width=60)
result_box.pack()

room_var = tk.StringVar()
room_label = tk.Label(app, text="Room (1–5)")
room_entry = tk.OptionMenu(app, room_var, *[str(i) for i in ROOMS])
date_label = tk.Label(app, text="Date (YYYY-MM-DD)")
edit_date_entry = DateEntry(app, date_pattern='yyyy-mm-dd')
start_hour_label = tk.Label(app, text="Start Hour (8–15)")
start_hour_entry = tk.Entry(app)
end_hour_label = tk.Label(app, text="End Hour (9–16)")
end_hour_entry = tk.Entry(app)
update_btn = tk.Button(app, text="Update Reservation", command=update_reservation)
cancel_btn = tk.Button(app, text="Cancel Reservation", command=cancel_reservation)


def show_edit_fields():
    room_label.pack()
    room_entry.pack()
    date_label.pack()
    edit_date_entry.pack() 
    start_hour_label.pack()
    start_hour_entry.pack()
    end_hour_label.pack()
    end_hour_entry.pack()
    update_btn.pack()
    cancel_btn.pack()

def hide_edit_fields():
    room_label.pack_forget()
    room_entry.pack_forget()
    date_label.pack_forget()
    edit_date_entry.pack_forget() 
    start_hour_label.pack_forget()
    start_hour_entry.pack_forget()
    end_hour_label.pack_forget()
    end_hour_entry.pack_forget()
    update_btn.pack_forget()
    cancel_btn.pack_forget()

hide_edit_fields()

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

app.mainloop()
