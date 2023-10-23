import pickle

# Apri il file Pickle in modalità lettura binaria ('rb')
with open('user_sessions.pkl', 'rb') as file:
    # Carica il contenuto del file Pickle in un oggetto Python
    profilo = pickle.load(file)

# Sostituisci 'numero_profilo' con l'indice dell'elemento che desideri visualizzare
numero_profilo = 0  # Cambia l'indice secondo le tue esigenze

# Accedi al dizionario all'interno dell'elemento desiderato
profilo_selezionato = profilo[numero_profilo]

# Visualizza il contenuto del dizionario
print(profilo_selezionato)
