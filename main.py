from tkinter import *
from tkinter import messagebox
import tkintermapview
import requests
from bs4 import BeautifulSoup

users: list = []
clinics: list = []


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
                messagebox.showwarning("Ostrzeżenie",
                                       f"Nie znaleziono współrzędnych dla {self.location}. Użyto domyślnych współrzędnych.")
                return [52.23, 21.00]
            latitude = float(latitude_elements[1].text.replace(',', '.'))
            longitude = float(longitude_elements[1].text.replace(',', '.'))
            return [latitude, longitude]
        except (requests.RequestException, ValueError, IndexError) as e:
            messagebox.showwarning("Ostrzeżenie",
                                   f"Nie udało się pobrać współrzędnych dla {self.location}: {e}. Użyto domyślnych współrzędnych.")
            return [52.23, 21.00]


class User:
    def __init__(self, name, surname, location, data_urodzenia, pesel, clinic_name=None):
        self.name = name
        self.surname = surname
        self.location = location
        self.data_urodzenia = data_urodzenia
        self.pesel = pesel
        self.clinic_name = clinic_name
        self.coordinates = self.get_coordinates()
        self.marker = map_widget.set_marker(self.coordinates[0], self.coordinates[1],
                                            text=f'{self.name} {self.surname}')

    def get_coordinates(self) -> list:
        try:
            adres_url: str = f'https://pl.wikipedia.org/wiki/{self.location}'
            response = requests.get(adres_url)
            response.raise_for_status()
            response_html = BeautifulSoup(response.text, 'html.parser')
            latitude_elements = response_html.select('.latitude')
            longitude_elements = response_html.select('.longitude')
            if len(latitude_elements) < 2 or len(longitude_elements) < 2:
                messagebox.showwarning("Ostrzeżenie",
                                       f"Nie znaleziono współrzędnych dla {self.location}. Użyto domyślnych współrzędnych.")
                return [52.23, 21.00]
            latitude = float(latitude_elements[1].text.replace(',', '.'))
            longitude = float(longitude_elements[1].text.replace(',', '.'))
            return [latitude, longitude]
        except (requests.RequestException, ValueError, IndexError) as e:
            messagebox.showwarning("Ostrzeżenie",
                                   f"Nie udało się pobrać współrzędnych dla {self.location}: {e}. Użyto domyślnych współrzędnych.")
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
    if any(user.clinic_name == clinics[i].name for user in users):
        messagebox.showerror("Błąd", "Nie można usunąć przychodni, która ma przypisanych pacjentów!")
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
        for user in users:
            if user.clinic_name == clinics[i].name:
                user.clinic_name = name
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

ramka_lista_obiektow = Frame(scrollable_frame, padx=10, pady=10)
ramka_clinics = Frame(scrollable_frame, padx=10, pady=10)
ramka_mapa = Frame(scrollable_frame, padx=10, pady=10)

ramka_clinics.grid(row=0, column=0, sticky="nsew")
ramka_lista_obiektow.grid(row=0, column=1, sticky="nsew")
ramka_mapa.grid(row=1, column=0, columnspan=2, sticky="nsew")

scrollable_frame.grid_rowconfigure(0, weight=1)
scrollable_frame.grid_rowconfigure(1, weight=1)
scrollable_frame.grid_columnconfigure(0, weight=1)
scrollable_frame.grid_columnconfigure(1, weight=1)

# ramka_clinics
label_clinics = Label(ramka_clinics, text="Zarządzanie przychodniami:", font=("Arial", 14, "bold"))
label_clinics.grid(row=0, column=0, columnspan=2, pady=5)

label_clinic_form = Label(ramka_clinics, text="Dodaj przychodnię:", font=("Arial", 11, "bold"))
label_clinic_form.grid(row=1, column=0, columnspan=2, sticky=W)

label_clinic_name = Label(ramka_clinics, text="Nazwa:")
label_clinic_name.grid(row=2, column=0, sticky=W)

label_clinic_location = Label(ramka_clinics, text="Lokalizacja:")
label_clinic_location.grid(row=3, column=0, sticky=W)

entry_clinic_name = Entry(ramka_clinics, width=30)
entry_clinic_name.grid(row=2, column=1)

entry_clinic_location = Entry(ramka_clinics, width=30)
entry_clinic_location.grid(row=3, column=1)

button_add_clinic = Button(ramka_clinics, text="Dodaj przychodnię", command=add_clinic)
button_add_clinic.grid(row=4, column=0, columnspan=2, pady=5)

label_clinics_list = Label(ramka_clinics, text="Lista przychodni:", font=("Arial", 11, "bold"))
label_clinics_list.grid(row=5, column=0, columnspan=2, sticky=W)

listbox_clinics = Listbox(ramka_clinics, width=50, height=10)
listbox_clinics.grid(row=6, column=0, columnspan=2)

button_clinic_map_all = Button(ramka_clinics, text="Generuj mapę wszystkich placówek", command=generate_map_of_clinics)
button_clinic_map_all.grid(row=7, column=0, pady=5)

button_remove_clinic = Button(ramka_clinics, text="Usuń", command=remove_clinic)
button_remove_clinic.grid(row=7, column=1, pady=5)

button_edit_clinic = Button(ramka_clinics, text="Edytuj", command=edit_clinic)
button_edit_clinic.grid(row=8, column=0, columnspan=2, pady=5)

# ramka_lista_obiektow
label_lista_obiektow = Label(ramka_lista_obiektow, text="Lista pacjentów:", font=("Arial", 14, "bold"))
label_lista_obiektow.grid(row=0, column=0, columnspan=2)

listbox_lista_obiektow = Listbox(ramka_lista_obiektow, width=50, height=10)
listbox_lista_obiektow.grid(row=1, column=0, columnspan=2)

button_usun_obiekt = Button(ramka_lista_obiektow, text="Usuń", command=remove_users)
button_usun_obiekt.grid(row=2, column=0, pady=5)

clinic_var = StringVar()
clinic_menu = OptionMenu(ramka_lista_obiektow, clinic_var, "")
clinic_menu.grid(row=3, column=0, columnspan=2, pady=5)

# ramka_mapa
map_widget = tkintermapview.TkinterMapView(ramka_mapa, width=1200, height=400, corner_radius=0)
map_widget.grid(row=0, column=0, columnspan=2)
map_widget.set_position(52.23, 21.00)
map_widget.set_zoom(6)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


def _on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


canvas.bind_all("<MouseWheel>", _on_mousewheel)
update_clinic_dropdown()

root.mainloop()
