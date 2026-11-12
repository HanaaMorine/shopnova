# 1. On part d'une image avec Python 3.11 (version légère)
FROM python:3.10-slim

# 2. On travaille dans le dossier /app du conteneur
WORKDIR /app

# 3. On copie la liste des bibliothèques et on les installe
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. On copie le reste du projet
COPY . .

# 5. L'API utilise le port 8000
EXPOSE 8000

# 6. La commande qui lance l'API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "backend"]