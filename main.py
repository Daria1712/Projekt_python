from tkinter import *

import tkintermapview

users: list = []


class User:
    def __init__(self, name, surname, location, data_urodzenia, pesel):
        self.name = name
        self.surname = surname
        self.location = location
        self.data_urodzenia = data_urodzenia
        self.pesel = pesel
        self.coordinates = self.get_coordinates()
        self.marker = map_widget.set_marker(self.coordinates[0], self.coordinates[1],
                                            text=f'{self.name} {self.surname}')

    def get_coordinates(self) -> list:
        import requests
        from bs4 import BeautifulSoup
        adres_url: str = f'https://pl.wikipedia.org/wiki/{self.location}'
        response_html = BeautifulSoup(requests.get(adres_url).text, 'html.parser')

        return [
            float(response_html.select('.latitude')[1].text.replace(',', '.')),
            float(response_html.select('.longitude')[1].text.replace(',', '.')),
        ]


def add_user() -> None:
    name = entry_imie.get()
    surname = entry_nazwisko.get()
    location = entry_przychodnia.get()
    data_urodzenia = entry_data_urodzenia.get()
    pesel = entry_pesel.get()

    user = User(name=name, surname=surname, location=location, data_urodzenia=data_urodzenia, pesel=pesel)
    users.append(user)

    print(users)

    entry_imie.delete(0, END)
    entry_nazwisko.delete(0, END)
    entry_przychodnia.delete(0, END)
    entry_data_urodzenia.delete(0, END)
    entry_pesel.delete(0, END)

    entry_imie.focus()
    show_users()


def show_users() -> None:
    listbox_lista_obiektow.delete(0, END)
    for idx, user in enumerate(users):
        listbox_lista_obiektow.insert(idx, f'{idx + 1}. {user.name} {user.surname}')


def remove_users() -> None:
    i = (listbox_lista_obiektow.index(ACTIVE))
    print(i)
    users[i].marker.delete()
    users.pop(i)
    show_users()


def edit_user() -> None:
    i = listbox_lista_obiektow.index(ACTIVE)
    name = users[i].name
    surname = users[i].surname
    location = users[i].location
    data_urodzenia = users[i].data_urodzenia
    pesel = users[i].pesel

    entry_imie.insert(0, name)
    entry_nazwisko.insert(0, surname)
    entry_przychodnia.insert(0, location)
    entry_data_urodzenia.insert(0, data_urodzenia)
    entry_pesel.insert(0, pesel)

    button_dodaj_obiekt.config(text='Zapisz', command=lambda: update_user(i))


def update_user(i):
    name = entry_imie.get()
    surname = entry_nazwisko.get()
    location = entry_przychodnia.get()
    data_urodzenia = entry_data_urodzenia.get()
    pesel = entry_pesel.get()

    users[i].name = name
    users[i].surname = surname
    users[i].location = location
    users[i].data_urodzenia = data_urodzenia
    users[i].pesel = pesel

    users[i].coordinates = users[i].get_coordinates()
    users[i].marker.delete()
    users[i].marker = map_widget.set_marker(users[i].coordinates[0], users[i].coordinates[1],
                                            text=f'{users[i].name} {users[i].surname}')

    show_users()
    button_dodaj_obiekt.config(text='Dodaj', command=add_user)

    entry_imie.delete(0, END)
    entry_nazwisko.delete(0, END)
    entry_przychodnia.delete(0, END)
    entry_data_urodzenia.delete(0, END)
    entry_pesel.delete(0, END)

    entry_imie.focus()


def show_user_details():
    i = (listbox_lista_obiektow.index(ACTIVE))
    label_szczegoly_obiketu_name_wartosc.config(text=users[i].name)
    label_szczegoly_obiketu_surname_wartosc.config(text=users[i].surname)
    label_szczegoly_obiketu_przychodnia_wartosc.config(text=users[i].location)
    label_szczegoly_obiketu_data_urodzenia_wartosc.config(text=users[i].data_urodzenia)
    label_szczegoly_obiketu_pesel.config(text=users[i].pesel)

    map_widget.set_zoom(15)
    map_widget.set_position(users[i].coordinates[0], users[i].coordinates[1])


root = Tk()
root.geometry("1200x700")
root.title("Lista pacjentów")

ramka_lista_obiektow = Frame(root)
ramka_formularz = Frame(root)
ramka_szczegoly_obiektow = Frame(root)
ramka_mapa = Frame(root)

ramka_lista_obiektow.grid(row=0, column=0)
ramka_formularz.grid(row=0, column=1)
ramka_szczegoly_obiektow.grid(row=1, column=0, columnspan=2)
ramka_mapa.grid(row=2, column=0, columnspan=2)

# ramka_lista_obiektow
label_lista_obiektow = Label(ramka_lista_obiektow, text="Lista pacjentów:")
label_lista_obiektow.grid(row=0, column=0)

listbox_lista_obiektow = Listbox(ramka_lista_obiektow, width=50, height=10)
listbox_lista_obiektow.grid(row=1, column=0, columnspan=3)

button_pokaz_szczegoly = Button(ramka_lista_obiektow, text="Pokaż szczegóły", command=show_user_details)
button_pokaz_szczegoly.grid(row=2, column=0)

button_usun_obiekt = Button(ramka_lista_obiektow, text="Usuń", command=remove_users)
button_usun_obiekt.grid(row=2, column=1)

button_edytuj_obiekt = Button(ramka_lista_obiektow, text="Edytuj", command=edit_user)
button_edytuj_obiekt.grid(row=2, column=2)

# ramka_formularz
label_formularz = Label(ramka_formularz, text="Formularz:")
label_formularz.grid(row=0, column=0)

label_imie = Label(ramka_formularz, text="Imię:")
label_imie.grid(row=1, column=0, sticky=W)

label_nazwisko = Label(ramka_formularz, text="Nazwisko:")
label_nazwisko.grid(row=2, column=0, sticky=W)

label_przychodnia = Label(ramka_formularz, text="Przychodnia:")
label_przychodnia.grid(row=3, column=0, sticky=W)

label_data_urodzenia = Label(ramka_formularz, text="Data urodzenia:")
label_data_urodzenia.grid(row=4, column=0, sticky=W)

label_data_urodzenia = Label(ramka_formularz, text="Numer pesel:")
label_data_urodzenia.grid(row=5, column=0, sticky=W)

entry_imie = Entry(ramka_formularz)
entry_imie.grid(row=1, column=1)

entry_nazwisko = Entry(ramka_formularz)
entry_nazwisko.grid(row=2, column=1)

entry_przychodnia = Entry(ramka_formularz)
entry_przychodnia.grid(row=3, column=1)

entry_data_urodzenia = Entry(ramka_formularz)
entry_data_urodzenia.grid(row=4, column=1)

entry_pesel = Entry(ramka_formularz)
entry_pesel.grid(row=5, column=1)

button_dodaj_obiekt = Button(ramka_formularz, text="Dodaj", command=add_user)
button_dodaj_obiekt.grid(row=6, column=0, columnspan=2)

# ramka_szczegoly_obiektow
label_pokaz_szczegoly = Label(ramka_szczegoly_obiektow, text="Szczegóły pacjenta:")
label_pokaz_szczegoly.grid(row=0, column=0)

label_szczegoly_obiketu_name = Label(ramka_szczegoly_obiektow, text="Imię:")
label_szczegoly_obiketu_name.grid(row=1, column=0)

label_szczegoly_obiketu_name_wartosc = Label(ramka_szczegoly_obiektow, text="....")
label_szczegoly_obiketu_name_wartosc.grid(row=1, column=1)

label_szczegoly_obiketu_surname = Label(ramka_szczegoly_obiektow, text="Nazwisko:")
label_szczegoly_obiketu_surname.grid(row=1, column=2)

label_szczegoly_obiketu_surname_wartosc = Label(ramka_szczegoly_obiektow, text="....")
label_szczegoly_obiketu_surname_wartosc.grid(row=1, column=3)

label_szczegoly_obiketu_przychodnia = Label(ramka_szczegoly_obiektow, text="Przychodnia:")
label_szczegoly_obiketu_przychodnia.grid(row=1, column=4)

label_szczegoly_obiketu_przychodnia_wartosc = Label(ramka_szczegoly_obiektow, text="....")
label_szczegoly_obiketu_przychodnia_wartosc.grid(row=1, column=5)

label_szczegoly_obiketu_data_urodzenia = Label(ramka_szczegoly_obiektow, text="Data urodzenia:")
label_szczegoly_obiketu_data_urodzenia.grid(row=2, column=0)

label_szczegoly_obiketu_data_urodzenia_wartosc = Label(ramka_szczegoly_obiektow, text="....")
label_szczegoly_obiketu_data_urodzenia_wartosc.grid(row=2, column=1)

label_szczegoly_obiketu_pesel = Label(ramka_szczegoly_obiektow, text="Numer pesel:")
label_szczegoly_obiketu_pesel.grid(row=2, column=2)

label_szczegoly_obiketu_pesel_wartosc = Label(ramka_szczegoly_obiektow, text="....")
label_szczegoly_obiketu_pesel_wartosc.grid(row=2, column=3)

# ramka_mapa
map_widget = tkintermapview.TkinterMapView(ramka_mapa, width=1200, height=400, corner_radius=0)
map_widget.grid(row=0, column=0, columnspan=2)
map_widget.set_position(52.23, 21.00)
map_widget.set_zoom(6)

root.mainloop()

