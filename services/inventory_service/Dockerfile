FROM python:3.11-slim
WORKDIR /app

# Installer les dépendances Python du service
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code du service
COPY . .

# Le Dockerfile est construit avec le contexte du dossier `services/inventory_service`.
# Nous ne pouvons donc pas atteindre `../../database` directement ici.
# La connexion à la base se fera plutôt côté gateway (qui a déjà le volume database monté),
# et ce service reste purement gRPC sans accès direct au module db_connection dans ce build.

EXPOSE 5006
CMD ["python", "app.py"]
