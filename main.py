from tkinter import *
from tkinter import messagebox
import tkintermapview
import requests
from bs4 import BeautifulSoup

users: list = []
clinics: list = []
doctors: list = []

class Clinic:
    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.coordinates = self.get_coordinates()
        self.marker = map_widget.set_marker(self.coordinates[0], self.coordinates[1], text=self.name)

    def get_coordinates(self) -> list:
        try:
            adres_url: str = f'https://pl.wikipedia.org/wiki/{self.location}'
            response = requests.get(adres_url)
            response.raise_for_status()
            response_html = BeautifulSoup(response.text, 'html.parser')
            latitude_elements = response_html.select('.latitude')
            longitude_elements = response_html.select('.longitude')
            if len(latitude_elements) < 2 or len(longitude_elements) < 2:
                messagebox.showwarning("Ostrzeżenie", f"Nie znaleziono współrzędnych dla {self.location}. Użyto domyślnych współrzędnych.")
                return [52.23, 21.00]
            latitude = float(latitude_elements[1].text.replace(',', '.'))
            longitude = float(longitude_elements[1].text.replace(',', '.'))
            return [latitude, longitude]
        except (requests.RequestException, ValueError, IndexError) as e:
            messagebox.showwarning("Ostrzeżenie", f"Nie udało się pobrać współrzędnych dla {self.location}: {e}. Użyto domyślnych współrzędnych.")
            return [52.23, 21.00]

class Doctor:
    def __init__(self, name, surname, location, clinic_id):
        self.name = name
        self.surname = surname
        self.location = location
        self.clinic_id = clinic_id
        self.coordinates = self.get_coordinates()
        self.marker = map_widget.set_marker(self.coordinates[0], self.coordinates[1], text=f'{self.name} {self.surname}')

    def get_coordinates(self) -> list:
        try:
            adres_url: str = f'https://pl.wikipedia.org/wiki/{self.location}'
            response = requests.get(adres_url)
            response.raise_for_status()
            response_html = BeautifulSoup(response.text, 'html.parser')
            latitude_elements = response_html.select('.latitude')
            longitude_elements = response_html.select('.longitude')
            if len(latitude_elements) < 2 or len(longitude_elements) < 2:
                messagebox.showwarning("Ostrzeżenie", f"Nie znaleziono współrzędnych dla {self.location}. Użyto domyślnych współrzędnych.")
                return [52.23, 21.00]
            latitude = float(latitude_elements[1].text.replace(',', '.'))
            longitude = float(longitude_elements[1].text.replace(',', '.'))
            return [latitude, longitude]
        except (requests.RequestException, ValueError, IndexError) as e:
            messagebox.showwarning("Ostrzeżenie", f"Nie udało się pobrać współrzędnych dla {self.location}: {e}. Użyto domyślnych współrzędnych.")
            return [52.23, 21.00]

    def get_doctor_id(self):
        return f'{self.name} {self.surname} {self.location} {self.clinic_id}'

class User:
    def __init__(self, name, surname, location, data_urodzenia, pesel, doctor_id=None):
        self.name = name
        self.surname = surname
        self.location = location
        self.data_urodzenia = data_urodzenia
        self.pesel = pesel
        self.doctor_id = doctor_id
        self.coordinates = self.get_coordinates()
        self.marker = map_widget.set_marker(self.coordinates[0], self.coordinates[1], text=f'{self.name} {self.surname}')

    def get_coordinates(self) -> list:
        try:
            adres_url: str = f'https://pl.wikipedia.org/wiki/{self.location}'
            response = requests.get(adres_url)
            response.raise_for_status()
            response_html = BeautifulSoup(response.text, 'html.parser')
            latitude_elements = response_html.select('.latitude')
            longitude_elements = response_html.select('.longitude')
            if len(latitude_elements) < 2 or len(longitude_elements) < 2:
                messagebox.showwarning("Ostrzeżenie", f"Nie znaleziono współrzędnych dla {self.location}. Użyto domyślnych współrzędnych.")
                return [52.23, 21.00]
            latitude = float(latitude_elements[1].text.replace(',', '.'))
            longitude = float(longitude_elements[1].text.replace(',', '.'))
            return [latitude, longitude]
        except (requests.RequestException, ValueError, IndexError) as e:
            messagebox.showwarning("Ostrzeżenie", f"Nie udało się pobrać współrzędnych dla {self.location}: {e}. Użyto domyślnych współrzędnych.")
            return [52.23, 21.00]

def add_clinic():
    name = entry_clinic_name.get().strip()
    location = entry_clinic_location.get().strip()
    if not all([name, location]):
        messagebox.showerror("Błąd", "Nazwa i lokalizacja przychodni muszą być wypełnione!")
        return
    if any(clinic.name == name for clinic in clinics):
        messagebox.showerror("Błąd", "Przychodnia o tej nazwie już istnieje!")
        return
    if not location.replace(" ", "_").isalnum():
        messagebox.showerror("Błąd", "Lokalizacja zawiera nieprawidłowe znaki!")
        return
    clinic = Clinic(name, location)
    clinics.append(clinic)
    update_clinic_dropdown()
    entry_clinic_name.delete(0, END)
    entry_clinic_location.delete(0, END)
    show_clinics()

def show_clinics():
    listbox_clinics.delete(0, END)
    for idx, clinic in enumerate(clinics):
        listbox_clinics.insert(idx, f'{idx + 1}. {clinic.name}')

def remove_clinic():
    if not listbox_clinics.curselection():
        messagebox.showerror("Błąd", "Wybierz przychodnię do usunięcia!")
        return
    i = listbox_clinics.index(ACTIVE)
    if any(doctor.clinic_id == clinics[i].name for doctor in doctors):
        messagebox.showerror("Błąd", "Nie można usunąć przychodni, która ma przypisanych lekarzy!")
        return
    clinics[i].marker.delete()
    clinics.pop(i)
    show_clinics()
    update_clinic_dropdown()

def edit_clinic():
    if not listbox_clinics.curselection():
        messagebox.showerror("Błąd", "Wybierz przychodnię do edycji!")
        return
    i = listbox_clinics.index(ACTIVE)
    entry_clinic_name.insert(0, clinics[i].name)
    entry_clinic_location.insert(0, clinics[i].location)
    button_add_clinic.config(text='Zapisz', command=lambda: update_clinic(i))

def update_clinic(i):
    name = entry_clinic_name.get().strip()
    location = entry_clinic_location.get().strip()
    if not all([name, location]):
        messagebox.showerror("Błąd", "Nazwa i lokalizacja przychodni muszą być wypełnione!")
        return
    if any(clinic.name == name and clinic is not clinics[i] for clinic in clinics):
        messagebox.showerror("Błąd", "Przychodnia o tej nazwie już istnieje!")
        return
    if not location.replace(" ", "_").isalnum():
        messagebox.showerror("Błąd", "Lokalizacja zawiera nieprawidłowe znaki!")
        return
    if clinics[i].name != name:
        for doctor in doctors:
            if doctor.clinic_id == clinics[i].name:
                doctor.clinic_id = name
    clinics[i].marker.delete()
    clinics[i].name = name
    clinics[i].location = location
    clinics[i].coordinates = clinics[i].get_coordinates()
    clinics[i].marker = map_widget.set_marker(clinics[i].coordinates[0], clinics[i].coordinates[1], text=name)
    show_clinics()
    update_clinic_dropdown()
    button_add_clinic.config(text='Dodaj przychodnię', command=add_clinic)
    entry_clinic_name.delete(0, END)
    entry_clinic_location.delete(0, END)

def generate_map_of_clinics():
    map_widget.delete_all_marker()
    for clinic in clinics:
        map_widget.set_marker(clinic.coordinates[0], clinic.coordinates[1], text=clinic.name)

def add_doctor():
    name = entry_doctor_name.get().strip()
    surname = entry_doctor_surname.get().strip()
    location = entry_doctor_location.get().strip()
    clinic_id = clinic_var.get() if clinic_var.get() else None
    if not all([name, surname, location, clinic_id]):
        messagebox.showerror("Błąd", "Wszystkie pola lekarza muszą być wypełnione!")
        return
    doctor = Doctor(name, surname, location, clinic_id)
    doctors.append(doctor)
    entry_doctor_name.delete(0, END)
    entry_doctor_surname.delete(0, END)
    entry_doctor_location.delete(0, END)
    clinic_var.set("")
    show_doctors()

def show_doctors():
    listbox_doctors.delete(0, END)
    for idx, doctor in enumerate(doctors):
        listbox_doctors.insert(idx, f'{idx + 1}. {doctor.name} {doctor.surname}')

def remove_doctor():
    if not listbox_doctors.curselection():
        messagebox.showerror("Błąd", "Wybierz lekarza do usunięcia!")
        return
    i = listbox_doctors.index(ACTIVE)
    doctor_patients = [user for user in users if user.doctor_id == doctors[i].get_doctor_id()]
    if doctor_patients:
        messagebox.showerror("Błąd", "Nie można usunąć lekarza, który ma przypisanych pacjentów!")
        return
    doctors[i].marker.delete()
    doctors.pop(i)
    show_doctors()

def edit_doctor():
    if not listbox_doctors.curselection():
        messagebox.showerror("Błąd", "Wybierz lekarza do edycji!")
        return
    i = listbox_doctors.index(ACTIVE)
    entry_doctor_name.insert(0, doctors[i].name)
    entry_doctor_surname.insert(0, doctors[i].surname)
    entry_doctor_location.insert(0, doctors[i].location)
    clinic_var.set(doctors[i].clinic_id)
    button_add_doctor.config(text='Zapisz', command=lambda: update_doctor(i))

def update_doctor(i):
    name = entry_doctor_name.get().strip()
    surname = entry_doctor_surname.get().strip()
    location = entry_doctor_location.get().strip()
    clinic_id = clinic_var.get() if clinic_var.get() else None
    if not all([name, surname, location, clinic_id]):
        messagebox.showerror("Błąd", "Wszystkie pola lekarza muszą być wypełnione!")
        return
    new_doctor = Doctor(name, surname, location, clinic_id)
    doctors[i].marker.delete()
    doctors[i] = new_doctor
    show_doctors()
    button_add_doctor.config(text='Dodaj lekarza', command=add_doctor)
    entry_doctor_name.delete(0, END)
    entry_doctor_surname.delete(0, END)
    entry_doctor_location.delete(0, END)
    clinic_var.set("")

def employee_localization_handler():
    if not listbox_clinics.curselection():
        messagebox.showerror("Błąd", "Wybierz przychodnię, aby zobaczyć szczegóły!")
        return
    i = listbox_clinics.index(ACTIVE)
    clinic_id = clinics[i].name
    map_widget.delete_all_marker()
    doctors_in_clinic = [doctor for doctor in doctors if doctor.clinic_id == clinic_id]
    for doctor in doctors_in_clinic:
        map_widget.set_marker(doctor.coordinates[0], doctor.coordinates[1], text=f'{doctor.name} {doctor.surname}')

def show_users():
    listbox_lista_obiektow.delete(0, END)
    for idx, user in enumerate(users):
        listbox_lista_obiektow.insert(idx, f'{idx + 1}. {user.name} {user.surname}')

def remove_users():
    if not listbox_lista_obiektow.curselection():
        messagebox.showerror("Błąd", "Wybierz pacjenta do usunięcia!")
        return
    i = listbox_lista_obiektow.index(ACTIVE)
    users[i].marker.delete()
    users.pop(i)
    show_users()

def update_clinic_dropdown():
    clinic_menu['menu'].delete(0, 'end')
    for clinic in clinics:
        clinic_menu['menu'].add_command(label=clinic.name, command=lambda c=clinic.name: clinic_var.set(c))

root = Tk()
root.geometry("1600x1000")
root.title("Lista pacjentów")
root.state('zoomed')

main_frame = Frame(root)
main_frame.pack(fill=BOTH, expand=True)

canvas = Canvas(main_frame)
scrollbar = Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scrollable_frame = Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

ramka_clinics = Frame(scrollable_frame, padx=10, pady=10)
ramka_doctors = Frame(scrollable_frame, padx=10, pady=10)
ramka_lista_obiektow = Frame(scrollable_frame, padx=10, pady=10)
ramka_mapa = Frame(scrollable_frame, padx=10, pady=10)

ramka_clinics.grid(row=0, column=0, sticky="nsew")
ramka_doctors.grid(row=0, column=1, sticky="nsew")
ramka_lista_obiektow.grid(row=0, column=2, sticky="nsew")
ramka_mapa.grid(row=1, column=0, columnspan=3, sticky="nsew")

scrollable_frame.grid_rowconfigure(0, weight=1)
scrollable_frame.grid_rowconfigure(1, weight=1)
scrollable_frame.grid_columnconfigure(0, weight=1)
scrollable_frame.grid_columnconfigure(1, weight=1)
scrollable_frame.grid_columnconfigure(2, weight=1)

# ramka_clinics
label_clinics = Label(ramka_clinics, text="Zarządzanie przychodniami:", font=("Arial", 14, "bold"))
label_clinics.grid(row=0, column=0, columnspan=3, pady=(0, 15))

label_clinic_form = Label(ramka_clinics, text="Dodaj przychodnię:", font=("Arial", 11, "bold"))
label_clinic_form.grid(row=1, column=0, columnspan=2, sticky=W, pady=(0, 5))

label_clinic_name = Label(ramka_clinics, text="Nazwa:", font=("Arial", 10))
label_clinic_name.grid(row=2, column=0, sticky=W, pady=5)

label_clinic_location = Label(ramka_clinics, text="Lokalizacja:", font=("Arial", 10))
label_clinic_location.grid(row=3, column=0, sticky=W, pady=5)

entry_clinic_name = Entry(ramka_clinics, width=40, font=("Arial", 10))
entry_clinic_name.grid(row=2, column=1, pady=5, sticky="ew", padx=(10, 0))

entry_clinic_location = Entry(ramka_clinics, width=40, font=("Arial", 10))
entry_clinic_location.grid(row=3, column=1, pady=5, sticky="ew", padx=(10, 0))

button_add_clinic = Button(ramka_clinics, text="Dodaj przychodnię", command=add_clinic, font=("Arial", 10), bg="#4CAF50", fg="white")
button_add_clinic.grid(row=4, column=0, columnspan=2, pady=10)

label_clinics_list = Label(ramka_clinics, text="Lista przychodni:", font=("Arial", 11, "bold"))
label_clinics_list.grid(row=5, column=0, columnspan=2, sticky=W, pady=(10, 5))

clinic_frame = Frame(ramka_clinics)
clinic_frame.grid(row=6, column=0, columnspan=3, pady=5, sticky="nsew")

listbox_clinics = Listbox(clinic_frame, width=50, height=8, font=("Arial", 9))
clinic_scrollbar = Scrollbar(clinic_frame, orient="vertical")
listbox_clinics.config(yscrollcommand=clinic_scrollbar.set)
clinic_scrollbar.config(command=listbox_clinics.yview)

listbox_clinics.pack(side=LEFT, fill=BOTH, expand=True)
clinic_scrollbar.pack(side=RIGHT, fill=Y)

button_frame_clinics = Frame(ramka_clinics)
button_frame_clinics.grid(row=7, column=0, columnspan=3, pady=10)

button_clinic_map_all = Button(button_frame_clinics, text="Generuj mapę wszystkich placówek", command=generate_map_of_clinics, font=("Arial", 9), bg="#2196F3", fg="white")
button_clinic_map_all.pack(side=LEFT, padx=5)

button_clinic_map_employees = Button(button_frame_clinics, text="Mapa lokalizacji pracowników placówki", command=employee_localization_handler, font=("Arial", 9), bg="#2196F3", fg="white")
button_clinic_map_employees.pack(side=LEFT, padx=5)

button_remove_clinic = Button(button_frame_clinics, text="Usuń", command=remove_clinic, font=("Arial", 9), bg="#f44336", fg="white")
button_remove_clinic.pack(side=LEFT, padx=5)

button_edit_clinic = Button(button_frame_clinics, text="Edytuj", command=edit_clinic, font=("Arial", 9), bg="#FF9800", fg="white")
button_edit_clinic.pack(side=LEFT, padx=5)

ramka_clinics.grid_columnconfigure(1, weight=1)
ramka_clinics.grid_rowconfigure(6, weight=1)

# ramka_doctors
label_doctors = Label(ramka_doctors, text="Zarządzanie lekarzami:", font=("Arial", 14, "bold"))
label_doctors.grid(row=0, column=0, columnspan=2, pady=(10, 15), sticky="w")

label_doctor_form = Label(ramka_doctors, text="Dodaj lekarza:", font=("Arial", 11, "bold"))
label_doctor_form.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky="w")

label_doctor_name = Label(ramka_doctors, text="Imię:", font=("Arial", 10))
label_doctor_name.grid(row=2, column=0, sticky="w", pady=5, padx=(10, 5))
entry_doctor_name = Entry(ramka_doctors, width=40, font=("Arial", 10))
entry_doctor_name.grid(row=2, column=1, pady=5, sticky="ew", padx=(0, 10))

label_doctor_surname = Label(ramka_doctors, text="Nazwisko:", font=("Arial", 10))
label_doctor_surname.grid(row=3, column=0, sticky="w", pady=5, padx=(10, 5))
entry_doctor_surname = Entry(ramka_doctors, width=40, font=("Arial", 10))
entry_doctor_surname.grid(row=3, column=1, pady=5, sticky="ew", padx=(0, 10))

label_doctor_location = Label(ramka_doctors, text="Lokalizacja:", font=("Arial", 10))
label_doctor_location.grid(row=4, column=0, sticky="w", pady=5, padx=(10, 5))
entry_doctor_location = Entry(ramka_doctors, width=40, font=("Arial", 10))
entry_doctor_location.grid(row=4, column=1, pady=5, sticky="ew", padx=(0, 10))

label_doctor_clinic = Label(ramka_doctors, text="Przychodnia:", font=("Arial", 10))
label_doctor_clinic.grid(row=5, column=0, sticky="w", pady=5, padx=(10, 5))
clinic_var = StringVar()
clinic_menu = OptionMenu(ramka_doctors, clinic_var, "")
clinic_menu.grid(row=5, column=1, pady=5, sticky="ew", padx=(0, 10))

button_add_doctor = Button(ramka_doctors, text="Dodaj lekarza", command=add_doctor, font=("Arial", 10), bg="#4CAF50", fg="white")
button_add_doctor.grid(row=6, column=0, columnspan=2, pady=10)

label_doctors_list = Label(ramka_doctors, text="Lista lekarzy:", font=("Arial", 11, "bold"))
label_doctors_list.grid(row=7, column=0, columnspan=2, pady=(10, 5), sticky="w")

doctor_frame = Frame(ramka_doctors)
doctor_frame.grid(row=8, column=0, columnspan=2, pady=5, sticky="nsew")

listbox_doctors = Listbox(doctor_frame, width=50, height=8, font=("Arial", 9))
doctor_scrollbar = Scrollbar(doctor_frame, orient="vertical")
listbox_doctors.config(yscrollcommand=doctor_scrollbar.set)
doctor_scrollbar.config(command=listbox_doctors.yview)
listbox_doctors.pack(side=LEFT, fill=BOTH, expand=True)
doctor_scrollbar.pack(side=RIGHT, fill=Y)

button_frame_doctors = Frame(ramka_doctors)
button_frame_doctors.grid(row=9, column=0, columnspan=2, pady=10)

button_remove_doctor = Button(button_frame_doctors, text="Usuń", command=remove_doctor, font=("Arial", 9), bg="#f44336", fg="white")
button_remove_doctor.pack(side=LEFT, padx=5)

button_edit_doctor = Button(button_frame_doctors, text="Edytuj", command=edit_doctor, font=("Arial", 9), bg="#FF9800", fg="white")
button_edit_doctor.pack(side=LEFT, padx=5)

ramka_doctors.grid_columnconfigure(1, weight=1)
ramka_doctors.grid_rowconfigure(8, weight=1)

# ramka_lista_obiektow
label_lista_obiektow = Label(ramka_lista_obiektow, text="Lista pacjentów:", font=("Arial", 14, "bold"))
label_lista_obiektow.grid(row=0, column=0, columnspan=2)

listbox_lista_obiektow = Listbox(ramka_lista_obiektow, width=50, height=10)
listbox_lista_obiektow.grid(row=1, column=0, columnspan=2)

button_usun_obiekt = Button(ramka_lista_obiektow, text="Usuń", command=remove_users)
button_usun_obiekt.grid(row=2, column=0, pady=5)

# ramka_mapa
map_widget = tkintermapview.TkinterMapView(ramka_mapa, width=1200, height=400, corner_radius=0)
map_widget.grid(row=0, column=0, columnspan=2)
map_widget.set_position(52.23, 21.00)
map_widget.set_zoom(6)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)
update_clinic_dropdown()

root.mainloop()