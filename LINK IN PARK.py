import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from collections import deque
import datetime


class ParkingLotGUI(tk.Tk):
    def __init__(self, slots):
        super().__init__()
        self.title("Sistem Manajemen Parkir")
        self.slots = slots
        self.parking_lot = [[] for _ in range(slots)]
        self.entry_times = {}
        self.initialize_gui()

    def initialize_gui(self):
        self.configure(bg="#F0F0F0")  # Mengatur warna latar belakang

        self.canvas = tk.Canvas(self, width=600, height=400, bg="#F0F0F0")
        self.canvas.pack()

        self.slot_labels = []
        for i in range(self.slots):
            x = 50 + (i % 5) * 100
            y = 50 + (i // 5) * 100
            slot_label = self.canvas.create_rectangle(
                x, y, x + 80, y + 80, fill="green", outline="#A0A0A0", width=2
            )
            self.canvas.create_text(x + 40, y + 20, text=str(i + 1), font=("Arial", 12))
            self.slot_labels.append(slot_label)

        self.car_number_label = tk.Label(
            self, text="Nomor Kendaraan:", font=("Arial", 12), bg="#F0F0F0"
        )
        self.car_number_label.pack()
        self.car_entry = tk.Entry(self, font=("Arial", 12))
        self.car_entry.pack()

        self.car_type_label = tk.Label(
            self, text="Jenis Mobil:", font=("Arial", 12), bg="#F0F0F0"
        )
        self.car_type_label.pack()
        self.car_type_combo = ttk.Combobox(
            self,
            values=[
                "SUV",
                "MPV",
                "Sedan",
                "Truk",
                "Bus",
                "Double Cabin",
                "Off Road",
                "Wagon",
                "Hatchback",
                "Limousine",
            ],
            font=("Arial", 12),
        )
        # state="readonly")
        self.car_type_combo.pack()

        self.car_enter_button = tk.Button(
            self,
            text="Masuk",
            command=self.enter_car,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            relief=tk.FLAT,
        )
        self.car_enter_button.pack()

        self.car_exit_button = tk.Button(
            self,
            text="Keluar",
            command=self.exit_car,
            font=("Arial", 12, "bold"),
            bg="#F44336",
            fg="white",
            relief=tk.FLAT,
        )
        self.car_exit_button.pack()

        self.car_listbox = tk.Listbox(
            self, font=("Arial", 12), relief=tk.FLAT, selectbackground="#B0B0B0"
        )
        self.car_listbox.pack()

    def enter_car(self):
        car_number = self.car_entry.get()
        car_type = self.car_type_combo.get()

        if car_number and car_type:
            if self.is_car_parked(car_number):
                messagebox.showwarning(
                    "Duplicate Car", "Car with the same number plate is already parked."
                )
            elif not self.is_car_allowed(car_type):
                messagebox.showwarning(
                    "Invalid Car Type",
                    "The car type is not allowed in the parking lot.",
                )
            else:
                slot_index = self.get_next_available_slot()
                if slot_index is not None:
                    self.parking_lot[slot_index].append(car_number)
                    self.entry_times[car_number] = datetime.datetime.now()
                    self.update_slot(slot_index)
                    self.update_car_list()
                    self.show_entry_ticket(car_number, slot_index, car_type)
                else:
                    messagebox.showwarning("Parking Lot Full", "Parking lot is full.")
        else:
            messagebox.showwarning("Invalid Input", "Please fill in all fields.")
        self.car_entry.delete(0, tk.END)
        self.car_type_combo.delete(0, tk.END)

    def is_car_allowed(self, car_type):
        allowed_car_types = [
            "SUV",
            "Sedan",
            "MPV",
            "Double Cabin",
            "Off Road",
            "Wagon",
            "Hatchback",
        ]  # Jenis mobil yang diizinkan masuk parkiran

        if car_type in allowed_car_types:
            return True
        return False

    def is_car_parked(self, car_number):
        for slot in self.parking_lot:
            if car_number in slot:
                return True
        return False

    def get_next_available_slot(self):
        visited = set()
        queue = deque()
        queue.append(0)  # Mulai pencarian dari slot 0
        while queue:
            current_slot = queue.popleft()
            if not self.parking_lot[current_slot]:
                return current_slot
            if current_slot not in visited:
                visited.add(current_slot)
                neighbors = self.get_adjacent_slots(current_slot)
                queue.extend(neighbors)
        return None

    def get_adjacent_slots(self, slot_index):
        # Mendapatkan slot tetangga yang terhubung dengan slot_index (misalnya, menggunakan aturan tertentu)
        # Di sini, kita menggunakan aturan tetangga sejajar
        adjacent_slots = []
        if slot_index > 0:
            adjacent_slots.append(slot_index - 1)
        if slot_index < self.slots - 1:
            adjacent_slots.append(slot_index + 1)
        return adjacent_slots

    def exit_car(self):
        car_number = self.car_entry.get()
        if car_number:
            if not self.is_car_parked(car_number):
                messagebox.showwarning(
                    "Car Not Found",
                    "Car with the specified number plate is not parked.",
                )
            else:
                slot_index = self.find_car_slot(car_number)
                self.parking_lot[slot_index].remove(car_number)
                entry_time = self.entry_times.pop(car_number)
                exit_time = datetime.datetime.now()
                parking_duration = exit_time - entry_time
                parking_cost = self.calculate_parking_cost(
                    parking_duration.total_seconds()
                )
                self.update_slot(slot_index)
                self.update_car_list()
                self.show_exit_ticket(
                    car_number,
                    slot_index,
                    entry_time=entry_time,
                    exit_time=exit_time,
                    parking_cost=parking_cost,
                )
        else:
            messagebox.showwarning("Invalid Input", "Please enter a car number.")
        self.car_entry.delete(0, tk.END)

    def calculate_parking_cost(self, parking_duration_seconds):
        base_cost = 5000
        additional_cost_per_10_seconds = 2000

        additional_duration_seconds = parking_duration_seconds - 10
        additional_duration_units = int(additional_duration_seconds / 10)
        additional_cost = additional_duration_units * additional_cost_per_10_seconds

        parking_cost = base_cost + additional_cost
        return parking_cost

    def show_entry_ticket(self, car_number, slot_index, car_type):
        ticket = f"PARKING TICKET\n\nCar Number: {car_number}\nSlot Number: {slot_index + 1}\nCar Type: {car_type}\nEntry Time: {self.entry_times[car_number]}\n"
        messagebox.showinfo("Parking Ticket", ticket)

    def show_exit_ticket(
        self, car_number, slot_index, entry_time=None, exit_time=None, parking_cost=None
    ):
        ticket = f"PARKING TICKET\n\nCar Number: {car_number}\nSlot Number: {slot_index + 1}\n"
        if entry_time and exit_time:
            parking_duration = exit_time - entry_time
            ticket += f"Entry Time: {entry_time}\nExit Time: {exit_time}\n"
            ticket += f"Parking Duration: {parking_duration}\n"
        if parking_cost:
            ticket += f"Parking Cost: Rp. {parking_cost}"
        messagebox.showinfo("Parking Ticket", ticket)

    def find_car_slot(self, car_number):
        for i, slot in enumerate(self.parking_lot):
            if car_number in slot:
                return i
        return None

    def update_slot(self, slot_index):
        slot_label = self.slot_labels[slot_index]
        if self.parking_lot[slot_index]:
            self.canvas.itemconfig(slot_label, fill="red")
        else:
            self.canvas.itemconfig(slot_label, fill="green")

    def update_car_list(self):
        self.car_listbox.delete(0, tk.END)
        for i, slot in enumerate(self.parking_lot):
            slot_number = i + 1
            if slot:
                cars = ", ".join(slot)
                self.car_listbox.insert(tk.END, f"Slot {slot_number}: {cars}")
            else:
                self.car_listbox.insert(tk.END, f"Slot {slot_number}: Empty")


if __name__ == "__main__":
    parking_lot_gui = ParkingLotGUI(10)
    parking_lot_gui.mainloop()
