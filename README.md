# 🤖 InstaBot - Bot Instagram Automatisé (Via cron VPS + Telegram Trigger)

Ce projet contient un bot Instagram automatisé qui peut être :
- 🕒 lancé automatiquement 2 fois par jour grâce à **Via cron VPS** (cron)
- 🧑‍💻 lancé manuellement via une commande Telegram

## 📦 Fonctionnalités

- Connexion à un compte Instagram via `instagrapi`
- Actions Instagram personnalisées (liker, commenter, etc.)
- Envoi d’un message à un bot Telegram en cas de succès/échec
- Déclenchement manuel du script via une commande Telegram
- Exécution automatique 2 fois par jour via Via cron VPS

---

## ⚙️ Installation locale

### 1. Cloner le dépôt

```bash
git clone https://github.com/JeremieN6/botInstagram.git
cd instabot
```

### 2. Cloner le dépôt

Ajoute les variables d’environnement nécessaires :

INSTAGRAM_USERNAME=ton_identifiant
INSTAGRAM_PASSWORD=ton_mot_de_passe
TELEGRAM_BOT_TOKEN=ton_token_bot_telegram
TELEGRAM_CHAT_ID=ton_chat_id


### 3. Installer les dépendances

Assure-toi d’avoir Python 3.10+ installé, puis :
pip install -r requirements.txt


### 4. Lancer le script manuellement
python script.py



🚀 Automatisation avec Via cron VPS
📁 Fichier Via cron VPS : .github/workflows/instabot.yml
Ce fichier est déjà prêt dans le dépôt. Il déclenche le script automatiquement 2 fois par jour (à 9h et 21h, heure de Paris).

🔐 Ajouter les secrets GitHub
Sur GitHub :

Va dans Settings > Secrets and variables > Actions

Clique sur New repository secret

Ajoute les secrets suivants :

Nom du secret	Description
INSTAGRAM_USERNAME	Identifiant Instagram
INSTAGRAM_PASSWORD	Mot de passe Instagram
TELEGRAM_BOT_TOKEN	Token du bot Telegram
TELEGRAM_CHAT_ID	Chat ID (où envoyer les messages)


💡 Exécution manuelle depuis GitHub
Tu peux aussi déclencher manuellement le script dans l’onglet Actions > Run workflow.

💬 Lancer le script via Telegram
Le script écoute une commande précise envoyée à ton bot Telegram (ex. : /startbot) pour exécuter l’action.
Tu dois héberger un script séparé (ex : en local ou sur un VPS) qui tourne en boucle pour écouter les messages Telegram. Ce script est fourni dans le projet.

📁 Contenu du dépôt
bash
Copier
Modifier
/
├── script.py                  # Script principal
├── telegram_trigger.py        # Script d'écoute Telegram (manuel)
├── requirements.txt           # Dépendances Python
├── .github/
│   └── workflows/
│       └── instabot.yml       # Tâche Via cron VPS
├── README.md                  # Ce fichier


🐍 Dépendances
Fichier requirements.txt :

txt
Copier
Modifier
instagrapi
python-dotenv
python-telegram-bot

🧠 À noter
Le script est prévu pour un usage éthique et personnel.

Ne pas abuser des appels à l’API Instagram pour éviter les bans.

Via cron VPS ne permet pas d’écouter Telegram en continu. Pour cela, hébergez telegram_trigger.py sur une machine ou un serveur.

🙋‍♂️ Auteur
Développé par Jeremie : jeremien6
Contact : contact@jeremiecode.fr