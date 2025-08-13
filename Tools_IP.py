import requests
import ipaddress
import tkinter as tk
from tkinter import ttk, messagebox
import socket
import subprocess
import platform
import threading
from PIL import Image, ImageTk
import os

URL = "http://ip-api.com/json/"

# Fonction pour charger une image emoji
def charger_emoji(nom_fichier, size=(24, 24)):
    dossier_projet = os.path.dirname(__file__)  # ← reste dans le dossier du script
    chemin = os.path.join(dossier_projet, "emojis", nom_fichier)
    img = Image.open(chemin).resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)

def ping_process(domain):
    try:
        ip = socket.gethostbyname(domain)
        ip_result.set(ip)
        console_output.delete("1.0", tk.END)
        console_output.insert(tk.END, f"Résolution DNS : {domain} → {ip}\n")
    except socket.gaierror:
        messagebox.showerror("Erreur DNS", "Impossible de résoudre le nom de domaine.")
        return

    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        console_output.insert(tk.END, f"Test de ping vers {domain}...\n")
        result = subprocess.run(["ping", param, "4", domain], capture_output=True, text=True)
        console_output.insert(tk.END, result.stdout + "\n")
    except subprocess.CalledProcessError as e:
        console_output.insert(tk.END, f"Le ping a échoué : {e}\n")

def ping_domain():
    domain = domain_entry.get().strip()
    if not domain:
        messagebox.showerror("Erreur", "Veuillez entrer un nom de domaine.")
        return
    threading.Thread(target=ping_process, args=(domain,), daemon=True).start()

def localiser():
    ip = ip_entry.get().strip()

    try:
        ipaddress.ip_address(ip)
    except ValueError:
        messagebox.showerror("Format invalide", "L'adresse IP saisie est invalide.")
        return

    try:
        réponse = requests.get(URL + ip).json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur réseau", f"Une erreur réseau est survenue :\n{e}")
        return

    if réponse.get("status") == "success":
        afficher_resultat_avec_images(réponse)
    else:
        messagebox.showwarning("Localisation échouée", "Impossible de localiser cette adresse IP.")

def afficher_resultat_avec_images(réponse):
    for widget in geo_result_frame.winfo_children():
        widget.destroy()

    infos = [
        (emoji_search, f"Adresse IP : {réponse['query']}"),
        (emoji_globe, f"Pays : {réponse['country']}"),
        (emoji_city, f"Ville : {réponse['city']}"),
        (emoji_zip, f"Code postal : {réponse['zip']}"),
        (emoji_lat, f"Latitude : {réponse['lat']}"),
        (emoji_lon, f"Longitude : {réponse['lon']}"),
        (emoji_clock, f"Fuseau horaire : {réponse['timezone']}"),
        (emoji_isp, f"Fournisseur : {réponse['isp']}"),
    ]

    for img, txt in infos:
        lbl = tk.Label(geo_result_frame, image=img, text=txt, compound="left", font=("Segoe UI", 12), anchor="w", bg="#f0f0f0", padx=5)
        lbl.image = img
        lbl.pack(fill="x", padx=5, pady=2)

# Fenêtre principale
fenetre = tk.Tk()
fenetre.title("🌐 LocalisatorIP — Analyse & Géolocalisation d'Adresse IP")
fenetre.geometry("1100x700")
fenetre.resizable(False, False)

# Charger les emojis après la création de la fenêtre
emoji_search = charger_emoji("search.png")
emoji_globe = charger_emoji("globe.png")
emoji_city = charger_emoji("city.png")
emoji_zip = charger_emoji("zip.png")
emoji_lat = charger_emoji("lat.png")
emoji_lon = charger_emoji("lon.png")
emoji_clock = charger_emoji("clock.png")
emoji_isp = charger_emoji("isp.png")

style = ttk.Style()
style.configure("TLabel", font=("Segoe UI", 12))
style.configure("TButton", font=("Segoe UI", 12))

main_frame = ttk.Frame(fenetre, padding=10)
main_frame.pack(fill="both", expand=True)

ping_frame = ttk.LabelFrame(main_frame, text="Test de Ping", padding=15)
ping_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

geo_frame = ttk.LabelFrame(main_frame, text="Géolocalisation IP", padding=15)
geo_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)

# Volet Ping
ttk.Label(ping_frame, text="Nom de domaine :").pack(anchor="w", pady=(0, 5))
domain_entry = ttk.Entry(ping_frame, width=45, font=("Segoe UI", 12))
domain_entry.pack(anchor="w", pady=(0, 10))

ttk.Button(ping_frame, text="Ping", command=ping_domain).pack(anchor="center", pady=(0, 10))

ttk.Label(ping_frame, text="Domaine --> IP:").pack(anchor="w", pady=(10, 5))
ip_result = tk.StringVar()
ttk.Label(ping_frame, textvariable=ip_result, background="#f0f0f0", padding=5, relief="solid", font=("Segoe UI", 12)).pack(anchor="w", fill="x")

ttk.Button(ping_frame, text="Utiliser cette IP", command=lambda: ip_entry.delete(0, tk.END) or ip_entry.insert(0, ip_result.get())).pack(anchor="center", pady=(10, 10))

ttk.Label(ping_frame, text="Console Ping :").pack(anchor="w", pady=(15, 5))
console_output = tk.Text(ping_frame, height=15, width=65, font=("Consolas", 11), background="#1e1e1e", foreground="#d4d4d4")
console_output.pack(fill="both", expand=True)

# Volet Géolocalisation
ttk.Label(geo_frame, text="Adresse IP à localiser :").pack(anchor="w", pady=(0, 5))
ip_entry = ttk.Entry(geo_frame, width=45, font=("Segoe UI", 12))
ip_entry.pack(anchor="w", pady=(0, 10))

ttk.Button(geo_frame, text="Localiser", command=localiser).pack(anchor="center", pady=(0, 15))

geo_result_frame = tk.Frame(geo_frame, bg="#f0f0f0", bd=1, relief="solid")
geo_result_frame.pack(fill="both", expand=True, padx=5, pady=5)

# Label de remerciement en bas
footer_label = tk.Label(
    fenetre,
    text="By ƊąɾҟȺɾҽ̀ʂ",
    font=("Segoe UI", 11, "italic"),
    bg="#e0e0e0",
    fg="#333333",
    pady=10
)
footer_label.pack(side="bottom", fill="x")

fenetre.mainloop()
