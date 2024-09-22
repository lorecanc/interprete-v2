# Usa un'immagine base di Python
FROM python:3.12-slim

# Imposta la directory di lavoro nel container
WORKDIR /app

# Copia i file requirements.txt nella directory di lavoro
COPY requirements.txt .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto dei file dell'applicazione
COPY . .

# Esponi la porta su cui l'applicazione verrà eseguita
EXPOSE 5000

# Definisci il comando per eseguire l'applicazione
CMD ["python", "app.py"]
