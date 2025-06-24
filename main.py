from tkinter import *
from tkinter import messagebox
import tkintermapview
import requests
from bs4 import BeautifulSoup


def get_coordinates(location: str) -> list:
    adres_url: str = f'https://pl.wikipedia.org/wiki/{location}'
    response_html = BeautifulSoup(requests.get(adres_url).text, 'html.parser')

    return [
        float(response_html.select('.latitude')[1].text.replace(',', '.')),
        float(response_html.select('.longitude')[1].text.replace(',', '.')),
    ]


class Clinic:
    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.coordinates = get_coordinates(location)


class Doctor:
    def __init__(self, name, surname, location, clinic_id):
        self.name = name
        self.surname = surname
        self.location = location
        self.coordinates = get_coordinates(location)
        self.clinic_id = clinic_id

    def get_doctor_id(self):
        return f'{self.name} {self.surname} {self.location} {self.clinic_id}'


class User:
    def __init__(self, name, surname, location, data_urodzenia, pesel, doctor_id=None):
        self.name = name
        self.surname = surname
        self.data_urodzenia = data_urodzenia
        self.pesel = pesel
        self.location = location
        self.doctor_id = doctor_id
        self.coordinates = get_coordinates(location)

    def get_user_id(self):
        return self.pesel


clinics = []
patients = []
doctors = []


def add_clinic():
    name = entry_clinic_name.get()
    location = entry_clinic_location.get()

    if not all([name, location]):
        messagebox.showerror("Błąd", "Nazwa i lokalizacja przychodni muszą być wypełnione!")
        return

    if any(clinic.name == name for clinic in clinics):
        messagebox.showerror("Błąd", "Przychodnia o tej nazwie już istnieje!")
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

    if clinics[i].name != name:
        for doctor in doctors:
            if doctor.clinic_id == clinics[i].id:
                doctor.clinic_id = clinics[i].name

    clinics[i].name = name
    clinics[i].location = location
    clinics[i].coordinates = get_coordinates(location)
    show_clinics()
    update_clinic_dropdown()
    button_add_clinic.config(text='Dodaj przychodnię', command=add_clinic)
    entry_clinic_name.delete(0, END)
    entry_clinic_location.delete(0, END)
    entry_clinic_location.delete(0, END)
    entry_clinic_location.delete(0, END)


def generate_map_of_clinics():
    map_widget.delete_all_marker()

    for clinic in clinics:
        map_widget.set_marker(clinic.coordinates[0], clinic.coordinates[1], text=clinic.name)


def employee_localization_handler():
    if not listbox_clinics.curselection():
        messagebox.showerror("Błąd", "Wybierz przychodnię, aby zobaczyć szczegóły!")
        return
    i = listbox_clinics.index(ACTIVE)
    clinic_id = clinics[i].name
    map_widget.delete_all_marker()
    doctors_in_clinic = [doctor for doctor in doctors if doctor.clinic_id == clinic_id]

    for doctor in doctors_in_clinic:
        map_widget.set_marker(doctor.coordinates[0], doctor.coordinates[1], text=doctor.name + ' ' + doctor.surname)


def add_doctor():
    name = entry_doctor_name.get().strip()
    surname = entry_doctor_surname.get().strip()
    location = entry_doctor_location.get().strip()
    clinic_id = clinic_var.get() if clinic_var.get() else None

    if not all([location, name, surname, clinic_id]):
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
    doctor_patients = [patient for patient in patients if patient.doctor_id == doctors[i].get_doctor_id()]
    if len(doctor_patients) != 0:
        messagebox.showerror("Błąd", "Nie można usunąć lekarza, który ma przypisanych pacjentów!")
        return
    doctors.pop(i)
    show_doctors()
    show_doctor_patients()
    update_doctor_dropdown()


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

    if not all([name, surname, clinic_id]):
        messagebox.showerror("Błąd", "Wszystkie pola lekarza muszą być wypełnione!")
        return

    new_doctor = Doctor(name, surname, location, clinic_id)

    if new_doctor.get_doctor_id() != doctors[i].get_doctor_id():
        for patient in patients:
            if patient.doctor_id == doctors[i].get_doctor_id():
                patient.doctor_id = new_doctor.get_doctor_id()

    doctors[i] = new_doctor
    show_doctors()
    update_doctor_dropdown()
    button_add_doctor.config(text='Dodaj lekarza', command=add_doctor)
    entry_doctor_name.delete(0, END)
    entry_doctor_surname.delete(0, END)
    entry_doctor_location.delete(0, END)
    clinic_var.set("")


def show_doctor_patients():
    if not doctors or not listbox_doctors.curselection():
        listbox_doctor_patients.delete(0, END)
        return
    i = listbox_doctors.index(ACTIVE)
    listbox_doctor_patients.delete(0, END)
    doctor = doctors[i]
    doctor_patients = [patient for patient in patients if patient.doctor_id == doctor.get_doctor_id()]

    for idx, patient in enumerate(doctor_patients):
        listbox_doctor_patients.insert(idx, f'{idx + 1}. {patient.name} {patient.surname}')

    map_widget.delete_all_marker()
    for patient in (doctor_patients):
        map_widget.set_marker(patient.coordinates[0], patient.coordinates[1], text=patient.name + ' ' + patient.surname)


def add_user():
    name = entry_imie.get().strip()
    surname = entry_nazwisko.get().strip()
    data_urodzenia = entry_data_urodzenia.get().strip()
    pesel = entry_pesel.get().strip()
    location = entry_patient_location.get()
    doctor_id = doctor_patient_var.get() if doctor_patient_var.get() else None

    if not all([name, surname, location, data_urodzenia, pesel]):
        messagebox.showerror("Błąd", "Wszystkie pola muszą być wypełnione!")
        return

    if any(patient.pesel == pesel for patient in patients):
        messagebox.showerror("Błąd", "Pacjent z tym numerem PESEL już istnieje!")
        return

    user = User(name=name, surname=surname,
                data_urodzenia=data_urodzenia, pesel=pesel, doctor_id=doctor_id, location=location)
    patients.append(user)

    entry_imie.delete(0, END)
    entry_nazwisko.delete(0, END)
    entry_patient_location.delete(0, END)
    entry_data_urodzenia.delete(0, END)
    entry_patient_location.delete(0, END)
    entry_pesel.delete(0, END)
    clinic_patient_var.set("")
    doctor_patient_var.set("")

    show_users()


def show_users():
    listbox_lista_obiektow.delete(0, END)
    for idx, user in enumerate(patients):
        listbox_lista_obiektow.insert(idx, f'{idx + 1}. {user.name} {user.surname}')


def remove_user():
    if not listbox_lista_obiektow.curselection():
        messagebox.showerror("Błąd", "Wybierz pacjenta do usunięcia!")
        return
    i = listbox_lista_obiektow.index(ACTIVE)
    patients.pop(i)
    show_users()
    show_doctor_patients()


def edit_user():
    if not listbox_lista_obiektow.curselection():
        messagebox.showerror("Błąd", "Wybierz pacjenta do edycji!")
        return

    i = listbox_lista_obiektow.index(ACTIVE)
    name = patients[i].name
    surname = patients[i].surname
    location = patients[i].location
    data_urodzenia = patients[i].data_urodzenia
    pesel = patients[i].pesel
    doctor_id = patients[i].doctor_id
    clinic_id = [doctor.clinic_id for doctor in doctors if doctor.get_doctor_id() == doctor_id][0]

    entry_imie.insert(0, name)
    entry_nazwisko.insert(0, surname)
    entry_patient_location.insert(0, location)
    entry_data_urodzenia.insert(0, data_urodzenia)
    entry_pesel.insert(0, pesel)
    doctor_patient_var.set(doctor_id if doctor_id else "")
    clinic_patient_var.set(clinic_id if clinic_id else "")

    button_dodaj_obiekt.config(text='Zapisz', command=lambda: update_user(i))


def update_user(i):
    name = entry_imie.get().strip()
    surname = entry_nazwisko.get().strip()
    location = entry_patient_location.get()
    data_urodzenia = entry_data_urodzenia.get().strip()
    pesel = entry_pesel.get().strip()
    doctor_id = doctor_patient_var.get() if doctor_patient_var.get() else None

    if not all([name, surname, location, data_urodzenia, pesel]):
        messagebox.showerror("Błąd", "Wszystkie pola muszą być wypełnione!")
        return

    if any(user.pesel == pesel and user is not patients[i] for user in patients):
        messagebox.showerror("Błąd", "Pacjent z tym numerem PESEL już istnieje!")
        return

    new_patient = User(name, surname, location, data_urodzenia, pesel, doctor_id)
    patients[i] = new_patient

    show_users()
    show_doctor_patients()
    button_dodaj_obiekt.config(text='Dodaj', command=add_user)

    entry_imie.delete(0, END)
    entry_nazwisko.delete(0, END)
    entry_patient_location.delete(0, END)
    entry_data_urodzenia.delete(0, END)
    entry_pesel.delete(0, END)
    clinic_patient_var.set("")
    doctor_patient_var.set("")


def update_doctor_dropdown():
    doctor_patient_menu['menu'].delete(0, 'end')

    for doctor in doctors:
        doctor_full_name = f"{doctor.name} {doctor.surname}"
        doctor_patient_menu['menu'].add_command(
            label=doctor_full_name,
            command=lambda d_id=doctor.get_doctor_id(): doctor_patient_var.set(d_id)
        )


def update_clinic_dropdown():
    clinic_menu['menu'].delete(0, 'end')
    clinic_patient_menu['menu'].delete(0, 'end')

    for clinic in clinics:
        clinic_patient_menu['menu'].add_command(label=clinic.name,
                                                command=lambda c=clinic.name: clinic_patient_var.set(c))
        clinic_menu['menu'].add_command(label=clinic.name, command=lambda c=clinic.name: clinic_var.set(c))


def on_clinic_patient_change():
    clinic_id = clinic_patient_var.get()
    selected_doctors_from_clinic = [doctor for doctor in doctors if doctor.clinic_id == clinic_id]
    doctor_patient_menu['menu'].delete(0, 'end')

    for selected_doctor in selected_doctors_from_clinic:
        doctor_patient_menu['menu'].add_command(label=selected_doctor.get_doctor_id(),
                                                command=lambda
                                                    c=selected_doctor.get_doctor_id(): doctor_patient_var.set(c))


root = Tk()
root.geometry("1600x1000")  # Larger window
root.title("Zarządzanie Przychodnią")
root.state('zoomed')  # Maximize window

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

ramka_szczegoly_obiektow = Frame(scrollable_frame, padx=15, pady=15, relief="ridge", bd=2)
ramka_clinics = Frame(scrollable_frame, padx=15, pady=15, relief="ridge", bd=2)
ramka_patients = Frame(scrollable_frame, padx=15, pady=15, relief="ridge", bd=2)
ramka_doctors = Frame(scrollable_frame, padx=15, pady=15, relief="ridge", bd=2)
ramka_map = Frame(scrollable_frame, padx=15, pady=15, relief="ridge", bd=2)

ramka_szczegoly_obiektow.grid(row=0, column=0, columnspan=3, padx=8, pady=8, sticky="nsew")
ramka_clinics.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")
ramka_doctors.grid(row=1, column=1, padx=8, pady=8, sticky="nsew")
ramka_map.grid(row=1, column=2, padx=8, pady=8, sticky="nsew")
ramka_patients.grid(row=2, column=0, columnspan=2, padx=8, pady=8, sticky="nsew")

scrollable_frame.grid_rowconfigure(0, weight=1)  # Top - details
scrollable_frame.grid_rowconfigure(1, weight=2)  # Middle - clinics, doctors, map
scrollable_frame.grid_rowconfigure(2, weight=3)  # Bottom - patients (wide)
scrollable_frame.grid_columnconfigure(0, weight=1)  # Left column - 33%
scrollable_frame.grid_columnconfigure(1, weight=1)  # Middle column - 33%
scrollable_frame.grid_columnconfigure(2, weight=1)  # Right column - 33%

for i in range(6):
    ramka_szczegoly_obiektow.grid_columnconfigure(i, weight=1)

label_clinics = Label(ramka_clinics, text="Zarządzanie przychodniami:", font=("Arial", 14, "bold"))
label_clinics.grid(row=0, column=0, columnspan=3, pady=(0, 15))

label_clinic_form = Label(ramka_clinics, text="Dodaj przychodnię:", font=("Arial", 11, "bold"))
label_clinic_form.grid(row=1, column=0, columnspan=2, sticky=W, pady=(0, 5))

label_clinic_name = Label(ramka_clinics, text="Nazwa:")
label_clinic_name.grid(row=2, column=0, sticky=W, pady=5)

label_clinic_location = Label(ramka_clinics, text="Lokalizacja:")
label_clinic_location.grid(row=3, column=0, sticky=W, pady=5)

entry_clinic_name = Entry(ramka_clinics, width=40, font=("Arial", 10))
entry_clinic_name.grid(row=2, column=1, pady=5, sticky="ew", padx=(10, 0))

entry_clinic_location = Entry(ramka_clinics, width=40, font=("Arial", 10))
entry_clinic_location.grid(row=3, column=1, pady=5, sticky="ew", padx=(10, 0))

button_add_clinic = Button(ramka_clinics, text="Dodaj przychodnię", command=add_clinic,
                           font=("Arial", 10), bg="#4CAF50", fg="white")
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

button_clinic_map_all = Button(button_frame_clinics, text="Generuj mapę wszystkich placówek",
                               command=generate_map_of_clinics,
                               font=("Arial", 9), bg="#2196F3", fg="white")
button_clinic_map_all.pack(side=LEFT, padx=5)

button_clinic_map_employees = Button(button_frame_clinics, text="Mapa lokalizacji pracowników placówki",
                                     command=employee_localization_handler,
                                     font=("Arial", 9), bg="#2196F3", fg="white")
button_clinic_map_employees.pack(side=LEFT, padx=5)

button_remove_clinic = Button(button_frame_clinics, text="Usuń", command=remove_clinic,
                              font=("Arial", 9), bg="#f44336", fg="white")
button_remove_clinic.pack(side=LEFT, padx=5)

button_edit_clinic = Button(button_frame_clinics, text="Edytuj", command=edit_clinic,
                            font=("Arial", 9), bg="#FF9800", fg="white")
button_edit_clinic.pack(side=LEFT, padx=5)

ramka_clinics.grid_columnconfigure(1, weight=1)
ramka_clinics.grid_rowconfigure(6, weight=1)

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

button_add_doctor = Button(ramka_doctors, text="Dodaj lekarza", command=add_doctor,
                           font=("Arial", 10), bg="#4CAF50", fg="white")
button_add_doctor.grid(row=6, column=0, columnspan=2, pady=10)

label_doctors_list = Label(ramka_doctors, text="Lista lekarzy:", font=("Arial", 11, "bold"))
label_doctors_list.grid(row=7, column=0, columnspan=2, pady=(10, 5), sticky="w")

doctor_frame = Frame(ramka_doctors)
doctor_frame.grid(row=7, column=0, columnspan=3, pady=5, sticky="nsew")

listbox_doctors = Listbox(doctor_frame, width=50, height=6, font=("Arial", 9))
doctor_scrollbar = Scrollbar(doctor_frame, orient="vertical")
listbox_doctors.config(yscrollcommand=doctor_scrollbar.set)
doctor_scrollbar.config(command=listbox_doctors.yview)
listbox_doctors.bind('<<ListboxSelect>>', lambda event: show_doctor_patients())

listbox_doctors.pack(side=LEFT, fill=BOTH, expand=True)
doctor_scrollbar.pack(side=RIGHT, fill=Y)

button_frame_doctors = Frame(ramka_doctors)
button_frame_doctors.grid(row=8, column=0, columnspan=3, pady=10)

button_remove_doctor = Button(button_frame_doctors, text="Usuń", command=remove_doctor,
                              font=("Arial", 9), bg="#f44336", fg="white")
button_remove_doctor.pack(side=LEFT, padx=5)

button_edit_doctor = Button(button_frame_doctors, text="Edytuj", command=edit_doctor,
                            font=("Arial", 9), bg="#FF9800", fg="white")
button_edit_doctor.pack(side=LEFT, padx=5)

ramka_doctors.grid_columnconfigure(1, weight=1)
ramka_doctors.grid_rowconfigure(7, weight=1)

label_patients = Label(ramka_patients, text="Zarządzanie pacjentami:", font=("Arial", 14, "bold"))
label_patients.grid(row=0, column=0, columnspan=6, pady=(0, 15))

label_patient_form = Label(ramka_patients, text="Dodaj pacjenta:", font=("Arial", 11, "bold"))
label_patient_form.grid(row=1, column=0, columnspan=6, sticky=W, pady=(0, 10))

label_imie = Label(ramka_patients, text="Imię:")
label_imie.grid(row=2, column=0, sticky=W, pady=3, padx=(0, 5))

entry_imie = Entry(ramka_patients, width=25, font=("Arial", 10))
entry_imie.grid(row=2, column=1, pady=3, sticky="ew", padx=(0, 15))

label_nazwisko = Label(ramka_patients, text="Nazwisko:")
label_nazwisko.grid(row=3, column=0, sticky=W, pady=3, padx=(0, 5))

entry_nazwisko = Entry(ramka_patients, width=25, font=("Arial", 10))
entry_nazwisko.grid(row=3, column=1, pady=3, sticky="ew", padx=(0, 15))

label_przychodnia = Label(ramka_patients, text="Przychodnia:")
label_przychodnia.grid(row=4, column=0, sticky=W, pady=3, padx=(0, 5))

clinic_patient_var = StringVar()
clinic_patient_var.set("")
clinic_patient_var.trace("w", on_clinic_patient_change)
clinic_patient_menu = OptionMenu(ramka_patients, clinic_patient_var, "")
clinic_patient_menu.grid(row=4, column=1, pady=3, sticky="ew", padx=(0, 15))

label_data_urodzenia = Label(ramka_patients, text="Data urodzenia:")
label_data_urodzenia.grid(row=2, column=2, sticky=W, pady=3, padx=(15, 5))

entry_data_urodzenia = Entry(ramka_patients, width=25, font=("Arial", 10))
entry_data_urodzenia.grid(row=2, column=3, pady=3, sticky="ew", padx=(0, 15))

label_pesel = Label(ramka_patients, text="Numer PESEL:")
label_pesel.grid(row=3, column=2, sticky="w", pady=3, padx=(15, 5))

entry_pesel = Entry(ramka_patients, width=25, font=("Arial", 10))
entry_pesel.grid(row=3, column=3, pady=3, sticky="ew", padx=(0, 15))

entry_patient_location_label = Label(ramka_patients, text="Lokalizacja:")
entry_patient_location_label.grid(row=3, column=4, sticky="w", pady=3, padx=(15, 5))

entry_patient_location = Entry(ramka_patients, width=25, font=("Arial", 10))
entry_patient_location.grid(row=3, column=5, pady=3, sticky="ew", padx=(0, 15))

label_doctor = Label(ramka_patients, text="Lekarz:")
label_doctor.grid(row=4, column=2, sticky=W, pady=3, padx=(15, 5))

doctor_patient_var = StringVar()
doctor_patient_menu = OptionMenu(ramka_patients, doctor_patient_var, "")
doctor_patient_menu.grid(row=4, column=3, pady=3, sticky="ew", padx=(0, 15))

button_dodaj_obiekt = Button(ramka_patients, text="Dodaj pacjenta", command=add_user,
                             font=("Arial", 11), bg="#4CAF50", fg="white", width=20)
button_dodaj_obiekt.grid(row=5, column=0, columnspan=6, pady=15)

label_lista_obiektow = Label(ramka_patients, text="Lista pacjentów:", font=("Arial", 11, "bold"))
label_lista_obiektow.grid(row=6, column=0, columnspan=6, sticky=W, pady=(10, 5))

patient_frame = Frame(ramka_patients)
patient_frame.grid(row=7, column=0, columnspan=6, pady=5, sticky="nsew")

listbox_lista_obiektow = Listbox(patient_frame, width=80, height=10, font=("Arial", 9))
patient_scrollbar = Scrollbar(patient_frame, orient="vertical")
listbox_lista_obiektow.config(yscrollcommand=patient_scrollbar.set)
patient_scrollbar.config(command=listbox_lista_obiektow.yview)

listbox_lista_obiektow.pack(side=LEFT, fill=BOTH, expand=True)
patient_scrollbar.pack(side=RIGHT, fill=Y)

button_frame_patients = Frame(ramka_patients)
button_frame_patients.grid(row=8, column=0, columnspan=6, pady=10)

button_usun_obiekt = Button(button_frame_patients, text="Usuń", command=remove_user,
                            font=("Arial", 10), bg="#f44336", fg="white", width=10)
button_usun_obiekt.pack(side=LEFT, padx=8)

button_edytuj_obiekt = Button(button_frame_patients, text="Edytuj", command=edit_user,
                              font=("Arial", 10), bg="#FF9800", fg="white", width=10)
button_edytuj_obiekt.pack(side=LEFT, padx=8)

ramka_patients.grid_columnconfigure(1, weight=1)
ramka_patients.grid_columnconfigure(3, weight=1)
ramka_patients.grid_rowconfigure(7, weight=1)

label_map = Label(ramka_map, text="Mapa:", font=("Arial", 14, "bold"))
label_map.pack(pady=(0, 10))

map_widget = tkintermapview.TkinterMapView(ramka_map, width=500, height=400, corner_radius=5)
map_widget.pack(expand=True, fill=BOTH, padx=5, pady=5)
map_widget.set_position(52.0, 19.5)
map_widget.set_zoom(6)

separator_frame = Frame(ramka_map, height=2, bg="gray")
separator_frame.pack(fill=X, padx=10, pady=10)

stats_frame = Frame(ramka_map)
stats_frame.pack(fill=X, padx=10, pady=5)

label_doctor_patients = Label(ramka_map, text="Pacjenci wybranego lekarza:", font=("Arial", 11, "bold"))
label_doctor_patients.pack(anchor=W, padx=10)

doctor_patients_frame = Frame(ramka_map)
doctor_patients_frame.pack(fill=BOTH, expand=True, padx=10, pady=(5, 10))

listbox_doctor_patients = Listbox(doctor_patients_frame, width=45, height=6, font=("Arial", 9))
doctor_patients_scrollbar = Scrollbar(doctor_patients_frame, orient="vertical")
listbox_doctor_patients.config(yscrollcommand=doctor_patients_scrollbar.set)
doctor_patients_scrollbar.config(command=listbox_doctor_patients.yview)

listbox_doctor_patients.pack(side=LEFT, fill=BOTH, expand=True)
doctor_patients_scrollbar.pack(side=RIGHT, fill=Y)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


def _on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


canvas.bind_all("<MouseWheel>", _on_mousewheel)

update_clinic_dropdown()
update_doctor_dropdown()

root.mainloop()
