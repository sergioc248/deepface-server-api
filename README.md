# DeepFace API Server

This project is a facial recognition API built with **FastAPI**, **DeepFace**, and **Docker**. It allows you to:

- Upload face images to a known face database
- Automatically detect and match incoming face uploads
- Use a file system watchdog to hot-load new images from a folder

---

## 📦 Features

- Live face recognition via `/verify` endpoint
- Upload new faces via `/add-face`
- Watchdog automatically detects new files in `known_faces/`
- Runs in a Docker container and auto-starts on EC2 reboot
- Compatible with ARM64 (AWS Graviton) and x86_64

---

## 🧱 Project Structure

deepface-server-api/
├── app/
│ ├── main.py # FastAPI app
│ └── known_faces/ # Folder with stored face images
├── Dockerfile # Container build
├── requirements.txt # Python dependencies
├── docker-compose.yml # Easy container setup
└── README.md


---

## 🚀 How to Run (Locally or on EC2)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/deepface-server-api.git
cd deepface-server-api
```

### 2. Build and start with Docker Compose

docker-compose up -d

This:

    Builds the deepface-api-arm image

    Maps port 8000:8000

    Mounts your local app/known_faces/ folder into the container

    Starts automatically on reboot with restart: always

## 🔍 Using the API
### 📂 Add a Known Face
#### Option A — Upload via API

curl -X POST http://<your-ec2-ip>:8000/add-face \
  -F "file=@manface.jpg" \
  -F "name=manface"

#### Option B — Copy directly into the known_faces folder

scp -i your-key.pem manface.jpg ubuntu@<ec2-ip>:~/deepface-server-api/app/known_faces/

    The app uses a watchdog to auto-load any .jpg or .png added to the folder.

### 🧪 Verify a Face Match

curl -X POST http://<your-ec2-ip>:8000/verify \
  -F "file=@test.jpg"

Example response:

{
  "matched": true,
  "identity": "manface.jpg",
  "distance": 0.271
}

### 🌐 Swagger UI

Visit:

http://<your-ec2-ip>:8000/docs

Use the /verify and /add-face endpoints directly from your browser.
⚙️ .gitignore and Image Handling

The app/known_faces/ folder is included in the repo, but only manface.jpg is tracked:

app/known_faces/*
!app/known_faces/manface.jpg

You can replace manface.jpg with your default test image.
## ✅ Auto-Start on EC2 Reboot

The container is launched with:

--restart=always

So it will:

    Restart on EC2 reboot

    Restart if Docker crashes

## 🧠 Dependencies

Installed via Docker:

    deepface==0.0.93

    fastapi

    uvicorn

    opencv-python-headless

    pandas

    numpy

    scipy

    watchdog

    python-multipart