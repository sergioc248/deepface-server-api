from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from deepface import DeepFace
from scipy.spatial.distance import cosine
import shutil, os
from uuid import uuid4
import numpy as np
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time

app = FastAPI()

KNOWN_FACES_DIR = "app/known_faces"
FACE_DB = []  # List of dicts: { "name": "img.jpg", "embedding": [...] }

# ========== 📥 Load embeddings ==========

def preload_faces():
    global FACE_DB
    FACE_DB = []

    for file in os.listdir(KNOWN_FACES_DIR):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(KNOWN_FACES_DIR, file)
            try:
                embedding_obj = DeepFace.represent(img_path=path, enforce_detection=False)[0]
                FACE_DB.append({
                    "name": file,
                    "embedding": embedding_obj["embedding"]
                })
            except Exception as e:
                print(f"[WARN] Could not load {file}: {e}")

preload_faces()

# ========== 🔁 Watchdog handler ==========

class FaceFolderHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        if event.src_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            time.sleep(1)  # brief delay to ensure file is fully written
            try:
                filename = os.path.basename(event.src_path)
                embedding_obj = DeepFace.represent(img_path=event.src_path, enforce_detection=False)[0]
                FACE_DB.append({
                    "name": filename,
                    "embedding": embedding_obj["embedding"]
                })
                print(f"[INFO] New face added: {filename}")
            except Exception as e:
                print(f"[ERROR] Failed to process new face: {e}")

def start_watcher():
    observer = Observer()
    handler = FaceFolderHandler()
    observer.schedule(handler, path=KNOWN_FACES_DIR, recursive=False)
    observer.start()
    print("[INFO] Watchdog started for known_faces folder")

    # keep thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# ========== 🚀 Background startup ==========

@app.on_event("startup")
def start_background_tasks():
    threading.Thread(target=start_watcher, daemon=True).start()

# ========== 🧠 Face Matching Endpoint ==========

@app.post("/verify")
async def verify_face(file: UploadFile = File(...)):
    tmp_path = f"/tmp/{uuid4().hex}.jpg"
    with open(tmp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        embedding = DeepFace.represent(img_path=tmp_path, enforce_detection=False)[0]["embedding"]
        os.remove(tmp_path)

        best_match = None
        best_distance = float("inf")
        for person in FACE_DB:
            dist = cosine(embedding, person["embedding"])
            if dist < best_distance:
                best_distance = dist
                best_match = person

        THRESHOLD = 0.4
        if best_distance < THRESHOLD:
            return {"matched": True, "identity": best_match["name"], "distance": round(best_distance, 4)}
        else:
            return {"matched": False, "identity": None}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ========== 🆕 Manual Upload Endpoint ==========

@app.post("/add-face")
async def add_face(file: UploadFile = File(...), name: str = Form(...)):
    save_path = os.path.join(KNOWN_FACES_DIR, f"{name}.jpg")
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": f"{name}.jpg saved. Watchdog will load it automatically."}
